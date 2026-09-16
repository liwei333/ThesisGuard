"""Independent Phase A only: snapshots, tool preflight, read-only metadata.

No fixture imports, tests, migrations, database deletion or data modification.
All outputs use exclusive creation under this script's evidence directory.
"""
import asyncio
import datetime
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

MAIN = Path('/Users/qianduoduo/Desktop/AI_app/ThesisGuard')
CANDIDATE = Path('/Users/qianduoduo/.config/superpowers/worktrees/ThesisGuard/codex-wp04-02-evidence-domain-service')
OUT = Path(__file__).resolve().parent
DIAGNOSTICS = ['TG_TEST_ADMIN_DATABASE_URL', 'TG_R1C_REPLAY_BASELINE', 'TG_R1C02_REPLAY_PRIOR']

def now():
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def save(name, value):
    with (OUT / name).open('x') as handle:
        json.dump(value, handle, indent=2, ensure_ascii=False, default=str)
        handle.write('\n')

def run(argv, cwd=CANDIDATE, env=None):
    start = now()
    proc = subprocess.run(argv, cwd=cwd, env=env, text=True, capture_output=True, timeout=40)
    return dict(argv=argv, cwd=str(cwd), start=start, end=now(), exit_code=proc.returncode, stdout=proc.stdout, stderr=proc.stderr)

def digest(path):
    data = path.read_bytes()
    return dict(size=len(data), sha256=hashlib.sha256(data).hexdigest())

def snapshot(label):
    result = dict(time=now(), repositories={})
    for label_repo, root in [('main', MAIN), ('candidate', CANDIDATE)]:
        commands = [run(['git', '--no-optional-locks', *args], root) for args in [
            ['status', '--short', '--untracked-files=all'], ['rev-parse', '--abbrev-ref', 'HEAD'],
            ['rev-parse', 'HEAD', 'HEAD^'], ['diff', '--stat'], ['diff', '--cached', '--stat'],
            ['show', '--format=fuller', '--no-patch', 'HEAD'], ['diff-tree', '--no-commit-id', '--name-status', '-r', 'HEAD']]]
        listing = run(['git', '--no-optional-locks', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], root)
        files = {}
        for name in listing['stdout'].split('\0'):
            if not name or (root / name).is_relative_to(OUT):
                continue
            path = root / name
            if path.is_file():
                files[name] = digest(path)
        # Include ignored historical evidence, retaining all old artifacts.
        if root == MAIN:
            for path in (MAIN / 'docs').rglob('*'):
                if path.is_file() and not path.is_relative_to(OUT):
                    files[str(path.relative_to(root))] = digest(path)
        result['repositories'][label_repo] = dict(commands=commands, files=files)
    save(f'phase-a-20260916-{label}-files.json', result)
    print(json.dumps({k: [c['stdout'] for c in v['commands'][:3]] for k,v in result['repositories'].items()}, indent=2))

