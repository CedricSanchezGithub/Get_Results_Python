from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

class MatchIngest(BaseModel):
    """
    Représente le payload JSON attendu par POST /api/ingest/matches.
    """
    match_date: datetime
    team_1_name: str
    team_1_score: Optional[int] = None
    team_2_name: str
    team_2_score: Optional[int] = None
    category: str = Field(..., description="Clé de pivot pour le backend (ex: -18M)")
    pool_id: str = Field(..., description="ID technique de la poule (source)")
    official_phase_name: Optional[str] = None
    round: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%dT%H:%M:%S')
        }