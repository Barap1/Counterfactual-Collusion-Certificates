#!/usr/bin/env python3
"""Small dependency-free Markdown renderer for the paper preview."""
import html, re, sys
from pathlib import Path

src = Path(sys.argv[1]).read_text(encoding='utf-8')

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
# Embed any present planned SVGs inline; absent planned figures remain explicitly pending.
figdir=Path('paper/figures')
if figdir.exists():
    for svg in sorted(figdir.glob('*.svg')):
        body += '\n<figure>'+svg.read_text(encoding='utf-8')+'<figcaption>'+html.escape(svg.stem)+'</figcaption></figure>'
page='''<!doctype html><html><head><meta charset="utf-8"><title>CCC draft preview</title><style>
@page{size:letter;margin:1in}html{font-size:11pt}body{font-family:"Times New Roman",serif;line-height:1.28;color:#171717;max-width:6.5in;margin:0 auto}h1{font-size:19pt;line-height:1.08}h2{font-size:14pt;margin-top:1.1em;break-after:avoid}h3{font-size:11.5pt;margin-top:.9em;break-after:avoid}p{margin:.45em 0;text-align:justify}table{width:100%;border-collapse:collapse;font-size:9.5pt;margin:.6em 0;break-inside:avoid}th,td{border:1px solid #777;padding:3px 5px;vertical-align:top}th{background:#eee}blockquote{border-left:2px solid #777;padding-left:.6em;margin-left:.5em}code{font-size:9pt}li{margin:.2em 0}hr{border:0;border-top:1px solid #aaa}a{color:inherit;text-decoration:none}figure{break-inside:avoid}svg{max-width:100%;height:auto}
.status{font-family:Arial,sans-serif;font-size:9pt;font-weight:bold;color:#7a1d1d;border:1px solid #7a1d1d;padding:7px;margin:0 0 12px}
</style></head><body><div class="status">DRAFT PREVIEW — RESULT-PENDING placeholders remain; not for submission.</div>'''+body+'</body></html>'
Path('paper/build/draft.html').write_text(page,encoding='utf-8')
