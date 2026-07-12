"""Configuration management module for ndastro_engine.

This module provides the ConfigurationManager class for handling
application configuration settings in a centralized manner.
"""

import contextlib
import os
import struct
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, fields, replace
from pathlib import Path
from typing import TYPE_CHECKING, Literal, TypeAlias, TypeVar, cast

from dotenv import load_dotenv
from skyfield.iokit import Loader

import ndastro_engine.config as _self  # self-reference to mutate module globals
from ndastro_engine.utils import get_app_data_dir

if TYPE_CHECKING:
    from collections.abc import Generator

    from skyfield.jpllib import SpiceKernel

PositionReference: TypeAlias = Literal["geocentric", "topocentric"]
NodeType: TypeAlias = Literal["true", "mean"]
SunriseDefinition: TypeAlias = Literal["geometric", "disc_centre"]

# ---------------------------------------------------------------------------
# Valid value sets for validated settings
# ---------------------------------------------------------------------------

_VALID_POSITION_REFERENCES: frozenset[PositionReference] = frozenset({"geocentric", "topocentric"})
_VALID_NODE_TYPES: frozenset[NodeType] = frozenset({"true", "mean"})
_VALID_SUNRISE_DEFINITIONS: frozenset[SunriseDefinition] = frozenset({"geometric", "disc_centre"})


def _try_load_dotenv(env_file: str | Path | None = None) -> None:
    """Load environment variables from a .env file if python-dotenv is installed.

    This is a no-op when python-dotenv is not present, keeping the engine
    free of mandatory runtime dependencies beyond skyfield.

    Args:
        env_file: Explicit path to a .env file.  When ``None``, python-dotenv
            searches the current working directory and its parents.

    """
    with contextlib.suppress(ImportError):
        load_dotenv(env_file)


def _read_bool_env(key: str, default: bool) -> bool:
    """Read an environment variable as a boolean (``'true'``/``'1'`` → True)."""
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes"}


