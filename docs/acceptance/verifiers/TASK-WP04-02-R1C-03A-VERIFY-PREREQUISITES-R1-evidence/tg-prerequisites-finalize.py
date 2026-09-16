import os,json,hashlib,pathlib,subprocess,datetime,re
MAIN=pathlib.Path('/Users/qianduoduo/Desktop/AI_app/ThesisGuard')
CAND=pathlib.Path('/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service')
OUT=MAIN/'docs/acceptance/verifiers/TASK-WP04-02-R1C-03A-VERIFY-PREREQUISITES-R1-evidence'
REPORT=MAIN/'docs/acceptance/TASK-WP04-02-R1C-03A-VERIFY-PREREQUISITES-R1-execution-report.md'
sha=lambda b:hashlib.sha256(b).hexdigest()
commands=json.loads((OUT/'command-results.json').read_text())
static=json.loads((OUT/'static-command-results.json').read_text())
for record in static:
 if record['name'] not in {r['name'] for r in commands}:commands.append(record)
commands.sort(key=lambda x:x['start'])
for r in commands:assert sha(pathlib.Path(r['log']).read_bytes())==r['log_sha256'],r['name']
(OUT/'command-results.json').write_text(json.dumps(commands,indent=2)+'\n')
def logged(name,args,cwd):
 start=datetime.datetime.now(datetime.timezone.utc).isoformat()
 p=subprocess.run(args,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
 log=OUT/(name+'.log');log.write_bytes(p.stdout)
 commands.append(dict(name=name,argv=args,cwd=str(cwd),start=start,end=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=p.returncode,log=str(log),log_sha256=sha(p.stdout)))
 (OUT/'command-results.json').write_text(json.dumps(commands,indent=2)+'\n')
 assert p.returncode==0,(name,p.stdout)
 return p.stdout.decode()
def snap(label,root):
 status=logged(label+'-status',['git','status','--short','--branch','--untracked-files=all'],root)
 branch=logged(label+'-branch',['git','branch','--show-current'],root)
 head=logged(label+'-head-parent',['git','rev-parse','HEAD','HEAD^'],root)
 diff=subprocess.run(['git','diff','--binary'],cwd=root,check=True,stdout=subprocess.PIPE).stdout
 logged(label+'-diff-check',['git','diff','--check'],root)
 return dict(status=status,branch=branch,head_parent=head,diff=dict(sha256=sha(diff),bytes=len(diff)),candidate_file_hashes={n:sha((CAND/n).read_bytes()) for n in ['backend/evidence/errors.py','backend/evidence/services.py','tests/test_evidence_services.py']})
results=dict(timestamp_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),candidate=snap('candidate-final',CAND),main=snap('main-final',MAIN))
before=json.loads((OUT/'before-snapshots.json').read_text())
assert results['candidate']==before['candidate'],'Candidate drift'
for key in ['branch','head_parent','diff']:assert results['main'][key]==before['main'][key],key
recovery=json.loads((OUT/'recovery-manifest.json').read_text())
paths=[str(CAND/n) for n in ['backend/evidence/errors.py','backend/evidence/services.py','tests/test_evidence_services.py']]
for a in recovery['artifacts']:
 for n in [a['restored_path'],a['durable_copy']]:
  assert sha(pathlib.Path(n).read_bytes())==a['expected_sha256'],n
  paths.append(n)
logged('final-fixed-hashes',['shasum','-a','256',*paths],CAND)
(OUT/'after-snapshots.json').write_text(json.dumps(results,indent=2)+'\n')
byname={r['name']:r for r in commands}
targets=['fresh-focused','fresh-r1c02','fresh-r1c01','fresh-r1b-wiring','fresh-r1b-reverify','fresh-r1a','fresh-full-services','fresh-regression']
summary=[]
for name in targets+['owned-boundary']:
 r=byname[name];content=pathlib.Path(r['log']).read_text()
 last=[x.strip(' =') for x in content.splitlines() if re.search(r'\d+ (passed|failed|skipped|error)',x)][-1]
 if name in targets:
  assert r['exit_code']==0,name
  assert not re.search(r'\d+ (failed|skipped|error)',last),(name,last)
 summary.append(dict(name=name,result=last,exit_code=r['exit_code'],log=r['log']))