def environment():
    env = os.environ.copy()
    if any(name in env for name in DIAGNOSTICS):
        raise RuntimeError('Diagnostic variable unexpectedly present; no dependent action allowed')
    expected_path = '/opt/miniconda3/bin:/opt/homebrew/bin:/opt/homebrew/opt/postgresql@16/bin:/usr/bin:/bin:/usr/sbin:/sbin'
    assert env['PATH'] == expected_path
    assert env['PYTHONPATH'] == str(CANDIDATE) + ':/opt/homebrew/lib/python3.12/site-packages'
    assert env['PYTHONDONTWRITEBYTECODE'] == '1'
    paths = dict(python='/opt/homebrew/bin/python3.12', pytest='/opt/homebrew/bin/pytest', alembic='/opt/miniconda3/bin/alembic', ruff='/opt/miniconda3/bin/ruff', mypy='/opt/miniconda3/bin/mypy', psql='/opt/homebrew/opt/postgresql@16/bin/psql')
    results = [run([path, '--version'], env=env) for path in paths.values()]
    child_code = "import os,shutil,sys,json; print(json.dumps({'sys_executable':sys.executable,'PATH':os.environ['PATH'],'PYTHONPATH':os.environ['PYTHONPATH'],'which_alembic':shutil.which('alembic'),'which_pytest':shutil.which('pytest')}))"
    child = run([paths['python'], '-c', child_code], env={**env, 'DATABASE_URL': 'postgresql+asyncpg://unused@127.0.0.1:15432/postgres'})
    # Same subprocess inheritance as original fixture, inspection command only.
    heads = run(['alembic', '-c', 'migrations/alembic.ini', 'heads'], env={**env, 'DATABASE_URL': 'postgresql+asyncpg://unused@127.0.0.1:15432/postgres'})
    libs = {name: importlib.metadata.version(name) for name in ['pytest','pytest-asyncio','asyncpg','SQLAlchemy','boto3']}
    save('phase-a-20260916-effective-environment.json', dict(time=now(), effective_environment={k: env.get(k) for k in ['PATH','PYTHONPATH','PYTHONDONTWRITEBYTECODE']}, diagnostic_variables_unset={k:k not in env for k in DIAGNOSTICS}, paths={k:dict(path=v,realpath=str(Path(v).resolve()),fingerprint=digest(Path(v)),shebang=Path(v).read_bytes().split(b'\n')[0].decode(errors='replace') if k not in ['python','ruff','psql'] else None) for k,v in paths.items()}, sys_executable=sys.executable, libraries=libs, versions=results, child_discovery=child, heads=heads, approval_environment='normal require_escalated exec_command; login=false; command-local PATH', future_test_argv=['/opt/homebrew/bin/pytest','-p','no:cacheprovider','-q','tests/test_evidence_services.py','-k','r1c05c01','-rs'], future_tests_executed=False))
    print(json.dumps(dict(versions=[r['stdout'].strip() or r['stderr'].strip() for r in results], child=child, heads=heads), indent=2))
    assert all(r['exit_code']==0 for r in results+[child,heads])
    assert json.loads(child['stdout'])['which_alembic']==paths['alembic']
    assert heads['stdout'].strip()=='000000000004 (head)'

