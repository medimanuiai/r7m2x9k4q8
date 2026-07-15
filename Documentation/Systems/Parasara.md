# Parāśara (Interpretation and Rules) Documentation Index

The canonical engine documentation index is `systems/Parasara/Documentation/README.md`. It separates verified current behavior, approved target architecture, implementation status, governance, guides, and operations.

Key locations for Parasara documentation and code:

- Engine code: systems/Parasara/engine/
  - Normalizer: systems/Parasara/engine/normalizer.py
  - Enrichments: systems/Parasara/engine/enrichments/
  - Dasha: systems/Parasara/engine/dasha/
  - Rules runtime: systems/Parasara/engine/rules/runtime.py
  - Models: systems/Parasara/engine/models.py

- Rules and YAMLs: both `systems/Parasara/rules/` and `systems/Parasara/engine/rules/` contain rule-related content; ownership remains under audit and must not be inferred from this index.
- Fixtures: systems/Parasara/fixtures/
- Tools: systems/Parasara/tools/ (includes surya_to_parasara.py and generate_snapshot utilities)

Tests and validation:

- Parāśara aspects tests: tests/enrichments/test_parashara_aspects.py
- Dasha tests and golden: tests/dasha/
- Snapshot and artifact generator: tests/testing_framework/

Notes:

- Functional-role tables are under `systems/Parasara/enrichment_tables/functional_roles/`; rule-related data also exists under the rule roots noted above.
- No `tests/golden_charts/` directory was present at the 2026-07-13 review. Use the test and snapshot paths linked by the canonical documentation rather than assuming it exists.
- `tools/rules_lint.py` exists as a local validation utility. Repository evidence reviewed on 2026-07-13 did not establish that it is enforced by CI before merging.
