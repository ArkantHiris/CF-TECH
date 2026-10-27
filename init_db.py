from sqlmodel import SQLModel
from app.database import engine

# Import obligatoire pour que SQLModel enregistre toutes vos tables en mémoire
# Lit le __init__.py en premier , cela permet de centraliser les imports
import app.models

def init_db() -> None:
    """
    Fonction créant les différentes tables d'après les objets dans models
    """

    print("Création de la base de données et des tables...")

    # Cette ligne lit toutes les classes ayant `table=True` et génère les CREATE TABLE, si elles n'existent pas
    SQLModel.metadata.create_all(engine)

    print("Base de données initialisée avec succès ! Le fichier cf_tech.db a été créé.")


# Garde fou évitant de supprimer et recréer la db, si ce code n'est pas exécuté depuis le terminal
if __name__ == "__main__":
    init_db()