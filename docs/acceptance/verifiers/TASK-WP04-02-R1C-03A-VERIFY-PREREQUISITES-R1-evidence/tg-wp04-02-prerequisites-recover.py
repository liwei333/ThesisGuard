from pathlib import Path
import hashlib
import json
import re
import subprocess
from datetime import datetime, UTC

TASK = 'TASK-WP04-02-R1C-03A-VERIFY-PREREQUISITES-R1'
MAIN = Path('/Users/qianduoduo/Desktop/AI_app/ThesisGuard')
CANDIDATE = Path('/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service')
EXPORTS = [
    Path('/Users/qianduoduo/.codex/sessions/2026/09/14/rollout-2026-09-14T17-50-45-01a09f53-8329-7303-a582-0e477073f77e.jsonl'),
    Path('/Users/qianduoduo/.codex/sessions/2026/09/14/rollout-2026-09-14T18-50-00-01a09f89-c36c-7403-b3b5-fe2be965523e.jsonl'),
]
EXPECTED = {
    'test_wp04_02_r1b_r1_wiring_20260915.py': '909f50bd902ecd9c0013121681b614fcbc302f718cc7c9d5dc96f6237d106786',
    'test_wp04_02_r1b_reverify.py': '0f7cea4d14735bd165b75d756444259a64483a97e6a338227bc09af806490cc9',
    'test_wp04_02_r1a_verifier.py': '66be45f354d1df34370eedd9811b3bc68cf29852d45027ea576a67975b18ddfe',
    'test_wp04_02_r1c_01_independent_20260915.py': '857914f073c552be98f895a456d2f0ec486452e1c9aed06a87176c6e7fefd48a',
    'test_wp04_02_r1c_02_independent_20260915.py': '64162c0aafc3ad620ee0cab5e4d8d0ed10e6d61ab8dc21322f4364144c442a05',
}
sha = lambda data: hashlib.sha256(data).hexdigest()
states = {}
provenance = {name: [] for name in EXPECTED}


def apply_recorded_hunks(content, lines):
    old_lines = content.splitlines()
    cursor = 0
    index = 0
    while index < len(lines):
        header = lines[index]
        if header == '*** End of File':
            index += 1
            continue
        assert header.startswith('@@'), header
        anchor = header[3:] if header.startswith('@@ ') else ''
        if anchor:
            positions = [i for i in range(cursor, len(old_lines)) if old_lines[i] == anchor]
            assert positions, ('missing recorded anchor', anchor)
            cursor = positions[0] + 1
        index += 1
        hunk = []
        while index < len(lines) and not lines[index].startswith(('@@', '***')):
            hunk.append(lines[index])
            index += 1
        before = [line[1:] for line in hunk if line.startswith((' ', '-'))]
        after = [line[1:] for line in hunk if line.startswith((' ', '+'))]
        assert before, 'No-context original hunk cannot be recovered without guessing'
        positions = [i for i in range(cursor, len(old_lines) - len(before) + 1)
                     if old_lines[i:i + len(before)] == before]
        assert positions, ('missing exact original hunk', before[:2])
        position = positions[0]
        old_lines[position:position + len(before)] = after
        cursor = position + len(after)
    return '\n'.join(old_lines) + '\n'


for export in EXPORTS:
    with export.open('rb') as stream:
        for number, raw_record in enumerate(stream, 1):
            record = json.loads(raw_record)
            payload = record.get('payload', {})
            if payload.get('type') not in ('function_call', 'custom_tool_call'):
                continue
            body = payload.get('arguments', payload.get('input', ''))
            if not isinstance(body, str):
                continue
            patches = []
            if body.startswith('*** Begin Patch'):
                patches.append(body)
            else:
                for literal in re.finditer(r'(?:const patch = |tools\.apply_patch\()((?:"(?:[^"\\]|\\.)*"))', body):
                    patches.append(json.loads(literal.group(1)))
            for patch in patches:
                parts = patch.splitlines()
                for start, line in enumerate(parts):
                    match = re.fullmatch(r'\*\*\* (Add|Update) File: /tmp/(test_wp04_02[^/]+\.py)', line)
                    if not match or match.group(2) not in EXPECTED:
                        continue
                    kind, name = match.groups()
                    end = start + 1
                    while end < len(parts) and not parts[end].startswith(('*** Add File:', '*** Update File:', '*** Delete File:', '*** End Patch')):
                        end += 1
                    section = parts[start + 1:end]
                    if kind == 'Add':
                        assert name not in states, ('duplicate recorded full original', name)
                        assert all(line.startswith('+') for line in section)
                        states[name] = '\n'.join(line[1:] for line in section) + '\n'
                    else:
                        assert name in states, ('recorded update lacks full original', name)
                        states[name] = apply_recorded_hunks(states[name], section)
                    provenance[name].append({
                        'export': str(export), 'line_number': number,
                        'record_timestamp': record.get('timestamp'), 'call_id': payload.get('call_id'),
                        'tool': payload.get('name'), 'record_sha256': sha(raw_record),
                        'original_patch_section': '\n'.join(parts[start:end]) + '\n',
                        'resulting_sha256': sha(states[name].encode()),
                    })

