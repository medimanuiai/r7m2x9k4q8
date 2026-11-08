from typing import Dict, Any, List
import os
from pathlib import Path
import yaml

SIGNS = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

# Default heuristic weights (tunable / M1)
HOUSE_BENEFIT = {1: 0.18, 5: 0.18, 9: 0.18, 4: 0.06, 10: 0.06, 2: 0.03, 11: 0.03}
HOUSE_PENALTY = {6: -0.12, 8: -0.12, 12: -0.12}

# kendra and trikona sets
KENDRAS = {1,4,7,10}
TRIKONAS = {1,5,9}


def load_pinned_knowledge(identity, *, resolved_versions=None):
    """Read the selected manifest's exact knowledge bundle, without resolving a run."""
    import hashlib
    import json
    from systems.Parasara.engine.adapter.surya_adapter import StrictInputError
    from systems.Parasara.engine.models import StrictInputIssue
    from systems.Parasara.engine.versioning import (
        ResolvedEvaluationVersions, manifest_from_data, manifest_fingerprint_sha256,
        _knowledge_bundle_sha256, _resolve_repository_path, _semantic_data_artifact,
    )
    root = Path(__file__).resolve().parents[4]
    try:
        if resolved_versions is None:
            manifest = manifest_from_data(json.loads((root / "systems/Parasara/rules/parashara/v1/rule-set-manifest.json").read_text(encoding="utf-8")))
            if manifest.manifest_fingerprint_sha256 != "3e942f97cec7c24079faabc3db358b84177b752a8eb35a7b0d909f84a92d1220":
                raise ValueError("unexpected_v1_manifest")
        else:
            if not isinstance(resolved_versions, ResolvedEvaluationVersions):
                raise ValueError("invalid_authority")
            manifest = resolved_versions.manifest
        if manifest_fingerprint_sha256(manifest) != manifest.manifest_fingerprint_sha256:
            raise ValueError("manifest_fingerprint_mismatch")
        bundles = [item for item in manifest.knowledge_data if item.identity == identity]
        if len(bundles) != 1:
            raise ValueError("knowledge_bundle_missing")
        bundle = bundles[0]
        if _knowledge_bundle_sha256(root, bundle.artifacts) != bundle.content_sha256:
            raise ValueError("knowledge_bundle_mismatch")
        artifacts = {}
        for pin in bundle.artifacts:
            path = _resolve_repository_path(root, pin["path"])
            value = _semantic_data_artifact(path)
            # Recheck the exact value handed to producers, not a cached prior read.
            from systems.Parasara.engine.rules.prepared_state import canonical_json_bytes
            if hashlib.sha256(canonical_json_bytes(value)).hexdigest() != pin["content_sha256"]:
                raise ValueError("knowledge_artifact_mismatch")
            artifacts[pin["path"]] = value
        evidence = dict(identity=bundle.identity, version=bundle.version,
            bundle_sha256=bundle.content_sha256,
            manifest_sha256=manifest.manifest_fingerprint_sha256,
            artifacts=[dict(pin) for pin in bundle.artifacts])
        return artifacts, evidence
    except (OSError, ValueError, TypeError, KeyError):
        raise StrictInputError((StrictInputIssue("$.knowledge", "knowledge_artifact_mismatch"),)) from None


def compute_functional_roles_strict(astro, *, resolved_versions=None):
    from systems.Parasara.engine.identities import CANONICAL_PLANETS, SIGNS as signs, SIGN_LORD
    artifacts, evidence = load_pinned_knowledge("functional-roles-compatibility", resolved_versions=resolved_versions)
    issues = set()
    permitted = {"functional_benefic", "functional_malefic", "neutral", "yogakaraka", "benefic", "malefic"}
    for lagna_index, sign in enumerate(signs):
        key = f"systems/Parasara/enrichment_tables/functional_roles/{sign}.yaml"
        rows = artifacts.get(key)
        if not isinstance(rows, dict) or set(rows) != set(CANONICAL_PLANETS):
            issues.add("role_table_incomplete")
        if not isinstance(rows, dict):
            continue
        for planet, row in rows.items():
            if planet not in CANONICAL_PLANETS or not isinstance(row, dict):
                issues.add("role_row_malformed")
                continue
            score = row.get("functional_score")
            if row.get("functional_role") not in permitted or type(score) not in (int, float) or not 0 <= score <= 1:
                issues.add("role_row_malformed")
            owned = [number for number in range(1, 13)
                     if SIGN_LORD[signs[(lagna_index + number - 1) % 12]] == planet]
            if "owns_houses" in row and row["owns_houses"] != owned:
                issues.add("role_ownership_mismatch")
    return dict(readiness="malformed" if issues else "unsupported",
        issues=sorted(issues) if issues else ["astrology_sme_approval_required"],
        evidence=evidence, lagna=astro.lagna_sign, astrology_sme_approved=False)


