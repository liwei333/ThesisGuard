import os, sys, json, subprocess, hashlib, datetime, pathlib, shlex, shutil
ROOT=pathlib.Path('/Users/qianduoduo/Desktop/AI_app/ThesisGuard')
CAND=pathlib.Path('/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service')
OUT=ROOT/'docs/acceptance/verifiers/TASK-WP04-02-R1C-03A-VERIFY-PREREQUISITES-R1-evidence'
ENV=dict(os.environ, PATH='/opt/miniconda3/bin:'+os.environ['PATH'], PYTHONDONTWRITEBYTECODE='1', PYTHONPATH=str(CAND)+':/opt/miniconda3/lib/python3.12/site-packages:/opt/homebrew/lib/python3.12/site-packages')
FORBIDDEN=['TG_TEST_ADMIN_DATABASE_URL','TG_R1C_REPLAY_BASELINE','TG_R1C02_REPLAY_PRIOR']
assert all(x not in ENV for x in FORBIDDEN), 'Required unset variables are present'
MAN=OUT/'command-results.json'
records=json.loads(MAN.read_text()) if MAN.exists() else []
def run(name,args,env=None,cwd=CAND):
    start=datetime.datetime.now(datetime.timezone.utc).isoformat()
    logfile=OUT/(name+'.log')
    assert not logfile.exists(), logfile
    with logfile.open('xb') as f:
        result=subprocess.run(args,cwd=cwd,env=env or ENV,stdout=f,stderr=subprocess.STDOUT)
    data=logfile.read_bytes()
    records=json.loads(MAN.read_text()) if MAN.exists() else []
    records.append(dict(name=name,argv=args,command=shlex.join(args),cwd=str(cwd),environment={k:(env or ENV).get(k) for k in ['PATH','PYTHONDONTWRITEBYTECODE','PYTHONPATH','MYPYPATH','PYTHONPYCACHEPREFIX']},required_unset=FORBIDDEN,start=start,end=datetime.datetime.now(datetime.timezone.utc).isoformat(),exit_code=result.returncode,log=str(logfile),log_sha256=hashlib.sha256(data).hexdigest()))
    MAN.write_text(json.dumps(records,indent=2)+'\n')
    print(name,'exit',result.returncode,flush=True)
    print(data.decode(errors='replace')[-2400:],flush=True)
    return result.returncode
if sys.argv[1]=='identity':
    commands=[('docker-version',['/usr/local/bin/docker','version']),('docker-context',['/usr/local/bin/docker','context','inspect','desktop-linux','--format','{{.Name}} {{.Endpoints.docker.Host}}']),('postgres-inspect',['/usr/local/bin/docker','inspect','thesisguard-postgres','--format','{{json .Id}} {{json .Name}} {{json .Config.Image}} {{json .Created}} {{json .State}} {{json .HostConfig.RestartPolicy}} {{json .HostConfig.PortBindings}} {{json .Mounts}} {{json .Config.Labels}}']),('postgres-volume',['/usr/local/bin/docker','volume','inspect','thesisguard-postgres-data']),('postgres-ready',['/usr/local/bin/docker','exec','thesisguard-postgres','pg_isready','-U','thesisguard','-d','postgres']),('postgres-version',['/usr/local/bin/docker','exec','thesisguard-postgres','postgres','--version'])]
    for name,args in commands:
        if run(name,args):sys.exit(1)
    runtime={name:shutil.which(name,path=ENV['PATH']) for name in ['python','pytest','ruff','mypy','alembic']}
    runtime['required_unset']={name:name not in ENV for name in FORBIDDEN}
    (OUT/'runtime-resolution.json').write_text(json.dumps(runtime,indent=2)+'\n')
    for name in ['python','pytest','ruff','mypy','alembic']:
        if run(name+'-version',[runtime[name],'--version']):sys.exit(1)
    run('runtime-libraries',[runtime['python'],'-c',"import importlib.metadata as m,json; print(json.dumps({n:m.version(n) for n in ['pytest','pytest-asyncio','asyncpg','SQLAlchemy','fastapi','pydantic','httpx','alembic','ruff','mypy']},indent=2))"])
    sys.exit(0)
if sys.argv[1]=='matrix':
    targets=[('focused',['tests/test_evidence_services.py','-k','r1c or trusted or current_valid or lifecycle or state_transition']),('r1c02',['/tmp/test_wp04_02_r1c_02_independent_20260915.py']),('r1c01',['/tmp/test_wp04_02_r1c_01_independent_20260915.py']),('r1b-wiring',['/tmp/test_wp04_02_r1b_r1_wiring_20260915.py']),('r1b-reverify',['/tmp/test_wp04_02_r1b_reverify.py']),('r1a',['/tmp/test_wp04_02_r1a_verifier.py']),('full-services',['tests/test_evidence_services.py']),('regression',['tests/test_evidence_persistence.py','tests/test_migrations.py','tests/test_evidence_migrations.py','tests/test_research_api.py','tests/test_research_persistence.py'])]
    for name,target in targets:
        if run('fresh-'+name,['/opt/miniconda3/bin/pytest','-p','no:cacheprovider','-q',*target,'-rs']):sys.exit(1)
    sys.exit(0)
if sys.argv[1]=='static':
    files=['backend/evidence/errors.py','backend/evidence/services.py','tests/test_evidence_services.py']
    checks=[('ruff',['/opt/miniconda3/bin/ruff','check','--no-cache',*files],ENV),('format',['/opt/miniconda3/bin/ruff','format','--check','--no-cache',*files],ENV),('mypy',['/opt/miniconda3/bin/mypy','--explicit-package-bases','--ignore-missing-imports','--cache-dir=/tmp/tg-r1c-03a-mypy',*files],dict(ENV,MYPYPATH='.')),('compileall',['/opt/miniconda3/bin/python','-m','compileall','-q',*files],dict(ENV,PYTHONPYCACHEPREFIX='/tmp/tg-r1c-03a-pycache')),('alembic-heads',['/opt/miniconda3/bin/alembic','-c','migrations/alembic.ini','heads'],ENV)]
    codes=[run(name,args,env) for name,args,env in checks]
    sys.exit(any(codes))
if sys.argv[1]=='boundary':
    target=str(ROOT/'docs/acceptance/verifiers/test_wp04_02_r1c03a_prerequisites_boundary_20260916.py')
    sys.exit(run('owned-boundary',['/opt/miniconda3/bin/pytest','-p','no:cacheprovider','-q',target,'-rs']))
