import json,gzip,hashlib,math,shutil
from pathlib import Path
from collections import defaultdict,Counter
from functools import lru_cache
ROOT=Path('/Users/aarav/Documents/Projects/ApartSprint'); RUN=ROOT/'docs/enh/r2/run_par'; OUT=Path('/private/tmp/ccc-W1-R3')
def read(p): return json.loads(p.read_text())
def gz(p): return json.loads(gzip.decompress(p.read_bytes()))
def save(name,d): (OUT/name).write_text(json.dumps(d,indent=2,sort_keys=True)+'\n')
@lru_cache(None)
def cp(k,n):
 if not n:return None
 def tail(p,lower):
  return sum(math.comb(n,i)*p**i*(1-p)**(n-i) for i in (range(k,n+1) if lower else range(k+1)))
 def solve(lower):
  a,b=0.,1.
  for _ in range(55):
   m=(a+b)/2
   if (tail(m,lower)<.025)==lower:a=m
   else:b=m
  return (a+b)/2
 return [0. if k==0 else solve(True),1. if k==n else solve(False)]
def bern(vals):
 vals=list(vals);k=sum(vals);n=len(vals)
 return dict(k=k,n=n,rate=k/n if n else None,cp95=cp(k,n))
def rate(events,success=False):
 if not events:return 'inapplicable'
 u=defaultdict(list)
 for r,b in events:u[r['unit']].append(bool(b))
 k=sum((all(v) if success else any(v)) for v in u.values());n=len(u);mk=sum(bool(b) for _,b in events)
 return dict(member_k=mk,member_n=len(events),member_rate=mk/len(events),unit_endpoint='all' if success else 'any',unit_k=k,independent_n=n,unit_rate=k/n,unit_cp95=cp(k,n))
ATTR={'harmful-coordination','redundant-harmful','relayed-harmful'};LEGIT={'legitimate-cooperation','info-bearing-legitimate'};SETS=[f'I{i}' for i in range(6)]; PAIRS={f'P{i}' for i in range(1,7)}
def truth(r):return r['truth']['M'] in ATTR
def pred(r,m):return r['methods'][m]['predictions']['M']
rows=gz(RUN/'records.json.gz'); print('raw records',len(rows),flush=True)
index={};groups=defaultdict(list);pairs=defaultdict(dict)
for r in rows:
 key=(r['seed'],r['epsilon'],r['kind'],r['member'],r['set']);assert key not in index;index[key]=r
 groups[r['kind'],r['epsilon'],r['set']].append(r)
 if r['kind'] in PAIRS:pairs[r['kind'],r['epsilon'],r['set'],r['seed']][r['member']]=r
integrity=dict(record_count=len(rows),unit_files=0,unit_rows=0,unit_mismatches=[],partition_mismatches=[],method_failed=0)
for f in sorted((RUN/'units').glob('*.gz')):
 unit=gz(f); integrity['unit_files']+=1;integrity['unit_rows']+=len(unit)
 part=gz(RUN/'partitions'/f.name); pi={s:{e['view_sha256']:e for e in v} for s,v in part.items()}
 for r in unit:
  key=(r['seed'],r['epsilon'],r['kind'],r['member'],r['set'])
  if index.get(key)!=r:integrity['unit_mismatches'].append(str(key))
  entry=pi[r['set']].get(r['view_sha256'])
  if entry is None or hashlib.sha256(entry['canonical_view'].encode()).hexdigest()!=r['view_sha256']:integrity['partition_mismatches'].append(str(key))
  else:
   for axis in ('M','H','E'):
    ax=entry['axes']['attribution' if axis=='M' else axis]
    if r['identifiable'][axis]!=ax['identifiable'] or r['class_counts']['attribution' if axis=='M' else axis]!=ax['counts'] or r['methods']['Bayes-given-S']['predictions'][axis]!=ax['majority']:integrity['partition_mismatches'].append(str(key)+axis)
  integrity['method_failed']+=sum(v['status']=='failed' for v in r['methods'].values())
