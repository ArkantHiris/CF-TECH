from datetime import date, datetime, timezone

from sqlmodel import Session

from app.database import engine
from app.enums import Role, NiveauEtude, Postes, NiveauAcces

# Adaptez les noms de modules à votre dossier (vous utilisez "controler" pour les deux premiers)
from app.services.salle_service import creer_salle
from app.services.user_service import (
    creer_formateur,
    creer_staff,
    creer_apprenant,
    creer_admin,
)
from app.services.session_service import creer_session_cours
from app.services.inscription_service import creer_inscription


def seed_database() -> None:

    with Session(engine) as session:

        try:
            # 1. Salles
            salles = [creer_salle(session, d) for d in [
                {"nom": "Amphi A", "capacite": 100,
                 "localisation": "Bâtiment Principal - RDC",
                 "equipements": {"video_projecteur": True, "tableau": "blanc"}},
                {"nom": "Labo Code 101", "capacite": 20,
                 "localisation": "Bâtiment B - 1er Étage",
                 "equipements": {"pc_fixes": 20}},
                {"nom": "Salle Réunion Nord", "capacite": 12,
                 "localisation": "Bâtiment A - 2ème Étage",
                 "equipements": {"visio": True}},
            ]]

            # 2. Formateurs
            formateurs = [creer_formateur(session, d) for d in [
                {"nom": "Durand", "prenom": "Marc", "email": "marc.durand@cf-tech.fr",
                 "role": Role.formateur, "specialite": "Python & SQLModel",
                 "date_embauche": date(2022, 9, 1), "taux_horaire": 45.0},
                {"nom": "Lefevre", "prenom": "Sophie", "email": "sophie.lefevre@cf-tech.fr",
                 "role": Role.formateur, "specialite": "DevOps & Web",
                 "date_embauche": date(2023, 1, 15), "taux_horaire": 50.0},
            ]]

            # 3. Staff pédagogique
            staffs = [creer_staff(session, d) for d in [
                {"nom": "Moreau", "prenom": "Thomas", "email": "thomas.moreau@cf-tech.fr",
                 "role": Role.staff_pedagogique, "poste": Postes.responsable,
                 "date_prise_fonction": date(2021, 6, 1)},
                {"nom": "Bernard", "prenom": "Julie", "email": "julie.bernard@cf-tech.fr",
                 "role": Role.staff_pedagogique, "poste": Postes.charge_projet,
                 "date_prise_fonction": date(2023, 9, 1)},
            ]]

            # 4. Apprenants
            apprenants = [creer_apprenant(session, d) for d in [
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
            ]]

            # 5. Admins
            # L'email de Thomas Moreau (admin) est différent de celui du staff :
            # l'unicité est vérifiée sur les 4 tables d'utilisateurs.
            admins = [creer_admin(session, d) for d in [
                {"nom": "Bernard", "prenom": "Claire", "email": "claire.bernard@cf-tech.fr",
                 "role": Role.admin, "niveau_acces": NiveauAcces.superadmin,
                 "date_promotion": date(2023, 6, 1)},
                {"nom": "Moreau", "prenom": "Thomas", "email": "thomas.moreau.admin@cf-tech.fr",
                 "role": Role.admin, "niveau_acces": NiveauAcces.admin_standard,
                 "date_promotion": date(2024, 1, 15)},
            ]]

            # 6. Sessions
            # creer_session_cours valide et vérifie les règles mais n'ajoute pas l'objet :
            # add + flush après chaque session pour que la suivante la voie.
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
                session.flush()
                sessions_formation.append(s)

            # 7. Inscriptions
            # creer_inscription fait déjà add + flush : pas besoin de les refaire.
            donnees_inscriptions = [
                {"apprenant_id": apprenants[0].id, "session_id": sessions_formation[0].id},
                {"apprenant_id": apprenants[0].id, "session_id": sessions_formation[1].id},
                {"apprenant_id": apprenants[1].id, "session_id": sessions_formation[1].id},
                {"apprenant_id": apprenants[2].id, "session_id": sessions_formation[2].id},
                {"apprenant_id": apprenants[3].id, "session_id": sessions_formation[3].id},
                {"apprenant_id": apprenants[1].id, "session_id": sessions_formation[3].id},
            ]
            for d in donnees_inscriptions:
                creer_inscription(session, d)

            # Un seul commit : tout est validé d'un coup, ou rien
            session.commit()
            print("Jeu de données complet inséré avec succès !")

        except Exception as e:
            session.rollback()
            print(f"Une erreur est survenue, annulation de toutes les insertions : {e}")
            raise


# Garde-fou : le seed ne s'exécute que lancé directement depuis le terminal
if __name__ == "__main__":
    seed_database()