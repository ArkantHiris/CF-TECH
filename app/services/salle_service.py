from typing import Any

from sqlmodel import Session, select, func

from app.models import Salle, SessionCours
from app.schemas.salle_schemas import SalleBase

# Champs qu'on ne peut jamais modifier
CHAMPS_NON_MODIFIABLES = {"id"}


def _verifier_nom_libre(db: Session, nom: str, ignorer_id: int | None = None) -> None:
    """Message lisible avant que la contrainte UNIQUE de la base ne lève une IntegrityError."""
    conditions = [Salle.nom == nom]
    if ignorer_id is not None:
        conditions.append(Salle.id != ignorer_id)
    if db.exec(select(Salle).where(*conditions)).first():
        raise ValueError(f"Une salle nommée « {nom} » existe déjà")


def creer_salle(db: Session, donnees: dict[str, Any]) -> Salle:
    salle = Salle.model_validate(donnees)          # règles Pydantic de SalleBase
    _verifier_nom_libre(db, salle.nom)
    db.add(salle)
    db.flush()                                     # id disponible, pas de commit
    return salle


def lire_salle(db: Session, salle_id: int) -> Salle | None:
    return db.get(Salle, salle_id)


def lister_salles(db: Session, actives_seulement: bool = False) -> list[Salle]:
    requete = select(Salle)
    if actives_seulement:
        requete = requete.where(Salle.is_active == True)  # noqa: E712
    return list(db.exec(requete).all())


def modifier_salle(db: Session, salle_id: int, changements: dict[str, Any]) -> Salle:
    salle = db.get(Salle, salle_id)
    if salle is None:
        raise ValueError(f"La salle {salle_id} n'existe pas")

    interdits = CHAMPS_NON_MODIFIABLES & changements.keys()
    if interdits:
        raise ValueError(f"Champ(s) non modifiable(s) : {', '.join(sorted(interdits))}")

    # Validation de l'état final (existant + changements)
    donnees = salle.model_dump(exclude={"id"}) | changements
    SalleBase.model_validate(donnees)

    if "nom" in changements:
        _verifier_nom_libre(db, donnees["nom"], ignorer_id=salle_id)

    # On ne peut pas réduire la capacité sous celle d'une session existante
    if "capacite" in changements:
        trop_grandes = db.exec(
            select(func.count()).select_from(SessionCours).where(
                SessionCours.salle_id == salle_id,
                SessionCours.capacite_max > donnees["capacite"],
            )
        ).one()
        if trop_grandes:
            raise ValueError(
                f"{trop_grandes} session(s) de cette salle ont une capacite_max "
                f"supérieure à {donnees['capacite']}"
            )

    salle.sqlmodel_update(changements)
    db.add(salle)
    db.flush()
    return salle


def desactiver_salle(db: Session, salle_id: int) -> Salle:
    """Suppression logique : les sessions passées gardent leur salle."""
    salle = db.get(Salle, salle_id)
    if salle is None:
        raise ValueError(f"La salle {salle_id} n'existe pas")
    salle.is_active = False
    db.add(salle)
    db.flush()
    return salle