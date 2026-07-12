from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class StrengthComponents(BaseModel):
    dignity_bonus: float = 0.0
    combust_penalty: float = 0.0
    retro_bonus: float = 0.0
    temp_friend_bonus: float = 0.0
    varga_bonus: float = 0.0


class PlanetStrength(BaseModel):
    planet: str
    dignity: Optional[str]
    functional_role: Optional[str]
    functional_score: Optional[float]
    combust: Optional[bool]
    retrograde: Optional[bool]
    temporary_friendship: Optional[str]
    strength: float = Field(..., ge=0.0, le=1.0)
    strength_components: Optional[StrengthComponents]


class HouseSummary(BaseModel):
    number: int
    sign: Optional[str]
    lord: Optional[str]
    occupants: List[str]
    lord_strength: Optional[float]
    benefic_pressure: float
    malefic_pressure: float
    aspected_by: List[str]
    house_score: float


class DerivedState(BaseModel):
    planets: Dict[str, PlanetStrength]
    houses: List[HouseSummary]
    functional_roles: Dict[str, Dict]
    relationships: Dict[str, List[Dict]]
    diagnostics: Dict[str, int]
