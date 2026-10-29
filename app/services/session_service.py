# Importer les outils pour communiquer avec la base de données
from sqlmodel import Session, select

# Importer les dates
from datetime import datetime

# Importer le modèle et les statuts des sessions de cours
from app.models.session import SessionCours, StatutSession


# Rechercher une session de cours par son identifiant
def lire_session(
    db: Session,
    session_id: int
) -> SessionCours | None:
    # Rechercher la session dans la base de données
    session = db.get(SessionCours, session_id)

    # Retourner la session trouvée ou None
    return session


# Lister toutes les sessions de cours
def lister_sessions(db: Session) -> list[SessionCours]:
    # Préparer la requête pour sélectionner toutes les sessions
    requete = select(SessionCours)

    # Exécuter la requête et récupérer les sessions
    sessions = db.exec(requete).all()

    # Retourner la liste des sessions
    return sessions


# Créer une nouvelle session de cours
def creer_session(
    db: Session,
    titre: str,
    date_debut: datetime,
    date_fin: datetime,
    salle_id: int,
    formateur_id: int
) -> SessionCours:
    # Créer un objet session de cours
    nouvelle_session = SessionCours(
        titre=titre,
        date_debut=date_debut,
        date_fin=date_fin,
        salle_id=salle_id,
        formateur_id=formateur_id
    )
    # Ajouter la nouvelle session à la base de données
    db.add(nouvelle_session)

    # Enregistrer les modifications
    db.commit()

    # Actualiser les données de la session
    db.refresh(nouvelle_session)

    # Retourner la session créée
    return nouvelle_session


# Modifier le statut d'une session de cours
def modifier_statut_session(
    db: Session,
    session_id: int,
    nouveau_statut: StatutSession
) -> SessionCours | None:

    # Rechercher la session par son identifiant
    session = db.get(SessionCours, session_id)

    # Vérifier si la session existe
    if session is None:
        return None

    # Modifier le statut de la session
    session.statut = nouveau_statut

    # Enregistrer les modifications
    db.add(session)
    db.commit()

    # Actualiser les données de la session
    db.refresh(session)

    # Retourner la session modifiée
    return session


# Annuler une session de cours
def annuler_session(
    db: Session,
    session_id: int
) -> SessionCours | None:

    # Modifier le statut de la session en "Annulée"
    return modifier_statut_session(
        db,
        session_id,
        StatutSession.annulee
    )


