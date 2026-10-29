from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.models import Salle, Formateur, SessionCours
from app.enums import StatutSession
from app.schemas.session_schemas import SessionCoursBase


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


def creer_session_cours(db: Session, donnees: dict[str, Any]) -> SessionCours:
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
    verifier_formateur_disponible(db, s.formateur_id, s.date_debut, s.date_fin)
    verifier_salle_disponible(db, s.salle_id, s.date_debut, s.date_fin)
    return s

def modifier_session_cours(
    db: Session, session_id: int, changements: dict[str, Any]
) -> SessionCours:
    s = db.get(SessionCours, session_id)
    if s is None:
        raise ValueError(f"La session {session_id} n'existe pas")

    # Validation de l'état final : champs + date_debut < date_fin
    donnees = s.model_dump(exclude={"id"}) | changements
    SessionCoursBase.model_validate(donnees)

    # Salle : existence et capacité
    salle = db.get(Salle, donnees["salle_id"])
    if salle is None:
        raise ValueError(f"La salle {donnees['salle_id']} n'existe pas")
    if donnees["capacite_max"] > salle.capacite:
        raise ValueError(
            f"capacite_max ({donnees['capacite_max']}) supérieure à la capacité "
            f"de la salle « {salle.nom} » ({salle.capacite})"
        )

    # Formateur : existence
    if db.get(Formateur, donnees["formateur_id"]) is None:
        raise ValueError(f"Le formateur {donnees['formateur_id']} n'existe pas")

    # Disponibilités, en excluant la session elle-même
    verifier_formateur_disponible(
        db, donnees["formateur_id"], donnees["date_debut"], donnees["date_fin"], ignorer_id=session_id
    )
    verifier_salle_disponible(
        db, donnees["salle_id"], donnees["date_debut"], donnees["date_fin"], ignorer_id=session_id
    )

    s.sqlmodel_update(changements)
    db.add(s)
    db.flush()
    return s

def lire_session(db: Session, session_id: int) -> SessionCours | None:
    return db.get(SessionCours, session_id)


def lister_sessions(db: Session) -> list[SessionCours]:
    return db.exec(select(SessionCours)).all()


def changer_statut_session(
    db: Session, session_id: int, nouveau_statut: StatutSession
) -> SessionCours:
    s = db.get(SessionCours, session_id)
    if s is None:
        raise ValueError(f"La session {session_id} n'existe pas")
    if s.statut == StatutSession.ARCHIVED and nouveau_statut != StatutSession.ARCHIVED:
        raise ValueError("Une session archivée ne peut pas être rouverte")
    s.statut = nouveau_statut
    db.add(s)
    db.flush()
    return s


def archiver_session(db: Session, session_id: int) -> SessionCours:
    return changer_statut_session(db, session_id, StatutSession.ARCHIVED)