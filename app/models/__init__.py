# Appel des configurations des bases de données pour l'init

from app.models.user import Apprenant, Formateur, StaffPedagogique, Admin, Role, NiveauEtude, Postes, NiveauAcces
from app.models.salle import Salle
from app.models.session import SessionCours, StatutSession
from app.models.inscription import Inscription, StatutInscription