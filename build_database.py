"""Build a pinned ICE 287(g) agreement snapshot without overwriting files."""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,tempfile,urllib.request
from datetime import datetime,timezone
from pathlib import Path
import duckdb
from datapond_build import ensure_metadata,build_columns_table

ROOT=Path(__file__).resolve().parent
TABLES={'agreements':'One record per agreement; multiple agreements and overlapping scopes per agency are retained','agencies':'One record per agency; geography reflects active or most recently listed agreement'}
CONFIG={'memory_limit':'128MiB','threads':'1','max_temp_directory_size':'0B'}
def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def acquire(source,root=ROOT):
    path=root/source['local_path']
    path.parent.mkdir(parents=True,exist_ok=True)
    if not path.exists():
        part=path.with_suffix(path.suffix+'.part')
        if part.exists():raise FileExistsError(part)
        if source['bytes']>16*1024**2:raise ValueError('Source exceeds this small-dataset download budget')
        if shutil.disk_usage(root).free<1024**3:raise RuntimeError('Less than 1 GiB physical free space')
        received=0
        with urllib.request.urlopen(source['url'],timeout=40) as response,part.open('xb') as out:
            while True:
                block=response.read(min(1024**2,source['bytes']-received+1))
                if not block:break
                received+=len(block)
                if received>source['bytes']:raise ValueError('Source exceeds declared byte size')
                out.write(block)
        if received!=source['bytes'] or digest(part)!=source['expected_full_sha256']:raise ValueError('Source hash or length mismatch')
        # Atomic no-clobber publication, even if another writer created path.
        # Keep the verified part as a hard link for inspection; no extra data copy.
        os.link(part,path)
    if path.stat().st_size!=source['bytes'] or digest(path)!=source['expected_full_sha256']:raise ValueError('Unpinned source')
    return path
def validate(con,expected):
    checks={}
    def check(name,sql,want=0):
        actual=con.execute(sql).fetchone()[0]
        checks[name]={'actual':actual,'expected':want,'passed':actual==want}
        if actual!=want:raise ValueError(f'{name}: {actual} != {want}')
    for table,key in [('agreements','agreement_id'),('agencies','agency_id')]:
        check(table+'_rows',f'SELECT count(*) FROM {table}',expected[table])
        check(table+'_key_nulls',f'SELECT count(*) FROM {table} WHERE {key} IS NULL')
        check(table+'_key_duplicates',f'SELECT count(*) FROM (SELECT {key} FROM {table} GROUP BY 1 HAVING count(*)>1)')
    check('agency_links','SELECT count(*) FROM agreements a LEFT JOIN agencies b USING(agency_id) WHERE b.agency_id IS NULL')
    check('agency_summary_counts',"SELECT count(*) FROM agencies a LEFT JOIN (SELECT agency_id,count(*) n,count(*) FILTER(WHERE status='Active') active FROM agreements GROUP BY 1) b USING(agency_id) WHERE a.n_agreements IS DISTINCT FROM b.n OR a.n_active IS DISTINCT FROM b.active OR a.has_active IS DISTINCT FROM (b.active>0)")
    check('termination_interval_order','SELECT count(*) FROM agreements WHERE last_appeared_date>removed_by_date')
    check('status_domain',"SELECT count(*) FROM agreements WHERE status IS NULL OR status NOT IN ('Active','Removed','Superseded')")
    check('wkb_roundtrip',"SELECT count(*) FROM agreements WHERE geometry_wkb IS NOT NULL AND ST_AsWKB(ST_GeomFromWKB(geometry_wkb))::BLOB<>geometry_wkb")
    return checks
