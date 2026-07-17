"""Supported generic loader ordering and identity contracts after WP16."""

from __future__ import annotations

from pathlib import Path
from copy import deepcopy

import pytest
import yaml

from systems.Parasara.engine.rules import loader
from systems.Parasara.engine.rules.yoga_loader import load_yoga_rules


RULES = Path(__file__).resolve().parents[1] / "rules" / "parashara" / "v1"


@pytest.fixture(autouse=True)
def _preserve_registry():
    before = deepcopy(loader.RULE_REGISTRY)
    try:
        yield
    finally:
        loader.RULE_REGISTRY.clear()
        loader.RULE_REGISTRY.update(before)


def _write(path: Path, rows) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(rows, sort_keys=False), encoding="utf-8")


def test_loader_is_deterministic_last_source_wins_and_keeps_registry_identity(tmp_path):
    imported_reference = loader.RULE_REGISTRY
    _write(tmp_path / "z" / "b.yaml", [{"id": "duplicate", "source": "z-b"}])
    _write(tmp_path / "a" / "c.yml", [{"id": "duplicate", "source": "a-c"}])
    _write(tmp_path / "a" / "a.yaml", [{"id": "first", "source": "a-a"}])
    _write(tmp_path / "root.yaml", [{"id": "root", "source": "root"}])

    first = loader.load_rules_from_dir(str(tmp_path))
    first_snapshot = {key: dict(value) for key, value in first.items()}
    second = loader.load_rules_from_dir(str(tmp_path))

    assert first is second is imported_reference
    assert list(second) == ["root", "first", "duplicate"]
    assert second["duplicate"]["source"] == "z-b"
    assert {key: dict(value) for key, value in second.items()} == first_snapshot


def test_loader_ignores_non_mapping_rows_without_dropping_later_records(tmp_path):
    _write(tmp_path / "rules.yaml", [None, {"id": "kept", "type": "typed-owner"}])
    loaded = loader.load_rules_from_dir(str(tmp_path))
    assert list(loaded) == ["kept"]


def test_generic_loader_then_yoga_loader_preserves_identity_and_all_sources():
    reference = loader.RULE_REGISTRY
    generic = loader.load_rules_from_dir(str(RULES))
    loaded_yogas = load_yoga_rules(str(RULES))
    assert generic is loader.RULE_REGISTRY is reference
    assert len(generic) == 13
    assert [row["id"] for row in loaded_yogas] == [
        "rajayoga_naive", "dhana_naive", "arishta_naive"
    ]
    assert all(loader.get_rule(row["id"]) is row for row in loaded_yogas)


def test_yoga_loader_then_generic_loader_preserves_identity_and_typed_sources():
    reference = loader.RULE_REGISTRY
    load_yoga_rules(str(RULES))
    generic = loader.load_rules_from_dir(str(RULES))
    assert generic is loader.RULE_REGISTRY is reference
    assert len(generic) == 13
    assert [loader.get_rule(rule_id)["id"] for rule_id in (
        "rajayoga_naive", "dhana_naive", "arishta_naive"
    )] == ["rajayoga_naive", "dhana_naive", "arishta_naive"]
