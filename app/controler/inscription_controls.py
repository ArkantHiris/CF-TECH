from typing import Any

from sqlmodel import Session, select, func

from app.enums import StatutInscription, StatutSession
from app.models import Apprenant, SessionCours, Inscription


def creer_inscription(db: Session, donnees: dict[str, Any]) -> Inscription:
    """
    1. Validation Pydantic (champs, ids positifs)
    2. L'apprenant et la session existent
    3. Pas de doublon (apprenant, session)
    4. Le statut de la session est OPEN
    5. La session n'est pas pleine (nb d'inscrits < capacite_max)
    6. Aucune autre session de l'apprenant ne chevauche celle-ci
    """
    # 1. Validation Pydantic
    insc = Inscription.model_validate(donnees)

    # 2. Existence
    if db.get(Apprenant, insc.apprenant_id) is None:
        raise ValueError(f"L'apprenant {insc.apprenant_id} n'existe pas")

    session_cours = db.get(SessionCours, insc.session_id)
    if session_cours is None:
        raise ValueError(f"La session {insc.session_id} n'existe pas")

    # 3. Unicité (message lisible ; la contrainte UNIQUE de la base reste le garde-fou)
    doublon = db.exec(
        select(Inscription).where(
            Inscription.apprenant_id == insc.apprenant_id,
            Inscription.session_id == insc.session_id,
        )
    ).first()
    if doublon:
        raise ValueError(
            f"L'apprenant {insc.apprenant_id} est déjà inscrit à la session "
            f"« {session_cours.titre} »"
        )

    # 4. Statut de la session
    if session_cours.statut != StatutSession.OPEN:
        raise ValueError(
            f"La session « {session_cours.titre} » n'est pas ouverte "
            f"(statut : {session_cours.statut.value})"
        )

    # 5. Places disponibles (inscriptions annulées non comptées)
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

    # 6. Chevauchement avec les autres sessions de l'apprenant
    #    (inscriptions annulées ignorées ; intervalles stricts : bout à bout autorisé)
    conflit = db.exec(
        select(SessionCours)
        .join(Inscription, Inscription.session_id == SessionCours.id)
        .where(
            Inscription.apprenant_id == insc.apprenant_id,
            Inscription.statut != StatutInscription.annulee,
            SessionCours.date_debut < session_cours.date_fin,
            SessionCours.date_fin > session_cours.date_debut,
        )
    ).first()
    if conflit:
        raise ValueError(
            f"L'apprenant {insc.apprenant_id} est déjà inscrit à « {conflit.titre} » "
            f"({conflit.date_debut} → {conflit.date_fin}), qui chevauche cette session"
        )

    return insc