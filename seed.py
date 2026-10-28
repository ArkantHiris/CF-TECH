from datetime import date, datetime, timezone
from typing import Any, TypeVar

from sqlmodel import Session, SQLModel

from app.database import engine
import app.models
from app.enums import Role, NiveauEtude, Postes, NiveauAcces
from app.controler.session_controls import creer_session_cours
from app.controler.inscription_controls import creer_inscription

# Nécessaire au typage SQLModel
T = TypeVar("T", bound=SQLModel)


def valider(modele: type[T], liste_dicts: list[dict[str, Any]]) -> list[T]:
    """
    Valide chaque dictionnaire avec Pydantic et renvoie la liste d'objets.
    """
    return [modele.model_validate(item) for item in liste_dicts]


def enregistrer(session: Session, objets: list[SQLModel]) -> None:
    """
    Ajoute les objets et les envoie à la base (flush) pour obtenir leurs id,
    sans valider définitivement la transaction.
    """
    session.add_all(objets)
    session.flush()


def seed_database():

    with Session(engine) as session:

        try:
            # 1. Création de 3 salles
            salles = valider(app.models.Salle, [
                {"nom": "Amphi A", "capacite": 100,
                 "localisation": "Bâtiment Principal - RDC",
                 "equipements": {"video_projecteur": True, "tableau": "blanc"}},
                {"nom": "Labo Code 101", "capacite": 20,
                 "localisation": "Bâtiment B - 1er Étage",
                 "equipements": {"pc_fixes": 20}},
                {"nom": "Salle Réunion Nord", "capacite": 12,
                 "localisation": "Bâtiment A - 2ème Étage",
                 "equipements": {"visio": True}},
            ])
            enregistrer(session, salles)

            # 2. Création de 2 formateurs
            formateurs = valider(app.models.Formateur, [
                {"nom": "Durand", "prenom": "Marc", "email": "marc.durand@cf-tech.fr",
                 "role": Role.formateur, "specialite": "Python & SQLModel",
                 "date_embauche": date(2022, 9, 1), "taux_horaire": 45.0},
                {"nom": "Lefevre", "prenom": "Sophie", "email": "sophie.lefevre@cf-tech.fr",
                 "role": Role.formateur, "specialite": "DevOps & Web",
                 "date_embauche": date(2023, 1, 15), "taux_horaire": 50.0},
            ])
            enregistrer(session, formateurs)

            # 3. Création de 2 staffs pédagogiques
            staffs = valider(app.models.StaffPedagogique, [
                {"nom": "Moreau", "prenom": "Thomas", "email": "thomas.moreau@cf-tech.fr",
                 "role": Role.staff_pedagogique, "poste": Postes.responsable,
                 "date_prise_fonction": date(2021, 6, 1)},
                {"nom": "Bernard", "prenom": "Julie", "email": "julie.bernard@cf-tech.fr",
                 "role": Role.staff_pedagogique, "poste": Postes.charge_projet,
                 "date_prise_fonction": date(2023, 9, 1)},
            ])
            enregistrer(session, staffs)

            # 4. Création de 4 apprenants
            apprenants = valider(app.models.Apprenant, [
                {"nom": "Dupont", "prenom": "Alice", "email": "alice.dupont@cf-tech.fr",
                 "role": Role.apprenant, "date_naissance": date(2001, 3, 12),
                 "niveau_etude": NiveauEtude.bac_3},
                {"nom": "Martin", "prenom": "Lucas", "email": "lucas.martin@cf-tech.fr",
                 "role": Role.apprenant, "date_naissance": date(1999, 8, 22),
                 "niveau_etude": NiveauEtude.bac_2},
                {"nom": "Benali", "prenom": "Chloé", "email": "chloe.benali@cf-tech.fr",
                 "role": Role.apprenant, "date_naissance": date(2003, 11, 5),
                 "niveau_etude": NiveauEtude.bac},
                {"nom": "Petit", "prenom": "Hugo", "email": "hugo.petit@cf-tech.fr",
                 "role": Role.apprenant, "date_naissance": date(2000, 1, 15),
                 "niveau_etude": NiveauEtude.bac_5},
            ])
            enregistrer(session, apprenants)

            # 5. Création de 2 admins
            admins = valider(app.models.Admin, [
                {"nom": "Bernard", "prenom": "Claire", "email": "claire.bernard@cf-tech.fr",
                 "role": Role.admin, "niveau_acces": NiveauAcces.superadmin,
                 "date_promotion": date(2023, 6, 1)},
                {"nom": "Moreau", "prenom": "Thomas", "email": "thomas.moreau@cf-tech.fr",
                 "role": Role.admin, "niveau_acces": NiveauAcces.admin_standard,
                 "date_promotion": date(2024, 1, 15)},
            ])
            enregistrer(session, admins)

            # 6. Création de 4 sessions via le service (capacité, disponibilité formateur/salle)
            donnees_sessions = [
                {"titre": "Initiation Python", "capacite_max": 30,
                 "description": "Bases du langage Python",
                 "prerequis": ["Aucun"],
                 "date_debut": datetime(2026, 3, 1, 13, tzinfo=timezone.utc),
                 "date_fin": datetime(2026, 3, 5, 15, tzinfo=timezone.utc),
                 "salle_id": salles[0].id, "formateur_id": formateurs[0].id},
                {"titre": "Bases de données SQLModel", "capacite_max": 15,
                 "prerequis": ["Python"],
                 "date_debut": datetime(2026, 3, 10, 15, tzinfo=timezone.utc),
                 "date_fin": datetime(2026, 3, 12, 18, tzinfo=timezone.utc),
                 "salle_id": salles[1].id, "formateur_id": formateurs[0].id},
                {"titre": "Architecture Flask", "capacite_max": 25,
                 "prerequis": ["Python"],
                 "date_debut": datetime(2026, 3, 15, 8, tzinfo=timezone.utc),
                 "date_fin": datetime(2026, 3, 20, 11, tzinfo=timezone.utc),
                 "salle_id": salles[0].id, "formateur_id": formateurs[1].id},
                {"titre": "Introduction à Docker", "capacite_max": 10,
                 "prerequis": ["Linux"],
                 "date_debut": datetime(2026, 3, 22, 13, tzinfo=timezone.utc),
                 "date_fin": datetime(2026, 3, 25, 17, tzinfo=timezone.utc),
                 "salle_id": salles[2].id, "formateur_id": formateurs[1].id},
            ]
            sessions_formation = []
            for d in donnees_sessions:
                s = creer_session_cours(session, d)
                session.add(s)
                session.flush()   # pour que la vérification suivante voie cette session
                sessions_formation.append(s)

            # 7. Inscriptions (chaque apprenant est inscrit à au moins une session)
            donnees_inscriptions = [
                {"apprenant_id": apprenants[0].id, "session_id": sessions_formation[0].id},
                {"apprenant_id": apprenants[0].id, "session_id": sessions_formation[1].id},
                {"apprenant_id": apprenants[1].id, "session_id": sessions_formation[1].id},
                {"apprenant_id": apprenants[2].id, "session_id": sessions_formation[2].id},
                {"apprenant_id": apprenants[3].id, "session_id": sessions_formation[3].id},
                {"apprenant_id": apprenants[1].id, "session_id": sessions_formation[3].id},
            ]
            for d in donnees_inscriptions:
                insc = creer_inscription(session, d)
                session.add(insc)
                session.flush()   # pour que le comptage voie les inscriptions précédentes

            # Un seul commit : tout est validé d'un coup, ou rien
            session.commit()

            print("Jeu de données complet inséré avec succès !")

        except Exception as e:

            session.rollback()
            print(f"Une erreur est survenue, annulation de toutes les insertions : {e}")
            raise e


# Garde fou évitant de supprimer et recréer la db, si ce code n'est pas exécuté depuis le terminal
if __name__ == "__main__":
    seed_database()