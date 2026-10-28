import enum
from datetime import datetime, UTC, date
from typing import Optional
from pydantic import field_validator
from sqlmodel import SQLModel, Field


# Définition des Énumérations ( des listes contenants les valeurs possibles et acceptées )
# Enum crée un objet enum grâce à la library enum, typage nécessaire pour SQLModel
class Role(str, enum.Enum):
    """Rôles possibles pour un utilisateur"""
    apprenant = "apprenant"
    formateur = "formateur"
    staff_pedagogique = "staff_pedagogique"
    admin = "admin"


class NiveauEtude(str, enum.Enum):
    """Niveaux d'études possibles"""
    brevet = "Brevet"
    cap = "CAP"
    bep = "BEP"
    bac = "Bac"
    bac_1 = "Bac +1"
    bac_2 = "Bac +2"
    bac_3 = "Bac +3"
    bac_4 = "Bac +4"
    bac_5 = "Bac +5"
    bac_plus = "Bac +5 +"


class Postes(str, enum.Enum):
    """Postes au sein du staff de CF-Tech"""
    responsable = "Responsable pédagogique"
    charge_projet = "Chargé(e) de Projet"


class NiveauAcces(str, enum.Enum):
    """Niveaux d'accès disponibles"""
    superadmin = "SUPERADMIN"
    admin_standard = "ADMIN_STANDART"


# Modèle de base commun (pas de table)
class UserBase(SQLModel):
    """
    Champs et règles communes à tous les utilisateurs.
    Pas de table=True : la validation Pydantic est active.
    """
    nom: str = Field(min_length=1, max_length=50)
    prenom: str = Field(min_length=1, max_length=50)
    email: str = Field(
        unique=True, index=True, max_length=50,
        regex=r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
    )
    date_creation: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    role: Role


# Apprenant
"""
Famille de classes représentant l' apprenant
La diviser en plusieurs classes permet à Pydantic de controler les valeurs sans multiplier les validates
En effet, table=True retire le controle de Pydantic
"""
class ApprenantBase(UserBase):
    date_naissance: date
    niveau_etude: NiveauEtude
    date_inscription_plateforme: datetime = Field(default_factory=lambda: datetime.now(UTC))
    certification_obtenue: Optional[str] = Field(default=None, max_length=50)
    telephone: Optional[str] = Field(default=None, max_length=20)

    # Décorateurs (ils s'appliquent de bas en haut depuis la fonction)
    # classmethod est necessaire car self n'existe pas encore (field_validator et non model_validator), donc on utilise cls à la place
    # field_validator pour vérifier que le rôle est le bon pour cette classe
    @field_validator("role")
    @classmethod
    def verifier_role(cls, value):
        if value != Role.apprenant:
            raise ValueError("Le rôle doit être 'apprenant'")
        return value

    # Même principe qu'au dessus, mais on vérifie si la date de naissance est crédible
    @field_validator("date_naissance")
    @classmethod
    def naissance_dans_le_passe(cls, value):
        if value >= date.today():
            raise ValueError("La date de naissance doit être dans le passé")
        return value

# C'est ici que l'on crée la table physiquement
class Apprenant(ApprenantBase, table=True):

    __tablename__ = "apprenant"

    # Optional car c'est la base qui va créer l'id et non l'ORM
    id: Optional[int] = Field(default=None, primary_key=True, index=True)


# Formateur
"""
Famille de classes représentant le formateur
La diviser en plusieurs classes permet à Pydantic de controler les valeurs sans multiplier les validates
En effet, table=True retire le controle de Pydantic
"""
class FormateurBase(UserBase):
    specialite: str = Field(min_length=1, max_length=50)
    date_embauche: date
    taux_horaire: float = Field(gt=0)
    bio: Optional[str] = Field(default=None, max_length=50)

    @field_validator("role")
    @classmethod
    def verifier_role(cls, value):
        if value != Role.formateur:
            raise ValueError("Le rôle doit être 'formateur'")
        return value

    @field_validator("date_embauche")
    @classmethod
    def embauche_pas_dans_le_futur(cls, value):
        if value > date.today():
            raise ValueError("La date d'embauche ne peut pas être dans le futur")
        return value

# C'est ici que l'on crée la table physiquement
class Formateur(FormateurBase, table=True):

    __tablename__ = "formateur"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)


# Staff pédagogique 
"""
Famille de classes représentant le staff pédagogique
La diviser en plusieurs classes permet à Pydantic de controler les valeurs sans multiplier les validates
En effet, table=True retire le controle de Pydantic
"""
class StaffPedagogiqueBase(UserBase):
    poste: Postes
    date_prise_fonction: date
    responsabilites: Optional[str] = Field(default=None, max_length=50)

    @field_validator("role")
    @classmethod
    def verifier_role(cls, value):
        if value != Role.staff_pedagogique:
            raise ValueError("Le rôle doit être 'staff_pedagogique'")
        return value

# C'est ici que l'on crée la table physiquement
class StaffPedagogique(StaffPedagogiqueBase, table=True):
    __tablename__ = "staff_pedagogique"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)


# Admin 
"""
Famille de classes représentant l'admin'
La diviser en plusieurs classes permet à Pydantic de controler les valeurs sans multiplier les validates
En effet, table=True retire le controle de Pydantic
"""
class AdminBase(UserBase):
    niveau_acces: NiveauAcces
    date_promotion: date

    @field_validator("role")
    @classmethod
    def verifier_role(cls, value):
        if value != Role.admin:
            raise ValueError("Le rôle doit être 'admin'")
        return value

# C'est ici que l'on crée la table physiquement
class Admin(AdminBase, table=True):
    __tablename__ = "admin"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)