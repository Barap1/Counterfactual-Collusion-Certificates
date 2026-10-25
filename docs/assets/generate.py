"""Original, editable README diagrams. Run from the repository root; SVG only."""
from pathlib import Path
from html import escape

P = Path('docs/assets')
P.mkdir(exist_ok=True)
INK, MUTED, LINE = '#19313e', '#4c606a', '#c9d2d3'
PAPER, TEAL, RUST = '#faf9f6', '#006a60', '#854925'


def start(width, height, title, description):
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>',
        f'<rect width="{width}" height="{height}" fill="{PAPER}"/>',
        f'<g font-family="Arial, Helvetica, sans-serif" fill="{INK}">',
    ]


def text(svg, x, y, value, size=24, color=INK, weight='400'):
    svg.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
               f'font-weight="{weight}">{escape(value)}</text>')


def rect(svg, x, y, width, height, fill, stroke='none', radius=8):
    svg.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
               f'rx="{radius}" fill="{fill}" stroke="{stroke}"/>')


def arrow(svg, x, y, color):
    svg.append(f'<path d="M{x} {y}v20m-5 -5 5 5 5 -5" fill="none" '
               f'stroke="{color}" stroke-width="2"/>')


def save(name, svg):
    (P / name).write_text('\n'.join([*svg, '</g></svg>']) + '\n')


svg = start(640, 536, 'Same replay, different programmed policies',
    'Constructed deterministic allocation pair. Both teams send the same message and assign '
    'the task to dispatch. Mean outsider reward is 14 with the message and 19 after removal '
    'in both worlds. Lowering each outsider task cost by 10 separates their programmed '
    'responses: the permitted efficiency policy switches allocation and yields 29; the '
    'prohibited coalition-protecting policy keeps allocation and yields 14. The probe '
    'separates only these specified policies; identical replay alone does not settle attribution.')
text(svg, 24, 40, 'Same replay. Different policies.', 30, weight='700')
rect(svg, 24, 62, 592, 160, '#ffffff', LINE)
text(svg, 44, 94, 'SAME MESSAGE · SAME DISPATCH ALLOCATION', 20, MUTED, '700')
text(svg, 44, 128, '“Please allocate the contested task', 23, weight='700')
text(svg, 44, 157, 'to our dispatch team.”', 23, weight='700')
text(svg, 44, 199, 'Mean outsider reward: 14 → 19 after removal', 23)
rect(svg, 24, 244, 592, 52, INK)
text(svg, 44, 277, 'Probe: lower each outsider’s task cost by 10.', 23, '#ffffff')
arrow(svg, 166, 305, TEAL)
arrow(svg, 474, 305, RUST)
for x, color, background, title, permission, response, reward in [
    (24, TEAL, '#e8f2ef', 'Efficiency policy', '(permitted)', 'Switches allocation', '29'),
    (332, RUST, '#f4ece5', 'Coalition protection', '(prohibited)', 'Keeps allocation', '14'),
]:
    rect(svg, x, 332, 284, 140, background)
    text(svg, x + 18, 365, title, 24, color, '700')
    text(svg, x + 18, 392, permission, 22, color)
    text(svg, x + 18, 425, response, 23, INK, '700')
    text(svg, x + 18, 455, f'Outsider reward: {reward}', 22)
text(svg, 24, 514, 'Same replay alone does not settle attribution.', 24, weight='700')
save('allocation-twins.svg', svg)

svg = start(640, 246, 'Claims and the evidence they require',
    'Observation requires visible communication. Causal influence needs a valid controlled '
    'replay showing a nonzero effect. Harmful exposure needs outsider outcome measures. Attribution '
    'additionally requires a declared policy and evidence distinguishing legitimate '
    'alternatives. These are requirements, not automatic conclusions; otherwise attribution '
    'remains unresolved.')
text(svg, 28, 31, 'Claim', 22, MUTED, '700')
text(svg, 264, 31, 'Evidence needed', 22, MUTED, '700')
for i, (claim, evidence) in enumerate([
    ('Observation', 'Visible communication'),
    ('Causal influence', 'Valid replay + nonzero effect'),
    ('Harmful exposure', 'Outsider outcome measures'),
    ('Attribution', 'Policy + separating evidence'),
]):
    y = 48 + i * 47
    rect(svg, 16, y, 608, 42, INK if i == 3 else '#ffffff', LINE if i < 3 else 'none', 5)
    text(svg, 28, y + 28, claim, 22, '#ffffff' if i == 3 else INK, '700')
    text(svg, 264, y + 28, evidence, 22, '#e0eeec' if i == 3 else MUTED)
save('evidence-steps.svg', svg)
