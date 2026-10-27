"""
Pont technique entre le code Python et notre language SQL, ici SQLite
Géré automatiquement par l'ORM (SQLModel)
    - Engine : Passerelle permanente vers le fichier physique
    - Session : session temporaire de travail pour effectuer les transactions
"""

from sqlmodel import create_engine, Session

# url de la database, dans notre cas : SQLite
DATABASE_URL = "sqlite:///cf_tech.db"

# connect_args={"check_same_thread": False} est nécessaire pour SQLite avec FastAPI/Python
engine = create_engine(DATABASE_URL, echo=True, connect_args={"check_same_thread": False})