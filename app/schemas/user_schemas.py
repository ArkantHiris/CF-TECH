import re
from datetime import datetime, date, UTC
from typing import Optional
from pydantic import field_validator, ConfigDict
from sqlmodel import SQLModel, Field

from app.enums import Role, NiveauEtude, Postes, NiveauAcces

# Methode commune à plusieurs classes
def email_valide(mail_value: Optional[str]) -> Optional[str]:
    """
    Règle d'email commune aux schémas de création et de modification
    """

    if mail_value is not None and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", mail_value):

        raise ValueError("Adresse email invalide")
    
    return mail_value


# Début des models de base de chaque user 

class UserBase(SQLModel):
    """
    Champs et règles communes à tous les utilisateurs.
    Pas de table = True pour permette à Pydantic la validation dès l'instanciation
    """

    nom: str = Field(min_length=1, max_length=50)
    prenom: str = Field(min_length=1, max_length=50)
    email: str = Field(unique=True, index=True, max_length=50)
    date_creation: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    role: Role

    # Permet de vérifier si le mail respecte le format correct, cls plutôt que self car l'objet n'existe pas encore
    @field_validator("email")
    @classmethod
    def verifier_email(cls, mail_value: str) -> str:

        return email_valide(mail_value)



class ApprenantBase(UserBase):
    """
    Champs et règles spécifiques à l'utilisateur Apprenant
    Hérite des règles et champs de UserBase
    Pas de table = True pour permettre la validation Pydantic dès l'instanciation
    """
    date_naissance: date
    niveau_etude: NiveauEtude
    date_inscription_plateforme: datetime = Field(default_factory=lambda: datetime.now(UTC))
    certification_obtenue: Optional[str] = Field(default=None, max_length=50)
    telephone: Optional[str] = Field(default=None, max_length=20)


    # Permet de vérifier si le rôle est bon pour cette class, cls plutôt que self car l'objet n'existe pas encore
    @field_validator("role")
    @classmethod
    def verifier_role(cls, role_value: Role) -> Role:

        if role_value != Role.apprenant:

            raise ValueError("Le rôle doit être 'apprenant'")
        
        return role_value

    # Permet de vérifier si l'apprenant est bien agé de 16 ans minimum, cls plutôt que self car l'objet n'existe pas encore
    @field_validator("date_naissance")
    @classmethod
    def verifier_age_minimum(cls, age_value: date) -> date:

        aujourd_hui = date.today()

        # On part 16 ans en arrière pour voir si la personne était née
        try:

            date_limite = aujourd_hui.replace(year=aujourd_hui.year - 16)

        except ValueError:

            # gère les années bisextiles
            # pour mettre par défaut au 28 février
            date_limite = aujourd_hui.replace(
                year = aujourd_hui.year - 16, month=2, day=28
            )

        # Si la personne est née après la date limite, elle a moins de 16 ans
        if age_value > date_limite:
            raise ValueError(
                "L'apprenant doit avoir au moins 16 ans pour s'inscrire."
            )

        return age_value


class FormateurBase(UserBase):
    """
    Champs et règles spécifiques à l'utilisateur Formateur
    Hérite des règles et champs de UserBase
    Pas de table = True pour permettre la validation Pydantic dès l'instanciation
    """

    specialite: str = Field(min_length=1, max_length=50)
    date_embauche: date
    taux_horaire: float = Field(gt=0)
    bio: Optional[str] = Field(default=None, max_length=50)

    # Permet de vérifier si le rôle est bon pour cette class, cls plutôt que self car l'objet n'existe pas encore
    @field_validator("role")
    @classmethod
    def verifier_role(cls, role_value: Role) -> Role:

        if role_value != Role.formateur:

            raise ValueError("Le rôle doit être 'formateur'")
        
        return role_value

    # S'assure que la date d'embauche est crédible
    @field_validator("date_embauche")
    @classmethod
    def embauche_pas_dans_le_futur(cls, date_value: date) -> date:

        if date_value > date.today():

            raise ValueError("La date d'embauche ne peut pas être dans le futur")
        
        return date_value