(OUT/'test-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
source_exports={}
for a in recovery['artifacts']:
 for rec in a['source_record_lines']:
  path=rec['export'];source_exports[path]=sha(pathlib.Path(path).read_bytes())
(OUT/'source-export-hashes.json').write_text(json.dumps(source_exports,indent=2)+'\n')
table='\n'.join('| '+x['name']+' | '+x['result']+' | '+str(x['exit_code'])+' |' for x in summary)
artifactrows='\n'.join('| '+a['filename']+' | `'+a['actual_sha256']+'` |' for a in recovery['artifacts'])
text=f'''# TASK-WP04-02-R1C-03A-VERIFY-PREREQUISITES-R1 execution evidence

STATUS: BLOCKED

Role: prerequisite recovery executor and evidence collector. This report does not issue independent acceptance. The candidate and five original verifiers were preserved. Required original matrix completed; supplemental verifier has unresolved failures and must be reviewed separately. No business implementation repair or expectation adjustment was made.

## Fixed candidate and preservation

Before and after branch `codex/wp04-02-evidence-domain-service`, HEAD `bdd70edc153b6ed5def65ed99c41f325df45f066`, parent `f7c50ab6cbfb0a737f01fa77d565a76ba77cb6af`. Exact dirty state remains services.py and tests/test_evidence_services.py modified. Binary cumulative diff is 60912 bytes, SHA-256 `87191ad61bb565553ac89431386a5c029f10da630f3c60ec71e209576d2f00f8` before/after. Three candidate hashes match the recovery contract:

- errors.py: `3cf37eb3efbf4c7bf7ab3d4213e4ce9865f2b9209fdbeb3d6c267fe84b06d1ec`
- services.py: `43b548232df4267f377c5e144222c9278c3cc478f6800720240c4618b689ebe3`
- tests/test_evidence_services.py: `47ff645c0f782af67e9f6ee64520105febdb28c6547a43bf89b435bead6c5108`

Main remains `7d3734bc8346c16f9bbf7f7d9806309949c996de`, parent `6e1d38e79035bfb6cd36964a16a289f8cd332eb8`, branch main, empty tracked diff. All 14 initial untracked documentation paths preserved. Relative to the earlier acceptance's 12-file snapshot, TASK-MD00-CONTRACT-R1 acceptance/contract were already present at this task start; no incorporation. Only new recovery/evidence files under docs/acceptance were added. No Git mutation or candidate edits.

## Original recovery

Complete raw task export Add File bodies and exact subsequent original patch sections were mechanically materialized in memory; no historical command executed, no logical reconstruction from summaries, no reformatted originals. All five fixed /tmp paths were absent and restored only after all expected hashes matched and no existing conflicts were found. Identical bytes archived under docs/acceptance/verifiers/.

| Original artifact | SHA-256 in /tmp and durable archive |
|---|---|
{artifactrows}

Sources: rollout-2026-09-14T17-50-45-01a09f53-8329-7303-a582-0e477073f77e.jsonl and rollout-2026-09-14T18-50-00-01a09f89-c36c-7403-b3b5-fe2be965523e.jsonl in known local Codex task exports. recovery-manifest.json records exact export paths, line numbers and raw record hashes; five source-records.json files retain complete source/patch sections. source-export-hashes.json records current whole-export hashes. Recovery script preserved as tg-wp04-02-prerequisites-recover.py. Archive whitespace check found no trailing whitespace and all originals end with newline; no original bytes changed.

## Existing local PostgreSQL and permissions

Initial listener absent, Docker desktop-linux socket absent, daemon off. Existing Docker.app and existing Docker.raw disk were identified; project compose specified the original container/port/named volume. Exact container mount metadata was unavailable while daemon was offline. Normal require_escalated approval allowed `/usr/local/bin/docker desktop start --timeout 60`, exit0. The existing engine resumed existing unless-stopped containers automatically, including other local projects. No compose up/create/start, replacement container, host/port change, volume reset/deletion or business migration was issued.

Actual restored container ID `6684af51cd5a403090647d495967c019f50b5ae33898da24f89ad143d46f2a2f`, name thesisguard-postgres, image pgvector/pgvector:pg17, created 2026-09-12T13:10:02.651706346Z. Compose project thesisguard, config original main docker-compose.yml. Host15432 maps container5432. Existing volume thesisguard-postgres-data created 2026-09-12T12:13:59Z, local driver, original /var/lib/postgresql/data mount. PostgreSQL17.11 accepts connections. Fixture default route remains 127.0.0.1:15432/postgres. All successful DB commands used normal require_escalated approval, existing fixture random disposable DB creation/migrations/precise teardown only. No setup/cleanup errors or Research skips in the fresh original matrix. No automatic approval-review rejection occurred. prerequisite-events.json also discloses sandbox-only diagnosis limitations and a read-only query of a wrong project-prefixed volume name; actual Mounts identified the correct existing volume without creation.

## Actual runtime and command results

Existing `/opt/miniconda3/bin/` tools: Python3.12.9, pytest9.1.1, Ruff0.16.1, mypy2.3.0, Alembic1.18.5. Docker29.7.2/Desktop4.90.0. Main runtime libraries: pytest-asyncio1.4.0, asyncpg0.31.0, SQLAlchemy2.0.48, FastAPI0.135.1, Pydantic2.12.5, httpx0.28.1. First focused attempt exited4 during conftest import, missing boto3; no business assertion ran and this is not RED. Existing Homebrew Python3.12 packages supplied boto3/botocore1.43.93 and s3transfer0.19.2 as fallback. Application import then exited0. No dependency installation/upgrade.

Fresh DB environment: PATH starts /opt/miniconda3/bin; PYTHONDONTWRITEBYTECODE=1; PYTHONPATH is candidate absolute directory, then existing Miniconda3.12 primary site-packages, then existing Homebrew3.12 fallback site-packages. This recorded path extension resolves missing installed dependency only; no stub, production injection or DB redirect. pytest and Alembic fixture subprocess share primary runtime. Static checks used native Miniconda without fallback, same primary versions. effective-runtime.json gives every actual module source; runtime-resolution.json gives executable resolution. TG_TEST_ADMIN_DATABASE_URL, TG_R1C_REPLAY_BASELINE and TG_R1C02_REPLAY_PRIOR are absent; new boundary environment test confirms absence.

Every matrix argv, cwd, relevant nonsecret environment, start/end, exit and complete log SHA is in command-results.json; tg-prerequisites-run.py preserves the executed runner. Static records merged by command name from static-command-results.json after concurrent independent static/runtime execution, with recorded log hashes validated. Complete output files, including failure outputs, are preserved.

| Fresh target | Actual summary | Exit |
|---|---|---|
{table}

Ruff check --no-cache, Ruff format --check --no-cache: exit0, 3 original files. MYPYPATH=. mypy --explicit-package-bases --ignore-missing-imports --cache-dir=/tmp/tg-r1c-03a-mypy: exit0, no issues in3 source files; unused external-module configuration note only. PYTHONPYCACHEPREFIX=/tmp/tg-r1c-03a-pycache Python compileall -q: exit0. Alembic -c migrations/alembic.ini heads: exit0, 000000000004(head). Final candidate/main diff-check, status, branch, HEAD/parent and all3+10 fixed hashes: exit0, unchanged.

Chronological original R1C-03A RED and old executor GREEN are historical inputs only. This task did not reset/reconstruct the pre-fix candidate or set prior-behavior diagnostics. New import failure is setup evidence, and supplemental assertion failures are reported below rather than relabeled as original business RED.

## Boundary evidence and unresolved supplemental oracle

Candidate focused/full tests include 75 rejection cases across revise same-series, revise automatic replacement, direct replacement, underlying create initial and underlying create replacement; 8 ordinary omitted/None cases across four correction routes; 4 ordinary replay/new-trusted-request cases. Rejection cases commit after the domain error and use fresh sessions to compare seven table counts plus full prior exact version/children and series columns. Ordinary cases preserve legacy rule, exact historical children, replacement routing, full CORRECTION tuple, legitimate review and current-valid behavior. Five restored independent verifiers preserve current-valid/lifecycle/R1A/R1B/routing/idempotency/rollback coverage.

New verifier-owned test_wp04_02_r1c03a_prerequisites_boundary_20260916.py independently calls public entrypoints and compares all columns of all rows in nine persistence tables, sharing only the candidate disposable fixture/constraint-legal legacy seed. It is explicitly new provenance, not a restored original and not independent acceptance of the executor's work. It produced 43 passed/15 failed, exit1. The existing tests and originals were not changed afterward.

- 11 automatic-route nodes fail at line80 before the service call: assertion that the support row must have supersedes_evidence_version_id. Actual shared legacy support is an initial FACT version with None, so this is a new verifier request-construction assumption failure, not demonstrated business rejection failure.
- 4 ordinary direct/underlying-replacement nodes (omitted and None each) fail at line262 after caller commit/fresh-session exact/history/no-inheritance/CORRECTION tuple/routing/children assertions succeeded. Expected audit event_type EVIDENCE_CORRECTION; actual EVIDENCE_VERSION_CREATED. Frozen contract's audit event schema allows generic Created/etc.; it specifies CORRECTION in status_change_kind with four fields, not this event_type literal. No candidate defect is inferred from this ungrounded oracle expectation. Actor/time assertions after the failing event_type were not reached.

Exact15 nodes and classifications are in supplemental-findings.json; complete stacks in owned-boundary.log. Supplemental all-entry coverage remains incomplete for automatic routing, and audit-event interpretation unresolved. The original matrix is complete, but execution cannot silently replace the failed oracle, change expectations, or declare independent acceptance. Independent verifier/dispatcher must review these new oracle assumptions and, if necessary, separately authorize a corrected verifier contract. No repair to candidate implementation is authorized by this report.

## Achieved and missing

AC1 preservation, AC2 exact-original restoration, AC3 existing endpoint/runtime recovery and original AC4 matrix execution have fresh evidence. AC5 commands/logs/provenance/snapshots are durably collected. Supplemental boundary oracle has unresolved failures; complete separate independent R1C-03A acceptance is missing. Required L1/L2/L3/L4 artifacts are supplied for independent review, not self-approved.

Production approved trusted correction rule set remains empty. Positive trusted registry/semantic validators, initial-import qualification, full ordinary-correction qualification table, R1C-03B, R1D, final WP04-02 independent full acceptance, Evidence API/Research exact references and Agent work remain unfinished and unauthorized by this prerequisite task. No entire R1C/WP04-02 completion is claimed.

New evidence files are individually listed and hashed in evidence-file-manifest.json. Snapshot files before-snapshots.json and after-snapshots.json preserve exact beginning/final candidate and main state. Report status remains BLOCKED pending separate independent oracle review/acceptance.
'''
REPORT.write_text(text)
# Capture final main status again after report creation, without altering candidate.
results['main']['status']=logged('main-final-with-report-status',['git','status','--short','--branch','--untracked-files=all'],MAIN)
(OUT/'after-snapshots.json').write_text(json.dumps(results,indent=2)+'\n')
allpaths=sorted(OUT.glob('*'))+[REPORT]+[pathlib.Path(a['durable_copy']) for a in recovery['artifacts']]+[MAIN/'docs/acceptance/verifiers/test_wp04_02_r1c03a_prerequisites_boundary_20260916.py']
white=[]
for p in allpaths:
 if p.suffix in {'.json','.py','.md'}:
  b=p.read_bytes();trailing=[i for i,l in enumerate(b.splitlines(),1) if l.endswith((b' ',b'\t'))]
  white.append(dict(path=str(p),trailing_whitespace_lines=trailing,ends_with_newline=b.endswith(b'\n')))
  assert not trailing,p
  assert b.endswith(b'\n'),p
(OUT/'new-evidence-whitespace-check.json').write_text(json.dumps(white,indent=2)+'\n')
allpaths=sorted(OUT.glob('*'))+[REPORT]+[pathlib.Path(a['durable_copy']) for a in recovery['artifacts']]+[MAIN/'docs/acceptance/verifiers/test_wp04_02_r1c03a_prerequisites_boundary_20260916.py']
files=[dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in allpaths if p.is_file()]
(OUT/'evidence-file-manifest.json').write_text(json.dumps(dict(note='Manifest excludes itself; all listed files are newly created task evidence.',files=files),indent=2)+'\n')
print('BLOCKED: evidence complete; supplemental verifier unresolved')
print(REPORT)
print(json.dumps(summary,indent=2))
