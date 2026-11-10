"""Explicit installed-0.2 loopback proof; outside the historical 0.1 replay suite.

THINKTHEN_02_BIN=/installed/bin/thinkthen python3 tests/installed_find_migration.py
"""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

from test_find_migration import ROOT, RUNNER, case


class InstalledFindMigrationTest(unittest.TestCase):
    def test_one_case_one_record_with_typed_outcomes_and_exact_original_candidate_ids(self):
        cases = [case('duplicate', [('a', 'same'), ('b', 'same')], 'b'),
                 case('unicode', [('a', 'é🙂'), ('b', '答')], 'b'),
                 case('multiline', [('a', 'line\none'), ('b', 'é\r\n🙂')], 'b'),
                 case('none', [('a', 'answer')]),
                 case('unsure', [('a', 'first'), ('b', 'second')], 'a'),
                 case('low-none', [('a', 'first'), ('b', 'second')]),
                 case('failed', [('a', 'answer')]),
                 case('blank', [('a', ''), ('b', ' \t')], 'a'),
                 case('oversized', [('a', 'x' * 100001)], 'a')]
        for c in cases:
            c['args'][0] = c['id']
        expected = {
            'duplicate': ['same', 'same'], 'unicode': ['é🙂', '答'],
            'multiline': ['{"id":"a","text":"line\\none"}', '{"id":"b","text":"é\\r\\n🙂"}'],
            'none': ['answer'], 'unsure': ['first', 'second'], 'low-none': ['first', 'second'],
            'failed': ['answer'], 'blank': ['{"id":"a","text":""}', '{"id":"b","text":" \\t"}']}
        distributions = {name: {'u1': 0.05, 'u2': 0.9, 'none': 0.05} for name in ('duplicate', 'unicode', 'multiline')}
        distributions.update(none={'u1': 0.1, 'none': 0.9}, unsure={'u1': 0.4, 'u2': 0.3, 'none': 0.3},
                             **{'low-none': {'u1': 0.3, 'u2': 0.3, 'none': 0.4},
                                'blank': {'u1': 0.9, 'u2': 0.05, 'none': 0.05}})
        received, errors = [], []

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
                questions = body['questions']
                if len(questions) != 1:
                    errors.append('not exactly one question')
                answers = {}
                for identity, question in questions.items():
                    name = question['instructions'].rsplit('Question: ', 1)[-1]
                    received.append(name)
                    lines = expected[name]
                    criteria = question['criteria']
                    if [criteria[f'u{i + 1}'] for i in range(len(lines))] != lines or set(criteria) != {f'u{i+1}' for i in range(len(lines))} | {'none'}:
                        errors.append('candidate count/text changed: ' + name)
                    answers[identity] = {'type': 'unknown'} if name == 'failed' else dict(type='choice', probabilities=distributions[name])
                data = json.dumps(dict(answers=answers)).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *_):
                pass

        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            (folder / 'find.jsonl').write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in cases))
            server = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
            worker = threading.Thread(target=server.serve_forever)
            worker.start()
            try:
                # Supply only this fixture's key/address; never read an ambient provider key.
                env = {k: v for k, v in os.environ.items() if not k.startswith(('THINKTHEN_', 'BENCH_', 'BEATLES_BENCH_'))}
                env.update(THINKTHEN_BIN=os.environ['THINKTHEN_02_BIN'],
                           THINKTHEN_API_KEY='fixture-key', THINKTHEN_BACKEND='systemone',
                           THINKTHEN_BASE_URL=f'http://127.0.0.1:{server.server_port}/v1',
                           BEATLES_BENCH_MODEL='benchmark-loopback', BENCH_THINKTHEN_ARGS='--threshold 0.5',
                           BENCH_FUNCTIONS=str(folder))
                done = subprocess.run([sys.executable, RUNNER, 'packed-find', folder / 'run'],
                                      capture_output=True, text=True, env=env)
                self.assertEqual(done.returncode, 0, done.stderr)
            finally:
                server.shutdown()
                server.server_close()
                worker.join()
            self.assertEqual(errors, [])
            self.assertCountEqual(received, expected)
            outputs = [json.loads(line) for line in (folder / 'run/outputs.jsonl').read_text().splitlines()]
            self.assertEqual(len(outputs), 9)
            by_id = {o['id']: o for o in outputs}
            for name in ('duplicate', 'unicode', 'multiline'):
                self.assertEqual(by_id[name]['outcome'], dict(status='answered', selection='candidate', candidate_id='b'))
            self.assertEqual(by_id['unicode']['rows'][0]['answer'], dict(start=3, end=4, text='答'))
            self.assertEqual(by_id['none']['outcome'], dict(status='answered', selection='none'))
            self.assertEqual(by_id['unsure']['outcome'], dict(status='unsure'))
            self.assertEqual(by_id['low-none']['outcome'], dict(status='unsure'))
            self.assertEqual(by_id['blank']['outcome'], dict(status='answered', selection='candidate', candidate_id='a'))
            for name, exit_code in (('failed', 4), ('oversized', 6)):
                self.assertEqual(by_id[name]['outcome']['status'], 'failed')
                self.assertEqual(by_id[name]['exit'], exit_code)
            self.assertEqual(by_id['failed']['rows'][0]['error']['code'], 'backend.reply')
            self.assertEqual(by_id['oversized']['rows'][0]['error']['code'], 'record.too-large')
            for output in outputs:
                self.assertEqual(output['rows'][0]['source']['backend'], 'systemone')
                self.assertEqual(output['rows'][0]['source']['model'], 'benchmark-loopback')
            # A missing process output and an empty successful output are neither none nor failure rows.
            outputs = [o for o in outputs if o['id'] != 'duplicate']
            by_id['unicode']['rows'] = []
            (folder / 'run/outputs.jsonl').write_text(''.join(json.dumps(o) + '\n' for o in outputs))
            done = subprocess.run([sys.executable, ROOT / 'scripts/score/score_suite.py', 'find', folder / 'run', folder / 'find.jsonl'],
                                  capture_output=True, text=True, env=env)
            self.assertEqual(done.returncode, 0, done.stderr)
            rows = {r['measure']: r for r in json.loads(done.stdout)['rows']}
            self.assertEqual(rows['exact match']['n'], 9)
            self.assertEqual(rows['exact match']['value'], 3 / 9)
            self.assertEqual(rows['answered accuracy']['n'], 3)
            self.assertEqual(rows['missing cases']['value'], 2)
            self.assertEqual(rows['unsure cases']['value'], 2)
            self.assertEqual(rows['failed cases']['value'], 2)
            self.assertEqual(rows['correct none cases']['value'], 1)
            self.assertEqual(rows['false none cases']['value'], 0)
            self.assertIsNone(rows['exact match']['input_tokens'])
            self.assertIsNone(rows['exact match']['usd'])


if __name__ == '__main__':
    unittest.main()
