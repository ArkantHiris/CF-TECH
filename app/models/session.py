from typing import Optional
from sqlmodel import Field

from app.schemas.session_schemas import SessionCoursBase


class SessionCours(SessionCoursBase, table=True):
    """Table créée physiquement"""
    __tablename__ = "session_cours"

    id: Optional[int] = Field(default=None, primary_key=True)