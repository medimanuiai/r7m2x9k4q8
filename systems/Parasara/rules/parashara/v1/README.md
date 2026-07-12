Parāśara rule-set v1

Structure:
- macros.yaml  - reusable macro definitions
- yogas.yaml   - yoga detection rules
- planets.yaml - planet-specific rules
- calibration.json - populated by backtest harness

Lifecycle: rules should include `id`, `version`, `status` fields. Promotion requires passing tests and backtests.
