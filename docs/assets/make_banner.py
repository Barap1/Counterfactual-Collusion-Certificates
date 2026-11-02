#!/usr/bin/env python3
"""Generate the README header banner (wide and narrow SVG).

Colors follow the paper figures and the evidence explorer: paper #f8f5f1,
ink #193025, forest #194b37, rule #d5dbd6, brown #85543b, muted #65635b.
Text uses Old Standard TT (SIL OFL 1.1, bundled in paper/v2/fonts/), subset
to the glyphs used and embedded, because README images cannot load web fonts.
It also writes the tech-stack badges in docs/assets/badges/.
The plotted values are the allocation-twin outsider rewards for seed
19693329 (docs/MATH.md section 4). Needs fontTools and brotli; no network.

    python3 docs/assets/make_banner.py
"""
import base64
import io
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
FONTS = ROOT / "paper/v2/fonts"
PAPER, INK, FOREST, RULE, BROWN, MUTED, CARD_LINE = (
    "#f8f5f1", "#193025", "#194b37", "#d5dbd6", "#85543b", "#65635b", "#e3dfda")
SANS = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
SERIF = "'CCC Serif', 'Old Standard TT', Georgia, serif"

TITLE1, TITLE2 = "When Cooperation Looks", "Like Collusion"
SUBTITLE = "The limits of counterfactual auditing in multi-agent AI"
OVERLINE = "COUNTERFACTUAL COLLUSION CERTIFICATES"
BYLINE = "Aarav Patel  ·  Georgia Institute of Technology"
REWARDS = [14, 19, 14, 19]          # F, K, S/N, J outsider reward: identical for both teams
SPLIT = {"permitted": 29, "prohibited": 14}   # factual arm under the cost probe


def font_face(filename, weight, style, text):
    font = TTFont(FONTS / filename)
    options = subset.Options()
    options.flavor = "woff2"
    options.layout_features = ["kern", "liga"]
    options.name_IDs = ["*"]           # keep copyright and license records
    sub = subset.Subsetter(options)
    sub.populate(text=text)
    sub.subset(font)
    buffer = io.BytesIO()
    font.flavor = "woff2"
    font.save(buffer)
    data = base64.b64encode(buffer.getvalue()).decode()
    return (f"@font-face{{font-family:'CCC Serif';font-weight:{weight};font-style:{style};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2');}}")


def styles():
    regular_text = TITLE1 + TITLE2
    italic_text = SUBTITLE
    return "".join([font_face("OldStandard-Regular.ttf", 400, "normal", regular_text),
                    font_face("OldStandard-Italic.ttf", 400, "italic", italic_text)])


def motif(x0, y_base, step, scale, label_size):
    """Outsider reward by evidence level: one shared path, then the probe split."""
    xs = [x0 + i * step for i in range(5)]
    y = lambda r: y_base - (r - 10) * scale
    parts = []
    shared = " ".join(f"{'M' if i == 0 else 'L'}{xs[i]} {y(r)}" for i, r in enumerate(REWARDS))
    parts.append(f'<path d="{shared}" fill="none" stroke="{INK}" stroke-width="2.5" stroke-linejoin="round"/>')
    for i, r in enumerate(REWARDS):
        parts.append(f'<circle cx="{xs[i]}" cy="{y(r)}" r="5" fill="{INK}"/>')
    x3, y3 = xs[3], y(REWARDS[3])
    for name, color in (("permitted", FOREST), ("prohibited", BROWN)):
        r = SPLIT[name]
        dash = '' if name == "permitted" else ' stroke-dasharray="7 5"'
        parts.append(f'<path d="M{x3} {y3} L{xs[4]} {y(r)}" fill="none" stroke="{color}" stroke-width="2.5"{dash}/>')
        parts.append(f'<circle cx="{xs[4]}" cy="{y(r)}" r="6" fill="{PAPER}" stroke="{color}" stroke-width="2.5"/>')
        parts.append(f'<text x="{xs[4] + 14}" y="{y(r) + label_size * 0.35:.0f}" fill="{color}" font-family="{SANS}" '
                     f'font-size="{label_size}" font-weight="600">{r} {name}</text>')
    axis_y = y_base + 26
    parts.append(f'<line x1="{xs[0] - 14}" y1="{axis_y - 14}" x2="{xs[4] + 14}" y2="{axis_y - 14}" stroke="{RULE}" stroke-width="1.5"/>')
    for i, x in enumerate(xs):
        parts.append(f'<text x="{x}" y="{axis_y + 6}" fill="{MUTED}" font-family="{SANS}" font-size="{label_size}" '
                     f'text-anchor="middle">I{i}</text>')
    parts.append(f'<text x="{(xs[0] + xs[3]) / 2}" y="{axis_y + 34}" fill="{MUTED}" font-family="{SANS}" '
                 f'font-size="{label_size - 1}" text-anchor="middle">same evidence for both teams</text>')
    parts.append(f'<text x="{xs[4]}" y="{axis_y + 34}" fill="{MUTED}" font-family="{SANS}" '
                 f'font-size="{label_size - 1}" text-anchor="middle">cost probe</text>')
    return "\n    ".join(parts)


DESC = ("Banner: When Cooperation Looks Like Collusion, the limits of counterfactual auditing in multi-agent AI, "
        "by Aarav Patel, Georgia Institute of Technology. A small chart shows the outsider reward for two constructed "
        "teams across evidence levels I0 to I3 (14, 19, 14, 19), identical for both, then at I4 a cost probe splits "
        "them: 29 for the permitted team and 14 for the prohibited team.")


