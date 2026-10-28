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


# Définir le schéma pour afficher les informations d'une salle
class SalleRead(BaseModel):


    # Identifiant unique de la salle
    id: int


    # Nom de la salle, limité à 50 caractères
    nom: str = Field(min_length=1, max_length=50)


    # Capacité de la salle
    capacite: int


    # Localisation de la salle, limité à 50 caractères
    localisation: str = Field(min_length=1, max_length=50)


    # Equipements disponibles, limité à 50 caractères
    equipements: str = Field(max_length=50)

    # Indiquer si la salle est active, inactive ou non renseignée
    is_active: bool | None
    
    