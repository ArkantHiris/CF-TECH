from typing import Any, TypeVar

from sqlmodel import Session, SQLModel, select

from app.models import Apprenant, Formateur, StaffPedagogique, Admin
from app.schemas.user_schemas import (
    ApprenantBase,
    FormateurBase,
    StaffPedagogiqueBase,
    AdminBase,
)

# Pour le typehint, renvoie une instance de la class
T = TypeVar("T", bound=SQLModel)

# Les quatre tables d'utilisateurs 
TABLES_UTILISATEURS = (Apprenant, Formateur, StaffPedagogique, Admin)

# Champs qu'on ne peut jamais modifier après la création
CHAMPS_NON_MODIFIABLES = {"id", "role", "date_creation"}


# Méthodes réutilisables dans les fonctions

def verifier_email_libre(db: Session, email: str, ignorer: tuple[type, int] | None = None) -> None:
    """
    Vérifie qu'aucun utilisateur  n'a déjà cet email.
    `ignorer` = (table, id) de l'utilisateur en cours de modification.
    """

    for table in TABLES_UTILISATEURS:
        conditions = [table.email == email]
        if ignorer and ignorer[0] is table:
            conditions.append(table.id != ignorer[1])
        if db.exec(select(table).where(*conditions)).first():
            raise ValueError(f"L'email « {email} » est déjà utilisé")


def creer(db: Session, table: type[T], donnees: dict[str, Any]) -> T:
    """
    Permet de créer la ligne dans la table correspondante
    """
    
     # règles Pydantic héritées de la Base
    objet = table.model_validate(donnees) 

    verifier_email_libre(db, objet.email)

    db.add(objet)
    # id disponible, pas de commit
    db.flush()  

    return objet


def lire(db: Session, table: type[T], user_id: int) -> T | None:
    """
    Permet de lire une ligne simple dans la table correspondante
    """

    return db.get(table, user_id)


def lister(db: Session, table: type[T], actifs_seulement: bool = False) -> list[T]:
    """
    Permet de lister les utilisateurs.
    Si 3e argument est true, alors on ne liste que les utilisateurs actifs
    """

    # Ici tous les users
    requete = select(table)

    if actifs_seulement:

        # ici on conditionne qu'ils soient actifs si c'est demandé
        requete = requete.where(table.is_active == True) 

    return list(db.exec(requete).all())


def modifier(db: Session, table: type[T], base: type[SQLModel], user_id: int, changements: dict[str, Any]) -> T:
    """
    Permet de modifier une ligne précise par id, dans une table
    """

    objet = db.get(table, user_id)

    # On s'assure que la ligne existe bien
    if objet is None:
        raise ValueError(f"{table.__name__} {user_id} introuvable")

    # On vérifie que c'est un champ modifiable
    interdits = CHAMPS_NON_MODIFIABLES & changements.keys()

    if interdits:

        raise ValueError(f"Champ(s) non modifiable(s) : {', '.join(sorted(interdits))}")


    # On retire l'id de la modif future, puis on applique les changements
    donnees = objet.model_dump(exclude={"id"}) | changements

    # On valide les données avec pydanthic
    base.model_validate(donnees)

    # Si changement de l'email, on vérife le format
    if "email" in changements:

        verifier_email_libre(db, donnees["email"], ignorer=(table, user_id))

    objet.sqlmodel_update(changements)

    db.add(objet)
    # Car on connait l'id
    db.flush()

    return objet


def desactiver(db: Session, table: type[T], user_id: int) -> T:
    """
    Désactivation d'un user
    Permet de garder l'historique des inscriptions
    """

    objet = db.get(table, user_id)

    # On vérifie que l'user existe bien
    if objet is None:

        raise ValueError(f"{table.__name__} {user_id} introuvable")
    
    objet.is_active = False

    db.add(objet)
    # Car on connaît l'id
    db.flush()

    return objet


"""
Fonctions permettant la création, lecture d'une ligne, la liste de plusieurs lignes, modification ou désactivation d'une ligne
Dans la table apprenant
"""

def creer_apprenant(db: Session, donnees: dict[str, Any]) -> Apprenant:
    return creer(db, Apprenant, donnees)

def lire_apprenant(db: Session, user_id: int) -> Apprenant | None:
    return lire(db, Apprenant, user_id)

def lister_apprenants(db: Session, actifs_seulement: bool = False) -> list[Apprenant]:
    return lister(db, Apprenant, actifs_seulement)

def modifier_apprenant(db: Session, user_id: int, changements: dict[str, Any]) -> Apprenant:
    return modifier(db, Apprenant, ApprenantBase, user_id, changements)

def desactiver_apprenant(db: Session, user_id: int) -> Apprenant:
    return desactiver(db, Apprenant, user_id)


"""
Fonctions permettant la création, lecture d'une ligne, la liste de plusieurs lignes, modification ou désactivation d'une ligne
Dans la table formateur
"""

def creer_formateur(db: Session, donnees: dict[str, Any]) -> Formateur:
    return creer(db, Formateur, donnees)

def lire_formateur(db: Session, user_id: int) -> Formateur | None:
    return lire(db, Formateur, user_id)

def lister_formateurs(db: Session, actifs_seulement: bool = False) -> list[Formateur]:
    return lister(db, Formateur, actifs_seulement)

def modifier_formateur(db: Session, user_id: int, changements: dict[str, Any]) -> Formateur:
    return modifier(db, Formateur, FormateurBase, user_id, changements)

def desactiver_formateur(db: Session, user_id: int) -> Formateur:
    return desactiver(db, Formateur, user_id)


"""
Fonctions permettant la création, lecture d'une ligne, la liste de plusieurs lignes, modification ou désactivation d'une ligne
Dans la table staff
"""

def creer_staff(db: Session, donnees: dict[str, Any]) -> StaffPedagogique:
    return creer(db, StaffPedagogique, donnees)

def lire_staff(db: Session, user_id: int) -> StaffPedagogique | None:
    return lire(db, StaffPedagogique, user_id)

def lister_staffs(db: Session, actifs_seulement: bool = False) -> list[StaffPedagogique]:
    return lister(db, StaffPedagogique, actifs_seulement)

def modifier_staff(db: Session, user_id: int, changements: dict[str, Any]) -> StaffPedagogique:
    return modifier(db, StaffPedagogique, StaffPedagogiqueBase, user_id, changements)

def desactiver_staff(db: Session, user_id: int) -> StaffPedagogique:
    return desactiver(db, StaffPedagogique, user_id)


"""
Fonctions permettant la création, lecture d'une ligne, la liste de plusieurs lignes, modification ou désactivation d'une ligne
Dans la table admin
"""

def creer_admin(db: Session, donnees: dict[str, Any]) -> Admin:
    return creer(db, Admin, donnees)

def lire_admin(db: Session, user_id: int) -> Admin | None:
    return lire(db, Admin, user_id)

def lister_admins(db: Session, actifs_seulement: bool = False) -> list[Admin]:
    return lister(db, Admin, actifs_seulement)

def modifier_admin(db: Session, user_id: int, changements: dict[str, Any]) -> Admin:
    return modifier(db, Admin, AdminBase, user_id, changements)

def desactiver_admin(db: Session, user_id: int) -> Admin:
    return desactiver(db, Admin, user_id)