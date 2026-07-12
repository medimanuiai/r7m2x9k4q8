import ast
from pathlib import Path


def test_interpreters_do_not_use_chart_directly():
    """Enforce: interpreters must consume `AstroState`, not `Chart`.

    This simple test scans Python source under `engine/interpreters` and fails
    if the identifier `Chart` is imported or referenced. It's a lightweight
    static check for M1 to ensure single source of truth.
    """
    repo_root = Path(__file__).resolve().parents[3]
    interp_dir = repo_root / 'systems' / 'Parasara' / 'engine' / 'interpreters'
    assert interp_dir.exists()
    violations = []
    for py in interp_dir.rglob('*.py'):
        src = py.read_text(encoding='utf-8')
        try:
            tree = ast.parse(src)
        except Exception:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id == 'Chart':
                violations.append(f'{py.relative_to(repo_root)} references Chart')
            if isinstance(node, ast.Attribute) and getattr(node, 'attr', '') == 'Chart':
                violations.append(f'{py.relative_to(repo_root)} references Chart attribute')
            if isinstance(node, ast.ImportFrom) and (node.module or '').endswith('models'):
                for n in node.names:
                    if n.name == 'Chart':
                        violations.append(f'{py.relative_to(repo_root)} imports Chart')

    assert not violations, 'Interpreters must not reference Chart directly:\n' + '\n'.join(violations)
