"""Prove stale pack/source checks preserve an existing bundle (temporary files only)."""
from pathlib import Path
import importlib.util,json,tempfile
ROOT=Path(__file__).resolve().parents[4]
spec=importlib.util.spec_from_file_location('bundle_audit',ROOT/'demo/explorer/bundle_data.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
results=[]
for field in ('files','source_hashes'):
 with tempfile.TemporaryDirectory(prefix='ccc-bundle-guard-') as d:
  p=Path(d);(p/'data').mkdir();(p/'out').mkdir()
  for name in ('cases.json','study.json'):(p/'data'/name).write_bytes((ROOT/'demo/data'/name).read_bytes())
  m=json.loads((ROOT/'demo/data/MANIFEST.json').read_text());m[field][0]['sha256']='0'*64
  (p/'data/MANIFEST.json').write_text(json.dumps(m));(p/'out/index.js').write_text('previous bundle preserved')
  b.PACK=p/'data';b.OUT=p/'out'
  try:b.main();raise AssertionError('Expected stale provenance rejection')
  except ValueError as error:
   assert (p/'out/index.js').read_text()=='previous bundle preserved'
   results.append(dict(field=field,status='PASS',error=str(error),previous_bundle_preserved=True))
(Path(__file__).parent/'provenance-guard.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
