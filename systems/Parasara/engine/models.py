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


# FWP01 opt-in models. The compatibility classes above retain their contracts.
from dataclasses import dataclass
from pydantic import ConfigDict


class StrictChart(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    metadata: Dict[str, Any]
    lagna: Dict[str, Any]
    planets: List[Dict[str, Any]]
    houses: List[Dict[str, Any]]
    aspects: List[Dict[str, Any]] = []
    vargas: Dict[str, Any] = {}
    current_transits: Dict[str, Any] = {}


@dataclass(frozen=True, order=True)
class StrictInputIssue:
    path: str
    code: str


@dataclass(frozen=True)
class StrictChartBatchItem:
    index: int
    chart: Optional[StrictChart]
    issues: tuple[StrictInputIssue, ...]


@dataclass(frozen=True)
class StrictChartBatchResult:
    records: tuple[StrictChartBatchItem, ...]

    @property
    def charts(self) -> tuple[StrictChart, ...]:
        return tuple(item.chart for item in self.records if item.chart is not None)

    @property
    def failures(self) -> tuple[StrictChartBatchItem, ...]:
        return tuple(item for item in self.records if item.issues)
