# CF-TECH
Projet mettant en avant les bases de données et ORM
# CF-TECH — Training Center Management System
# CF-TECH — Système de gestion d’un centre de formation

[English](#english) | [Français](#français)

---

<a id="english"></a>
## English

### Overview

CF-TECH is an educational software project designed to manage the activities of a training center. It focuses on relational database design, Object-Relational Mapping (ORM), data validation, business rules, and database migrations.

**Project status:** In development. Features described below are part of the project scope and may not all be implemented yet.

### Objectives

- Design and manage a relational database.
- Use SQLModel and SQLAlchemy for ORM-based data management.
- Validate data with Pydantic.
- Manage database schema changes with Alembic.
- Define relationships and enforce data integrity.
- Implement role-based access control.
- Write automated tests with pytest.
- Collaborate through Git branches and pull requests.

### Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| SQLModel | Database models and ORM |
| SQLAlchemy | Relational database interaction |
| Pydantic | Data validation |
| Alembic | Database schema migrations |
| SQLite | Default database engine |
| pytest | Automated testing |
| email-validator | Email address validation |

### Main Entities

| Entity | Description |
|---|---|
| `UserBase` | Shared attributes and validation for user accounts |
| `Apprenant` | Learner information |
| `Formateur` | Trainer information |
| `StaffPedagogique` | Educational staff information |
| `Admin` | Administrative account and privileges |
| `Salle` | Training room, capacity, and equipment |
| `Session` | Training session details, schedule, and status |
| `Inscription` | Enrollment linking learners to sessions |

### Planned Features and Business Rules

- **User accounts:** validate email addresses, enforce unique accounts, require users to be at least 16 years old, and associate accounts with roles.
- **Rooms:** manage capacity and equipment, and prevent conflicting room bookings.
- **Training sessions:** validate date ranges, manage `OPEN`, `CLOSED`, and `ARCHIVED` statuses, and support prerequisites.
- **Enrollments:** manage `ENREGISTRE`, `DESINSCRIT`, and `EN_ATTENTE` statuses, track attendance, and apply enrollment and capacity rules.
- **Permissions:** centralize access checks through a `check_permission` utility.
- **Availability:** use an `is_salle_disponible` utility to check room availability.

These rules describe the intended scope and should be verified against the current implementation.

### Project Structure

```text
CF-TECH/
├── alembic/                                 # db versioning
├── app/
|     ├──models/                             # models for the different tables
|     |     ├──__init__.py
|     |     ├──inscription.py
|     |     ├──salle.py
|     |     ├──session.py
|     |     └──user.py
|     ├──schemas/                            # schemas for the different tables
|     |     ├──__init__.py
|     |     ├──inscription_schemas.py
|     |     ├──salle_schemas.py
|     |     ├──session_schemas.py
|     |     └──user_schemas.py               
|     ├──service/                            # services for the different tables
|     |     ├──inscription_service.py        
|     |     ├──salle_service.py              
|     |     ├──session_service.py            
|     |     └──user_service.py               
|     ├──database.py                         # config sqlmodel
|     ├──enums.py                            # list of enums of the project
├── app_test.py                              # Application entry point
├── init_db.py                               # script create db
├── interface.py                             # interface config
├── seed.py                                  # script seed db
├── requirements.txt                         # Python dependencies
└── README.md                                # Project documentation
```

The structure may evolve as models, database configuration, business logic, migrations, and tests are added.

### Prerequisites

- Python 3.11 or another version compatible with the project's dependencies
- Git
- A terminal (PowerShell on Windows, for example)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/ArkantHiris/CF-TECH.git
   cd CF-TECH
   ```

2. Create a virtual environment:

   ```powershell
   python -m venv venv
   ```

3. Activate it in PowerShell:

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. Install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Create database v4 :

   ```bash
   python init_db.py
   ```

6. Seed the database (only v4) :

      ```bash
   python seed.py
   ```

### Usage

Launch the application from the project root:

```bash
python app.py
```

The current entry point provides a command-line menu for the main management areas. Database-backed management operations are still under development.

### Database Migrations

Alembic is intended to manage database schema versioning. Once Alembic is configured and the SQLModel metadata is registered, typical commands include:

```bash
alembic init migrations
alembic revision --autogenerate -m "Initial database schema"
alembic upgrade head
```

Run `alembic init migrations` only once. Review autogenerated migrations before applying them.

### Testing

Run the test suite from the project root:

```bash
pytest
```

Tests should cover model validation, permissions, database relationships, room availability, scheduling conflicts, session capacity, enrollment rules, and migrations as these features are implemented.

### Development Workflow

1. Create a dedicated branch for each task.
2. Implement the change in the relevant modules.
3. Run the tests.
4. Commit with a clear message.
5. Open a pull request for review.
6. Merge after validation.

### Contributors

Developed as part of a collaborative training project focused on database design, ORM, data validation, and software development practices.

Repository: [ArkantHiris/CF-TECH](https://github.com/ArkantHiris/CF-TECH)

---

<a id="français"></a>
## Français

### Présentation

CF-TECH est un projet logiciel pédagogique destiné à gérer les activités d’un centre de formation. Il porte sur la conception de bases de données relationnelles, le mapping objet-relationnel (ORM), la validation des données, les règles métier et les migrations de base de données.

**État du projet :** en cours de développement. Les fonctionnalités décrites ci-dessous font partie du périmètre prévu et ne sont pas nécessairement toutes implémentées.

### Objectifs

- Concevoir et gérer une base de données relationnelle.
- Utiliser SQLModel et SQLAlchemy pour la gestion des données avec un ORM.
- Valider les données avec Pydantic.
- Gérer les évolutions du schéma de base de données avec Alembic.
- Définir les relations et garantir l’intégrité des données.
- Mettre en place un contrôle d’accès selon les rôles.
- Écrire des tests automatisés avec pytest.
- Collaborer avec des branches Git et des pull requests.

### Technologies

| Technologie | Utilisation |
|---|---|
| Python | Logique applicative |
| SQLModel | Modèles de données et ORM |
| SQLAlchemy | Interaction avec la base relationnelle |
| Pydantic | Validation des données |
| Alembic | Migrations du schéma de base de données |
| SQLite | Moteur de base de données par défaut |
| pytest | Tests automatisés |
| email-validator | Validation des adresses e-mail |

### Entités principales

| Entité | Description |
|---|---|
| `UserBase` | Attributs communs et validation des comptes utilisateur |
| `Apprenant` | Informations sur les apprenants |
| `Formateur` | Informations sur les formateurs |
| `StaffPedagogique` | Informations sur le personnel pédagogique |
| `Admin` | Compte et privilèges administratifs |
| `Salle` | Salle de formation, capacité et équipements |
| `Session` | Informations, planning et statut d’une session de formation |
| `Inscription` | Inscription reliant un apprenant à une session |

### Fonctionnalités prévues et règles métier

- **Comptes utilisateur :** valider les adresses e-mail, garantir l’unicité des comptes, imposer un âge minimum de 16 ans et associer chaque compte à un rôle.
- **Salles :** gérer la capacité et les équipements, et empêcher les réservations de salles qui se chevauchent.
- **Sessions de formation :** valider les dates, gérer les statuts `OPEN`, `CLOSED` et `ARCHIVED`, et prendre en charge les prérequis.
- **Inscriptions :** gérer les statuts `ENREGISTRE`, `DESINSCRIT` et `EN_ATTENTE`, suivre les présences et appliquer les règles d’inscription et de capacité.
- **Permissions :** centraliser les vérifications d’accès dans un utilitaire `check_permission`.
- **Disponibilité :** utiliser un utilitaire `is_salle_disponible` pour vérifier la disponibilité d’une salle.

Ces règles décrivent le périmètre attendu et doivent être vérifiées par rapport à l’implémentation actuelle.

### Structure du projet

```text
CF-TECH/
├── alembic/                                 # db versioning
├── app/
|     ├──models/                             # models for the different tables
|     |     ├──__init__.py
|     |     ├──inscription.py
|     |     ├──salle.py
|     |     ├──session.py
|     |     └──user.py
|     ├──schemas/                            # schemas for the different tables
|     |     ├──__init__.py
|     |     ├──inscription_schemas.py
|     |     ├──salle_schemas.py
|     |     ├──session_schemas.py
|     |     └──user_schemas.py               
|     ├──service/                            # services for the different tables
|     |     ├──inscription_service.py        
|     |     ├──salle_service.py              
|     |     ├──session_service.py            
|     |     └──user_service.py               
|     ├──database.py                         # config sqlmodel
|     ├──enums.py                            # list of enums of the project
├── app_test.py                              # Application entry point
├── init_db.py                               # script create db
├── interface.py                             # interface config
├── seed.py                                  # script seed db
├── requirements.txt                         # Python dependencies
└── README.md                                # Project documentation
```

Cette structure pourra évoluer avec l’ajout des modèles, de la configuration de la base de données, de la logique métier, des migrations et des tests.

### Prérequis

- Python 3.11 ou une version compatible avec les dépendances du projet
- Git
- Un terminal (PowerShell sous Windows, par exemple)

### Installation

1. Cloner le dépôt :

   ```bash
   git clone https://github.com/ArkantHiris/CF-TECH.git
   cd CF-TECH
   ```

2. Créer un environnement virtuel :

   ```powershell
   python -m venv venv
   ```

3. L’activer dans PowerShell :

   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

4. Installer les dépendances :

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. Créer la base de données v4 :

   ```bash
   python init_db.py
   ```

6. Remplis la base de données (seulement v4) :

      ```bash
   python seed.py
   ```

### Utilisation

Depuis la racine du projet, lancer :

```bash
python app.py
```

Le point d’entrée actuel propose un menu en ligne de commande pour les principaux domaines de gestion. Les opérations de gestion connectées à la base de données sont encore en cours de développement.

### Migrations de base de données

Alembic est prévu pour gérer le versionnement du schéma de la base de données. Une fois Alembic configuré et les métadonnées SQLModel enregistrées, les commandes habituelles comprennent :

```bash
alembic init migrations
alembic revision --autogenerate -m "Initial database schema"
alembic upgrade head
```

La commande `alembic init migrations` ne doit être exécutée qu’une seule fois. Il faut vérifier les migrations générées automatiquement avant de les appliquer.

### Tests

Depuis la racine du projet, exécuter :

```bash
pytest
```

Au fur et à mesure de l’implémentation, les tests devront couvrir la validation des modèles, les permissions, les relations entre tables, la disponibilité des salles, les conflits de planning, la capacité des sessions, les règles d’inscription et les migrations.

### Méthode de développement

1. Créer une branche dédiée à chaque tâche.
2. Implémenter la modification dans les modules concernés.
3. Exécuter les tests.
4. Créer un commit avec un message explicite.
5. Ouvrir une pull request pour revue.
6. Fusionner après validation.

### Contributeurs

Projet réalisé dans le cadre d’un travail collaboratif de formation portant sur la conception de bases de données, les ORM, la validation des données et les bonnes pratiques de développement logiciel.

Dépôt : [ArkantHiris/CF-TECH](https://github.com/ArkantHiris/CF-TECH)

---

*CF-TECH — Apprendre l’ingénierie des bases de données par le développement d’une application pratique.*
