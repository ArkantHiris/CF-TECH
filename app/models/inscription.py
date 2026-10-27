import enum
from datetime import datetime, UTC
from typing import Optional
from sqlalchemy import UniqueConstraint
from sqlmodel import SQLModel, Field

class StatutInscription(str, enum.Enum):
    """
    Liste des différents statuts de l'inscription d'un apprenant
    """

    en_attente = "En attente"
    confirmee = "Confirmée"
    annulee = "Annulée"
    terminee = "Terminée"


"""
Famille de classes représentant les inscriptions
La diviser en plusieurs classes permet à Pydantic de controler les valeurs sans multiplier les validates
En effet, table=True retire le controle de Pydantic
"""
class InscriptionBase(SQLModel):

    date_inscription: datetime = Field(default_factory=lambda: datetime.now(UTC))
    statut: StatutInscription = Field(default=StatutInscription.en_attente)

    # Clés étrangères pour lier l'apprenant à la session
    apprenant_id: int = Field(foreign_key="apprenant.id", gt=0)
    session_id: int = Field(foreign_key="session_cours.id", gt=0)


# C'est ici que l'on crée la table physiquement
class Inscription(InscriptionBase, table=True):

    __tablename__ = "inscription"

    # attribut de SQLAlchemy comme tablename, permet de les passer en colonne
    __table_args__ = (
        # contrainte d'unicité, et la virgule est obligatoire car table_args a besoin d'un tuple
        UniqueConstraint("apprenant_id", "session_id"),
    )

    id: Optional[int] = Field(default=None, primary_key=True, index=True)