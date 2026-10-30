from typing import Any

from sqlmodel import Session, select, func

from app.models import Salle, SessionCours
from app.schemas.salle_schemas import SalleBase

# Champs qu'on ne peut jamais modifier
CHAMPS_NON_MODIFIABLES = {"id"}


def verifier_nom_libre(db: Session, nom: str, ignorer_id: int | None = None) -> None:
    """
    Vérifie si le nom d'une salle est libre (car unique)
    """

    conditions = [Salle.nom == nom]

    # On ajoute la condition de s'ignorer lui même
    if ignorer_id is not None:

        conditions.append(Salle.id != ignorer_id)

    # Si on trouve un résultat, alors le nom est déjà pris
    if db.exec(select(Salle).where(*conditions)).first():

        raise ValueError(f"Une salle nommée « {nom} » existe déjà")


def creer_salle(db: Session, donnees: dict[str, Any]) -> Salle:
    """
    Permet la création d'une ligne dans la table salle
    """

    # Vérifs de Pydantic
    salle = Salle.model_validate(donnees) 

    # On vérifie si le nom est libre         
    verifier_nom_libre(db, salle.nom)

    db.add(salle)
    # On peut car on a l'id
    db.flush()             

    return salle


def lire_salle(db: Session, salle_id: int) -> Salle | None:
    """
    Permet d'afficher une ligne de la table salle
    """
    return db.get(Salle, salle_id)


def lister_salles(db: Session, actives_seulement: bool = False) -> list[Salle]:
    """
    Permet d'afficher une liste de la table salle
    Si 3e paramètre en true, alors on affiche que les salles actives.
    """

    requete = select(Salle)

    if actives_seulement:

        requete = requete.where(Salle.is_active == True)  

    return list(db.exec(requete).all())


def modifier_salle(db: Session, salle_id: int, changements: dict[str, Any]) -> Salle:
    """
    Permet de modifier une ligne de la table salle
    """

    salle = db.get(Salle, salle_id)

    # Si la salle existe vraiment
    if salle is None:

        raise ValueError(f"La salle {salle_id} n'existe pas")

    # On vérifie si des champs non modifiables font parti des changements (l'intersection des deux grâce au &)
    interdits = CHAMPS_NON_MODIFIABLES & changements.keys()

    if interdits:

        raise ValueError(f"Champ(s) non modifiable(s) : {', '.join(sorted(interdits))}")

    # On prépare les données en retirant l'id
    donnees = salle.model_dump(exclude={"id"}) | changements

    # On passe ces données à la vérif pydantic
    SalleBase.model_validate(donnees)

    # Si la clé nom est présente, on vérifie la dispo
    if "nom" in changements:

        verifier_nom_libre(db, donnees["nom"], ignorer_id=salle_id)

    # RAF verifier que la capacite de session reste inferieur ou egale à la capacite d'une salle

    salle.sqlmodel_update(changements)

    db.add(salle)
    # Car on a l'id
    db.flush()
    
    return salle


def desactiver_salle(db: Session, salle_id: int) -> Salle:
    """
    On passe le statut en inactif, mais on ne supprime pour garder l'historique dans inscription
    """

    salle = db.get(Salle, salle_id)

    # Si la salle existe
    if salle is None:
        raise ValueError(f"La salle {salle_id} n'existe pas")
    
    salle.is_active = False

    db.add(salle)
    # Car on a l'id
    db.flush()

    return salle