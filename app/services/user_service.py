from typing import Any, TypeVar

from sqlmodel import Session, SQLModel, select

from app.models import Apprenant, Formateur, StaffPedagogique, Admin
from app.schemas.user_schemas import (
    ApprenantBase,
    FormateurBase,
    StaffPedagogiqueBase,
    AdminBase,
)

T = TypeVar("T", bound=SQLModel)

# Les quatre tables d'utilisateurs (pour l'unicité globale de l'email)
TABLES_UTILISATEURS = (Apprenant, Formateur, StaffPedagogique, Admin)

# Champs qu'on ne peut jamais modifier après la création
CHAMPS_NON_MODIFIABLES = {"id", "role", "date_creation"}


# =====================================================================
# Fonctions génériques (écrites une fois, utilisées par les 4 types)
# =====================================================================

def _verifier_email_libre(db: Session, email: str, ignorer: tuple[type, int] | None = None) -> None:
    """
    Vérifie qu'aucun utilisateur (de n'importe quel type) n'a déjà cet email.
    `ignorer` = (table, id) de l'utilisateur en cours de modification.
    """
    for table in TABLES_UTILISATEURS:
        conditions = [table.email == email]
        if ignorer and ignorer[0] is table:
            conditions.append(table.id != ignorer[1])
        if db.exec(select(table).where(*conditions)).first():
            raise ValueError(f"L'email « {email} » est déjà utilisé")


def _creer(db: Session, table: type[T], donnees: dict[str, Any]) -> T:
    objet = table.model_validate(donnees)       # règles Pydantic héritées de la Base
    _verifier_email_libre(db, objet.email)
    db.add(objet)
    db.flush()                                  # id disponible, pas de commit
    return objet


def _lire(db: Session, table: type[T], user_id: int) -> T | None:
    return db.get(table, user_id)


def _lister(db: Session, table: type[T], actifs_seulement: bool = False) -> list[T]:
    requete = select(table)
    if actifs_seulement:
        requete = requete.where(table.is_active == True)  # noqa: E712
    return list(db.exec(requete).all())


def _modifier(
    db: Session, table: type[T], base: type[SQLModel], user_id: int, changements: dict[str, Any]
) -> T:
    objet = db.get(table, user_id)
    if objet is None:
        raise ValueError(f"{table.__name__} {user_id} introuvable")

    interdits = CHAMPS_NON_MODIFIABLES & changements.keys()
    if interdits:
        raise ValueError(f"Champ(s) non modifiable(s) : {', '.join(sorted(interdits))}")

    # Validation de l'état final (existant + changements) avec les règles de la Base
    donnees = objet.model_dump(exclude={"id"}) | changements
    base.model_validate(donnees)

    if "email" in changements:
        _verifier_email_libre(db, donnees["email"], ignorer=(table, user_id))

    objet.sqlmodel_update(changements)
    db.add(objet)
    db.flush()
    return objet


def _desactiver(db: Session, table: type[T], user_id: int) -> T:
    """Suppression logique : on garde l'historique (inscriptions, sessions...)."""
    objet = db.get(table, user_id)
    if objet is None:
        raise ValueError(f"{table.__name__} {user_id} introuvable")
    objet.is_active = False
    db.add(objet)
    db.flush()
    return objet


# =====================================================================
# Apprenant
# =====================================================================

def creer_apprenant(db: Session, donnees: dict[str, Any]) -> Apprenant:
    return _creer(db, Apprenant, donnees)

def lire_apprenant(db: Session, user_id: int) -> Apprenant | None:
    return _lire(db, Apprenant, user_id)

def lister_apprenants(db: Session, actifs_seulement: bool = False) -> list[Apprenant]:
    return _lister(db, Apprenant, actifs_seulement)

def modifier_apprenant(db: Session, user_id: int, changements: dict[str, Any]) -> Apprenant:
    return _modifier(db, Apprenant, ApprenantBase, user_id, changements)

def desactiver_apprenant(db: Session, user_id: int) -> Apprenant:
    return _desactiver(db, Apprenant, user_id)


# =====================================================================
# Formateur
# =====================================================================

def creer_formateur(db: Session, donnees: dict[str, Any]) -> Formateur:
    return _creer(db, Formateur, donnees)

def lire_formateur(db: Session, user_id: int) -> Formateur | None:
    return _lire(db, Formateur, user_id)

def lister_formateurs(db: Session, actifs_seulement: bool = False) -> list[Formateur]:
    return _lister(db, Formateur, actifs_seulement)

def modifier_formateur(db: Session, user_id: int, changements: dict[str, Any]) -> Formateur:
    return _modifier(db, Formateur, FormateurBase, user_id, changements)

def desactiver_formateur(db: Session, user_id: int) -> Formateur:
    return _desactiver(db, Formateur, user_id)


# =====================================================================
# Staff pédagogique
# =====================================================================

def creer_staff(db: Session, donnees: dict[str, Any]) -> StaffPedagogique:
    return _creer(db, StaffPedagogique, donnees)

def lire_staff(db: Session, user_id: int) -> StaffPedagogique | None:
    return _lire(db, StaffPedagogique, user_id)

def lister_staffs(db: Session, actifs_seulement: bool = False) -> list[StaffPedagogique]:
    return _lister(db, StaffPedagogique, actifs_seulement)

def modifier_staff(db: Session, user_id: int, changements: dict[str, Any]) -> StaffPedagogique:
    return _modifier(db, StaffPedagogique, StaffPedagogiqueBase, user_id, changements)

def desactiver_staff(db: Session, user_id: int) -> StaffPedagogique:
    return _desactiver(db, StaffPedagogique, user_id)


# =====================================================================
# Admin
# =====================================================================

def creer_admin(db: Session, donnees: dict[str, Any]) -> Admin:
    return _creer(db, Admin, donnees)

def lire_admin(db: Session, user_id: int) -> Admin | None:
    return _lire(db, Admin, user_id)

def lister_admins(db: Session, actifs_seulement: bool = False) -> list[Admin]:
    return _lister(db, Admin, actifs_seulement)

def modifier_admin(db: Session, user_id: int, changements: dict[str, Any]) -> Admin:
    return _modifier(db, Admin, AdminBase, user_id, changements)

def desactiver_admin(db: Session, user_id: int) -> Admin:
    return _desactiver(db, Admin, user_id)