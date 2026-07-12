# Licensing Audit

Date: 2026-07-04

Status: Completed — `systems/Parasara/Documentation/licenses.json` has been generated and reviewed for obvious incompatibilities.

Summary:
- `licenses.json` was produced from the dev environment and is stored at `systems/Parasara/Documentation/licenses.json`.
- No AGPL dependencies were flagged in the initial scan. Any future dependency additions should be re-scanned in CI.

How to re-run (local or CI):

1. Ensure Python environment is active and `pip` available.
2. Install audit tool:

```bash
python -m pip install pip-licenses
```

3. Generate license report for installed packages (after installing requirements):

```bash
python -m pip install -r systems/Parasara/requirements.txt
pip-licenses --format=json > systems/Parasara/Documentation/licenses.json
```

4. Inspect `licenses.json` for any AGPL or incompatible licenses. If found, document package and mitigation steps in this file.

Notes:
- Add `pip-licenses` to CI job that builds the Parāśara environment and store `licenses.json` as an artifact for auditing.

