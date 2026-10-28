from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.models import Salle, Formateur, SessionCours


def verifier_formateur_disponible(
    db: Session,
    formateur_id: int,
    date_debut: datetime,
    date_fin: datetime,
    ignorer_id: int | None = None,
) -> None:
    """Lève une ValueError si le formateur a déjà une session qui chevauche [date_debut, date_fin]."""
    conditions = [
        SessionCours.formateur_id == formateur_id,
        SessionCours.date_debut < date_fin,
        SessionCours.date_fin > date_debut,
    ]
    if ignorer_id is not None:
        conditions.append(SessionCours.id != ignorer_id)

    conflit = db.exec(select(SessionCours).where(*conditions)).first()
    if conflit:
        raise ValueError(
            f"Le formateur {formateur_id} est déjà pris par la session "
            f"« {conflit.titre} » ({conflit.date_debut} → {conflit.date_fin})"
        )


def verifier_salle_disponible(
    db: Session,
    salle_id: int,
    date_debut: datetime,
    date_fin: datetime,
    ignorer_id: int | None = None,
) -> None:
    """Lève une ValueError si la salle est déjà occupée sur [date_debut, date_fin]."""
    conditions = [
        SessionCours.salle_id == salle_id,
        SessionCours.date_debut < date_fin,
        SessionCours.date_fin > date_debut,
    ]
    if ignorer_id is not None:
        conditions.append(SessionCours.id != ignorer_id)

    conflit = db.exec(select(SessionCours).where(*conditions)).first()
    if conflit:
        raise ValueError(
            f"La salle {salle_id} est déjà occupée par la session "
            f"« {conflit.titre} » ({conflit.date_debut} → {conflit.date_fin})"
        )


def creer_session_cours(
    db: Session, donnees: dict[str, Any], ignorer_id: int | None = None
) -> SessionCours:
    """
    1. Validation Pydantic (champs, date_debut < date_fin)
    2. La salle existe et capacite_max <= capacité de la salle
    3. Le formateur existe
    4. Ni la salle ni le formateur ne sont déjà pris sur ce créneau
    """
    # 1. Validation Pydantic
    s = SessionCours.model_validate(donnees)

    # 2. Salle : existence et capacité
    salle = db.get(Salle, s.salle_id)
    if salle is None:
        raise ValueError(f"La salle {s.salle_id} n'existe pas")
    if s.capacite_max > salle.capacite:
        raise ValueError(
            f"capacite_max ({s.capacite_max}) supérieure à la capacité "
            f"de la salle « {salle.nom} » ({salle.capacite})"
        )

    # 3. Formateur : existence
    if db.get(Formateur, s.formateur_id) is None:
        raise ValueError(f"Le formateur {s.formateur_id} n'existe pas")

    # 4. Disponibilités
    verifier_formateur_disponible(db, s.formateur_id, s.date_debut, s.date_fin, ignorer_id)
    verifier_salle_disponible(db, s.salle_id, s.date_debut, s.date_fin, ignorer_id)

    return s