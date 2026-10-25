#!/usr/bin/env python3
"""Build paper v2: draft_v2.md -> build/submission_v2.md/.html -> PDF (headless Chrome).

Usage: python3 paper/v2/make_v2.py [--figdir figures/enh/dev] [--no-pdf]
Adapted from paper/build/make_submission.py (which is not modified). Reuses the
dependency-free renderer paper/build/markdown_to_html.py.
References are regenerated from paper/v2/references_v2.bib (numbering as in the draft).
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
V2 = ROOT / "paper/v2"
DRAFT, BIB = V2 / "draft_v2.md", V2 / "references_v2.bib"
BUILD = V2 / "build"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
REF_ORDER = ["nakamura2026colosseum", "tran2026enforcing", "kaur2026vla", "rose2026helios",
    "xu2026competitivemarginals", "riemer2026position", "zhang2026latentaudit", "idowu2026anticollusion",
    "lee2026faithful", "motwani2024secret", "everitt2021incentives", "ward2024intention",
    "chockler2004responsibility", "li2026gcjr", "shah2026car", "arslan2026audit", "geifman2017selective",
    "pona2026ctd", "calvano2020artificial", "lopesdemoraes2026deterrence"]

# (file, placement heading prefix, role). Placement = end of that section; main text unless appendix.
FIGS = [
    ("figdir:fig_ladder.svg", "## 1. Introduction", "Figure 1. "),
    ("figdir:fig_twins.svg", "after:**Scoped limit statement.**", "Figure 2. "),
    ("figures/fig_heldout_delta.svg", "### 5.1 ", "Figure 3. Held-out real-agent matched-world contrasts (EXP-002), aggregate Delta and world-cluster CI (OC). The preregistered directional test is a confirmatory null; non-commit exclusion points are the registered sensitivity (ORS), not the primary. "),
    ("figdir:fig_frontier.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A9 (RQ2, frontier; main-text candidate if space allows). "),
    ("figdir:fig_risk.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A10 (RQ5, risk-coverage; main-text candidate if space allows). "),
    # appendix
    ("figures/fig_arms.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A1. Branch schematic F/K/S/N (schematic, no data). "),
    ("figures/fig_heldout_cases.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A2. Case-level outsider-effect certificate intervals versus m_O (EXP-002, descriptive); certificates are exploratory. "),
    ("figures/fig_supported_vs_oracle.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A3. Supported verdicts versus oracle exposure effect on DEV fixtures (DEV). "),
    ("figures/fig_gateA_integrity.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A4. Gate A integrity checks (DEV). "),
    ("figures/fig_confusion_dev.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A5. Baseline positive-call rates on DEV fixtures (DEV). "),
    ("figdir:fig_prevalence.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A6. "),
    ("figdir:fig_overattribution.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A7. "),
    ("figdir:fig_risk_E.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A8. "),
]

def entry_for(bib: str, key: str) -> str:
    st = bib.index("{" + key + ",")
    return bib[st: bib.index("\n}", st)]

def field(e: str, n: str) -> str:
    m = re.search(n + r"\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}", e, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""

def refs_block(bib: str) -> str:
    venue = {"riemer2026position": "ICML 2026 (position)", "idowu2026anticollusion": "Knowledge-Based Systems 344:116067 (2026)",
             "lee2026faithful": "Findings of EMNLP 2026", "everitt2021incentives": "AAAI 2021", "lopesdemoraes2026deterrence": "ICAIF 2026"}
    out = ["## References", ""]
    for i, k in enumerate(REF_ORDER, 1):
        e = entry_for(bib, k)
        au = ", ".join(" ".join(reversed(a.split(", "))) for a in field(e, "author").split(" and ")).replace("{\\`o}", "ò")
        t = field(e, "title").replace("{", "").replace("}", "")
        if field(e, "journal"):
            d = field(e, "journal") + f" {field(e, 'volume')}" + (f"({field(e, 'number')})" if field(e, "number") else "") + ":" + field(e, "pages").replace("--", "-")
            d += f". doi:{field(e, 'doi')}" if field(e, "doi") else ""
        else:
            d = f"arXiv:{field(e, 'eprint')}"
        v = f" {venue[k]}." if k in venue else ""
        out.append(f"{i}. {au} ({field(e, 'year')}). {t}. {d}.{v}")
    return "\n".join(out) + "\n\n"

def section_end(src: str, heading_prefix: str) -> int:
    if heading_prefix.startswith("after:"):
        k = src.index(heading_prefix[6:])
        e = src.find("\n\n", k)
        return e + 2 if e != -1 else len(src)
    m = re.search(r"(?m)^" + re.escape(heading_prefix) + r".*$", src)
    if not m:
        raise ValueError(f"placement heading not found: {heading_prefix}")
    lvl = len(heading_prefix.split()[0])
    nxt = re.search(r"(?m)^#{1," + str(lvl) + r"} ", src[m.end():])
    return m.end() + nxt.start() if nxt else len(src)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--figdir", default="figures/enh/dev")
    ap.add_argument("--figheight", default="1.9in", help="max rendered figure height")
    ap.add_argument("--no-pdf", action="store_true")
    a = ap.parse_args()
    figdir = ROOT / a.figdir
    BUILD.mkdir(exist_ok=True)
    src = DRAFT.read_text(encoding="utf-8")
    src = re.sub(r"(?s)<!--.*?-->\n?", "", src)                      # editor comments
    src = re.sub(r"(?s)# TITLE OPTIONS.*?\n---\n\n", "", src)          # title block (owner picks; option 1 shown)
    src = src.replace("# [Title: option 1 pending owner choice]",
                      "# A Knockout Measures What a Message Did, Not What It Should Have Done: Evidence Standards for AI Collusion Attribution")
    # appendix planning sections G/H are editor material, not rendered
    src = re.sub(r"(?s)\n## G\. Figure plan.*?(?=\n## I\. )", "\n", src)
    # references from bib only
    src = re.sub(r"(?s)## References\n.*?(?=\n---\n\n# APPENDIX)", refs_block(BIB.read_text(encoding="utf-8")).rstrip(), src)
    unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", src)))

    for fname, where, cap in FIGS:
        if fname.startswith("figdir:"):
            path = figdir / fname[7:]
            meta = json.loads(path.with_suffix(".json").read_text()) if path.with_suffix(".json").exists() else {}
            c = meta.get("caption", "")
            c = re.sub(r"^\[(\w+)\]\s*", r"(\1) ", c).replace("[", "(").replace("]", ")")
            caption = cap + c
        else:
            path, caption = ROOT / fname, cap
        if not path.is_file():
            raise ValueError(f"missing figure {path}")
        rel = Path("../../../") / path.relative_to(ROOT)
        at = section_end(src, where)
        src = src[:at].rstrip() + f"\n\n![{caption.strip().replace(']', ')')}]({rel})\n\n" + src[at:].lstrip("\n")
    # main-text / appendix split marker for page counting
    md_out, html_out, pdf_out = BUILD / "submission_v2.md", BUILD / "submission_v2.html", BUILD / "submission_v2.pdf"
    md_out.write_text(src, encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "paper/build/markdown_to_html.py"), str(md_out), str(html_out)], cwd=ROOT, check=True)
    h = html_out.read_text(encoding="utf-8")
    h = h.replace("max-height:3.3in", "max-height:%s" % a.figheight).replace("figure[aria-label^=\"Figure 4.\"] svg{max-height:4in}", "")
    h = h.replace("</style>", "ol{font-size:9pt;line-height:1.15;padding-left:1.4em}ol li{margin:.1em 0}</style>", 1)
    h = h.replace("<title>CCC submission</title>", "<title>CCC paper v2 (figures: %s)</title>" % a.figdir)
    html_out.write_text(h, encoding="utf-8")
    report = {"figdir": a.figdir, "placeholders_remaining": unresolved, "svgs": h.count("<svg "),
              "cite_check_tags": len(re.findall(r"CITE-CHECK", src)), "owner_tags": sorted(set(re.findall(r"\[OWNER[^\]]*\]", src)))}
    if not a.no_pdf:
        subprocess.run([CHROME, "--headless=new", "--no-pdf-header-footer", f"--print-to-pdf={pdf_out}", html_out.as_uri()],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=180)
        report["pdf"] = str(pdf_out.relative_to(ROOT))
    (BUILD / "build_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
