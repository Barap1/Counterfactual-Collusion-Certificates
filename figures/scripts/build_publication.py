#!/usr/bin/env python3
"""Build static, offline VIS-001a figures from committed Gate A evidence."""
from __future__ import annotations
import gzip, hashlib, json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "figures"
sys.path.insert(0, str(ROOT / "starter/collusion_hackathon/colosseum"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

NAVY = "#17324D"; TEAL = "#168C86"; AMBER = "#D99A28"; RED = "#B85C5C"
BLUE = "#4C78A8"; PURPLE = "#8C6BB1"; GREY = "#72808E"; PALE = "#F3F5F6"
METHODS = ["CCC", "B0", "B1", "B2", "B2+", "B3a", "B3b", "B4-rule"]
FAMILIES = ["A1a", "A1b", "A2a", "A2b", "A3a", "A3b", "A4a", "A4b", "A5a-verbatim", "A5a-paraphrase", "A5b", "A6a", "A6b", "A6c-F", "A6c-K", "A6d", "A6e", "A6f", "A6g", "A6h"]
COLORS = {"CCC": NAVY, "B0": GREY, "B1": BLUE, "B2": TEAL, "B2+": PURPLE, "B3a": "#E6AB02", "B3b": "#66A61E", "B4-rule": RED}

def sha(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1<<20),b""): h.update(b)
    return h.hexdigest()

def sidecar(stem, sources, caption, labels):
    payload={"figure":stem,"caption":caption,"labels":labels,"source_files":[{"path":str(p.relative_to(ROOT)),"sha256":sha(p)} for p in sources],"generated_by":"figures/scripts/build_publication.py","data_tier":"synthetic DEV fixtures; no real experiment data"}
    (OUT/f"{stem}.json").write_text(json.dumps(payload,indent=2,sort_keys=True)+"\n")

def style():
    plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8,"axes.titlesize":10,"axes.labelsize":8,"figure.facecolor":"white","axes.facecolor":"white","text.color":NAVY,"axes.labelcolor":NAVY,"xtick.color":NAVY,"ytick.color":NAVY,"pdf.fonttype":42,"svg.fonttype":"none"})

def save(fig, stem, sources, caption, labels, pdf=True):
    fig.savefig(OUT/f"{stem}.svg",bbox_inches="tight")
    if pdf: fig.savefig(OUT/f"{stem}.pdf",bbox_inches="tight")
    plt.close(fig); sidecar(stem,sources,caption,labels)

def arms():
    fig,ax=plt.subplots(figsize=(7.15,3.45)); ax.set_xlim(0,10); ax.set_ylim(0,5); ax.axis("off")
    ax.text(.2,4.77,"Shared recorded prefix",weight="bold",color=NAVY,fontsize=10)
    ax.add_patch(FancyBboxPatch((.25,3.55),2.2,.65,boxstyle="round,pad=.12",fc="#E9EEF1",ec="#AAB6BF"))
    ax.text(1.35,3.87,"same world + history",ha="center",va="center",color=NAVY)
    ax.add_patch(FancyArrowPatch((2.55,3.88),(3.35,3.88),arrowstyle="-|>",mutation_scale=12,color=NAVY,lw=1.5))
    ax.axvline(3.55,ymin=.11,ymax=.88,color=AMBER,lw=1.7,ls=(0,(3,2)))
    ax.text(3.55,4.47,"t* · earliest exposure",ha="center",color="#9A6810",weight="bold",fontsize=8)
    arms=[("F","Factual","receiver sees original E*",TEAL),("S","Sham","sham: empty mask, same receiver view",BLUE), ("K","Knockout","receiver-mask: E* withheld at every receiver prompt",RED), ("Nₘ","Placebo mask","mask matched non-audited M*; E* stays visible",PURPLE)]
    ys=[3.55,2.62,1.69,.76]
    for (code,name,desc,col),y in zip(arms,ys):
        ax.add_patch(FancyArrowPatch((3.58,3.87),(4.35,y+.27),connectionstyle="arc3,rad=0.0",arrowstyle="-|>",mutation_scale=10,color=col,lw=1.4))
        ax.add_patch(FancyBboxPatch((4.42,y),2.15,.56,boxstyle="round,pad=.1",fc=col,ec=col,alpha=.13))
        ax.text(4.56,y+.29,code,weight="bold",color=col,va="center",fontsize=9)
        ax.text(4.88,y+.29,name,weight="bold",color=NAVY,va="center")
        ax.text(6.82,y+.29,desc,va="center",color=NAVY,fontsize=7)
        ax.add_patch(FancyArrowPatch((6.25,y+.03),(6.25,y-.16),arrowstyle="-|>",mutation_scale=8,color=GREY,lw=.8))
        ax.text(6.55,y-.13,"fresh continuation",va="center",color=GREY,fontsize=7)
    ax.text(.3,.25,"Fixed across arms: world, checkpoint, non-target state, receiver policy and protocol.  Changed at receiver: only the declared post-fork exposure/view.",color=NAVY,fontsize=7.4)
    ax.text(9.8,4.55,"SCHEMATIC · no empirical values",ha="right",fontsize=7,color=GREY)
    protocol=ROOT/"docs/research/sci002/protocol.md"
    sources=[protocol]
    save(fig,"fig_arms",sources,"Schematic of F/S/K/Nₘ branches from earliest exposure. Nₘ masks preregistered matched non-audited message(s) M* from the same sender through the persistent receiver-mask path; audited exposure E* remains visible; this checks whether masking irrelevant content itself is harmless. No empirical values.",{"tier":"schematic","protocol":"v1.2 §3.1","N_m":"mask preregistered matched non-audited M* from same sender; E* remains visible"})