async def databases():
    import asyncpg
    old = json.loads((MAIN/'docs/acceptance/TASK-WP04-02-R1C-05C-01-independent-db-inventory.json').read_text())
    assert len(old['names']) == 45 and len(set(old['names'])) == 45
    events=[]
    async def connect(name):
        return await asyncpg.connect(user='thesisguard', password='thesisguard_dev_password', host='127.0.0.1', port=15432, database=name, timeout=8, command_timeout=15, server_settings={'default_transaction_read_only':'on', 'application_name':'TG_INDEPENDENT_REVERIFY_R1_PHASE_A'})
    async def fetch(conn, sql, *params):
        start=now()
        try:
            rows=[dict(r) for r in await conn.fetch(sql, *params)]
            events.append(dict(start=start,end=now(),database=conn.get_settings().database if hasattr(conn.get_settings(),'database') else None,sql=sql,parameters=params,result=rows))
            return rows
        except Exception as exc:
            events.append(dict(start=start,end=now(),sql=sql,parameters=params,error=repr(exc)))
            raise
    admin=await connect('postgres')
    catalog_sql="SELECT d.oid,d.datname,pg_get_userbyid(d.datdba) AS owner,d.datistemplate,d.datallowconn,d.datconnlimit,d.datacl::text,shobj_description(d.oid,'pg_database') AS comment,pg_database_size(d.oid) AS size_bytes FROM pg_database d ORDER BY d.datname"
    before=await fetch(admin,catalog_sql)
    save('phase-a-20260916-before-databases.json',dict(time=now(),host='127.0.0.1',port=15432,databases=before))
    server=await fetch(admin,"SELECT version(),inet_server_addr()::text AS address,inet_server_port() AS internal_port,current_user,pg_postmaster_start_time() AS postmaster_start,current_setting('transaction_read_only') AS transaction_read_only")
    settings=await fetch(admin,"SELECT name,setting FROM pg_settings WHERE name IN ('logging_collector','log_destination','log_directory','log_filename','log_statement','log_min_duration_statement') ORDER BY name")
    roles=await fetch(admin,"SELECT rolname,rolsuper,rolcreatedb,rolcanlogin FROM pg_roles WHERE rolname=current_user")
    activities_sql="SELECT datname,pid,usename,application_name,client_addr::text,backend_start,xact_start,query_start,state,wait_event_type,wait_event,backend_type FROM pg_stat_activity WHERE datname=ANY($1::text[]) AND pid<>pg_backend_pid() ORDER BY datname,pid"
    initial_activity=await fetch(admin,activities_sql,old['names'])
    log_diagnostic={}
    if any(r['name']=='logging_collector' and r['setting']=='on' for r in settings):
        try:
            log_diagnostic['directory']=await fetch(admin,"SELECT name,size,modification FROM pg_ls_logdir() ORDER BY modification DESC LIMIT 10")
        except Exception as exc:
            log_diagnostic['error']=repr(exc)
    else:
        log_diagnostic['unavailable_reason']='logging_collector off; no PostgreSQL collector log directory is available for exact CREATE DATABASE attribution; no container or substitute log access attempted'
    rows=[]
    by_name={r['datname']:r for r in before}
    for name in old['names']:
        item=dict(name=name,catalog=by_name.get(name),observed_at=now(),connections_before=[r for r in initial_activity if r['datname']==name],ownership='UNKNOWN',cleanup_target=False,attribution_reason='No pre-failed-run snapshot or exact-name CREATE DATABASE/run mapping; role ownership, UUID prefix, counts, catalog OID order, emptiness and time alone do not establish failed-verifier ownership.')
        conn=None
        try:
            conn=await connect(name)
            item['metadata']=await fetch(conn,"SELECT current_database() AS database,current_user,current_setting('transaction_read_only') AS transaction_read_only,(SELECT count(*) FROM pg_largeobject_metadata) AS large_object_count")
            item['schemas']=await fetch(conn,"SELECT nspname,pg_get_userbyid(nspowner) AS owner,obj_description(oid,'pg_namespace') AS comment FROM pg_namespace WHERE nspname NOT LIKE 'pg_%' AND nspname<>'information_schema' ORDER BY nspname")
            item['extensions']=await fetch(conn,"SELECT extname,extversion FROM pg_extension ORDER BY extname")
            item['relations']=await fetch(conn,"SELECT n.nspname,c.relname,c.relkind,pg_get_userbyid(c.relowner) AS owner,c.reltuples,pg_total_relation_size(c.oid) AS total_bytes,obj_description(c.oid,'pg_class') AS comment FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace WHERE n.nspname NOT LIKE 'pg_%' AND n.nspname<>'information_schema' ORDER BY n.nspname,c.relname")
            item['routines']=await fetch(conn,"SELECT n.nspname,p.proname,p.prokind FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace WHERE n.nspname NOT LIKE 'pg_%' AND n.nspname<>'information_schema' ORDER BY n.nspname,p.proname")
            item['row_counts']=[]
            for relation in item['relations']:
                if relation['relkind'] in ['r','p','m']:
                    schema='"'+relation['nspname'].replace('"','""')+'"'
                    table='"'+relation['relname'].replace('"','""')+'"'
                    count=await fetch(conn,f'SELECT count(*) AS row_count FROM {schema}.{table}')
                    item['row_counts'].append(dict(schema=relation['nspname'],table=relation['relname'],**count[0]))
            if any(r['relname']=='alembic_version' and r['nspname']=='public' and r['relkind']=='r' for r in item['relations']):
                item['alembic_versions']=await fetch(conn,'SELECT version_num FROM public.alembic_version ORDER BY version_num')
            item['connect_result']='SUCCESS'
            item['content_classification']='NO_USER_RELATIONS_OR_ROUTINES_OR_LARGE_OBJECTS' if not item['relations'] and not item['routines'] and item['metadata'][0]['large_object_count']==0 else 'USER_OBJECTS_PRESENT'
        except Exception as exc:
            item['connect_or_metadata_error']=repr(exc)
            item['connect_result']='ERROR'
            item['content_classification']='UNKNOWN'
        finally:
            if conn:
                await conn.close()
        rows.append(item)
        print(name,item['connect_result'],item['content_classification'],item['ownership'],flush=True)
    final_activity=await fetch(admin,activities_sql,old['names'])
    after=await fetch(admin,catalog_sql)
    await admin.close()
    for item in rows:
        item['connections_after']=[r for r in final_activity if r['datname']==item['name']]
    save('phase-a-20260916-per-database-evidence.json',dict(time=now(),server=server,roles=roles,logging=settings,log_attribution=log_diagnostic,databases=rows,confirmed_cleanup_names=[],unknown_names=old['names'],cleanup_authorized=False))
    save('phase-a-20260916-after-databases.json',dict(time=now(),host='127.0.0.1',port=15432,databases=after,added_names=sorted(set(r['datname'] for r in after)-set(by_name)),removed_names=sorted(set(by_name)-set(r['datname'] for r in after))))
    save('phase-a-20260916-readonly-query-log.json',events)

