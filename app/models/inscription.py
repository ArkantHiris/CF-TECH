from typing import Optional
from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from app.schemas.inscription_schemas import InscriptionBase


class Inscription(InscriptionBase, table=True):
    """
    Class permettant la création physique de la table inscription, table = true
    """

    __tablename__ = "inscription"

    # Pour éviter les doublons de cette combinaison de colonnes
    __table_args__ = (
        UniqueConstraint("apprenant_id", "session_id", name="uq_inscription_apprenant_session"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)