from typing import Any
# func donne accès aux fonction sql SUM COUNT etc
from sqlmodel import Session, select, func

from app.enums import StatutInscription
from app.models import Apprenant, SessionCours, Inscription


def creer_inscription(db: Session, donnees: dict[str, Any]) -> Inscription:
    """
    1. Validation Pydantic (champs, ids positifs)
    2. L'apprenant et la session existent
    3. La session n'est pas pleine (inscriptions annulées non comptées)
    """
    insc = Inscription.model_validate(donnees)

    if db.get(Apprenant, insc.apprenant_id) is None:
        raise ValueError(f"L'apprenant {insc.apprenant_id} n'existe pas")

    session_cours = db.get(SessionCours, insc.session_id)
    if session_cours is None:
        raise ValueError(f"La session {insc.session_id} n'existe pas")

    nb_inscrits = db.exec(
        select(func.count()).select_from(Inscription).where(
            Inscription.session_id == insc.session_id,
            Inscription.statut != StatutInscription.annulee,
        )
    ).one()
    if nb_inscrits >= session_cours.capacite_max:
        raise ValueError(
            f"La session « {session_cours.titre} » est complète "
            f"({session_cours.capacite_max} places)"
        )
    return insc