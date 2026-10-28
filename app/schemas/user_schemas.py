import re
from datetime import datetime, date, UTC
from typing import Optional
from pydantic import field_validator, ConfigDict
from sqlmodel import SQLModel, Field

from app.enums import Role, NiveauEtude, Postes, NiveauAcces

# Methode commune à plusieurs classes
def _email_valide(v: Optional[str]) -> Optional[str]:
    """Règle d'email commune aux schémas de création et de modification."""
    if v is not None and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", v):
        raise ValueError("Adresse email invalide")
    return v


# Début des classes de creation
class UserBase(SQLModel):
    """
    Champs et règles communes à tous les utilisateurs.
    Pas de table=True : la validation Pydantic est active dès l'instanciation.
    """
    nom: str = Field(min_length=1, max_length=50)
    prenom: str = Field(min_length=1, max_length=50)
    email: str = Field(unique=True, index=True, max_length=50)
    date_creation: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_active: bool = True
    role: Role

    @field_validator("email")
    @classmethod
    def verifier_email(cls, v: str) -> str:
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", v):
            raise ValueError("Adresse email invalide")
        return v


class ApprenantBase(UserBase):
    date_naissance: date
    niveau_etude: NiveauEtude
    date_inscription_plateforme: datetime = Field(default_factory=lambda: datetime.now(UTC))
    certification_obtenue: Optional[str] = Field(default=None, max_length=50)
    telephone: Optional[str] = Field(default=None, max_length=20)

    @field_validator("role")
    @classmethod
    def verifier_role(cls, v: Role) -> Role:
        if v != Role.apprenant:
            raise ValueError("Le rôle doit être 'apprenant'")
        return v

    @field_validator("date_naissance")
    @classmethod
    def verifier_age_minimum(cls, v: date) -> date:
        aujourd_hui = date.today()

        # On part 16 ans en arrière pour voir si la personne était née
        try:
            date_limite = aujourd_hui.replace(year=aujourd_hui.year - 16)
        except ValueError:
            #gère les années bisextile
            date_limite = aujourd_hui.replace(
                year=aujourd_hui.year - 16, month=2, day=28
            )

        # Si la personne est née APRES la date limite, elle a moins de 16 ans
        if v > date_limite:
            raise ValueError(
                "L'apprenant doit avoir au moins 16 ans pour s'inscrire."
            )

        return v


class FormateurBase(UserBase):
    specialite: str = Field(min_length=1, max_length=50)
    date_embauche: date
    taux_horaire: float = Field(gt=0)
    bio: Optional[str] = Field(default=None, max_length=50)

    @field_validator("role")
    @classmethod
    def verifier_role(cls, v: Role) -> Role:
        if v != Role.formateur:
            raise ValueError("Le rôle doit être 'formateur'")
        return v

    @field_validator("date_embauche")
    @classmethod
    def embauche_pas_dans_le_futur(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("La date d'embauche ne peut pas être dans le futur")
        return v


class StaffPedagogiqueBase(UserBase):
    poste: Postes
    date_prise_fonction: date
    responsabilites: Optional[str] = Field(default=None, max_length=50)

    @field_validator("role")
    @classmethod
    def verifier_role(cls, v: Role) -> Role:
        if v != Role.staff_pedagogique:
            raise ValueError("Le rôle doit être 'staff_pedagogique'")
        return v


class AdminBase(UserBase):
    niveau_acces: NiveauAcces
    date_promotion: date

    @field_validator("role")
    @classmethod
    def verifier_role(cls, v: Role) -> Role:
        if v != Role.admin:
            raise ValueError("Le rôle doit être 'admin'")
        return v


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
    Champs modifiables communs à tous les utilisateurs.
    role et date_creation n'y figurent pas, et extra="forbid" refuse
    tout champ inconnu : impossible donc de modifier le rôle.
    """
    model_config = ConfigDict(extra="forbid")

    nom: Optional[str] = Field(default=None, min_length=1, max_length=50)
    prenom: Optional[str] = Field(default=None, min_length=1, max_length=50)
    email: Optional[str] = Field(default=None, max_length=50)
    is_active: Optional[bool] = None

    @field_validator("email")
    @classmethod
    def verifier_email(cls, v: Optional[str]) -> Optional[str]:
        return _email_valide(v)


class ApprenantUpdate(UserUpdateBase):
    date_naissance: Optional[date] = None
    niveau_etude: Optional[NiveauEtude] = None
    certification_obtenue: Optional[str] = Field(default=None, max_length=50)
    telephone: Optional[str] = Field(default=None, max_length=20)

    @field_validator("date_naissance")
    @classmethod
    def naissance_dans_le_passe(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v >= date.today():
            raise ValueError("La date de naissance doit être dans le passé")
        return v


class FormateurUpdate(UserUpdateBase):
    specialite: Optional[str] = Field(default=None, min_length=1, max_length=50)
    date_embauche: Optional[date] = None
    taux_horaire: Optional[float] = Field(default=None, gt=0)
    bio: Optional[str] = Field(default=None, max_length=50)

    @field_validator("date_embauche")
    @classmethod
    def embauche_pas_dans_le_futur(cls, v: Optional[date]) -> Optional[date]:
        if v is not None and v > date.today():
            raise ValueError("La date d'embauche ne peut pas être dans le futur")
        return v


class StaffPedagogiqueUpdate(UserUpdateBase):
    poste: Optional[Postes] = None
    date_prise_fonction: Optional[date] = None
    responsabilites: Optional[str] = Field(default=None, max_length=50)


class AdminUpdate(UserUpdateBase):
    niveau_acces: Optional[NiveauAcces] = None
    date_promotion: Optional[date] = None