def build(output,root=ROOT):
    root=Path(root);output=Path(output)
    lock=json.loads((root/'source-manifest.json').read_text())
    if output.exists() or Path(str(output)+'.wal').exists() or output.with_suffix('.manifest.json').exists():raise FileExistsError(output)
    if shutil.disk_usage(output.parent).free<1024**3:raise RuntimeError('Less than 1 GiB physical free space')
    sources={Path(s['path']).name:s for s in lock['sources']}
    paths={name:acquire(source,root) for name,source in sources.items()}
    expected={'agreements':sources['agreements-sf.parquet']['rows'],'agencies':sources['agencies.parquet']['rows']}
    # Never open the proposed final path for writing: another worker may create
    # it after the initial existence check. A private directory isolates the build.
    workdir=Path(tempfile.mkdtemp(prefix='.'+output.stem+'-build-',dir=output.parent))
    working_output=workdir/output.name
    con=duckdb.connect(str(working_output),config=CONFIG)
    try:
        con.execute('CREATE TABLE agreements AS SELECT * EXCLUDE(geometry),ST_AsWKB(geometry)::BLOB AS geometry_wkb FROM read_parquet(?)',[str(paths['agreements-sf.parquet'])])
        con.execute('CREATE TABLE agencies AS SELECT * FROM read_parquet(?)',[str(paths['agencies.parquet'])])
        con.execute('CREATE TABLE _provenance(table_name VARCHAR,source_url VARCHAR,source_commit VARCHAR,sha256 VARCHAR,source_bytes BIGINT,acquired_utc VARCHAR,license VARCHAR)')
        for table,file in [('agreements','agreements-sf.parquet'),('agencies','agencies.parquet')]:
            s=sources[file]
            con.execute('INSERT INTO _provenance VALUES (?,?,?,?,?,?,?)',[table,s['url'],s['commit'],s['expected_full_sha256'],s['bytes'],lock['acquired_utc'],lock['data_license']])
        con.execute('CREATE TABLE _geometry_metadata(metadata_key VARCHAR,metadata_value VARCHAR)')
        for _,key,value in con.execute('SELECT * FROM parquet_kv_metadata(?)',[str(paths['agreements-sf.parquet'])]).fetchall():
            con.execute('INSERT INTO _geometry_metadata VALUES (?,?)',[key.decode(),value.decode()])
        # Keep all source fields except the explicitly documented WKB serialization.
        equality=con.execute('''SELECT count(*) FROM (
            (SELECT * FROM agreements EXCEPT ALL SELECT * EXCLUDE(geometry),ST_AsWKB(geometry)::BLOB AS geometry_wkb FROM read_parquet(?))
            UNION ALL (SELECT * EXCLUDE(geometry),ST_AsWKB(geometry)::BLOB AS geometry_wkb FROM read_parquet(?) EXCEPT ALL SELECT * FROM agreements))''',[str(paths['agreements-sf.parquet'])]*2).fetchone()[0]
        if equality:raise ValueError('Agreement content differs from source')
        equality=con.execute('''SELECT count(*) FROM (
            (SELECT * FROM agencies EXCEPT ALL SELECT * FROM read_parquet(?))
            UNION ALL (SELECT * FROM read_parquet(?) EXCEPT ALL SELECT * FROM agencies))''',[str(paths['agencies.parquet'])]*2).fetchone()[0]
        if equality:raise ValueError('Agency content differs from source')
        ensure_metadata(con,tables=list(TABLES),descriptions=TABLES,source_url='https://deportationdata.org/data/processed/ice.html#ice-287g-agreements',license='CC0-1.0')
        build_columns_table(con,tables=list(TABLES),join_hints={'agency_id':'Join agreements to agencies inside this snapshot; repeated agreements are intentional.','agreement_id':'Unique within agreements in this snapshot.','county_fips':'String geography code; preserve leading zeros. Missing or multijurisdictional values need care.','geometry_wkb':'OGC WKB BLOB converted with ST_AsWKB; original CRS/Arrow metadata in _geometry_metadata.'})
        checks=validate(con,expected)
        schemas={table:con.execute(f'DESCRIBE {table}').fetchall() for table in TABLES}
        nulls={table:{col:con.execute(f'SELECT count(*) FILTER(WHERE "{col}" IS NULL) FROM {table}').fetchone()[0] for col,*_ in schemas[table]} for table in TABLES}
        profile={'status_counts':con.execute('SELECT status,count(*) FROM agreements GROUP BY 1 ORDER BY 1').fetchall(),'signed_range':con.execute('SELECT min(signed_date),max(signed_date),max(last_appeared_date) FROM agreements').fetchone(),'empty_geometry':con.execute("SELECT count(*) FROM agreements WHERE ST_AsText(ST_GeomFromWKB(geometry_wkb)) LIKE '%EMPTY'").fetchone()[0]}
        con.execute('CHECKPOINT')
    finally:con.close()
    record={'status':'passed','built_utc':datetime.now(timezone.utc).isoformat(),'source_commit':lock['source_commit'],'source_hashes_verified':True,'config':CONFIG,'duckdb':duckdb.__version__,'tables':expected,'checks':checks,'schemas':schemas,'null_counts':nulls,'profile':profile,'database_bytes':working_output.stat().st_size,'database_sha256':digest(working_output),'output':output.name}
    os.link(working_output,output)
    with output.with_suffix('.manifest.json').open('x') as stream:json.dump(record,stream,indent=2,default=str)
    print(json.dumps({k:v for k,v in record.items() if k not in ['schemas','null_counts','checks']},indent=2,default=str))
    return record
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=ROOT/'ice-287g.duckdb');args=parser.parse_args();build(args.output)
