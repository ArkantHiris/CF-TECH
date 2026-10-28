# Importer les outils nécessaires pour valider les données
from pydantic import BaseModel, Field
from sqlmodel import SQLModel, Field
from typing import Any
from sqlalchemy import JSON


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

