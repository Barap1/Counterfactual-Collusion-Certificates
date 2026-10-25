#!/usr/bin/env python3
"""CCC paper v2 figures for the identifiability-frontier benchmark.

Reads ONLY benchmark outputs in --run (frontiers.json, separators.json, scores.json,
symmetry.json, population.json, RESULTS.json if present) and writes SVG + PDF + a
sidecar JSON with every plotted number for each figure.

  python figures/enh/make_enh_figures.py --run docs/enh/bench/dev_run \
      --out figures/enh/dev --label DEV

Hand-written SVG, Arial, navy/grey house style of figures/make_results.py; concept colours
(causal, harm, attribution, uncertainty) are the CSS variables of demo/explorer/style.css.
PDF is produced by headless Chrome (vector) when available.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

# ---- palette -----------------------------------------------------------------
NAVY, GREY, LIGHT, INK, MUTED, LINE, SOFT = "#17324D", "#66727D", "#D8DEE5", "#1b1a17", "#5d5a52", "#d9d5ca", "#f1eee6"
CAUSAL, CAUSAL_BG = "#0b5cad", "#e4effa"
HARM, HARM_BG = "#b3261e", "#fbe7e4"
ATTR, ATTR_BG = "#6b3fa0", "#efe7f8"
UNC, UNC_BG = "#8a5a00", "#fbf0d4"
OK, OK_BG = "#1d6b3a", "#e1f2e6"
# method colours (Paul Tol bright, CVD-safe), fixed order, never cycled
MCOL = {"CCC-v1.2.2": "#4477AA", "CCC-L-v1": "#228833", "CCC-L-v0": "#66CCEE", "STRONGEST": "#CC6677", "Bayes-given-S": "#17324D"}
V1_NOTE = "DEV-informed method version"
FONT = "Arial, Helvetica, sans-serif"
SETS = ["I0", "I1", "I2", "I3", "I4", "I5"]
KINDS = ["P1", "P2", "P3", "P4", "P5", "P6"]
KIND_NAMES = {"P1": "P1 redundant-harmful vs inert", "P2": "P2 collusive allocation vs efficient coop.",
              "P3": "P3 unauthorized vs authorized", "P4": "P4 common cause vs message-caused",
              "P5": "P5 suspicious vs plain (same label)", "P6": "P6 useful info vs steering"}
BASELINES = ["B0", "B1", "B2", "B2+", "B3a", "B3b", "B4"]
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def esc(s) -> str:
    return html.escape(str(s))


class Svg:
    def __init__(self, w, h, title, subtitle, label):
        self.w, self.h, self.label = w, h, label
        self.o: list[str] = []
        self.defs: list[str] = []
        self.add(f'<rect width="100%" height="100%" fill="white"/>')
        self.text(24, 28, title, 17, NAVY, weight="bold")
        self.text(24, 47, subtitle, 11, GREY)
        if label == "DEV":
            self.stamp("DEVELOPMENT DATA")
        else:
            self.stamp(f"{label} RUN", color=OK)

    def stamp(self, s, color=HARM):
        w = 7.6 * len(s) + 18
        self.add(f'<rect x="{self.w-w-16:.1f}" y="12" width="{w:.1f}" height="24" rx="3" fill="white" stroke="{color}" stroke-width="1.6"/>')
        self.text(self.w - w / 2 - 16, 29, s, 12, color, "middle", "bold")

    def add(self, s):
        self.o.append(s)

    def text(self, x, y, s, size=11, fill=INK, anchor="start", weight="normal", rotate=0, italic=False, cls=""):
        tr = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate else ""
        st = ' font-style="italic"' if italic else ""
        self.add(f'<text x="{x:.1f}" y="{y:.1f}" font-family="{FONT}" font-size="{size}px" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}"{st}{tr}>{esc(s)}</text>')

    def lines(self, x, y, rows, size=11, fill=INK, anchor="start", lh=None, weight="normal"):
        lh = lh or size * 1.3
        for i, r in enumerate(rows):
            self.text(x, y + i * lh, r, size, fill, anchor, weight)

    def line(self, x1, y1, x2, y2, stroke=LIGHT, width=1.0, dash=""):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}"{d}/>')

    def rect(self, x, y, w, h, fill="none", stroke="none", sw=1.0, rx=0, extra=""):
        self.add(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" {extra}/>')

    def circle(self, x, y, r, fill, stroke="white", sw=1.2):
        self.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def path(self, d, stroke, width=1.8, fill="none", dash=""):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        self.add(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" stroke-linejoin="round"{da}/>')

    def arrow(self, x1, y1, x2, y2, color=GREY, width=1.6):
        self.line(x1, y1, x2, y2, color, width)
        a = math.atan2(y2 - y1, x2 - x1)
        p = [(x2, y2), (x2 - 8 * math.cos(a - .4), y2 - 8 * math.sin(a - .4)), (x2 - 8 * math.cos(a + .4), y2 - 8 * math.sin(a + .4))]
        self.add(f'<polygon points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in p)}" fill="{color}"/>')

    def hatch(self, name, color):
        self.defs.append(f'<pattern id="{name}" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="white"/><line x1="0" y1="0" x2="0" y2="6" stroke="{color}" stroke-width="1" opacity="0.5"/></pattern>')

    def render(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}">'
                f'<title>{esc(self.label)}</title>' + (f'<defs>{"".join(self.defs)}</defs>' if self.defs else "") + "\n" + "\n".join(self.o) + "\n</svg>\n")


# ---- utilities ---------------------------------------------------------------
def clopper_pearson(k, n, alpha=0.05):
    from math import comb

    def cdf(x, p):  # P(X <= x)
        return sum(comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, x + 1))

    def bisect(f, lo=0.0, hi=1.0):
        for _ in range(80):
            mid = (lo + hi) / 2
            if f(mid):
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2
    lo = 0.0 if k == 0 else bisect(lambda p: 1 - cdf(k - 1, p) < alpha / 2)
    hi = 1.0 if k == n else bisect(lambda p: cdf(k, p) > alpha / 2, 0.0, 1.0)
    return lo, hi


def load(run: Path, name: str, required=True):
    p = run / name
    if not p.exists():
        if required:
            print(f"WARNING: missing {name}", file=sys.stderr)
        return None, None
    return json.loads(p.read_text()), p


def to_pdf(svg_path: Path, w: int, h: int, pdf_path: Path) -> bool:
    if not Path(CHROME).exists():
        return False
    with tempfile.TemporaryDirectory() as td:
        page = Path(td) / "p.html"
        page.write_text(f'<!doctype html><meta charset="utf-8"><style>@page{{size:{w}px {h}px;margin:0}}html,body{{margin:0;padding:0}}svg{{display:block}}</style>' + svg_path.read_text())
        r = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf_path}", f"file://{page}"],
                           capture_output=True, timeout=120)
        return pdf_path.exists() and r.returncode == 0


class Ctx:
    def __init__(self, run, out, label):
        self.run, self.out, self.label = Path(run), Path(out), label
        self.sources: dict[str, str] = {}
        self.missing: list[str] = []
        self.out.mkdir(parents=True, exist_ok=True)
        self.evidence = "development" if label == "DEV" else "new-prospective"

    def get(self, name, required=True):
        d, p = load(self.run, name, required)
        if p is not None:
            self.sources[name] = sha(p)
        elif required:
            self.missing.append(name)
        return d

    def save(self, name, svg: Svg, caption, values, used):
        (self.out / f"{name}.svg").write_text(svg.render(), encoding="utf-8")
        pdf_ok = to_pdf(self.out / f"{name}.svg", svg.w, svg.h, self.out / f"{name}.pdf")
        side = {"figure": name, "run_label": self.label, "evidence_category": self.evidence,
                "caption": f"[{self.label}] {caption}",
                "source_files": {k: self.sources[k] for k in used if k in self.sources},
                "missing_fields": [m for m in self.missing if m.startswith(name) or m.startswith("*")],
                "pdf_written": pdf_ok, "plotted_values": values}
        (self.out / f"{name}.json").write_text(json.dumps(side, indent=1, sort_keys=True, default=str) + "\n", encoding="utf-8")
        print(f"wrote {name}.svg/.json" + ("/.pdf" if pdf_ok else " (no pdf)"))


# ---- 1. ladder ---------------------------------------------------------------
def fig_ladder(c: Ctx):
    s = Svg(1060, 600, "Evidence ladder: what each claim needs",
            "Concept diagram (no data). A knockout measures what a message did, not whether it should have done it.", c.label)
    rungs = [
        ("L0", "Suspicious text", "Does the transcript look like coordination?", MUTED, SOFT, ["I0"], "transcript + factual outcome"),
        ("L1", "Causal influence", "Does behaviour change when the message is removed?", CAUSAL, CAUSAL_BG, ["I1"], "+ single-message knockout K"),
        ("L2", "Harmful exposure", "Does the removal change outsider outcomes beyond controls?", HARM, HARM_BG, ["I2", "I3"], "+ sham/placebo; + joint knockout of all same-sender carriers"),
        ("L3", "Attribution", "Should this message have done it? (collusion vs legitimate cooperation)", ATTR, ATTR_BG, ["I4", "I5"], "+ incentive probe (I4) or external normative record (I5)"),
    ]
    x0, bw, gap = 28, 232, 20
    base_y = 470
    steps = {}
    for i, (L, name, q, col, bg, sets, need) in enumerate(rungs):
        x = x0 + i * (bw + gap)
        top = 130 + (3 - i) * 0 + (3 - i) * 0
        y = 395 - i * 62
        h = base_y - y - 80
        h = 122 + i * 0
        y = 360 - i * 60
        s.rect(x, y, bw, h, bg, col, 2, 6)
        s.text(x + 14, y + 30, L, 22, col, weight="bold")
        s.text(x + 56, y + 30, name, 15, INK, weight="bold")
        words = q.split()
        lines, cur = [], ""
        for w_ in words:
            if len(cur) + len(w_) > 31:
                lines.append(cur)
                cur = w_
            else:
                cur = (cur + " " + w_).strip()
        lines.append(cur)
        s.lines(x + 14, y + 54, lines, 12, MUTED, lh=15)
        steps[L] = (x, y, h)
        if i:
            px = x0 + (i - 1) * (bw + gap) + bw
            s.arrow(px + 2, steps[rungs[i - 1][0]][1] + 20, x - 2, y + 20, GREY)
    # information set chips along the bottom
    s.text(28, 508, "Information set needed (nested: each includes all earlier ones)", 12, NAVY, weight="bold")
    chips = [("I0", "transcript + factual"), ("I1", "+ single knockout K"), ("I2", "+ sham / placebo"),
             ("I3", "+ joint knockout, same-sender"), ("I4", "+ incentive / environment probe"), ("I5", "+ external normative record")]
    cw = 160
    colmap = {"I0": MUTED, "I1": CAUSAL, "I2": HARM, "I3": HARM, "I4": ATTR, "I5": ATTR}
    for i, (k, t) in enumerate(chips):
        x = 28 + i * (cw + 8)
        s.rect(x, 520, cw, 50, "white", colmap[k], 2, 5)
        s.text(x + 10, 540, k, 15, colmap[k], weight="bold")
        words, cur, ls = t.split(), "", []
        for w_ in words:
            if len(cur) + len(w_) > 24:
                ls.append(cur)
                cur = w_
            else:
                cur = (cur + " " + w_).strip()
        ls.append(cur)
        s.lines(x + 40, 538, ls, 11, INK, lh=13)
    # connectors rung -> chips
    chip_x = {k: 28 + i * (cw + 8) + cw / 2 for i, (k, _) in enumerate(chips)}
    for L, name, q, col, bg, sets, need in rungs:
        x, y, h = steps[L]
        for k in sets:
            s.line(x + bw / 2, y + h, chip_x[k], 520, col, 1.4, "4 3")
    # uncertainty band
    s.rect(28, 60, 1004, 44, UNC_BG, UNC, 1.6, 5)
    s.text(42, 78, "Uncertainty", 13, UNC, weight="bold")
    s.text(130, 78, "If the information set cannot separate a twin pair, the supported answer is to abstain at that rung (identifiability), not to guess.", 12, INK)
    s.text(130, 94, "Equivalence under a fixed set is definitional; the measured claims are the frontier, the pipeline symmetry check, prevalence and baseline behaviour.", 11, MUTED)
    c.save("fig_ladder", s, "Evidence ladder L0 suspicious text, L1 causal influence, L2 harmful exposure, L3 attribution, with the information set (I0-I5) each rung needs. Concept colours: causal effect (blue), harm (red), attribution (purple), uncertainty (amber).",
           {"rungs": [{"rung": r[0], "name": r[1], "info_sets": r[5], "needs": r[6]} for r in rungs],
            "info_sets": dict(chips), "colours": {"causal": CAUSAL, "harm": HARM, "attribution": ATTR, "uncertainty": UNC}}, [])


# ---- 2. twins ----------------------------------------------------------------
def fig_twins(c: Ctx, F, SEP, RES):
    s = Svg(1060, 716, "One evidence, two verdicts", "P2 twin pair: identical observables under I1-I3, opposite labels; only the I4 incentive probe separates them.", c.label)
    cands = sorted((x["seed"] for x in F if x["epsilon"] == 0 and "P2" in x["pairs"]))
    seed = cands[0]
    ex = RES.get("twin_exhibit")
    if not ex:
        raise SystemExit("FATAL: RESULTS.json twin_exhibit missing")
    if ex.get("seed") != seed or ex.get("kind") != "P2" or ex.get("epsilon") != 0:
        raise SystemExit(f"FATAL: twin_exhibit ({ex.get('kind')}, eps {ex.get('epsilon')}, seed {ex.get('seed')}) != rule (P2, eps 0, seed {seed})")
    fr = [x for x in F if x["seed"] == seed and x["epsilon"] == 0][0]["pairs"]["P2"]
    ccc = [x for x in SEP if x["kind"] == "P2" and x["seed"] == seed and x["epsilon"] == 0 and x["method"] == "CCC-v1.2.2"]
    ccc_diff = ccc[0]["observed_first_difference"] if ccc else "missing"
    s.text(24, 66, f"Pair rule: P2, eps = 0, lowest seed in this run = {seed} (stated rule, not chosen by appearance). Bars: outsider reward, mean over continuations.", 11, MUTED)
    members = ex["members"]
    worlds = [("A", "World A: colluding allocation", HARM, HARM_BG, "forbidden coordination"), ("B", "World B: efficiency-motivated cooperation", OK, OK_BG, "legitimate")]
    colx, cw = [40, 560], 460
    allv = [v for k in "AB" for v in members[k]["outcomes"].values()]
    vmax, vmin = max(0.0, max(allv)), min(0.0, min(allv))
    span = (vmax - vmin) or 1.0
    px0, py, ph = 10, 160, 120
    zy = py + 14 + (ph - 28) * vmax / span
    def bars(x, o, keys, bx0, col, bg):
        for j, b in enumerate(keys):
            bx = x + bx0 + j * 90
            v = o[b]
            bh = abs(v) / span * (ph - 28)
            by = zy - bh if v >= 0 else zy
            s.rect(bx, by, 46, max(bh, 1.5), bg, col, 1.6)
            s.text(bx + 23, by - 5 if v >= 0 else by + bh + 13, f"{v:g}", 11, INK, "middle")
            s.text(bx + 23, py + ph + 18, b, 12, INK, "middle", "bold")
    for (k, title, col, bg, lab), x in zip(worlds, colx):
        m = members[k]
        s.rect(x, 82, cw, 34, bg, col, 1.6, 5)
        s.text(x + 12, 104, title, 14, col, weight="bold")
        s.text(x + cw - 12, 104, "label: " + lab, 11, INK, "end")
        s.text(x, 142, "Observed under I1-I3 (F factual, K knockout, S sham, N filler)", 12, NAVY, weight="bold")
        s.line(x + px0, zy, x + cw - 10, zy, GREY, 1)
        bars(x, m["outcomes"], ["F", "K", "S", "N"], 30, CAUSAL, CAUSAL_BG)
        s.rect(x, 330, cw, 62, "white", CAUSAL, 1.6, 5)
        s.text(x + 12, 352, "CCC v1.2.2 verdict (exposure level, L2)", 12, CAUSAL, weight="bold")
        s.text(x + 12, 378, m["ccc_status"], 15, INK, weight="bold")
        s.text(x + cw - 12, 378, "not an attribution", 11, MUTED, "end", italic=True)
    s.text(530, 225, "=", 40, NAVY, "middle", "bold")
    s.text(530, 370, "=", 28, NAVY, "middle", "bold")
    s.text(530, 408, "same output at every set" if ccc_diff is None else f"CCC first differs at {ccc_diff}", 9, MUTED, "middle")
    s.text(40, 432, "Enumerated twin distinguishability (exact byte-identical views, this seed):", 12, NAVY, weight="bold")
    for i, k in enumerate(SETS):
        d = fr["by_set"][k]["pair_distinct"]
        x = 40 + i * 118
        s.rect(x, 442, 108, 40, ATTR_BG if d else UNC_BG, ATTR if d else UNC, 1.6, 5)
        s.text(x + 10, 460, k, 14, ATTR if d else UNC, weight="bold")
        s.text(x + 10, 475, "distinct" if d else "identical", 11, INK)
    s.text(40 + 6 * 118 + 4, 467, "-> abstain on attribution through I3", 11, UNC, weight="bold")
    s.rect(40, 500, 980, 176, ATTR_BG, ATTR, 1.8, 6)
    s.text(54, 522, "I4 incentive probe: lower outsider costs on the contested task (ceding becomes welfare improving)", 13, ATTR, weight="bold")
    pyy = 546
    for k, x in zip("AB", [60, 580]):
        m = members[k]
        pr = m["i4_probe"]
        s.text(x, pyy, f"World {k}: {pr['metric']}  {pr['before']} -> {pr['after']}", 12, INK, weight="bold")
        s.text(x, pyy + 18, pr["reading"], 12, INK)
        # PF / PK mini bars
        base = pyy + 96
        s.line(x, base, x + 200, base, GREY, 1)
        for j, b in enumerate(["PF", "PK"]):
            v = m["outcomes"][b]
            bh = abs(v) / span * 62
            s.rect(x + 20 + j * 90, base - bh, 46, max(bh, 1.5), "white", ATTR, 1.8)
            s.text(x + 43 + j * 90, base - bh - 4, f"{v:g}", 11, INK, "middle")
            s.text(x + 43 + j * 90, base + 14, b, 11, INK, "middle", "bold")
        s.text(x + 215, base - 30, "PF probe factual, PK probe knockout", 10, MUTED)
        s.text(x + 215, base - 16, "(outsider reward)", 10, MUTED)
    s.text(60, 698, "The efficient team cedes when an outsider is cheaper, the colluding allocation does not; the pair separates at I4 only (enumeration, minimal_pair_separator).", 11, MUTED)
    vals = {"pair_rule": "P2, epsilon 0, lowest seed in run", "seed": seed,
            "enumerated_pair_distinct_by_set": {k: fr["by_set"][k]["pair_distinct"] for k in SETS},
            "minimal_pair_separator": fr["minimal_pair_separator"], "ccc_v1.2.2_observed_first_difference": ccc_diff,
            "twin_exhibit_information_set_for_ccc_status": ex.get("information_set"),
            "members": {k: {"label": worlds[i][4], "outcomes_outsider": members[k]["outcomes"], "ccc_status": members[k]["ccc_status"], "i4_probe": members[k]["i4_probe"]} for i, k in enumerate("AB")}}
    c.save("fig_twins", s, f"One evidence, two verdicts. P2 twin pair at seed {seed} (lowest seed rule). Identical observables under I1-I3 (enumeration), opposite labels, frozen CCC v1.2.2 emits the same exposure-level output for both; the I4 incentive probe separates them.",
           vals, ["frontiers.json", "separators.json", "RESULTS.json"])


# ---- 3. frontier -------------------------------------------------------------
def fig_frontier(c: Ctx, F, SEP, RES):
    s = Svg(1060, 1130, "Identifiability frontier: pair type by information set",
            "Fill = enumeration says the twin members' views differ (share of seed units). Numbers: Bayes = pair accuracy (T3); others = share of units whose output differs between members.", c.label)
    s.hatch("hd", ATTR)
    cx0, cy0, cwid, chei = 330, 110, 100, 84
    methods = [("Bayes-given-S", "B", MCOL["Bayes-given-S"]), ("CCC-L-v1", "L1", MCOL["CCC-L-v1"]), ("CCC-L-v0", "L0", MCOL["CCC-L-v0"]), ("CCC-v1.2.2", "C", MCOL["CCC-v1.2.2"])]
    T3 = {(r["kind"], r["epsilon"]): r for r in RES["tables"]["T3"]}
    vals = {}
    for pi, eps in enumerate([0, 0.1]):
        oy = cy0 + pi * 462
        s.text(24, oy - 24, f"eps = {eps}" + (" (no exploration noise)" if eps == 0 else " (uniform exploration, probability 0.1)"), 13, NAVY, weight="bold")
        for j, k in enumerate(SETS):
            s.text(cx0 + j * cwid + cwid / 2, oy - 8, k, 13, INK, "middle", "bold")
        for i, kind in enumerate(KINDS):
            y = oy + i * chei * 0.0 + i * 0.0
            yy = oy + i * chei * 0.78
            s.text(cx0 - 10, yy + 22, KIND_NAMES[kind], 11, INK, "end")
            # Prospective rows contain only their own pair kind (or no pair).
            units = [x for x in F if x["epsilon"] == eps and kind in x["pairs"]]
            n = len(units)
            for j, k in enumerate(SETS):
                sep = sum(1 for u in units if u["pairs"][kind]["by_set"][k]["pair_distinct"])
                share = sep / n
                definitional = (kind == "P3" and k == "I5")
                x = cx0 + j * cwid
                h = chei * 0.78 - 4
                fill = CAUSAL_BG if share >= 0.5 else SOFT
                stroke = CAUSAL if share >= 0.5 else LINE
                s.rect(x + 2, yy, cwid - 4, h, "url(#hd)" if definitional else fill, ATTR if definitional else stroke, 1.6 if definitional else 1, 3)
                cell = {"enumerated_separable_share": share, "n_seed_units": n, "definitional": definitional}
                for mi, (m, tag, col) in enumerate(methods):
                    if m == "Bayes-given-S":
                        t3 = T3.get((kind, eps))
                        r_ = t3["by_set"][k]["bayes_pair_accuracy_one"]["rate"] if t3 else None
                        leak = False
                    else:
                        rows = [r for r in SEP if r["kind"] == kind and r["method"] == m and r["epsilon"] == eps]
                        nm = len(rows)
                        obs = sum(1 for r in rows if r["observed_first_difference"] is not None and SETS.index(r["observed_first_difference"]) <= j)
                        r_ = obs / nm if nm else None
                        leak = (share < 0.5 and r_ and r_ > 0)
                    cell[m] = r_
                    tx = x + 12
                    ty = yy + 15 + mi * 13
                    s.rect(tx, ty - 8, 8, 8, col)
                    s.text(tx + 13, ty, "n/a" if r_ is None else f"{r_:.2f}", 11, HARM if leak else INK, weight="bold" if leak else "normal")
                if definitional:
                    s.text(x + cwid - 7, yy + 13, "def.", 10, ATTR, "end", weight="bold")
                vals[f"eps{eps}/{kind}/{k}"] = cell
    ly = 140 + 640 + 12 - 20
    never = ", ".join(k for k in KINDS if all(vals[f"eps{e}/{k}/{ss}"]["CCC-v1.2.2"] == 0 for e in (0, 0.1) for ss in SETS)) or "none"
    LY = 1038
    s.text(24, LY, "Legend", 12, NAVY, weight="bold")
    s.rect(80, LY-10, 16, 12, CAUSAL_BG, CAUSAL); s.text(100, LY, "separable by enumeration", 11, INK)
    s.rect(250, LY-10, 16, 12, SOFT, LINE); s.text(270, LY, "not separable (byte-identical views)", 11, INK)
    s.rect(490, LY-10, 16, 12, "url(#hd)", ATTR); s.text(510, LY, "definitional, def. (P3 at I5: authorization is the label)", 11, INK)
    x = 80
    for m, tag, col in methods:
        s.rect(x, LY+11, 9, 9, col); s.text(x + 14, LY+20, {"Bayes-given-S": "Bayes-given-S pair accuracy", "CCC-L-v1": "CCC-L v1 (DEV-informed method version)", "CCC-L-v0": "CCC-L v0", "CCC-v1.2.2": "CCC v1.2.2 (frozen)"}[m], 10, INK); x += {"Bayes-given-S": 170, "CCC-L-v1": 250, "CCC-L-v0": 100, "CCC-v1.2.2": 150}[m]
    s.text(24, LY+42, "n/a = no T3 row (P5 is a same-label control). Red number = output differs on a not-separable cell (symmetry leak). P5 is a same-label control (transcripts differ, labels agree), not a different-label pair.", 11, MUTED)
    s.text(24, LY+58, "Share = seed units whose method output differs between twin members at that set or an earlier one; pair types CCC v1.2.2 never separates: " + never, 11, MUTED)
    c.save("fig_frontier", s, "Frontier heat map, pair type P1-P6 by information set I0-I5, both noise strata. Fill from exact enumeration; overlaid: Bayes-given-S pair accuracy (RQ2, T3) and the share of seed units on which CCC-L v1 (DEV-informed method version), CCC-L v0 and frozen CCC v1.2.2 emit different outputs for the two twin members. P3 at I5 is definitional.",
           vals, ["frontiers.json", "separators.json", "RESULTS.json"])


# ---- 4. risk-coverage ----------------------------------------------------------
def frozen_strongest(c, RES):
    """The protocol's frozen strongest baseline, read from the run (never computed here)."""
    sb = None
    if RES and isinstance(RES.get("dev_derived"), dict):
        sb = RES["dev_derived"].get("strongest_baseline")
    if not sb:
        p = c.run / "strongest_baseline.json"
        if p.exists():
            c.sources["strongest_baseline.json"] = sha(p)
            sb = json.loads(p.read_text()).get("strongest_baseline")
    if not sb:
        raise SystemExit("FATAL: frozen strongest baseline missing (RESULTS.json dev_derived.strongest_baseline / strongest_baseline.json)")
    return sb


