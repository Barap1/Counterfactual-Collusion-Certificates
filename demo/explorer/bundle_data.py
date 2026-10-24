#!/usr/bin/env python3
"""Convert the JSON evidence pack (demo/data) into file://-loadable JS files.

Source of truth: demo/data/*.json. Numbers are copied verbatim; the only
transformation is overlaying untruncated message text from demo/data/full/ onto
the compact case file (same arm/rep or same record index) and wrapping the JSON
in `window.CCC_DATA` assignments. Never hand-edit demo/explorer/data/*.js.

Usage: python3 demo/explorer/bundle_data.py
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
PACK = HERE.parent / "data"
OUT = HERE / "data"


def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def dump(obj):
    # ensure_ascii keeps files pure ASCII; </ escaped so script text is safe
    return json.dumps(obj, ensure_ascii=True, separators=(",", ":")).replace("</", "<\\/")


def merge_full(case, full):
    """Overlay untruncated interaction text; fail loudly on structural mismatch."""
    if not full:
        return case, "compact"
    used = False
    oi_c, oi_f = case.get("original_interaction"), full.get("original_interaction")
    if oi_c and oi_f:
        assert len(oi_c) == len(oi_f), "original_interaction length mismatch"
        for a, b in zip(oi_c, oi_f):
            assert a["source_record_index"] == b["source_record_index"]
            a["messages"], a["tool_results"] = b["messages"], b["tool_results"]
        used = True
    cf = {(c["arm"], c["rep"]): c for c in full.get("continuations", []) if "messages" in c}
    for c in case.get("continuations", []):
        f = cf.get((c["arm"], c["rep"]))
        if f is not None and isinstance(f.get("messages"), list) and isinstance(c.get("messages"), list):
            assert len(f["messages"]) == len(c["messages"]), "continuation length mismatch"
            for a, b in zip(c["messages"], f["messages"]):
                a["messages"], a["tool_results"] = b["messages"], b["tool_results"]
            used = True
    if full.get("detector_text_evidence") and case.get("detector_text_evidence"):
        case["detector_text_evidence"] = full["detector_text_evidence"]
        used = True
    return case, ("full text" if used else "compact")


def write_js(path, stmt):
    path.write_text("window.CCC_DATA = window.CCC_DATA || {};\n" + stmt + "\n", encoding="ascii")


def main():
    OUT.mkdir(exist_ok=True)
    for old in OUT.glob("*.js"):
        old.unlink()
    index = load(PACK / "cases.json")
    study = load(PACK / "study.json")
    manifest = load(PACK / "MANIFEST.json")
    meta = {k: manifest[k] for k in ("schema", "generator", "generator_commit_HEAD", "archive_sha256", "source_strategy") if k in manifest}
    meta["n_files"] = len(manifest.get("files", []))
    meta["n_source_hashes"] = len(manifest.get("source_hashes", []))
    write_js(OUT / "index.js",
             "window.CCC_DATA.index=%s;\nwindow.CCC_DATA.study=%s;\nwindow.CCC_DATA.manifest=%s;\nwindow.CCC_DATA.cases=window.CCC_DATA.cases||{};"
             % (dump(index), dump(study), dump(meta)))
    n = 0
    for entry in index["cases"]:
        case = load(PACK / entry["file"])
        full_p = PACK / case["full_text_file"] if case.get("full_text_file") else None
        case, text_mode = merge_full(case, load(full_p) if full_p and full_p.exists() else None)
        case["_text_mode"] = text_mode
        write_js(OUT / ("case_%s.js" % entry["id"]),
                 "window.CCC_DATA.cases=window.CCC_DATA.cases||{};\nwindow.CCC_DATA.cases[%s]=%s;" % (dump(entry["id"]), dump(case)))
        n += 1
    twins = PACK / "twins.json"
    if twins.exists():
        write_js(OUT / "twins.js", "window.CCC_DATA.twins=%s;" % dump(load(twins)))
        print("twins.json found -> data/twins.js")
    else:
        print("twins.json absent -> Twin worlds section stays hidden")
    print("wrote index.js + %d case files to %s" % (n, OUT))


if __name__ == "__main__":
    main()
