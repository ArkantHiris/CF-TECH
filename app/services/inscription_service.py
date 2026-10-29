# Importer les outils pour interroger la base de données
from sqlmodel import Session, select

# Importer le modèle et le statut des inscriptions 
from app.models.inscription import Inscription, StatutInscription

# Vérifier si unapprenant est déja inscrit à une séssion
def verifier_inscription_existante(
        db: Session,
        apprenant_id: int,
        session_id: int
) -> bool:
    

    # Rechercher une inscription pour cet apprenant et cette session
    requete = select(Inscription).where(
        Inscription.apprenant_id == apprenant_id,
        Inscription.session_id == session_id
    )
    # Exécuter la requête et récupérer la première inscription trouvée
    inscription = db.exec(requete).first()
    # Retourner True si l'inscription existe, sinon False
    return inscription is not None


# Créer une nouvelle inscription
def creer_inscription(
    db: Session,
    apprenant_id: int,
    session_id: int
) -> Inscription:
        # Vérifier si l'apprenant est déjà inscrit
    if verifier_inscription_existante(db, apprenant_id, session_id):
        raise ValueError("Cet apprenant est déjà inscrit à cette session.")


    # Créer un nouvel objet inscription
    nouvelle_inscription = Inscription(
        apprenant_id=apprenant_id,
        session_id=session_id
    )


    # Ajouter la nouvelle inscription à la session
    db.add(nouvelle_inscription)


    # Enregistrer les modifications dans la base de données
    db.commit()

    # Actualiser l'inscription avec les données de la base
    db.refresh(nouvelle_inscription)
    # Retourner la nouvelle inscription
    return nouvelle_inscription


# Rechercher une inscription par son identifiant
def lire_inscription(
    db: Session,
    inscription_id: int
) -> Inscription | None:

    
    # Rechercher une inscription par son identifiant
    inscription = db.get(Inscription, inscription_id)
    # Retourner une inscription trouvée
    return inscription
 # Liter les inscriptions
def lister_inscriptions(db: Session)-> list[Inscription]:
    # Sélectionner toutes les inscriptions
    requete = select(Inscription)
    # Executer la requête et récupérer toutes les inscriptions
    inscriptions = db.exec(requete).all()
    # Retourner la liste des inscriptions
    return inscriptions


# Modifier le statut d'une inscription 
def modifier_statut_inscription(
    db: Session,
    inscription_id: int, 
    nouveau_statut: StatutInscription
    ) -> Inscription:
    # Rechercher l'iscription à modifier
    inscription = lire_inscription(db, inscription_id)
    # Vérifier si l'inscription existe
    if inscription is None:
        raise ValueError( " Inscription introuvable")
    # Modifier le statut de l'inscription
    inscription.statut = nouveau_statut
    # Enregistrer le nouveau statut dans la base de données
    db.commit()
    # Actualiser l'inscription après la modification
    db.refresh(inscription)
    # Retourner l'inscription avec son nouveau statut
    return inscription


# Annuler une inscription sans la supprimer de la base
def annuler_inscription(
    db: Session,
    inscription_id: int
) -> bool:
    # Rechercher l'inscription à annuler
    inscription = lire_inscription(db, inscription_id)
    # Vérifier si l'inscription existe
    if inscription is None:
        return False
    # Modifier le statut de l'inscription pour l'annuler
    modifier_statut_inscription(
        db,
        inscription_id,
        StatutInscription.annulee
    )
    # Confirmer que l'inscription a été annulée
    return True



















