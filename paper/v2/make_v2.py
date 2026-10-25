#!/usr/bin/env python3
"""Build paper v2: draft_v2.md -> build/submission_v2.md/.html -> PDF (headless Chrome).

Usage: python3 paper/v2/make_v2.py [--figdir figures/enh/dev] [--no-pdf]
Adapted from paper/build/make_submission.py (which is not modified). Reuses the
dependency-free renderer paper/build/markdown_to_html.py.
References are regenerated from paper/v2/references_v2.bib (numbering as in the draft).
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys, tempfile
from datetime import datetime, timezone
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
    ("paper/v2/figures/fig_ladder_audit.svg", "## 1. Introduction", "Figure 1. Evidence ladder (conceptual design). Each rung has separate requirements; influence and harmful exposure do not by themselves justify attribution. "),
    ("paper/v2/figures/fig_twins_audit.svg", "after:**Scoped limit statement.**", "Figure 2. Deterministic P2 twins (NP), seed 19693329 selected by the lowest-seed rule. Labels are scripted; I4 separates this pair within the declared generator. "),
    ("paper/v2/figures/fig_heldout_delta_audit.svg", "### 5.4 ", "Figure 3. Held-out matched-world contrasts (EXP-002), mean Delta and world-cluster 95% CI [OC]. The directional hypothesis is not supported. Outlines mark H02/H05 for post-hoc inspection [PH]; they are not the registered non-commit sensitivity estimate [ORS]. "),
    # appendix
    ("figures/fig_arms.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A1. Branch schematic F/K/S/N (schematic, no data). "),
    ("figures/fig_heldout_cases.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A2. Case-level outsider-effect certificate intervals versus m_O (EXP-002, descriptive); certificates are exploratory. "),
    ("figures/fig_supported_vs_oracle.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A3. Supported verdicts versus oracle exposure effect on DEV fixtures (DEV). "),
    ("paper/v2/figures/fig_gateA_integrity_audit.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A4. Gate A integrity checks (DEV): formal gate criteria passed with narrowing; the stricter A6 diagnostic is 350/360. "),
    ("figures/fig_confusion_dev.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A5. Baseline positive-call rates on DEV fixtures (DEV). "),
    ("paper/v2/figures/fig_prevalence_audit.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A6. RQ3 label-effect prevalence: 61/200 at eps=0 (NP); 41/200 at eps=0.1 is platform-dependent, not established. Exact CP95 intervals cross the 25% prediction threshold; the aggregate prediction failed. The eps=0 restriction was post hoc. "),
    ("figdir:fig_overattribution.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A7. "),
    ("figdir:fig_risk_E.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A8. "),
    ("figdir:fig_frontier.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A9. RQ2 frontier. "),
    ("figdir:fig_risk.svg", "## A. Limitations and Dual-Use / Ethical Considerations", "Figure A10. RQ5 attribution risk-coverage. "),
]

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def input_paths(figdir: Path) -> list[Path]:
    paths = [DRAFT, BIB, V2 / "submission.css", V2 / "prepare_audit_figures.py", ROOT / "figures/enh/prospective/fig_twins.json", ROOT / "figures/enh/prospective/fig_ladder.json", Path(__file__).resolve(), ROOT / "paper/build/markdown_to_html.py"]
    paths.extend((V2 / "fonts").glob("*"))
    for fname, _, _ in FIGS:
        p = figdir / fname[7:] if fname.startswith("figdir:") else ROOT / fname
        paths.append(p)
        if p.with_suffix(".json").exists():
            paths.append(p.with_suffix(".json"))
    return sorted(set(paths))

def clean_source(src: str) -> str:
    src = re.sub(r"(?s)<!--.*?-->\n?", "", src)
    src = re.sub(r"(?s)# TITLE OPTIONS.*?\n---\n\n", "", src)
    # Delete only the named editorial section, at any appendix letter; retain G/I.
    src = re.sub(r"(?ms)^## [A-Z]\. Figure plan\s*\n.*?(?=^## |\Z)", "", src)
    return src

def check_freshness() -> bool:
    p = BUILD / "build_report.json"
    if not p.exists():
        return False
    r = json.loads(p.read_text())
    if not r.get("pdf_current") or not r.get("inputs") or not r.get("outputs"):
        return False
    current = all((ROOT / name).is_file() and digest(ROOT / name) == sha
                  for group in ("inputs", "outputs") for name, sha in r[group].items())
    return current and "paper/v2/build/submission_v2.pdf" in r["outputs"]

def archive_previous() -> None:
    # Preserve previous derived artifacts, then invalidate the PDF candidate before
    # any operation can fail. --no-pdf also invalidates a previously built PDF.
    for name in ("submission_v2.md", "submission_v2.html", "submission_v2.pdf", "build_report.json"):
        p = BUILD / name
        if p.exists():
            archive = BUILD / "history" / digest(p)
            archive.mkdir(parents=True, exist_ok=True)
            target = archive / name
            if not target.exists():
                target.write_bytes(p.read_bytes())
    (BUILD / "submission_v2.pdf").unlink(missing_ok=True)

def render_pdf(html_out: Path, pdf_out: Path, chrome: str) -> None:
    # Fresh profile avoids reusing a running Chrome/default user session. Never
    # suppress renderer failures or leave a stale PDF at the candidate path.
    with tempfile.TemporaryDirectory(prefix="ccc-paper-") as profile:
        temporary_pdf = Path(profile) / "candidate.pdf"
        command = [chrome, "--headless=new", "--no-first-run", "--no-default-browser-check",
                   "--disable-background-networking", "--disable-component-update", "--disable-sync",
                   "--metrics-recording-only", f"--user-data-dir={profile}",
                   "--no-pdf-header-footer", f"--print-to-pdf={temporary_pdf}", html_out.as_uri()]
        with (BUILD / "renderer.log").open("w") as log:
            subprocess.run(command, check=True, stdout=log, stderr=log, timeout=60)
        content = temporary_pdf.read_bytes()
        if not content.startswith(b"%PDF-") or len(content) < 1000:
            raise ValueError("renderer did not produce a valid PDF header/output")
        # Atomic publication only after a successful renderer exit and output check.
        staged = BUILD / ".submission_v2.pdf.tmp"
        staged.write_bytes(content)
        os.replace(staged, pdf_out)

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
    ap.add_argument("--figdir", default="figures/enh/prospective")
    ap.add_argument("--figheight", default="1.9in", help="max rendered figure height")
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--chrome", default=CHROME, help="existing Chrome/Chromium executable")
    ap.add_argument("--check", action="store_true", help="exit 0 only if PDF and all source/output hashes are current")
    a = ap.parse_args()
    if a.check:
        current = check_freshness()
        print(json.dumps({"pdf_current": current}))
        return 0 if current else 1
    figdir = ROOT / a.figdir
    BUILD.mkdir(exist_ok=True)
    archive_previous()
    report_path = BUILD / "build_report.json"
    report = {"pdf_current": False, "status": "build started", "figdir": a.figdir,
              "built_utc": datetime.now(timezone.utc).isoformat()}
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    src = clean_source(DRAFT.read_text(encoding="utf-8"))
    # references from bib only
    src, ref_count = re.subn(r"(?s)## References\n.*?(?=\n---\n\n# (?:APPENDIX|Appendices))", refs_block(BIB.read_text(encoding="utf-8")).rstrip(), src)
    if ref_count != 1:
        raise ValueError("expected one references/appendix boundary")
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
        caption = caption.strip().replace("[", "(").replace("]", ")")
        src = src[:at].rstrip() + f"\n\n![{caption}]({rel})\n\n" + src[at:].lstrip("\n")
    # main-text / appendix split marker for page counting
    md_out, html_out, pdf_out = BUILD / "submission_v2.md", BUILD / "submission_v2.html", BUILD / "submission_v2.pdf"
    md_out.write_text(src, encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "paper/build/markdown_to_html.py"), str(md_out), str(html_out)], cwd=ROOT, check=True)
    h = html_out.read_text(encoding="utf-8")
    h = h.replace("max-height:3.3in", "max-height:%s" % a.figheight).replace("figure[aria-label^=\"Figure 4.\"] svg{max-height:4in}", "")
    h = h.replace("</style>", "ol{font-size:9pt;line-height:1.15;padding-left:1.4em}ol li{margin:.1em 0}</style>", 1)
    h = h.replace("<title>CCC submission</title>", "<title>CCC paper v2 (figures: %s)</title>" % a.figdir)
    # Template typography is local and hash-covered. Keep owner identity unset.
    h = h.replace("</style>", (V2 / "submission.css").read_text() + "</style>", 1)
    h = re.sub(r"(<h1>.*?</h1>)\s*(<p>Author:.*?</p>)", r'<header class="title-block">\1\2<p>With Apart Research</p><p class="title-note">Research conducted at the AI Collusion Research Sprint, October 2026.</p></header>', h, count=1, flags=re.S)
    h = h.replace("<h2>References</h2>", '<h2 class="references-start">References</h2>')
    h = h.replace("<h1>Appendices</h1>", '<h1 class="appendices-start">Appendices</h1>')
    html_out.write_text(h, encoding="utf-8")
    report.update({"placeholders_remaining": unresolved, "svgs": h.count("<svg "),
              "cite_check_tags": len(re.findall(r"CITE-CHECK", src)), "owner_tags": sorted(set(re.findall(r"\[OWNER[^\]]*\]", src))),
              "inputs": {str(p.relative_to(ROOT)): digest(p) for p in input_paths(figdir)},
              "outputs": {str(p.relative_to(ROOT)): digest(p) for p in (md_out, html_out)}})
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    if not a.no_pdf:
        try:
            render_pdf(html_out, pdf_out, a.chrome)
            report.update(pdf_current=True, pdf=str(pdf_out.relative_to(ROOT)))
            report["outputs"][str(pdf_out.relative_to(ROOT))] = digest(pdf_out)
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            pdf_out.unlink(missing_ok=True)
            report.update(status="PDF BLOCKED; HTML/Markdown available", renderer_error=str(exc))
            report_path.write_text(json.dumps(report, indent=2) + "\n")
            print(json.dumps(report, indent=2))
            return 1
    report["status"] = "PDF built; owner approval pending" if report["pdf_current"] else "HTML/Markdown only; no current PDF"
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
