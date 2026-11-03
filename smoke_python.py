import importlib.metadata,json,sys
from pathlib import Path
import datapond,datapond.registry as registry,duckdb
def require(ok,message='Python client validation failed'):
    if not ok:raise ValueError(message)
registry.REGISTRY_URL=sys.argv[1]
registry.CACHE_DIR=Path(sys.argv[2]);registry.CACHE_FILE=registry.CACHE_DIR/'registry.json'
probe=duckdb.connect()
try:require(probe.execute("SELECT installed FROM duckdb_extensions() WHERE extension_name='httpfs'").fetchone()[0],'HTTPFS must already be installed')
finally:probe.close()
require(datapond.list()==['ice-287g'],'Unexpected local catalog')
con=datapond.connect('ice-287g',quiet=True)
try:
    con.execute("SET memory_limit='128MiB'");con.execute('SET threads=1');con.execute("SET max_temp_directory_size='0B'")
    require(con.execute('SELECT count(*) FROM agreements').fetchone()[0]==3201)
    require(con.execute('SELECT count(*) FROM agencies').fetchone()[0]==2491)
    require(con.execute('SELECT count(*) FROM _metadata').fetchone()[0]==2)
    require(con.execute('SELECT count(*) FROM _columns').fetchone()[0]==65)
    require(con.execute("SELECT count(*) FROM agreements WHERE ST_AsText(ST_GeomFromWKB(geometry_wkb)) LIKE '%EMPTY'").fetchone()[0]==406)
    require(con.execute("SELECT count(*) FROM agreements WHERE state_fips LIKE '0%'").fetchone()[0]>0)
    require(isinstance(con.execute('SELECT geometry_wkb FROM agreements LIMIT 1').fetchone()[0],bytes))
    example=con.execute('SELECT status,count(*) AS agreements FROM agreements GROUP BY status ORDER BY status').fetchall()
    require(example==[('Active',2725),('Removed',273),('Superseded',203)])
    print(json.dumps({'passed':True,'client':'Python datapond','version':importlib.metadata.version('datapond'),'duckdb':duckdb.__version__,'example':example}))
finally:con.close()
