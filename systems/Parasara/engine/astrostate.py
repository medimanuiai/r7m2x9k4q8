from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class Location(BaseModel):
    place: Optional[str]
    latitude: Optional[float]
    longitude: Optional[float]
    timezone_offset_minutes: Optional[int]


class PlanetState(BaseModel):
    name: str
    sign: Optional[str]
    degree: Optional[float]
    house: Optional[int]
    dignity: Optional[str] = None
    strength: Optional[float] = None
    canonical_id: Optional[str] = None
    degree_norm: Optional[float] = None
    vargas: Optional[Dict[str, Any]] = None


class AstroState(BaseModel):
    metadata: Dict[str, Any]
    location: Optional[Location]
    lagna_sign: Optional[str]
    lagna_degree: Optional[float] = None
    planets: List[PlanetState] = []
    houses: List[Dict[str, Any]] = []
    diagnostics: Dict[str, Any] = {}
    # simple enrichment map for varga confirmations and derived fields
    enrichments: Dict[str, Any] = {}
    # Derived canonical state consolidating enrichments for rule engine
    derived: Optional[Dict[str, Any]] = None
