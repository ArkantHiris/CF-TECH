from typing import Any, Optional

from pydantic import ConfigDict
from sqlalchemy import JSON
from sqlmodel import SQLModel, Field


class SalleBase(SQLModel):
    """
    Champs et règles de validation d'une salle.
    Pas de table=True : la validation Pydantic est active dès l'instanciation.
    """
    nom: str = Field(unique=True, index=True, min_length=1, max_length=50)
    capacite: int = Field(gt=0)
    localisation: str = Field(min_length=1, max_length=50)
    equipements: dict[str, Any] = Field(default_factory=dict, sa_type=JSON)
    is_active: bool = True


# Début read

class SalleRead(SalleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# Début update

class SalleUpdate(SQLModel):
    """
    Champs modifiables d'une salle. Tous sont facultatifs ;
    extra="forbid" refuse les champs inconnus (dont "id").
    """
    model_config = ConfigDict(extra="forbid")

    nom: Optional[str] = Field(default=None, min_length=1, max_length=50)
    capacite: Optional[int] = Field(default=None, gt=0)
    localisation: Optional[str] = Field(default=None, min_length=1, max_length=50)
    equipements: Optional[dict[str, Any]] = None
    is_active: Optional[bool] = None