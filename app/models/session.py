from typing import Optional
from sqlmodel import Field

from app.schemas.session_schemas import SessionCoursBase


class SessionCours(SessionCoursBase, table=True):
    """
    Class permettant la création physique de la table session_cours, table = true
    """

    __tablename__ = "session_cours"

    id: Optional[int] = Field(default=None, primary_key=True)