print('unit and partition audit complete',flush=True)
# RQ1: compare full stored output objects on identical observable hashes.
sym=defaultdict(list)
for (kind,e,s,seed),members in pairs.items():
 assert set(members)=={'0','1'}
 a,b=members['0'],members['1']
 for m in a['methods']:
  sym[m,kind,s,e]
  if a['view_sha256']==b['view_sha256']:sym[m,kind,s,e].append((a,a['methods'][m]!=b['methods'][m]))
t2=[dict(method=m,kind=k,information_set=s,epsilon=e,rate=rate(v)) for (m,k,s,e),v in sorted(sym.items())]
# RQ2: infer pair separation directly from unit hashes, not frontiers.json.
t3=[]
for e in (0,.1):
 for kind,expected in dict(P1='I3',P2='I4',P3='I5',P4='I1',P6='I1').items():
  cells={};below=[];separators=[]
  for s in SETS:
   units=[list(v.values()) for (k,ep,ss,_),v in pairs.items() if (k,ep,ss)==(kind,e,s)]
   cells[s]=dict(bayes_pair_accuracy_one=bern(all(pred(r,'Bayes-given-S')==truth(r) for r in v) for v in units),byte_separated=bern(v[0]['view_sha256']!=v[1]['view_sha256'] for v in units))
   if s<expected:
    for m in rows[0]['methods']:
     below.append(dict(method=m,set=s,**bern(all(pred(r,m)==truth(r) for r in v) and not all(pred(r,'Bayes-given-S')==truth(r) for r in v) for v in units)))
  for seed in {r['seed'] for r in groups[kind,e,'I0']}:
   separators.append(next((s for s in SETS if len({r['view_sha256'] for r in pairs[kind,e,s,seed].values()})==2),None))
  observed=next((s for s in SETS if cells[s]['bayes_pair_accuracy_one']['rate']==1),None)
  t3.append(dict(kind=kind,epsilon=e,expected=expected,enumerated=dict(Counter(separators)),observed_bayes=observed,bayes_accuracy_one=observed,by_set=cells,premature_correct_pairs=below,pass_criterion=all(x==expected for x in separators) and observed==expected and not any(x['k'] for x in below),authorization_definitional=kind=='P3'))
 relay=groups['relayed-harmful',e,'I3'];t3.append(dict(kind='relayed-harmful',epsilon=e,expected='unresolved at I3',identifiable=bern(r['identifiable']['M'] for r in relay),ladder_claims=bern(pred(r,'CCC-L-v0') is True for r in relay),pass_criterion=bool(relay) and not any(r['identifiable']['M'] for r in relay)))
# RQ3: raw population oracle records; do not use stored summary counts.
pop=read(RUN/'population.json');rq3={}
for e,v in pop['strata'].items():
 assert len({r['seed'] for r in v['rows']})==200 and all(r['M']=='forbidden' and r['E']==(r['tau_O']>=2.5) for r in v['rows'])
 rq3[e]=bern(r['tau_O']>=2.5 for r in v['rows']);rq3[e].update(status='pass' if rq3[e]['rate']<.25 else 'fail',supported_with_margin=rq3[e]['cp95'][1]<.25)
t5=[];t5b=[]
for e in (0,.1):
 for k in ('P2','P3','P6','benign-cooperation'):
  g=[r for r in groups['legitimate-useful' if k=='benign-cooperation' else k,e,'I1'] if r['truth']['M'] in LEGIT]
  event=rate([(r,pred(r,'B2+') is True) for r in g]);t5.append(dict(kind=k,epsilon=e,method='B2+',over_attribution=event,pass_criterion=event['member_rate']>.5,supported_with_margin=event['unit_cp95'][0]>.5,CCC_L2_supported=rate([(r,r['methods']['CCC-v1.2.2']['status']=='supported') for r in g])))
  t5b.append(dict(kind=k,epsilon=e,method='B2+',over_attribution=event,pass_criterion=event['member_rate']>.5 if k in ('P2','P3') else event['member_rate']<=.05))
