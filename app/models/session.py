import enum
from datetime import datetime
from typing import Optional
from pydantic import model_validator
from sqlmodel import SQLModel, Field

class StatutSession(str, enum.Enum):
    """
    Liste des différents statuts pour une session de cours
    """

    planifiee = "Planifiée"
    en_cours = "En cours"
    terminee = "Terminée"
    annulee = "Annulée"


"""
Famille de classes representant une session de cours
La diviser en plusieurs classes permet à Pydantic de controler les valeurs sans multiplier les validates
En effet, table=True retire le controle de Pydantic
"""
class SessionCoursBase(SQLModel):

    titre: str = Field(min_length=1, max_length=100)
    date_debut: datetime
    date_fin: datetime
    statut: StatutSession = Field(default=StatutSession.planifiee)

    # Clés étrangères vers les tables Salle et Formateur
    salle_id: int = Field(foreign_key="salle.id", gt=0)
    formateur_id: int = Field(foreign_key="formateur.id", gt=0)

    # Ici on peut utiliser self car le mode="after" de model_validator, attend la création de l'objet, vu que l'on veut comparer deux champs entre eux
    @model_validator(mode="after")
    def verifier_dates(self):
        if self.date_fin <= self.date_debut:
            raise ValueError("date_fin doit être postérieure à date_debut")
        return self


# C'est ici que l'on crée la table physiquement
class SessionCours(SessionCoursBase, table=True):

    __tablename__ = "session_cours"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)