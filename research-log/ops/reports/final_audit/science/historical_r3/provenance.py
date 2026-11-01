from pathlib import Path
import json,gzip,hashlib
from collections import Counter
R=Path('/Users/aarav/Documents/Projects/ApartSprint'); P=R/'docs/enh/r2/run_par';O=Path('/private/tmp/ccc-W1-R3')
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compare(a,b):
 out=dict(total=0,compressed_equal=0,decompressed_equal=0,missing=[],different=[])
 for f in a:
  dest=b/f.name;out['total']+=1
  if not dest.exists():out['missing'].append(f.name);continue
  same=f.read_bytes()==dest.read_bytes();eq=gzip.decompress(f.read_bytes())==gzip.decompress(dest.read_bytes());out['compressed_equal']+=same;out['decompressed_equal']+=eq
  if not eq:out['different'].append(f.name)
 return out
frozen=read(R/'docs/enh/r2/FREEZE.json'); hashes={}
def flatten(d):
 for k,v in d.items():
  if k.startswith('ccc/') and isinstance(v,str):hashes[k]=v
  elif isinstance(v,dict):flatten(v)
flatten(frozen['code_hashes'])
v2=read(P/'GATE_v2.json');old=read(R/'ops/reports/codex_runs/gate1_failed/run_par_prev/GATE.json');serial=R/'docs/enh/r2/run'
d=dict(frozen_hash_disagreements=[p for p,h in hashes.items() if sha(R/p)!=h],protocol_hash_equal=sha(R/frozen['protocol']['path'])==frozen['protocol']['sha256'],serial_eps0=compare(sorted((serial/'units').glob('*-eps-0.json.gz')),P/'units'),archived_gate=dict(status=old['status'],compared=old['compared'],infrastructure_error=old['infrastructure_error'],mismatch_count=len(old['mismatches']),missing_count=sum(x.endswith(': missing') for x in old['mismatches']),first_mismatches=old['mismatches'][:4]),v2_recorded={k:v for k,v in v2.items() if k!='identity'},v2_identity={k:v for k,v in v2['identity'].items() if k!='hashes'},failures=read(P/'failures.json'))
d['gate40_current']={e:compare([P/'units'/f'{s}-eps-{e}.json.gz' for s in old['seeds']],serial/'units') for e in ('0','0.1')}
d['v2_actual']={}
for folder in ('units','partitions'):
 d['v2_actual'][folder+'_A_vs_B']=compare(sorted((P/'gate_v2/A'/folder).glob('*.gz')),P/'gate_v2/B'/folder)
 d['v2_actual'][folder+'_A_vs_serial_eps0']=compare(sorted((P/'gate_v2/A'/folder).glob('*eps-0.json.gz')),serial/folder)
 d['v2_actual'][folder+'_A_vs_final']=compare(sorted((P/'gate_v2/A'/folder).glob('*.gz')),P/folder)
runtimes=Counter();bad=[];checksum_bad=[]
for f in sorted((P/'execution/modal/methods').glob('*.json')):
 receipt=read(f);runtimes[receipt['runtime']['python']]+=1
 if receipt['task']['identity']!=v2['identity']:bad.append(f.name)
 for path,h in receipt['sha256'].items():
  if sha(P/path)!=h:checksum_bad.append(path)
d.update(method_receipt_count=sum(runtimes.values()),method_runtime_counts=dict(runtimes),receipt_identity_disagreements=bad,receipt_checksum_disagreements=checksum_bad)
manifest=read(P/'manifest.json');d['manifest_seed_count']=len(manifest['seeds']);d['schedule_kind_counts']=dict(Counter(k for kinds in manifest['seeds'].values() for k in kinds));d['complete']=read(P/'COMPLETE.json')
(O/'provenance.json').write_text(json.dumps(d,indent=2,sort_keys=True)+'\n');print(json.dumps({k:v for k,v in d.items() if k not in ('complete','v2_recorded')},indent=2))
