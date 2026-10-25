"""README-native typography; one comparison, explicit theme and mobile layouts."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PALETTES = {
    'light': {'ink': '#1f2328', 'muted': '#59636e', 'line': '#d1d9e0', 'good': '#116329', 'policy': '#953800'},
    'dark': {'ink': '#f0f6fc', 'muted': '#9198a1', 'line': '#3d444d', 'good': '#7ee787', 'policy': '#ffa657'},
}
DESCRIPTION = (
    'Constructed deterministic allocation pair. Both programmed teams send the same message '
    'and assign the task to dispatch. Mean outsider reward is 14 with the message and 19 '
    'after removal in both worlds. Reducing each outsider task cost by 10 makes the '
    'permitted efficiency policy switch allocation, yielding 29, while the prohibited '
    'coalition-protecting policy keeps allocation, yielding 14. This separates only the '
    'specified policies; identical replay alone does not settle attribution.'
)


class Drawing:
    def __init__(self, width, height, theme):
        self.colors = PALETTES[theme]
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
            '<title id="title">Same replay evidence, different programmed policies</title>',
            f'<desc id="desc">{escape(DESCRIPTION)}</desc>',
            '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",'
            'Helvetica,Arial,sans-serif;font-size:16px}</style>',
        ]

    def text(self, x, y, value, *, color='ink', bold=False):
        self.parts.append(f'<text x="{x}" y="{y}" fill="{self.colors[color]}" '
                          f'font-weight="{600 if bold else 400}">{escape(value)}</text>')

    def line(self, x1, y1, x2, y2, color='line'):
        self.parts.append(f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{self.colors[color]}"/>')

    def arrow(self, x, y):
        self.parts.append(f'<path d="M{x} {y}v18m-4 -4 4 4 4 -4" fill="none" '
                          f'stroke="{self.colors["muted"]}" stroke-width="1.25"/>')

    def policy(self, x, y, width, title, response, reward, color, compact=False):
        height = 64 if compact else 82
        self.parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="{height}" '
                          f'rx="4" fill="none" stroke="{self.colors["line"]}"/>')
        self.parts.append(f'<path d="M{x} {y+12}v{height-24}" stroke="{self.colors[color]}" stroke-width="2"/>')
        self.text(x+14, y+26, title, color=color, bold=True)
        self.text(x+14, y+51, f'{response} · reward {reward}' if compact else response)
        if not compact:
            self.text(x+14, y+74, f'Mean outsider reward: {reward}')

    def save(self, name):
        (ROOT/name).write_text('\n'.join([*self.parts, '</svg>'])+'\n')


def desktop(theme):
    d = Drawing(640, 292, theme)
    d.text(8, 24, 'Same message', bold=True)
    d.text(184, 24, '“Please allocate the contested task to our dispatch team.”')
    d.text(8, 56, 'Same allocation', bold=True)
    d.text(184, 56, 'Task goes to dispatch.')
    d.text(8, 88, 'Same removal effect', bold=True)
    d.text(184, 88, '14 → 19 mean outsider reward')
    d.line(8, 110, 632, 110)
    d.text(8, 142, 'Cost probe', bold=True)
    d.text(112, 142, 'Lower each outsider’s task cost by 10.')
    d.arrow(160, 157)
    d.arrow(480, 157)
    d.policy(8, 190, 300, 'Efficiency policy · permitted', 'Switches allocation', '29', 'good')
    d.policy(332, 190, 300, 'Coalition protection · prohibited', 'Keeps allocation', '14', 'policy')
    d.save('allocation-twins.svg' if theme == 'light' else 'allocation-twins.dark.svg')


def mobile(theme):
    d = Drawing(324, 382, theme)
    d.text(8, 22, 'Same message', bold=True)
    d.text(8, 48, '“Please allocate the contested task')
    d.text(8, 72, 'to our dispatch team.”')
    d.text(8, 100, 'Same allocation: task → dispatch')
    d.text(8, 128, 'Same removal effect: 14 → 19')
    d.text(8, 150, '(mean outsider reward)', color='muted')
    d.line(8, 166, 316, 166)
    d.text(8, 190, 'Cost probe', bold=True)
    d.text(8, 214, 'Lower each outsider’s task cost by 10.')
    d.policy(8, 236, 308, 'Efficiency policy · permitted', 'Switches allocation', '29', 'good', compact=True)
    d.policy(8, 310, 308, 'Coalition protection · prohibited', 'Keeps allocation', '14', 'policy', compact=True)
    d.save('allocation-twins.mobile.svg' if theme == 'light' else 'allocation-twins.mobile-dark.svg')


if __name__ == '__main__':
    for theme in PALETTES:
        desktop(theme)
        mobile(theme)