def integrity(data, source):
    checks=data["gate_checks"]
    rows=[("F vs S identical",checks["F_vs_S_identical"]), ("K-only intended exposure",checks["K_only_intended_exposure"]), ("Branch isolation",checks["branch_isolation"]), ("A2 not supported",checks["A2_not_supported"]), ("A6 invalid detection",checks["A6_invalid"])]
    fig,ax=plt.subplots(figsize=(7.15,2.55)); ax.axis("off")
    ax.text(.02,1.02,"Gate A integrity checks",transform=ax.transAxes,fontsize=11,weight="bold",color=NAVY)
    ax.text(.98,1.02,"DEV fixtures, protocol v1.2.2",transform=ax.transAxes,ha="right",fontsize=8,color=AMBER,weight="bold")
    table=[]
    for label,item in rows:
        passed=item.get("passed",item["pass"]==item["total"])
        table.append([label,f'{item["pass"]} / {item["total"]}',"PASS" if passed else "FAIL"])
    t=ax.table(cellText=table,colLabels=["Check","Pass / total","Gate"],cellLoc="left",colLoc="left",bbox=[.02,.08,.96,.82],colWidths=[.52,.25,.19])
    t.auto_set_font_size(False); t.set_fontsize(8)
    for (r,c),cell in t.get_celld().items():
        cell.set_edgecolor("#D7DEE3"); cell.set_linewidth(.6)
        if r==0: cell.set_facecolor(NAVY); cell.get_text().set_color("white"); cell.get_text().set_weight("bold")
        elif c==2: cell.set_facecolor("#F6E8E8" if table[r-1][2]=="FAIL" else "#E8F3F1"); cell.get_text().set_color(RED if table[r-1][2]=="FAIL" else TEAL); cell.get_text().set_weight("bold")
        else: cell.set_facecolor("#FAFBFC" if r%2 else "white")
    ax.text(.02,-.04,"A6 sensitivity gate fails (350/360); overall Gate A reported FAIL. Counts are fixture checks, not real-world rates.",transform=ax.transAxes,fontsize=7,color=GREY)
    save(fig,"fig_gateA_integrity",[source],"Gate A integrity checks on DEV fixtures, protocol v1.2.2. Each cell is a fixture check; this is not a real-world rate. Overall Gate A: FAIL.",{"tier":"DEV fixtures","protocol":"v1.2.2","overall":"FAIL"})

