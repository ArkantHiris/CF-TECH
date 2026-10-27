# Importer les outils nécessaires pour valider les données
from pydantic import BaseModel, Field, model_validator
from datetime import datetime
from typing import Literal


# Définir le schéma pour créer une nouvelle session
class SessionCreate(BaseModel):

    # Titre de la session
    titre: str = Field(min_length=1, max_length=100)

    # Description facultative de la session
    description: str | None = None

    # Date et heure de début de la session
    date_debut: datetime

    # Date et heure de fin de la session
    date_fin: datetime

    # Nombre maximum de participants
    capacite_max: int = Field(ge=1)

    # Statut de la session
    statut: Literal["OPEN", "CLOSED", "ARCHIVED"]

    # Prérequis facultatifs
    prerequis: str | None = None

    # Identifiant du formateur
    id_1: int

    # Identifiant de la salle
    id_2: int

    # Vérifier que la date de fin est après la date du début de la session
    @model_validator(mode="after")
    def verifier_dates(self):
        # comparer les deux dates
        if self.date_fin <= self.date_debut:
            raise ValueError("Start date must be before end date ")
        # Retourner l'objet si las dates sont valides
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