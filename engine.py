"""Editorial Studio publication engine: strict preflight, local image assets, PDF verification."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from io import BytesIO
import json
import re
from typing import Any
from contextvars import ContextVar
from hashlib import sha256
from html import unescape
from creative import DIRECTIONS, normalize_brief, propose_directions, brief_checks
from urllib.parse import urlparse

from PIL import Image, ImageOps, ImageDraw, ImageFont, UnidentifiedImageError
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor, Color
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
import pymupdf as fitz
from functools import wraps
from threading import RLock
from local_files import temporary_path, atomic_write

ROOT = Path(__file__).resolve().parent
PROJECTS = ROOT / "projects"
OUTPUTS = ROOT / "output"
# Context-local visual style; safe even if two publications render in parallel.
_ACTIVE_STYLE = ContextVar('editorial_studio_style', default='field-notes')
_ACTIVE_DISTRIBUTION = ContextVar('editorial_studio_distribution', default='private')
_PALETTES = {
    'field-notes': dict(ink='#1C302C', paper='#F7F3E9', accent='#AF7352', sage='#71877A', muted='#777C74', white='#FFFFFF', line='#D8D4C7'),
    'bold-perspective': dict(ink='#202D33', paper='#FFF4E8', accent='#E76748', sage='#347C88', muted='#6B7377', white='#FFFFFF', line='#D6CBC1'),
}
class Palette:
    def __getitem__(self, key):
        return _PALETTES[_ACTIVE_STYLE.get()][key]
COLORS = Palette()

def is_bold():
    return _ACTIVE_STYLE.get() == 'bold-perspective'

W, H = A4


class PublicationError(Exception):
    pass

_STATE_LOCK=RLock()
def serialized(function):
    """Keep local edits and export snapshots coherent across request threads."""
    @wraps(function)
    def guarded(*args, **kwargs):
        with _STATE_LOCK:return function(*args, **kwargs)
    return guarded


def slugify(value: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return s[:56] or "untitled"


def clean_headline(value: str, limit: int = 110) -> str:
    """UI and PDF headlines are text, not user-authored HTML fragments."""
    value=unescape(re.sub(r'</?[A-Za-z][^>]*>', ' ', str(value)))
    return ' '.join(value.split())[:limit]


def path_for(slug: str) -> Path:
    if slug != slugify(slug):
        raise PublicationError("Invalid project identifier")
    p = (PROJECTS / slug).resolve()
    if p.parent != PROJECTS.resolve():
        raise PublicationError("Invalid project path")
    return p


def load(slug: str) -> dict:
    path = path_for(slug) / "manifest.json"
    if not path.exists():
        raise PublicationError(f"Project not found: {slug}")
    return json.loads(path.read_text(encoding="utf-8"))


@serialized
def store(slug: str, doc: dict):
    if doc.get("slug") != slug:
        raise PublicationError("Project slug cannot change")
    p = path_for(slug)
    p.mkdir(parents=True, exist_ok=True)
    # Atomic write to avoid a half-written manifest after application shutdown.
    atomic_write(p / "manifest.json", json.dumps(doc, ensure_ascii=False, indent=2).encode("utf-8"))


def blank_image() -> dict:
    return {"file": "", "source": "", "credit": "", "rights": "", "evidence":"", "approved": False, "width": 0, "height": 0}


@serialized
def create_project(title: str, kind="magazine", description="", edition="", brief=None) -> dict:
    if kind not in ("magazine", "onepager"):
        raise PublicationError("Unknown publication template")
    title = clean_headline(title, 90)
    if len(title) < 2:
        raise PublicationError("Enter a title")
    stem = slugify(title)
    slug = stem
    n = 2
    while path_for(slug).exists():
        slug = f"{stem[:50]}-{n}"
        n += 1
    creative_brief = normalize_brief(brief, kind)
    doc = {"schema_version": 2, "slug": slug, "title": title, "kicker": "THE EDITORIAL STUDIO", "edition": edition or "Edition 01", "description": description or "A story worth keeping.", "kind": kind, "brief": creative_brief, "style": {"selected": None, "decided_at": None}, "hero": blank_image(), "stories": [], "created": datetime.now(timezone.utc).isoformat()}
    store(slug, doc)
    (path_for(slug) / "assets").mkdir(exist_ok=True)
    return doc


def photo_slots(doc: dict):
    yield "hero", "Cover image", doc.get("hero", {})
    for e in doc.get("stories", []):
        yield e["id"], e.get("title", "Story"), e.get("image", {})


def credits_page_count(doc: dict) -> int:
    return max(1,(len(list(photo_slots(doc)))+6)//7)


def _asset_file(slug: str, photo: dict) -> Path | None:
    name = photo.get("file", "")
    if not name or not re.fullmatch(r"[a-z0-9_-]+\.jpg", name):
        return None
    project = path_for(slug)
    folder = (project / "assets").resolve()
    if folder.parent != project:return None
    resolved = (folder / name).resolve()
    return resolved if resolved.parent == folder else None


def _valid_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        parsed.port  # Validate syntax/range; ordinary hyperlinks may use custom HTTPS ports.
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username and not parsed.password and not any(ord(c)<33 or ord(c)==127 for c in url)
    except Exception:
        return False


def preflight(doc: dict) -> dict:
    slug = doc["slug"]
    errors, warnings, successes = [], [], []
    if not doc.get("title", "").strip():
        errors.append("Publication title is missing")
    if doc.get('kind')=='magazine':
        if len(wrap(doc.get('description',''),'Helvetica',11,W-80))>3:
            errors.append('Cover introduction is too long for its reserved space')
        if len(wrap(doc.get('description',''),'Helvetica',15,W-96))>11:
            errors.append('Editorial introduction exceeds its reserved page space')
    else:
        if len(wrap(doc.get('description',''),'Helvetica',10.8,W-84))>4:
            errors.append('Onepager introduction exceeds the reserved page space')
    if not doc.get("stories"):
        errors.append("Add at least one story")
    if doc.get('schema_version',1) >= 2:
        errors.extend(brief_checks(doc.get('brief',{})))
        if doc.get('style',{}).get('selected') not in DIRECTIONS:
            errors.append('Select one of the two proposed style directions before publication')
    if doc.get("kind") == "onepager" and len(doc.get("stories", [])) > 3:
        errors.append("Onepager supports at most 3 stories; use the magazine template")
    if doc.get("kind") == "magazine" and len(doc.get("stories", [])) > 12:
        errors.append("Magazine v0.1 supports at most 12 stories (image credits and table of contents capacity)")
    for slot, label, photo in photo_slots(doc):
        initial_errors = len(errors)
        f = _asset_file(slug, photo)
        if not f or not f.exists():
            errors.append(f"{label}: image file missing (not just an image URL)")
            continue
        try:
            with Image.open(f) as img:
                img.verify()
            with Image.open(f) as img:
                iw, ih = img.size
        except (UnidentifiedImageError, OSError):
            errors.append(f"{label}: corrupted or unreadable image")
            continue
        if iw < 1100 or ih < 700:
            errors.append(f"{label}: low resolution ({iw} x {ih}); minimum 1100 x 700")
        if not photo.get("source", "").strip():
            errors.append(f"{label}: photograph source missing")
        if not photo.get("credit", "").strip():
            errors.append(f"{label}: photo credit missing")
        if photo.get("rights") not in ("own", "licensed", "permission", "private_reference"):
            errors.append(f"{label}: usage basis must be chosen")
        if photo.get('rights') in ('licensed','permission') and not photo.get('evidence','').strip():
            errors.append(f'{label}: record license or permission evidence')
        if photo.get("rights") == "private_reference":
            if doc.get('brief',{}).get('distribution') == 'public':
                errors.append(f'{label}: private-reference photo cannot be publicly distributed')
            else:
                warnings.append(f"{label}: private reference only; not cleared for public distribution")
        if not photo.get("approved", False):
            errors.append(f"{label}: photo has not been approved")
        # Image approval belongs to a particular set of pixels, not a filename.
        digest=photo.get('sha256','')
        if digest:
            if sha256(f.read_bytes()).hexdigest()!=digest:
                errors.append(f'{label}: file changed after import or approval; reimport and reapprove')
        elif doc.get('brief',{}).get('distribution')=='public':
            errors.append(f'{label}: image fingerprint missing; reimport before public publication')
        else:
            warnings.append(f'{label}: legacy image has no fingerprint; reimport recommended')
        if len(errors) == initial_errors:
            successes.append(label)
    for e in doc.get("stories", []):
        if not e.get("title", "").strip():
            errors.append("A story is missing its name")
        if not e.get("description", "").strip():
            errors.append(f"{e.get('title', 'Story')}: story text missing")
        if doc.get('kind')=='magazine':
            if len(wrap(e.get('description',''),'Helvetica',10.4,W-86))>5:
                errors.append(f"{e.get('title','Story')}: story text exceeds the available page space")
            if len(e.get('title',''))>38:
                errors.append(f"{e.get('title','Story')}: contents-page heading exceeds 38 characters")
            if len(wrap('NOTE  '+str(e.get('notes','')),'Helvetica',8.4,W-86))>2:
                errors.append(f"{e.get('title','Story')}: note exceeds the available page space")
        else:
            if len(wrap(e.get('description',''),'Helvetica',8.6,W-218))>3:
                errors.append(f"{e.get('title','Story')}: onepager text exceeds the available space")
            if len(e.get('title',''))>42:
                errors.append(f"{e.get('title','Story')}: onepager heading exceeds 42 characters")
        for k in ("website", "maps"):
            if e.get(k) and not _valid_url(e[k]):
                errors.append(f"{e.get('title', 'Story')}: invalid {k} link")
        if not e.get("website"):
            warnings.append(f"{e.get('title', 'Story')}: original source link missing")
    total_photos=len(list(photo_slots(doc)))
    try:
        from finalized_edition import inspect_edition
        custom=inspect_edition(path_for(slug),doc)
        if custom:
            total_photos=len(custom['assets'])
            if not errors:successes=[a['id'] for a in custom['assets']]
    except (ValueError,KeyError,OSError) as ex:
        errors.append('Custom edition: '+str(ex))
    return {"pass": not errors, "errors": errors, "warnings": warnings, "ready_photos": len(successes), "total_photos": total_photos, "messages": successes}


def _require_style(doc: dict):
    if doc.get('schema_version',1) >= 2 and doc.get('style',{}).get('selected') not in DIRECTIONS:
        raise PublicationError('Choose one of the two creative directions before producing content')


@serialized
def import_image(slug: str, slot: str, data: bytes, source: str, credit: str, rights: str) -> dict:
    doc = load(slug)
    _require_style(doc)
    img_obj = doc["hero"] if slot == "hero" else next((e["image"] for e in doc["stories"] if e["id"] == slot), None)
    if img_obj is None:
        raise PublicationError("Unknown image slot")
    if len(data) > 14_000_000:
        raise PublicationError("Image exceeds 14 MB")
    try:
        with Image.open(BytesIO(data), formats=('JPEG','PNG','WEBP')) as read:
            if read.width * read.height > 50_000_000:
                raise PublicationError("Image has too many pixels")
            clean = ImageOps.exif_transpose(read).convert("RGB")
    except (UnidentifiedImageError, Image.DecompressionBombError, OSError, ValueError) as ex:
        raise PublicationError("File is not a valid JPEG, PNG or WebP image") from ex
    original_size = clean.size
    clean.thumbnail((2800, 2800), Image.Resampling.LANCZOS)
    fname = "hero.jpg" if slot == "hero" else f"{slot}.jpg"
    dest = path_for(slug) / "assets" / fname
    dest.parent.mkdir(exist_ok=True)
    if dest.parent.resolve().parent != path_for(slug) or dest.is_symlink():
        raise PublicationError("Invalid image destination")
    tmp = temporary_path(dest)
    try:
        clean.save(tmp, format="JPEG", quality=89, optimize=True, subsampling=0)
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)
    img_obj.update({"file": fname, "sha256":sha256(dest.read_bytes()).hexdigest(), "source": source.strip(), "credit": credit.strip(), "rights": rights, "evidence":"", "approved": False, "width": original_size[0], "height": original_size[1]})
    store(slug, doc)
    return img_obj


@serialized
def set_image_metadata(slug: str, slot: str, metadata: dict) -> dict:
    doc = load(slug)
    obj = doc["hero"] if slot == "hero" else next((e["image"] for e in doc["stories"] if e["id"] == slot), None)
    if obj is None:
        raise PublicationError("Unknown image slot")
    for k in ("source", "credit", "rights", "evidence", "approved"):
        if k in metadata:
            if k=='approved':
                if type(metadata[k]) is not bool:
                    raise PublicationError('Image approval must be true or false')
                obj[k]=metadata[k]
            else:
                updated=str(metadata[k])[:600]
                if obj.get(k)!=updated and 'approved' not in metadata:
                    obj['approved']=False
                obj[k]=updated
    # Metadata approval is bound to an existing and valid local image.
    if obj.get("approved") and not (_asset_file(slug, obj) and _asset_file(slug, obj).exists()):
        raise PublicationError("Cannot approve a missing local photograph")
    store(slug, doc)
    return obj


@serialized
def add_story(slug: str, title: str):
    doc = load(slug)
    _require_style(doc)
    ids = {x["id"] for x in doc["stories"]}
    stem = slugify(title)
    idx = stem
    n = 2
    while idx in ids:
        idx = f"{stem}-{n}"; n += 1
    entry = {"id": idx, "title": clean_headline(title), "area": "", "price": "", "best_for": "Lunch or dinner" if doc.get('brief',{}).get('category')=='restaurants' else "", "order": "", "description": "", "notes": "", "website": "", "maps": "", "image": blank_image()}
    doc["stories"].append(entry)
    store(slug, doc)
    return entry


@serialized
def update_story(slug: str, sid: str, changes: dict):
    doc = load(slug)
    e = next((x for x in doc["stories"] if x["id"] == sid), None)
    if e is None:
        raise PublicationError("Unknown story")
    allowed = ("title", "area", "price", "best_for", "order", "description", "notes", "website", "maps")
    for k in allowed:
        if k in changes:
            e[k] = clean_headline(changes[k]) if k=='title' else str(changes[k])[:2000]
    store(slug, doc)
    return e


@serialized
def update_brief(slug: str, changes: dict):
    doc = load(slug)
    current = dict(doc.get('brief',{}))
    current.update({k:v for k,v in changes.items() if k in (
        'subject','purpose','audience','preferred_style','reference_url',
        'category','distribution','language')})
    doc['brief'] = normalize_brief(current, doc['kind'])
    # A changed brief requires an explicit new creative decision.
    doc['style'] = {'selected':None,'decided_at':None}
    store(slug,doc)
    return doc


@serialized
def select_style(slug: str, style_id: str):
    if style_id not in DIRECTIONS:
        raise PublicationError('Unknown creative style direction')
    doc=load(slug)
    if doc.get('schema_version',1)>=2 and brief_checks(doc.get('brief',{})):
        raise PublicationError('Complete the creative brief before choosing a direction')
    doc['style']={'selected':style_id,'decided_at':datetime.now(timezone.utc).isoformat()}
    store(slug,doc)
    return doc['style']


@serialized
def update_project(slug: str, changes: dict):
    doc = load(slug)
    for k in ("title", "kicker", "edition", "description"):
        if k in changes:
            doc[k] = clean_headline(changes[k],90) if k=='title' else str(changes[k])[:2000]
    store(slug, doc)
    return doc


# PDF composition utilities ----------------------------------------------------
def fill_rect(c, x, y, w, h, color):
    c.setFillColor(HexColor(color)); c.rect(x,y,w,h,stroke=0,fill=1)


def line(c,x1,y1,x2,y2,color=None,width=0.7):
    c.setLineWidth(width);c.setStrokeColor(HexColor(color or COLORS["line"]));c.line(x1,y1,x2,y2)


def spaced(c, text, x, y, font="Helvetica-Bold", size=8, color=None, spacing=2):
    c.setFillColor(HexColor(color or COLORS["accent"]))
    t=c.beginText(x,y);t.setFont(font,size);t.setCharSpace(spacing);t.textOut(text.upper());t.setCharSpace(0);c.drawText(t)


def wrap(text, font, size, max_width):
    words=str(text).replace("\n"," \u2022 ").split()
    out=[];cur=""
    for word in words:
        t=(cur+" "+word).strip()
        if stringWidth(t,font,size)<=max_width:
            cur=t
        else:
            if cur:out.append(cur)
            if stringWidth(word,font,size)>max_width:
                # Split pathological long input to keep it inside the page.
                piece=""
                for ch in word:
                    if stringWidth(piece+ch,font,size)>max_width:
                        if piece:out.append(piece)
                        piece=ch
                    else:piece+=ch
                cur=piece
            else:cur=word
    if cur:out.append(cur)
    return out


def block(c,text,x,y,width,font="Helvetica",size=10,color=None,leading=None,max_lines=99):
    leading=leading or size*1.48
    lines=wrap(text,font,size,width)
    c.setFillColor(HexColor(color or COLORS["ink"]));c.setFont(font,size)
    for i,s in enumerate(lines[:max_lines]):
        c.drawString(x,y-i*leading,s)
    return y-min(len(lines),max_lines)*leading


def large_title(c,text,x,y,max_width,max_lines=2,size=41):
    headline = 'Helvetica-Bold' if is_bold() else 'Times-Roman'
    lines=wrap(text,headline,size,max_width)
    while len(lines)>max_lines and size>22:
        size-=1; lines=wrap(text,headline,size,max_width)
    c.setFillColor(HexColor(COLORS["ink"]));c.setFont("Helvetica-Bold" if is_bold() else "Times-Roman",size)
    for idx,s in enumerate(lines[:max_lines]):c.drawString(x,y-idx*size*1.03,s)
    return y - min(max_lines,len(lines))*size*1.03


def photo(c, path, x,y,w,h):
    with Image.open(path) as im:
        im=ImageOps.fit(im.convert("RGB"), (int(w*2.4),int(h*2.4)),method=Image.Resampling.LANCZOS,centering=(0.5,0.5))
        c.drawImage(ImageReader(im),x,y,width=w,height=h,mask="auto")


def footer(c,index,total,slug):
    line(c,42,38,W-42,38)
    spaced(c,f"EDITORIAL STUDIO / {_ACTIVE_DISTRIBUTION.get().upper()} EDITION",42,25,size=6.4,spacing=1)
    c.setFillColor(HexColor(COLORS["muted"]));c.setFont("Helvetica",8)
    c.drawRightString(W-42,25,f"{index:02d} / {total:02d}")


def cover_page(c,doc,slug,number,total):
    fill_rect(c,0,0,W,H,COLORS["paper"])
    image_path = _asset_file(slug, doc["hero"])
    photo(c,image_path,0,H*0.33,W,H*0.67)
    fill_rect(c,0,0,W,H*.33,COLORS['paper'])
    if is_bold():
        fill_rect(c,0,H*.33-5,W,9,COLORS['accent'])
    spaced(c,doc.get("kicker","THE LOCAL TABLE"),40,H*.29,size=8.5)
    y=large_title(c,doc["title"],40,H*.244,W-80,max_lines=2,size=52)
    block(c,doc.get("description", ""),40,max(y-7,86),W-80,size=11,max_lines=3)
    c.setFont("Helvetica-Bold",9);c.setFillColor(HexColor(COLORS["accent"]));c.drawString(40,57,doc.get("edition",""))
    footer(c,number,total,slug);c.showPage()


def editorial_page(c,doc,slug,number,total):
    fill_rect(c,0,0,W,H,COLORS["paper"])
    spaced(c,"A NOTE FROM THE EDITOR",46,H-74)
    large_title(c,"The story behind the images.",46,H-141,W-92,size=43)
    line(c,46,H-231,W-46,H-231,COLORS["accent"],2)
    block(c,doc.get("description", ""),46,H-276,W-96,size=15,leading=24,max_lines=11)
    c.setFillColor(HexColor(COLORS["ink"]))
    c.setFont("Times-Italic",23);c.drawString(46,132,"Every edition begins with an idea.")
    spaced(c,"CURATED, VERIFIED, SAVED FOR OFFLINE USE",46,96,size=7)
    footer(c,number,total,slug);c.showPage()


def contents_page(c,doc,slug,number,total):
    fill_rect(c,0,0,W,H,COLORS["paper"])
    spaced(c,"INSIDE THE EDITION",46,H-70)
    large_title(c,"Inside this edition",46,H-123,W-90,size=42)
    y=H-205
    for idx,e in enumerate(doc["stories"][:13],start=1):
        c.setFont("Helvetica-Bold",8);c.setFillColor(HexColor(COLORS["accent"]));c.drawString(47,y,f"{idx:02d}")
        c.setFont("Times-Roman",20 if len(doc["stories"])<12 else 17);c.setFillColor(HexColor(COLORS["ink"]));c.drawString(90,y-3,str(e.get("title",""))[:38])
        c.setFont("Helvetica",8);c.setFillColor(HexColor(COLORS["muted"]));c.drawRightString(W-48,y-1,e.get("area",""))
        line(c,47,y-16,W-47,y-16)
        y-=46 if len(doc["stories"])<12 else 40
    spaced(c,"ALL IMAGES ARE EMBEDDED IN THE PDF",47,100,size=7)
    footer(c,number,total,slug);c.showPage()


def story_page(c, doc, e, slug, index, number, total):
    fill_rect(c,0,0,W,H,COLORS["paper"])
    p = _asset_file(slug,e["image"])
    # Full-height editorial photograph across top half.
    photo(c,p,0,H*.49,W,H*.51)
    fill_rect(c,0,0,W,H*.49,COLORS["paper"])
    spaced(c,f"{index:02d}  /  {e.get('area','LOCAL TABLE')}",43,H*.454,size=7.8)
    after=large_title(c,e.get("title","Untitled"),43,H*.409,W-86,max_lines=2,size=34)
    cy=min(after-7,H*.32)
    block(c,e.get("description",""),43,cy,W-86,size=10.4,leading=15,max_lines=5)
    # Bottom half uses fixed bands so text will not spill into the footer.
    line(c,43,162,W-43,162)
    c.setFont("Helvetica-Bold",7.7);c.setFillColor(HexColor(COLORS["accent"]))
    restaurant_mode = doc.get('brief',{}).get('category') == 'restaurants'
    c.drawString(43,146,"WHAT TO ORDER" if restaurant_mode else "KEY HIGHLIGHT")
    c.drawString(313,146,"BEST FOR / PRICE" if restaurant_mode else "DETAILS / CONTEXT")
    block(c,e.get("order", ""),43,129,245,size=9,max_lines=3,leading=12)
    block(c," · ".join(filter(None,[e.get("best_for",""),e.get("price","")])),313,129,238,size=9,max_lines=3,leading=12)
    c.setFont("Helvetica",8);c.setFillColor(HexColor(COLORS["muted"]))
    note=e.get("notes","")
    if note: block(c,"NOTE  "+note,43,89,W-86,size=8.4,max_lines=2,leading=10)
    # Links in compact footer row.
    if e.get("website"):
        c.setFillColor(HexColor(COLORS["accent"]));c.setFont("Helvetica-Bold",8);c.drawString(43,54,"WEBSITE")
        c.linkURL(e["website"],(40,50,117,69),relative=0)
    if e.get("maps"):
        c.setFillColor(HexColor(COLORS["accent"]));c.setFont("Helvetica-Bold",8);c.drawString(155,54,"MAP / LINK" if doc.get("brief",{}).get("category") != "restaurants" else "GOOGLE MAPS")
        c.linkURL(e["maps"],(151,50,258,69),relative=0)
    footer(c,number,total,slug);c.showPage()


def itinerary_page(c,doc,slug,number,total):
    fill_rect(c,0,0,W,H,COLORS["paper"])
    spaced(c,"BEFORE YOU GO",45,H-68)
    large_title(c,"Notes for the reader",45,H-121,W-88,size=43)
    y=H-208
    notes=[("01", "Check the source", "Every story is editorial, not a substitute for up-to-date information from the original source."),
           ("02", "Read the image credits", "The photo credits page records origin, photographer or organization and usage basis."),
           ("03", "Follow the references", "Where available, story cards link to official sources and relevant details."),
           ("04", "Keep the PDF", "Images are embedded locally and the publication opens offline."),
           ("05", "Respect image rights", "Personal-reference images are not cleared for public distribution without permission.")]
    for num,title,desc in notes:
        spaced(c,num,45,y,size=9)
        c.setFillColor(HexColor(COLORS["ink"]));c.setFont("Times-Roman",24);c.drawString(88,y-5,title)
        block(c,desc,90,y-28,450,size=10,max_lines=3)
        line(c,45,y-73,W-46,y-73)
        y-=111
    footer(c,number,total,slug);c.showPage()


def credits_page(c,doc,slug,number,total,items,part,parts):
    fill_rect(c,0,0,W,H,COLORS["paper"])
    spaced(c,"IMAGE PROVENANCE",46,H-69)
    large_title(c,"Images & sources",46,H-126,W-92,size=38)
    block(c,f"Page {part} of {parts}. Image credits are part of the publication, not optional. Verify usage rights for the intended audience.",46,H-180,W-92,size=10,leading=16,max_lines=4)
    y=H-262
    for slot,label,obj in items:
        c.setFont("Helvetica-Bold",9);c.setFillColor(HexColor(COLORS["ink"]));c.drawString(46,y,label[:62])
        y-=15
        source=f"Credit: {obj.get('credit','')}  |  Basis: {obj.get('rights','')}"
        y=block(c,source,46,y,W-94,font="Helvetica",size=7.7,leading=10,max_lines=2)-5
        src=obj.get('source','')
        y=block(c,'Source: '+src,46,y,W-94,font="Helvetica",size=7.0,leading=9,max_lines=2)-10
        if _valid_url(src):c.linkURL(src,(45,y+4,W-46,y+42),relative=0)
    footer(c,number,total,slug);c.showPage()


def onepager(c,doc,slug):
    fill_rect(c,0,0,W,H,COLORS["paper"])
    photo(c,_asset_file(slug,doc["hero"]),0,H*.67,W,H*.33)
    spaced(c,doc.get("kicker","EDITORIAL STUDIO"),40,H*.635,size=7.8)
    end=large_title(c,doc.get("title",""),40,H*.598,W-80,size=39,max_lines=2)
    block(c,doc.get("description",""),40,end-6,W-84,size=10.8,leading=14,max_lines=4)
    entries=doc.get("stories",[])[:3]
    y=H*.421
    for e in entries:
        f=_asset_file(slug,e["image"])
        photo(c,f,40,y-77,123,83)
        c.setFont("Times-Roman",17);c.setFillColor(HexColor(COLORS["ink"]));c.drawString(181,y-10,e.get("title","")[:42])
        block(c,e.get("description",""),181,y-29,W-218,size=8.6,leading=11,max_lines=3)
        if e.get("website"):c.linkURL(e["website"],(178,y-65,W-40,y-2),relative=0)
        y-=102
    spaced(c,doc.get("edition",""),40,58,size=7)
    footer(c,1,1,slug);c.showPage()


@serialized
def render_pdf(doc: dict, output: Path) -> dict:
    slug=doc["slug"]
    result=preflight(doc)
    if not result["pass"]:
        raise PublicationError("Preflight failed: " + " | ".join(result["errors"][:8]))
    style_id = doc.get('style',{}).get('selected') or 'field-notes'
    theme_token = _ACTIVE_STYLE.set(style_id)
    distribution_token = _ACTIVE_DISTRIBUTION.set(doc.get('brief',{}).get('distribution','private'))
    output.parent.mkdir(parents=True,exist_ok=True)
    tmp=temporary_path(output)
    try:
        c=canvas.Canvas(str(tmp),pagesize=A4,pageCompression=1)
        c.setTitle(f"{doc['title']} | Editorial Studio")
        if doc.get("kind")=="onepager":
            total=1
            onepager(c,doc,slug)
        else:
            credit_entries=list(photo_slots(doc))
            ncredits=credits_page_count(doc)
            total=4+len(doc["stories"])+ncredits
            cover_page(c,doc,slug,1,total)
            editorial_page(c,doc,slug,2,total)
            contents_page(c,doc,slug,3,total)
            for i,e in enumerate(doc["stories"],start=1):
                story_page(c,doc,e,slug,i,3+i,total)
            itinerary_page(c,doc,slug,4+len(doc["stories"]),total)
            for page_index in range(ncredits):
                part=credit_entries[page_index*7:(page_index+1)*7]
                credits_page(c,doc,slug,5+len(doc["stories"])+page_index,total,part,page_index+1,ncredits)
        c.save()
        # Independent structural and photo verification, before publishing.
        audit=verify_pdf(tmp,doc)
        if not audit["pass"]:
            raise PublicationError("PDF audit failed: " + "; ".join(audit["errors"]))
        tmp.replace(output)
        snapshot=output.with_suffix(".manifest.json")
        atomic_write(snapshot,json.dumps(doc,ensure_ascii=False,indent=2).encode("utf-8"))
        return {**audit,"file":str(output),"snapshot":str(snapshot)}
    finally:
        if tmp.exists():tmp.unlink()
        _ACTIVE_STYLE.reset(theme_token)
        _ACTIVE_DISTRIBUTION.reset(distribution_token)


def verify_pdf(path:Path,doc:dict) -> dict:
    try:
        with fitz.open(path) as pdf:
            actual_pages=len(pdf)
            expected_pages=1 if doc.get("kind")=="onepager" else 4+len(doc["stories"])+credits_page_count(doc)
            errors=[]
            if actual_pages != expected_pages:
                errors.append(f"Expected {expected_pages} pages, PDF contains {actual_pages}")
            photo_indices=[0] if doc.get("kind")=="onepager" else [0]+list(range(3,3+len(doc["stories"])))
            for idx in photo_indices:
                if idx>=len(pdf) or len(pdf[idx].get_images(full=True))==0:
                    errors.append(f"Page {idx+1}: embedded photograph missing")
            nlinks=sum(len(page.get_links()) for page in pdf)
            if any(e.get("website") or e.get("maps") for e in doc.get("stories",[])) and nlinks<1:
                errors.append("No functional PDF hyperlinks")
            if doc.get("kind")=="onepager" and len(pdf[0].get_images(full=True)) < 1+len(doc.get("stories", [])):
                errors.append("Onepager: not all story images are embedded")
            return {"pass":not errors,"errors":errors,"pages":actual_pages,"photo_pages_verified":len(photo_indices),"links":nlinks,"bytes":path.stat().st_size}
    except Exception as ex:
        return {"pass":False,"errors":[f"Invalid PDF: {ex}"],"pages":0,"photo_pages_verified":0,"links":0,"bytes":0}


@serialized
def export(slug: str):
    doc=load(slug)
    stem=doc["slug"] + ("-onepager" if doc["kind"]=="onepager" else "-magazine")
    path=OUTPUTS/(stem+".pdf")
    from finalized_edition import inspect_edition, publish_edition
    if (path_for(slug)/'finalized-edition.json').exists():
        check=preflight(doc)
        if not check['pass']:raise PublicationError('Preflight failed: '+' | '.join(check['errors']))
        try:return publish_edition(inspect_edition(path_for(slug),doc),doc,path)
        except (ValueError,KeyError,OSError) as ex:raise PublicationError(str(ex)) from ex
    return render_pdf(doc,path)


def list_projects():
    result=[]
    for path in sorted(PROJECTS.glob("*/manifest.json")):
        try:
            d=json.loads(path.read_text(encoding="utf-8"))
            pf=preflight(d)
            result.append({"slug":d["slug"],"title":d["title"],"kind":d["kind"],"edition":d.get("edition",""),"ready_photos":pf["ready_photos"],"total_photos":pf["total_photos"],"ready":pf["pass"],"style":d.get('style',{}).get('selected')})
        except Exception:
            continue
    return result
