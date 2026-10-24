#!/usr/bin/env python3
"""Small dependency-free Markdown renderer for the paper preview."""
import html, re, sys
from pathlib import Path

src = Path(sys.argv[1]).read_text(encoding='utf-8')
output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('paper/build/draft.html')

def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'`([^`]+)`', r'<code>\1</code>', s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*([^*]+)\*', r'<em>\1</em>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    return s

lines = src.splitlines()
out = []
i = 0
while i < len(lines):
    raw = lines[i]
    s = raw.strip()
    if not s:
        i += 1; continue
    figure = re.fullmatch(r'!\[([^\]]+)\]\(([^)]+\.svg)\)', s)
    if figure:
        caption, filename = figure.groups()
        svg_path = (Path(sys.argv[1]).resolve().parent / filename).resolve()
        svg = svg_path.read_text(encoding='utf-8')
        # Strip XML/DTD preambles without loading external entities.
        svg = svg[svg.index('<svg'):svg.rindex('</svg>') + len('</svg>')]
        prefix = f'embedded_{len(out)}_'
        # Matplotlib reuses IDs across files; namespace them within the document.
        ids = re.findall(r'\bid="([^"]+)"', svg)
        for identifier in sorted(set(ids), key=len, reverse=True):
            svg = svg.replace(f'id="{identifier}"', f'id="{prefix}{identifier}"')
            svg = svg.replace(f'href="#{identifier}"', f'href="#{prefix}{identifier}"')
            svg = svg.replace(f'url(#{identifier})', f'url(#{prefix}{identifier})')
        # A width-only SVG otherwise clips when its intrinsic width exceeds the column.
        if not re.search(r'\bviewBox=', svg.split('>', 1)[0]):
            width = re.search(r'\bwidth="([0-9.]+)(?:px|pt)?"', svg.split('>', 1)[0])
            height = re.search(r'\bheight="([0-9.]+)(?:px|pt)?"', svg.split('>', 1)[0])
            if width and height:
                svg = svg.replace('<svg ', f'<svg viewBox="0 0 {width.group(1)} {height.group(1)}" ', 1)
            else:
                raise ValueError(f'SVG needs a viewBox or numeric dimensions: {svg_path}')
        out.append('<figure role="group" aria-label="'+html.escape(caption, quote=True)+'">'+svg+'<figcaption>'+inline(caption)+'</figcaption></figure>')
        i += 1
        continue
    if s.startswith('|') and i + 1 < len(lines) and re.match(r'^\s*\|?\s*:?-{3}', lines[i+1]):
        rows=[]
        while i < len(lines) and lines[i].strip().startswith('|'):
            cells=[c.strip() for c in lines[i].strip().strip('|').split('|')]
            if not all(re.fullmatch(r':?-{3,}:?', c) for c in cells): rows.append(cells)
            i += 1
        if rows:
            out.append('<table><thead><tr>'+''.join('<th>'+inline(c)+'</th>' for c in rows[0])+'</tr></thead><tbody>')
            for row in rows[1:]: out.append('<tr>'+''.join('<td>'+inline(c)+'</td>' for c in row)+'</tr>')
            out.append('</tbody></table>')
        continue
    if s.startswith('### '): out.append('<h3>'+inline(s[4:])+'</h3>'); i+=1; continue
    if s.startswith('## '): out.append('<h2>'+inline(s[3:])+'</h2>'); i+=1; continue
    if s.startswith('# '): out.append('<h1>'+inline(s[2:])+'</h1>'); i+=1; continue
    if s.startswith('---'):
        out.append('<hr>'); i+=1; continue
    if s.startswith('- '):
        out.append('<ul>')
        while i<len(lines) and lines[i].strip().startswith('- '):
            out.append('<li>'+inline(lines[i].strip()[2:])+'</li>'); i+=1
        out.append('</ul>'); continue
    if re.match(r'^\d+\.\s', s):
        out.append('<ol>')
        while i<len(lines) and re.match(r'^\s*\d+\.\s', lines[i]):
            out.append('<li>'+inline(re.sub(r'^\s*\d+\.\s*','',lines[i]))+'</li>'); i+=1
        out.append('</ol>'); continue
    if s.startswith('> '): out.append('<blockquote>'+inline(s[2:])+'</blockquote>'); i+=1; continue
    para=[s]; i+=1
    while i<len(lines) and lines[i].strip() and not re.match(r'^(#{1,3}\s|[-*]\s|\d+\.\s|\||---|>\s)',lines[i].strip()):
        para.append(lines[i].strip()); i+=1
    out.append('<p>'+inline(' '.join(para))+'</p>')

body='\n'.join(out)
# SVGs are embedded by the submission builder using the captions from figures_plan.md.
page='''<!doctype html><html><head><meta charset="utf-8"><title>CCC submission</title><style>
@page{size:letter;margin:1in}html{font-size:11pt}body{font-family:"Times New Roman",serif;line-height:1.28;color:#171717;max-width:6.5in;margin:0 auto}h1{font-size:19pt;line-height:1.08}h2{font-size:14pt;margin-top:1.1em;break-after:avoid}h3{font-size:11.5pt;margin-top:.9em;break-after:avoid}p{margin:.45em 0;text-align:justify}table{width:100%;border-collapse:collapse;font-size:9.5pt;margin:.6em 0;break-inside:avoid}th,td{border:1px solid #777;padding:3px 5px;vertical-align:top}th{background:#eee}blockquote{border-left:2px solid #777;padding-left:.6em;margin-left:.5em}code{font-size:9pt}li{margin:.2em 0}hr{border:0;border-top:1px solid #aaa}a{color:inherit;text-decoration:none}figure{break-inside:avoid;page-break-inside:avoid;margin:1em auto;text-align:center;max-width:100%}figure svg{display:block;width:auto;height:auto;max-width:100%;max-height:3.3in;margin:0 auto}figure[aria-label^="Figure 4."] svg{max-height:4in}figcaption{font-size:9pt;line-height:1.25;margin-top:.4em;text-align:center}
.status{font-family:Arial,sans-serif;font-size:9pt;font-weight:bold;color:#7a1d1d;border:1px solid #7a1d1d;padding:7px;margin:0 0 12px}
</style></head><body>'''+body+'</body></html>'
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(page,encoding='utf-8')
