"""The benchmark's migration interface preserves inputs before any inference."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / 'scripts/run/ask_suite.py'


def case(identity, records, truth='none'):
    return dict(id=identity, function='find', level='memory', test='migration',
                args=['Which?', '--jsonl', '--field', '/input'],
                records=[dict(id=i, input=t) for i, t in records], truth=truth)


class FindPackingTest(unittest.TestCase):
    def validate(self, cases):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'find.jsonl'
            path.write_text(''.join(json.dumps(c, ensure_ascii=False) + '\n' for c in cases))
            return subprocess.run([sys.executable, RUNNER, 'validate-find', path], capture_output=True, text=True)

    def test_all_original_cases_have_their_original_inventory_without_calls(self):
        done = subprocess.run([sys.executable, RUNNER, 'validate-find', ROOT / 'questions/suite/find.jsonl'],
                              capture_output=True, text=True, env=dict(os.environ, THINKTHEN_BIN='/nonexistent/no-model'))
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout), dict(cases=700, memory=300, context=300, card=100,
                         gold_none=90, multiline_candidates=400, **{'plain-lines-v1': 300, 'json-candidates-v1': 400}))

    def test_duplicate_ids_refuse_but_duplicate_text_and_blank_candidates_survive(self):
        for records, ok in [([('a', 'same'), ('b', 'same')], True),
                            ([('a', ''), ('b', '\r\n é🙂')], True),
                            ([('a', 'one'), ('a', 'two')], False)]:
            with self.subTest(records=records):
                done = self.validate([case('test', records)])
                self.assertEqual(done.returncode == 0, ok, done.stderr)
                if ok:
                    self.assertEqual(json.loads(done.stdout)['cases'], 1)
                else:
                    self.assertIn('distinct', done.stderr)

    def test_unknown_old_options_cannot_be_silently_discarded(self):
        c = case('test', [('a', 'one')])
        c['args'] += ['--invented-option']
        done = self.validate([c])
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('refusing to drop', done.stderr)

    def test_command_start_failure_is_retained_for_every_case(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            cases = [case('first', [('a', 'x')]), case('second', [('a', 'y')])]
            (folder / 'find.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in cases))
            env = {k: v for k, v in os.environ.items() if not k.startswith(('THINKTHEN_', 'BENCH_', 'BEATLES_BENCH_'))}
            env.update(THINKTHEN_BIN=str(folder / 'missing-command'), BENCH_FUNCTIONS=str(folder))
            done = subprocess.run([sys.executable, RUNNER, 'packed-find', folder / 'run'],
                                  capture_output=True, text=True, env=env)
            self.assertEqual(done.returncode, 0, done.stderr)
            outputs = [json.loads(line) for line in (folder / 'run/outputs.jsonl').read_text().splitlines()]
            self.assertEqual([o['id'] for o in outputs], ['first', 'second'])
            for output in outputs:
                self.assertIsNone(output['exit'])
                self.assertEqual(output['rows'], [])
                self.assertEqual(output['outcome'], dict(status='harness-error', error='could not start command: FileNotFoundError'))


class FindScoringTest(unittest.TestCase):
    def test_migration_report_refuses_historical_outputs(self):
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            (folder / 'cases.jsonl').write_text(json.dumps(case('old', [('a', 'x')])) + '\n')
            historical = dict(id='old', exit=0, rows=[dict(value=None, answer=dict(pick='none'))])
            (folder / 'outputs.jsonl').write_text(json.dumps(historical) + '\n')
            done = subprocess.run([sys.executable, ROOT / 'scripts/score/score_suite.py', 'find', folder, folder / 'cases.jsonl'],
                                  capture_output=True, text=True)
            self.assertNotEqual(done.returncode, 0)
            self.assertEqual(done.stdout, '')
            self.assertIn('historical rows cannot be relabeled', done.stderr)

    def test_failed_unsure_missing_and_invalid_output_never_become_none(self):
        sys.path.insert(0, str(ROOT / 'scripts/run'))
        import find_packing
        cases = [case(str(i), [('a', 'x')], truth) for i, truth in enumerate(
            ['a', 'none', 'none', 'a', 'a', 'a', 'none', 'a', 'none'])]
        outputs = []
        for c in cases:
            _, mapping = find_packing.pack(c)
            row = dict(id=c['id'], function='find', position=1, status='answered', answer=None)
            outputs.append(dict(id=c['id'], exit=0, rows=[row], packing=mapping))
        outputs[1]['exit'] = 3  # The command's explicit --check unsure outcome.
        outputs[1]['rows'][0]['status'] = 'unsure'
        outputs[2]['rows'] = []
        outputs[3]['exit'] = 6
        outputs[3]['rows'][0].update(status='failed', error=dict(code='record.response', message='bad reply'))
        outputs[4].update(exit=2, rows=[])
        outputs[5]['rows'][0]['answer'] = dict(start=1, end=2, text='x')
        outputs[6]['exit'] = 1  # --check none is still an answered null.
        outputs[7]['rows'][0]['answer'] = dict(start=0, end=1, text='x')
        outputs[8].update(parse_error=True, rows=[])
        with tempfile.TemporaryDirectory() as folder:
            folder = Path(folder)
            (folder / 'cases.jsonl').write_text(''.join(json.dumps(c) + '\n' for c in cases))
            (folder / 'outputs.jsonl').write_text(''.join(json.dumps(o) + '\n' for o in outputs))
            done = subprocess.run([sys.executable, ROOT / 'scripts/score/score_suite.py', 'find', folder, folder / 'cases.jsonl'],
                                  capture_output=True, text=True)
            self.assertEqual(done.returncode, 0, done.stderr)
            rows = {r['measure']: r for r in json.loads(done.stdout)['rows']}
            self.assertEqual({r['test'] for r in rows.values()}, {'all'})
            self.assertEqual((rows['exact match']['n'], rows['exact match']['value']), (9, 2 / 9))
            self.assertEqual((rows['answered accuracy']['n'], rows['answered accuracy']['value']), (3, 2 / 3))
            for key, count in [('unsure', 1), ('missing', 1), ('failed', 1), ('call-failed', 1),
                               ('harness-error', 2), ('false none', 1), ('correct none', 1)]:
                self.assertEqual(rows[key + ' cases']['value'], count, key)
            self.assertIsNone(rows['exact match']['usd'])


if __name__ == '__main__':
    unittest.main()
