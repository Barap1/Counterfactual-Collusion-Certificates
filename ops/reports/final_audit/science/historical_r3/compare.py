import json,math
from pathlib import Path
P=Path('/private/tmp/ccc-W1-R3');R=Path('/Users/aarav/Documents/Projects/ApartSprint/docs/enh/r2/run_par');a=json.loads((P/'independent.json').read_text());b=json.loads((R/'RESULTS.json').read_text());diff=[]
def check(x,y,path):
 if isinstance(x,(int,float)) and not isinstance(x,bool) and isinstance(y,(int,float)) and not isinstance(y,bool):
  if not math.isclose(x,y,abs_tol=1e-12,rel_tol=1e-12):diff.append([path,x,y])
 elif type(x)!=type(y):diff.append([path,x,y])
 elif isinstance(x,dict):
  for k in x:
   if k not in y:diff.append([path+'/'+k,'missing in report'])
   else:check(x[k],y[k],path+'/'+k)
 elif isinstance(x,list):
  if len(x)!=len(y):diff.append([path,'length',len(x),len(y)])
  else:
   for i,(u,v) in enumerate(zip(x,y)):check(u,v,path+'/'+str(i))
 elif x!=y:diff.append([path,x,y])
for k,v in a['status'].items():check(v,b['rq'][k]['status'],k)
check(a['T2'],b['tables']['T2']['violations'],'T2')
for t in a['T3']:t.get('premature_correct_pairs',[]).sort(key=lambda x:(x['method'],x['set']))
for t in b['tables']['T3']:t.get('premature_correct_pairs',[]).sort(key=lambda x:(x['method'],x['set']))
for key in ('T3','T5','T5b','T8','T8_v0','RQ6'):
 if key.startswith('T8'):
  for row in a[key]:row['gap_by_abstention_cost']={'0.25':row['absolute_gap'],'0.5':row['absolute_gap']}
 check(a[key],b['tables'][key],key)
check(a['RQ3'],b['rq']['RQ3']['by_epsilon'],'RQ3')
check(a['pair_attribution']['CCC-L-v1'],b['rq']['RQ5']['pair_attribution'],'pairs-v1');check(a['pair_attribution']['CCC-L-v0'],b['rq']['RQ5']['v0_comparison']['pair_attribution'],'pairs-v0')
(P/'comparison.json').write_text(json.dumps(dict(tolerance=1e-12,differences=diff),indent=2)+'\n');print('differences',len(diff),diff[:5]);print('integrity',a['integrity']);print('T2 eligible cells',sum(isinstance(x['rate'],dict) for x in a['T2']),'n',sorted({x['rate']['independent_n'] for x in a['T2'] if isinstance(x['rate'],dict)}));print('RQ3',a['RQ3'])
for t in a['T5']:print('RQ4',t['kind'],t['epsilon'],t['over_attribution'])
for key in ('T8','T8_v0'):
 t=a[key];print(key,'passing cells',sum(x['pass_criterion'] for x in t),'of',len(t),'overclaim unit events',sum(x['overclaim']['unit_k'] for x in t));print('undefined gaps',sum(x['absolute_gap'] is None for x in t),'bad gap',sum(x['absolute_gap'] is not None and x['absolute_gap']>.02 for x in t),'low prec',sum(isinstance(x['abstention_precision'],dict) and x['abstention_precision']['member_rate']<.9 for x in t),'low recall',sum(isinstance(x['abstention_recall'],dict) and x['abstention_recall']['member_rate']<.9 for x in t));print('pairs',a['pair_attribution']['CCC-L-v1' if key=='T8' else 'CCC-L-v0'])
print('RQ6 supported legitimate I2',[(x['kind'],x['epsilon'],x['supported_on_legitimate']) for x in a['RQ6'] if x['set']=='I2' and isinstance(x['supported_on_legitimate'],dict)])
