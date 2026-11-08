"""Opt-in source-scoped aspect facts. V1 remains the default contract."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field, replace
from functools import lru_cache
import hashlib
import json
import re
from pathlib import Path
from types import MappingProxyType

from .canonical import FrozenMapping, canonical_json_bytes, freeze_canonical
from .capabilities import CapabilityCatalog, CapabilityRequirement, get_production_capability_catalog
from .parameters import ASPECT_PARAMETER_SCHEMA, CANONICAL_PLANETS, invalid_parameters_error
from .registry import PredicateRegistry, get_production_registry, predicate_registry_fingerprint_sha256
from .models import PredicateError, PredicateResult, PredicateStatus, PredicateTraceStep
from .prepared_state import (
    PreparedAstroState, PreparedCapability, PreparedPlanet, PreparationIssue,
    prepared_capability_to_data, state_canonical_projection,
)
from systems.Parasara.engine.capability import CapabilityReadiness as Readiness

PROFILE = "source_scoped_aspects_v2"
PROFILE_IDENTITY = "parashara-source-scoped-aspects"
VERSION = "2.0.0"
GRAPH = "aspects.whole_sign_graph"
PLACEMENT = "planets.house_placement"
SOURCE_KIND = "strict_classical_whole_sign_graph"
FACTUAL_SCOPE = "seven_classical_planets"
CONDITION_COMPATIBILITY_CONTRACT = "source-scoped-prepared@2.0.0"
_READY = (Readiness.READY, Readiness.READY_EMPTY)
_TOKEN = object()
_SIGNS = ("Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces")
# Immutable classical projection of rules/parashara/aspects.yaml@1. The
# artifact-concordance regression pins every row to its existing canonical YAML
# content digest, using the versioning owner's artifact convention.
# Nodes intentionally have no authorized offsets in the V2 factual profile.
_ASPECT_ARTIFACT_SHA256 = "fcc896cb5eb8d9d16305b01629a0f6dbe9af0effb691c6929c15fef0154af601"
_PINNED_CLASSICAL_OFFSETS = FrozenMapping({
    "Sun": (7,), "Moon": (7,), "Mars": (4, 7, 8), "Mercury": (7,),
    "Jupiter": (5, 7, 9), "Venus": (7,), "Saturn": (3, 7, 10),
})
ARGUMENT_SCHEMA = replace(ASPECT_PARAMETER_SCHEMA, schema_version=VERSION)
SOURCE_SUPPORT = freeze_canonical(tuple(
    {"source": source,
     "readiness": Readiness.UNSUPPORTED if source in ("Rahu", "Ketu") else Readiness.READY,
     "issues": ("astrology_sme_approval_required",) if source in ("Rahu", "Ketu") else ()}
    for source in CANONICAL_PLANETS
))


def implementation_digest(*paths: str) -> str:
    """Fingerprint actual implementations and explicitly owned dependencies."""
    root = Path(__file__).resolve().parent
    return hashlib.sha256(canonical_json_bytes({
        path: hashlib.sha256((root / path).read_bytes()).hexdigest()
        for path in sorted(paths)
    })).hexdigest()


def require_v2_authority(authority):
    from systems.Parasara.engine.versioning import ResolvedEvaluationVersions
    if not isinstance(authority, ResolvedEvaluationVersions):
        raise TypeError("V2 requires resolved evaluation authority")
    manifest = authority.manifest
    from .evaluator_v2 import CONDITION_CONTENT_SHA256
    from .dsl.compiler_v2 import DSL_COMPILER_CONTENT_SHA256
    expected = (
        ("parashara-predicate-library", VERSION, "predicate-result@1.0.0", registry_fingerprint()),
        ("parashara-condition-evaluator", VERSION, CONDITION_COMPATIBILITY_CONTRACT, CONDITION_CONTENT_SHA256),
        ("parashara-rule-dsl-compiler", VERSION, "resolved-rule+condition@1.0.0", DSL_COMPILER_CONTENT_SHA256),
    )
    actual = tuple(None if c is None else (c.identity, c.version, c.compatibility_contract, c.content_sha256)
                   for c in (manifest.predicate_library, manifest.condition_evaluator, manifest.dsl))
    if actual != expected or manifest.dependency_graph is not None:
        raise ValueError("incompatible V2 authority components")
    return authority


@lru_cache(maxsize=1)
def get_capability_catalog_v2():
    catalog = CapabilityCatalog()
    old = get_production_capability_catalog()
    for key in old.capability_ids():
        item = old.lookup(key)
        catalog.register(replace(item, capability_version=VERSION) if key == GRAPH else item)
    return catalog.finalize()


@dataclass(frozen=True, slots=True, kw_only=True)
class AspectCapabilityV2:
    readiness: Readiness
    content: object = None
    issues: tuple[str, ...] = ()
    observed_version: str | None = None
    source_kind: str | None = None
    capability_id: str = GRAPH
    capability_version: str = VERSION

    @property
    def content_empty(self):
        return self.readiness is Readiness.READY_EMPTY

    def __post_init__(self):
        if self.capability_id != GRAPH or self.capability_version != VERSION:
            raise ValueError("invalid V2 graph identity")
        if not isinstance(self.readiness, Readiness) or not isinstance(self.issues, tuple):
            raise TypeError("invalid V2 readiness")
        if self.observed_version is not None and (not isinstance(self.observed_version, str)
                or re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", self.observed_version) is None):
            raise ValueError("invalid observed graph version")
        if self.source_kind not in (None, SOURCE_KIND) or len(set(self.issues)) != len(self.issues):
            raise ValueError("invalid graph provenance or issues")
        if self.readiness in _READY:
            content = freeze_canonical(self.content)
            issue = validate_envelope(content)
            if issue or self.issues or self.source_kind != SOURCE_KIND or self.observed_version != VERSION:
                raise ValueError(issue or "invalid V2 graph provenance")
            if (not content["edges"]) != self.content_empty:
                raise ValueError("invalid V2 graph emptiness")
            object.__setattr__(self, "content", content)
        elif self.content is not None:
            raise ValueError("unavailable V2 graph cannot carry content")
        if self.readiness in (Readiness.MISSING, Readiness.UNSUPPORTED) and (self.observed_version is not None or self.source_kind is not None):
            raise ValueError("missing graph cannot claim observed provenance")
        if self.readiness is Readiness.VERSION_MISMATCH and self.observed_version in (None, VERSION):
            raise ValueError("version mismatch requires a different observed version")
        if self.issues and any(x not in ("aspect_coverage_malformed", "aspect_coverage_contradictory") for x in self.issues):
            raise ValueError("unsafe V2 graph issue")


def validate_envelope(content, legacy=None):
    if not isinstance(content, Mapping) or set(content) != {"edges", "source_support", "config_version"}:
        return "aspect_coverage_malformed"
    if content["source_support"] != SOURCE_SUPPORT or not isinstance(content["edges"], tuple):
        return "aspect_coverage_malformed"
    if type(content["config_version"]) is not int or content["config_version"] != 1:
        return "aspect_coverage_contradictory"
    seen = set()
    planets = {} if legacy is None else {p.planet_id: p for p in legacy.planets}
    if legacy is not None and tuple(planets) != CANONICAL_PLANETS:
        return "aspect_coverage_contradictory"
    placements = None if legacy is None else legacy.capabilities[PLACEMENT]
    for edge in content["edges"]:
        if not isinstance(edge, Mapping) or set(edge) != {"source", "target", "aspect", "kind", "trace"}:
            return "aspect_coverage_malformed"
        source, target, trace = edge["source"], edge["target"], edge["trace"]
        if source not in CANONICAL_PLANETS[:7] or target is not None and target not in CANONICAL_PLANETS:
            return "aspect_coverage_contradictory"
        if not isinstance(trace, Mapping) or trace.get("producer") != "fwp01.strict_aspects" or trace.get("producer_version") != "1.0.0":
            return "aspect_coverage_contradictory"
        if set(trace) != {"source_planet", "source_sign", "source_house", "offset", "target_sign", "target_house", "matched_planets", "producer", "producer_version", "authority"}:
            return "aspect_coverage_malformed"
        if trace["source_sign"] not in _SIGNS or trace["target_sign"] not in _SIGNS:
            return "aspect_coverage_malformed"
        if trace.get("source_planet") != source or edge["kind"] != "whole-sign" or edge["aspect"] != f'{trace.get("offset")}th':
            return "aspect_coverage_contradictory"
        if not isinstance(trace.get("authority"), Mapping) or not trace["authority"]:
            return "aspect_coverage_contradictory"
        authority = trace["authority"]
        manifest_sha = authority.get("manifest_sha256")
        if (set(authority) != {"identity", "version", "manifest_sha256", "bundle_sha256", "artifacts"}
                or not isinstance(manifest_sha, str) or len(manifest_sha) != 64
                or any(c not in "0123456789abcdef" for c in manifest_sha)):
            return "aspect_coverage_malformed"
        if (authority.get("identity"), authority.get("version"), authority.get("bundle_sha256")) != (
            "parashara-aspects", "1", "e93d8bb7cc2d0f3cd007d09c2e1fff02056605da47bd8f937c6d22b465b14ed7"):
            return "aspect_coverage_contradictory"
        if authority.get("artifacts") != freeze_canonical(({
            "path": "rules/parashara/aspects.yaml",
            "content_sha256": _ASPECT_ARTIFACT_SHA256,
        },)):
            return "aspect_coverage_contradictory"
        if (type(trace.get("offset")) is not int or not 1 <= trace["offset"] <= 12
                or type(trace.get("source_house")) is not int or not 1 <= trace["source_house"] <= 12
                or type(trace.get("target_house")) is not int or not 1 <= trace["target_house"] <= 12):
            return "aspect_coverage_malformed"
        # Validate supplied facts together; never repair them or run a producer.
        # Offsets count inclusively: seventh is +6 signs/houses, wrapping at 12.
        offset = trace["offset"]
        if offset not in _PINNED_CLASSICAL_OFFSETS[source]:
            return "aspect_coverage_contradictory"
        if (trace["target_sign"] != _SIGNS[(_SIGNS.index(trace["source_sign"]) + offset - 1) % 12]
                or trace["target_house"] != (trace["source_house"] + offset - 2) % 12 + 1):
            return "aspect_coverage_contradictory"
        if not isinstance(trace.get("matched_planets"), tuple) or any(p not in CANONICAL_PLANETS for p in trace["matched_planets"]):
            return "aspect_coverage_malformed"
        if trace["matched_planets"] != tuple(p for p in CANONICAL_PLANETS if p in trace["matched_planets"]):
            return "aspect_coverage_malformed"
        if target is not None and target not in trace["matched_planets"]:
            return "aspect_coverage_contradictory"
        identity = (source, target, edge["aspect"], edge["kind"])
        if identity in seen:
            return "aspect_coverage_malformed"
        seen.add(identity)
        if legacy is not None:
            if source not in planets or target is not None and target not in planets:
                return "aspect_coverage_contradictory"
            if trace.get("source_sign") != planets[source].sign:
                return "aspect_coverage_contradictory"
            if target is not None and trace.get("target_sign") != planets[target].sign:
                return "aspect_coverage_contradictory"
            matched = tuple(p for p in CANONICAL_PLANETS if planets[p].sign == trace["target_sign"])
            if trace["matched_planets"] != matched:
                return "aspect_coverage_contradictory"
            if placements.readiness in _READY:
                houses = placements.content
                if houses.get(source) is not None and trace.get("source_house") != houses[source]:
                    return "aspect_coverage_contradictory"
                if target is not None and houses.get(target) is not None and trace.get("target_house") != houses[target]:
                    return "aspect_coverage_contradictory"
                if any(houses.get(p) is not None and houses[p] != trace["target_house"] for p in matched):
                    return "aspect_coverage_contradictory"
    return None


@dataclass(frozen=True, slots=True, kw_only=True, eq=False)
class PreparedAstroStateV2:
    """Factual identity excludes the private same-run authority binding."""
    _legacy: PreparedAstroState = field(repr=False)
    graph: AspectCapabilityV2
    _authority: object = field(repr=False)
    _token: object = field(repr=False)
    schema_version: str = VERSION
    producer_version: str = VERSION
    normalization_version: str = "1.0.0"
    system_scope: str = "parasara"

    def __post_init__(self):
        if self._token is not _TOKEN or not isinstance(self._legacy, PreparedAstroState):
            raise TypeError("V2 prepared state requires the owned factory")
        if (self.schema_version, self.producer_version, self.normalization_version, self.system_scope) != (VERSION, VERSION, "1.0.0", "parasara"):
            raise ValueError("incompatible V2 prepared versions")
        if self._legacy.capabilities[GRAPH].readiness is not Readiness.MISSING:
            raise ValueError("V1 bridge must withhold the whole-sign graph")
        if self.graph.readiness in _READY:
            issue = validate_envelope(self.graph.content, self._legacy)
            if issue:
                raise ValueError(issue)

    @property
    def planets(self):
        return self._legacy.planets

    @property
    def lagna_sign(self):
        return self._legacy.lagna_sign

    @property
    def capabilities(self):
        return MappingProxyType({**self._legacy.capabilities, GRAPH: self.graph})

    def require_authority(self, authority):
        if authority is not self._authority:
            raise ValueError("V2 state authority is not the same resolved object")


@dataclass(frozen=True, slots=True, kw_only=True)
class PreparationOutcomeV2:
    succeeded: bool
    state: PreparedAstroStateV2 | None
    issues: tuple[PreparationIssue, ...] = ()

    def __post_init__(self):
        if type(self.succeeded) is not bool or self.succeeded != (isinstance(self.state, PreparedAstroStateV2) and not self.issues):
            raise ValueError("invalid V2 preparation outcome")
        if not isinstance(self.issues, tuple) or any(not isinstance(x, PreparationIssue) for x in self.issues):
            raise TypeError("V2 preparation issues must be typed")


def make_prepared_v2(legacy, graph, authority):
    require_v2_authority(authority)
    # Retain exactly the six V1 capability values; the bridge withholds aspects.
    missing = PreparedCapability(capability_id=GRAPH, capability_version="1.0.0", observed_version=None,
        readiness=Readiness.MISSING, source_kind=None, content_empty=False, content=None)
    legacy = replace(legacy, capabilities={**legacy.capabilities, GRAPH: missing})
    if graph.readiness in _READY:
        issue = validate_envelope(graph.content, legacy)
        if issue:
            graph = AspectCapabilityV2(readiness=Readiness.MALFORMED, issues=(issue,), source_kind=SOURCE_KIND, observed_version=VERSION)
    return PreparedAstroStateV2(_legacy=legacy, graph=graph, _authority=authority, _token=_TOKEN)


def state_canonical_projection_v2(state):
    if not isinstance(state, PreparedAstroStateV2):
        raise TypeError("state must be PreparedAstroStateV2")
    projection = dict(state_canonical_projection(state._legacy))
    projection.update(schema_version=VERSION, producer_version=VERSION)
    projection["capabilities"] = {**projection["capabilities"], GRAPH: prepared_capability_to_data(state.graph)}
    return FrozenMapping(projection)


def state_canonical_bytes_v2(state):
    return canonical_json_bytes(state_canonical_projection_v2(state))


def state_sha256_v2(state):
    return hashlib.sha256(state_canonical_bytes_v2(state)).hexdigest()


def _decode_graph(value):
    # Reject unsafe canonical values before recoverable coverage classification.
    value = freeze_canonical(value)
    issue = "aspect_coverage_malformed"
    try:
        if not isinstance(value, Mapping) or set(value) != {"capability_id", "capability_version", "observed_version", "readiness", "source_kind", "content_empty", "content", "issues"}:
            raise ValueError(issue)
        fields = dict(value)
        empty = fields.pop("content_empty")
        fields["readiness"] = Readiness(fields["readiness"])
        if type(empty) is not bool or empty != (fields["readiness"] is Readiness.READY_EMPTY):
            raise ValueError(issue)
        if fields["capability_id"] != GRAPH:
            raise ValueError("aspect_coverage_contradictory")
        observed = fields["capability_version"] if fields["capability_version"] != VERSION else fields["observed_version"]
        if observed is not None and observed != VERSION:
            return AspectCapabilityV2(readiness=Readiness.VERSION_MISMATCH,
                source_kind=SOURCE_KIND, observed_version=observed)
        return AspectCapabilityV2(**fields)
    except (ValueError, TypeError) as exc:
        if str(exc) == "aspect_coverage_contradictory":
            issue = str(exc)
        return AspectCapabilityV2(readiness=Readiness.MALFORMED, source_kind=SOURCE_KIND,
                                  observed_version=VERSION, issues=(issue,))


def state_from_canonical_bytes_v2(payload, *, resolved_versions):
    """Revalidate untrusted serialized facts and bind the caller's exact authority."""
    require_v2_authority(resolved_versions)
    try:
        data = json.loads(payload)
        if set(data) != {"schema_version", "producer_version", "normalization_version", "system_scope", "lagna_sign", "planets", "capabilities"}:
            raise ValueError("invalid prepared keys")
        if (data["schema_version"], data["producer_version"], data["normalization_version"], data["system_scope"]) != (VERSION, VERSION, "1.0.0", "parasara"):
            raise ValueError("invalid prepared versions")
        caps = dict(data["capabilities"])
        graph = _decode_graph(caps[GRAPH])
        caps[GRAPH] = dict(capability_id=GRAPH, capability_version="1.0.0", observed_version=None,
            readiness=Readiness.MISSING, source_kind=None, content_empty=False, content=None, issues=())
        prepared = {}
        for key, value in caps.items():
            value["readiness"] = Readiness(value["readiness"])
            value["issues"] = tuple(value["issues"])
            prepared[key] = PreparedCapability(**value)
        legacy = PreparedAstroState(schema_version="1.0.0", producer_version="1.0.0", normalization_version="1.0.0",
            system_scope="parasara", lagna_sign=data["lagna_sign"],
            planets=tuple(PreparedPlanet(**p) for p in data["planets"]), capabilities=prepared)
        return PreparationOutcomeV2(succeeded=True, state=make_prepared_v2(legacy, graph, resolved_versions))
    except (ValueError, TypeError, KeyError, UnicodeError):
        return PreparationOutcomeV2(succeeded=False, state=None,
            issues=(PreparationIssue(code="invalid_canonical_v2_state", path="$"),))