def _load_table_for_lagna(lagna: str) -> Dict[str, Dict[str, Any]]:
    """Load a YAML table override for a given lagna if present.

    Lookup order (anchored to the repository, independent of CWD):
    1. `systems/Parasara/enrichment_tables/functional_roles/<lagna>.yaml`
    2. `rules/parashara/functional_roles/<lagna>.yaml`
    File maps planet name -> { functional_role:, functional_score:, yoga_role:, owns_houses: [] }
    """
    repository_root = Path(__file__).resolve().parents[4]

    # Compatibility table used by the approved functional-role tests/goldens.
    base1 = repository_root / 'systems' / 'Parasara' / 'enrichment_tables' / 'functional_roles'
    fname1 = base1 / f"{lagna}.yaml"
    if os.path.exists(fname1):
        try:
            with open(fname1, 'r', encoding='utf-8') as fh:
                docs = yaml.safe_load(fh)
                if isinstance(docs, dict):
                    return docs
        except Exception:
            pass

    # Fallback data-driven table.
    base2 = repository_root / 'rules' / 'parashara' / 'functional_roles'
    fname2 = base2 / f"{lagna}.yaml"
    if os.path.exists(fname2):
        try:
            with open(fname2, 'r', encoding='utf-8') as fh:
                docs = yaml.safe_load(fh)
                if isinstance(docs, dict):
                    return docs.get('functional_roles', docs)
        except Exception:
            pass
    return {}


def compute_functional_roles(astro) -> Dict[str, Dict[str, Any]]:
    """Compute a table-driven or heuristic functional role mapping for planets.

    Returns mapping planet_name -> {
      natural_role: 'natural_benefic'|'natural_malefic'|'neutral',
      owns_houses: [int],
      functional_score: float 0..1,
      functional_role: 'functional_benefic'|'functional_malefic'|'neutral'|'yogakaraka',
      yoga_role: optional string
    }
    """
    lagna = getattr(astro, 'lagna_sign', None) or ''
    table = _load_table_for_lagna(lagna)
    # build reverse sign->lord map comes from caller usually; fallback basic map
    SIGN_LORD = {
        'Aries': 'Mars', 'Taurus': 'Venus', 'Gemini': 'Mercury', 'Cancer': 'Moon',
        'Leo': 'Sun', 'Virgo': 'Mercury', 'Libra': 'Venus', 'Scorpio': 'Mars',
        'Sagittarius': 'Jupiter', 'Capricorn': 'Saturn', 'Aquarius': 'Saturn', 'Pisces': 'Jupiter',
    }
    # build LORD_SIGNS: planet -> signs
    LORD_SIGNS: Dict[str, List[str]] = {}
    for s, lord in SIGN_LORD.items():
        if lord:
            LORD_SIGNS.setdefault(lord, []).append(s)

    results: Dict[str, Dict[str, Any]] = {}
    for p in astro.planets:
        name = p.name
        # natural role (simple)
        NAT_BEN = {'Jupiter', 'Venus', 'Mercury', 'Moon'}
        NAT_MAL = {'Saturn', 'Mars', 'Rahu', 'Ketu', 'Sun'}
        natural = 'neutral'
        if name in NAT_BEN:
            natural = 'natural_benefic'
        elif name in NAT_MAL:
            natural = 'natural_malefic'

        # owned signs and convert to houses relative to lagna
        owned_signs = LORD_SIGNS.get(name, [])
        owns_houses: List[int] = []
        try:
            lagna_idx = SIGNS.index(lagna) if lagna in SIGNS else None
        except Exception:
            lagna_idx = None
        for osign in owned_signs:
            try:
                si = SIGNS.index(osign)
                if lagna_idx is not None:
                    house_num = ((si - lagna_idx) % 12) + 1
                    owns_houses.append(house_num)
            except ValueError:
                continue
        owns_houses = sorted(list(set(owns_houses)))

        reasons: List[str] = []
        # check for table override
        if table and name in table:
            entry = table.get(name) or {}
            func_role = entry.get('functional_role')
            func_score = float(entry.get('functional_score') or 0.5)
            yoga_role = entry.get('yoga_role')
            if entry.get('owns_houses'):
                reasons.append(f"owns_houses={entry.get('owns_houses')}")
            if yoga_role:
                reasons.append(f"yoga_role={yoga_role}")
            results[name] = {
                'planet': name,
                'natural_role': natural,
                'owns_houses': owns_houses,
                'functional_role': func_role,
                'functional_score': round(func_score, 3),
                'yoga_role': yoga_role,
                'reason': reasons,
            }
            continue

        # heuristic scoring
        score = 0.5
        for h in owns_houses:
            score += HOUSE_BENEFIT.get(h, 0.0)
            score += HOUSE_PENALTY.get(h, 0.0)
        # yogakaraka detection: owns any kendra and any trikona
        yoga_role = None
        if any((h in KENDRAS) for h in owns_houses) and any((h in TRIKONAS) for h in owns_houses):
            yoga_role = 'yogakaraka'
            score += 0.25

        # normalize to 0..1
        score = max(0.0, min(1.0, score))
        if yoga_role:
            func_label = 'yogakaraka'
            reasons.append('owns kendra and trikona -> yogakaraka')
        elif score >= 0.6:
            func_label = 'functional_benefic'
            reasons.append(f'score={round(score,3)} -> benefic')
        elif score <= 0.4:
            func_label = 'functional_malefic'
            reasons.append(f'score={round(score,3)} -> malefic')
        else:
            func_label = 'functional_neutral'
            reasons.append(f'score={round(score,3)} -> neutral')

        results[name] = {
            'planet': name,
            'natural_role': natural,
            'owns_houses': owns_houses,
            'functional_role': func_label,
            'functional_score': round(score, 3),
            'yoga_role': yoga_role,
            'reason': reasons,
        }

    return results
