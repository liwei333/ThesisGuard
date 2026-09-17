"""Close an interrupted preflight from retained evidence; never execute tests or DB I/O."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
MAIN = ROOT.parents[2]
CANDIDATE = Path('/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service')

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def git(cwd, *args):
    result = subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True)
    return {'argv': ['git', *args], 'cwd': str(cwd), 'exit_code': result.returncode,
            'stdout': result.stdout, 'stderr': result.stderr}

def save(name, value):
    path = ROOT / name
    with path.open('x') as output:
        json.dump(value, output, ensure_ascii=False, indent=2)
        output.write('\n')

before = json.loads((ROOT / 'before.json').read_text())
records = [json.loads(line) for line in (ROOT / 'execution.log').read_text().splitlines()]
collect = next(record for record in records if record['label'] == 'collect-only')
nodes = ['tests/test_evidence_services.py::' + name
         for name in re.findall(r'^\s*<Coroutine (test_r1c05c01_[^\n]+)>$', collect['stdout'], re.M)]
distribution = {name: sum(name in node for node in nodes) for name in [
    'forbidden_status_commit_fresh_no_residue', 'allowed_routing_history_audit',
    'committed_exact_replay_read_only', 'legacy_forbidden_prior_committed_replay']}
assert len(nodes) == len(set(nodes)) == 41
assert list(distribution.values()) == [20, 16, 3, 2]
assert (ROOT / 'resources.jsonl').stat().st_size == 0
save('collected-nodeids.json', {'source': 'retained collect-only stdout; post-stop evidence extraction',
     'count': len(nodes), 'distribution': distribution, 'nodeids': nodes})
for record in records:
    for stream in ['stdout', 'stderr']:
        assert hashlib.sha256(record[stream].encode()).hexdigest() == record[stream + '_sha256']
        with (ROOT / (record['label'] + '.' + stream + '.txt')).open('x') as output:
            output.write(record[stream])
candidate_commands = [git(CANDIDATE, 'rev-parse', 'HEAD'), git(CANDIDATE, 'rev-parse', 'HEAD^'),
                      git(CANDIDATE, 'branch', '--show-current'), git(CANDIDATE, 'status', '--porcelain')]
candidate_hashes = {name: digest(CANDIDATE / name) for name in before['fixed_candidate_hashes_expected']}
main_commands = [git(MAIN, 'rev-parse', 'HEAD'), git(MAIN, 'status', '--porcelain'),
                 git(MAIN, 'diff', '--name-status'), git(MAIN, 'diff', '--cached', '--name-status'),
                 git(MAIN, 'diff', '--name-status', before['main_gate']['anchor'], 'HEAD'),
                 git(MAIN, 'merge-base', '--is-ancestor', before['main_gate']['anchor'], 'HEAD')]
main_hashes = {name: digest(MAIN / name) for name in before['pinned_main_hashes_expected']}
save('after.json', {
    'task_id': before['task_id'], 'run_id': before['run_id'], 'ended_at': datetime.now(timezone.utc).isoformat(),
    'verdict': 'BLOCKED', 'stop_cause': 'Verifier collect parser expected flat nodeids but pytest emitted a Coroutine tree; original helper exited 1 before real execution.',
    'real_pytest_invocations': 0, 'real_test_count': 0, 'create_sent': 0, 'create_budget': 41,
    'dropped': 0, 'new_resources': [], 'new_resource_release': 'NOT_APPLICABLE: no CREATE attempt',
    'catalog_before': None, 'catalog_after': None,
    'catalog_evidence_gap': 'Full catalog identities are absent from retained artifacts; no equality or historical identity-preservation claim is made.',
    'historical_unknown_operations': 'No per-database connection, termination, rename or DROP in retained command records; no resource events.',
    'original_helper_source': {'path': '/private/tmp/tg_wp04_02_r1c_05c_01_focused_db_reverify_r3_runner.py',
        'recorded_sha256': before['helper_source_sha256'], 'available': False},
    'candidate_commands': candidate_commands, 'candidate_hashes': candidate_hashes,
    'candidate_hash_match': candidate_hashes == before['fixed_candidate_hashes_expected'],
    'main_commands': main_commands, 'main_hashes': main_hashes,
    'main_hash_match': main_hashes == before['pinned_main_hashes_expected'],
    'post_stop_actions': 'Read-only Git/hash review and evidence extraction only; no retry, test invocation or DB operation.'})
artifacts = {path.name: {'bytes': path.stat().st_size, 'sha256': digest(path)}
             for path in sorted(ROOT.iterdir()) if path.is_file() and path.name != 'manifest.json'}
save('manifest.json', {'task_id': before['task_id'], 'run_id': before['run_id'],
     'verdict': 'BLOCKED', 'artifacts': artifacts, 'self_hash_excluded': True,
     'original_helper_source_sha256_unverified': before['helper_source_sha256'],
     'closure_helper_source': 'close-evidence.py'})
manifest = json.loads((ROOT / 'manifest.json').read_text())
for name, metadata in manifest['artifacts'].items():
    assert (ROOT / name).stat().st_size == metadata['bytes']
    assert digest(ROOT / name) == metadata['sha256']
for path in ROOT.glob('*.json'):
    json.loads(path.read_text())
print(json.dumps({'verdict': 'BLOCKED', 'collected': len(nodes), 'distribution': distribution,
                 'real_tests': 0, 'create_sent': 0, 'manifest_valid': True}))
