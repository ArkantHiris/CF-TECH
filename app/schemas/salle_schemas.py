# Importer les outils nécessaires pour valider les données
from pydantic import BaseModel, Field


# Définir le schéma pour créer une nouvelle salle
class SalleCreate(BaseModel):


    # Nom de la salle
    nom: str = Field(min_length=1)


    # Capacité minimale : 1 place
    capacite: int = Field(ge=1)


    # Localisation de la salle, limité à 50 caractères
    localisation: str = Field(min_length=1, max_length=50)


    # Equipements disponibles, limité à 50 caractères
    equipements: str = Field(max_length=50)


    # Indiquer si la salle est active, inactive ou non renseignée
    is_active: bool | None = None


# Définir le schéma pour afficher les informations d'une salle
class SalleRead(BaseModel):


    # Identifiant unique de la salle
    id: int


    # Nom de la salle, limité à 50 caractères
    nom: str = Field(min_length=1, max_length=50)


    # Capacité de la salle
    capacite: int


    # Localisation de la salle, limité à 50 caractères
    localisation: str = Field(min_length=1, max_length=50)


    # Equipements disponibles, limité à 50 caractères
    equipements: str = Field(max_length=50)

    # Indiquer si la salle est active, inactive ou non renseignée
    is_active: bool | None
    
    