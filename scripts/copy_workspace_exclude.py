import shutil
import os
from pathlib import Path

src = Path(r"C:/Users/mvman/OneDrive/Documents/Projects/Jyothishyam")
dst = Path(r"C:/Users/mvman/OneDrive/Documents/Projects/Jyothishyam_push_latest")
excludes = [
    "frontend/.next",
    "frontend/node_modules",
    "node_modules",
    "**/node_modules",
    "systems/SuryaSiddhanta/ndastro_engine/data/ephemeris",
    ".git",
]

if dst.exists():
    shutil.rmtree(dst)

for root, dirs, files in os.walk(src):
    rel = os.path.relpath(root, src)
    if rel == ".":
        rel = ""
    # skip excluded dirs
    skip_dir = False
    for ex in excludes:
        # handle simple prefix excludes
        if ex.endswith("/**"):
            p = ex[:-3]
        else:
            p = ex
        if p and (rel == p or rel.startswith(p + os.sep)):
            skip_dir = True
            break
    if skip_dir:
        # prevent walking into subdirs
        dirs[:] = []
        continue
    # create destination dir
    target_dir = dst.joinpath(rel)
    target_dir.mkdir(parents=True, exist_ok=True)
    for f in files:
        src_file = Path(root).joinpath(f)
        rel_file = os.path.join(rel, f) if rel else f
        # check excluded file paths
        skip_file = False
        for ex in excludes:
            if src_file.match(ex):
                skip_file = True
                break
        if skip_file:
            continue
        shutil.copy2(src_file, target_dir.joinpath(f))

print('Copy complete to', dst)
