from typing import Optional
from sqlmodel import Field

from app.schemas.salle_schemas import SalleBase


class Salle(SalleBase, table=True):
    """
    Class permettant la création physique de la table salle, table = true
    """
    
    __tablename__ = "salle"

    id: Optional[int] = Field(default=None, primary_key=True)