"""Editor-selected image import. Downloads never grant image approval."""
from __future__ import annotations
from io import BytesIO
from pathlib import Path
import os,subprocess,sys
from PIL import Image,UnidentifiedImageError
from engine import PublicationError,import_image,load,store,serialized
from image_transport import safe_photo_url as _safe_photo_url,DownloadError

MAX_IMAGE_BYTES=14_000_000
MAX_DOWNLOAD_SECONDS=18
DOWNLOAD_WORKER=Path(__file__).with_name('image_transport.py')

def safe_photo_url(url: str, *, dns: bool=False) -> str:
    try:return _safe_photo_url(url,dns=dns)
    except (DownloadError,ValueError) as ex:raise PublicationError(str(ex)) from ex

def _download_image(url: str) -> bytes:
    url=safe_photo_url(url)
    # A killable worker bounds DNS, TLS, header parsing and body reads together.
    # It uses only the standard library and receives no application/session state.
    env={'PYTHONDONTWRITEBYTECODE':'1'}
    for key in ('SystemRoot','WINDIR'):
        if key in os.environ:env[key]=os.environ[key]
    try:
        result=subprocess.run([sys.executable,str(DOWNLOAD_WORKER)],input=url.encode('utf-8'),
            stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=MAX_DOWNLOAD_SECONDS,
            env=env,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0),check=False)
    except subprocess.TimeoutExpired as ex:
        raise PublicationError('Photo download timed out') from ex
    except OSError as ex:
        raise PublicationError('Could not start the image downloader') from ex
    if result.returncode:
        raise PublicationError('The selected image could not be downloaded safely')
    data=result.stdout
    if not data or len(data)>MAX_IMAGE_BYTES:raise PublicationError('Invalid photo size (14 MB max)')
    try:
        with Image.open(BytesIO(data),formats=('JPEG','PNG','WEBP')) as im:
            if im.width*im.height>50_000_000:raise PublicationError('Image is too large in pixels')
            im.verify()
    except (UnidentifiedImageError,Image.DecompressionBombError,OSError) as ex:
        raise PublicationError('Downloaded resource is not a readable JPEG, PNG or WebP image') from ex
    return data


@serialized
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