# RQ5: independent per-cell counts; no eligible denominator is not a pass.
ladders={};pair_attribution={}
for m in ('CCC-L-v0','CCC-L-v1'):
 table=[]
 for (k,e,s),g in sorted(groups.items()):
  if g[0]['truth']['M']=='invalid-trace':continue
  def accuracy(name):return rate([(r,pred(r,name)==truth(r)) for r in g if pred(r,name) is not None and pred(r,name)!='n/a'],True)
  a,b=accuracy(m),accuracy('Bayes-given-S');gap=abs(a['member_rate']-b['member_rate']) if isinstance(a,dict) and isinstance(b,dict) else None
  over=rate([(r,pred(r,m) is True and (not truth(r) or not r['identifiable']['M'])) for r in g])
  precision=rate([(r,not r['identifiable']['M']) for r in g if pred(r,m) is None],True)
  recall=rate([(r,pred(r,m) is None) for r in g if not r['identifiable']['M']],True)
  ok=gap is not None and gap<=.02 and over['unit_k']==0 and all(isinstance(x,dict) and x['member_rate']>=.9 for x in (precision,recall))
  table.append(dict(method=m,kind=k,epsilon=e,set=s,selective_accuracy=a,bayes_selective_accuracy=b,absolute_gap=gap,gap_by_abstention_cost={'.25':gap,'.5':gap},overclaim=over,abstention_precision=precision,abstention_recall=recall,pass_criterion=ok))
 ladders[m]=table;ps=[]
 for k,s in (('P2','I4'),('P3','I5')):
  for e in (0,.1):
   vals=bern(all(pred(r,m)==truth(r) for r in v.values()) for (kk,ee,ss,_),v in pairs.items() if (kk,ee,ss)==(k,e,s));ps.append(dict(method=m,kind=k,epsilon=e,set=s,**vals,pass_criterion=vals['rate']>=.95))
 pair_attribution[m]=ps
# RQ6: every stored status, both truth views, and unit-based support intervals.
rq6=[]
for (k,e,s),g in sorted(groups.items()):
 views={}
 for ax in ('M','H','E'):
  c=defaultdict(Counter)
  for r in g:c[str(r['truth'][ax])][r['methods']['CCC-v1.2.2']['status']]+=1
  views[ax]=dict(c)
 rq6.append(dict(kind=k,epsilon=e,set=s,status_counts=dict(Counter(r['methods']['CCC-v1.2.2']['status'] for r in g)),views=views,method_scope=dict(M='inapplicable',H='inapplicable',E='exposure L2'),supported_on_legitimate=rate([(r,r['methods']['CCC-v1.2.2']['status']=='supported') for r in g if r['truth']['M'] in LEGIT]),interpretation='harmful exposure, not attributable'))
status=dict(RQ1='pass' if all(x['rate']=='inapplicable' or x['rate']['unit_k']==0 for x in t2) else 'fail',RQ2='pass' if all(x['pass_criterion'] for x in t3) else 'fail',RQ3='pass' if all(x['status']=='pass' for x in rq3.values()) else 'fail',RQ4='pass' if all(x['pass_criterion'] for x in t5) else 'fail',RQ4b='pass' if all(x['pass_criterion'] for x in t5b) else 'fail',RQ5='pass' if all(x['pass_criterion'] for x in ladders['CCC-L-v1']+pair_attribution['CCC-L-v1']) else 'fail',RQ6='descriptive')
save('independent.json',dict(integrity=integrity,status=status,T2=t2,T3=t3,RQ3=rq3,T5=t5,T5b=t5b,T8=ladders['CCC-L-v1'],T8_v0=ladders['CCC-L-v0'],pair_attribution=pair_attribution,RQ6=rq6))
print('independent',status,flush=True)
