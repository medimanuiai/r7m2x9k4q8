# WP01 — P0 Characterization Fixtures and Tests Completion Report

Date: 2026-07-14

Verdict: **COMPLETE**

## 1. Preflight and inherited baseline

WP01 was started only after reviewing the completed remediation evidence in `WorkPackage/WP00-R/WP00-R.md`. That report records `VERDICT: COMPLETE` and `WP01_READY: YES`.

Before any WP01 edit, both pinned environments were available and import-clean:

| Lane | Interpreter | Collection | Safe baseline | Approved snapshot |
|---|---|---:|---:|---|
| primary | Python 3.14.6 | 63 identical nodes | 61 passed, 2 skipped | exact match |
| compatibility | Python 3.11.9 | 63 identical nodes | 61 passed, 2 skipped | exact match |

Both lanes used PyYAML 6.0.3, Pydantic 2.13.4, and pytest 9.1.1. `pip check` and the required imports passed. All pytest commands used `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH=.`, `NDASTRO_USE_SRTM=0`, disabled the pytest cache provider, and placed `--basetemp` under ignored `jyothishyam_env/` storage.

The working tree was already dirty from the owner-approved WP00/WP00-R implementation and unrelated documentation work. Its pre-WP01 state was recorded and preserved. WP01 did not restore, rewrite, or claim those inherited changes.

## 2. Files added

WP01 added only these permitted files:

- `tests/rules/test_registered_predicates_characterization.py`
- `tests/enrichments/test_yoga_characterization.py`
- `systems/Parasara/tests/test_career_characterization.py`
- `systems/Parasara/Documentation/Engine/Prompt-01/Reports/WP01-P0-Characterization-Fixtures-and-Tests.md`

No existing production, rule, schema, snapshot, CI, dependency, or test file was modified by WP01.

## 3. Predicate characterization matrix

The suite verifies that the registry contains exactly six public IDs and that `ASPECT` and `ASPECT_EXISTS` reference the same handler. It freezes the current `PredicateResult` field sequence, result identity, inputs, evidence, trace/error lists, cache flags, timing type, logical repeatability, and non-mutation behavior.

| Registered ID | Matched case | Unmatched case | Additional contract |
|---|---|---|---|
| `ASPECT` | Mars to Moon edge | reversed endpoints | aliases the `ASPECT_EXISTS` handler and returns `predicate_id=ASPECT_EXISTS` |
| `ASPECT_EXISTS` | shared edge behavior through alias coverage | reversed endpoints | same result model/evidence contract as `ASPECT` |
| `PLANET_IN_HOUSE` | Mars in house 1 | Mars not in house 2 | lowercase predicate-name normalization |
| `HOUSE_OCCUPANT` | Moon in house 4 | Moon not in house 5 | exact planet/house evidence |
| `FUNCTIONAL_ROLE` | Mars is `yogakaraka` for Aries lagna | Mars is not `functional_malefic` | current context-based candidate restriction and evidence order |
| `PLANET_EXALTED` | Sun present in the metadata exaltation map | Moon absent from that map | equivalent fresh-state repetition; semantics explicitly deferred |

Missing-parameter behavior is recorded for all six IDs. In particular, current `ASPECT`/`ASPECT_EXISTS` behavior treats an empty filter as matching every available edge, while the other four representative empty-parameter calls safely return unmatched. This is characterization evidence, not approval of the parameter semantics.

## 4. Yoga characterization

The Yoga suite protects the active loader/evaluator path with the authoritative `surya_test_chart.json` fixture:

- exact rule-file order: `rajayoga_naive`, `dhana_naive`, `arishta_naive`;
- exact names, versions, categories, row keys, and value types;
- firing vector `[true, false, false]`;
- stable matched-edge order and functional-role evidence order;
- current unknown-predicate evidence for `HOUSE_LORDS_COMBINATION`;
- current empty `houses` and `aspects_used` projections;
- valid UUID trace identity;
- output storage in `astro.enrichments["yogas"]`;
- repeat evaluation equality after excluding only `trace_id`;
- stable registry membership/order and equivalent logical state on repetition.

