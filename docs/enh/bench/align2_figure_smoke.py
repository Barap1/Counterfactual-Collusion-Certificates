"""Exercise the existing twin figure consumer; SVG/JSON only, no browser/PDF."""
import importlib.util
import json
from pathlib import Path
root=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('enh_figures',root/'figures/enh/make_enh_figures.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
# PDF uses Chrome, outside this data-contract check; never launch a browser.
module.to_pdf=lambda *args:False
out=root/'docs/enh/bench/figure_compat'
ctx=module.Ctx(root/'docs/enh/bench/dev_run',out,'DEV')
module.fig_twins(ctx,ctx.get('frontiers.json'),ctx.get('separators.json'),ctx.get('RESULTS.json'))
assert not ctx.missing,ctx.missing
side=json.loads((out/'fig_twins.json').read_text())
assert not side['missing_fields']
assert side['plotted_values']['twin_exhibit_present']
assert 'missing in run outputs' not in (out/'fig_twins.svg').read_text()
assert set(side['plotted_values']['members'])=={'A','B'}
print('PASS: existing fig_twins consumer has all outcomes, statuses and probe fields')
