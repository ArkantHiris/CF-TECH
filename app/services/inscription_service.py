from typing import Any

from sqlmodel import Session, select, func

from app.enums import StatutInscription, StatutSession
from app.models import Apprenant, SessionCours, Inscription


# Methodes réutilisables dans plusieurs fonctions

def verifier_inscription_existante(db: Session, apprenant_id: int, session_id: int) -> bool:
    """
    True si l'apprenant a déjà une inscription (même annulée) à cette session
    """

    requete = select(Inscription).where(

        Inscription.apprenant_id == apprenant_id,
        Inscription.session_id == session_id,

    )

    return db.exec(requete).first() is not None


def verifier_session_ouverte(session_cours: SessionCours) -> None:
    """
    True si la session est bien ouverte 
    """

    if session_cours.statut != StatutSession.OPEN:

        raise ValueError(

            f"La session « {session_cours.titre} » n'est pas ouverte "
            f"(statut : {session_cours.statut.value})"
        )


def verifier_places(db: Session, session_cours: SessionCours) -> None:
    """
    True si le nombre d'inscrits (hors annulés) strictement inférieur à capacite_max
    """

    nb_inscrits = db.exec(

        select(func.count()).select_from(Inscription).where(

            Inscription.session_id == session_cours.id,
            Inscription.statut != StatutInscription.annulee,
        )
    ).one()

    if nb_inscrits >= session_cours.capacite_max:

        raise ValueError(

            f"La session « {session_cours.titre} » est complète"
            f"({session_cours.capacite_max} places)"
        )


def verifier_pas_de_chevauchement(db: Session, apprenant_id: int, session_cours: SessionCours) -> None:
    """
    Provoque une erreur si il y a chevauchement de sessiosn
    """

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
        # Interrompt si une erreur est trouvée
        raise ValueError(
            f"L'apprenant {apprenant_id} est déjà inscrit à « {conflit.titre} » "
            f"({conflit.date_debut} → {conflit.date_fin}), qui chevauche cette session"
        )


# Méthodes de création 

def creer_inscription(db: Session, donnees: dict[str, Any]) -> Inscription:
    """
    Crée l'inscription d'un apprenant à une session si il passe toutes les vérifs
    """

    # 1. Validation Pydantic
    inscription = Inscription.model_validate(donnees)

    # 2. Existence de l'apprenant ou la session de cours
    if db.get(Apprenant, inscription.apprenant_id) is None:

        raise ValueError(f"L'apprenant {inscription.apprenant_id} n'existe pas")
    
    session_cours = db.get(SessionCours, inscription.session_id)

    if session_cours is None:

        raise ValueError(f"La session {inscription.session_id} n'existe pas")

    # 3. Doublon d'inscription de l'apprenant sur ce cours
    if verifier_inscription_existante(db, inscription.apprenant_id, inscription.session_id):

        raise ValueError(

            f"L'apprenant {inscription.apprenant_id} est déjà inscrit à « {session_cours.titre} »"

        )

    # 4. Session ouverte
    verifier_session_ouverte(session_cours)

    # 5. Places encore disponibles
    verifier_places(db, session_cours)

    # 6. Cours en simultanés
    verifier_pas_de_chevauchement(db, inscription.apprenant_id, session_cours)

    db.add(inscription)

    # id disponible, pas de commit
    db.flush()        

    return inscription


# Méthode de lecture

def lire_inscription(db: Session, inscription_id: int) -> Inscription | None:
    """
    Lecture des data d'une inscription par rapport à son id
    """

    return db.get(Inscription, inscription_id)


def lister_inscriptions(db: Session, apprenant_id: int | None = None, session_id: int | None = None,) -> list[Inscription]:
    """
    Toutes les inscriptions, filtrables par apprenant et/ou par session
    """

    requete = select(Inscription)

    if apprenant_id is not None:

        requete = requete.where(Inscription.apprenant_id == apprenant_id)

    if session_id is not None:

        requete = requete.where(Inscription.session_id == session_id)

    return list(db.exec(requete).all())



# Methodes update

def modifier_statut_inscription(db: Session, inscription_id: int, nouveau_statut: StatutInscription) -> Inscription:
    """
    Permet de modifier le statut d'une inscription
    """

    # vérifie l'existence de l'inscription
    inscription = lire_inscription(db, inscription_id)

    if inscription is None:

        raise ValueError(f"L'inscription {inscription_id} est introuvable")

    ancien = inscription.statut

    # vérifie si l'inscription est finie
    if ancien == StatutInscription.terminee and nouveau_statut != ancien:

        raise ValueError("Une inscription terminée ne peut plus changer de statut")

    # Réactiver une inscription annulée 
    if ancien == StatutInscription.annulee and nouveau_statut != StatutInscription.annulee:

        session_cours = db.get(SessionCours, inscription.session_id)

        # on révérifie les règles d'inscription
        verifier_session_ouverte(session_cours)
        verifier_places(db, session_cours)
        verifier_pas_de_chevauchement(db, inscription.apprenant_id, session_cours)


    inscription.statut = nouveau_statut

    db.add(inscription)
    # car on connait l'id
    db.flush()

    return inscription


def annuler_inscription(db: Session, inscription_id: int) -> Inscription:
    """
    Annule sans supprimer : l'historique est conservé et la place est libérée
    Utile si on se réinscrit
    """

    return modifier_statut_inscription(db, inscription_id, StatutInscription.annulee)