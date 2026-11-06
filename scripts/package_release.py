"""Build a reproducible-ish ZIP and SHA256 for private-beta GitHub Releases.

Requires no external packaging dependency. Deliberately excludes users' projects,
output PDFs, local secrets, git internals, test fixtures and Python caches.
"""
from __future__ import annotations
import hashlib
import subprocess
import sys
import zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'dist'
SKIP_PARTS={'dist','.git','projects','output','.venv','__pycache__','tests','.github'}
subprocess.run([sys.executable,str(ROOT/'scripts/validate_repository.py')],check=True)
DEST.mkdir(exist_ok=True)
version='0.3.0'
zipfile_path=DEST/f'editorial-studio-v{version}-private-beta.zip'
files=[p for p in ROOT.rglob('*') if p.is_file() and not (set(p.relative_to(ROOT).parts) & SKIP_PARTS)
       and p.suffix not in ('.pyc','.log') and p.name not in ('.DS_Store',)]
with zipfile.ZipFile(zipfile_path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for f in sorted(files):
        arc=Path('editorial-studio')/f.relative_to(ROOT)
        zi=zipfile.ZipInfo(arc.as_posix(),date_time=(2026,1,1,0,0,0))
        zi.compress_type=zipfile.ZIP_DEFLATED
        zi.external_attr=(0o100644<<16)
        z.writestr(zi,f.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
sha=hashlib.sha256(zipfile_path.read_bytes()).hexdigest()
(zipfile_path.with_suffix(zipfile_path.suffix+'.sha256')).write_text(f'{sha}  {zipfile_path.name}\n',encoding='utf-8')
print(f'Created: {zipfile_path}')
print(f'SHA256:  {sha}')
