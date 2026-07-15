# Current M1 Vertical Slice

Status: CURRENT-STATE  
Owner: Parāśara engine maintainers  
Last verified: 2026-07-13

## Purpose

The M1 vertical slice provides a development path from a Surya-format fixture to a Career snapshot. It is prototype evidence, not proof that the approved target architecture is complete.

## Current flow

```text
Surya-format JSON
  -> SuryaAdapter
  -> Chart
  -> chart_to_astrostate
  -> mutable enriched AstroState
  -> Career interpreter
  -> M1 rule runtime and local scoring/confidence
  -> snapshot dictionary/JSON
```

The current flow does not include the approved shared InferenceEngine, universal active-runtime RuleMatch boundary, typed DomainPrediction boundary, or dedicated OutputAssembler.

## Verification

This command executes the current pipeline and writes generated JSON only to pytest's temporary directory, plus any normal Python/pytest caches:

```powershell
$env:PYTHONPATH='.'
python -m pytest -q systems/Parasara/tests/test_vertical_slice_career.py
```

Fixtures and snapshots live under `systems/Parasara/fixtures/` and `systems/Parasara/tests/snapshots/`.

The test compares the returned generated dictionary with `systems/Parasara/tests/snapshots/output_golden_chart_01.json`. It does not validate the public output schema, scientific correctness, SME approval, or the target architecture.

## Snapshot generation

`systems/Parasara/tools/generate_snapshot.py` and `systems/Parasara/tools/surya_to_parasara.py` can write fixtures or snapshots. These are mutating workflows and must not run during read-only audits.

Direct generation requires an explicit output path and overwrites that path if it already exists. `surya_to_parasara.py` defaults to writing `systems/Parasara/fixtures/surya_generated_chart.json`; with `--run-snapshot`, it also writes `systems/Parasara/tests/snapshots/generated_surya_parasara_output.json`.

The CI comparator is also mutating unless an output path outside the repository is supplied, because its default generated output is `tmp_generated_snapshot.json` at the repository root.

## Current acceptance

The M1 output exposes Career summary, score, confidence, components, indicators, and evidence fields. These are compatibility behavior pending the approved RuleMatch, inference, typed-domain, and output stages.

The current snapshot additionally contains a placeholder Wealth domain, empty Dasha and transit collections, and skeletal top-level explainability policy sections. A matching snapshot confirms regression stability only; it does not promote these placeholders into approved contracts.

## Known boundary risks

- The normalizer and enrichments mutate the current AstroState.
- Career owns generic scoring, confidence, narrative, and dictionary assembly.
- The M1 runtime uses hardcoded rule types and imports test instrumentation.
- Rule/table discovery can depend on the process working directory.
- The snapshot assembler does not act as the target schema-validating OutputAssembler.