def _read_float_env(key: str, default: float) -> float:
    """Read an environment variable as a float, falling back to *default* on error."""
    raw = os.getenv(key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


@dataclass
class EngineSettings:
    """All ndastro_engine calculation preferences, mirroring JHora [CalculationPreferences].

    Construct from environment variables via :meth:`from_env`, or create
    directly with explicit values for testing.

    """

    position_reference: PositionReference = "geocentric"
    node_type: NodeType = "true"
    ayanamsa_delta: float = 0.0
    dasa_year_length: float = 365.25
    apply_nutation: bool = True
    apply_aberration: bool = True
    apply_grav_deflection: bool = True
    sunrise_definition: SunriseDefinition = "geometric"

    def __post_init__(self) -> None:
        """Validate string fields against their allowed value sets."""
        if self.position_reference not in _VALID_POSITION_REFERENCES:
            msg = f"position_reference must be one of {sorted(_VALID_POSITION_REFERENCES)}, got {self.position_reference!r}"
            raise ValueError(msg)
        if self.node_type not in _VALID_NODE_TYPES:
            msg = f"node_type must be one of {sorted(_VALID_NODE_TYPES)}, got {self.node_type!r}"
            raise ValueError(msg)
        if self.sunrise_definition not in _VALID_SUNRISE_DEFINITIONS:
            msg = f"sunrise_definition must be one of {sorted(_VALID_SUNRISE_DEFINITIONS)}, got {self.sunrise_definition!r}"
            raise ValueError(msg)

    @classmethod
    def from_env(cls) -> "EngineSettings":
        """Construct an :class:`EngineSettings` from ``NDASTRO_*`` environment variables."""
        return cls(
            position_reference=_validated_str("NDASTRO_POSITION_REFERENCE", "geocentric", _VALID_POSITION_REFERENCES),
            node_type=_validated_str("NDASTRO_NODE_TYPE", "true", _VALID_NODE_TYPES),
            ayanamsa_delta=_read_float_env("NDASTRO_AYANAMSA_DELTA", 0.0),
            dasa_year_length=_read_float_env("NDASTRO_DASA_YEAR_LENGTH", 365.25),
            apply_nutation=_read_bool_env("NDASTRO_APPLY_NUTATION", default=True),
            apply_aberration=_read_bool_env("NDASTRO_APPLY_ABERRATION", default=True),
            apply_grav_deflection=_read_bool_env("NDASTRO_APPLY_GRAV_DEFLECTION", default=True),
            sunrise_definition=_validated_str("NDASTRO_SUNRISE_DEFINITION", "geometric", _VALID_SUNRISE_DEFINITIONS),
        )


@dataclass
class EngineSettingsOverride:
    """Selective override for :class:`EngineSettings`.

    Every field defaults to ``None``, meaning "keep whatever came from the
    environment".  Only fields you explicitly set will be applied on top of
    the environment-sourced values when passed to :func:`configure`.

    Example::

        configure(EngineSettingsOverride(node_type="mean"), env_file=".env")
        # All other settings come from .env; only node_type is forced to 'mean'.

    """

    position_reference: PositionReference | None = None
    node_type: NodeType | None = None
    ayanamsa_delta: float | None = None
    dasa_year_length: float | None = None
    apply_nutation: bool | None = None
    apply_aberration: bool | None = None
    apply_grav_deflection: bool | None = None
    sunrise_definition: SunriseDefinition | None = None


# Cached once at import time — avoids repeated dataclass descriptor lookups inside
# override_settings() and configure() on every hot-path call.
_OVERRIDE_FIELDS: tuple = ()  # populated below after class is defined


class ConfigurationManager:
    """Manages application configuration settings.

    This class provides a centralized way to handle configuration settings for the application.
    It initializes with default settings and can be extended to load, validate, and manage
    various configuration parameters.

    Attributes:
        settings (dict): A dictionary containing configuration key-value pairs.

    """

    def __init__(self) -> None:
        """Initialize the ConfigurationManager with default settings."""
        try:
            data_dir = get_app_data_dir("ndastro")
            Path(data_dir).mkdir(parents=True, exist_ok=True)

            # Custom loader for downloading and caching .bsp files
            loader = Loader(data_dir, verbose=True)

            self.ts = loader.timescale()

            # Try to load ephemeris, delete and retry if corrupted
            ephemeris_file = "de440t.bsp"
            try:
                self.eph: SpiceKernel = cast("SpiceKernel", loader(ephemeris_file))
            except (struct.error, ValueError):
                # File is corrupted, delete and retry
                corrupted_file = Path(data_dir) / ephemeris_file
                if corrupted_file.exists():
                    print(f"Detected corrupted ephemeris file, deleting: {corrupted_file}")
                    corrupted_file.unlink()
                    print("Re-downloading ephemeris file...")
                    self.eph = cast("SpiceKernel", loader(ephemeris_file))
                else:
                    raise
        except Exception as e:
            msg = f"Failed to initialize astronomical data. Check your internet connection or disk space to download the ephemeris file. Error: {e}"
            raise RuntimeError(msg) from e


# ---------------------------------------------------------------------------
# Module-level configuration state
# ---------------------------------------------------------------------------

# Auto-load .env on first import (no-op when python-dotenv is not installed).
_try_load_dotenv()


_LiteralStrT = TypeVar("_LiteralStrT", bound=str)


def _validated_str(key: str, default: _LiteralStrT, valid: frozenset[str]) -> _LiteralStrT:
    val = os.getenv(key, default)
    if val not in valid:
        msg = f"{key} must be one of {sorted(valid)}, got {val!r}"
        raise ValueError(msg)
    return cast("_LiteralStrT", val)


# ---------------------------------------------------------------------------
# Module-level settings instance and Skyfield singletons
# ---------------------------------------------------------------------------

settings = EngineSettings.from_env()

# Populate the field cache now that EngineSettingsOverride is defined.
_OVERRIDE_FIELDS = fields(EngineSettingsOverride)

_ndastro_config = ConfigurationManager()
ts = _ndastro_config.ts
eph = _ndastro_config.eph


def configure(
    override: EngineSettingsOverride | None = None,
    *,
    env_file: str | Path | None = None,
) -> None:
    """Configure the ndastro_engine at application start time.

    Call this once before invoking any engine functions — typically in a
    FastAPI lifespan handler or an application entry point — to apply
    settings programmatically rather than relying solely on environment
    variables.

    Settings are resolved in this order:

    1. Load *env_file* (if given) into ``os.environ``.
    2. Read all settings from ``NDASTRO_*`` environment variables.
    3. Apply only the non-``None`` fields from *override* on top.

    Correspondence to JHora.ini ``[CalculationPreferences]`` — see
    :class:`EngineSettings` for the full field-to-key mapping.

    Args:
        override: An :class:`EngineSettingsOverride` with the fields you want
            to force.  Fields left as ``None`` keep the value from the
            environment.  When ``None`` itself, env vars alone are used.
        env_file: Path to a ``.env`` file to load before applying settings.
            Only loaded when explicitly provided.

    Raises:
        ValueError: If a resolved string value is not in its valid set
            (raised by :meth:`EngineSettings.__post_init__`).

    """
    if env_file is not None:
        _try_load_dotenv(env_file)

    base = EngineSettings.from_env()
    if override is not None:
        updates = {f.name: v for f in _OVERRIDE_FIELDS if (v := getattr(override, f.name)) is not None}
        _self.settings = replace(base, **updates)
    else:
        _self.settings = base


# ---------------------------------------------------------------------------
# Per-request settings override via Python contextvars
# ---------------------------------------------------------------------------

#: Holds a per-asyncio-task (per-request) settings override.  ``None`` means
#: "use the module-level :data:`settings`".
_request_settings: ContextVar["EngineSettings | None"] = ContextVar("_request_settings", default=None)


def get_effective_settings() -> "EngineSettings":
    """Return the settings in effect for the current task / thread.

    If a per-request override has been registered via :func:`override_settings`
    it is returned; otherwise the module-level :data:`settings` is returned.
    This function is the single authoritative accessor used by engine internals
    so that per-request overrides are always honoured without touching the
    global state.
    """
    return _request_settings.get() or _self.settings


@contextmanager
def override_settings(override: "EngineSettingsOverride") -> "Generator[EngineSettings, None, None]":
    """Context manager that applies *override* for the duration of the ``with`` block.

    Thread- and async-safe: the override is stored in a :class:`~contextvars.ContextVar`
    which is scoped to the current asyncio task, so concurrent requests are
    completely isolated.

    Example (inside a FastAPI endpoint)::

        with override_settings(EngineSettingsOverride(node_type="mean")) as s:
            results = get_lunar_node_positions(dt)

    Args:
        override: An :class:`EngineSettingsOverride` specifying which fields to
            change.  Only non-``None`` fields are applied; the rest are inherited
            from the current effective settings.

    Yields:
        The resulting :class:`EngineSettings` that is active for the block.

    """
    base = get_effective_settings()
    updates = {f.name: v for f in _OVERRIDE_FIELDS if (v := getattr(override, f.name)) is not None}
    if not updates:
        # Nothing to override — avoid object allocation and just yield current settings.
        yield base
        return
    new_settings = replace(base, **updates)
    token = _request_settings.set(new_settings)
    try:
        yield new_settings
    finally:
        _request_settings.reset(token)
