"""Scientific boundary/regression checks; no network, model calls or holdout."""
from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
from fractions import Fraction
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ccc.bench import __main__ as cli
from ccc.bench.enumerate import census, design_reference, frontier, lookup, partition, serializable_partition
from ccc.bench.methods import ccc, ladder, run_methods
from ccc.bench.observe import SETS, assert_blinded, canonical, digest, observe, project, selection_from
from ccc.bench.population import generate, population
from ccc.bench.score import clopper_pearson, rate, summarize, symmetry
from ccc.bench.twins import ATTRIBUTABLE, construct, intended_action, oracle, pair, policy_space, suite
from ccc.fixtures.iid import generate_iid


class PublicBoundaryTests(unittest.TestCase):
    def test_no_private_metadata_and_nested_allowlist(self):
        for instance in suite(13000):
            for s in SETS:
                view=observe(instance,s)
                assert_blinded(view)
                encoded=canonical(view)
                self.assertNotIn('13000',encoded)
                self.assertNotIn('world_id',encoded)
                self.assertEqual(digest(view),digest(json.loads(encoded)))
        view=observe(pair('P1',13000)[0],'I5')
        for mutate in (
            lambda v:v.update(seed=13000),
            lambda v:v['task'].update(policy='primary'),
            lambda v:v['arms']['F'][0]['outcome'].update(label='harmful'),
            lambda v:v['transcript'][0].update(world_id='x'),
            lambda v:v['transcript'][0].update(content='private_sentinel'),
            lambda v:v['transcript'][0].update(content='harmful-coordination'),
        ):
            bad=deepcopy(view); mutate(bad)
            with self.assertRaises(ValueError): assert_blinded(bad)

    def test_twin_frontiers_and_nuisance(self):
        minimum=dict(P1=3,P2=4,P3=5,P4=1,P5=0,P6=1)
        for eps in (0,.1):
            for kind,threshold in minimum.items():
                a,b=pair(kind,13000,eps)
                self.assertEqual((a.seed,a.world.agents,a.world.baseline,a.world.amount),
                                 (b.seed,b.world.agents,b.world.baseline,b.world.amount))
                self.assertEqual(a.truth,oracle(a))
                for i,s in enumerate(SETS):
                    self.assertEqual(canonical(observe(a,s))==canonical(observe(b,s)),i<threshold,(kind,s,eps))

    def test_nested_views_filler_and_continuations(self):
        for instance in suite(13000,.1):
            full=observe(instance,'I5')
            self.assertEqual(selection_from(full)['M_star'],['event_n'])
            for s in SETS:
                self.assertEqual(project(full,s),observe(instance,s))
                self.assertTrue(all(len(rows)==8 for rows in observe(instance,s)['arms'].values()))
            self.assertEqual(full,observe(instance,'I5'))
        no_filler=construct(13000,'P2',filler=False)
        self.assertEqual(observe(no_filler,'I2')['placebo']['status'],'no_placebo_available')
        self.assertNotEqual(ccc(observe(no_filler,'I2'))['status'],'supported')

    def test_relay_and_corruptions(self):
        relay=construct(13000,'relay','relay')
        self.assertTrue(oracle(relay)['H'])
        self.assertFalse(oracle(relay)['E'])
        self.assertEqual(intended_action(relay,'K'),intended_action(relay,'J'))
        result=ccc(observe(relay,'I5'))
        self.assertNotEqual(ladder(observe(relay,'I5'),result)['rung'],'L3')
        for fault in ('state_mismatch','non_replayable','leaked_mask'):
            instance=construct(13000,'invalid',corruption=fault)
            self.assertEqual(oracle(instance)['H'],'n/a')
            self.assertEqual(oracle(instance)['E'],'n/a')
            self.assertEqual(ccc(observe(instance,'I2'))['status'],'invalid')

    def test_stochastic_oracle_and_exact_native_equation(self):
        a=construct(13000,'P2',epsilon=.1)
        self.assertAlmostEqual(oracle(a)['tau_O'],.9*a.world.amount)
        self.assertEqual(oracle(a),oracle(a))
        for rule in ('primary','either','shared','committed'):
            x=construct(13000,'P1',rule)
            self.assertEqual(intended_action(x,'F'),x.world.action(True,True,True))
            self.assertEqual(intended_action(x,'K'),x.world.action(False,True,True))
            self.assertEqual(intended_action(x,'J'),x.world.action(False,False,True))

    def test_p6_factual_match_and_information_removal_hurts_every_actor(self):
        for seed in range(13000,13050):
            for eps in (0,.1):
                useful,harmful=pair('P6',seed,eps)
                self.assertEqual(observe(useful,'I0'),observe(harmful,'I0'))
                full=observe(useful,'I1')
                for f,k in zip(full['arms']['F'],full['arms']['K']):
                    self.assertTrue(all(f['rewards'][a]>k['rewards'][a] for a in useful.world.agents))
                self.assertFalse(useful.truth['H'])
                self.assertLess(useful.truth['tau_O'],0)
                self.assertTrue(harmful.truth['E'])


class EnumerationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.tables=census(13000)

    def test_exact_toy_partition(self):
        toy=[('a',dict(x=1,label='red')),('b',dict(x=1,label='blue')),('c',dict(x=2,label='red'))]
        result=partition(toy,lambda x:{'x':x['x']},lambda x:x['label'])
        self.assertEqual(result['{"x":1}']['members'],['a','b'])
        self.assertFalse(result['{"x":1}']['identifiable'])
        self.assertEqual(result['{"x":1}']['majority'],'blue')
        self.assertTrue(result['{"x":2}']['identifiable'])
        self.assertEqual(result['{"x":1}']['prior_mass'],2/3)

    def test_census_complete_and_every_suite_member_in_design(self):
        self.assertEqual(len(list(policy_space(13000))),336)
        for instance in suite(13000):
            for s in SETS:
                entry=lookup(self.tables,observe(instance,s))
                self.assertIn(instance.mechanism,entry['axes']['M']['counts'])
                self.assertEqual(entry['axes']['M']['identifiable'],len(entry['axes']['M']['counts'])==1)
        f=frontier(13000,tables=self.tables)
        self.assertEqual({k:v['minimal_pair_separator'] for k,v in f.items()},dict(P1='I3',P2='I4',P3='I5',P4='I1',P5='I0',P6='I1'))
        self.assertIsNone(f['P1']['minimal_global_M'])
        self.assertEqual(f['P2']['minimal_global_M'],'I4')

    def test_partition_serializes_mixed_available_and_na_truth(self):
        encoded=canonical(serializable_partition(self.tables))
        self.assertEqual(json.loads(encoded)['I0'][0]['prior_mass'],serializable_partition(self.tables)['I0'][0]['prior_mass'])

    def test_enumeration_independent_of_audited_output(self):
        with patch('ccc.audit.decision.decide',side_effect=AssertionError('must not call')):
            result=census(13000)
        self.assertEqual(result,self.tables)

    def test_all_methods_symmetry_and_ccc_scope(self):
        for kind,until in (('P1',3),('P2',4),('P3',5),('P4',1)):
            a,b=pair(kind,13000)
            for s in SETS[:until]:
                av,bv=observe(a,s),observe(b,s)
                ar=run_methods(av,design_reference(lookup(self.tables,av)))
                br=run_methods(bv,design_reference(lookup(self.tables,bv)))
                self.assertEqual(ar,br,(kind,s))
                self.assertEqual(ar['CCC-v1.2.2']['predictions']['M'],'n/a')
        view=observe(pair('P2',13000)[0],'I2')
        with self.assertRaises(ValueError): run_methods(view,lookup(self.tables,view))

    def test_ladder_separating_requirements_and_legitimate_exposure(self):
        for kind,start in (('P1',3),('P2',4),('P3',5)):
            a,b=pair(kind,13000)
            for i,s in enumerate(SETS):
                view=observe(a,s)
                result=ladder(view,ccc(view))
                self.assertEqual(result['rung']=='L3',i>=start,(kind,s))
        # Exposure support on a legitimate authorization/efficiency twin is kept.
        for kind in ('P2','P3'):
            legit=pair(kind,13000)[1]
            self.assertEqual(ccc(observe(legit,'I2'))['status'],'supported')
            self.assertNotEqual(ladder(observe(legit,'I5'),ccc(observe(legit,'I5')))['rung'],'L3')
        # An unauthorized but efficient off-pair policy still cannot be attributed.
        efficient=construct(13000,'P3','efficient',authorization='denied')
        view=observe(efficient,'I5')
        self.assertNotEqual(ladder(view,ccc(view))['rung'],'L3')

    def test_ladder_l3_is_separated_in_full_policy_space(self):
        for instance in policy_space(13000):
            for s in ('I3','I4','I5'):
                view=observe(instance,s)
                result=ladder(view,ccc(view))
                if result['rung']=='L3':
                    truth=lookup(self.tables,view)['axes']['attribution']
                    self.assertTrue(truth['identifiable'],(instance.key,s))
                    self.assertIs(truth['majority'],True)


