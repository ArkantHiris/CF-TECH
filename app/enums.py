import enum

# Définition des Énumérations ( des listes contenants les valeurs possibles et acceptées )
# Enum crée un objet enum grâce à la library enum, typage nécessaire pour SQLModel

class Role(str, enum.Enum):
    """Rôles possibles pour un utilisateur"""
    apprenant = "apprenant"
    formateur = "formateur"
    staff_pedagogique = "staff_pedagogique"
    admin = "admin"


class NiveauEtude(str, enum.Enum):
    """Niveaux d'études possibles"""
    brevet = "Brevet"
    cap = "CAP"
    bep = "BEP"
    bac = "Bac"
    bac_1 = "Bac +1"
    bac_2 = "Bac +2"
    bac_3 = "Bac +3"
    bac_4 = "Bac +4"
    bac_5 = "Bac +5"
    bac_plus = "Bac +5 +"


class Postes(str, enum.Enum):
    """Postes au sein du staff de CF-Tech"""
    responsable = "Responsable pédagogique"
    charge_projet = "Chargé(e) de Projet"


class NiveauAcces(str, enum.Enum):
    """Niveaux d'accès disponibles"""
    superadmin = "SUPERADMIN"
    admin_standard = "ADMIN_STANDART"

class StatutSession(str, enum.Enum):
    """Statuts possibles d'une session de cours"""
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    ARCHIVED = "ARCHIVED"

class StatutInscription(str, enum.Enum):
    """Statuts possibles de l'inscription d'un apprenant"""
    en_attente = "En attente"
    confirmee = "Confirmée"
    annulee = "Annulée"
    terminee = "Terminée"