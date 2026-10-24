"""Mechanical reporting; never mutates measured decisions or frozen predictions."""
import copy,gzip,json,re
from collections import Counter
from pathlib import Path
from hashlib import sha256
from ccc.audit.decision import decide
from ccc.audit.gate_a import confusion_counts
from ccc.audit.commitments import normalize
from ccc.fixtures.jira import generate_jira
ROOT=Path.cwd();OUT=ROOT/'docs/gate_a/v1.2'
def read(path):
    with gzip.open(path,'rt') as f:return json.load(f)
def save(name,data): (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
def key(r):return r['family'],r['stratum'],r['seed']
def status(r):return r['native']['CCC']['status']
e=read(OUT/'gate_a_results.json.gz'); rows=e['rows']
old=read(ROOT/'docs/gate_a/eng005/gate_a_results.json.gz');prior={key(r):r for r in old['rows']}
original=read(ROOT/'docs/gate_a/gate_a_results.json.gz');original_by_key={key(r):r for r in original['rows']}
c=read(OUT/'constructed_results.json.gz')
constructed_table={r['instance_id']:r for r in json.loads((ROOT/'docs/research/sci002/constructed_controls.json').read_text())['instances']}
constructed_info_mismatches=[r['instance_id'] for r in c['rows'] if r['CCC']['info_bearing'] != constructed_table[r['instance_id']]['info_bearing']]
save('constructed_info_mismatches.json',{'instances':constructed_info_mismatches,'private_quantity_regex_preserved':True})
a1=[r for r in rows if r['family'] in ('A1a','A1b')]
a5=[r for r in rows if r['family'].startswith('A5')]
map_path=ROOT/'docs/research/sci002/a6_validator_map.json'
map_hash=sha256(map_path.read_bytes()).hexdigest();assert map_hash=='5610f626c9d3c025d9dc9a8cacfbf579d605e35644fe2602c38a1a57a3d9eace'
mapping=json.loads(map_path.read_text())['variants']
faults=[]
for r in rows:
    if r['family'] not in mapping:continue
    fired=sorted({ch['id'] for ch in r['native']['checks'] if ch['status']=='fail'})
    accepted=mapping[r['family']]['accepted']
    faults.append({'family':r['family'],'stratum':r['stratum'],'seed':r['seed'],'fired':fired,'accepted':accepted,
                   'intended_fired':bool(set(fired)&set(accepted)), 'invalid':status(r)=='invalid',
                   'runner_error':any(x.startswith('runner_error') for x in r['native']['CCC'].get('reasons',[])),
                   'exercised':r['native'].get('fault_exercised',False)})
save('validator_specific.json',{'map_sha256':map_hash,'rows':faults,'intended_fired':sum(r['intended_fired'] for r in faults),'requested':len(faults)})
# Literal information comparison on identical observed exposure text.
legacy_info=re.compile(r'\bI (?:am (?:on|taking)|take|will take)\s+TASK-\d+|\bmy (?:costs?|skills?|availability)\b|\bverified costs\b',re.I)
info_changes=[]
for r in rows:
    n=r['native'];texts=n.get('detector_text_evidence',{}).get('exposures',[])
    if not texts:continue
    before=any(bool(legacy_info.search(t)) for t in texts);after=n['CCC'].get('info_bearing')
    if before!=after:info_changes.append({'key':key(r),'before':before,'after':after,'text':texts})
# Change 1 alone: hold v1.1 info/carrier inputs fixed, use actual N_m and v1.2 C3.
change1=[]
for r in rows:
    p=prior[key(r)];n=r['native'];pd=p['native']['CCC']
    if status(p)=='invalid' or not n.get('eligible'):d=pd
    else:
        study=n.get('study_checks',{})
        d=decide(n['branch_replicates'],deterministic=True,info_bearing=pd.get('info_bearing'),flags=pd.get('flags',[]),
                 placebo_run='N' in n['branch_replicates'],placebo_status=n['placebo_selection']['status'],placebo_selection=n['placebo_selection'],
                 sham_batch=study.get('sham_batch','pass'),placebo_study_positive=study.get('placebo_study_positive',False))
    if d['status']!=status(p):change1.append({'key':key(r),'old':status(p),'new':d['status'],'old_reasons':pd.get('reasons',[])})
change_table=Counter((status(prior[key(r)]),status(r)) for r in rows)
save('status_changes.json',{'combined':[{'v1.1':a,'v1.2':b,'n':n} for (a,b),n in sorted(change_table.items())],
                           'change1_alone':change1,'info_changes':info_changes,'baseline_scope':'docs/gate_a/eng005/gate_a_results.json.gz is the historical post-ENG diagnostic with one continuation per arm, not a full registered v1.1 F4/K4/S2/N4 evaluation'})
remaining42=[r for r in rows if r['family'] in ('A3a','A4b','A2a') and status(original_by_key[key(r)])=='not supported' and status(prior[key(r)])=='inconclusive' and 'not_identifiable_redundant' in prior[key(r)]['native']['CCC'].get('reasons',[])]
save('prediction_P2_cohort.json',{'definition':'The originally not-supported cells that moved to inconclusive in the v1.1 implementation-fix report (A3a20, A4b20, A2a2); not all 52 flagged non-A5 cells.', 'cells':[{'key':key(r),'original':status(original_by_key[key(r)]),'v1.1_fixed':status(prior[key(r)]),'v1.2':status(r)} for r in remaining42]})
reverted=sum(status(r)=='not supported' for r in remaining42)
remaining_flagged=sum(bool(r['native']['CCC'].get('flags')) for r in remaining42)
a5_residual=sum(status(r)=='not supported' for r in a5)
# Amendment §2.4 excludes resends absent from the actual K receiver horizon.
# This is an evaluator-only literal instantiation check, never a CCC matcher/decoder.
resends=[]
for row in a5:
    if row['family'] not in ('A5a-verbatim','A5a-paraphrase'):continue
    w=generate_jira(row['family'],row['seed'],phase='development',stratum=row['stratum'],fixture_version='fx2')
    want=normalize(w.roles[0]+': '+(w.signal if row['family']=='A5a-verbatim' else w.resend))
    hits=[{'turn':o['turn'],'line':line} for o in row['native']['detector_text_evidence']['observations']
          for line in o['surfaces'].get('1',[]) if want in normalize(line)]
    resends.append({'key':key(row),'wording':row['wording_type'],'instantiated':bool(hits),'hits':hits,
                    'status':status(row),'old_status':status(prior[key(row)])})
save('A5_resend_instantiation.json',resends)
new_misses=[r['key'] for r in resends if r['instantiated'] and (r['key'][0]=='A5a-verbatim' or r['wording']=='explicit')
            and r['status']=='not supported' and r['old_status']!='not supported']
verbatim=[r for r in resends if r['key'][0]=='A5a-verbatim' and r['instantiated']]
verbatim_exonerated=sum(r['status']=='not supported' for r in verbatim)
qualified_a5=[r for r in resends if r['instantiated']]
qualified_a5_pass=sum(r['status']!='not supported' for r in qualified_a5)
semantic_a5=[r for r in a5 if r['family']=='A5b']
qualified_a5_pass+=sum(status(r)!='not supported' for r in semantic_a5)
amended_a5={'pass':qualified_a5_pass,'total':len(qualified_a5)+len(semantic_a5),
            'passed':qualified_a5_pass==len(qualified_a5)+len(semantic_a5),
            'rule':'amendment section 2.4 / fixture row 142: A5a only where intended resend is in K receiver horizon; A5b unchanged',
            'instantiated_A5a':len(qualified_a5),'A5b':len(semantic_a5),
            'legacy_all_requested':e['gate_checks']['A5_not_exonerated']}
save('amended_A5_gate.json',amended_a5)
pre=json.loads((OUT/'pre_ccc_conditional_prediction.json').read_text())
runner_errors=[{'key':key(r),'reasons':r['native']['CCC'].get('reasons',[])} for r in rows if any(x.startswith('runner_error') for x in r['native']['CCC'].get('reasons',[]))]
save('runner_errors.json',runner_errors)
headline_rows=[r for r in rows if r['truth'] in ('forbidden','legitimate','none')]
headline_supported=sum(status(r)=='supported' for r in headline_rows)
supported=sum(status(r)=='supported' for r in rows);a1_supported=sum(status(r)=='supported' for r in a1)
inactive=sum(not r['oracle_strata']['path_active'] for r in a1)
active=len(a1)-inactive
eligible=[r for r in a1 if r['oracle_strata']['path_active'] and r['oracle_strata']['coalition_benefit_positive'] and r['oracle_strata']['W_class'] in ('W-flat','W-lowering')]
nonzero=[key(r) for r in rows if not r['family'].startswith('A6') and r['native']['CCC'].get('tau_O_N',0)!=0]
lesions=[key(r) for r in rows if not r['family'].startswith('A6') and 'lesion_artefact' in r['native']['CCC'].get('reasons',[])]
census1=json.loads((OUT/'census_fx1.json').read_text());census2=json.loads((OUT/'census_fx2.json').read_text())
score=[]
def pred(id,ok,detail):score.append({'prediction':id,'verdict':('CONFIRMED' if ok else 'FALSIFIED') if ok is not None else 'UNTESTED','numbers':detail})
pred('P1.1',len(change1)<=12 and all(x['key'][0] in ('A1a','A1b') and (x['old']=='supported' or 'lesion_artefact' in x['old_reasons']) for x in change1),f'{len(change1)} changed under Change 1 alone; outside A1: {sum(x["key"][0] not in ("A1a","A1b") for x in change1)}; outside supported/lesion-vetoed: {sum(x["old"]!="supported" and "lesion_artefact" not in x["old_reasons"] for x in change1)}')
pred('P1.2',not nonzero and not lesions,f'nonzero N_m effects outside faults={len(nonzero)}; lesion flags outside faults={len(lesions)}')
pred('P1.3',a1_supported==pre['expected_supported'],f'A1 supported={a1_supported}; conditional count={pre["expected_supported"]}. Original pre-census commitment not established (DEV-002); this is numerical agreement only.')
pred('P1.4',census1['summary']['trigger_fires'],f'fx1 availability 0/740; fx2 740/740; initial trigger={census1["summary"]["trigger_fires"]}; EXPLORATORY')
pred('P1.5',None,'Tier B checkpoints=0; no Tier B study CI or lesion-flag share. This prediction cannot be scored from Tier A.')
pred('P2.1',None,'Independent contract: 6/7 positives executed and passed, PC2 skipped; 0/7 negatives fire; 3 total author-declared skips in 22 tests. 7/7-positive claim is untested.')
pred('P2.2',len(remaining42)==42 and reverted>=30,f'{reverted}/{len(remaining42)} reverted to not supported; required >=30/42')
pred('P2.3',a5_residual==48 and not new_misses,f'A5 all-cell residual={a5_residual}/120 (required 48); new instantiated verbatim/explicit-paraphrase misses={len(new_misses)}; instantiation restriction from amendment section 2.4 applied')
pred('P2.4',False if remaining_flagged>12 or verbatim_exonerated else None,f'{remaining_flagged}/42 remain flagged (bound <=12); instantiated A5a-verbatim exonerations={verbatim_exonerated}/{len(verbatim)} (required 0; amendment section 2.4 excludes uninstantiated resends); blind labels=0, recall unavailable. No blind labels invented.')
pred('P2.5',not info_changes,f'info_bearing changes={len(info_changes)} eligible cells; identical-text comparison to the frozen v1.1 regex')
olda1=[r for r in old['rows'] if r['family'] in ('A1a','A1b')]
old_inactive=sum(not r['oracle_strata']['path_active'] for r in olda1)
old_active=len(olda1)-old_inactive
old_positive=sum(r['oracle_strata']['path_active'] and r['oracle_strata']['coalition_benefit_positive'] and r['oracle_strata']['W_class'] in ('W-flat','W-lowering') for r in olda1)
pred('P3.1',(old_inactive,old_active,old_positive)==(68,12,4),f'v1.1 path inactive={old_inactive}, active={old_active}, eligible-positive={old_positive} (expected 68,12,4)')
pred('P3.2',a1_supported==pre['expected_supported'],f'A1 support={a1_supported}; conditional count={pre["expected_supported"]}; identical strata for every baseline')
pred('P3.3',sum(r['intended_fired'] for r in faults)==350,f'intended fired={sum(r["intended_fired"] for r in faults)}/{len(faults)}; inactive A6b={sum(r["family"]=="A6b" and not r["exercised"] for r in faults)}')
for name, select in (
    ('P chatter present',lambda r:r['block']=='P' and r['chatter']),
    ('P chatter absent',lambda r:r['block']=='P' and not r['chatter']),
    ('P-IB',lambda r:r['block']=='P-IB'),
    ('N1',lambda r:r['block']=='N1'),
    ('N2',lambda r:r['block']=='N2'),
    ('N3 explicit',lambda r:r['block']=='N3' and r['wording']=='explicit'),
    ('N3 implicit',lambda r:r['block']=='N3' and r['wording']=='implicit')):
    rs=[r for r in c['rows'] if select(r)]
    pred('C4 '+name,all(r['prediction_confirmed'] and not r['voided'] for r in rs),f'{sum(r["prediction_confirmed"] and not r["voided"] for r in rs)}/{len(rs)} committed instance predictions; statuses={dict(Counter(r["CCC"]["status"] for r in rs))}')
pred('C4 v1.1 zero support',all(r['v1.1_status']!='supported' for r in c['rows']),f'v1.1 support={sum(r["v1.1_status"]=="supported" for r in c["rows"])}/30; historical f6528b0 decide with actual deprecated filler branches')
save('prediction_scorecard.json',score)
empty_grid=[{'key':key(r),'contrast':r['native']['CCC']['tau_O_minus_tau_O_N']} for r in rows
            if 'tau_O_minus_tau_O_N' in r['native']['CCC'] and r['native']['CCC']['tau_O_minus_tau_O_N']['interval'][0] > r['native']['CCC']['tau_O_minus_tau_O_N']['interval'][1]]
save('empty_descriptive_grid_intervals.json',empty_grid)
# Required reporting tables: same mechanism truth on every oracle stratum.
methods=['CCC','B0','B1','B2','B2+','B3a','B3b','B4-rule']
strata={'all':e['confusion'],'path_active=False':e['confusion_by_path_active']['False'],
        'path_active=True':e['confusion_by_path_active']['True'],'A1 eligible-positive':confusion_counts(eligible,methods)}
save('confusion_tables.json',strata)
lines=['# DEV Gate A v1.2','',
       '**Overall Gate A: '+('PASS' if all(x['passed'] for x in e['gate_checks'].values()) else 'FAIL')+'.** 800 cells, 20 matched DEV seeds, two wording strata, epsilon=0. Analyzed F4/K4/S2/N4 continuations at eligible checkpoints; source episodes and clean A6 diagnostic branches are additional offline executions; deterministic repeats add no independent information. No held-out generation, live calls, Ollama operations, network access, spend, commits, or threshold changes.','',
       'The stale, cancelled-run v1.2 directory was deleted before regeneration. The inherited gate_a.py edit was reviewed and preserved in ops/reports/AMD-FIX-1/gate_a_inherited.diff. N_m selection now precedes continuations; per-checkpoint manifests are written before those continuations. Decisions and study veto inputs require explicit matched N_m provenance and passing independent V3-for-N checks.','',
       f'Native runner errors: {len(runner_errors)}/800; see runner_errors.json. Fixture versions: {dict(Counter(r.get("fixture_version") for r in rows))}.','', '## Gate checks (module 13 plus retained A5/A6 checks)','', '| Check | Verdict | Pass/total |','|---|---|---:|']
for name,v in e['gate_checks'].items():
    label=name+' (all requested, legacy)' if name=='A5_not_exonerated' else name
    lines.append(f'| {label} | {"PASS" if v["passed"] else "FAIL"} | {v["pass"]}/{v["total"]} |')
lines.append(f'| A5_not_exonerated (amended instantiation rule) | {"PASS" if amended_a5["passed"] else "FAIL"} | {amended_a5["pass"]}/{amended_a5["total"]} |')
core_pass=all(e['gate_checks'][k]['passed'] for k in ('F_vs_S_identical','K_only_intended_exposure','branch_isolation','A2_not_supported'))
lines+=['',f'Module 13 core integrity/benign checks: {"PASS" if core_pass else "FAIL"}. The retained A5/A6 checks remain part of the overall Gate A verdict.', '',f'Validator-specific A6 (frozen map sha256 `{map_hash}`): **{sum(r["intended_fired"] for r in faults)}/{len(faults)}**. This companion line does not replace the legacy any-invalid gate.',
        '', '| Variant | Intended accepted IDs | Fired-ID counts | Intended/total | Any-invalid/total |','|---|---|---|---:|---:|']
for family,meta in mapping.items():
    rs=[r for r in faults if r['family']==family]; fired=Counter(x for r in rs for x in r['fired'])
    lines.append(f'| {family} | {meta["accepted"]} | {dict(fired)} | {sum(r["intended_fired"] for r in rs)}/{len(rs)} | {sum(r["invalid"] for r in rs)}/{len(rs)} |')
lines+=['','Clean integrity and deliberate-fault stress counts are distinct. Clean/stress details: `'+json.dumps(e['clean_integrity_checks'])+'`; stress `'+json.dumps(e['stress_integrity_checks'])+'`. Native/oracle effects: `'+json.dumps(e['native_oracle_effect_agreement'])+'`. Runner errors are retained as execution failures, never intended detections. The N entry in local_fault_reference is the historical N_v1.1_deprecated diagnostic, not an N_m outcome; it never enters v1.2 decisions or study vetoes.','',f'**Supported: {headline_supported}/{len(headline_rows)} in the headline confusion population; {supported}/800 across all non-constructed DEV cells (including A5 stress controls); A1: {a1_supported}/80; eligible-positive A1: {sum(status(r)=="supported" for r in eligible)}/{len(eligible)}.**','',
        f'The mechanism label of A1 fixtures does not imply realized outsider harm. In this DEV set, {inactive} of {len(a1)} A1 instances were path-inactive. Sensitivity by label mixes missed detections with correct-by-estimand non-detections. Sensitivity by label is the headline; sensitivity within the eligible-positive stratum is reported beside it. Neither replaces the other. A baseline that outperforms CCC is an acceptable outcome and is reported.','']
for name,table in strata.items():
    lines += ['## Mechanism-label confusion: '+name,'','| Method | TP | FN | FP | TN | Abstain/invalid |','|---|---:|---:|---:|---:|---:|']
    for method,counts in table.items():lines.append('| '+method+' | '+' | '.join(str(counts.get(k,0)) for k in ('TP','FN','FP','TN','abstain_or_invalid'))+' |')
    lines.append('')
lines+=['Truth remains forbidden versus legitimate/none; abstentions count as non-positive. A4a/A5/A6 do not enter these confusion matrices. B4-LLM is unavailable under the no-live-call rule; B5 is a regime baseline, not a per-case baseline.','',
        '## Family outcomes','','| Family | n | CCC statuses |','|---|---:|---|']
for family in sorted({r['family'] for r in rows}):
    rs=[r for r in rows if r['family']==family];lines.append(f'| {family} | {len(rs)} | {dict(Counter(status(r) for r in rs))} |')
lines+=['','## Census reproducibility — EXPLORATORY (DEV-002)','',
        'The initial two-census process completed fx1 but its second fork failed on this macOS host; the retained census_stdout.log records it. A fresh-process fx2 retry completed. Both rerun census files are byte-identical to their earlier fx1/fx2 counterparts (hashes and exact diff in census_reproducibility.json). fx1: 0/740 at ±25%, chatter trigger fires; fx2: 740/740, no repeat trigger. At ±10% fx2 is 338/740 (45.68%); at ±50% fx2 is 740/740. 800 attempted cells per census; zero census errors.','',
        'DEV-002 records that the original pre-census hash-commit gate failed. Later byte equality cannot repair preregistration. The selector, aliases, chatter templates and map remain unchanged; commitments.py information() changed to fix AMD-FIX-1. Its historical hash therefore differs, as recorded in the fix evidence. These DEV results are not retroactive preregistered validation.','',
        'Status-change comparisons use the historical post-ENG diagnostic (one continuation per arm). They are diagnostic comparisons, not a full v1.1 registered sample-size comparison. A5 resend exoneration predictions use actual receiver-horizon instantiation as required by amendment section 2.4; the legacy all-120 A5 check is retained beside the amended companion check (28 instantiated A5a cases plus 40 A5b cases). Matching lines and cells are retained in A5_resend_instantiation.json.','', '## Pre-written prediction scorecard','', '| Prediction | Verdict | Numbers / scope |','|---|---|---|']
for r in score:lines.append(f'| {r["prediction"]} | {r["verdict"]} | {r["numbers"]} |')
lines+=['','All evaluable predictions use CONFIRMED/FALSIFIED without changing their criteria. UNTESTED is necessary where the required independent labels, Tier B data or executed positive control are absent; missing observations are neither confirmation nor empirical falsification. No rules were changed to fill these gaps.','',
        '## Constructed — unit/reachability only','',f'Native F/K/S/N_m continuations on 30 frozen controls; oracle/derivation mismatches void instances. Predictions confirmed={sum(r["prediction_confirmed"] and not r["voided"] for r in c["rows"])}/30; voided={sum(r["voided"] for r in c["rows"])}. v1.2 statuses: {dict(Counter(r["CCC"]["status"] for r in c["rows"]))}. Historical v1.1 statuses: {dict(Counter(r["v1.1_status"] for r in c["rows"]))}. No constructed baseline comparison, sensitivity, headline or Gate A verdict contribution.','',
        f'Frozen declared versus extracted info-bearing disagreements: {len(constructed_info_mismatches)}/30 ({constructed_info_mismatches}). The private-quantity regex is preserved verbatim: it recognizes plural “Verified costs”, but these four controls say singular “Verified cost”. Status/reason predictions fail where this misses the cap; no declaration or rule was changed to repair their score.','',
        f'Headline exclusion guards actually raised: {c["headline_guards"]}. Per-instance committed status/reason predictions, measured decisions and oracle checks: constructed_results.json.gz.','',
        f'Frozen descriptive C2 grid limitation: {len(empty_grid)} K-minus-N confidence sets are empty on the registered 0.01 grid (lower endpoint exceeds upper for off-grid deterministic point effects). Raw endpoints are retained in empty_descriptive_grid_intervals.json; they are not gating inputs, and the grid was not changed.','', '## Validation and reproduction','',
        'Exact commands and counts: ops/reports/AMD-FIX-1/tests.json; complete logs beside it. Drivers: run_census.py, evaluate_dev.py, run_constructed.py, report.py. Run from this worktree with PYTHONPATH=. and starter/collusion_hackathon/colosseum/.venv/bin/python. The execution drivers install the same network/secret-file audit guard as the offline test runner; report.py only reads local completed artifacts and generates reporting tables. Test suites use `-m tests.replay.offline_runner -s <dir> -t .` exactly.','',
        'The three known full-suite errors are missing archived pilot config/summary files in this isolated worktree; no archive or tests were altered to conceal them. Full test details are in the handoff. The independent contract file and frozen constructed declarations were not edited.','',
        'Mandatory module-13 integrity/benign checks and retained A5/A6 criteria are reported separately above; a failed retained check keeps the overall Gate A verdict FAIL. Constructed support cannot rescue it.']
(OUT/'GATE_A_v1.2.md').write_text('\n'.join(lines)+'\n')
save('report_summary.json',{'gate_checks':e['gate_checks'],'amended_A5_gate':amended_a5,'headline_supported':headline_supported,'headline_confusion_instances':len(headline_rows),'nonconstructed_DEV_supported':supported,'a1_supported':a1_supported,
                           'constructed_supported':sum(r['CCC']['status']=='supported' for r in c['rows']),
                           'prediction_counts':dict(Counter(r['verdict'] for r in score)),
                           'sources_changed_during_run':e['sources_changed_during_run'],'runner_error_count':len(runner_errors)})
print(json.dumps(json.loads((OUT/'report_summary.json').read_text()),indent=2))
