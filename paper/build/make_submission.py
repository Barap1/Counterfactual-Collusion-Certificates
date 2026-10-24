#!/usr/bin/env python3
"""Build a clean, reviewable Markdown submission from the tagged audit draft."""
from __future__ import annotations

import re
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DRAFT = ROOT / "paper/draft.md"
BIB = ROOT / "paper/references_draft.bib"
PLAN = ROOT / "paper/figures_plan.md"
OUT = ROOT / "paper/build/submission.md"
HTML = ROOT / "paper/build/submission.html"
REPORT = ROOT / "paper/build/submission_validation.json"


def bib_entries(text: str) -> dict[str, str]:
    entries: dict[str, str] = {}
    for match in re.finditer(r"@\w+\s*\{\s*([^,]+),", text):
        key = match.group(1).strip()
        start = match.start()
        depth = 0
        escaped = False
        for pos in range(text.index("{", start), len(text)):
            char = text[pos]
            if char == "{" and not escaped:
                depth += 1
            elif char == "}" and not escaped:
                depth -= 1
                if depth == 0:
                    entries[key] = text[start : pos + 1]
                    break
            escaped = (char == "\\" and not escaped)
            if char != "\\":
                escaped = False
    return entries


def field(entry: str, name: str) -> str:
    match = re.search(rf"\b{name}\s*=\s*\{{((?:[^{{}}]|\{{[^{{}}]*\}})*)\}}", entry, re.S)
    if not match:
        match = re.search(rf'\b{name}\s*=\s*"([^"]*)"', entry, re.S)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def main() -> int:
    source = DRAFT.read_text(encoding="utf-8")
    bib = bib_entries(BIB.read_text(encoding="utf-8"))
    plan = PLAN.read_text(encoding="utf-8")

    # Remove any explicit tag-grammar / DRAFT preamble section before the abstract.
    abstract = re.search(r"(?m)^## Abstract\s*$", source)
    marker = re.search(r"(?im)^#{1,3} .*?(?:tag grammar|draft preamble).*?$", source)
    if abstract and marker and marker.start() < abstract.start():
        source = source[: marker.start()] + source[abstract.start() :]

    source = re.sub(r"\[VERIFIED\s*:[^\]]*\]", "", source)
    source = re.sub(r"\[PROVISIONAL(?:\s*:[^\]]*)?\]", "", source)
    source = re.sub(r"\[RESULT-PENDING(?:\s*:[^\]]*)?\]", "", source)
    # Clean punctuation left by removed evidence tags without changing prose.
    source = re.sub(r"\(\s*\)", "", source)
    source = re.sub(r"[ \t]+([.,;:!?])", r"\1", source)
    source = re.sub(r":\s*\.", ".", source)
    source = re.sub(r"[ \t]{2,}", " ", source)

    owner_tags = list(dict.fromkeys(re.findall(r"\[(?:OWNER|TODO)\b[^\]]*\]", source)))

    cite_order: list[str] = []

    def cite_group(match: re.Match[str]) -> str:
        raw = match.group(1)
        keys = re.findall(r"@?([A-Za-z][A-Za-z0-9_:-]*)", raw)
        looks_like_citation = raw.startswith("@") or any(key in bib for key in keys) or bool(re.fullmatch(r"[A-Za-z]+(?:19|20)\d{2}[A-Za-z0-9_:-]*(?:;.*)?", raw))
        if looks_like_citation and any(key not in bib for key in keys):
            raise ValueError(f"Unresolved citation group: {raw}")
        if not keys or any(key not in bib for key in keys):
            return match.group(0)
        for key in keys:
            if key not in cite_order:
                cite_order.append(key)
        nums = [str(cite_order.index(key) + 1) for key in keys]
        return "[" + ", ".join(nums) + "]"

    # Handles both [@key] and this draft's [key; key] / [key] citation forms.
    source = re.sub(r"\[([^\[\]]+)\]", cite_group, source)
    unresolved = sorted(set(re.findall(r"\[@([A-Za-z][A-Za-z0-9_:-]*)\]", source)))
    if unresolved:
        raise ValueError(f"Unresolved bracket citation keys: {unresolved}")

    # Keep the complete usage statement last, irrespective of draft placement.
    usage_match = re.search(r"(?ms)^## LLM Usage Statement\s*\n.*?(?=^## |\Z)", source)
    usage = usage_match.group(0).strip() if usage_match else ""
    if usage_match:
        source = source[:usage_match.start()] + source[usage_match.end():]
    # Replace reference notes at their template position, before the appendices.
    source = re.sub(r"(?ms)^## References\s*\n.*?(?=^## |\Z)", "", source)
    refs = ["## References", ""]
    for number, key in enumerate(cite_order, 1):
        entry = bib[key]
        authors = field(entry, "author").replace(" and ", "; ") or ""
        title = field(entry, "title").replace("{", "").replace("}", "")
        year = field(entry, "year")
        journal = field(entry, "journal")
        eprint = field(entry, "eprint")
        url = field(entry, "url")
        detail = f" {journal}." if journal else (f" arXiv:{eprint}." if eprint else "")
        link = f" <{url}>" if url else ""
        refs.append(f"{number}. {authors} ({year}). {title}.{detail}{link}")
    appendix = re.search(r"(?m)^## Appendix A", source)
    insert_at = appendix.start() if appendix else len(source)
    source = source[:insert_at].rstrip() + "\n\n" + "\n".join(refs) + "\n\n" + source[insert_at:].lstrip()

    # The explicit manifest is the single source of figure placement and captions.
    rows = re.findall(r"(?m)^\|\s*(B?\d+)\s*\|\s*(figures/[^|]+\.svg)\s*\|\s*([^|]+)\|\s*([^|]+)\|", plan)
    if len(rows) != 6:
        raise ValueError(f"Expected six manifest figures, got {len(rows)}")
    inserted = []
    for number, filename, subsection, caption in rows:
        path = ROOT / filename.strip()
        if not path.is_file():
            raise ValueError(f"Missing figure: {path}")
        heading = re.search(rf"(?m)^### {re.escape(subsection.strip())} .*?$", source)
        if not heading:
            raise ValueError(f"Missing placement: {subsection}")
        following = re.search(r"(?m)^##?#? ", source[heading.end():])
        insert_at = heading.end() + following.start() if following else len(source)
        block = f"\n\n![Figure {number}. {caption.strip()}](../../{filename.strip()})\n\n"
        source = source[:insert_at].rstrip() + block + source[insert_at:]
        inserted.append(filename.strip())
    source = source.rstrip() + "\n\n" + usage + "\n"

    OUT.write_text(source, encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "paper/build/markdown_to_html.py"), str(OUT), str(HTML)], cwd=ROOT, check=True)

    evidence_left = re.findall(r"\[(?:VERIFIED\s*:|PROVISIONAL(?:\s*:|\])|RESULT-PENDING(?:\s*:|\]))", source)
    cited_keys = set(cite_order)
    bib_missing = sorted(cited_keys - bib.keys())
    figure_paths = re.findall(r"!\[[^\]]*\]\(([^)]+\.svg)\)", source)
    bad_figures = [p for p in figure_paths if not (OUT.parent / p).resolve().is_file()]
    if evidence_left or bib_missing or bad_figures:
        raise ValueError(f"Validation failed: evidence={evidence_left}, bib={bib_missing}, figures={bad_figures}")

    html = HTML.read_text(encoding="utf-8")
    headings = re.findall(r"(?m)^## (.+)$", source)
    expected = ["Abstract", "1. Introduction", "2. Related Work", "3. Methods", "4. Results", "5. Discussion and Limitations", "6. Conclusion", "Code and Data"]
    if "Author Contributions" in headings:
        expected.append("Author Contributions")
    expected += ["References", "Appendix A. Limitations and Dual-Use / Ethical Considerations", "Appendix B. Additional material", "LLM Usage Statement"]
    remaining_ids = {name: sorted(set(re.findall(r"[^\n]*(?:REV-|DEV-0|STAT-|PUB-|ENG-|director|module-13)[^\n]*", body, re.I))) for name, body in [("submission.md", source), ("submission.html", html)]}
    evidence_pattern = r"\[(?:VERIFIED|PROVISIONAL|RESULT-PENDING)\b"
    if headings != expected or html.count("<svg ") != 6 or re.search(evidence_pattern, html) or any(remaining_ids.values()):
        raise ValueError("Section, SVG, evidence or internal-ID validation failed")
    report = {"citations_resolved": len(cite_order), "citation_keys": cite_order,
              "figures_embedded": inserted, "section_order": headings,
              "evidence_tags": 0, "remaining_internal_ids": remaining_ids,
              "remaining_owner_todo_tags": owner_tags}
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
