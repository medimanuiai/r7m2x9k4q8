# Parāśara Licensing Audit

Status: EVIDENCE  
Owner: Parāśara engine maintainers  
Evidence date: 2026-07-04  
Last documentation review: 2026-07-13

## Scope and conclusion

The adjacent report at `../evidence/licenses.json` is a point-in-time inventory produced from one development environment. No dependency in that inventory was labeled AGPL.

Evidence SHA-256:

`4C3FCAF14C3FC1112DB1BF27087FCC084E2678ED6E474643365946D7A231A2A3`

This is not a legal opinion or a complete repository licensing certification. It does not prove that the environment matched production or CI, that every dependency and asset was included, that package metadata was accurate, or that future changes remain compatible.

## Verified limitations

- `requirements-dev.txt` contains duplicate entries and unpinned versions.
- `systems/Parasara/requirements.txt` also uses unpinned versions.
- `setup.py` declares no `install_requires`, so it is not a complete dependency source.
- `pytest-xdist` appears in development requirements but was not present in the evidence inventory.
- `pip-licenses` appears in Parāśara requirements but was not present in the evidence inventory, which may reflect tool self-exclusion or environment mismatch.
- The inventory does not establish coverage of frontend packages, SuryaSiddhanta package metadata, vendored code, ephemeris/data files, generated assets, external references, models, fonts, or documentation/media licenses.
- Package-license labels alone do not verify notice, attribution, source-offer, redistribution, patent, trademark, or data-license obligations.

## Regeneration

Regeneration installs or invokes external tooling and writes evidence. It must be performed as a separately approved compliance workflow, not during a read-only audit.

Record exact environment inputs, tool/version, command, timestamp, review owner, identified obligations, and mitigation decisions. Do not overwrite prior evidence silently.

Prefer a locked, reproducible environment and produce both a license report and software bill of materials. Compare the report against every declared dependency source and investigate missing or unexpected packages.

## Required review scope

A release review must include:

- Python runtime and all production/dev dependency sets as applicable;
- frontend and authentication dependencies included in the release;
- SuryaSiddhanta and other local/system packages;
- ephemerides, datasets, YAML/reference tables, fixtures, and external reference material;
- copied or generated code/assets;
- required license texts, notices, attribution, and distribution obligations;
- security/vulnerability results tracked separately from license compatibility.

## Production gate

Legal or designated compliance review must approve the complete dependency and asset inventory before production release.
