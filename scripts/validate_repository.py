"""Check GitHub-ready distribution structure and stop accidental private-data commits."""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path
from hashlib import sha256

ROOT=Path(__file__).resolve().parents[1]
SKILL=ROOT/'.agents/skills/editorial-studio'
PLUGIN=ROOT/'plugins/editorial-studio'
ERRORS=[]

def require(ok,msg):
    if not ok:ERRORS.append(msg)

require((ROOT/'.gitignore').exists(),'Missing .gitignore')
require((ROOT/'SECURITY.md').exists(),'Missing security policy')
require((ROOT/'.github/workflows/ci.yml').exists(),'Missing GitHub CI')
require((SKILL/'SKILL.md').exists(),'Missing repo skill')
require((PLUGIN/'plugin.json').exists(),'Missing portable plugin manifest')
require((ROOT/'.agents/plugins/marketplace.json').exists(),'Missing repo plugin marketplace')
# Local private projects may exist on a developer computer; they are Git-ignored
# and explicitly excluded by the release packager. They are not source files.
ignore=(ROOT/'.gitignore').read_text(encoding='utf-8') if (ROOT/'.gitignore').exists() else ''
require('/projects/' in ignore and '/output/' in ignore,
        'Private projects and PDF output must be excluded from Git')
for directory in ('outputs','work','private','photos','marketing','account-data'):
    require('/'+directory+'/' in ignore,'Local-only directory must be excluded from Git: '+directory)
# Ignore rules do not protect files already in the index (or force-added files).
# Inspect the actual index when in a checkout; extracted release sources have no .git.
if (ROOT/'.git').exists():
    try:
        tracked=subprocess.run(['git','-C',str(ROOT),'ls-files','-z'],check=True,capture_output=True,timeout=15).stdout.decode('utf-8').split('\0')
        from package_release import LOCAL_DATA_COMPONENTS
        for name in filter(None,tracked):
            top=name.split('/',1)[0].casefold()
            require(top not in LOCAL_DATA_COMPONENTS and not (top.startswith('.env') and top!='.env.example'),
                    'Local-only data is tracked in Git: '+name)
    except (OSError,subprocess.SubprocessError,UnicodeError) as ex:
        ERRORS.append('Could not inspect tracked-file boundary: '+str(ex))
if (SKILL/'SKILL.md').exists():
    body=(SKILL/'SKILL.md').read_text(encoding='utf-8')
    require(body.startswith('---\n'),'SKILL.md missing YAML frontmatter')
    front=body.split('---',2)[1] if body.startswith('---') else ''
    require(re.search(r'^name:\s*editorial-studio\s*$',front,re.M) is not None,
           'Skill name must match installation name')
    require(re.search(r'^description:\s*\S',front,re.M) is not None,
           'Skill description is missing')
source_names={p.relative_to(SKILL).as_posix() for p in SKILL.rglob('*') if p.is_file()}
mirror=PLUGIN/'skills/editorial-studio'
mirror_names={p.relative_to(mirror).as_posix() for p in mirror.rglob('*') if p.is_file()}
require(source_names==mirror_names,'Skill directory file lists differ')
for sf in sorted(SKILL.rglob('*')):
    if sf.is_file():
        relative=sf.relative_to(SKILL)
        pf=PLUGIN/'skills/editorial-studio'/relative
        require(pf.exists() and pf.read_bytes()==sf.read_bytes(),
                f'Plugin skill mirror is missing or stale: {relative}')
if (PLUGIN/'plugin.json').exists():
    data=json.loads((PLUGIN/'plugin.json').read_text(encoding='utf-8'))
    require(data.get('name')=='editorial-studio','Portable plugin name mismatch')
    require(re.fullmatch(r'\d+\.\d+\.\d+',data.get('version','')) is not None,
            'Plugin version must be SemVer')
try:
    marketplace=json.loads((ROOT/'.agents/plugins/marketplace.json').read_text(encoding='utf-8'))
    require(any(x.get('source',{}).get('path')=='./plugins/editorial-studio' for x in marketplace.get('plugins',[])),
            'Local marketplace must reference portable plugin directory')
except Exception as ex:ERRORS.append(f'Invalid marketplace JSON: {ex}')
for reference in re.findall(r'references/[A-Za-z0-9_.-]+\.md',(SKILL/'SKILL.md').read_text(encoding='utf-8')):
    require((SKILL/reference).is_file(),'Missing skill reference: '+reference)
try:
    from package_release import release_files
    inventory={p.relative_to(ROOT).as_posix() for p in release_files(ROOT)}
    required={'studio.py','engine.py','creative.py','photo_researcher.py','image_transport.py','finalized_edition.py','local_files.py','requirements.txt','requirements.lock','release-files.json'}
    require(required<=inventory,'Release inventory omits runtime files')
    require(all('.agents/skills/editorial-studio/'+n in inventory and 'plugins/editorial-studio/skills/editorial-studio/'+n in inventory for n in source_names),'Release inventory omits skill resources')
except (OSError,ValueError,TypeError) as ex:ERRORS.append('Invalid release inventory: '+str(ex))
if ERRORS:
    print('NOT GITHUB-READY:')
    for error in ERRORS:print(' - '+error)
    raise SystemExit(1)
print('PASS: distribution structure, skill mirror, plugin, local project-data boundary')
