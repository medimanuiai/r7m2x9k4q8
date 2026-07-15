from pathlib import Path

import yaml

from tools import rules_lint


GENERIC_RULE = {
    'id': 'generic', 'name': 'Generic', 'author': 'test', 'created_date': '2026-01-01',
    'source_reference': 'test', 'classical_reference': 'test', 'validation_status': 'test',
    'sme_required': False, 'sme_approved': False,
}

YOGA_RULE = {
    'id': 'yoga', 'name': 'Yoga', 'version': 1, 'category': 'test',
    'conditions': {'type': 'AND', 'children': []}, 'weights': {'base': 1.0},
    'evidence_required': 0, 'provenance': 'test', 'sme_approved': False, 'tests': [],
}


def write_yaml(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(value), encoding='utf-8')


def test_discovery_is_recursive_deterministic_and_deduplicated(tmp_path):
    yml = tmp_path / 'z' / 'rule.yml'
    yaml_path = tmp_path / 'a' / 'rule.yaml'
    write_yaml(yml, [GENERIC_RULE])
    write_yaml(yaml_path, [{'id': 'runtime-rule'}])
    (tmp_path / 'ignored.json').write_text('{}', encoding='utf-8')

    discovered = rules_lint.discover_rule_files(tmp_path)
    expected = sorted([yml.resolve(), yaml_path.resolve()], key=lambda path: str(path).casefold())
    assert discovered == expected
    assert rules_lint.normalize_rule_paths([yml, yml.resolve(), yaml_path]) == expected


def test_lint_supports_existing_yml_and_yoga_yaml_formats(tmp_path):
    generic = tmp_path / 'generic.yml'
    yoga = tmp_path / 'yogas.yaml'
    write_yaml(generic, [GENERIC_RULE])
    write_yaml(yoga, [YOGA_RULE])

    assert rules_lint.lint_file(generic) == (True, 'ok')
    assert rules_lint.lint_file(yoga) == (True, 'ok')
    assert rules_lint.main([str(tmp_path)]) == 0


def test_empty_generic_yaml_matches_runtime_loader_behavior(tmp_path):
    empty = tmp_path / 'macros.yaml'
    empty.write_text('# no active rules\n', encoding='utf-8')
    assert rules_lint.lint_file(empty) == (True, 'ok')


def test_malformed_supported_extensions_fail_command(tmp_path):
    for filename in ('broken.yml', 'broken.yaml'):
        path = tmp_path / filename
        path.write_text('- [unterminated', encoding='utf-8')
        assert rules_lint.main([str(tmp_path)]) == 2
        path.unlink()


def test_repository_yogas_file_is_discovered_once():
    paths = rules_lint.discover_rule_files(Path('systems/Parasara/rules'))
    yogas = [path for path in paths if path.name == 'yogas.yaml']
    assert len(yogas) == 1
    assert rules_lint.lint_file(yogas[0]) == (True, 'ok')