def _result(status, inputs, evidence, code=None, capability=GRAPH, *, recoverable=True):
    details = {"capability_id": capability, "capability_version": VERSION if capability == GRAPH else "1.0.0",
               "filters": inputs, **evidence}
    errors = () if code is None else (PredicateError(code=code,
        message="The source-scoped aspect query is unavailable or invalid.", predicate_id="ASPECT_EXISTS",
        details=details, recoverable=recoverable),)
    return PredicateResult(matched=status is PredicateStatus.MATCHED, predicate_id="ASPECT_EXISTS",
        predicate_version=VERSION, inputs=inputs, evidence=evidence, errors=errors, status=status,
        trace_steps=(PredicateTraceStep(step_id="aspect_v2.coverage", operation="source_scoped_aspect_query",
            details=details, observation={"status": status.value}, error_code=code),))


def evaluate_aspect_exists_v2(parameters, state, context):
    validated = ARGUMENT_SCHEMA.validate(parameters)
    if not validated.valid:
        result = _result(PredicateStatus.INVALID_PARAMETERS, {},
            {"issues": tuple(i.details() for i in validated.issues)}, "invalid_parameters")
        return replace(result, errors=(invalid_parameters_error("ASPECT_EXISTS", validated),))
    if not isinstance(state, PreparedAstroStateV2):
        raise TypeError("V2 aspects require V2 prepared state")
    inputs = validated.normalized_inputs
    source, source_house = inputs.get("from_planet"), inputs.get("from_house")
    target, target_house = inputs.get("to_planet"), inputs.get("to_house")
    candidates = (source,) if source else CANONICAL_PLANETS
    eligible = candidates
    graph = state.graph
    evidence = {"candidate_sources": candidates, "eligible_sources": eligible,
        "supported_sources": (), "unavailable_sources": (), "coverage_complete": False,
        "matched_edges": (), "safe_reasons": graph.issues}
    if graph.readiness not in _READY:
        evidence.update(readiness=graph.readiness.value, expected_version=VERSION,
                        observed_version=graph.observed_version, issues=graph.issues)
        code = {Readiness.MISSING: "missing_capability", Readiness.MALFORMED: "malformed_capability",
                Readiness.VERSION_MISMATCH: "capability_version_mismatch", Readiness.UNSUPPORTED: "unsupported_capability"}[graph.readiness]
        return _result(PredicateStatus.MISSING_CAPABILITY, inputs, evidence, code,
                       recoverable=graph.readiness not in (Readiness.MALFORMED, Readiness.UNSUPPORTED))
    support = {row["source"]: row for row in graph.content["source_support"]}

    def coverage():
        evidence.update(eligible_sources=eligible,
            supported_sources=tuple(p for p in eligible if support[p]["readiness"] == Readiness.READY),
            unavailable_sources=tuple(p for p in eligible if support[p]["readiness"] != Readiness.READY))
        evidence["coverage_complete"] = not evidence["unavailable_sources"]
        evidence["safe_reasons"] = tuple(sorted({reason for p in evidence["unavailable_sources"] for reason in support[p]["issues"]}))
    coverage()
    if source and support[source]["readiness"] != Readiness.READY:
        return _result(PredicateStatus.MISSING_CAPABILITY, inputs, evidence, "aspect_source_unsupported")
    placement = state.capabilities[PLACEMENT]
    houses = placement.content if placement.readiness in _READY else {}
    if source_house is not None:
        if any(houses.get(p) is None for p in candidates):
            return _result(PredicateStatus.MISSING_CAPABILITY, inputs, evidence, "aspect_source_placement_unavailable", PLACEMENT)
        eligible = tuple(p for p in candidates if houses[p] == source_house)
        coverage()
    if target_house is not None:
        targets = (target,) if target else CANONICAL_PLANETS
        if any(houses.get(p) is None for p in targets):
            return _result(PredicateStatus.MISSING_CAPABILITY, inputs, evidence, "aspect_target_placement_unavailable", PLACEMENT)
    matches = tuple(e for e in graph.content["edges"]
        if e["source"] in evidence["supported_sources"]
        and (target is None or e["target"] == target)
        and (target_house is None or e["target"] is not None and houses[e["target"]] == target_house))
    evidence["matched_edges"] = matches
    if matches:
        return _result(PredicateStatus.MATCHED, inputs, evidence)
    if not evidence["coverage_complete"]:
        return _result(PredicateStatus.MISSING_CAPABILITY, inputs, evidence, "aspect_source_coverage_incomplete")
    return _result(PredicateStatus.UNMATCHED, inputs, evidence)


