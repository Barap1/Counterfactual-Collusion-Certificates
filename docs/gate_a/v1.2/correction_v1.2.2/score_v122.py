# Mechanical re-scoring of v1.2.2 evidence (derived from ops/reports/AMD-FIX-2/report.py; JSON outputs only).
from tests.replay.offline_runner import guard
import sys
sys.addaudithook(guard)
"""Mechanical reporting; never mutates measured decisions or frozen predictions."""
import copy,gzip,json,re
from collections import Counter
from pathlib import Path
from hashlib import sha256
from ccc.audit.decision import decide
from ccc.audit.gate_a import confusion_counts
from ccc.audit.commitments import normalize
from ccc.fixtures.jira import generate_jira
ROOT=Path.cwd();PRIOR=ROOT/'docs/gate_a/v1.2';OUT=PRIOR/'correction_v1.2.2'
PREV=PRIOR/'correction_v1.2.1'
def read(path):
    with gzip.open(path,'rt') as f:return json.load(f)
def save(name,data): (OUT/name).write_text(json.dumps(data,indent=2)+'\n')
def key(r):return r['family'],r['stratum'],r['seed']
def status(r):return r['native']['CCC']['status']
e=read(OUT/'gate_a_results.json.gz'); rows=e['rows']
old=read(ROOT/'docs/gate_a/eng005/gate_a_results.json.gz');prior={key(r):r for r in old['rows']}
original=read(ROOT/'docs/gate_a/gate_a_results.json.gz');original_by_key={key(r):r for r in original['rows']}
c=read(OUT/'constructed_results.json.gz')  # carried forward byte-identical from v1.2.1 (theta-independent)
constructed_table={r['instance_id']:r for r in json.loads((ROOT/'docs/research/sci002/constructed_controls.json').read_text())['instances']}
constructed_info_mismatches=[r['instance_id'] for r in c['rows'] if r['CCC']['info_bearing'] != constructed_table[r['instance_id']]['info_bearing']]
save('constructed_info_mismatches.json',{'instances':constructed_info_mismatches,'private_quantity_regex_preserved':False})
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
pre=json.loads((PRIOR/'pre_ccc_conditional_prediction.json').read_text())
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
census1=json.loads((PRIOR/'census_fx1.json').read_text());census2=json.loads((PRIOR/'census_fx2.json').read_text())
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
previous_score={r['prediction']:r for r in json.loads((PREV/'prediction_scorecard.json').read_text())}
deltas=[{'prediction':r['prediction'],'before':previous_score[r['prediction']]['verdict'],
         'after':r['verdict'],'old_numbers':previous_score[r['prediction']]['numbers'],'numbers':r['numbers']}
        for r in score if r['verdict']!=previous_score[r['prediction']]['verdict']]
save('scorecard_deltas.json',deltas)
pc=read(PRIOR/'constructed_results.json.gz');pc_by={r['instance_id']:r for r in pc['rows']}
save('constructed_prediction_scorecard.json',[{'instance_id':r['instance_id'],'prediction':r['prediction'],
     'verdict':'UNTESTED' if r['voided'] else 'CONFIRMED' if r['prediction_confirmed'] else 'FALSIFIED',
     'previous_verdict':'UNTESTED' if pc_by[r['instance_id']]['voided'] else 'CONFIRMED' if pc_by[r['instance_id']]['prediction_confirmed'] else 'FALSIFIED',
     'measured_status':r['CCC']['status'],'measured_reasons':r['CCC']['reasons']} for r in c['rows']])
prior_e=read(PREV/'gate_a_results.json.gz');pr={key(r):r for r in prior_e['rows']}
save('v1.2.1_to_v1.2.2_decision_deltas.json',[{'key':key(r),'old':pr[key(r)]['native']['CCC'],'new':r['native']['CCC']}
     for r in rows if pr[key(r)]['native']['CCC']!=r['native']['CCC']])
summary={'evidence_version':'1.2.2','gate_checks':e['gate_checks'],'amended_A5_gate':amended_a5,
         'headline_supported':headline_supported,'headline_confusion_instances':len(headline_rows),
         'nonconstructed_DEV_supported':supported,'a1_supported':a1_supported,
         'constructed_supported':sum(r['CCC']['status']=='supported' for r in c['rows']),
         'constructed_predictions_match':sum(r['prediction_confirmed'] and not r['voided'] for r in c['rows']),
         'prediction_counts':dict(Counter(r['verdict'] for r in score)),
         'sources_changed_during_run':e['sources_changed_during_run'],'runner_error_count':len(runner_errors)}
save('report_summary.json',summary)
