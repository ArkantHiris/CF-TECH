import enum
from datetime import datetime, UTC
from typing import Optional
from sqlmodel import SQLModel, Field

class StatutInscription(str, enum.Enum):
    """
    Liste des différents statuts de l'inscription d'un apprenant
    """

    en_attente = "En attente"
    confirmee = "Confirmée"
    annulee = "Annulée"
    terminee = "Terminée"


class Inscription(SQLModel, table=True):
    """
    Classe représentant les inscriptions
    Table créée physiquement ( d'où le table=True )
    """

    __tablename__ = "inscription"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    date_inscription: datetime =  Field(default_factory=lambda: datetime.now(UTC))
    statut: StatutInscription = Field(default=StatutInscription.en_attente)

    # Clés étrangères pour lier l'apprenant à la session
    apprenant_id: int = Field(foreign_key="apprenant.id")
    session_id: int = Field(foreign_key="session.id")