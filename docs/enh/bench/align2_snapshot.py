"""Preserve pre-A4 DEV artifacts before the authorized development rerun."""
from pathlib import Path
import gzip
base=Path('docs/enh/bench'); target=base/'bench_align_snapshot'
target.mkdir(exist_ok=True)
for name in ('RESULTS_dev.json','records.json.gz','scores.json','symmetry.json','separators.json','frontiers.json','population.json','manifest.json','COMPLETE.json','strongest_baseline.json'):
    source=base/'dev_run'/name
    dest=target/(name if name.endswith('.gz') else name+'.gz')
    if not dest.exists():
        dest.write_bytes(source.read_bytes() if name.endswith('.gz') else gzip.compress(source.read_bytes(),mtime=0))
