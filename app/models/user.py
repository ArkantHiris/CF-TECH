from typing import Optional
from sqlmodel import Field

from app.schemas.user_schemas import (
    ApprenantBase,
    FormateurBase,
    StaffPedagogiqueBase,
    AdminBase,
)

class Apprenant(ApprenantBase, table=True):
    """Table créée physiquement"""
    __tablename__ = "apprenant"

    id: Optional[int] = Field(default=None, primary_key=True)


class Formateur(FormateurBase, table=True):
    __tablename__ = "formateur"

    id: Optional[int] = Field(default=None, primary_key=True)


class StaffPedagogique(StaffPedagogiqueBase, table=True):
    __tablename__ = "staff_pedagogique"

    id: Optional[int] = Field(default=None, primary_key=True)


class Admin(AdminBase, table=True):
    __tablename__ = "admin"

    id: Optional[int] = Field(default=None, primary_key=True)
