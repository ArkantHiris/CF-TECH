import enum
from datetime import datetime, UTC, date
from typing import Optional
from sqlmodel import SQLModel, Field


# Définition des Énumérations ( des listes contenants les valeurs possibles et acceptées )
# Enum crée un objet enum grâce à la library enum, typage nécessaire pour SQLModel

class RoleEnum(str, enum.Enum):  
    """
    Liste des rôles possible pour un utilisateur, chaque rôle est lié à une classe
    """

    apprenant = "apprenant"
    formateur = "formateur"
    staff_pedagogique = "staff_pedagogique"
    admin = "admin"

class NiveauEtude(str, enum.Enum):
    """
    Liste des différents niveaux d'études possibles
    """

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
    """
    Liste des différents postes au staff de CF-Tech
    """

    responsable = "Responsable pédagogique"
    charge_projet = "Chargé(e) de Projet"

class NiveauAcces(str, enum.Enum):
    """
    Liste des niveaux d'accès disponibles
    """

    superadmin = "SUPERADMIN"
    admin_standard = "ADMIN_STANDART"



#  Modèle de base (Non créée physiquement)

class UserBase(SQLModel, table=False):
    """
    Classe parente des différents utilisateurs.
    Les classes enfants héritent des caractéristiques communes à toutes.
    Les classes enfants sont discriminer grâce à la colonne role ( clé polymorphique )
    Cet objet/table n'est pas créé(e) physiquement (d'où le table=False)
    """

    nom: str = Field(max_length=50)
    prenom: str = Field(max_length=50)
    email: str = Field(unique=True, index=True, max_length=50)
    date_creation: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = Field(default=True)
    role: RoleEnum



# Modèles Enfants (Seuls eux créent des tables physiques)

class Apprenant(UserBase, table=True):
    """
    Classe représentant les apprenants
    Table créée physiquement ( d'où le table=True )
    """

    __tablename__ = "apprenant"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    date_naissance: date
    niveau_etude: NiveauEtude
    date_inscription_plateforme: datetime = Field(default_factory=lambda: datetime.now(UTC))
    certification_obtenue: Optional[str] = Field(default=None, max_length=50)
    telephone: Optional[str] = Field(default=None, max_length=20)


class Formateur(UserBase, table=True):
    """
    Classe représentant les formateurs
    Table créée physiquement ( d'où le table=True )
    """

    __tablename__ = "formateur"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    specialite: str = Field(max_length=50)
    date_embauche: date
    taux_horaire: float
    bio: Optional[str] = Field(default=None, max_length=50)

class StaffPedagogique(UserBase, table=True):
    """
    Classe représentant le staff pédagogique
    Table créée physiquement ( d'où le table=True )
    """

    __tablename__ = "staff_pedagogique"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    poste: Postes
    date_prise_fonction: date
    responsabilites: Optional[str] = Field(default=None, max_length=50)

class Admin(UserBase, table=True):
    """
    Classe représentant les admins
    Table créée physiquement ( d'où le table=True )
    """

    __tablename__ = "admin"

    id: Optional[int] = Field(default=None, primary_key=True, index=True)
    niveau_acces: NiveauAcces
    date_promotion: str = Field(max_length=50)