from datetime import datetime, UTC
from sqlmodel import SQLModel, Field

from app.enums import StatutInscription


class InscriptionBase(SQLModel):
    """
    Champs et règles de validation d'une inscription.
    Pas de table=True : la validation Pydantic est active dès l'instanciation.
    """
    date_inscription: datetime = Field(default_factory=lambda: datetime.now(UTC))
    statut: StatutInscription = Field(default=StatutInscription.en_attente)

    # Clés étrangères pour lier l'apprenant à la session
    apprenant_id: int = Field(foreign_key="apprenant.id", gt=0)
    session_id: int = Field(foreign_key="session_cours.id", gt=0)