async def directories():
    import asyncpg
    names=json.loads((MAIN/'docs/acceptance/TASK-WP04-02-R1C-05C-01-independent-db-inventory.json').read_text())['names']
    conn=await asyncpg.connect(user='thesisguard',password='thesisguard_dev_password',host='127.0.0.1',port=15432,database='postgres',timeout=8,command_timeout=15,server_settings={'default_transaction_read_only':'on','application_name':'TG_INDEPENDENT_REVERIFY_R1_PHASE_A'})
    results=[]
    queries=[("SELECT current_setting('transaction_read_only') AS readonly,pg_current_logfile() AS current_logfile",[]),
             ("SELECT name,size,modification FROM pg_ls_logdir() ORDER BY modification DESC LIMIT 10",[]),
             ("SELECT d.datname,d.oid,s.size,s.access,s.modification,s.change,s.creation,s.isdir FROM pg_database d CROSS JOIN LATERAL pg_stat_file(format('base/%s',d.oid),true) s WHERE d.datname=ANY($1::text[]) ORDER BY d.datname",[names])]
    for sql,params in queries:
        start=now()
        try:
            rows=[dict(r) for r in await conn.fetch(sql,*params)]
            results.append(dict(start=start,end=now(),sql=sql,parameters=params,rows=rows))
        except Exception as exc:
            results.append(dict(start=start,end=now(),sql=sql,parameters=params,error=repr(exc)))
    await conn.close()
    save('phase-a-20260916-directory-metadata.json',dict(time=now(),host='127.0.0.1',port=15432,results=results,interpretation='Directory change/modification are not database creation time or run ownership proof. PostgreSQL catalog has no database creation timestamp. No file contents or container logs read.'))
    print(json.dumps(results,indent=2,default=str))

async def cache_metadata():
    import asyncpg
    names=json.loads((MAIN/'docs/acceptance/TASK-WP04-02-R1C-05C-01-independent-db-inventory.json').read_text())['names']
    conn=await asyncpg.connect(user='thesisguard',password='thesisguard_dev_password',host='127.0.0.1',port=15432,database='postgres',timeout=8,command_timeout=15,server_settings={'default_transaction_read_only':'on','application_name':'TG_INDEPENDENT_REVERIFY_R1_PHASE_A'})
    sql="SELECT d.datname,d.oid,s.size,s.modification,s.change,s.creation,s.isdir FROM pg_database d CROSS JOIN LATERAL pg_stat_file(format('base/%s/pg_internal.init',d.oid),true) s WHERE d.datname=ANY($1::text[]) ORDER BY d.datname"
    start=now()
    rows=[dict(r) for r in await conn.fetch(sql,names)]
    await conn.close()
    save('phase-a-20260916-cache-file-metadata.json',dict(start=start,end=now(),host='127.0.0.1',port=15432,sql=sql,parameters=[names],rows=rows,interpretation='Physical size delta equals observed pg_internal.init size in each database; cache initialization is an inference. File contents were not read; no baseline file-level inventory exists. SQL read-only does not guarantee byte-identical physical storage.'))
    print(json.dumps(dict(count=len(rows),sizes=sorted(set(r['size'] for r in rows))),indent=2))

if __name__=='__main__':
    if sys.argv[1] in ['before','after']:
        snapshot(sys.argv[1])
    elif sys.argv[1]=='environment':
        environment()
    elif sys.argv[1]=='databases':
        asyncio.run(databases())
    elif sys.argv[1]=='directories':
        asyncio.run(directories())
    elif sys.argv[1]=='cache-metadata':
        asyncio.run(cache_metadata())
    else:
        raise RuntimeError('Unsupported mode')
