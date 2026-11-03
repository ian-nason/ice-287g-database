"""An optimized interpreter must reject an incorrect client catalog."""
from pathlib import Path
import os,subprocess,sys,unittest
ROOT=Path(__file__).resolve().parent
PROBE=r'''
import runpy,sys
from unittest.mock import patch
class Connection:
    def execute(self,*args,**kwargs):return self
    def fetchone(self):return (0,)
    def fetchall(self):return []
    def close(self):pass
target=sys.argv[1]
sys.argv=[target,'http://127.0.0.1:1/not-requested','unused-fixture-cache']
with patch('datapond.list',return_value=['wrong-dataset']),patch('datapond.connect',return_value=Connection()):
    runpy.run_path(target,run_name='__main__')
'''
class ClientValidationTests(unittest.TestCase):
    def test_optimized_python_rejects_wrong_catalog(self):
        result=subprocess.run([sys.executable,'-O','-c',PROBE,str(ROOT/'smoke_python.py')],cwd=ROOT,capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('Unexpected local catalog',result.stderr)
if __name__=='__main__':unittest.main()
