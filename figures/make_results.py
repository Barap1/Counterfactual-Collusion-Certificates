#!/usr/bin/env python3
"""Template for future ccc.analysis output figures; intentionally not run for results.

Expected input: results/analysis/<phase>/figure_data/*.csv and aggregate.json,
following docs/stats/analysis_spec.md §8. This script refuses to run until
those tables exist and contain the documented columns.
"""
from __future__ import annotations
import argparse, csv, hashlib, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
NAVY="#17324D"; TEAL="#168C86"; AMBER="#D99A28"; BLUE="#4C78A8"; GREY="#72808E"

def digest(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def read_csv(path, required):
    if not path.exists(): raise FileNotFoundError(f"Required analysis output missing: {path}")
    with path.open(newline="",encoding="utf-8") as f:
        reader=csv.DictReader(f)
        missing=set(required)-set(reader.fieldnames or [])
        if missing: raise ValueError(f"{path}: missing schema columns {sorted(missing)}")
        return list(reader)

def emit(fig, out, name, inputs, caption, phase, analysis_version):
    out.mkdir(parents=True,exist_ok=True)
    fig.savefig(out/f"{name}.svg",bbox_inches="tight")
    fig.savefig(out/f"{name}.pdf",bbox_inches="tight")
    plt.close(fig)
    (out/f"{name}.json").write_text(json.dumps({"figure":name,"caption":caption,"phase":phase,"analysis_version":analysis_version,"source_files":[{"path":str(p.relative_to(ROOT)),"sha256":digest(p)} for p in inputs]},indent=2,sort_keys=True)+"\n")

def make_delta(rows, out, inputs, phase, version):
    # figure_data/fig_delta_by_world: per-world d_w and B1/B2 tau_O.
    for c in ("world_id","d_w","tau_O_B1","tau_O_B2","n_independent"):
        if rows and c not in rows[0]: raise ValueError(f"fig_delta_by_world missing {c}")
    rows=sorted(rows,key=lambda r:r["world_id"])
    fig,ax=plt.subplots(figsize=(3.4,2.2)); x=range(len(rows))
    vals=[float(r["d_w"]) for r in rows]
    ax.axhline(0,color=GREY,lw=.8); ax.bar(x,vals,color=[TEAL if v>=0 else AMBER for v in vals],width=.72)
    ax.set(xlabel="World (sorted by ID)",ylabel="dᵥ = τO(B1) − τO(B2) · reward units",title="Per-world exposure contrast")
    ax.spines[["top","right"]].set_visible(False)
    emit(fig,out,"fig_delta_by_world",inputs,"Per-world signed B1−B2 outsider-reward contrast; world is the independent unit. Error intervals are not implied by this per-world display.",phase,version)

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("analysis_dir",type=Path,help="results/analysis/<phase>"); ap.add_argument("--out",type=Path,default=None); args=ap.parse_args()
    base=args.analysis_dir if args.analysis_dir.is_absolute() else ROOT/args.analysis_dir
    if not (base/"aggregate.json").exists(): raise SystemExit(f"No aggregate.json found at {base}; no results figure was generated.")
    aggregate=json.loads((base/"aggregate.json").read_text())
    phase=aggregate.get("phase",base.name); version=aggregate.get("analysis_version","unknown")
    src=base/"figure_data/fig_delta_by_world.csv"
    rows=read_csv(src,["world_id","d_w","tau_O_B1","tau_O_B2","n_independent"])
    out=args.out or ROOT/"figures/results"/phase
    make_delta(rows,out,[src,base/"aggregate.json"],phase,version)

if __name__=="__main__": main()
