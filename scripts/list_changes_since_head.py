import os, subprocess, json, sys
from pathlib import Path

repo = Path('.')
# get last commit epoch
try:
    ts = int(subprocess.check_output(['git','show','-s','--format=%ct','HEAD']).strip())
except Exception as e:
    print('error getting HEAD time:', e)
    sys.exit(1)

threshold = ts
out = []
for p in repo.rglob('*'):
    if p.is_file():
        # skip .git and snapshot folders
        if '.git' in p.parts: continue
        # skip files in temp push folders
        if 'Jyothishyam_push' in p.parts: continue
        try:
            m = int(p.stat().st_mtime)
        except Exception:
            continue
        if m > threshold:
            out.append({'path': str(p), 'mtime': m})

# sort and print
out.sort(key=lambda x: x['mtime'], reverse=True)
print(json.dumps({'since': threshold, 'count': len(out), 'files': out}, indent=2))