def classify(label): return label in {"flag","supported"}
def confusion_panels(data, source):
    rows=data["rows"]
    paths=[None,False,True]
    titles=["Mechanism label","Oracle path_active = false","Oracle path_active = true"]
    # Full-width stacked panels keep family labels and 7 pt k/n labels legible at 2-column scale.
    fig,axs=plt.subplots(3,1,figsize=(7.15,12.4),sharex=True,gridspec_kw={"hspace":.23})
    fig.subplots_adjust(left=.20,right=.88,top=.91,bottom=.06)
    fig.suptitle("Positive-call rate by DEV fixture family and method",x=.20,y=.975,ha="left",fontsize=12,weight="bold",color=NAVY)
    fig.text(.20,.948,"DEV fixtures · protocol v1.2.2 · θ=0.4",fontsize=8,color=AMBER,weight="bold",ha="left")
    import numpy as np
    for ax,path,title in zip(axs,paths,titles):
        rates=np.full((len(FAMILIES),len(METHODS)),np.nan)
        annotations=[["" for _ in METHODS] for _ in FAMILIES]
        for yi,fam in enumerate(FAMILIES):
            subset=[r for r in rows if r["family"]==fam and (path is None or r["oracle_strata"]["path_active"] is path)]
            for xi,method in enumerate(METHODS):
                if not subset: continue
                k=sum(classify(item["native"]["CCC"]["status"]) if method=="CCC" else classify(item["native"]["baselines"][method]["label"]) for item in subset)
                n=len(subset); rates[yi,xi]=k/n; annotations[yi][xi]=f"{k}/{n}"
        im=ax.imshow(rates,aspect="auto",interpolation="nearest",cmap="cividis",vmin=0,vmax=1)
        ax.set_title(title,loc="left",fontsize=9,weight="bold",color=NAVY,pad=7)
        ax.set_yticks(range(len(FAMILIES)),labels=FAMILIES,fontsize=7)
        ax.set_xticks(range(len(METHODS)),labels=METHODS,fontsize=7)
        ax.tick_params(axis="x",top=True,labeltop=True,bottom=False,labelbottom=False,pad=4)
        ax.set_xticks(np.arange(-.5,len(METHODS),1),minor=True); ax.set_yticks(np.arange(-.5,len(FAMILIES),1),minor=True)
        ax.grid(which="minor",color="white",linewidth=.8); ax.tick_params(which="minor",bottom=False,left=False)
        ax.axvline(.5,color="#B85C5C",linewidth=2.2)
        for yi in range(len(FAMILIES)):
            for xi in range(len(METHODS)):
                val=rates[yi,xi]
                # Dark text on pale cells and white text on darker cells maintains contrast.
                color=(NAVY if val < .45 else "white") if not np.isnan(val) else NAVY
                ax.text(xi,yi,annotations[yi][xi],ha="center",va="center",fontsize=7,color=color,weight="bold")
        for spine in ax.spines.values(): spine.set_visible(False)
    cax=fig.add_axes([.905,.18,.022,.68])
    cb=fig.colorbar(im,cax=cax); cb.set_label("Positive-call rate (k/n)",fontsize=8); cb.ax.tick_params(labelsize=7)
    caption="Each cell shows positive-call rate with positive count/eligible fixture count (k/n). Panels show all fixtures and oracle path_active strata. DEV fixtures only; protocol v1.2.2, theta=0.4; not real observations."
    save(fig,"fig_confusion_dev",[source],caption,{"tier":"DEV fixtures","protocol":"v1.2.2","theta":0.4,"fixture_count":data["instances"],"methods":METHODS,"families":FAMILIES,"cell":"positive-call rate; annotation k/n","panels":["mechanism label","oracle path_active=false","oracle path_active=true"],"colormap":"cividis"})

