"""Benchmark-only 0.2 find presentation and exact Unicode-scalar identity mapping."""
import hashlib
import json
from collections import Counter


def pack(case):
    if case['args'][1:] not in (['--jsonl', '--field', '/input'], ['--jsonl', '--field', '/input', '--none']):
        raise ValueError('unsupported legacy find arguments; refusing to drop options')
    records = case['records']
    if case['function'] != 'find' or not records:
        raise ValueError('find requires a nonempty candidate set')
    ids = [(type(r['id']), r['id']) for r in records]
    if any(type(i) not in (str, int) for _, i in ids) or len(set(ids)) != len(ids):
        raise ValueError('candidate IDs must be distinct strings or integers')
    texts = [r['input'] for r in records]
    if any(not isinstance(t, str) for t in texts):
        raise ValueError('candidate text must be a string')
    plain = all(t.strip() and '\n' not in t and '\r' not in t for t in texts)
    lines = texts if plain else [json.dumps({'id': r['id'], 'text': r['input']},
                                           ensure_ascii=False, separators=(',', ':')) for r in records]
    document = '\n'.join(lines)
    spans, start = [], 0
    for r, line in zip(records, lines):
        spans.append(dict(id=r['id'], start=start, end=start + len(line), text=line))
        start += len(line) + 1
    encoded = document.encode('utf-8')  # Refuse unpaired surrogates; never silently replace evidence.
    return dict(id=case['id'], input=document), dict(
        contract='thinkthen-0.2-packed-find-v1',
        presentation='plain-lines-v1' if plain else 'json-candidates-v1',
        offset_unit='unicode-scalar', candidates=spans,
        document_sha256=hashlib.sha256(encoded).hexdigest(), document_bytes=len(encoded),
        question=case['args'][0], legacy_none_enabled='--none' in case['args'])


def outcome(output, packing):
    """Classify actual command/row dispositions; only an answered null is none."""
    if output.get('harness_error'):
        return dict(status='harness-error', error=output['harness_error'])
    if output.get('parse_error'):
        return dict(status='harness-error', error='invalid command row JSON')
    code, rows = output['exit'], output.get('rows', [])
    if not isinstance(rows, list):
        return dict(status='harness-error', error='expected a typed row list')
    if not rows:
        return dict(status='call-failed' if code else 'missing')
    if len(rows) != 1 or not isinstance(rows[0], dict):
        return dict(status='harness-error', error='expected one typed row')
    row = rows[0]
    if row.get('function') != 'find' or type(row.get('id')) is not type(output['id']) or row.get('id') != output['id'] or row.get('position') != 1:
        return dict(status='harness-error', error='row identity does not match the packed case')
    status = row.get('status')
    if status == 'failed':
        return dict(status='failed', error=row.get('error'))
    if status == 'unsure':
        return dict(status='unsure' if code in (0, 3) else 'call-failed')
    if status != 'answered' or 'answer' not in row:
        return dict(status='harness-error', error='missing typed disposition')
    answer = row['answer']
    if answer is None:
        return dict(status='answered', selection='none') if code in (0, 1) else dict(status='call-failed')
    if code != 0:
        return dict(status='call-failed')
    matches = [s for s in packing['candidates'] if all(answer.get(k) == s[k] for k in ('start', 'end', 'text'))] if isinstance(answer, dict) else []
    if len(matches) != 1:
        return dict(status='harness-error', error='answer does not identify an exact packed candidate span')
    return dict(status='answered', selection='candidate', candidate_id=matches[0]['id'])


def inventory(cases):
    counts = Counter()
    ids = [(type(c['id']), c['id']) for c in cases]
    if len(set(ids)) != len(ids):
        raise ValueError('duplicate case IDs')
    for case in cases:
        record, mapping = pack(case)
        if record['input'].count('\n') + 1 != len(case['records']):
            raise ValueError('candidate count changed')
        counts['cases'] += 1
        counts[case['level']] += 1
        counts['gold_none'] += case['truth'] == 'none'
        counts['multiline_candidates'] += any('\n' in r['input'] or '\r' in r['input'] for r in case['records'])
        counts[mapping['presentation']] += 1
        if case['truth'] != 'none' and not any(type(case['truth']) is type(s['id']) and case['truth'] == s['id'] for s in mapping['candidates']):
            raise ValueError('gold candidate absent')
    return dict(counts)