class StaffPedagogiqueBase(UserBase):
    """
    Champs et règles spécifiques à l'utilisateur Staff pedagogique
    Hérite des règles et champs de UserBase
    Pas de table = True pour permettre la validation Pydantic dès l'instanciation
    """

    poste: Postes
    date_prise_fonction: date
    responsabilites: Optional[str] = Field(default=None, max_length=50)

    # Permet de vérifier si le rôle est bon pour cette class, cls plutôt que self car l'objet n'existe pas encore
    @field_validator("role")
    @classmethod
    def verifier_role(cls, role_value: Role) -> Role:

        if role_value != Role.staff_pedagogique:

            raise ValueError("Le rôle doit être 'staff_pedagogique'")
        
        return role_value


class AdminBase(UserBase):
    """
    Champs et règles spécifiques à l'utilisateur Admin
    Hérite des règles et champs de UserBase
    Pas de table = True pour permettre la validation Pydantic dès l'instanciation
    """

    niveau_acces: NiveauAcces
    date_promotion: date

    # Permet de vérifier si le rôle est bon pour cette class, cls plutôt que self car l'objet n'existe pas encore
    @field_validator("role")
    @classmethod
    def verifier_role(cls, role_value: Role) -> Role:

        if role_value != Role.admin:

            raise ValueError("Le rôle doit être 'admin'")
        
        return role_value


# Début des classes de lecture 
class ApprenantRead(ApprenantBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class FormateurRead(FormateurBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class StaffPedagogiqueRead(StaffPedagogiqueBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class AdminRead(AdminBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# Debut des class d'update 
class UserUpdateBase(SQLModel):
    """
    Champs modifiables communs à tous les utilisateurs
    role et date_creation n'y figurent pas
    Et extra="forbid" refuse tout champ inconnu : impossible donc de modifier le rôle
    """

    model_config = ConfigDict(extra="forbid")

    nom: Optional[str] = Field(default=None, min_length=1, max_length=50)
    prenom: Optional[str] = Field(default=None, min_length=1, max_length=50)
    email: Optional[str] = Field(default=None, max_length=50)
    is_active: Optional[bool] = None

    # Permet de vérifier si le mail respecte le format correct, cls plutôt que self car l'objet n'existe pas encore
    @field_validator("email")
    @classmethod
    def verifier_email(cls, mail_value: Optional[str]) -> Optional[str]:

        return email_valide(mail_value)


class ApprenantUpdate(UserUpdateBase):
    """
    Champs modifiables de l'apprenant
    """

    date_naissance: Optional[date] = None
    niveau_etude: Optional[NiveauEtude] = None
    certification_obtenue: Optional[str] = Field(default=None, max_length=50)
    telephone: Optional[str] = Field(default=None, max_length=20)

    # Permet de vérifier si l'apprenant est bien agé de 16 ans minimum, cls plutôt que self car l'objet n'existe pas encore
    @field_validator("date_naissance")
    @classmethod
    def verifier_age_minimum(cls, age_value: date) -> date:

        aujourd_hui = date.today()

        # On part 16 ans en arrière pour voir si la personne était née
        try:

            date_limite = aujourd_hui.replace(year=aujourd_hui.year - 16)

        except ValueError:

            # gère les années bisextiles
            # pour mettre par défaut au 28 février
            date_limite = aujourd_hui.replace(
                year = aujourd_hui.year - 16, month=2, day=28
            )

        # Si la personne est née après la date limite, elle a moins de 16 ans
        if age_value > date_limite:
            raise ValueError(
                "L'apprenant doit avoir au moins 16 ans pour s'inscrire."
            )

        return age_value


class FormateurUpdate(UserUpdateBase):
    """
    Champs modifiables du Formateur
    """

    specialite: Optional[str] = Field(default=None, min_length=1, max_length=50)
    date_embauche: Optional[date] = None
    taux_horaire: Optional[float] = Field(default=None, gt=0)
    bio: Optional[str] = Field(default=None, max_length=50)

    # S'assure que la date d'embauche est crédible
    @field_validator("date_embauche")
    @classmethod
    def embauche_pas_dans_le_futur(cls, date_value: date) -> date:
    
        if date_value > date.today():
    
            raise ValueError("La date d'embauche ne peut pas être dans le futur")
            
        return date_value


class StaffPedagogiqueUpdate(UserUpdateBase):
    """
    Champs modifiables du staff pédagogique
    """

    poste: Optional[Postes] = None
    date_prise_fonction: Optional[date] = None
    responsabilites: Optional[str] = Field(default=None, max_length=50)


class AdminUpdate(UserUpdateBase):
    """
    Champs modifiables de l'admin
    """

    niveau_acces: Optional[NiveauAcces] = None
    date_promotion: Optional[date] = None