# Validate all full originals before touching any restored or archive path.
for name, expected in EXPECTED.items():
    assert name in states, ('no authoritative full original', name)
    actual = sha(states[name].encode())
    print(name, actual, 'MATCH' if actual == expected else 'MISMATCH', flush=True)
    assert actual == expected, ('fixed hash mismatch', name)
    for target in (Path('/tmp', name), MAIN / 'docs/acceptance/verifiers' / name):
        if target.exists():
            assert target.is_file() and sha(target.read_bytes()) == expected, ('existing file conflict; will not overwrite', str(target))

archive = MAIN / 'docs/acceptance/verifiers'
evidence = archive / (TASK + '-evidence')
assert not evidence.exists(), 'Task evidence path already exists; do not overwrite'
evidence.mkdir(parents=True)

def snapshot(root):
    commands = {}
    for name, args in (
        ('status', ['git', 'status', '--short', '--branch', '--untracked-files=all']),
        ('branch', ['git', 'branch', '--show-current']),
        ('head_parent', ['git', 'rev-parse', 'HEAD', 'HEAD^']),
        ('diff', ['git', 'diff', '--binary']),
    ):
        result = subprocess.run(args, cwd=root, capture_output=True, text=True, check=True)
        commands[name] = result.stdout if name != 'diff' else {'sha256': sha(result.stdout.encode()), 'bytes': len(result.stdout.encode())}
    commands['candidate_file_hashes'] = {name: sha((CANDIDATE / name).read_bytes()) for name in (
        'backend/evidence/errors.py', 'backend/evidence/services.py', 'tests/test_evidence_services.py')}
    return commands

# Initial main status excludes the newly created empty evidence directory.
(evidence / 'before-snapshots.json').write_text(json.dumps({
    'timestamp_utc': datetime.now(UTC).isoformat(),
    'main': snapshot(MAIN), 'candidate': snapshot(CANDIDATE),
}, indent=2) + '\n')
manifest = {'task': TASK, 'timestamp_utc': datetime.now(UTC).isoformat(),
            'method': 'Mechanical materialization of complete original Add File source plus exact subsequent recorded patch sections. No historical command executed; no source rewritten or reformatted.',
            'artifacts': []}
for name, expected in EXPECTED.items():
    data = states[name].encode()
    restored = Path('/tmp', name)
    restored_absent = not restored.exists()
    if restored_absent:
        with restored.open('xb') as output:
            output.write(data)
    destination = archive / name
    if not destination.exists():
        with destination.open('xb') as output:
            output.write(data)
    assert restored.read_bytes() == data == destination.read_bytes()
    source_evidence = evidence / (name + '.source-records.json')
    source_evidence.write_text(json.dumps(provenance[name], ensure_ascii=False, indent=2) + '\n')
    manifest['artifacts'].append({
        'filename': name, 'expected_sha256': expected, 'actual_sha256': sha(data),
        'restored_path': str(restored), 'restored_from_absent_path': restored_absent,
        'durable_copy': str(destination), 'source_records': str(source_evidence),
        'source_record_lines': [{'export': record['export'], 'line_number': record['line_number'], 'record_sha256': record['record_sha256']} for record in provenance[name]],
    })
(evidence / 'recovery-manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
print('Recovered all five exact originals; durable evidence:', evidence)
