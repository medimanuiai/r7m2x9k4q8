from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class Nakshatra(BaseModel):
    name: str
    pada: Optional[int]
    index: Optional[int]


class Planet(BaseModel):
    name: str
    sign: Optional[str]
    degree: Optional[float]
    house: Optional[int]
    nakshatra: Optional[Nakshatra]
    motion: Optional[Dict[str, Any]]
    flags: Optional[Dict[str, Any]]


class Metadata(BaseModel):
    birth_datetime_utc: Optional[str]
    birth_location: Dict[str, Any]
    ayanamsa: Optional[str] = None
    house_system: Optional[str] = None
    sidereal: Optional[bool] = None
    ephemeris_source: Optional[str] = None


class Lagna(BaseModel):
    sign: Optional[str]
    degree: Optional[float]


class Chart(BaseModel):
    metadata: Metadata
    lagna: Optional[Lagna]
    planets: List[Planet] = []
    houses: List[Any] = []
    aspects: Optional[List[Dict[str, Any]]] = None
    current_transits: Optional[Dict[str, Any]] = None
    vargas: Optional[Dict[str, Any]] = None
