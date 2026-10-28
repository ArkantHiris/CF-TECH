from typing import Optional
from sqlmodel import Field

from app.schemas.salle_schemas import SalleBase


class Salle(SalleBase, table=True):
    """Table créée physiquement"""
    __tablename__ = "salle"

    id: Optional[int] = Field(default=None, primary_key=True)