@lru_cache(maxsize=1)
def get_registry_v2():
    registry = PredicateRegistry(catalog=get_capability_catalog_v2())
    for old in get_production_registry().canonical_definitions():
        if old.predicate_id == "ASPECT_EXISTS":
            old = replace(old, predicate_version=VERSION, parameter_schema=ARGUMENT_SCHEMA,
                required_capabilities=(
                    CapabilityRequirement(capability_id=GRAPH, capability_version=VERSION, required=True, when_parameters_present=()),
                    CapabilityRequirement(capability_id=PLACEMENT, capability_version="1.0.0", required=True,
                        when_parameters_present=("from_house", "to_house")),
                ), handler=evaluate_aspect_exists_v2)
        registry.register(old)
    return registry.finalize()


@lru_cache(maxsize=1)
def registry_fingerprint():
    return hashlib.sha256(canonical_json_bytes({
        "profile": PROFILE, "identity": PROFILE_IDENTITY, "version": VERSION,
        "definitions": predicate_registry_fingerprint_sha256(get_registry_v2()),
        "implementation": implementation_digest("aspect_contract_v2.py", "registry.py", "parameters.py", "canonical.py", "prepared_state.py", "canonical_predicates.py", "snapshot_adapter.py", "capabilities.py", "../capability.py", "../astrostate_api.py", "../versioning.py"),
    })).hexdigest()