The outer Yoga `planets` field is built from a set in current production. The tests protect membership while deliberately not treating its process-dependent ordering as a compatibility promise. Rule-row order and evidence-list order, which are stable and meaningful, are asserted exactly.

## 5. Career and public-output characterization

Career coverage protects both the approved `golden_chart_01.json` vertical slice and the non-empty `surya_test_chart.json` behavior:

- exact candidate membership/order for the approved fixture;
- exact score, confidence, summary, components, indicators, evidence, scoring breakdown, formula, rounding, and `career_001` trace value;
- exact non-empty indicator order: `10th_lord_Venus`, then `rajayoga_naive`;
- exact contribution and evidence order;
- current provenance resolution to `derived_rules.yml`, then `yogas.yaml`, without freezing machine-specific absolute prefixes;
- identical repeated interpreter output with no AstroState mutation;
- exact full public snapshot comparison through a temporary output path;
- byte-hash verification that the approved snapshot was consumed read-only.

The approved public snapshot SHA-256 remained:

`DA2059BA3CFB92EED267F93D1E41585DAC1422D68F685022C8609CFD04AD57AF`

The approved Career-only fixture SHA-256 remained:

`510ED861517E43DFC65BF0839B41E5FD2C3FE65BF9BCF2A817EC691E5068E764`

## 6. Isolation and normalization decisions

Every new suite snapshots mutable rule/predicate registries and the predicate cache, establishes its own known state, and restores the original objects in `finally`. Fixture and rules paths are derived from each test file's resolved repository location, so the tests do not depend on the process working directory. Generated output uses `tmp_path` only.

Predicate timing and cache-hit telemetry are excluded only from logical-result equality because the first and cached calls necessarily differ there; both fields are asserted independently. Yoga repetition excludes only random `trace_id`. Career uses no normalization: approved output and repeat results compare exactly. Absolute `_source_file` prefixes are not frozen because they are machine-specific; the observable source filenames and their order are protected.

## 7. Commands and results

The command forms below were executed once with each pinned interpreter path (`prompt01-py314` followed by `prompt01-py311`). Every command exited 0.

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONPATH='.'
$env:NDASTRO_USE_SRTM='0'