def svg(width, height, body, css):
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-labelledby="t d">
  <title id="t">CCC: When Cooperation Looks Like Collusion</title>
  <desc id="d">{DESC}</desc>
  <style>{css}</style>
  <rect x="0.75" y="0.75" width="{width - 1.5}" height="{height - 1.5}" rx="16" fill="{PAPER}" stroke="{CARD_LINE}" stroke-width="1.5"/>
  {body}
</svg>
"""


def wide(css):
    text = f"""<text x="64" y="76" fill="{FOREST}" font-family="{SANS}" font-size="15" font-weight="700" letter-spacing="2.4">{OVERLINE}</text>
  <text x="62" y="146" fill="{INK}" font-family="{SERIF}" font-size="54">{TITLE1}</text>
  <text x="62" y="206" fill="{INK}" font-family="{SERIF}" font-size="54">{TITLE2}</text>
  <text x="64" y="252" fill="{MUTED}" font-family="{SERIF}" font-style="italic" font-size="25">{SUBTITLE}</text>
  <line x1="64" y1="282" x2="160" y2="282" stroke="{FOREST}" stroke-width="2"/>
  <text x="64" y="316" fill="{MUTED}" font-family="{SANS}" font-size="16">{BYLINE}</text>
  <line x1="800" y1="56" x2="800" y2="304" stroke="{RULE}" stroke-width="1.5"/>
  <text x="840" y="76" fill="{MUTED}" font-family="{SANS}" font-size="13" font-weight="700" letter-spacing="1.8">OUTSIDER REWARD</text>
    {motif(850, 246, 66, 6.2, 16)}"""
    return svg(1280, 360, text, css)


def narrow(css):
    text = f"""<text x="48" y="70" fill="{FOREST}" font-family="{SANS}" font-size="17" font-weight="700" letter-spacing="2">{OVERLINE}</text>
  <text x="46" y="146" fill="{INK}" font-family="{SERIF}" font-size="56">{TITLE1}</text>
  <text x="46" y="208" fill="{INK}" font-family="{SERIF}" font-size="56">{TITLE2}</text>
  <text x="48" y="256" fill="{MUTED}" font-family="{SERIF}" font-style="italic" font-size="25">The limits of counterfactual auditing</text>
  <text x="48" y="290" fill="{MUTED}" font-family="{SERIF}" font-style="italic" font-size="25">in multi-agent AI</text>
  <line x1="48" y1="322" x2="144" y2="322" stroke="{FOREST}" stroke-width="2"/>
  <text x="48" y="358" fill="{MUTED}" font-family="{SANS}" font-size="19">{BYLINE}</text>
  <line x1="48" y1="396" x2="672" y2="396" stroke="{RULE}" stroke-width="1.5"/>
  <text x="48" y="436" fill="{MUTED}" font-family="{SANS}" font-size="15" font-weight="700" letter-spacing="1.8">OUTSIDER REWARD</text>
    {motif(110, 600, 104, 6.6, 19)}"""
    return svg(720, 700, text, css)


BADGES = [  # (file, label, value, value color): the project's actual stack
    ("python", "python", "3.12+", FOREST),
    ("analysis", "analysis", "NumPy \u00b7 SciPy", FOREST),
    ("inference", "local inference", "Ollama \u00b7 gemma4:26b", FOREST),
    ("environment", "environment", "Colosseum \u00b7 Terrarium", FOREST),
    ("compute", "benchmark compute", "Modal (Linux)", FOREST),
    ("explorer", "explorer", "vanilla JS, offline", FOREST),
    ("license", "license", "MIT", BROWN),
]
METRIC_FONT = Path("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf")


def text_width(text, size):
    """Advance width in Liberation Sans, metric-compatible with Arial and Helvetica."""
    font = TTFont(METRIC_FONT)
    cmap, hmtx, upem = font.getBestCmap(), font["hmtx"], font["head"].unitsPerEm
    return sum(hmtx[cmap.get(ord(c), cmap[ord("?")])][0] for c in text) * size / upem


def badge(label, value, color, size=12, pad=8, height=24):
    lw, vw = text_width(label, size) + 2 * pad, text_width(value, size) + 2 * pad
    w = lw + vw
    font = "Helvetica, Arial, 'Liberation Sans', sans-serif"
    y = height / 2 + size * 0.36
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w:.0f}" height="{height}" viewBox="0 0 {w:.1f} {height}" role="img" aria-label="{label}: {value}">
  <title>{label}: {value}</title>
  <clipPath id="r"><rect width="{w:.1f}" height="{height}" rx="4"/></clipPath>
  <g clip-path="url(#r)"><rect width="{lw:.1f}" height="{height}" fill="{INK}"/><rect x="{lw:.1f}" width="{vw:.1f}" height="{height}" fill="{color}"/></g>
  <g font-family="{font}" font-size="{size}">
    <text x="{pad}" y="{y:.1f}" fill="#e9eee7" textLength="{lw - 2 * pad:.1f}" lengthAdjust="spacingAndGlyphs">{label}</text>
    <text x="{lw + pad:.1f}" y="{y:.1f}" fill="#ffffff" textLength="{vw - 2 * pad:.1f}" lengthAdjust="spacingAndGlyphs">{value}</text>
  </g>
</svg>
"""


def main():
    css = styles()
    (OUT / "banner.svg").write_text(wide(css), encoding="utf-8")
    (OUT / "banner.mobile.svg").write_text(narrow(css), encoding="utf-8")
    (OUT / "badges").mkdir(exist_ok=True)
    for name, label, value, color in BADGES:
        (OUT / "badges" / f"{name}.svg").write_text(badge(label, value, color), encoding="utf-8")


if __name__ == "__main__":
    main()