def _unused_strongest_baseline(SC, axis):
    best = None
    for b in BASELINES:
        v = []
        for x in SC:
            if x["method"] == b and x["axis"] == axis and "risk_coverage" in x:
                v.append(min(p["risk"]["0.5"] for p in x["risk_coverage"]))
        if v:
            m = sum(v) / len(v)
            if best is None or m < best[1] or (m == best[1] and b < best[0]):
                best = (b, m, len(v))
    return best


def fig_risk(c: Ctx, SC, axis, name, axname, sbn):
    methods = [("CCC-v1.2.2", MCOL["CCC-v1.2.2"], "CCC v1.2.2"), ("CCC-L-v1", MCOL["CCC-L-v1"], f"CCC-L v1 ({V1_NOTE})"), ("CCC-L-v0", MCOL["CCC-L-v0"], "CCC-L v0"),
               (sbn, MCOL["STRONGEST"], f"strongest baseline ({sbn}, frozen)"), ("Bayes-given-S", MCOL["Bayes-given-S"], "Bayes-given-S")]
    pw, ph, gx, gy = 138, 104, 14, 28
    left, top = 92, 96
    W = left + 6 * (pw + gx) + 14
    H = top + 4 * (ph + gy) + 170
    s = Svg(W, H, f"Risk-coverage by information set ({axname})", "Risk = error + c * abstention (lower is better); coverage = share of members answered. Rows: noise stratum x abstention cost c.", c.label)
    # y max
    ymax = 0.0
    for x in SC:
        if x["axis"] == axis and "risk_coverage" in x:
            for p in x["risk_coverage"]:
                ymax = max(ymax, p["risk"]["0.25"], p["risk"]["0.5"])
    ymax = math.ceil(ymax * 10 + 1e-9) / 10 or 0.5
    vals = {"strongest_baseline_source": "RESULTS.json dev_derived.strongest_baseline (protocol-frozen)", "strongest_baseline": sbn, "panels": {}}
    na = []
    for ri, (eps, cc) in enumerate([(0, "0.25"), (0, "0.5"), (0.1, "0.25"), (0.1, "0.5")]):
        for ci, k in enumerate(SETS):
            x0 = left + ci * (pw + gx)
            y0 = top + ri * (ph + gy)
            s.rect(x0, y0, pw, ph, "white", LINE, 1)
            for g in range(0, int(round(ymax * 10)) + 1, 2):
                gv = g / 10
                yy = y0 + ph - gv / ymax * ph
                s.line(x0, yy, x0 + pw, yy, "#eceae3", 0.8)
                if ci == 0:
                    s.text(x0 - 5, yy + 3, f"{gv:.1f}", 10, MUTED, "end")
            if ri == 0:
                s.text(x0 + pw / 2, y0 - 8, k, 13, INK, "middle", "bold")
            if ci == 0:
                s.text(x0 - 40, y0 + ph / 2 + 18, f"eps {eps}  c={cc}", 11, NAVY, "middle", "bold", rotate=-90)
            panel = {}
            for m, col, nm in reversed(methods):
                e = [q for q in SC if q["method"] == m and q["axis"] == axis and q["epsilon"] == eps and q["information_set"] == k]
                if not e or "risk_coverage" not in e[0]:
                    if ri == 0 and ci == 0:
                        na.append(nm)
                    continue
                pts = sorted([(p["coverage"], p["risk"][cc]) for p in e[0]["risk_coverage"]])
                panel[m] = pts
                d = " ".join(("M" if i == 0 else "L") + f"{x0 + a * pw:.1f},{y0 + ph - b / ymax * ph:.1f}" for i, (a, b) in enumerate(pts))
                dash = "5 3" if m == "Bayes-given-S" else ""
                if len(pts) > 1:
                    s.path(d, col, 1.9, dash=dash)
                for a, b in pts:
                    s.circle(x0 + a * pw, y0 + ph - b / ymax * ph, 3.2 if m != "CCC-v1.2.2" else 5, col, "white", 1)
            # anchors
            aa = [q for q in SC if q["method"] == "always-answer" and q["axis"] == axis and q["epsilon"] == eps and q["information_set"] == k]
            ab = float(cc)
            if aa and "risk_coverage" in aa[0]:
                ans = max(aa[0]["risk_coverage"], key=lambda p: p["coverage"])
                panel["always-answer"] = (ans["coverage"], ans["risk"][cc])
                ay = y0 + ph - ans["risk"][cc] / ymax * ph
                s.add(f'<rect x="{x0+pw-5:.1f}" y="{ay-5:.1f}" width="10" height="10" fill="white" stroke="{GREY}" stroke-width="1.8"/>')
            panel["always-abstain"] = (0.0, ab)
            ay = y0 + ph - ab / ymax * ph
            s.add(f'<polygon points="{x0:.1f},{ay-6:.1f} {x0+6:.1f},{ay+5:.1f} {x0-6:.1f},{ay+5:.1f}" fill="white" stroke="{GREY}" stroke-width="1.8"/>')
            if ri == 3:
                for t in (0, 0.5, 1):
                    s.text(x0 + t * pw, y0 + ph + 13, f"{t:g}", 10, MUTED, "middle")
                if ci == 2:
                    s.text(x0 + pw + gx / 2, y0 + ph + 27, "coverage", 11, MUTED, "middle")
            vals["panels"][f"eps{eps}/c{cc}/{k}"] = panel
    ly = top + 4 * (ph + gy) + 8
    x = left
    for m, col, nm in methods:
        if x + 28 + 6.3 * len(nm) > W - 10:
            x = left
            ly += 18
        s.line(x, ly + 4, x + 22, ly + 4, col, 2.2, "5 3" if m == "Bayes-given-S" else "")
        s.circle(x + 11, ly + 4, 3.5, col)
        s.text(x + 28, ly + 8, nm, 11, INK)
        x += 28 + 6.3 * len(nm) + 22
    x = left + 6
    ly += 20
    s.add(f'<polygon points="{x:.1f},{ly-2:.1f} {x+6:.1f},{ly+9:.1f} {x-6:.1f},{ly+9:.1f}" fill="white" stroke="{GREY}" stroke-width="1.8"/>')
    s.text(x + 14, ly + 8, "always-abstain (coverage 0, risk c)", 11, INK)
    x = left + 260
    s.add(f'<rect x="{x:.1f}" y="{ly-1:.1f}" width="10" height="10" fill="white" stroke="{GREY}" stroke-width="1.8"/>')
    s.text(x + 15, ly + 8, "always-answer", 11, INK)
    notes = []
    if na:
        notes.append(f"Not plotted (method emits no {axname} output): {', '.join(sorted(set(na)))}.")
    notes.append("Where curves coincide, the top-drawn marker is CCC v1.2.2 (largest dot); coincident methods emitted identical outputs.")
    notes.append("Native binary methods have one or two curve points (confidence ties kept whole). Weighted risk has no binomial CI.")
    notes.append("Bayes-given-S uses only the design class prior given the view; it is a ceiling for methods restricted to that set, under the uniform design prior.")
    for i, t in enumerate(notes):
        s.text(left, ly + 28 + i * 16, t, 11, MUTED)
    vals["not_plotted_on_this_axis"] = sorted(set(na))
    c.save(name, s, f"Risk-coverage curves on the {axname} axis, per information set, both noise strata, abstention cost c in 0.25 and 0.5; CCC v1.2.2, CCC-L v1 (DEV-informed method version), CCC-L v0, frozen strongest baseline, Bayes-given-S and always-answer/abstain anchors.",
           vals, ["scores.json"])


