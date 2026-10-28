from typing import Optional
from sqlalchemy import UniqueConstraint
from sqlmodel import Field

from app.schemas.inscription_schemas import InscriptionBase


class Inscription(InscriptionBase, table=True):
    """Table créée physiquement"""
    __tablename__ = "inscription"
    __table_args__ = (
        UniqueConstraint("apprenant_id", "session_id", name="uq_inscription_apprenant_session"),
    )

    id: Optional[int] = Field(default=None, primary_key=True)