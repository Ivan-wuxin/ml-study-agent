"""Run upstream helper with project adapters. No external dependencies."""
import subprocess,sys,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
vendor=root/'vendor/webapp-testing'
if not vendor.exists():
    import zipfile
    with zipfile.ZipFile(root/'vendor.zip') as archive: archive.extractall(root)
files={str(p.relative_to(vendor)):hashlib.sha256(p.read_bytes()).hexdigest() for p in vendor.rglob('*') if p.is_file() and p.name!='UPSTREAM.json'}
metadata=json.loads((vendor/'UPSTREAM.json').read_text(encoding='utf-8'))
metadata.update(snapshot_date='2026-11-19',version='main snapshot identified by per-file SHA256; commit API rate-limited',sha256=files)
(vendor/'UPSTREAM.json').write_text(json.dumps(metadata,indent=2),encoding='utf-8')
args=[sys.executable,str(vendor/'scripts/with_server.py'),'--server','"'+sys.executable+'" skill_server.py','--port','8766','--',sys.executable,'skill_smoke.py']
result=subprocess.run(args,cwd=root,capture_output=True,text=True,timeout=45)
(root/'skill_test_log.txt').write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
print(result.stdout);result.check_returncode()
