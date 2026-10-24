"""Local fixture HTTP only: no real Ollama server, startup, or model requests."""
import copy
import json
import logging
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler
from http.client import HTTPResponse
from io import BytesIO
from types import SimpleNamespace
from urllib.parse import urlsplit
from urllib.request import Request
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from ccc.runner.manifest import ROOT, call_seed, load, plan, validate
from ccc.runner.live import OllamaSession, ModelReload, local_listener
from ccc.runner.storage import get


class FixtureHandler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_json(self, data):
        body = json.dumps(data).encode()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        state = self.server.state
        state['gets'].append(self.path)
        if self.path == '/api/version':
            return self.send_json({'version': '0.32.5'})
        if self.path == '/api/tags':
            return self.send_json({'models': [dict(name='gemma4:26b', digest=state['digest'])]})
        if self.path == '/api/ps':
            entry = dict(name='gemma4:26b', digest=state['digest'],
                         expires_at=state['expiry'], context_length=state['ctx'], size_vram=17661060710)
            if state['loaded_at'] is not None:
                entry['loaded_at'] = state['loaded_at']
            return self.send_json({'models': [entry]} if state['resident'] else {'models': []})
        self.send_error(404)

    def do_POST(self):
        state = self.server.state
        if self.path != '/v1/chat/completions':
            return self.send_error(404)
        payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        state['posts'].append(payload)
        state['expiry'] = f"9999-12-{30 - len(state['posts']) % 2}T23:59:59Z"
        if payload['messages'] == __import__('ccc.runner.live', fromlist=['CANARY_MESSAGES']).CANARY_MESSAGES:
            response = {'model': 'gemma4:26b', 'choices': [{'message': {'role': 'assistant', 'content': state.get('canary', 'fixed probe')}}]}
            state['canary_calls'] = state.get('canary_calls', 0) + 1
            if state.get('canary_reload') and state['canary_calls'] == 2:
                response['choices'][0]['message']['content'] = 'reloaded probe'
        elif state.get('respond'):
            response = state['respond'](payload)
        else:
            response = {'id': str(len(state['posts'])), 'model': 'gemma4:26b',
                        'choices': [{'message': {'role': 'assistant', 'content': 'fixture'}}]}
        if state.get('reload_on_post') == len(state['posts']):
            state['runner_pid'] = 'runner-2'
        self.send_json(response)


class MemorySocket:
    """Exercise the HTTP handler/parser without a socket syscall (sandbox denies bind)."""
    def __init__(self, data):
        self.input = BytesIO(data)
        self.output = BytesIO()

    def makefile(self, *args):
        return self.input

    def sendall(self, data):
        self.output.write(data)


class FixtureOpener:
    def __init__(self, server):
        self.server = server

    def open(self, request, timeout=None):
        if isinstance(request, str):
            request = Request(request)
        url = urlsplit(request.full_url)
        assert url.hostname == '127.0.0.1' and url.port == self.server.server_port
        body = request.data or b''
        wire = (f'{request.get_method()} {url.path} HTTP/1.0\r\nHost: 127.0.0.1\r\n'
                f'Content-Length: {len(body)}\r\n\r\n').encode() + body
        connection = MemorySocket(wire)
        FixtureHandler(connection, ('127.0.0.1', 1), self.server)
        response = HTTPResponse(MemorySocket(connection.output.getvalue()))
        response.begin()
        return response


@contextmanager
def fixture(m):
    # In-process localhost HTTP server: real stdlib HTTP request/response handling,
    # in-memory byte streams. Neither bind nor connect is available in this sandbox.
    server = SimpleNamespace(server_port=19439)
    server.state = {'digest': m['model']['weight_digest'], 'posts': [], 'gets': [],
                    'runner_pid': 'runner-1', 'loaded_at': '2026-10-23T01:00:00Z', 'resident': True, 'ctx': 32768,
                    'expiry': '9999-12-31T23:59:59Z'}
    with patch('ccc.runner.live.urllib.request.build_opener', return_value=FixtureOpener(server)), \
         patch('ccc.runner.live.local_listener', return_value=['fixture-pid']), \
         patch('ccc.runner.live.model_runner_pid', side_effect=lambda pids: server.state['runner_pid']):
        m['model']['base_url'] = f'http://127.0.0.1:{server.server_port}/v1'
        yield server.state


