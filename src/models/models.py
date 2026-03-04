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


class RankingIngest(BaseModel):
    """
    Représente le payload JSON attendu par POST /api/ingest/rankings.
    """
    team_name: str = Field(..., description="Nom de l'équipe")
    rank: int = Field(..., description="Position au classement")
    points: int = Field(default=0, description="Points totaux")
    matches_played: int = Field(default=0, description="Matchs joués")
    won: int = Field(default=0, description="Matchs gagnés")
    draws: int = Field(default=0, description="Matchs nuls")
    lost: int = Field(default=0, description="Matchs perdus")
    goals_for: int = Field(default=0, description="Buts marqués")
    goals_against: int = Field(default=0, description="Buts encaissés")
    goal_diff: int = Field(default=0, description="Différence de buts")
    category: str = Field(..., description="Clé de pivot pour le backend (ex: -18M)")
    pool_id: str = Field(..., description="ID technique de la poule (source)")
    official_phase_name: Optional[str] = None