# ---- 5. over-attribution -------------------------------------------------------
def fig_overattr(c: Ctx, RES, sbn):
    T5, T5b = RES["tables"]["T5"], RES["tables"]["T5b"]
    classes = [("P2", "P2 efficient cooperation"), ("P3", "P3 authorized transfer"), ("P6", "P6 useful information"), ("benign-cooperation", "benign cooperation")]
    for r in T5 + T5b:
        if r["method"] != sbn:
            raise SystemExit(f"FATAL: T5/T5b method {r['method']} != frozen strongest baseline {sbn}")
    pw, rh, left, top = 300, 74, 190, 120
    W = left + 2 * (pw + 130) + 20
    H = top + 4 * rh + 130
    s = Svg(W, H, "Over-attribution on legitimate members, per class",
            f"Frozen strongest baseline ({sbn}) under I1; rate of attributable-collusion output on legitimate members; CP95 over independent seed units. No pooling.", c.label)
    vals = {"strongest_baseline": sbn, "information_set": "I1 (RQ4/RQ4b protocol set)", "rows": {}}
    for ei, eps in enumerate([0, 0.1]):
        x0 = left + ei * (pw + 130)
        s.text(x0, top - 38, f"eps = {eps}", 13, NAVY, weight="bold")
        for t_ in (0, .25, .5, .75, 1):
            s.line(x0 + t_ * pw, top - 12, x0 + t_ * pw, top + 4 * rh - 14, "#eceae3", .8)
            s.text(x0 + t_ * pw, top + 4 * rh - 2, f"{t_:g}", 10, MUTED, "middle")
        s.line(x0 + .5 * pw, top - 16, x0 + .5 * pw, top + 4 * rh - 14, UNC, 1.6, "6 4")
        s.text(x0 + .5 * pw, top - 20, "0.5 (RQ4; RQ4b for P2/P3)", 10, UNC, "middle", "bold")
        for ci, (k, name) in enumerate(classes):
            yy = top + ci * rh
            if ei == 0:
                s.text(left - 12, yy + 22, name, 12, INK, "end", "bold")
            r5 = [r for r in T5 if r["kind"] == k and r["epsilon"] == eps][0]
            r5b = [r for r in T5b if r["kind"] == k and r["epsilon"] == eps][0]
            oa, l2 = r5["over_attribution"], r5["CCC_L2_supported"]
            for off, mk, met, col in [(10, "dot", oa, NAVY), (34, "dia", l2, HARM)]:
                lo, hi = met["unit_cp95"]
                y = yy + off
                s.line(x0 + lo * pw, y, x0 + hi * pw, y, col, 2.4)
                s.line(x0 + lo * pw, y - 4, x0 + lo * pw, y + 4, col, 1.6)
                s.line(x0 + hi * pw, y - 4, x0 + hi * pw, y + 4, col, 1.6)
                px = x0 + met["unit_rate"] * pw
                if mk == "dot":
                    s.circle(px, y, 5, col)
                else:
                    s.add(f'<polygon points="{px:.1f},{y-6:.1f} {px+6:.1f},{y:.1f} {px:.1f},{y+6:.1f} {px-6:.1f},{y:.1f}" fill="white" stroke="{HARM}" stroke-width="2"/>')
                s.text(x0 + pw + 8, y + 4, f"{met['unit_k']}/{met['independent_n']}", 10, INK)
            if k in ("P6", "benign-cooperation"):
                s.line(x0 + .05 * pw, yy - 4, x0 + .05 * pw, yy + 46, ATTR, 1.6, "2 3")
                s.text(x0 + .05 * pw + 4, yy + 58, "0.05 (RQ4b)", 9, ATTR, weight="bold")
            ok4b = r5b["pass_criterion"]
            ok4 = r5["pass_criterion"]
            s.text(x0 + pw + 44, yy + 18, f"RQ4 {'ok' if ok4 else 'no'}", 10, OK if ok4 else HARM, weight="bold")
            s.text(x0 + pw + 44, yy + 32, f"RQ4b {'ok' if ok4b else 'no'}", 10, OK if ok4b else HARM, weight="bold")
            vals["rows"][f"eps{eps}/{k}"] = {"baseline_over_attribution": oa, "ccc_v1.2.2_L2_supported": l2, "RQ4_class_pass": ok4, "RQ4b_class_pass": ok4b}
    ly = H - 56
    s.circle(30, ly, 5, NAVY); s.text(42, ly + 4, f"{sbn}: attributable-collusion output on a legitimate member (T5 / T5b)", 11, INK)
    s.add(f'<polygon points="{W/2+20:.0f},{ly-6} {W/2+26:.0f},{ly} {W/2+20:.0f},{ly+6} {W/2+14:.0f},{ly}" fill="white" stroke="{HARM}" stroke-width="2"/>')
    s.text(W / 2 + 36, ly + 4, "CCC v1.2.2 exposure-level 'supported' (L2 harmful exposure, not attribution)", 11, INK)
    s.text(24, ly + 24, "Unit endpoint: any flagged member within a seed unit; k/n = units. RQ4 needs all four classes above 0.5; RQ4b needs P2/P3 above 0.5 and P6/benign at most 0.05. 'ok/no' = class-level criterion met.", 10, MUTED)
    c.save("fig_overattribution", s, "Over-attribution of the frozen strongest baseline on legitimate members (P2, P3, P6, benign cooperation) under I1, per class and noise stratum, Clopper-Pearson 95% over independent seed units, with the 0.5 (RQ4) and 0.05 (RQ4b) lines; CCC v1.2.2 exposure-level supported rate shown separately as L2, not attribution.",
           vals, ["RESULTS.json"])


