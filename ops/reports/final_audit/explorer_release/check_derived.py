"""Offline exhaustive source-to-bundle checks; no ccc imports or model execution."""
import collections
import gzip
import hashlib
import json
from pathlib import Path
import tarfile

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).parent

def read(p):
    return json.loads((ROOT / p).read_text())

def sha(p):
    return hashlib.sha256((ROOT / p).read_bytes()).hexdigest()

def js_value(path, prefix):
    text = (ROOT / path).read_text().split(prefix, 1)[1]
    return json.JSONDecoder().raw_decode(text)[0]

def diffs(a, b, path='$'):
    if type(a) is not type(b):
        return [dict(path=path, before=a, after=b)]
    if isinstance(a, dict):
        result = []
        for k in sorted(a.keys() | b.keys()):
            if k not in a or k not in b:
                result.append(dict(path=path+'.'+k, before=a.get(k), after=b.get(k)))
            else:
                result += diffs(a[k], b[k], path+'.'+k)
        return result
    if isinstance(a, list):
        if a and b and all(isinstance(x,dict) and 'path' in x for x in a+b) and len({x['path'] for x in a})==len(a) and len({x['path'] for x in b})==len(b):
            return diffs({x['path']:x for x in a},{x['path']:x for x in b},path+'[by path]')
        if len(a) != len(b):
            return [dict(path=path, before=a, after=b)]
        return [d for i, (x, y) in enumerate(zip(a, b)) for d in diffs(x, y, path+'['+str(i)+']')]
    return [] if a == b else [dict(path=path, before=a, after=b)]

manifest = read('demo/data/MANIFEST.json')
meta = js_value('demo/explorer/data/index.js', 'window.CCC_DATA.manifest=')
assert meta['generator_commit_HEAD'] == manifest['generator_commit_HEAD']
assert meta['manifest_sha256'] == sha('demo/data/MANIFEST.json')
assert meta['bundle_generator_sha256'] == sha('demo/explorer/bundle_data.py')
for f in manifest['files']:
    assert sha(f['path']) == f['sha256'], f['path']
for f in manifest['source_hashes']:
    if 'archive_member' not in f:
        assert sha(f['path']) == f['sha256'], f['path']
index = read('demo/data/cases.json')
originals = {c['checkpoint_id']: c for c in read('docs/analysis/exp002_heldout_v3/checkpoint_certificates.json')}
statuses = collections.Counter()
for c in index['cases']:
    case = read('demo/data/'+c['file'])
    bundled = js_value('demo/explorer/data/case_'+c['id']+'.js', 'window.CCC_DATA.cases['+json.dumps(c['id'])+']=')
    assert bundled['certificate'] == case['certificate']
    assert bundled['gate_trace'] == case['gate_trace']
    assert c['status'] == case['certificate']['status']
    if c['id'] in originals:
        assert case['certificate'] == originals[c['id']]
        statuses[c['status']] += 1
assert len(index['cases']) == 21 and len(originals) == 16
assert statuses == {'not_supported':11, 'inconclusive':5}
study = read('demo/data/study.json')
assert study['scheduled_counts'] == {'valid':143, 'not_run':56}
twins = read('demo/data/twins.json')
assert twins == js_value('demo/explorer/data/twins.js', 'window.CCC_DATA.twins=')
assert twins['aggregate_criteria'] == {k:v['status'] for k,v in read('docs/enh/r2/run_par/RESULTS.json')['rq'].items()}
records = json.loads(gzip.decompress((ROOT / 'docs/enh/r2/run_par/records.json.gz').read_bytes()))
for pair in twins['pairs']:
    rows = [r for r in records if r['kind']==pair['kind'] and r['epsilon']==0]
    assert pair['seed']==min(r['seed'] for r in rows) and pair['epsilon']==0
    for member in pair['members']:
        for s, info in member['by_set'].items():
            r = next(r for r in rows if r['seed']==pair['seed'] and r['member']==member['member'] and r['set']==s)
            assert info['view_sha256']==r['view_sha256']
            assert info['identifiable']==r['identifiable']
            assert info['M_multiclass_identifiable']==r['M_multiclass_identifiable']
            for key, source in [('ccc','CCC-v1.2.2'), ('ccc_l','CCC-L-v0'), ('baseline',twins['strongest_baseline']['id']), ('bayes','Bayes-given-S')]:
                m=r['methods'][source]
                expected=dict(status=m['status'],rung=m.get('rung'),M_label=m.get('M_label'),**{k:m.get('predictions',{}).get(k) for k in ('E','H','M')})
                assert info['verdicts'][key]==expected

