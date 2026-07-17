# Parāśara rule-set v1

Live files:

- `derived_rules.yml`
- `m1_rules.yaml`
- `macros.yaml`
- `primitives.yml`
- `yogas.yaml`
- `calibration.json` (non-YAML calibration data)

`tools/rules_lint.py` discovers every supported `.yml` and `.yaml` file
recursively and deterministically. The authoritative Prompt-01 validator proves
each of the five supported files is inspected exactly once:

```text
python tools/validate_prompt01.py full
```

The linter enforces the metadata required by each supported file shape. It is
not a production lifecycle, promotion, backtest, SME-approval, or universal
rule-compiler service.
