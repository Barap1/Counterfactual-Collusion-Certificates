#!/usr/bin/env python3
"""Build SVG held-out results figures from the frozen v2 analysis tables."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAVY = "#17324D"
BLUE = "#4477AA"
VERMILLION = "#CC6677"
GREY = "#66727D"
LIGHT = "#D8DEE5"
LABEL = "held-out · protocol v1.2 · gemma4:26b local"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def text(x: float, y: float, value: str, size: int = 12, fill: str = NAVY, anchor: str = "start", weight: str = "normal", rotate: int = 0) -> str:
    trans = f' transform="rotate({rotate} {x:.1f} {y:.1f})"' if rotate else ""
    return f'<text x="{x:.1f}" y="{y:.1f}" font-family="Arial, sans-serif" font-size="{size}px" fill="{fill}" text-anchor="{anchor}" font-weight="{weight}"{trans}>{html.escape(value)}</text>'


def line(x1: float, y1: float, x2: float, y2: float, stroke: str = LIGHT, width: float = 1, dash: str = "") -> str:
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{stroke}" stroke-width="{width}"{d}/>'


def header(width: int, height: int, title: str, subtitle: str = LABEL) -> list[str]:
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="100%" height="100%" fill="white"/>', text(52, 29, title, 16, NAVY, weight="bold"), text(52, 49, subtitle, 10, GREY)]


def save(out: Path, name: str, content: list[str], sources: list[Path], caption: str):
    out.mkdir(parents=True, exist_ok=True)
    (out / f"{name}.svg").write_text("\n".join(content + ["</svg>", ""]), encoding="utf-8")
    sidecar = {"figure": name, "caption": caption, "label": LABEL, "source_files": [{"path": str(p.relative_to(ROOT)), "sha256": digest(p)} for p in dict.fromkeys(sources)]}
    (out / f"{name}.json").write_text(json.dumps(sidecar, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def make_delta(base: Path, out: Path):
    data = base / "figure_data/fig_delta_by_world.csv"
    cert = base / "checkpoint_certificates.csv"
    aggregate = base / "aggregate.json"
    repro_path = ROOT / "docs/review/rev001/rev001_repro.json"
    ledger = ROOT / "docs/review/rev001/CLAIMS_LEDGER.md"
    observations = rows(data)
    certificates = rows(cert)
    repro = json.loads(repro_path.read_text(encoding="utf-8"))
    if len(observations) != 8:
        raise ValueError("Expected eight matched world pairs")
    pair_by_world = {r["world_id"]: r["checkpoint_id"].split("_")[0] for r in certificates}
    observations.sort(key=lambda r: pair_by_world[r["world_id"]])
    delta = float(repro["Delta_total"])
    low, high = map(float, repro["bootstrap95"])
    p = float(repro["signflip_one_sided_p"])
    left, right, top, bottom = 76, 674, 89, 348
    ymin, ymax = -2.0, 6.0
    ymap = lambda v: bottom - (v - ymin) / (ymax - ymin) * (bottom - top)
    xmap = lambda i: left + i * (right - left) / 8
    s = header(720, 430, "Outsider reward contrast")
    s += [text(20, 220, "World-pair dᵥ (reward units)", 11, NAVY, rotate=-90)]
    for tick in [-2, 0, 2, 4, 6]:
        yy = ymap(tick); s.append(line(left, yy, right + 16, yy, GREY if tick == 0 else LIGHT, 1.15 if tick == 0 else .7))
        s.append(text(left - 10, yy + 4, str(tick), 9, GREY, "end"))
    pairs = []
    for i, r in enumerate(observations):
        pair = pair_by_world[r["world_id"]]; pairs.append(pair)
        value = float(r["d_w"]); xx, yy = xmap(i), ymap(value)
        s.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="4.1" fill="{BLUE}" stroke="white" stroke-width="1"/>')
        if pair in {"H02", "H05"}:
            s.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="7" fill="none" stroke="{NAVY}" stroke-width="1"/>')
        s.append(text(xx, bottom + 20, pair, 9, GREY, "middle"))
    # Place the study estimate in a separate final column, with its world-cluster interval.
    xx = xmap(8); s.append(line(xx, ymap(low), xx, ymap(high), VERMILLION, 2))
    s += [line(xx-4, ymap(low), xx+4, ymap(low), VERMILLION, 1.5), line(xx-4, ymap(high), xx+4, ymap(high), VERMILLION, 1.5), f'<path d="M {xx} {ymap(delta)-5} L {xx+5} {ymap(delta)} L {xx} {ymap(delta)+5} L {xx-5} {ymap(delta)} Z" fill="{VERMILLION}"/>', text(xx, bottom + 20, "Mean", 9, GREY, "middle")]
    s += [text(685, 91, f"Δ = {delta:.2f} [{low:.2f}, {high:.2f}]", 10, NAVY, "end", "bold"), text(685, 108, f"p = {p:.3f}", 10, NAVY, "end"), text(685, 125, "preregistered decision:", 9, NAVY, "end"), text(685, 140, "not supported", 9, NAVY, "end", "bold"), text(52, 393, "Outlined H02/H05: post-hoc sensitivity, not primary.", 9, GREY)]
    s.append("</svg>")
    save(out, "fig_heldout_delta", s[:-1], [data, cert, aggregate, repro_path, ledger], "Per-world-pair B1−B2 outsider-reward differences; diamond and interval show mean Delta and world-cluster 95% CI. Outlined H02/H05 are post-hoc sensitivity, not primary.")


def make_cases(base: Path, out: Path):
    data = base / "checkpoint_certificates.csv"
    aggregate = base / "aggregate.json"
    certs = rows(data)
    if len(certs) != 16:
        raise ValueError("Expected sixteen checkpoint certificates")
    certs.sort(key=lambda r: (r["regime"], int(r["checkpoint_id"][1:3])))
    width, height = 400, 560
    left, panelw = 56, 328
    bounds = {"B1": (111, 269), "B2": (337, 495)}
    ymin, ymax = -6.5, 16.5
    s = header(width, height, "Checkpoint certificates")
    for regime in ("B1", "B2"):
        top, bottom = bounds[regime]
        ymap = lambda v, t=top, b=bottom: b - (v-ymin)/(ymax-ymin)*(b-t)
        s.append(text(left + panelw/2, top-13, regime, 12, NAVY, "middle", "bold"))
        for tick in [-5, 0, 2.5, 5, 10, 15]:
            yy = ymap(tick)
            s.append(line(left, yy, left+panelw, yy, NAVY if tick == 2.5 else LIGHT, 1.2 if tick == 2.5 else .65, "4 3" if tick == 2.5 else ""))
            s.append(text(left-7, yy+3, f"{tick:g}", 8, GREY, "end"))
        subset = [r for r in certs if r["regime"] == regime]
        for i, r in enumerate(subset):
            xx = left + 10 + i*(panelw-20)/7
            lo, hi = float(r["tau_O_L"]), float(r["tau_O_U"])
            color = BLUE if r["status"] == "not_supported" else VERMILLION
            s += [line(xx, ymap(lo), xx, ymap(hi), color, 2), line(xx-4, ymap(lo), xx+4, ymap(lo), color, 1.2), line(xx-4, ymap(hi), xx+4, ymap(hi), color, 1.2), f'<circle cx="{xx}" cy="{ymap(lo):.1f}" r="2.4" fill="{color}"/>', f'<circle cx="{xx}" cy="{ymap(hi):.1f}" r="2.4" fill="{color}"/>', text(xx, bottom+16, r["checkpoint_id"][:3], 8, GREY, "middle")]
    s += [text(18, 300, "Case-level τO interval [L, U] (reward units)", 9, NAVY, rotate=-90), text(56, 522, "Dashed reference: mO = 2.5", 9, NAVY), f'<circle cx="61" cy="543" r="4" fill="{BLUE}"/>', text(71, 547, "Not supported", 9, GREY), f'<circle cx="193" cy="543" r="4" fill="{VERMILLION}"/>', text(203, 547, "Inconclusive", 9, GREY)]
    s.append("</svg>")
    save(out, "fig_heldout_cases", s[:-1], [data, aggregate], "Case-level outsider-effect confidence intervals by checkpoint, grouped by regime; dashed reference is mO = 2.5; colour encodes certificate status.")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("analysis_dir", nargs="?", type=Path, default=Path("docs/analysis/exp002_heldout_v2"))
    parser.add_argument("--out", type=Path, default=ROOT / "figures")
    args = parser.parse_args()
    base = args.analysis_dir if args.analysis_dir.is_absolute() else ROOT / args.analysis_dir
    make_delta(base, args.out)
    make_cases(base, args.out)


if __name__ == "__main__":
    main()
