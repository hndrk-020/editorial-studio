"""Check GitHub-ready distribution structure and stop accidental private-data commits."""
from __future__ import annotations
import json
import re
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
if (SKILL/'SKILL.md').exists():
    body=(SKILL/'SKILL.md').read_text(encoding='utf-8')
    require(body.startswith('---\n'),'SKILL.md missing YAML frontmatter')
    front=body.split('---',2)[1] if body.startswith('---') else ''
    require(re.search(r'^name:\s*editorial-studio\s*$',front,re.M) is not None,
           'Skill name must match installation name')
    require(re.search(r'^description:\s*\S',front,re.M) is not None,
           'Skill description is missing')
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
for path in ROOT.glob('**/.env'):
    if '.venv' not in path.parts:ERRORS.append(f'Unexpected secret-like file: {path.relative_to(ROOT)}')
if ERRORS:
    print('NOT GITHUB-READY:')
    for error in ERRORS:print(' - '+error)
    raise SystemExit(1)
print('PASS: distribution structure, skill mirror, plugin, local project-data boundary')
