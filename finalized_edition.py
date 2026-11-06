"""Re-export an explicitly registered, reviewed custom edition without relayout."""
import hashlib,json,shutil
from pathlib import Path
import fitz

def document_digest(doc):
    return hashlib.sha256(json.dumps(doc,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

def inspect_edition(directory,doc):
    config=directory/'finalized-edition.json'
    if not config.exists():return None
    spec=json.loads(config.read_text(encoding='utf-8'))
    if document_digest(doc)!=spec['manifest_sha256']:
        raise ValueError('Publication changed since custom proof approval. Rebuild and review the custom edition before export.')
    def local(name):
        path=(directory/name).resolve()
        if not path.is_relative_to(directory.resolve()):raise ValueError('Custom edition files must remain inside the project')
        return path
    pdf=local(spec['pdf'])
    if hashlib.sha256(pdf.read_bytes()).hexdigest()!=spec['pdf_sha256']:raise ValueError('Reviewed PDF fingerprint changed')
    assets=spec['assets'];approvals=doc.get('human_image_approval',{}).get('assets',{})
    if not assets or len({a['id'] for a in assets})!=len(assets):raise ValueError('Invalid custom image inventory')
    for asset in assets:
        digest=hashlib.sha256(local(asset['file']).read_bytes()).hexdigest()
        if not asset.get('approved') or digest!=asset['sha256'] or digest!=approvals.get(asset['id']):raise ValueError('Custom image approval changed: '+asset['id'])
    with fitz.open(pdf) as document:
        photo_pages=[i+1 for i,p in enumerate(document) if p.get_images(full=True)]
        if len(document)!=spec['pages'] or photo_pages!=spec['photo_pages']:raise ValueError('Custom edition page audit failed')
        if any(not p.get_text().strip() for p in document):raise ValueError('Custom edition has an empty text page')
        links=sum(len(p.get_links()) for p in document)
    return dict(spec,pdf_path=pdf,links=links)

def publish_edition(spec,doc,output):
    output.parent.mkdir(parents=True,exist_ok=True)
    temporary=output.with_suffix('.part')
    try:
        shutil.copyfile(spec['pdf_path'],temporary)
        if hashlib.sha256(temporary.read_bytes()).hexdigest()!=spec['pdf_sha256']:raise ValueError('Export copy verification failed')
        temporary.replace(output)
    finally:
        temporary.unlink(missing_ok=True)
    snapshot=output.with_suffix('.manifest.json');snapshot.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
    return dict(pass_=True,**{'pass':True},errors=[],pages=spec['pages'],photo_pages_verified=len(spec['photo_pages']),links=spec['links'],bytes=output.stat().st_size,file=str(output),snapshot=str(snapshot),reviewed_edition=True)
