"""Protocol §4 deterministic streams and read-only historical seed census.

No world is constructed here. Archive members are streamed, never extracted.
Only public JSON/JSONL/CSV seed fields are inspected; secrets are never opened.
"""
import csv
import io
import json
import re
import tarfile
from hashlib import sha256
from pathlib import Path

PAIRS = tuple(f'P{i}' for i in range(1, 7))
CLASSES = ('relayed-harmful', 'invalid-corrupted-trace', 'common-cause-single',
           'redundant-single', 'harm-without-dependence', 'legitimate-useful',
           'suspicious-language-no-harm', 'inert', 'info-bearing')
COUNTS = {**dict.fromkeys(PAIRS, 200), 'jira_iid': 200, **dict.fromkeys(CLASSES, 100)}
PARAMETERS = dict(m_O=2.5, eps=[0, 0.1], R_eps_0_1=8, abstention_costs=[0.25, 0.5],
                  interval='Clopper-Pearson 95%', bootstrap_B=10000, bootstrap_seed=20261026)


def list_hash(values):
    return sha256(json.dumps(sorted(values), separators=(',', ':')).encode()).hexdigest()


def _safe(path):
    name = Path(path).name
    return not (name.startswith('._') or name in ('.env', 'compute.env') or name.endswith('.local.json'))


def _seed_values(value, seed_context=False):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _seed_values(item, seed_context or 'seed' in key.lower())
    elif isinstance(value, list):
        for item in value:
            yield from _seed_values(item, seed_context)
    elif type(value) is int and seed_context:
        yield value
    elif isinstance(value, str):
        if seed_context and re.fullmatch(r'\d+', value):
            yield int(value)
        elif value.startswith(('{', '[')):
            try: yield from _seed_values(json.loads(value), seed_context)
            except json.JSONDecodeError: pass


def exclusions(root):
    """Conservative recursive seed-key census, with per-source hashes/evidence.

    All seed-named fields are included (world, sampling, master, bootstrap,
    ordering, placebo); numeric world_id fields are included conservatively.
    JSON/JSONL in archives includes manifests AND realized sampling requests.
    """
    root = Path(root)
    sources = []
    old = set()
    def consume(name, data, suffix):
        found = set()
        text = data.decode('utf-8')
        if suffix == '.csv':
            objects = csv.DictReader(io.StringIO(text))
        elif suffix == '.jsonl':
            objects = (json.loads(line) for line in text.splitlines() if line.strip())
        else:
            objects = [json.loads(text)]
        for obj in objects:
            found.update(_seed_values(obj))
        # Analysis tables may retain a world id rather than its seed field.
        found.update(int(x) for x in re.findall(r'"world_id"\s*:\s*"?(\d+)', text))
        old.update(found)
        sources.append(dict(path=name, sha256=sha256(data).hexdigest(), seeds=sorted(found)))
    directories = sorted(set(root.glob('docs/analysis/exp002_heldout*')) |
                         set(root.glob('docs/analysis/exp001_dev*')) | {root/'results/baselines'})
    for directory in directories:
        if not directory.is_dir(): continue
        for path in sorted(directory.rglob('*')):
            if path.is_file() and _safe(path) and path.suffix in ('.json', '.jsonl', '.csv'):
                consume(path.relative_to(root).as_posix(), path.read_bytes(), path.suffix)
    for archive in sorted((root/'docs/runner/archives').glob('*.tar.gz')):
        with tarfile.open(archive, 'r|gz') as stream:
            for member in stream:
                path = Path(member.name)
                if member.isfile() and _safe(path) and path.suffix in ('.json', '.jsonl', '.csv'):
                    consume(archive.relative_to(root).as_posix()+'!'+member.name,
                            stream.extractfile(member).read(), path.suffix)
    sets = dict(gate_a_12000_12019=list(range(12000, 12020)), dev_13000_13049=list(range(13000, 13050)),
                exp002_exp001_pilot_seeds=sorted(old), integers_0_99999=list(range(100000)))
    return sets, sources


def draw(protocol_sha256, excluded):
    if not re.fullmatch('[0-9a-f]{64}', protocol_sha256):
        raise ValueError('protocol-sha256 must be 64 lowercase hexadecimal characters')
    forbidden = set().union(*map(set, excluded.values()))
    used = set(); schedule = {}; skips = []
    # Label order is explicitly frozen; collisions cannot make traversal implicit.
    for label, count in COUNTS.items():
        values = []
        for i in range(count):
            j = 0
            while True:
                payload = f'{protocol_sha256}|{label}|{i}' + (f'|{j}' if j else '')
                value = int.from_bytes(sha256(payload.encode()).digest()[:4], 'big') >> 1
                if value not in forbidden and value not in used: break
                skips.append(dict(stratum=label, index=i, salt=j, seed=value,
                                  reason='excluded' if value in forbidden else 'already-used'))
                j += 1
            used.add(value); values.append(value)
        schedule[label] = values
    return dict(schema='r2-seeds-1', protocol_sha256=protocol_sha256, label_order=list(COUNTS),
                strata=schedule, skips_recorded=skips,
                seed_list_sha256=list_hash(used), self_intersection=len(sum(schedule.values(), []))-len(used),
                excluded_sets={k:dict(sha256=list_hash(v), count=len(v), intersection=len(used & set(v)))
                               for k, v in excluded.items()})


def check(path, root):
    actual = json.loads(Path(path).read_text())
    excluded, sources = exclusions(root)
    expected = draw(actual['protocol_sha256'], excluded)
    expected['enumeration_sources_sha256'] = sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()
    if actual != expected:
        raise ValueError('seed-check failure: schedule, skip ledger, exclusions or hashes differ')
    if expected['self_intersection'] or any(v['intersection'] for v in expected['excluded_sets'].values()):
        raise ValueError('seed-check failure: nonzero intersection')
    return actual


def materialize(protocol_sha256, path, root):
    root = Path(root)
    freeze_path = root/'docs/enh/r2/FREEZE.json'
    if not freeze_path.is_file(): raise ValueError('seed materialisation refused: FREEZE.json is absent')
    freeze = json.loads(freeze_path.read_text())
    if freeze.get('status') != 'FROZEN' or freeze['protocol']['sha256'] != protocol_sha256:
        raise ValueError('seed materialisation refused: protocol is not frozen')
    if sha256((root/freeze['protocol']['path']).read_bytes()).hexdigest() != protocol_sha256:
        raise ValueError('seed materialisation refused: protocol hash mismatch')
    excluded, sources = exclusions(root)
    result = draw(protocol_sha256, excluded)
    result['enumeration_sources_sha256'] = sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as output:
        output.write(json.dumps(result, indent=2, sort_keys=True)+'\n')
    return result
