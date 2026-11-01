"""Full DEV F4/K4/S2/N4 evaluation, with offline audit guards."""
import gzip,json,os,sys,time
from pathlib import Path
from hashlib import sha256
from tests.replay.offline_runner import guard
ROOT=Path.cwd(); OUT=ROOT/(sys.argv[1] if len(sys.argv)>1 else 'docs/gate_a/v1.2')
os.environ['CCC_STARTER_ROOT']=str(ROOT/'starter/collusion_hackathon')
sys.addaudithook(guard)
# The census process writes its complete JSON last. Wait for parseable complete outputs.
for version in ('fx1','fx2'):
    while True:
        try:
            result=json.loads((OUT/f'census_{version}.json').read_text())
            if result['summary']['instances']==800: break
        except (FileNotFoundError,json.JSONDecodeError): pass
        time.sleep(2)
# Byte reproducibility is established before any CCC run. DEV-002 remains exploratory.
diff={}
for version in ('fx1','fx2'):
    new=OUT/f'census_{version}.json'
    old=ROOT/f'ops/reports/AMD-IMP-A-evidence/census_{version}.json'
    diff[version]={'new_sha256':sha256(new.read_bytes()).hexdigest(),'previous_sha256':sha256(old.read_bytes()).hexdigest(),
                   'byte_identical':new.read_bytes()==old.read_bytes(),'json_equal':json.loads(new.read_bytes())==json.loads(old.read_bytes())}
(OUT/'census_reproducibility.json').write_text(json.dumps(diff,indent=2)+'\n')
assert all(r['byte_identical'] for r in diff.values())
from ccc.audit.commitments import information,world_aliases
from ccc.fixtures.jira import generate_jira,exact_oracle
census=json.loads((OUT/'census_fx2.json').read_text())
pre=[]
for row in census['rows']:
    if row['case'] not in ('A1a','A1b'): continue
    w=generate_jira(row['case'],row['seed'],phase='development',stratum=row['stratum'],fixture_version='fx2')
    oracle=exact_oracle(w)
    eligible=oracle['strata']['path_active'] and oracle['effects']['K']['tau_C']>0 and oracle['effects']['K']['tau_W']>=-5
    if eligible:
        info=information(w.signal,w.roles[0],world_aliases(w.tasks))
        pre.append({'case':w.case,'stratum':w.stratum,'seed':w.seed,'info_bearing':info,
                    'M_available':row['windows']['1/4']['status']=='accepted'})
(OUT/'pre_ccc_conditional_prediction.json').write_text(json.dumps({'expected_supported':sum(r['M_available'] and not r['info_bearing'] for r in pre),
                       'cells':pre,'timing':'after exploratory census re-run; before this CCC run; original pre-census commitment failed (DEV-002)'},indent=2)+'\n')
from ccc.audit.gate_a import main
# Each run starts a fresh selection manifest; worker writes remain append-only.
(OUT/'placebo_manifests.jsonl').write_text('')
main(OUT)
raw=OUT/'gate_a_results.json'
with gzip.GzipFile(filename=str(OUT/'gate_a_results.json.gz'),mode='wb',mtime=0) as f: f.write(raw.read_bytes())
raw.unlink()
