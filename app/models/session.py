import enum
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field

class StatutSession(str, enum.Enum):
    """
    Liste des différents statuts pour une session de cours
    """

    planifiee = "Planifiée"
    en_cours = "En cours"
    terminee = "Terminée"
    annulee = "Annulée"
    

class Session(SQLModel, table=True):
    """
    Classe représentant les sessions
    Table créée physiquement ( d'où le table=True )
    """

    __tablename__ = "session"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    titre: str = Field(max_length=100)
    date_debut: datetime
    date_fin: datetime
    statut: StatutSession = Field(default=StatutSession.planifiee)

    # Clés étrangères vers les tables Salle et Formateur
    salle_id: int = Field(foreign_key="salle.id")
    formateur_id: int = Field(foreign_key="formateur.id")