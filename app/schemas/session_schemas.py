# Importer les outils nécessaires pour valider les données
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Optional, Literal
from pydantic import model_validator
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


# Définir le schéma pour afficher une session
class SessionRead(BaseModel):

    # Identifiant unique de la session
    id: int

    # Titre de la session
    titre: str

    # Description facultative
    description: str | None

    # Date et heure de début
    date_debut: datetime

    # Date et heure de fin
    date_fin: datetime

    # Nombre maximum de participants
    capacite_max: int

    # Statut de la session
    statut: Literal["OPEN", "CLOSED", "ARCHIVED"]

    # Prérequis facultatifs
    prerequis: str | None

    # Identifiant du formateur
    id_1: int

    # Identifiant de la salle
    id_2: int