# Importer les outils pour valider les données
from pydantic import BaseModel, Field

# Importer le type pour gérer les dates et des heures
from datetime import datetime

# Importer Literal pour limiter les valeurs possibles
from typing import Literal


# Définir le schéma pour créer une nouvelle inscription
class InscriptionCreate(BaseModel):
    # Date et l'heure de l'inscription
    date_inscription: datetime

    # Statut de l'inscription
    statut_inscription: Literal["ENREGISTRE", "DESINSCRIT", "EN_ATTENTE"]

# Schéma pour afficher une inscription existante
class InscriptionRead(InscriptionCreate):
    # Identifiant unique pour inscription
    id: int









