#!/usr/bin/env python3
"""Legibility-only versions of existing figures. No experiments or new estimates."""
from pathlib import Path
import hashlib
import html
import json
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "paper/v2/figures"


def text(x, y, value, size=16, colour="#17324D", weight="normal"):
    return f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{colour}" font-weight="{weight}">{html.escape(str(value))}</text>'


def box(x, y, width, height, colour="#17324D"):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="3" fill="white" stroke="{colour}" stroke-width="1.5"/>'


def save(name, width, height, content, source, caption):
    original = ROOT / source
    meta = json.loads(original.read_text())
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>{content}</svg>'
    (OUT / (name + ".svg")).write_text(svg + "\n")
    meta.update(figure=name, caption=caption, versioned_from=source,
                original_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                field_differences=[{"field":"SVG layout and visible subset", "reason":"Compact existing content at readable main-text size; no plotted values or scientific categories changed."}])
    (OUT / (name + ".json")).write_text(json.dumps(meta, indent=2) + "\n")


def main():
    OUT.mkdir(exist_ok=True)
    ladder = json.loads((ROOT / "figures/enh/prospective/fig_ladder.json").read_text())["plotted_values"]
    colours = ["#8a5a00", "#0b5cad", "#b3261e", "#6b3fa0"]
    s = text(14, 24, "A knockout measures what a message did, not whether it should have done it.", 17, weight="bold")
    needs = ["Suspicious text", "Causal influence", "Harmful exposure", "Attribution"]
    gates = [["Transcript", "I0"], ["Knockout changes", "behaviour: I1"], ["Valid replay +", "harm/control gates"], ["Separating probe", "or norm: I4 / I5"]]
    for i, rung in enumerate(ladder["rungs"]):
        x = 12 + i * 177
        s += box(x, 40, 167, 100, colours[i])
        s += text(x+9, 64, rung["rung"] + " " + needs[i], 16, colours[i], "bold")
        s += text(x+9, 91, gates[i][0], 16) + text(x+9, 116, gates[i][1], 16)
    s += text(14, 163, "Each rung requires its own evidence; no rung implies the next. Conceptual diagram.", 16)
    save("fig_ladder_audit", 720, 180, s, "figures/enh/prospective/fig_ladder.json", "Evidence ladder (conceptual design): influence, harmful exposure and attribution require separately justified evidence.")

    data = json.loads((ROOT / "figures/enh/prospective/fig_twins.json").read_text())["plotted_values"]
    a, b = data["members"]["A"], data["members"]["B"]
    assert data["pair_rule"] == "P2, epsilon 0, lowest seed in run"
    assert all(a["outcomes_outsider"][k] == b["outcomes_outsider"][k] for k in ("F", "K", "S", "N", "J"))
    s = text(14, 24, "Designed twins: same evidence, different scripted labels", 20, weight="bold")
    s += text(14, 48, f'P2 | eps = 0 | seed {data["seed"]} (lowest-seed rule)', 16)
    for x, label, colour in [(14, "A: forbidden coordination", "#b3261e"), (370, "B: legitimate allocation", "#0b5cad")]:
        s += box(x, 62, 336, 40, colour) + text(x+10, 88, label, 18, colour, "bold")
    s += box(14, 115, 692, 80)
    rewards = a["outcomes_outsider"]
    s += text(26, 140, f'Shared I2 outsider rewards: F = {rewards["F"]:g}, K = {rewards["K"]:g}, S = {rewards["S"]:g}, N = {rewards["N"]:g}', 18)
    s += text(26, 165, f'tau_O = {rewards["K"]-rewards["F"]:g}; transcript and declared replay evidence remain identical through I3.', 16)
    s += text(14, 222, "I4 probe: make the outsiders cheaper on the contested task", 18, weight="bold")
    s += text(24, 250, "A keeps the contested allocation", 17, "#b3261e")
    s += text(380, 250, "B yields to the cheaper outsiders", 17, "#0b5cad")
    for x, member in [(24, a), (380, b)]:
        values = member["outcomes_outsider"]
        s += text(x, 274, f'Probe F = {values["PF"]:g}, K = {values["PK"]:g}', 17)
    s += text(14, 304, "I4 separates this constructed pair; this is not a general detection guarantee.", 16)
    save("fig_twins_audit", 720, 320, s, "figures/enh/prospective/fig_twins.json", "P2 deterministic twin exhibit (NP), selected by the lowest-seed rule. Scripted labels differ despite identical evidence through I3; the I4 environment probe separates them. Original full exhibit and metadata remain preserved.")

    original = ROOT / "figures/fig_heldout_delta.svg"
    old = "Outlined H02/H05: post-hoc sensitivity, not primary."
    new = "Outlined H02/H05: post-hoc case inspection (PH)."
    s = original.read_text().replace(old, new)
    s = re.sub(r'font-size="([0-9.]+)px"', lambda m: f'font-size="{max(14,float(m[1])):g}px"', s)
    (OUT / "fig_heldout_delta_audit.svg").write_text(s)
    p = OUT / "fig_heldout_delta_audit.json"
    meta = json.loads(p.read_text())
    meta["field_differences"] = [{"field":"SVG footer text", "before":old, "after":new}, {"field":"SVG font sizes", "after":"minimum 14px; coordinates and plotted marks unchanged"}, {"field":"caption", "reason":"Distinguish post-hoc case inspection from the separate registered non-commit sensitivity; all plotted values unchanged."}]
    p.write_text(json.dumps(meta, indent=2) + "\n")

    # Correct stale annotations only; original scientific marks/values are kept.
    for stem, old, new in [
        ("fig_gateA_integrity", "A6 sensitivity gate fails (350/360); overall Gate A reported FAIL. Counts are fixture checks, not real-world rates.", "A6 diagnostic fails (350/360); formal Gate A criteria passed with narrowing. Counts are fixture checks."),
        ("fig_prevalence", "n = 50 independent seeds per stratum", "n = 200 independent seeds per stratum"),
    ]:
        base = "figures/" if stem == "fig_gateA_integrity" else "figures/enh/prospective/"
        original = ROOT / (base + stem + ".svg")
        s = original.read_text()
        assert s.count(old) == 1, (stem, old)
        s = s.replace(old, new)
        if stem == "fig_prevalence":
            s = s.replace("61/200 = 30%", "61/200 = 30.5%").replace("41/200 = 20%", "41/200 = 20.5%")
            s = s.replace("the label-effect gap is the share of forbidden worlds below m_O.", "the plotted share is forbidden worlds at or above m_O.")
        (OUT / (stem + "_audit.svg")).write_text(s)
        meta = json.loads(original.with_suffix(".json").read_text())
        meta.update(figure=stem+"_audit", versioned_from=str(original.relative_to(ROOT)),
                    original_sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                    field_differences=[{"field":"SVG footer annotation", "before":old, "after":new, "plotted_values_changed":False, "precision_note":"Prevalence percentage labels use one decimal (30.5%, 20.5%); reading footer correctly describes tau_O >= m_O" if stem == "fig_prevalence" else "Counts unchanged"}])
        (OUT / (stem + "_audit.json")).write_text(json.dumps(meta, indent=2) + "\n")


if __name__ == "__main__":
    main()
