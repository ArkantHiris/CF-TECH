from typing import Optional
from sqlmodel import SQLModel, Field

"""
Famille de classes representant une salle
La diviser en plusieurs classes permet à Pydantic de controler les valeurs sans multiplier les validates
En effet, table=True retire le controle de Pydantic
"""
class SalleBase(SQLModel):

    #Champs et règles de validation (pas de table)
    nom: str = Field(unique=True, index=True, min_length=1, max_length=50)
    capacite: int = Field(gt=0)
    localisation: str = Field(max_length=50)
    equipements: str = Field(max_length=50)
    is_active: bool = True

# C'est ici que l'on crée la table physiquement
class Salle(SalleBase, table=True):
    
    __tablename__ = "salle"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
