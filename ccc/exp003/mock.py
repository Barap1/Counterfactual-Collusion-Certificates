"""Full offline fake-model dry-run using the public DEV seed 2, never held-out."""
import argparse
import json
from pathlib import Path
from ccc.runner.manifest import file_hash
from .manifest import SCHEMA
from .collector import run


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--config', type=Path, default=Path('docs/runner/dev_manifest.json'))
    args = parser.parse_args()
    m = json.loads(args.config.read_text())
    m.update(schema_version=SCHEMA, experiment_id='EXP-003-mock', backend='local',
             protocol_artifact='docs/enh/exp003/PROTOCOL.md',
             protocol_sha256=file_hash('docs/enh/exp003/PROTOCOL.md'), max_requests=2000,
             arms=['F', 'K', 'S', 'N', 'PF', 'PK'],
             continuations_per_arm={'F': 4, 'K': 4, 'S': 2, 'N': 4, 'PF': 4, 'PK': 4})
    m['policy']['live_inference_enabled'] = False
    m.pop('hard_stop_utc', None)
    m['worlds'] = [dict(id=f'mock_dev02_{r}', pair_id='mock_dev02', seed=2,
                        regime=r, split='development') for r in ('B1', 'B2')]
    run(m, args.output, dry_run=True)
    print(str(args.output / 'rows.json'))


if __name__ == '__main__':
    main()
