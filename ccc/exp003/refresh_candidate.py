"""Recompute review candidate bytes only; never create ORCH's final FREEZE.json."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = ROOT / 'docs/enh/exp003/FREEZE_candidate.json'


def sha(name):
    p = ROOT / name
    if p.name in ('.env', 'compute.env') or p.name.endswith('.local.json') or not p.resolve().is_relative_to(ROOT):
        raise ValueError('prohibited inventory path')
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    f = json.loads(CANDIDATE.read_text())
    names = set(f['code_sha256'])
    names.update(str(p.relative_to(ROOT)) for p in (ROOT/'ccc/exp003').glob('*.py'))
    names.update(str(p.relative_to(ROOT)) for p in (ROOT/'tests').glob('test_exp003*.py'))
    f['code_sha256'] = {n: sha(n) for n in sorted(names)}
    evidence = set(f['evidence_sha256'])
    evidence.update(['docs/enh/exp003/FEASIBILITY_TEMPLATE.md', 'docs/enh/exp003/WIRING.md',
                     'ccc/exp003/offline_evidence/W2_FIX2_validation.txt'])
    f['evidence_sha256'] = {n: sha(n) for n in sorted(evidence)}
    f['protocol_sha256'] = sha(f['protocol_artifact'])
    f['status'] = 'candidate-not-approved-not-committed'
    f['worker'] = 'W2-FIX2'
    CANDIDATE.write_text(json.dumps(f, indent=2, sort_keys=True)+'\n')
    saved = json.loads(CANDIDATE.read_text())
    for group in ('code_sha256', 'evidence_sha256'):
        assert all(sha(n) == h for n, h in saved[group].items())
    assert sha(saved['protocol_artifact']) == saved['protocol_sha256']
    print(f"Verified candidate: {len(names)} code and {len(evidence)} evidence hashes; protocol current; final freeze untouched")


if __name__ == '__main__':
    main()
