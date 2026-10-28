import re
from datetime import datetime, date, UTC
from typing import Optional
from pydantic import field_validator
from sqlmodel import SQLModel, Field

from app.enums import Role, NiveauEtude, Postes, NiveauAcces


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
    def naissance_dans_le_passe(cls, v: date) -> date:
        if v >= date.today():
            raise ValueError("La date de naissance doit être dans le passé")
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