"""Domain-neutral capability availability contracts.

Prompt-04 places the shared taxonomy below AstroState and predicate consumers.
The historical rule-module imports remain compatibility re-exports.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


_CAPABILITY_ID = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)+$")
_SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
_SAFE_CODE = re.compile(r"^[a-z][a-z0-9_]*$")


class CapabilityReadiness(str, Enum):
    READY = "ready"
    READY_EMPTY = "ready_empty"
    MISSING = "missing"
    MALFORMED = "malformed"
    VERSION_MISMATCH = "version_mismatch"
    UNSUPPORTED = "unsupported"


class CapabilityFactState(str, Enum):
    PRESENT = "present"
    ABSENT_ENTITY = "absent_entity"
    CAPABILITY_UNAVAILABLE = "capability_unavailable"
    MALFORMED_CAPABILITY = "malformed_capability"
    VERSION_MISMATCH = "version_mismatch"
    UNSUPPORTED_CAPABILITY = "unsupported_capability"


@dataclass(frozen=True, slots=True, kw_only=True)
class CapabilityInspection:
    capability_id: str
    expected_version: str
    observed_version: str | None
    readiness: CapabilityReadiness
    source_kind: str | None
    content_empty: bool
    issues: tuple[str, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.capability_id, str) or not _CAPABILITY_ID.fullmatch(self.capability_id):
            raise ValueError("capability_id must be canonical")
        if not isinstance(self.expected_version, str) or not _SEMVER.fullmatch(self.expected_version):
            raise ValueError("expected_version must be strict SemVer")
        if self.observed_version is not None and (
            not isinstance(self.observed_version, str) or not _SEMVER.fullmatch(self.observed_version)
        ):
            raise ValueError("observed_version must be strict SemVer")
        if not isinstance(self.readiness, CapabilityReadiness):
            raise TypeError("readiness must be CapabilityReadiness")
        if self.source_kind is not None and (
            not isinstance(self.source_kind, str) or not _SAFE_CODE.fullmatch(self.source_kind)
        ):
            raise ValueError("source_kind must be a safe identifier")
        if type(self.content_empty) is not bool or not isinstance(self.issues, tuple) or any(
            type(item) is not str or not _SAFE_CODE.fullmatch(item) for item in self.issues
        ):
            raise TypeError("inspection content_empty/issues have invalid types")
        if self.readiness is CapabilityReadiness.READY and self.content_empty:
            raise ValueError("ready content must be nonempty")
        if self.readiness is CapabilityReadiness.READY_EMPTY and not self.content_empty:
            raise ValueError("ready_empty content must be explicitly empty")
        if self.readiness in (CapabilityReadiness.MISSING, CapabilityReadiness.UNSUPPORTED):
            if self.observed_version is not None or self.source_kind is not None or self.content_empty:
                raise ValueError("missing/unsupported inspection cannot claim observed content")
        elif self.source_kind is None:
            raise ValueError("present or malformed content requires a source kind")
        if self.readiness is CapabilityReadiness.VERSION_MISMATCH and self.observed_version is None:
            raise ValueError("version mismatch requires an observed version")
        if self.readiness in (CapabilityReadiness.READY, CapabilityReadiness.READY_EMPTY) and self.issues:
            raise ValueError("ready inspections cannot contain issues")


__all__ = ("CapabilityFactState", "CapabilityInspection", "CapabilityReadiness")