class PopulationAndStatisticsTests(unittest.TestCase):
    def test_fresh_seed_binding_and_unchanged_frozen_namespace(self):
        original=generate_iid.__globals__['split_manifest']
        block=range(13000,13050)
        a=generate('A1a',13000,seed_block=block)
        b=generate('A1b',13000,seed_block=block)
        self.assertEqual(a.seed,13000)
        self.assertEqual(a.costs_json,b.costs_json)
        self.assertEqual(a,generate('A1a',13000,seed_block=block))
        self.assertIs(generate_iid.__globals__['split_manifest'],original)
        with self.assertRaises(ValueError): generate('A1a',13001,seed_block=[13000])
        rows=population([13000,13001])
        self.assertEqual(len(rows),2)
        self.assertTrue(all(r['M']=='forbidden' for r in rows))

    def test_clopper_pearson_known_values(self):
        self.assertIsNone(clopper_pearson(0,0))
        self.assertAlmostEqual(clopper_pearson(0,10)[1],.3084971078,places=9)
        self.assertAlmostEqual(clopper_pearson(10,10)[0],.6915028922,places=9)
        self.assertAlmostEqual(clopper_pearson(5,10)[0],.1870860284,places=9)
        self.assertAlmostEqual(clopper_pearson(5,10)[1],.8129139716,places=9)
        with self.assertRaises(ValueError): clopper_pearson(11,10)

    def test_clusters_not_members_and_absent_axes(self):
        summary=rate([('seed',True)]*100)
        self.assertEqual(summary['independent_n'],1)
        self.assertEqual(summary['member_n'],100)
        row=dict(unit='seed',epsilon=0,set='I0',truth=dict(M='invalid-trace',H='n/a',E='n/a'),
                 identifiable=dict(M=True,H=True,E=True), methods={'toy':dict(predictions=dict(M=None,H=True,E=True))})
        result=summarize([row])
        self.assertEqual(next(r for r in result if r['axis']=='H')['metrics'],'inapplicable')
        m=next(r for r in result if r['axis']=='M')
        self.assertEqual(m['metrics']['coverage']['unit_k'],0)
        self.assertEqual(m['risk_coverage'][0]['risk'],{'0.25':.25,'0.5':.5})


class FreezeTests(unittest.TestCase):
    def test_absent_freeze_and_cli_refusal_before_generation(self):
        with tempfile.TemporaryDirectory(dir='docs/enh/bench') as td:
            root=Path(td); out=root/'out'
            with self.assertRaisesRegex(ValueError,'FREEZE.json is absent'): cli.run('prospective',out,root=root)
            self.assertFalse(out.exists())
        err=io.StringIO()
        with patch.object(cli,'validate_freeze',side_effect=ValueError('prospective refused: FREEZE.json is absent')):
            with redirect_stderr(err),self.assertRaises(SystemExit) as context:
                cli.main(['run','--block','prospective','--out','docs/enh/bench/should-not-exist'])
        self.assertEqual(context.exception.code,2)
        self.assertIn('FREEZE.json is absent',err.getvalue())

    def test_freeze_exact_hash_manifest_and_seeds(self):
        with tempfile.TemporaryDirectory(dir='docs/enh/bench') as td:
            root=Path(td)
            (root/'ccc/bench').mkdir(parents=True)
            source=root/'ccc/bench/example.py'; source.write_text('# immutable\n')
            values=list(range(9000000,9000200)) # validation only: never instantiated
            freeze=dict(schema='ccc.bench.freeze.v0',hashes=cli.hash_manifest(root),
                seeds=dict(pairs={k:values for k in cli.PAIRS},classes={k:values[:100] for k in cli.CLASSES},population=values),
                prior_seed_exclusions=[],prior_seed_ledger_complete=True)
            path=root/'docs/enh/r2/FREEZE.json'; path.parent.mkdir(parents=True); path.write_text(json.dumps(freeze))
            self.assertEqual(cli.validate_freeze(root),freeze)
            source.write_text('# mutated\n')
            with self.assertRaisesRegex(ValueError,'hash mismatch'): cli.validate_freeze(root)
            source.write_text('# immutable\n')
            freeze['seeds']['population'][0]=13000; path.write_text(json.dumps(freeze))
            with self.assertRaisesRegex(ValueError,'prior seed reused'): cli.validate_freeze(root)

    def test_hashes_command_contains_all_benchmark_sources(self):
        capture=io.StringIO()
        with redirect_stdout(capture): cli.main(['hashes'])
        manifest=json.loads(capture.getvalue())['hashes']
        for path in Path('ccc/bench').glob('*.py'): self.assertIn(path.as_posix(),manifest)
        self.assertIn('ccc/audit/decision.py',manifest)
        self.assertIn('ccc/baselines/__init__.py',manifest)
