# Parasara (Interpretation & Rules) Documentation Index

Key locations for Parasara documentation and code:

- Engine code: systems/Parasara/engine/
  - Normalizer: systems/Parasara/engine/normalizer.py
  - Enrichments: systems/Parasara/engine/enrichments/
  - Dasha: systems/Parasara/engine/dasha/
  - Rules runtime: systems/Parasara/engine/rules/runtime.py
  - Models: systems/Parasara/engine/models.py

- Rules and YAMLs: systems/Parasara/rules/parashara/
- Fixtures: systems/Parasara/fixtures/
- Tools: systems/Parasara/tools/ (includes surya_to_parasara.py and generate_snapshot utilities)

Tests and validation:

- Parāśara aspects tests: tests/enrichments/test_parashara_aspects.py
- Dasha tests and golden: tests/dasha/
- Snapshot and artifact generator: tests/testing_framework/

Notes:
- Functional role rules and enrichment golden matrices live under `systems/Parasara/rules/parashara/` and `tests/golden_charts/` when present.
- Use `tools/rules_lint.py` to validate rule metadata before merging.
