from typing import Any

from sqlmodel import Session, select, func

from app.enums import StatutInscription, StatutSession
from app.models import Apprenant, SessionCours, Inscription


# =====================================================================
# Règles réutilisables (création ET réactivation d'une inscription)
# =====================================================================

def verifier_inscription_existante(db: Session, apprenant_id: int, session_id: int) -> bool:
    """True si l'apprenant a déjà une inscription (même annulée) à cette session."""
    requete = select(Inscription).where(
        Inscription.apprenant_id == apprenant_id,
        Inscription.session_id == session_id,
    )
    return db.exec(requete).first() is not None


def _verifier_session_ouverte(session_cours: SessionCours) -> None:
    if session_cours.statut != StatutSession.OPEN:
        raise ValueError(
            f"La session « {session_cours.titre} » n'est pas ouverte "
            f"(statut : {session_cours.statut.value})"
        )


def _verifier_places(db: Session, session_cours: SessionCours) -> None:
    """Nombre d'inscrits (hors annulées) strictement inférieur à capacite_max."""
    nb_inscrits = db.exec(
        select(func.count()).select_from(Inscription).where(
            Inscription.session_id == session_cours.id,
            Inscription.statut != StatutInscription.annulee,
        )
    ).one()
    if nb_inscrits >= session_cours.capacite_max:
        raise ValueError(
            f"La session « {session_cours.titre} » est complète "
            f"({session_cours.capacite_max} places)"
        )


def _verifier_pas_de_chevauchement(
    db: Session, apprenant_id: int, session_cours: SessionCours
) -> None:
    """Aucune autre session (inscription non annulée) de l'apprenant ne chevauche celle-ci."""
    conflit = db.exec(
        select(SessionCours)
        .join(Inscription, Inscription.session_id == SessionCours.id)
        .where(
            Inscription.apprenant_id == apprenant_id,
            Inscription.statut != StatutInscription.annulee,
            SessionCours.id != session_cours.id,
            SessionCours.date_debut < session_cours.date_fin,
            SessionCours.date_fin > session_cours.date_debut,
        )
    ).first()
    if conflit:
        raise ValueError(
            f"L'apprenant {apprenant_id} est déjà inscrit à « {conflit.titre} » "
            f"({conflit.date_debut} → {conflit.date_fin}), qui chevauche cette session"
        )


# =====================================================================
# Création
# =====================================================================

def creer_inscription(db: Session, donnees: dict[str, Any]) -> Inscription:
    """
    1. Validation Pydantic (champs, ids positifs)
    2. L'apprenant et la session existent
    3. Pas de doublon (apprenant, session)
    4. La session est OPEN
    5. Il reste de la place
    6. Pas de chevauchement avec une autre session de l'apprenant
    """
    # 1. Validation Pydantic
    inscription = Inscription.model_validate(donnees)

    # 2. Existence
    if db.get(Apprenant, inscription.apprenant_id) is None:
        raise ValueError(f"L'apprenant {inscription.apprenant_id} n'existe pas")
    session_cours = db.get(SessionCours, inscription.session_id)
    if session_cours is None:
        raise ValueError(f"La session {inscription.session_id} n'existe pas")

    # 3. Doublon
    if verifier_inscription_existante(db, inscription.apprenant_id, inscription.session_id):
        raise ValueError(
            f"L'apprenant {inscription.apprenant_id} est déjà inscrit à "
            f"« {session_cours.titre} » (réactivez l'inscription existante si elle est annulée)"
        )

    # 4 à 6. Règles de la session
    _verifier_session_ouverte(session_cours)
    _verifier_places(db, session_cours)
    _verifier_pas_de_chevauchement(db, inscription.apprenant_id, session_cours)

    db.add(inscription)
    db.flush()                      # id disponible, pas de commit
    return inscription


# =====================================================================
# Lecture
# =====================================================================

def lire_inscription(db: Session, inscription_id: int) -> Inscription | None:
    return db.get(Inscription, inscription_id)


def lister_inscriptions(
    db: Session,
    apprenant_id: int | None = None,
    session_id: int | None = None,
) -> list[Inscription]:
    """Toutes les inscriptions, filtrables par apprenant et/ou par session."""
    requete = select(Inscription)
    if apprenant_id is not None:
        requete = requete.where(Inscription.apprenant_id == apprenant_id)
    if session_id is not None:
        requete = requete.where(Inscription.session_id == session_id)
    return list(db.exec(requete).all())


# =====================================================================
# Modification du statut
# =====================================================================

def modifier_statut_inscription(
    db: Session, inscription_id: int, nouveau_statut: StatutInscription
) -> Inscription:
    inscription = lire_inscription(db, inscription_id)
    if inscription is None:
        raise ValueError(f"L'inscription {inscription_id} est introuvable")

    ancien = inscription.statut

    # Une inscription terminée est définitive
    if ancien == StatutInscription.terminee and nouveau_statut != ancien:
        raise ValueError("Une inscription terminée ne peut plus changer de statut")

    # Réactiver une inscription annulée = reprendre une place : on rejoue les règles
    if ancien == StatutInscription.annulee and nouveau_statut != StatutInscription.annulee:
        session_cours = db.get(SessionCours, inscription.session_id)
        _verifier_session_ouverte(session_cours)
        _verifier_places(db, session_cours)
        _verifier_pas_de_chevauchement(db, inscription.apprenant_id, session_cours)

    inscription.statut = nouveau_statut
    db.add(inscription)
    db.flush()
    return inscription


def annuler_inscription(db: Session, inscription_id: int) -> Inscription:
    """Annule sans supprimer : l'historique est conservé et la place est libérée."""
    return modifier_statut_inscription(db, inscription_id, StatutInscription.annulee)