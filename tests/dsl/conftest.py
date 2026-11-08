"""Synthetic-only helpers for Prompt-07 tests."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest

from systems.Parasara.engine.rules.dsl import CompilationSucceeded, RuleDslCompiler
from tests.versioning.conftest import SyntheticCatalogBuilder, SyntheticPack


FIXTURES = Path(__file__).resolve().parent / "fixtures"


@dataclass(frozen=True)
class ResolvedDslPack:
    pack: SyntheticPack
    resolved: object
    compiler: RuleDslCompiler
    compilation: CompilationSucceeded


@pytest.fixture
def minimal_payload() -> bytes:
    return (FIXTURES / "minimal.yaml").read_bytes()


@pytest.fixture
def macros_payload() -> bytes:
    return (FIXTURES / "macros.yaml").read_bytes()


@pytest.fixture
def synthetic_catalog(tmp_path: Path) -> SyntheticCatalogBuilder:
    return SyntheticCatalogBuilder(tmp_path)


@pytest.fixture
def resolved_dsl_pack(
    synthetic_catalog: SyntheticCatalogBuilder,
    minimal_payload: bytes,
) -> ResolvedDslPack:
    source_id = "synthetic/prompt07_fixture/fixture-v1/rules.yaml"
    pack = synthetic_catalog.add_dsl(source_id=source_id, payload=minimal_payload)
    resolved = pack.resolver.resolve(pack.config)
    compiler = RuleDslCompiler(resolved_versions=resolved)
    result = compiler.compile_authorized(source_id=source_id)
    assert isinstance(result, CompilationSucceeded)
    return ResolvedDslPack(pack=pack, resolved=resolved, compiler=compiler, compilation=result)
