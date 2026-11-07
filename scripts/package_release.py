"""Build a deterministic private source ZIP from a reviewed explicit inventory."""
from __future__ import annotations
import hashlib,json,stat,subprocess,sys,zipfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
LOCAL_DATA_COMPONENTS=frozenset({'projects','output','outputs','work','private','photos','marketing','account-data','.venv'})

def release_files(root: Path) -> list[Path]:
    names=json.loads((root/'release-files.json').read_text(encoding='utf-8'))
    if not isinstance(names,list) or not names or not all(isinstance(n,str) for n in names) or len(names)!=len(set(names)):
        raise ValueError('Invalid release inventory')
    result=[]
    for name in names:
        relative=PurePosixPath(name)
        if not relative.parts or relative.is_absolute() or relative.as_posix()!=name or any(p in ('','..','.') for p in relative.parts) or '\\' in name or ':' in name:
            raise ValueError('Unsafe release filename')
        if any(p.casefold() in LOCAL_DATA_COMPONENTS|{'.git','dist'} or p.casefold().startswith('.env') for p in relative.parts):
            raise ValueError('Private data cannot enter a release')
        current=root
        for part in relative.parts:
            current=current/part
            info=current.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info,'st_file_attributes',0)&getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',1024):
                raise ValueError('Linked release inputs are not allowed')
        if not stat.S_ISREG(info.st_mode) or info.st_nlink!=1 or info.st_size>2_000_000:
            raise ValueError('Release inputs must be bounded regular source files')
        result.append(current)
    return sorted(result)

def main():
    subprocess.run([sys.executable,str(ROOT/'scripts/validate_repository.py')],check=True)
    files=release_files(ROOT)
    version=json.loads((ROOT/'plugins/editorial-studio/plugin.json').read_text())['version']
    destination=ROOT/'dist';destination.mkdir(exist_ok=True)
    archive=destination/f'editorial-studio-v{version}-private-source.zip'
    from local_files import temporary_path,atomic_write
    temporary=temporary_path(archive)
    try:
        with zipfile.ZipFile(temporary,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as package:
            for path in files:
                member=zipfile.ZipInfo('editorial-studio/'+path.relative_to(ROOT).as_posix(),date_time=(2026,1,1,0,0,0))
                member.external_attr=0o100644<<16
                package.writestr(member,path.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
        temporary.replace(archive)
    finally:temporary.unlink(missing_ok=True)
    digest=hashlib.sha256(archive.read_bytes()).hexdigest()
    atomic_write(archive.with_suffix('.zip.sha256'),f'{digest}  {archive.name}\n'.encode())
    print(f'Created: {archive.name}\nSHA256: {digest}')

if __name__=='__main__':
    sys.path.insert(0,str(ROOT))
    main()
