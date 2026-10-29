from datetime import datetime
from typing import Any

from sqlmodel import Session, select

from app.models import Salle, Formateur, SessionCours
from app.enums import StatutSession
from app.schemas.session_schemas import SessionCoursBase


def verifier_formateur_disponible(db: Session,formateur_id: int,date_debut: datetime,date_fin: datetime,ignorer_id: int | None = None,) -> None:
    """
    Donne une ValueError si le formateur a déjà une session qui chevauche [date_debut, date_fin]
    """

    conditions = [
        SessionCours.formateur_id == formateur_id,
        SessionCours.date_debut < date_fin,
        SessionCours.date_fin > date_debut,
    ]

    # Permet d'éviter de comparer une session de cours avec elle même
    if ignorer_id is not None:

        conditions.append(SessionCours.id != ignorer_id)

    # On effectue la requête
    conflit = db.exec(select(SessionCours).where(*conditions)).first()
    # Si un seul résultat existe, on lève l'erreur
    if conflit:

        raise ValueError(

            f"Le formateur {formateur_id} est déjà pris par la session « {conflit.titre} »"
            f"({conflit.date_debut} → {conflit.date_fin})"
        )


def verifier_salle_disponible(db: Session,salle_id: int,date_debut: datetime,date_fin: datetime,ignorer_id: int | None = None,) -> None:
    """
    Donne une ValueError si la salle est déjà occupée sur [date_debut, date_fin]
    """

    conditions = [
        SessionCours.salle_id == salle_id,
        SessionCours.date_debut < date_fin,
        SessionCours.date_fin > date_debut,
    ]

    # Permet d'éviter de comparer une session à elle même
    if ignorer_id is not None:
        conditions.append(SessionCours.id != ignorer_id)

    # On effectue la requête
    conflit = db.exec(select(SessionCours).where(*conditions)).first()
    # Si une seul résultat existe, on lève l'erreur
    if conflit:

        raise ValueError(

            f"La salle {salle_id} est déjà occupée par la session "
            f"« {conflit.titre} » ({conflit.date_debut} → {conflit.date_fin})"
        )


def creer_session_cours(db: Session, donnees: dict[str, Any]) -> SessionCours:
    """
    On crée une session de cours, si les data passent toutes les vérifs
    """

    # 1. Validation Pydantic
    session_a_creer = SessionCours.model_validate(donnees)

    # 2. Salle existe
    salle = db.get(Salle, session_a_creer.salle_id)
    if salle is None:
        raise ValueError(f"La salle {session_a_creer.salle_id} n'existe pas")

    # 3. Capacité de salle
    if session_a_creer.capacite_max > salle.capacite:
        
        raise ValueError(
            f"capacite_max ({session_a_creer.capacite_max}) supérieure à la capacité de la salle :"
            f"« {salle.nom} » ({salle.capacite})"
        )

    # 4. Le formateur existe
    if db.get(Formateur, session_a_creer.formateur_id) is None:

        raise ValueError(f"Le formateur {session_a_creer.formateur_id} n'existe pas")

    # 5. Formateur disponible ?
    verifier_formateur_disponible(db, session_a_creer.formateur_id, session_a_creer.date_debut, session_a_creer.date_fin)

    # 6. Salle disponible ?
    verifier_salle_disponible(db, session_a_creer.salle_id, session_a_creer.date_debut, session_a_creer.date_fin)

    return session_a_creer


def modifier_session_cours(db: Session, session_id: int, changements: dict[str, Any]) -> SessionCours:
    """
    Permet de modifier les champs modifiables d'une row dans la table session cours
    """

    session_modif = db.get(SessionCours, session_id)

    # On vérifie si la session de cours existe
    if session_modif is None:

        raise ValueError(f"La session {session_id} n'existe pas")

    # On exclue l'id pour les changements à effectuer
    donnees = session_modif.model_dump(exclude={"id"}) | changements

    # Validation des modif par pydantic
    SessionCoursBase.model_validate(donnees)

    salle = db.get(Salle, donnees["salle_id"])
    # On vérifie si la salle existe
    if salle is None:
        raise ValueError(f"La salle {donnees['salle_id']} n'existe pas")

    # Si elle a toujours de la capacité
    if donnees["capacite_max"] > salle.capacite:

        raise ValueError(

            f"capacite_max ({donnees['capacite_max']}) supérieure à la capacité "
            f"de la salle « {salle.nom} » ({salle.capacite})"
        )

    # On vérifie si le formateur existe
    if db.get(Formateur, donnees["formateur_id"]) is None:

        raise ValueError(f"Le formateur {donnees['formateur_id']} n'existe pas")

    # On vérifie si le formateur est disponible (en excluant cette même formation)
    verifier_formateur_disponible(
        db, donnees["formateur_id"], donnees["date_debut"], donnees["date_fin"], ignorer_id=session_id
    )
    # On vérifie si la salle est disponible (en excluant cette même salle)
    verifier_salle_disponible(
        db, donnees["salle_id"], donnees["date_debut"], donnees["date_fin"], ignorer_id=session_id
    )

    session_modif.sqlmodel_update(changements)

    db.add(session_modif)
    # Car on a l'id
    db.flush()
    return session_modif

def lire_session(db: Session, session_id: int) -> SessionCours | None:
    """
    Permet de lire une ligne de la table session cours
    """

    return db.get(SessionCours, session_id)


def lister_sessions(db: Session) -> list[SessionCours]:
    """
    Permet d'afficher une liste de la table session cours
    """

    return db.exec(select(SessionCours)).all()


def changer_statut_session(db: Session, session_id: int, nouveau_statut: StatutSession) -> SessionCours:
    """
    Permet de changer le statut d'une session 
    """

    session_modif = db.get(SessionCours, session_id)

    # On vérifie si la session existe
    if session_modif is None:

        raise ValueError(f"La session {session_id} n'existe pas")

    # On vérifie si la session n'est pas archivée (donc non réouvrable par exemple)
    if session_modif.statut == StatutSession.ARCHIVED:

        raise ValueError("Une session archivée ne peut pas être rouverte")
    
    session_modif.statut = nouveau_statut

    db.add(session_modif)
    # Car on a l'id
    db.flush()
    return session_modif


def archiver_session(db: Session, session_id: int) -> SessionCours:
    """
    Change le statut d'une session en archivée
    """

    return changer_statut_session(db, session_id, StatutSession.ARCHIVED)