changes = {}
before_hashes = json.loads((OUT/'before-sha256.json').read_text())
with tarfile.open(OUT/'before-derived-v1.tar.gz') as tf:
    old_manifest=json.loads(tf.extractfile('demo/data/MANIFEST.json').read())
    old_index_text=tf.extractfile('demo/explorer/data/index.js').read().decode()
    old_meta=json.JSONDecoder().raw_decode(old_index_text.split('window.CCC_DATA.manifest=',1)[1])[0]
    old_index=json.JSONDecoder().raw_decode(old_index_text.split('window.CCC_DATA.index=',1)[1])[0]
    assert old_index==json.loads(tf.extractfile('demo/data/cases.json').read())
    old_twins=json.JSONDecoder().raw_decode(tf.extractfile('demo/explorer/data/twins.js').read().decode().split('window.CCC_DATA.twins=',1)[1])[0]
    assert old_twins==json.loads(tf.extractfile('demo/data/twins.json').read())
    import importlib.util
    spec=importlib.util.spec_from_file_location('ccc_audit_bundle',ROOT/'demo/explorer/bundle_data.py')
    bundler=importlib.util.module_from_spec(spec);spec.loader.exec_module(bundler)
    for c in old_index['cases']:
        expected=json.loads(tf.extractfile('demo/data/'+c['file']).read())
        full=json.loads(tf.extractfile('demo/data/'+expected['full_text_file']).read())
        expected,mode=bundler.merge_full(expected,full);expected['_text_mode']=mode
        text=tf.extractfile('demo/explorer/data/case_'+c['id']+'.js').read().decode()
        actual=json.JSONDecoder().raw_decode(text.split('window.CCC_DATA.cases['+json.dumps(c['id'])+']=',1)[1])[0]
        assert expected==actual, 'Original scientific bundle mismatch '+c['id']
    old_expected_meta={k:old_manifest[k] for k in old_meta if k in old_manifest}
    old_actual_meta={k:old_meta[k] for k in old_expected_meta}
    original_meta_diff=diffs(old_expected_meta,old_actual_meta)
    assert [d['path'] for d in original_meta_diff]==['$.generator_commit_HEAD']
    for p, old_hash in before_hashes.items():
        if not (ROOT/p).exists() or sha(p)==old_hash:
            continue
        old=tf.extractfile(p).read()
        if p.endswith('.json'):
            changes[p]=diffs(json.loads(old),read(p))
        elif p.startswith('demo/explorer/data/'):
            changes[p]=[dict(change='Derived JS wrapper; source JSON changes recorded separately',before_sha256=old_hash,after_sha256=sha(p))]
        else:
            changes[p]=[dict(change='Source/text correction; inspect Git diff',before_sha256=old_hash,after_sha256=sha(p))]
(OUT/'field-differences-v3.json').write_text(json.dumps(changes,indent=2,ensure_ascii=False)+'\n')
report=dict(status='PASS',cases=21,heldout=16,scripted_development=5,heldout_statuses=dict(statuses),scheduled=study['scheduled_counts'],twins=[dict(kind=p['kind'],seed=p['seed'],epsilon=p['epsilon'],separator=p['first_separating_set']) for p in twins['pairs']],criteria=twins['aggregate_criteria'],manifest_sha256=meta['manifest_sha256'],changed_files=sorted(changes),preserved_original_sha256=hashlib.sha256((OUT/'before-derived-v1.tar.gz').read_bytes()).hexdigest())
report['original_bundle_case_comparisons']=21
report['original_bundle_twins_equal']=True
report['original_metadata_only_difference']=original_meta_diff
(OUT/'derived-validation.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
