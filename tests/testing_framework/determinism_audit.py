import os
from pathlib import Path


def scan_repo_for_randomness(root: str = '.'):
    issues = []
    for p in Path(root).rglob('*.py'):
        try:
            txt = p.read_text()
        except Exception:
            continue
        if 'random.' in txt or 'numpy.random' in txt or 'np.random' in txt:
            issues.append(str(p))
    return issues


if __name__ == '__main__':
    import sys
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    issues = scan_repo_for_randomness(root)
    if issues:
        print('Potential randomness sources found in:')
        for i in issues:
            print(' -', i)
    else:
        print('No obvious randomness sources found.')
