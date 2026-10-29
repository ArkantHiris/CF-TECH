from datetime import datetime
from typing import Optional
from pydantic import ConfigDict, model_validator
from sqlalchemy import JSON
from sqlmodel import SQLModel, Field
from app.enums import StatutSession


class SessionCoursBase(SQLModel):
    """
    Champs et règles de validation d'une session.
    Pas de table=True : la validation Pydantic est active dès l'instanciation.
    """
    titre: str = Field(min_length=1, max_length=100)
    description: Optional[str] = Field(default=None)
    date_debut: datetime
    date_fin: datetime
    capacite_max: int = Field(gt=0)
    statut: StatutSession = Field(default=StatutSession.OPEN)
    prerequis: Optional[list[str]] = Field(default=None, sa_type=JSON)

    # Clés étrangères vers Salle et Formateur
    salle_id: int = Field(foreign_key="salle.id", gt=0)
    formateur_id: int = Field(foreign_key="formateur.id", gt=0)

    # mode="after" : l'objet existe, on peut comparer deux champs via self
    @model_validator(mode="after")
    def verifier_dates(self):
        if self.date_fin <= self.date_debut:
            raise ValueError("date_fin doit être postérieure à date_debut")
        return self


# Début read

class SessionCoursRead(SessionCoursBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# Début update

class SessionCoursUpdate(SQLModel):
    """
    Champs modifiables d'une session. Tous sont facultatifs ;
    extra="forbid" refuse les champs inconnus (dont "id").
    """
    model_config = ConfigDict(extra="forbid")

    titre: Optional[str] = Field(default=None, min_length=1, max_length=100)
    description: Optional[str] = None
    date_debut: Optional[datetime] = None
    date_fin: Optional[datetime] = None
    capacite_max: Optional[int] = Field(default=None, gt=0)
    statut: Optional[StatutSession] = None
    prerequis: Optional[list[str]] = None
    salle_id: Optional[int] = Field(default=None, gt=0)
    formateur_id: Optional[int] = Field(default=None, gt=0)