& <venv-python> -m pytest --collect-only -q -o addopts= -p no:cacheprovider --basetemp <lane-collect-temp>
& <venv-python> -m pytest -q -o addopts= -p no:cacheprovider --basetemp <lane-predicate-temp> tests/rules/test_registered_predicates_characterization.py
& <venv-python> -m pytest -q -o addopts= -p no:cacheprovider --basetemp <lane-yoga-temp> tests/enrichments/test_yoga_characterization.py
& <venv-python> -m pytest -q -o addopts= -p no:cacheprovider --basetemp <lane-career-temp> systems/Parasara/tests/test_career_characterization.py
& <venv-python> -m pytest -q --basetemp <lane-group-temp> tests/rules/test_registered_predicates_characterization.py tests/enrichments/test_yoga_characterization.py systems/Parasara/tests/test_career_characterization.py
& <venv-python> -m pytest -q -o addopts= -p no:cacheprovider --basetemp <lane-full-temp>
& <venv-python> systems/Parasara/tools/ci_snapshot_check.py --fixture systems/Parasara/fixtures/golden_chart_01.json --approved systems/Parasara/tests/snapshots/output_golden_chart_01.json --out <lane-temporary-output>
```

| Validation | Python 3.14.6 | Python 3.11.9 |
|---|---:|---:|
| post-WP01 collection | 88 collected | 88 collected, identical IDs |
| predicate suite | 19 passed | 19 passed |
| Yoga suite | 3 passed | 3 passed |
| Career suite | 3 passed | 3 passed |
| complete WP01 group, fresh run 1 | 25 passed | 25 passed |
| complete WP01 group, fresh run 2 | 25 passed | 25 passed |
| full safe baseline | 86 passed, 2 skipped | 86 passed, 2 skipped |
| repeated full safe baseline | 86 passed, 2 skipped | 86 passed, 2 skipped |
| approved snapshot comparator | `Snapshots match` | `Snapshots match` |

## 8. Unresolved observations and deferred semantics

These observations do not prevent a trustworthy characterization baseline, but remain decisions for later work packages:

1. `PLANET_EXALTED` currently reports a planet as exalted whenever its name occurs in `metadata.exaltations`; it does not verify the planet's actual sign or degree. WP01 records this without deciding the future semantics.
2. Empty `ASPECT` parameters currently act as an unrestricted query and match all graph edges. Future parameter validation must decide whether this remains valid.
3. The Yoga outer `planets` list is constructed through a set and can change order across processes. Membership is stable; unstable order is not promoted into a contract.
4. Yoga still emits an `unknown_predicate` child for `HOUSE_LORDS_COMBINATION`. The enclosing Dhana rule remains safely non-firing in the protected fixture.
5. The `ASPECT` alias currently returns canonical result identity `ASPECT_EXISTS`, not the invoked alias.
6. Career rule provenance currently depends on generic-loader collision resolution. Both pinned lanes resolve the protected indicators consistently, but future loader work must preserve or intentionally migrate that contract.

No hard-stop drift was observed in Yoga firing/row order, Career scoring/order/evidence, or approved public output.

## 9. Prohibited-file verification

`git diff --check` passed for all three new test files. A post-validation status review showed only the four WP01 additions listed in Section 2 attributable to this package. The production/rule/schema/snapshot/CI/dependency entries visible in the dirty tree were present at the WP01 preflight and belong to earlier approved or unrelated work; their status was not changed by WP01.

No snapshot update/accept command was run. Both approved hashes in Section 5 remained unchanged after all tests and comparison commands.

## 10. Requirement-to-test traceability

| Requirement | Test symbol(s) |
|---|---|
| exact six-ID registry and alias identity | `test_registry_contains_exactly_the_six_current_public_ids` |
| matched/unmatched results, evidence, errors, return fields, cache repeat | `test_matched_and_unmatched_return_contracts_are_exact` |
| missing-input current behavior | `test_missing_parameters_preserve_current_safe_result` |
| name normalization/input preservation | `test_predicate_name_is_normalized_but_input_mapping_is_preserved` |
| equivalent prepared-state repeat and exaltation observation | `test_equivalent_fresh_state_repeats_the_same_logical_result` |
| Yoga rule membership and row order | `test_loader_exposes_the_current_three_rule_set_in_file_order` |
| Yoga firing/non-firing, shape, types, evidence and ordering | `test_active_yoga_path_freezes_firing_nonfiring_shape_and_evidence_order` |
| Yoga UUID-only logical repeat and global isolation | `test_repeat_evaluation_changes_only_trace_identity_and_does_not_drift_registries` plus `isolated_rule_engine_globals` |
| Career candidate membership/order and approved domain contract | `test_candidate_membership_order_and_golden_career_contract` |
| exact read-only public golden | `test_approved_public_golden_is_consumed_read_only` |
| non-empty Career score/confidence/components/indicator/evidence order and repeat | `test_nonempty_career_result_freezes_order_rounding_evidence_and_repeatability` |
| registry/cache cleanup | `isolated_predicate_globals`, `isolated_rule_engine_globals`, `isolated_rule_globals` |
| CWD-independent fixtures and temporary output | resolved `REPO_ROOT` constants and `tmp_path` in all three suites |

## 11. Final disposition

WP01 supplies a repeatable P0 safety net for all six registered predicate IDs, the active Yoga evaluator, and active Career/public output in both required Python lanes. The inherited baseline remains green, approved goldens are unchanged, and no prohibited file was changed.

**VERDICT: COMPLETE**

WP02 was not started.
