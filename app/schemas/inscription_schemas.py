# Importer les outils pour valider les données
from pydantic import BaseModel, Field

# Importer le type pour gérer les dates et des heures
from datetime import datetime

# Importer Literal pour limiter les valeurs possibles
from typing import Literal

# Importer les statuts définis dans le modèle SQLModel
from app.models.inscription import StatutInscription


# Définir le schéma pour créer une nouvelle inscription
class InscriptionCreate(BaseModel):
    # Date et l'heure de l'inscription
    date_inscription: datetime
    # Identifiant de l'apprenant
    apprenant_id: int
    # Identifiant de la session
    session_id: int

    # Statut de l'inscription: utiliser les mêmes statuts que dans le modèle SQLModèle
    statut: StatutInscription

# Schéma pour afficher une inscription existante
class InscriptionRead(InscriptionCreate):
    # Identifiant unique pour inscription
    id: int