def supported_vs_oracle(data, source):
    # Non-A6 fixture cells only. The threshold is inclusive for this descriptive
    # comparison, matching the registered false-support definition.
    rows=[r for r in data["rows"] if not r["family"].startswith("A6")]
    m=data["parameters"]["m_O"]
    counts={"correct support":0,"false support":0,"not supported below":0,"not supported above":0,"abstention":0}
    positive_abstentions=[]
    for r in rows:
        c=r["native"]["CCC"]
        status=c["status"].lower()
        tau=r["oracle_effects"]["tau_O"]
        positive=tau >= m
        if status in {"abstain","inconclusive"}:
            counts["abstention"]+=1
            if positive and r["oracle_strata"]["path_active"]:
                positive_abstentions.append(r)
            continue
        support=status in {"supported","support"}
        if support and positive: counts["correct support"]+=1
        elif support: counts["false support"]+=1
        elif positive: counts["not supported above"]+=1
        else: counts["not supported below"]+=1

    # Assign each eligible cell exactly once. A cell with multiple reasons gets
    # the most directly causal reason first, with the remaining reason noted.
    priority=("pattern_mutual_disruption","pattern_efficient_transfer","not_identifiable_redundant")
    primary_counts={key:0 for key in priority}
    for r in positive_abstentions:
        reasons=r["native"]["CCC"].get("reasons",[]) or r["native"]["CCC"].get("flags",[])
        primary=next((key for key in priority if key in reasons),"other")
        primary_counts[primary]=primary_counts.get(primary,0)+1
    assert len(positive_abstentions)==20, f"expected 20 oracle-positive path-active abstentions; got {len(positive_abstentions)}"
    assert sum(primary_counts.values())==len(positive_abstentions)
    assert sum(counts.values())==len(rows)
    fig,axs=plt.subplots(1,2,figsize=(7.15,3.45),gridspec_kw={"width_ratios":[1.25,1]})
    ax=axs[0]
    cats=list(counts); vals=[counts[k] for k in cats]
    cols=[TEAL,RED,BLUE,RED,AMBER]
    bars=ax.bar(range(len(cats)),vals,color=cols,width=.72)
    ax.set_xticks(range(len(cats)),["Correct support\n(τO ≥ mO)","False support\n(τO < mO)","Not supported,\nτO < mO","Not supported,\nτO ≥ mO","Abstain"],fontsize=6.3)
    ax.set_ylabel("DEV fixture cells"); ax.set_title("CCC status vs oracle τO",loc="left",weight="bold",color=NAVY)
    ax.grid(axis="y",color="#E7EBEE",lw=.7); ax.set_axisbelow(True)
    for b,v in zip(bars,vals): ax.text(b.get_x()+b.get_width()/2,v+2,str(v),ha="center",fontsize=8,weight="bold",color=NAVY)
    ax=axs[1]; ax.set_title("Oracle-positive abstentions",loc="left",weight="bold",color=NAVY)
    items=[(key,primary_counts[key]) for key in priority if primary_counts[key]]
    if items:
        ax.barh(range(len(items)),[v for _,v in items],color=AMBER)
        ax.set_yticks(range(len(items)),[f"{k}  ({v})" for k,v in items],fontsize=7); ax.invert_yaxis()
        for i,(_,v) in enumerate(items): ax.text(v+.15,i,str(v),va="center",fontsize=7,color=NAVY)
    else: ax.text(.1,.5,"No abstentions",transform=ax.transAxes)
    ax.set_xlabel("Cells (n=20)"); ax.grid(axis="x",color="#E7EBEE",lw=.7); ax.set_axisbelow(True)
    ax.text(0,-.25,"Primary reasons; reasons may co-occur. All non-A6 abstentions: n=134.",transform=ax.transAxes,fontsize=6.3,color=GREY,va="top")
    fig.suptitle("DEV non-A6 fixture cells · CCC vs oracle",x=.04,y=1.02,ha="left",fontsize=11,weight="bold",color=NAVY)
    fig.tight_layout()
    caption="Non-A6 DEV fixture cells classified by CCC status against the inclusive oracle threshold tau_O >= m_O. Not supported means the audited exposure is not shown to meet the harm threshold; it is not exoneration. Right panel shows the 20 inconclusive cells with tau_O >= m_O and path_active, assigning each once to a primary reason; reasons may co-occur. All non-A6 abstentions: n=134."
    save(fig,"fig_supported_vs_oracle",[source],caption,{"tier":"DEV fixtures","protocol":"v1.2.2","theta":0.4,"excluded_families":["A6"],"cells":len(rows),"m_O":m,"oracle_positive":"tau_O >= m_O","oracle_positive_path_active_abstentions":len(positive_abstentions),"path_active":"required for right-panel selection","counts":counts,"primary_abstention_reason_counts":primary_counts,"abstention_reason_note":"primary reason assigned once per cell by priority; source reasons may co-occur","all_non_A6_abstentions":counts["abstention"]})

def main():
    OUT.mkdir(parents=True,exist_ok=True); style()
    source=ROOT/"docs/gate_a/v1.2/correction_v1.2.2/gate_a_results.json.gz"
    data=json.load(gzip.open(source,"rt",encoding="utf-8"))
    arms(); integrity(data,source); confusion_panels(data,source); supported_vs_oracle(data,source)
if __name__=="__main__": main()
