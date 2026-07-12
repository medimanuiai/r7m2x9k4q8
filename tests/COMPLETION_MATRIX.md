
Component | Implementation status | Validation status | Test count | Golden coverage | Production readiness
---|---:|---:|---:|---:|---:
Surya Validation | Generator implemented (`tests/surya/generate_surya_test_cases.py`), 500 cases written | Pending — expected planet positions need Skyfield-based validation to populate | 1 (scaffold `tests/surya/test_positions.py`) | 0 | false
Aspect Engine | Parāśara aspects implemented with Rahu/Ketu configurability (`systems/Parasara/engine/enrichments/aspects.py`) | Unit tests added and passing (`tests/enrichments/test_parashara_aspects.py`, `tests/enrichments/test_aspects.py`) | 3+ | 0 | false
Vimshottari Dasha | Canonical M1 implementation (`systems/Parasara/engine/dasha/vimshottari.py`) producing mahadasha/antardasha/pratyantardasha | Golden produced and test passing (`tests/dasha/golden_vimshottari_01.json`, `tests/dasha/test_vimshottari_golden.py`) | 3 | 1 | false
