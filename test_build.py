import hashlib,json
from pathlib import Path
import duckdb,unittest,tempfile
from contextlib import contextmanager
from build_database import acquire,build,validate

def test_rejects_wrong_source_hash(tmp_path):
    raw=tmp_path/'input';raw.write_bytes(b'changed upstream bytes')
    source={'local_path':'input','bytes':raw.stat().st_size,'expected_full_sha256':hashlib.sha256(b'expected').hexdigest()}
    with unittest.TestCase().assertRaisesRegex(ValueError,'Unpinned source'):acquire(source,tmp_path)
    unittest.TestCase().assertEqual(raw.read_bytes(),b'changed upstream bytes')

def test_refuses_to_overwrite(tmp_path):
    (tmp_path/'source-manifest.json').write_text('{}')
    output=tmp_path/'existing.duckdb';output.write_bytes(b'preserve me')
    with unittest.TestCase().assertRaises(FileExistsError):build(output,tmp_path)
    unittest.TestCase().assertEqual(output.read_bytes(),b'preserve me')

@contextmanager
def fixture_con():
    c=duckdb.connect(config={'memory_limit':'64MiB','threads':'1'})
    c.execute('CREATE TABLE agreements(agreement_id VARCHAR,agency_id VARCHAR,status VARCHAR,last_appeared_date DATE,removed_by_date DATE,geometry_wkb BLOB)')
    c.execute("INSERT INTO agreements VALUES ('a','agency','Active','2026-10-28',NULL,ST_AsWKB('POINT (0 0)'::GEOMETRY)::BLOB),('b','agency','Removed','2020-01-01','2020-02-01',ST_AsWKB('GEOMETRYCOLLECTION EMPTY'::GEOMETRY)::BLOB)")
    c.execute('CREATE TABLE agencies(agency_id VARCHAR,n_agreements INTEGER,n_active INTEGER,has_active BOOLEAN)')
    c.execute("INSERT INTO agencies VALUES ('agency',2,1,true)")
    yield c
    c.close()

def test_repeated_agency_and_empty_geometry_are_retained(con):
    unittest.TestCase().assertTrue(all(r['passed'] for r in validate(con,{'agreements':2,'agencies':1}).values()))

def test_duplicate_agreement_key_fails(con):
    con.execute("UPDATE agreements SET agreement_id='a'")
    with unittest.TestCase().assertRaisesRegex(ValueError,'agreements_key_duplicates'):validate(con,{'agreements':2,'agencies':1})

def test_inverted_termination_interval_fails(con):
    con.execute("UPDATE agreements SET removed_by_date='2019-01-01' WHERE agreement_id='b'")
    with unittest.TestCase().assertRaisesRegex(ValueError,'termination_interval_order'):validate(con,{'agreements':2,'agencies':1})

class BuildTests(unittest.TestCase):
    def test_hash(self):
        with tempfile.TemporaryDirectory() as d:test_rejects_wrong_source_hash(Path(d))
    def test_existing(self):
        with tempfile.TemporaryDirectory() as d:test_refuses_to_overwrite(Path(d))
    def test_valid(self):
        with fixture_con() as c:test_repeated_agency_and_empty_geometry_are_retained(c)
    def test_duplicate(self):
        with fixture_con() as c:test_duplicate_agreement_key_fails(c)
    def test_interval(self):
        with fixture_con() as c:test_inverted_termination_interval_fails(c)

if __name__=='__main__':unittest.main()
