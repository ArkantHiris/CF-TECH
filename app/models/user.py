from typing import Optional
from sqlmodel import Field

from app.schemas.user_schemas import (
    ApprenantBase,
    FormateurBase,
    StaffPedagogiqueBase,
    AdminBase,
)


class Apprenant(ApprenantBase, table=True):
    """
    Class permettant la création physique de la table apprenant, table = true
    """

    # Nom de la table
    __tablename__ = "apprenant"

    # ID n'est donné qu'à cet instant de la création, optional est un directive de SQLModel
    id: Optional[int] = Field(default=None, primary_key=True)


class Formateur(FormateurBase, table=True):
    """
    Class permettant la création physique de la table formateur, table = true
    """

    __tablename__ = "formateur"

    id: Optional[int] = Field(default=None, primary_key=True)


class StaffPedagogique(StaffPedagogiqueBase, table=True):
    """
    Class permettant la création physique de la table staff pedagogique, table = true
    """

    __tablename__ = "staff_pedagogique"

    id: Optional[int] = Field(default=None, primary_key=True)


class Admin(AdminBase, table=True):
    """
    Class permettant la création physique de la table admin, table = true
    """

    __tablename__ = "admin"

    id: Optional[int] = Field(default=None, primary_key=True)