class LiveTests(unittest.TestCase):
    def setUp(self):
        raw = json.loads((ROOT / 'docs/runner/exp001_manifest.json').read_text())
        # EXP-001 pins the v1.1 protocol file; in this worktree protocol.md is v1.2.
        raw['protocol_artifact'] = 'docs/research/sci002/protocol_v1.1.md'
        self.m = validate(raw)
        previous = logging.root.manager.disable
        logging.disable(logging.CRITICAL)
        self.addCleanup(logging.disable, previous)

    def test_pilot_fixed_matrix_and_parameters(self):
        p = plan(self.m)
        self.assertEqual((p['independent_worlds'], p['base_trajectories'], p['continuations']), (4, 8, 112))
        self.assertEqual([(j['world']['seed'], j['world']['regime']) for j in p['jobs']],
                         [(s, r) for s in (2, 3, 4, 5) for r in ('B1', 'B2')])
        for j in p['jobs']:
            self.assertEqual({a: sum(i['arm'] == a for i in j['order']) for a in 'FSKN'},
                             {'F': 4, 'S': 4, 'K': 4, 'N': 2})
        self.assertEqual(self.m['hard_stop_utc'], '2026-10-24T09:00:00Z')

    def test_call_seed_distinct_deterministic_every_dimension(self):
        seeds = [call_seed(self.m, 'checkpoint', a, r, t, k, 'agent')
                 for a in 'FSKN' for r in range(4) for t in range(8) for k in range(3)]
        self.assertEqual(len(set(seeds)), len(seeds))
        self.assertTrue(all(0 <= s < 2**31 for s in seeds))
        self.assertEqual(seeds[0], call_seed(copy.deepcopy(self.m), 'checkpoint', 'F', 0, 0, 0, 'agent'))
        changed = copy.deepcopy(self.m)
        changed['master_seed'] += 1
        self.assertNotEqual(seeds[0], call_seed(changed, 'checkpoint', 'F', 0, 0, 0, 'agent'))

    def test_holdout_sham_hash_subset_n_on_all_and_default_map(self):
        from ccc.runner.manifest import sham_selected
        self.m['phase'] = 'holdout'
        self.m['continuations_per_arm'] = {'F': 4, 'K': 4, 'S': 1, 'N': 4}
        p = plan(self.m)  # planning does not admit live seeds
        selected = [j for j in p['jobs'] if j['sham_selected']]
        self.assertEqual(sum(j['placebo'] for j in p['jobs']), len(p['jobs']))  # N_m on ALL checkpoints
        self.assertEqual(p['continuations'], 12 * len(p['jobs']) + len(selected))
        for j in p['jobs']:
            self.assertEqual(j['sham_selected'], sham_selected(j['world']['id']))
            self.assertEqual(sum(i['arm'] == 'S' for i in j['order']), int(j['sham_selected']))
        self.assertEqual(p, plan(copy.deepcopy(self.m)))
        from ccc.runner.collector import run
        with tempfile.TemporaryDirectory(dir=ROOT / 'docs/runner') as d, fixture(self.m) as state:
            with self.assertRaisesRegex(ValueError, 'STAT-001'):
                run(self.m, Path(d), live=True)
            self.assertEqual(state['gets'], [])
            self.assertEqual(list(Path(d).iterdir()), [])

    def test_preflight_digest_context_refuse_and_real_ps_accepts(self):
        with fixture(self.m) as state:
            state['digest'] = '0' * 64
            with self.assertRaisesRegex(ValueError, 'digest'):
                OllamaSession(self.m['model'])
            state['digest'] = self.m['model']['weight_digest']
            state['ctx'] = 4096
            with self.assertRaisesRegex(ValueError, 'context_length'):
                OllamaSession(self.m['model'])
            state['ctx'] = 32768
            state['loaded_at'] = None
            OllamaSession(self.m['model'])
            self.assertEqual(state['posts'], [])

    def test_residency_reload_expiry_and_loss_fail_closed(self):
        with fixture(self.m) as state:
            session = OllamaSession(self.m['model'])
            self.assertEqual(session.attestation()['weight_digest'], self.m['model']['weight_digest'])
            session.check()
            state['runner_pid'] = 'runner-2'
            with self.assertRaises(ModelReload):
                session.check()
            state['runner_pid'] = 'runner-1'
            state['expiry'] = '2000-01-01T00:00:00Z'
            with self.assertRaises(ModelReload):
                session.check()
            state['resident'] = False
            with self.assertRaises(ModelReload):
                session.check()

    def test_ollama_expires_at_in_local_offset_is_accepted(self):
        # Ollama serializes /api/ps expires_at in the server's local zone, not UTC.
        import os, time
        previous = os.environ.get("TZ")
        os.environ["TZ"] = "America/New_York"
        time.tzset()
        self.addCleanup(lambda: (os.environ.__setitem__("TZ", previous) if previous else os.environ.pop("TZ", None), time.tzset()))
        with fixture(self.m) as state:
            state['loaded_at'] = None
            state['expiry'] = '9999-12-31T19:59:59-05:00'
            session = OllamaSession(self.m['model'])
            session.check()
            state['expiry'] = '2000-01-01T00:00:00-05:00'  # lease in the past, still a valid offset form
            with self.assertRaisesRegex(ModelReload, "residency expired"):
                session.check()

    def test_real_ps_fingerprint_changes_fail_closed(self):
        with fixture(self.m) as state:
            state['loaded_at'] = None
            session = OllamaSession(self.m['model'])
            session.check()
            state['expiry'] = '9999-12-30T23:59:59Z'
            session.check()
        for field in ('digest', 'size_vram', 'context_length'):
            entry = dict(digest='a', size_vram=10, context_length=32768,
                         expires_at='9999-12-31T23:59:59Z')
            before = OllamaSession.token(entry)
            entry[field] = 'changed'
            self.assertNotEqual(before, OllamaSession.token(entry), field)

    def test_model_runner_process_selection(self):
        from ccc.runner.live import model_runner_pid
        with patch('ccc.runner.live.subprocess.run') as command:
            command.return_value.stdout = "10 1 ollama serve\n11 10 ollama runner --model /blobs/sha256-abc\n12 1 llama-server --model /blobs/sha256-other\n"
            self.assertEqual(model_runner_pid(['10']), '11')
            command.return_value.stdout += "13 10 llama-server --model /blobs/sha256-other\n"
            self.assertIsNone(model_runner_pid(['10']))
            command.side_effect = OSError('unavailable')
            self.assertIsNone(model_runner_pid(['10']))

    def test_listener_wildcard_lan_and_missing_refused(self):
        for output in ('p1\nn*:11434\n', 'p1\nn192.168.1.2:11434\n', ''):
            with patch('ccc.runner.live.subprocess.run') as command:
                command.return_value.stdout = output
                with self.assertRaises(ValueError):
                    local_listener(11434)
        with patch('ccc.runner.live.subprocess.run') as command:
            command.return_value.stdout = 'p10\nn127.0.0.1:11434\np10\nn[::1]:11434\n'
            self.assertEqual(local_listener(11434), ['10'])

    def test_http_guarded_payload_seeds_and_reload_invalidates_checkpoint(self):
        from ccc.runner.collector import run
        from ccc.replay.clients import ScriptedClient
        from ccc.replay.fixtures import signal_policy
        self.m['worlds'] = self.m['worlds'][:1]
        self.m['continuations_per_arm'] = {a: 2 for a in 'FSKN'}
        # Serve the scripted policy over in-memory HTTP using actual replay contexts.
        # This exercises live transport; it remains synthetic fixture evidence.
        from ccc.runner.collector import DurableClient
        original = DurableClient.generate_response
        current = {}
        clients = {}
        def call(client, input, params, ccc_context=None):
            current['context'] = ccc_context
            current['client'] = client
            return original(client, input, params, ccc_context)
        def respond(payload):
            c = current['client']
            scripted = clients.setdefault(id(c), ScriptedClient(signal_policy(), nonce=str(id(c))))
            response, _ = scripted.generate_response(payload['messages'], payload, ccc_context=current['context'])
            return response
        with tempfile.TemporaryDirectory(dir=ROOT / 'docs/runner') as d, fixture(self.m) as state:
            state['respond'] = respond
            state['loaded_at'] = None if getattr(self, 'real_ps', False) else state['loaded_at']
            if getattr(self, 'real_ps', False):
                state['runner_pid'] = None
            state['canary_reload'] = getattr(self, 'canary_reload', False)
            # Source = 28 calls. Reload during the second branch after a completed first branch.
            state['reload_on_post'] = getattr(self, 'reload_on_post', 50)
            with patch.object(DurableClient, 'generate_response', call), \
                 patch('ccc.runner.collector.LIVE_LEDGER', Path(d) / 'shared_budget.jsonl'):
                if state['reload_on_post'] is None and not state['canary_reload']:
                    report = run(self.m, Path(d), live=True)
                    self.assertEqual(report['worlds'][0]['attempts'][0]['status'], 'complete')
                    self.assertEqual(report['live_calls'], len(state['posts']))
                else:
                    with self.assertRaisesRegex(ValueError, 'invalid'):
                        run(self.m, Path(d), live=True)
            attempt = Path(d) / 'worlds/dev02_B1/attempt_0001'
            from ccc.runner.collector import status
            (Path(d) / 'WATCHDOG_EXIT.json').write_text('{}')
            inspected = status(Path(d))
            self.assertEqual(inspected['status'], 'ready' if state['reload_on_post'] is None and not state['canary_reload'] else 'halted')
            from ccc.runner.storage import lock
            with lock(Path(d)):
                pass
            result = get(attempt / 'result.json')
            if state['reload_on_post'] is None and not state['canary_reload']:
                self.assertEqual(result['status'], 'complete')
                self.assertTrue((attempt / 'session_after.json').exists())
                self.assertEqual(state['canary_calls'], 3)
                from ccc.runner.live import CANARY_MESSAGES
                self.assertEqual([i for i, p in enumerate(state['posts']) if p['messages'] == CANARY_MESSAGES],
                                 [28, 29, len(state['posts']) - 1])
                self.assertEqual(sorted(p.name for p in (attempt / 'canary').glob('*.end.json')),
                                 ['after.end.json', 'before.end.json', 'source_after.end.json'])
            else:
                self.assertEqual(result.get('reason'), 'model_reload', result)
                self.assertEqual(len(result['branches']), 8)
                self.assertTrue(all(b['status'] == 'invalid' and b['outcomes'] is None for b in result['branches']))
                self.assertEqual(get(attempt / 'invalidation.json')['scope'], 'all_checkpoint_branches')
                for p in (attempt / 'branches').glob('*/result.json'):
                    self.assertEqual(get(p)['reasons'], ['model_reload'])
            self.assertTrue(get(attempt / 'session_checks.json'))
            self.assertEqual(get(Path(d) / 'run_manifest.json')['ollama']['weight_digest'], self.m['model']['weight_digest'])
            for payload in state['posts']:
                self.assertEqual(payload['temperature'], 0.7)
                self.assertEqual(payload['reasoning_effort'], 'none')
                self.assertEqual(payload['options']['num_ctx'], 32768)
                self.assertEqual(payload['keep_alive'], -1)
                self.assertIsInstance(payload['seed'], int)
            regular = [p for p in state['posts'] if p['max_tokens'] != 16]
            self.assertEqual(len({p['seed'] for p in regular}), len(regular))
            print('fixture counts:', len(state['posts']), 'guarded calls;', state.get('canary_calls', 0), 'canaries;', len(result['branches']), 'branches;', result['status'])
            ledger = [json.loads(s) for s in (attempt / 'budget.jsonl').read_text().splitlines()]
            self.assertEqual(sum(r['event'] == 'attempt_begin' for r in ledger), len(state['posts']))

    def test_full_guarded_http_collection_no_reload(self):
        self.reload_on_post = None
        self.test_http_guarded_payload_seeds_and_reload_invalidates_checkpoint()

    def test_real_ps_canary_reload_invalidates_all_branches(self):
        self.reload_on_post = None
        self.real_ps = True
        self.canary_reload = True
        self.test_http_guarded_payload_seeds_and_reload_invalidates_checkpoint()

    def test_real_ps_no_reload(self):
        self.reload_on_post = None
        self.real_ps = True
        self.test_http_guarded_payload_seeds_and_reload_invalidates_checkpoint()

    def test_hard_stop_before_transport_or_writes(self):
        from ccc.runner.collector import run
        self.m['hard_stop_utc'] = '2000-01-01T00:00:00Z'
        with tempfile.TemporaryDirectory(dir=ROOT / 'docs/runner') as d, fixture(self.m) as state:
            with self.assertRaisesRegex(ValueError, 'hard stop'):
                run(self.m, Path(d), live=True)
            self.assertEqual(state['gets'], [])
            self.assertEqual(list(Path(d).iterdir()), [])

    def test_hard_stop_between_checkpoints(self):
        from ccc.runner.collector import run
        self.m['policy']['live_inference_enabled'] = False
        cutoff = datetime(2026, 10, 24, 9, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory(dir=ROOT / 'docs/runner') as d, \
             patch('ccc.runner.collector.datetime') as clock, \
             patch('ccc.runner.collector.collect_world', return_value={'status': 'complete'}) as collect:
            clock.now.side_effect = [cutoff-timedelta(seconds=1), cutoff-timedelta(seconds=1), cutoff]
            report = run(self.m, Path(d), dry_run=True)
            self.assertEqual(collect.call_count, 1)
            self.assertEqual(sum(bool(w['attempts']) for w in report['worlds']), 1)

    def test_hard_stop_after_source_retains_source_without_branches(self):
        from ccc.runner.collector import run
        self.m['policy']['live_inference_enabled'] = False
        self.m['worlds'] = self.m['worlds'][:1]
        cutoff = datetime(2026, 10, 24, 9, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory(dir=ROOT / 'docs/runner') as d, \
             patch('ccc.runner.collector.datetime') as clock:
            clock.now.side_effect = [cutoff-timedelta(seconds=1), cutoff-timedelta(seconds=1), cutoff]
            report = run(self.m, Path(d), dry_run=True)
            self.assertEqual(report['worlds'][0]['attempts'][0]['status'], 'stopped_hard_stop')
            self.assertTrue(list(Path(d).rglob('final_state.json')))
            self.assertFalse(list(Path(d).rglob('branches')))

    def test_model_reload_only_one_explicit_retry(self):
        from ccc.runner.collector import run
        self.m['policy']['live_inference_enabled'] = False
        with tempfile.TemporaryDirectory(dir=ROOT / 'docs/runner') as d, \
             patch('ccc.runner.collector.collect_world', return_value={'status': 'invalid', 'reason': 'model_reload'}) as collect:
            with self.assertRaisesRegex(ValueError, 'invalid'):
                run(self.m, Path(d), dry_run=True)
            with self.assertRaisesRegex(ValueError, 'invalid'):
                run(self.m, Path(d), dry_run=True, retry_failed=True)
            with self.assertRaisesRegex(ValueError, 'single checkpoint retry exhausted'):
                run(self.m, Path(d), dry_run=True, retry_failed=True)
            self.assertEqual(collect.call_count, 2)

    def test_default_map_and_legacy_seed_temperature_remote_refused(self):
        default = copy.deepcopy(self.m)
        del default['continuations_per_arm']
        self.assertEqual(validate(default)['continuations_per_arm'], {'F': 4, 'K': 4, 'S': 2, 'N': 4})
        for mutation in ('scalar', 'legacy', 'temperature', 'remote'):
            m = copy.deepcopy(self.m)
            if mutation == 'scalar':
                m['continuations_per_arm'] = 4
            elif mutation == 'legacy':
                m['sampling_seed'] = m.pop('master_seed')
            elif mutation == 'temperature':
                m['model']['parameters']['temperature'] = 0.0
            else:
                m['model']['base_url'] = 'http://192.168.1.2:11434/v1'
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                validate(m)
