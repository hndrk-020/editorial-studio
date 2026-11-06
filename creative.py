"""Creative brief, dual art directions, and general-purpose visual research queries.

No external API calls and no claims of AI evaluation of reference URLs. The URLs
are editor-provided inspiration and require human/agent inspection to interpret.
"""
from __future__ import annotations

from urllib.parse import quote, urlparse

DIRECTIONS = {
    'field-notes': {
        'id': 'field-notes', 'name': 'Field Notes', 'tagline': 'Quiet, tactile, unforgettable.',
        'personality': 'Considered, intimate, premium and enduring.',
        'palette': {'paper': '#F7F3E9', 'ink': '#1C302C', 'accent': '#AF7352', 'secondary': '#71877A', 'line': '#D8D4C7'},
        'typography': 'Elegant large serif headlines paired with restrained sans-serif labels.',
        'photography': 'Full-bleed natural-light images; deliberate white space; authentic documentary details.',
        'layout': 'Slow editorial rhythm. One hero image per story; spacious captions and small numbered details.',
        'avoid': 'Busy grids, excessive badges, stock-image clichés and decorative clutter.',
    },
    'bold-perspective': {
        'id': 'bold-perspective', 'name': 'Bold Perspective', 'tagline': 'A point of view on every page.',
        'personality': 'Confident, contemporary, energetic and editorial.',
        'palette': {'paper': '#FFF4E8', 'ink': '#202D33', 'accent': '#E76748', 'secondary': '#347C88', 'line': '#D6CBC1'},
        'typography': 'Oversized strong sans-serif headlines, compact serif commentary and expressive numbering.',
        'photography': 'Dynamic crops, cinematic contrast, intimate details and confident image pairings.',
        'layout': 'Bolder title blocks, larger issue numbers, graphic separator bars and alternating emphasis.',
        'avoid': 'Generic corporate cards, over-illustration, overcrowded pages and unverified visual assets.',
    }
}
CATEGORIES = {'travel','restaurants','people','architecture','products','real-estate','events','business','culture','other'}
DISTRIBUTIONS = {'private','internal','public'}


def valid_inspiration(url: str) -> bool:
    if not url:
        return True
    p = urlparse(url)
    return p.scheme == 'https' and bool(p.hostname) and not p.username and not p.password


def normalize_brief(raw: dict | None, kind: str = 'magazine') -> dict:
    raw = raw or {}
    category = str(raw.get('category','other')).strip()
    if category not in CATEGORIES: category = 'other'
    distribution = str(raw.get('distribution','private')).strip()
    if distribution not in DISTRIBUTIONS: distribution = 'private'
    brief = {
        'subject': str(raw.get('subject','')).strip()[:220],
        'purpose': str(raw.get('purpose','')).strip()[:450],
        'audience': str(raw.get('audience','')).strip()[:250],
        'preferred_style': str(raw.get('preferred_style','')).strip()[:400],
        'reference_url': str(raw.get('reference_url','')).strip()[:750],
        'category': category,
        'distribution': distribution,
        'language': str(raw.get('language','nl')).strip()[:20],
        'format': kind,
        'reference_reviewed': False,
    }
    if not valid_inspiration(brief['reference_url']):
        raise ValueError('Example URL must be a complete https:// address, or leave it blank.')
    return brief


def brief_checks(brief: dict) -> list[str]:
    if not isinstance(brief, dict):
        return ['Creative brief missing']
    required = ('subject','purpose','audience','preferred_style')
    errors = [f'Creative brief: {key.replace("_", " ")} missing' for key in required if not str(brief.get(key,'')).strip()]
    if not valid_inspiration(brief.get('reference_url','')):
        errors.append('Creative brief: example URL invalid')
    return errors


def propose_directions(brief: dict) -> list[dict]:
    """Two *distinct* paths. Honest: deterministic direction drafts, not LLM-generated art."""
    subject = brief.get('subject','this story').strip()[:100] or 'your story'
    style = brief.get('preferred_style','editorial').strip()[:120] or 'editorial'
    ref = brief.get('reference_url','')
    result=[]
    for key in ('field-notes','bold-perspective'):
        d = dict(DIRECTIONS[key])
        d['palette'] = dict(DIRECTIONS[key]['palette'])
        d['rationale'] = (f'An interpretation of “{style}” for {subject}: '
                          + ('more intimate, classic, and photography-led.' if key=='field-notes' else 'more graphic, contemporary, and energetic.'))
        d['reference_note'] = (f'Review {ref} for editorial inspiration; do not imitate its logo, proprietary graphics or exact layouts.'
                               if ref else 'No inspiration URL supplied; art direction is based on the written brief.')
        result.append(d)
    return result


def candidate_queries(doc: dict, slot: str) -> dict:
    """Return *research* links only. They are not evidence of a photo license or identity."""
    brief=doc.get('brief',{}) or {}
    story=next((s for s in doc.get('stories',[]) if s.get('id')==slot),None)
    if slot=='hero':
        subject=brief.get('subject') or doc.get('title','cover')
        usage='cover'
    elif story:
        subject=story.get('title','') or doc.get('title','')
        usage='story'
    else: raise ValueError('Unknown image slot')
    category=brief.get('category','other')
    search = f'{subject} {category} original photography official high resolution'.strip()
    return {
        'slot':slot,'subject':subject,'usage':usage,'category':category,
        'query':search,
        'caution':'Search results are only candidates. Verify exact subject, provenance, image rights and resolution before approval.',
        'sources':[
            {'name':'Official photos / media kit', 'url':'https://www.google.com/search?q='+quote(f'"{subject}" official photos media kit press')},
            {'name':'Image search', 'url':'https://www.google.com/search?tbm=isch&q='+quote(search)},
            {'name':'Wikimedia Commons', 'url':'https://commons.wikimedia.org/w/index.php?search='+quote(subject)+'&title=Special%3AMediaSearch&type=image'},
            {'name':'Licensed imagery', 'url':'https://www.google.com/search?q='+quote(f'{subject} licensed photo stock editorial')},
        ],
        'checklist':[
            'Confirm what and who is pictured; do not assume the search result is correct.',
            'Find the original website or permission/license statement.',
            'Credit photographer or organization accurately.',
            'Save a real image locally; do not rely on a preview thumbnail.',
            'Inspect crop, quality, rights and intended distribution.',
        ]
    }
