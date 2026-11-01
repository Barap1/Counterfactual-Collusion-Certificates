#!/usr/bin/env python3
"""Execute historical exhaustive field verifier with its sole write redirected."""
from pathlib import Path
from unittest.mock import patch
import hashlib,json,runpy
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
source=ROOT/'docs/analysis/exp002_heldout_v3/verify_correction_v3.py'
target=ROOT/'docs/analysis/exp002_heldout_v3/output_diff_v3.json'
original_write=Path.write_text
before=hashlib.sha256(target.read_bytes()).hexdigest()
def redirected(path,text,*args,**kwargs):
    assert path.resolve()==target,('unexpected write',str(path))
    return original_write(OUT/'v2_v3_diff_recomputed.json',text,*args,**kwargs)
with patch.object(Path,'write_text',redirected):
    runpy.run_path(str(source),run_name='__main__')
assert hashlib.sha256(target.read_bytes()).hexdigest()==before
x=json.loads((OUT/'v2_v3_diff_recomputed.json').read_text())
summary={'verification':'EXECUTED; existing verifier, only its sole write redirected','files':len(x['files']),'changed_fields_or_records':len(x['changes']),'numeric_tokens_compared':x['numeric_tokens_compared'],'numeric_tokens_byte_identical':x['numeric_tokens_byte_identical'],'status_changes':x['status_changes'],'frozen_diff_sha256_before':before,'frozen_diff_sha256_after':hashlib.sha256(target.read_bytes()).hexdigest(),'recomputed_diff_equals_historical':(OUT/'v2_v3_diff_recomputed.json').read_bytes()==target.read_bytes()}
old=json.loads((ROOT/'docs/analysis/exp002_heldout_v2/checkpoint_certificates.json').read_text());new=json.loads((ROOT/'docs/analysis/exp002_heldout_v3/checkpoint_certificates.json').read_text())
summary['all_valid_false_to_true']=sum(not a['gates']['all_valid'] and b['gates']['all_valid'] for a,b in zip(old,new))
summary['inconclusive_reasons_removed']=sum(a['reasons']!=b['reasons'] for a,b in zip(old,new))
assert summary['all_valid_false_to_true']==16 and summary['inconclusive_reasons_removed']==5
(OUT/'v2_v3_verification.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
