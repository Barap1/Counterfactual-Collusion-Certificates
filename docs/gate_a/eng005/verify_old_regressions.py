"""Run the new regressions against HEAD's pre-ENG-005 owned source in /tmp.

No checkout, worktree edits, secret copies, or repository git mutations.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[3]
old=Path(tempfile.mkdtemp(prefix='eng005-before-',dir='/private/tmp'))
(old/'ccc').mkdir()
for path in (ROOT/'ccc').iterdir():
    if path.name in ('audit','fixtures'):
        (old/'ccc'/path.name).mkdir()
        for src in path.glob('*.py'):
            rel=str(src.relative_to(ROOT))
            content=subprocess.check_output(['git','show','HEAD:'+rel],cwd=ROOT)
            (old/rel).write_bytes(content)
        for src in path.glob('*.json'):
            (old/'ccc'/path.name/src.name).symlink_to(src)
    elif path.name != '__pycache__':
        (old/'ccc'/path.name).symlink_to(path,target_is_directory=path.is_dir())
shutil.copytree(ROOT/'tests',old/'tests',ignore=shutil.ignore_patterns('__pycache__'))
(old/'starter').symlink_to(ROOT/'starter',target_is_directory=True)
py=ROOT/'starter/collusion_hackathon/colosseum/.venv/bin/python'
for name,folder in [('old_tests_audit','tests/audit'),('old_test_precondition','tests/fixtures')]:
    command=[str(py),'-m','tests.replay.offline_runner','-s',folder,'-t','.']
    if folder=='tests/fixtures':
        command += ['-p','test_eng005_precondition.py']
    result=subprocess.run(command,cwd=old,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
    (ROOT/'docs/gate_a/eng005'/f'{name}.txt').write_bytes(result.stdout)
    print(name,'exit',result.returncode)
print('Before-source snapshot:',old)
