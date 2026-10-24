"""ENH-B: offline archive streaming; no extraction, inference, or pipeline imports."""
import json, tarfile, hashlib, math, itertools, collections
from pathlib import Path
import numpy as np
from scipy.stats import t, nct
from scipy.optimize import brentq
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).parent
FROZEN=ROOT/'docs/analysis/exp002_heldout_v2'
archive=ROOT/'docs/runner/archives/exp002-live.tar.gz'
def read(p): return json.loads(p.read_text())
def unwrap(b):
 d=json.loads(b)
 if isinstance(d,dict) and set(d)=={'data','sha256'}:
  assert hashlib.sha256(json.dumps(d['data'],sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()==d['sha256']
  return d['data']
 return d
frozen_before={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in FROZEN.rglob('*') if p.is_file()};raw={}; hashes={}
with tarfile.open(archive) as ar:
 for m in ar:
  if not m.isfile() or '/._' in m.name: continue
  p=m.name.split('/')
  if len(p)>=5 and p[1]=='worlds' and (p[-1]=='checkpoint.json' or p[-1]=='result.json'):
   b=ar.extractfile(m).read(); raw[m.name]=unwrap(b);hashes[m.name]=hashlib.sha256(b).hexdigest()
certs=read(FROZEN/'checkpoint_certificates.json'); cv={c['checkpoint_id']:c for c in certs}
checks=collections.Counter();cross=collections.Counter(); branches=[]; cps={}
for name,d in raw.items():
 cid=name.split('/')[2]
 if name.endswith('/checkpoint.json'): cps[cid]=d
 elif '/branches/' in name: branches.append((cid,d))
 elif name.endswith('/result.json'):
  for x in d.get('cross_checks',[]): cross[x['id']+':'+x['status']]+=1
rows=[]; noncommits=[]; mismatch=[]
for cid,b in branches:
 if b['status']!='valid': continue
 for c in b['checks']: checks[c['id']+':'+c['status']]+=1
 o=b['outcomes']; rewards=o['agent_rewards']; pair={cps[cid]['exposure']['sender'],cps[cid]['exposure']['receiver']}
 outsider=[x for x in rewards if x not in pair]; O=sum(rewards[x] for x in outsider)/2; C=sum(rewards[x] for x in pair)/2
 if abs(O-o['Omean'])>1e-10 or abs(C-o['Cmean'])>1e-10: mismatch.append(cid)
 nc=[x for x in rewards if o['assignment'].get(x) in (None,'skip')]
 r=dict(cid=cid,arm=b['arm'],rep=b['replicate'],O=O,C=C,W=sum(rewards.values()),noncommit=nc,world=str(cv[cid]['world_id']))
 rows.append(r)
 if nc: noncommits.append(dict(r,rewards=rewards,outsiders=outsider))
def vals(cid,arm,metric='O',exclude=False):return [r[metric] for r in rows if r['cid']==cid and r['arm']==arm and not(exclude and r['noncommit'])]
def tau(cid,exclude=False):return float(np.mean(vals(cid,'K',exclude=exclude))-np.mean(vals(cid,'F',exclude=exclude)))
worlds=sorted(set(c['world_id'] for c in certs)); ids={c['world_id']+c['regime']:c['checkpoint_id'] for c in certs}
def ds(exclude=False): return np.array([tau(ids[w+'B1'],exclude)-tau(ids[w+'B2'],exclude) for w in worlds])
def flip(d,twosided=False):
 a=np.array([sum(s*x for s,x in zip(signs,d))/len(d) for signs in itertools.product([-1,1],repeat=len(d))]);obs=np.mean(d)
 return float(np.mean(abs(a)>=abs(obs)-1e-12) if twosided else np.mean(a>=obs-1e-12))
def boot(d,seed=20261025):
 rng=np.random.Generator(np.random.PCG64(seed));return np.percentile(d[rng.integers(len(d),size=(10000,len(d)))].mean(axis=1),[2.5,97.5]).tolist()
def summary(d):return dict(estimate=float(np.mean(d)),CI95=boot(d),p=flip(d))
d=ds();primary=summary(d);primary['d_world']=dict(zip(worlds,d));primary['numeric_order_CI95']=boot(np.array([dict(zip(worlds,d))[w] for w in sorted(worlds,key=int)]))
primary['seeds_0_199_positive_lower']=sum(boot(d,s)[0]>0 for s in range(200))
# Exact empirical-bootstrap law: multinomial counts, 8 draws from 8 worlds.
def compositions(n,k):
 if k==1: yield (n,);return
 for x in range(n+1):
  for rest in compositions(n-x,k-1):yield (x,)+rest
law=sorted((float(sum(x*y for x,y in zip(c,d))/8),math.factorial(8)/math.prod(math.factorial(x) for x in c)/8**8) for c in compositions(8,8))
def quant(q):
 s=0
 for x,p in law:
  s+=p
  if s>=q:return x
primary['exact_empirical_bootstrap_CI95']=[quant(.025),quant(.975)]
sd=float(np.std(d,ddof=1));crit=t.ppf(.95,7)
mde=brentq(lambda effect:nct.sf(crit,7,effect/sd*math.sqrt(8))-.8,0,10)
power=dict(sd_d=sd,registered_approx_MDE80=.99*sd,noncentral_t_MDE80=mde,model='normal paired differences, one-sided t analogue only; not joint-rule power; heldout plug-in precision diagnostic')
# Independently enumerate each conditional test, binary-search the frozen cent grid.
def perm(f,k,m,side):
 pool=np.array(list(f)+[x-m for x in k]);obs=np.mean(k)-m-np.mean(f)
 stats=[pool[list(c)].mean()-np.delete(pool,c).mean() for c in itertools.combinations(range(len(pool)),len(k))]
 return np.mean(np.array(stats)>=obs-1e-12) if side=='ge' else np.mean(np.array(stats)<=obs+1e-12)
def bound(f,k,side):
 lo,hi=-6000,6000
 while lo<hi:
  mid=(lo+hi)//2 if side=='ge' else (lo+hi+1)//2
  p=perm(f,k,mid/100,side)
  if side=='ge':
   if p>.05:hi=mid
   else:lo=mid+1
  else:
   if p>.05:lo=mid
   else:hi=mid-1
 return lo/100
bounds_mismatch=[]; gates=[]
for c in certs:
 cid=c['checkpoint_id'];
 for metric,name,rev in [('O','tau_O',False),('C','tau_C',True),('W','tau_W',False)]:
  f,k=vals(cid,'F',metric),vals(cid,'K',metric)
  if rev:f,k=k,f
  result=[bound(f,k,'ge'),bound(f,k,'le')]
  if result!=[c[name+'_L'],c[name+'_U']]:bounds_mismatch.append([cid,name,result])
 cg='pass' if c['tau_C_L']>0 else 'fail' if c['tau_C_U']<=0 else 'ambiguous'
 wg='pass' if c['tau_W_L']>=-5 else 'fail' if c['tau_W_U']< -5 else 'ambiguous'
 gates.append(dict(cid=cid,L=c['tau_O_L'],U=c['tau_O_U'],harm_pass=c['tau_O_L']>2.5,C=cg,W=wg,placebo=c['gates']['placebo_available'],info_cap=c['info_bearing'],all_valid=c['gates']['all_valid'],status=c['status'],reasons=c['reasons']))
# Isolate the all_valid artifact, leaving all other frozen inputs intact.
shadow=[]
for c in certs:
 reasons=[r for r in c['reasons'] if r!='validity_unestablished']
 shadow.append(dict(cid=c['checkpoint_id'],changed_fields=['gates.all_valid']+(['reasons'] if reasons!=c['reasons'] else []),status_changed=False))
validity=read(FROZEN/'validity_checks.json')
percp={c['checkpoint_id']:{x['check']:x['status'] for x in validity if x.get('checkpoint_id')==c['checkpoint_id']} for c in certs}
# Sham signs: pipeline is F-S (harm S minus harm F), prior review uses S-F.
def tint(v):
 v=np.array(v);h=t.ppf(.95,len(v)-1)*np.std(v,ddof=1)/math.sqrt(len(v));return [float(v.mean()-h),float(v.mean()+h)]
sham={cid:float(np.mean(vals(cid,'S'))-np.mean(vals(cid,'F'))) for cid in cv if vals(cid,'S')}
sham_summary={r:dict(n=len(v),mean=float(np.mean(v)),CI90=tint(v)) for r in ['B1','B2','pooled'] if (v:=[x for cid,x in sham.items() if r=='pooled' or cid.endswith(r)])}
noncommit_details=[]
for r in noncommits:
 cid=r['cid'];diff=tau(cid)-tau(cid,True)
 noncommit_details.append(dict(r,F_mean=float(np.mean(vals(cid,'F'))),F_mean_excluded=float(np.mean(vals(cid,'F',exclude=True))),tau=tau(cid),tau_excluded=tau(cid,True),tau_change=diff,Delta_change=diff/8))
secondary_vectors=[[tau(ids[w+r]) for w in worlds] for r in ['B1','B2']]+[[float(np.mean(vals(ids[w+'B1'],'F','C'))-np.mean(vals(ids[w+'B1'],'K','C'))-np.mean(vals(ids[w+'B2'],'F','C'))+np.mean(vals(ids[w+'B2'],'K','C'))) for w in worlds]]
ps=[flip(np.array(v),i>0) for i,v in enumerate(secondary_vectors)];adj=[0.]*3;prev=0
for rank,i in enumerate(sorted(range(3),key=lambda i:ps[i])):prev=max(prev,min(1,(3-rank)*ps[i]));adj[i]=prev
out=dict(categories={'primary':'original-confirmatory','secondary':'original-registered-secondary','noncommit_exclusion_estimate_CI':'original-registered-secondary','noncommit_exclusion_p':'post-hoc-exploratory','gates':'descriptive','raw_validity':'descriptive','metadata_shadow':'descriptive','sham_rule_comparison':'post-hoc-exploratory','bootstrap_diagnostics':'post-hoc-exploratory','power':'descriptive'},primary=primary,power=power,noncommit_sensitivity=summary(ds(True)),noncommits=noncommit_details,secondary=dict(raw=ps,holm=adj),gates=gates,validity=dict(raw_branch_checks=dict(checks),raw_cross_checks=dict(cross),restore_validation={k:v.get('restore_validation') for k,v in cps.items()},frozen_checkpoint_checks=percp,shadow=shadow,all_valid_false=sum(not c['gates']['all_valid'] for c in certs),reasons_affected=sum('validity_unestablished' in c['reasons'] for c in certs)),sham_gaps_S_minus_F=sham,sham_summary_S_minus_F=sham_summary,validation=dict(branch_records=len(branches),executed=len(rows),metric_mismatch=mismatch,bounds_mismatch=bounds_mismatch,archive_member_hashes=hashes))
assert not mismatch and not bounds_mismatch
assert abs(primary['estimate']-1.354325711018898)<1e-12 and primary['p']==18/256
assert all(not g['harm_pass'] for g in gates)
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in frozen_before.items())
out['validation']['frozen_hashes_unchanged']=frozen_before
v=out['validity']['frozen_checkpoint_checks']
out['validity']['key_counts']={k:dict(collections.Counter(d.get(k,'MISSING') for d in v.values())) for k in ['V1','V2','V3','V4','V5','V6','V7','V01','V02','V04','V05','V06','V07']}
out['validity']['affected_certificate_fields']={'gates.all_valid':16,'reasons':5,'status':0,'wording':0,'all_effect_estimates_and_bounds':0,'status_crosscheck':0,'other_certificate_fields':0}
out['validity']['not_supported_valid_evidence_wording_count']=11
out['validation']['source_hashes']={str(q.relative_to(ROOT)):hashlib.sha256(q.read_bytes()).hexdigest() for q in list((ROOT/'ccc/analysis').glob('*.py'))+[ROOT/'ccc/audit/decision.py',ROOT/'ccc/baselines/__init__.py',ROOT/'paper/build/submission.md']}
out['baseline_summary']={'category':'descriptive','provenance':'development; supplied Gate A v1.2.2 summary only, no fixture rerun','headline_n':280,'CCC':{'TP':4,'FN':76,'FP':0,'TN':200,'abstain':78,'coverage':202/280,'sensitivity':4/80},'B2plus':{'TP':4,'FN':76,'FP':0,'TN':200,'abstain':20,'coverage':260/280},'B2':{'TP':12,'FN':68,'FP':8,'TN':192,'abstain':20,'coverage':260/280,'sensitivity':12/80}}
(OUT/'review.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:out[k] for k in ['primary','power','noncommit_sensitivity','noncommits','secondary','gates','sham_summary_S_minus_F']},indent=2))
print('raw checks',dict(checks),'cross checks',dict(cross),'frozen keys first',next(iter(percp.values())))
