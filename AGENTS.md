# Jyothishyam project instructions

## Python policy — user decision, 2026-11-06

Use **Python 3.11.9 only** for application development, automated tests, and CI.
This retains the working frontend API's `prompt01-py311` runtime selection,
the existing Python 3.11 snapshot CI baseline, and the
dependency-equipped `jyothishyam_env/prompt01-py311` environment. It is not a
Python upgrade. `.python-version` records the selected version for CI and tooling.

This decision explicitly supersedes every earlier requirement to validate both
Python 3.11.9 and Python 3.14.6, including locked decisions, specifications,
prompts, audit recommendations, reports, and session handoffs.

- Do not run a second Python version, maintain a multi-version CI matrix,
  duplicate compatibility test runs, or compare outputs across Python versions.
- Missing second-version results are never a defect, audit finding, incomplete
  validation, acceptance failure, or release blocker.
- Preserve meaningful correctness, determinism, regression, and end-to-end
  checks on Python 3.11.9. Keep same-runtime fresh-process, hash-seed, working
  directory, cold/warm, snapshot, and calculation checks. Investigate failures;
  never suppress them or update expected outputs merely to obtain a pass.
- Include this policy in future specifications, prompts, and session handoffs.
  Reinstate multi-version validation only if the user explicitly requests it.
  Address concrete runtime compatibility problems individually without
  automatically expanding the supported version matrix.
- Preserve historical evidence as history. Its dual-version requirements are
  superseded and must not be used as current instructions.
- Keep policy maintenance bounded: no architecture review, dependency
  modernization, or new audit cycle. Run appropriate affected checks once on
  the selected runtime; retain purposeful determinism scenarios within them.

The priority is a working application with correct calculations and usable
results. General compatibility work must not delay that goal.

## Local validation

From the repository root in PowerShell, use the prepared environment:

```powershell
& ./jyothishyam_env/prompt01-py311/Scripts/Activate.ps1
python --version  # Python 3.11.9
python tools/validate_prompt05.py full
```

CI retains the Prompt-03 and Prompt-05 functional gates on the selected runtime.
Use the relevant stage validator for scoped work; all subprocesses must reuse
the current interpreter. Keep no-update snapshots and isolated temporary outputs.
