from typing import Optional
from sqlmodel import SQLModel, Field

class Salle(SQLModel, table=True):
    """
    Classe représentant les salles
    Table créée physiquement ( d'où le table=True )
    """

    __tablename__ = "salle"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    nom: str = Field(unique=True, index=True, max_length=50)
    capacite: int
    localisation: str = Field(max_length=50)
    equipements: str = Field(max_length=50)
    is_active: Optional[bool] = Field(default=True)