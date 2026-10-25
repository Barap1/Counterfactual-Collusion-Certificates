#!/usr/bin/env python3
"""Dependency-free checks for the maintained public reading path, never experiments."""
from pathlib import Path
from html.parser import HTMLParser
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


class EmbeddedLinks(HTMLParser):
    """Include explicitly sized README images in the public navigation check."""
    def __init__(self):
        super().__init__()
        self.targets = []
        self.missing_alt = False

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        key = 'src' if tag == 'img' else 'href' if tag == 'a' else None
        if key and attrs.get(key):
            self.targets.append(attrs[key])
        if tag == 'source' and attrs.get('srcset'):
            self.targets.extend(item.strip().split()[0] for item in attrs['srcset'].split(',') if item.strip())
        if tag == 'img' and not attrs.get('alt', '').strip():
            self.missing_alt = True


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
    pdf_links = 0
    for name in PAGES:
        path = ROOT / name
        if not path.is_file():
            failures.append(f'Missing reading-path page: {name}')
            continue
        source = prose(path)
        html = EmbeddedLinks()
        html.feed(source)
        if html.missing_alt:
            failures.append(f'{name}: image missing alternative text')
        targets = re.findall(r'!?\[[^\]]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)', source)
        for raw in targets + html.targets:
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
                # The normal existence check rejects placeholders. Once the owner
                # supplies the real PDF, adding its README link needs no code edit.
                pdf_links += 1
    ns = {'s': 'http://www.w3.org/2000/svg'}
    graphics = ('allocation-twins.svg', 'allocation-twins.dark.svg',
                'allocation-twins.mobile.svg', 'allocation-twins.mobile-dark.svg')
    for name in graphics:
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
    pdf_status = f'{pdf_links} existing README PDF links' if pdf_links else 'no README PDF link'
    print(f'PASS: {len(PAGES)} reading-path pages, {links} local links/anchors, {len(graphics)} editable SVG variants; {pdf_status}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
