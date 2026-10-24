#!/usr/bin/env python3
"""Offline preservation and structural checks against the task-entry snapshot."""
from collections import Counter
import html
import importlib.util
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / 'paper/build'
before = json.loads((BUILD / 'pub009_baseline.json').read_text())['draft']
after = (ROOT / 'paper/draft.md').read_text()
md = (BUILD / 'submission.md').read_text()
page = (BUILD / 'submission.html').read_text()
protected = r'\[(?:VERIFIED\s*:|OWNER\b|TODO\b)[^\]]*\]'
for kind in ['OWNER', 'TODO']:
    pattern = rf'\[{kind}\b[^\]]*\]'
    assert Counter(re.findall(pattern, before)) == Counter(re.findall(pattern, after))
    assert Counter(re.findall(pattern, after)) == Counter(re.findall(pattern, md))
old_evidence = Counter(re.findall(r'\[VERIFIED\s*:[^\]]*\]', before))
new_evidence = Counter(re.findall(r'\[VERIFIED\s*:[^\]]*\]', after))
assert not old_evidence - new_evidence
# Numeric tokens are unchanged apart from renamed task identifiers and added figure references.
def numeric_inventory(text):
    text = re.sub(protected, '', text)
    text = re.sub(r'`(?:docs|paper|ops)/[^`]+`|docs/release/LICENSES\.md', '', text)
    text = re.sub(r'(?m)^Figures? .+?shows? .+?\n', '', text)
    text = re.sub(r'\b(?:REV|DEV|EXP|STAT|PUB|ENG)-\d+\b', '', text)
    text = re.sub(r'\bDeviation [12]\b', '', text)
    return Counter(re.findall(r'\d+(?:\.\d+)*', text))
assert numeric_inventory(before) == numeric_inventory(after), (numeric_inventory(before)-numeric_inventory(after), numeric_inventory(after)-numeric_inventory(before))
# Citation occurrences, including appendix occurrences, remain exactly unchanged.
spec = importlib.util.spec_from_file_location('builder', BUILD / 'make_submission.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)
bib = builder.bib_entries((ROOT / 'paper/references_draft.bib').read_text())
def citations(text):
    result = []
    for bracket in re.findall(r'\[([^\[\]]+)\]', re.sub(protected, '', text)):
        keys = re.findall(r'@?([A-Za-z][A-Za-z0-9_:-]*)', bracket)
        if keys and all(key in bib for key in keys):
            result.append(tuple(keys))
    return Counter(result)
assert citations(before) == citations(after)
assert not re.search(r'\[(?:VERIFIED|PROVISIONAL|RESULT-PENDING)\b', md + page)
assert not re.search(r'REV-|DEV-0|STAT-|PUB-|ENG-|director|module-13', md + page, re.I)
assert re.findall(r'(?m)^## (.+)$', md) == re.findall(r'<h2>(.*?)</h2>', page)
svgs = re.findall(r'<svg\b.*?</svg>', page, re.S)
assert len(svgs) == 6
ids = []
for svg in svgs:
    tree = ET.fromstring(svg)
    assert tree.attrib.get('viewBox')
    ids.extend(node.attrib['id'] for node in tree.iter() if 'id' in node.attrib)
assert len(ids) == len(set(ids)), 'Duplicate SVG IDs'
assert page.count('<figcaption>') == 6
for n in ['1', '2', '3', '4', 'B1', 'B2']:
    assert f'<figcaption>Figure {n}.' in page
assert '<h2>References</h2>' in page
assert page.rfind('<h2>') == page.index('<h2>LLM Usage Statement</h2>')
result = {'original_verified_tags_preserved':sum(old_evidence.values()), 'added_path_provenance_tags':sum((new_evidence-old_evidence).values()), 'owner_todo_occurrences_preserved':len(re.findall(r'\[(?:OWNER|TODO)\b[^\]]*\]', before)), 'numeric_inventory_unchanged':True, 'citation_occurrences_unchanged':sum(citations(before).values()), 'svg_xml_valid':6, 'svg_ids_unique':True, 'internal_id_matches':0}
(BUILD / 'pub009_preservation_validation.json').write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
