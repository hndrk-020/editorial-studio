"""Source-aware, editor-supervised public-image importer.

No Google/Bing scraping and no image-search thumbnail extraction. An editor/agent
selects an exact image file URL and its original page/credit. The resulting local
JPEG starts UNAPPROVED. URLs are validated before any network activity.
"""
from __future__ import annotations

from ipaddress import ip_address
import socket
from urllib.parse import urlparse, urljoin
from urllib.request import build_opener, HTTPSHandler, HTTPRedirectHandler, ProxyHandler, Request
from urllib.error import HTTPError, URLError
from PIL import Image, ImageOps, UnidentifiedImageError
from io import BytesIO

from engine import PublicationError, import_image, load, store

MAX_IMAGE_BYTES = 14_000_000
MAX_REDIRECTS = 2
MAX_DOWNLOAD_SECONDS = 18


def safe_photo_url(url: str, *, dns: bool = False) -> str:
    u=urlparse(str(url).strip())
    if u.scheme != 'https' or not u.hostname or u.username or u.password:
        raise PublicationError('Photo URL must be a direct https:// image address without login details')
    if u.port not in (None,443):
        raise PublicationError('Only standard HTTPS image URLs are supported')
    host=u.hostname.lower().rstrip('.')
    if host == 'localhost' or host.endswith(('.local','.internal','.localhost')):
        raise PublicationError('Private/local network addresses are not allowed')
    try:
        ip=ip_address(host)
        if not ip.is_global:
            raise PublicationError('Local or private IP addresses are not allowed')
    except ValueError:
        pass
    if dns:
        try:
            ips={v[4][0] for v in socket.getaddrinfo(host,443,proto=socket.IPPROTO_TCP)}
        except OSError as ex:
            raise PublicationError('Could not resolve the image server hostname') from ex
        if not ips or not all(ip_address(x).is_global for x in ips):
            raise PublicationError('The image URL resolves to a private or restricted network address')
    return u.geturl()


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        return None


def _download_image(url: str) -> bytes:
    opener=build_opener(ProxyHandler({}),HTTPSHandler(),_NoRedirect())
    url=safe_photo_url(url,dns=True)
    for _ in range(MAX_REDIRECTS+1):
        req=Request(url,headers={'User-Agent':'EditorialStudioPhotoResearcher/0.2 (+human-supervised)','Accept':'image/jpeg,image/png,image/webp'})
        try:
            r=opener.open(req,timeout=MAX_DOWNLOAD_SECONDS)
        except HTTPError as ex:
            if ex.code in (301,302,303,307,308) and ex.headers.get('Location'):
                url=safe_photo_url(urljoin(url,ex.headers['Location']),dns=True)
                continue
            raise PublicationError(f'Photo host returned HTTP {ex.code}') from ex
        except (OSError,URLError) as ex:
            raise PublicationError('Photo host could not be reached; try downloading the photo manually') from ex
        with r:
            ctype=r.headers.get('Content-Type','').split(';')[0].strip().lower()
            if ctype not in ('image/jpeg','image/png','image/webp','application/octet-stream'):
                raise PublicationError(f'URL did not return a supported image (received {ctype or "no type"})')
            declared=int(r.headers.get('Content-Length') or 0)
            if declared>MAX_IMAGE_BYTES:
                raise PublicationError('Photo file is too large (14 MB maximum)')
            parts=[];size=0
            while True:
                chunk=r.read(min(256_000,MAX_IMAGE_BYTES-size+1))
                if not chunk:break
                size+=len(chunk)
                if size>MAX_IMAGE_BYTES:
                    raise PublicationError('Photo download exceeded 14 MB')
                parts.append(chunk)
            data=b''.join(parts)
            try:
                with Image.open(BytesIO(data)) as im:
                    if im.format not in ('JPEG','PNG','WEBP'):
                        raise PublicationError('Unsupported image encoding')
                    if im.width*im.height>50_000_000:
                        raise PublicationError('Image is too large in pixels')
                    im.verify()
            except (UnidentifiedImageError,OSError) as ex:
                raise PublicationError('Downloaded resource is not a readable image') from ex
            return data
    raise PublicationError('Photo URL redirected too many times')


def import_public_image(slug: str, slot: str, image_url: str, source_page: str,
                        credit: str, rights: str, *, evidence: str = '', downloader=None) -> dict:
    """A selected URL is *not* license proof. Reviewer approval is always reset."""
    safe_photo_url(image_url,dns=False)
    if not source_page.strip():
        raise PublicationError('Provide the original webpage or source reference')
    if not credit.strip():
        raise PublicationError('Provide a photographer or organization credit')
    if rights not in ('own','permission','licensed','private_reference'):
        raise PublicationError('Choose the intended image usage basis')
    getter=downloader or _download_image
    data=getter(image_url)
    photo=import_image(slug,slot,data,source_page,credit,rights)
    doc=load(slug)
    obj=doc['hero'] if slot=='hero' else next(e['image'] for e in doc['stories'] if e['id']==slot)
    obj['download_url']=image_url
    obj['evidence']=evidence.strip()[:600]
    obj['approval_note']='Downloaded candidate; verify subject, use and rights manually before approval'
    obj['approved']=False
    store(slug,doc)
    return photo
