from datetime import datetime, UTC
from typing import Optional
from pydantic import ConfigDict
from sqlmodel import SQLModel, Field
from app.enums import StatutInscription


class InscriptionBase(SQLModel):
    """
    Champs et règles de validation d'une inscription.
    Pas de table = True pour permette à Pydantic la validation dès l'instanciation
    """
    date_inscription: datetime = Field(default_factory=lambda: datetime.now(UTC))
    statut: StatutInscription = Field(default=StatutInscription.en_attente)

    # Clés étrangères pour lier l'apprenant à la session
    apprenant_id: int = Field(foreign_key="apprenant.id", gt=0)
    session_id: int = Field(foreign_key="session_cours.id", gt=0)


# Début read

class InscriptionRead(InscriptionBase):
    """
    Permet la lecture de la table inscription, pour une potentielle API
    """

    # Configdict permet à Pydantic d'accepter autre chose qu'un dict
    model_config = ConfigDict(from_attributes=True)
    id: int


# Début update

class InscriptionUpdate(SQLModel):
    """
    Seul le statut d'une inscription peut changer (en attente -> confirmée, annulée...)
    apprenant_id, session_id et date_inscription sont inchangeables 
    Pour changer d'apprenant ou de session, on annule l'inscription et on en crée une nouvelle
    """

    # extra="forbid" refuse tout autre champ.
    model_config = ConfigDict(extra="forbid")

    statut: Optional[StatutInscription] = None