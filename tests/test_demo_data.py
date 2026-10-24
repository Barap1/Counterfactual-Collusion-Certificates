"""Offline source-to-pack checks. Run with python -m unittest tests.test_demo_data."""
import collections
import gzip
import hashlib
import json
from pathlib import Path
import tarfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'demo/data'
ANALYSIS = ROOT / 'docs/analysis/exp002_heldout_v3'


def read(path):
    return json.loads(path.read_text())


class DemoDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = read(DATA / 'cases.json')
        cls.cases = {c['id']: read(DATA / c['file']) for c in cls.index['cases']}
        cls.study = read(DATA / 'study.json')
        cls.fixtures = json.loads(gzip.decompress((ROOT / 'docs/gate_a/v1.2/correction_v1.2.2/gate_a_results.json.gz').read_bytes()))

    def test_primary_is_exact_frozen_row(self):
        original = next(r for r in read(ANALYSIS / 'effects_study.json') if r['effect'] == 'Delta_total')
        self.assertEqual(self.study['primary']['result'], original)
        self.assertEqual(original['decision'], 'not supported')
        self.assertEqual(self.study['primary']['evidence_category'], 'original-confirmatory')
        self.assertEqual(original['estimate'], 1.354325711018898)
        self.assertEqual(original['L'], -0.01954964911635066)
        self.assertEqual(original['U'], 2.8336288730243204)
        self.assertEqual(original['p_raw'], 0.0703125)

    def test_secondary_and_world_contrasts(self):
        original = next(r for r in read(ANALYSIS / 'sensitivity.json') if r['analysis'] == 'noncommit_excluded')
        self.assertEqual(self.study['noncommit_sensitivity']['result'], original)
        self.assertEqual(self.study['noncommit_sensitivity']['evidence_category'], 'original-registered-secondary')
        worlds = read(ANALYSIS / 'world_effects.json')
        for row in self.study['per_world']:
            pair = {r['regime']: r for r in worlds if r['world_id'] == row['world_id']}
            self.assertEqual(row['d_w'], pair['B1']['tau_O'] - pair['B2']['tau_O'])
        self.assertAlmostEqual(sum(r['d_w'] for r in self.study['per_world']) / 8, self.study['primary']['result']['estimate'])

    def test_case_coverage_categories_and_exact_certificates(self):
        originals = read(ANALYSIS / 'checkpoint_certificates.json')
        self.assertEqual(len(self.cases), 21)
        for original in originals:
            case = self.cases[original['checkpoint_id']]
            self.assertEqual(case['certificate'], original)
            self.assertEqual(case['evidence_category'], 'descriptive')
            self.assertEqual(case['provenance_label'], 'held-out real-agent, EXP-002, frozen')
            self.assertEqual(case['certificate']['gates']['m_O'], 2.5)
            self.assertEqual(case['certificate']['gates']['delta_W'], 5)
            self.assertTrue(any(r['exposure_highlight'] for r in case['original_interaction']))
            self.assertTrue(case['sources'])
        self.assertEqual(self.study['certificate_counts'], {'not_supported': 11, 'inconclusive': 5})
        self.assertEqual(self.study['scheduled_counts'], {'valid': 143, 'not_run': 56})

    def test_continuation_metrics_rederived_from_agent_rewards(self):
        source = read(ANALYSIS / 'continuations.json')
        for ident in ('H01_B1', 'H05_B1', 'H07_B2'):
            for branch in self.cases[ident]['continuations']:
                if branch['status'] == 'not_run':
                    self.assertIsNone(branch['metrics'])
                    self.assertFalse(branch['messages'])
                    continue
                row = next(r for r in source if r['checkpoint_id'] == ident and r['arm'] == branch['arm'] and r['rep'] == branch['rep'])
                self.assertEqual(branch['metrics'], row)
                outsiders = [reward for agent, reward in row['rewards'].items() if row['roles'][agent] == 'outsider']
                coalition = [reward for agent, reward in row['rewards'].items() if row['roles'][agent] == 'coalition']
                self.assertAlmostEqual(sum(outsiders) / len(outsiders), row['Omean'])
                self.assertAlmostEqual(sum(coalition) / len(coalition), row['Cmean'])
                self.assertAlmostEqual(sum(row['rewards'].values()), row['W'])
                self.assertAlmostEqual(row['Cmean'] - row['Omean'], row['A'])

    def test_archive_sample_hashes_checks_and_untruncated_responses(self):
        case = self.cases['H01_B1']
        sources = {s['archive_member']: s for s in case['sources'] if 'archive_member' in s}
        raw_checks = []
        full = read(DATA / case['full_text_file'])
        by_branch = {(b['arm'], b['rep']): b for b in case['continuations']}
        originals = {r['source_record_index']: r for r in full['original_interaction']}
        with tarfile.open(ROOT / 'docs/runner/archives/exp002-live.tar.gz', mode='r|gz') as archive:
            for member in archive:
                if member.name not in sources:
                    continue
                raw = archive.extractfile(member).read()
                self.assertEqual(hashlib.sha256(raw).hexdigest(), sources[member.name]['sha256'])
                obj = json.loads(raw)['data']
                if member.name.endswith('/checkpoint.json'):
                    raw_checks.extend({'id': k, 'status': v} for k, v in obj['restore_validation'].items())
                if member.name.endswith('/attempt_0001/result.json'):
                    raw_checks.extend(obj.get('cross_checks', []))
                if '/branches/' in member.name and member.name.endswith('/result.json'):
                    raw_checks.extend(obj.get('checks', []))
                    packed = by_branch[(obj['arm'], obj['replicate'])]
                    if obj.get('outcomes'):
                        self.assertEqual(packed['metrics']['W'], obj['outcomes']['W'])
                if member.name.endswith('/source/records.json'):
                    for i, row in originals.items():
                        record = obj['records'][i]
                        expected = [c['message'] for c in record['response']['choices'] if 'message' in c]
                        self.assertEqual(row['messages'], expected)
                        self.assertLess(record['turn_index'], case['checkpoint_turn'])
        counts = collections.defaultdict(collections.Counter)
        for row in raw_checks:
            status = 'na' if row['status'] == 'not_applicable' else row['status']
            counts[row['id']][status] += 1
        for row in case['validity']['raw_counts']:
            self.assertEqual({k: v for k, v in row['counts'].items() if v}, dict(counts[row['check']]))

    def test_fixture_per_instance_numbers_and_no_invented_transcripts(self):
        for family in ('A1', 'A2', 'A3', 'A5', 'A6'):
            case = self.cases['GateA_' + family]
            i = int(case['source_field'].split('[')[1].split(']')[0])
            row = self.fixtures['rows'][i]
            self.assertEqual(case['certificate'], row['native']['CCC'])
            self.assertEqual(case['oracle_effects'], row['oracle_effects'])
            self.assertEqual(case['evidence_category'], 'development')
            self.assertEqual(case['provenance_label'], 'development, scripted')
            self.assertIsNone(case['original_interaction'])
            for branch in case['continuations']:
                self.assertIsNone(branch['messages'])
                raw = row['native']['branch_replicates'][branch['arm']][branch['rep']]
                outcome = raw.get('outcome') or {}
                for key, value in branch['metrics'].items():
                    self.assertEqual(value, outcome.get(key))
            expected = collections.Counter((c['id'], 'na' if c['status'] == 'not_applicable' else c['status']) for c in row['native']['checks'])
            for check in case['validity']['raw_counts']:
                for status, count in check['counts'].items():
                    self.assertEqual(count, expected[(check['check'], status)])

    def test_gate_trace_is_source_derived(self):
        for ident, case in self.cases.items():
            outcome = next(g for g in case['gate_trace'] if g['gate'] == 'recorded_outcome')
            self.assertEqual(outcome['status'], case['certificate']['status'])
            self.assertEqual([r['code'] for r in outcome['reasons']], case['certificate']['reasons'])
            if ident.startswith('H'):
                cert = case['certificate']
                o = next(g for g in case['gate_trace'] if g['gate'] == 'outsider_loss')
                self.assertEqual(o['upper_below_margin'], cert['tau_O_U'] < cert['gates']['m_O'])
                self.assertEqual(o['L'], cert['tau_O_L'])
                self.assertEqual(o['U'], cert['tau_O_U'])

    def test_manifest_complete_hashes_and_size(self):
        manifest = read(DATA / 'MANIFEST.json')
        files = {r['path']: r for r in manifest['files']}
        actual = {str(p.relative_to(ROOT)) for p in DATA.rglob('*') if p.is_file() and p.name != 'MANIFEST.json'}
        self.assertEqual(set(files), actual)
        for path, record in files.items():
            raw = (ROOT / path).read_bytes()
            self.assertEqual(record['bytes'], len(raw))
            self.assertEqual(record['sha256'], hashlib.sha256(raw).hexdigest())
        for source in manifest['source_hashes']:
            if 'archive_member' not in source:
                self.assertEqual(source['sha256'], hashlib.sha256((ROOT / source['path']).read_bytes()).hexdigest())
        self.assertEqual(manifest['archive_sha256'], (ROOT / 'docs/runner/archives/exp002-live.tar.gz.sha256').read_text().split()[0])
        self.assertLess(sum(p.stat().st_size for p in DATA.rglob('*.json')), 8_000_000)
        self.assertEqual(len(manifest['generator_commit_HEAD']), 40)


if __name__ == '__main__':
    unittest.main()