# ---- 6. prevalence --------------------------------------------------------------
def fig_prevalence(c: Ctx, RES):
    strata = RES["tables"]["T4"]["strata"]
    s = Svg(1000, 420, "RQ3 label-effect gap: prevalence", "Share of mechanism-'forbidden' iid worlds whose oracle exposure effect tau_O is at least m_O = 2.5; noise strata kept separate.", c.label)
    x0, x1 = 70, 480
    s.text(24, 80, "Prevalence with Clopper-Pearson 95% interval", 13, NAVY, weight="bold")
    yax = 250
    s.line(x0, yax, x1, yax, GREY, 1)
    for t_ in (0, .25, .5, .75, 1):
        xx = x0 + t_ * (x1 - x0)
        s.line(xx, yax, xx, yax + 5, GREY)
        s.text(xx, yax + 20, f"{int(t_*100)}%", 10, MUTED, "middle")
    px = x0 + .25 * (x1 - x0)
    s.line(px, 108, px, yax, UNC, 1.8, "6 4")
    s.text(px + 6, 118, "25% pre-registered line", 11, UNC, weight="bold")
    out = {}
    for i, eps in enumerate(["0", "0.1"]):
        st = strata[eps]
        k, n, rate, (lo, hi) = st["k"], st["n"], st["rate"], st["cp95"]
        y = 170 + i * 52
        s.text(24, y + 4, f"eps {eps}", 12, INK, weight="bold")
        s.line(x0 + lo * (x1 - x0), y, x0 + hi * (x1 - x0), y, CAUSAL, 3)
        s.line(x0 + lo * (x1 - x0), y - 6, x0 + lo * (x1 - x0), y + 6, CAUSAL, 2)
        s.line(x0 + hi * (x1 - x0), y - 6, x0 + hi * (x1 - x0), y + 6, CAUSAL, 2)
        s.circle(x0 + rate * (x1 - x0), y, 6, CAUSAL)
        s.text(x0 + hi * (x1 - x0) + 10, y + 4, f"{k}/{n} = {rate*100:.0f}%  [{lo*100:.1f}, {hi*100:.1f}]", 11, INK, weight="bold")
        out[eps] = {"k": k, "n": n, "rate": rate, "cp95": [lo, hi], "tau_O_sorted": sorted(r["tau_O"] for r in st["rows"]),
                    "status": RES["rq"]["RQ3"]["by_epsilon"][eps]["status"], "supported_with_margin": RES["rq"]["RQ3"]["by_epsilon"][eps]["supported_with_margin"]}
    s.text(24, yax + 48, "n = 50 independent seeds per stratum, one forbidden world per seed;", 11, MUTED)
    s.text(24, yax + 64, "k = worlds with tau_O >= 2.5. Strata share seeds and are not pooled.", 11, MUTED)
    allt = [v for o in out.values() for v in o["tau_O_sorted"]]
    lo_t, hi_t = min(allt + [0]), max(allt + [2.5])
    top, bot = 110, 320
    def ty(v): return bot - (v - lo_t) / (hi_t - lo_t) * (bot - top)
    s.text(560, 80, "Oracle tau_O per world", 13, NAVY, weight="bold")
    sx0 = 590
    s.line(sx0, bot, sx0, top, GREY)
    for t_ in range(int(math.ceil(lo_t / 5) * 5), int(hi_t) + 1, 5):
        s.line(sx0 - 4, ty(t_), sx0, ty(t_), GREY)
        s.text(sx0 - 8, ty(t_) + 4, f"{t_}", 10, MUTED, "end")
    s.line(sx0, ty(2.5), 970, ty(2.5), UNC, 1.8, "6 4")
    s.text(sx0 + 6, ty(2.5) - 5, "m_O = 2.5", 11, UNC, "start", "bold")
    for j, eps in enumerate(["0", "0.1"]):
        vs = out[eps]["tau_O_sorted"]
        xa = sx0 + 12 + j * 190
        s.text(xa + 80, bot + 18, f"eps {eps}", 11, INK, "middle", "bold")
        for i, v in enumerate(vs):
            xx = xa + (i + .5) / len(vs) * 170
            s.circle(xx, ty(v), 3.4, CAUSAL if v >= 2.5 else "white", CAUSAL, 1.4)
    s.text(sx0 + 10, bot + 34, "sorted by tau_O; filled = at or above m_O", 10, MUTED)
    s.text(24, 396, "Reading: a forbidden mechanism label does not by itself imply an exposure effect; the label-effect gap is the share of forbidden worlds below m_O.", 11, MUTED)
    c.save("fig_prevalence", s, "RQ3: share of mechanism-forbidden iid worlds with oracle tau_O >= 2.5, per noise stratum, with Clopper-Pearson 95% interval and the 25% pre-registered line; right panel shows tau_O per world.",
           {"strata": out, "line": 0.25, "estimand": RES["tables"]["T4"].get("estimand"), "evidence": RES["tables"]["T4"].get("evidence")}, ["RESULTS.json"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--label", required=True, choices=["DEV", "PROSPECTIVE"])
    a = ap.parse_args()
    c = Ctx(a.run, a.out, a.label)
    F, SEP, SC, POP = c.get("frontiers.json"), c.get("separators.json"), c.get("scores.json"), c.get("population.json")
    c.get("symmetry.json", False)
    RES = c.get("RESULTS.json")
    if not (F and SEP and SC and POP and RES):
        raise SystemExit(f"FATAL: missing required run files: {c.missing}")
    sbn = frozen_strongest(c, RES)
    fig_ladder(c)
    fig_twins(c, F, SEP, RES)
    fig_frontier(c, F, SEP, RES)
    fig_risk(c, SC, "M", "fig_risk", "attribution, axis M", sbn)
    fig_risk(c, SC, "E", "fig_risk_E", "exposure, axis E", sbn)
    fig_overattr(c, RES, sbn)
    fig_prevalence(c, RES)
    (c.out / "figures_manifest.json").write_text(json.dumps({"run": str(a.run), "label": a.label, "sources": c.sources, "missing_files": c.missing, "strongest_baseline": sbn, "results_evidence": RES.get("evidence")}, indent=1) + "\n")


if __name__ == "__main__":
    main()
