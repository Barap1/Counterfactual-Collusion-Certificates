#!/usr/bin/env python3
"""Dependency-free checks for the maintained public reading path, never experiments."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
PAGES = ('README.md', 'CCC_START_HERE.md', 'docs/README.md', 'docs/RESULTS.md',
         'docs/REPRODUCING.md', 'docs/LIMITATIONS.md', 'docs/assets/README.md',
         'docs/archive/README.md', 'paper/README.md', 'docs/release/CHECKLIST.md',
         'demo/explorer/README.md', 'paper/final/FIGURE_EVIDENCE_MAP.md', 'NOTICE.md',
         'paper/final/manuscript.md', 'paper/final/CLAIMS_LEDGER.md')


def prose(path):
    return re.sub(r'(?ms)^```.*?^```[^\n]*', '', path.read_text(encoding='utf-8'))


def anchors(path):
    result = set()
    counts = {}
    for heading in re.findall(r'(?m)^#{1,6}\s+(.+?)\s*#*$', prose(path)):
        slug = re.sub(r'[^\w\- ]', '', heading.lower()).replace(' ', '-')
        suffix = counts.get(slug, 0)
        counts[slug] = suffix + 1
        result.add(slug if not suffix else f'{slug}-{suffix}')
    return result


def main():
    failures = []
    links = 0
    for name in PAGES:
        path = ROOT / name
        if not path.is_file():
            failures.append(f'Missing reading-path page: {name}')
            continue
        source = prose(path)
        for raw in re.findall(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)', source):
            href = urlsplit(raw.strip('<>'))
            if href.scheme or href.netloc:
                continue  # external access is intentionally not performed
            target = (path.parent / unquote(href.path)).resolve() if href.path else path
            links += 1
            if not target.exists():
                failures.append(f'{name}: missing {raw}')
            elif href.fragment and target.suffix == '.md' and unquote(href.fragment) not in anchors(target):
                failures.append(f'{name}: missing anchor {raw}')
            if name == 'README.md' and target.suffix.lower() == '.pdf':
                failures.append('README must not link a paper PDF before the owner adds it')
    ns = {'s': 'http://www.w3.org/2000/svg'}
    for name in ('allocation-twins.svg', 'evidence-steps.svg'):
        svg = ET.parse(ROOT / 'docs/assets' / name).getroot()
        if svg.find('s:title', ns) is None or svg.find('s:desc', ns) is None:
            failures.append(f'{name}: missing accessible title/description')
        if svg.findall('.//s:script', ns) or svg.findall('.//s:foreignObject', ns):
            failures.append(f'{name}: unsupported active content')
        if not svg.findall('.//s:text', ns) or not svg.get('viewBox'):
            failures.append(f'{name}: missing editable text/viewBox')
    if failures:
        print('\n'.join(failures), file=sys.stderr)
        return 1
    print(f'PASS: {len(PAGES)} reading-path pages, {links} local links/anchors, 2 editable SVGs; no README PDF link')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
