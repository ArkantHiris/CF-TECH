
"""
CF-Tech - Training Management Interface
CF-Tech - Interface de gestion du centre de formation

Standalone graphical interface connected to the SQLite database cf_tech.db.
Interface graphique autonome connectée à la base de données SQLite cf_tech.db.

Database access is strictly read-only: this application displays data but
does not create, update or delete database records.
L'accès à la base est strictement en lecture seule : cette application
affiche les données, mais ne crée, ne modifie et ne supprime aucun enregistrement.
"""

from pathlib import Path
import sqlite3

import customtkinter as ctk


# =========================================================
# Configuration / Configuration générale
# =========================================================

# Resolve the directory containing this Python file.
# Détermine le dossier contenant ce fichier Python.
BASE_DIR = Path(__file__).resolve().parent

# Expected location of the SQLite database.
# Emplacement attendu de la base de données SQLite.
DATABASE_PATH = BASE_DIR / "cf_tech.db"

# Configure the application appearance.
# Configure l'apparence générale de l'application.
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Color palette: dark navy background with light blue accents.
# Palette de couleurs : fond bleu nuit avec des accents bleu clair.
BACKGROUND = "#0B1120"
SIDEBAR = "#111A2E"
PANEL = "#151F35"
PANEL_HOVER = "#1C2943"
ACCENT = "#3B82F6"
ACCENT_HOVER = "#2563EB"
TEXT = "#F3F6FC"
MUTED = "#9BAAC4"
BORDER = "#273550"
SUCCESS = "#34D399"
WARNING = "#FBBF24"
DANGER = "#F87171"


# =========================================================
# Database access / Accès à la base de données
# =========================================================

class Database:
    """
    Read-only access to the CF-Tech SQLite database.
    Accès en lecture seule à la base de données SQLite de CF-Tech.
    """

    def __init__(self, database_path: Path):
        """
        Store the database file path.
        Enregistre le chemin du fichier de base de données.
        """
        self.database_path = database_path

    def connect(self):
        """
        Open an existing SQLite database in read-only mode.
        Ouvre une base SQLite existante en lecture seule.

        Raises FileNotFoundError if the file does not exist.
        Déclenche FileNotFoundError si le fichier n'existe pas.
        """
        if not self.database_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.database_path}"
            )

        # The URI mode=ro prevents accidental database modifications.
        # Le paramètre URI mode=ro empêche les modifications accidentelles.
        connection_uri = self.database_path.as_uri() + "?mode=ro"

        connection = sqlite3.connect(
            connection_uri,
            uri=True,
            timeout=5,
        )

        # Rows can be accessed by column name as well as by index.
        # Les lignes sont accessibles par nom de colonne ou par index.
        connection.row_factory = sqlite3.Row
        return connection

    def get_tables(self):
        """
        Return all user-defined tables in the database.
        Retourne toutes les tables utilisateur présentes dans la base.
        """
        with self.connect() as connection:
            rows = connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table'
                  AND name NOT LIKE 'sqlite_%'
                ORDER BY name
                """
            ).fetchall()

        return [row["name"] for row in rows]

    def get_table_columns(self, table_name):
        """
        Return the columns of an existing table.
        Retourne les colonnes d'une table existante.

        The table name is checked against actual database tables first.
        Le nom est d'abord vérifié parmi les tables réellement présentes.
        """
        if table_name not in self.get_tables():
            return []

        with self.connect() as connection:
            rows = connection.execute(
                f'PRAGMA table_info("{table_name}")'
            ).fetchall()

        return [row["name"] for row in rows]

    def find_table(self, candidates):
        """
        Find the first table matching a list of possible names.
        Recherche la première table correspondant à une liste de noms possibles.

        This supports common French and English naming conventions.
        Cela permet de reconnaître des noms courants en français et en anglais.
        """
        tables = self.get_tables()
        table_lookup = {name.lower(): name for name in tables}

        for candidate in candidates:
            if candidate.lower() in table_lookup:
                return table_lookup[candidate.lower()]

        return None

    def read_table(self, candidates, limit=200):
        """
        Read records from a matching table.
        Lit les enregistrements d'une table correspondante.

        Returns the table name, its columns and formatted rows.
        Retourne le nom de la table, ses colonnes et les lignes formatées.
        """
        table_name = self.find_table(candidates)

        # No matching table: return an empty result instead of crashing.
        # Aucune table correspondante : retourne un résultat vide.
        if table_name is None:
            return None, [], []

        columns = self.get_table_columns(table_name)

        if not columns:
            return table_name, [], []

        # The table name comes from sqlite_master and has been validated.
        # Le nom provient de sqlite_master et a été vérifié.
        with self.connect() as connection:
            rows = connection.execute(
                f'SELECT * FROM "{table_name}" LIMIT ?',
                (limit,),
            ).fetchall()

        formatted_rows = [
            [self.format_value(row[column]) for column in columns]
            for row in rows
        ]

        return table_name, columns, formatted_rows

    @staticmethod
    def format_value(value):
        """
        Convert database values into display-friendly text.
        Convertit les valeurs de la base en texte facile à afficher.
        """
        if value is None:
            return "—"

        text_value = str(value)

        # Prevent very long values from making the interface difficult to read.
        # Évite que les valeurs trop longues rendent l'interface illisible.
        if len(text_value) > 100:
            return text_value[:97] + "..."

        return text_value

    def count_rows(self, candidates):
        """
        Count records in a matching table.
        Compte les enregistrements d'une table correspondante.

        Returns None if no matching table exists.
        Retourne None si aucune table correspondante n'existe.
        """
        table_name = self.find_table(candidates)

        if table_name is None:
            return None

        with self.connect() as connection:
            result = connection.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            ).fetchone()

        return result[0]


# =========================================================
# Main application / Application principale
# =========================================================

class CFTechApp(ctk.CTk):
    """
    Main window for the CF-Tech graphical interface.
    Fenêtre principale de l'interface graphique CF-Tech.
    """

    # Possible database table names for each page.
    # Noms de tables possibles pour chaque page de l'interface.
    PAGE_TABLES = {
        "Learners": ["apprenant", "apprenants", "learner", "learners"],
        "Trainers": ["formateur", "formateurs", "trainer", "trainers"],
        "Rooms": ["salle", "salles", "room", "rooms"],
        "Training Sessions": [
            "session",
            "sessions",
            "training_session",
            "training_sessions",
        ],
        "Enrollments": [
            "inscription",
            "inscriptions",
            "enrollment",
            "enrollments",
        ],
    }

    def __init__(self):
        """
        Initialize the application window and its components.
        Initialise la fenêtre et ses composants.
        """
        super().__init__()

        self.database = Database(DATABASE_PATH)
        self.current_page = "Dashboard"
        self.nav_buttons = {}

        # Window title, size and minimum dimensions.
        # Titre, dimensions et taille minimale de la fenêtre.
        self.title("CF-Tech | Training Management")
        self.geometry("1280x800")
        self.minsize(1000, 650)
        self.configure(fg_color=BACKGROUND)

        # Configure the main grid so the content area expands with the window.
        # Configure la grille pour que le contenu s'agrandisse avec la fenêtre.
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_sidebar()
        self.build_main_area()
        self.show_page("Dashboard")

    # -----------------------------------------------------
    # Sidebar / Barre latérale
    # -----------------------------------------------------

    def build_sidebar(self):
        """
        Create the left navigation panel.
        Crée le panneau de navigation situé à gauche.
        """
        self.sidebar = ctk.CTkFrame(
            self,
            width=245,
            corner_radius=0,
            fg_color=SIDEBAR,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

        # Brand area: logo and application name.
        # Zone de marque : logo et nom de l'application.
        brand = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
        )
        brand.pack(fill="x", padx=22, pady=(28, 35))

        logo = ctk.CTkFrame(
            brand,
            width=46,
            height=46,
            corner_radius=13,
            fg_color=ACCENT,
        )
        logo.pack(side="left", padx=(0, 12))
        logo.pack_propagate(False)

        ctk.CTkLabel(
            logo,
            text="CF",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="white",
        ).pack(expand=True)

        brand_text = ctk.CTkFrame(
            brand,
            fg_color="transparent",
        )
        brand_text.pack(side="left")

        ctk.CTkLabel(
            brand_text,
            text="CF-Tech",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            brand_text,
            text="TRAINING MANAGEMENT",
            font=ctk.CTkFont(size=9, weight="bold"),
            text_color=MUTED,
        ).pack(anchor="w", pady=(3, 0))

        # Navigation section heading.
        # Titre de la section de navigation.
        ctk.CTkLabel(
            self.sidebar,
            text="MAIN MENU",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#71819D",
        ).pack(anchor="w", padx=24, pady=(0, 12))

        pages = [
            ("Dashboard", "⌂"),
            ("Learners", "♙"),
            ("Trainers", "♧"),
            ("Rooms", "▦"),
            ("Training Sessions", "▣"),
            ("Enrollments", "☷"),
        ]

        # Create one navigation button per page.
        # Crée un bouton de navigation pour chaque page.
        for page, symbol in pages:
            button = ctk.CTkButton(
                self.sidebar,
                text=f"  {symbol}     {page}",
                height=44,
                corner_radius=10,
                anchor="w",
                fg_color="transparent",
                hover_color=PANEL_HOVER,
                text_color=MUTED,
                font=ctk.CTkFont(size=13),
                command=lambda name=page: self.show_page(name),
            )
            button.pack(fill="x", padx=14, pady=3)
            self.nav_buttons[page] = button

        # Sidebar footer.
        # Pied de page de la barre latérale.
        footer = ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
        )
        footer.pack(side="bottom", fill="x", padx=20, pady=22)

        ctk.CTkFrame(
            footer,
            height=1,
            fg_color=BORDER,
        ).pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(
            footer,
            text="CF-Tech Project",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            footer,
            text="SQLite database interface",
            font=ctk.CTkFont(size=10),
            text_color=MUTED,
        ).pack(anchor="w", pady=(4, 0))

    # -----------------------------------------------------
    # Main area / Zone principale
    # -----------------------------------------------------

    def build_main_area(self):
        """
        Create the header and the page display container.
        Crée l'en-tête et la zone d'affichage des pages.
        """
        self.main_area = ctk.CTkFrame(
            self,
            fg_color=BACKGROUND,
            corner_radius=0,
        )
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

        # Header containing the current page and database status.
        # En-tête affichant la page actuelle et l'état de la base.
        header = ctk.CTkFrame(
            self.main_area,
            fg_color="transparent",
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=35,
            pady=(25, 20),
        )
        header.grid_columnconfigure(0, weight=1)

        self.breadcrumb = ctk.CTkLabel(
            header,
            text="WORKSPACE / DASHBOARD",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=MUTED,
        )
        self.breadcrumb.grid(row=0, column=0, sticky="w")

        self.database_status = ctk.CTkLabel(
            header,
            text="Checking database...",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=WARNING,
            fg_color="#332A19",
            corner_radius=8,
            padx=12,
            pady=8,
        )
        self.database_status.grid(row=0, column=1, sticky="e")

        # This container is replaced whenever the user changes page.
        # Ce conteneur est remplacé à chaque changement de page.
        self.page_container = ctk.CTkFrame(
            self.main_area,
            fg_color="transparent",
        )
        self.page_container.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=35,
            pady=(0, 30),
        )
        self.page_container.grid_columnconfigure(0, weight=1)
        self.page_container.grid_rowconfigure(0, weight=1)

        self.refresh_database_status()

    def refresh_database_status(self):
        """
        Display whether the database can be accessed.
        Affiche si la base de données est accessible.
        """
        try:
            tables = self.database.get_tables()

            if tables:
                self.database_status.configure(
                    text="●  DATABASE CONNECTED",
                    text_color=SUCCESS,
                    fg_color="#12332F",
                )
            else:
                self.database_status.configure(
                    text="●  NO TABLES FOUND",
                    text_color=WARNING,
                    fg_color="#332A19",
                )

        except (FileNotFoundError, sqlite3.Error):
            self.database_status.configure(
                text="●  DATABASE UNAVAILABLE",
                text_color=DANGER,
                fg_color="#3A2029",
            )

    # -----------------------------------------------------
    # Navigation / Navigation entre les pages
    # -----------------------------------------------------

    def show_page(self, page):
        """
        Update the selected navigation item and display the requested page.
        Met à jour la navigation et affiche la page demandée.
        """
        self.current_page = page

        # Highlight the selected page in the sidebar.
        # Met en évidence la page sélectionnée dans la barre latérale.
        for name, button in self.nav_buttons.items():
            if name == page:
                button.configure(
                    fg_color=ACCENT,
                    hover_color=ACCENT_HOVER,
                    text_color="white",
                    font=ctk.CTkFont(size=13, weight="bold"),
                )
            else:
                button.configure(
                    fg_color="transparent",
                    hover_color=PANEL_HOVER,
                    text_color=MUTED,
                    font=ctk.CTkFont(size=13),
                )

        self.breadcrumb.configure(
            text=f"WORKSPACE / {page.upper()}"
        )

        # Remove the previous page's widgets before drawing the next page.
        # Supprime les widgets de l'ancienne page avant d'afficher la suivante.
        for widget in self.page_container.winfo_children():
            widget.destroy()

        if page == "Dashboard":
            self.show_dashboard()
        else:
            self.show_data_page(page)

    # -----------------------------------------------------
    # Dashboard / Tableau de bord
    # -----------------------------------------------------

    def show_dashboard(self):
        """
        Display database statistics and a session preview.
        Affiche les statistiques de la base et un aperçu des sessions.
        """
        page = ctk.CTkScrollableFrame(
            self.page_container,
            fg_color="transparent",
            corner_radius=0,
        )
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        page.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            page,
            text="Dashboard",
            font=ctk.CTkFont(size=30, weight="bold"),
            text_color=TEXT,
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 5),
        )

        ctk.CTkLabel(
            page,
            text="Overview of your training center.",
            font=ctk.CTkFont(size=13),
            text_color=MUTED,
        ).grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(0, 25),
        )

        # Each card counts records in a matching database table.
        # Chaque carte compte les enregistrements d'une table correspondante.
        cards = [
            (
                "LEARNERS",
                ["apprenant", "apprenants", "learner", "learners"],
                "#60A5FA",
            ),
            (
                "TRAINERS",
                ["formateur", "formateurs", "trainer", "trainers"],
                "#A78BFA",
            ),
            (
                "ROOMS",
                ["salle", "salles", "room", "rooms"],
                SUCCESS,
            ),
            (
                "ENROLLMENTS",
                ["inscription", "inscriptions", "enrollment", "enrollments"],
                WARNING,
            ),
        ]

        for index, (title, candidates, color) in enumerate(cards):
            count = self.safe_count(candidates)
            row = 2 + index // 2
            column = index % 2

            card = ctk.CTkFrame(
                page,
                fg_color=PANEL,
                corner_radius=14,
                border_width=1,
                border_color=BORDER,
            )
            card.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=(0, 10) if column == 0 else (10, 0),
                pady=(0, 16),
            )

            ctk.CTkLabel(
                card,
                text=title,
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=MUTED,
            ).pack(anchor="w", padx=20, pady=(18, 8))

            # A dash indicates that the expected table was not found.
            # Un tiret indique que la table attendue n'a pas été trouvée.
            value = "—" if count is None else str(count)

            ctk.CTkLabel(
                card,
                text=value,
                font=ctk.CTkFont(size=31, weight="bold"),
                text_color=color,
            ).pack(anchor="w", padx=20)

            subtitle = (
                "Table not found"
                if count is None
                else "Records in cf_tech.db"
            )

            ctk.CTkLabel(
                card,
                text=subtitle,
                font=ctk.CTkFont(size=11),
                text_color=MUTED,
            ).pack(anchor="w", padx=20, pady=(5, 18))

        # Panel containing the most recent session records.
        # Panneau contenant un aperçu des sessions de formation.
        preview = ctk.CTkFrame(
            page,
            fg_color=PANEL,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        preview.grid(
            row=4,
            column=0,
            columnspan=2,
            sticky="ew",
            pady=(4, 0),
        )

        ctk.CTkLabel(
            preview,
            text="Recent training sessions",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=TEXT,
        ).pack(anchor="w", padx=20, pady=(18, 12))

        # Handle missing database files or tables gracefully.
        # Gère proprement les bases ou tables absentes.
        try:
            table_name, columns, rows = self.database.read_table(
                self.PAGE_TABLES["Training Sessions"],
                limit=5,
            )

            if table_name and rows:
                self.render_small_table(preview, columns, rows)
            elif table_name:
                self.show_message(
                    preview,
                    "The training sessions table exists but contains no records.",
                )
            else:
                self.show_message(
                    preview,
                    "No training sessions table was found in cf_tech.db.",
                )

        except (FileNotFoundError, sqlite3.Error) as error:
            self.show_message(
                preview,
                f"Unable to load training sessions: {error}",
            )

        ctk.CTkLabel(
            preview,
            text=f"Database: {DATABASE_PATH.name}",
            font=ctk.CTkFont(size=10),
            text_color=MUTED,
        ).pack(anchor="w", padx=20, pady=(12, 18))

    def safe_count(self, candidates):
        """
        Return a record count, or None if the table cannot be read.
        Retourne un nombre d'enregistrements ou None si la table est inaccessible.
        """
        try:
            return self.database.count_rows(candidates)
        except (FileNotFoundError, sqlite3.Error):
            return None

    # -----------------------------------------------------
    # Data pages / Pages de données
    # -----------------------------------------------------

    def show_data_page(self, page_name):
        """
        Display records from the database table linked to this page.
        Affiche les enregistrements de la table associée à cette page.
        """
        page = ctk.CTkFrame(
            self.page_container,
            fg_color="transparent",
        )
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)

        # Page heading and refresh button.
        # Titre de la page et bouton d'actualisation.
        heading = ctk.CTkFrame(
            page,
            fg_color="transparent",
        )
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        heading.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            heading,
            text=page_name,
            font=ctk.CTkFont(size=29, weight="bold"),
            text_color=TEXT,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkButton(
            heading,
            text="↻  Refresh",
            width=105,
            height=38,
            corner_radius=9,
            fg_color=ACCENT,
            hover_color=ACCENT_HOVER,
            command=lambda: self.show_page(page_name),
        ).grid(row=0, column=1, sticky="e")

        # Search toolbar. Searching filters the displayed rows locally.
        # Barre de recherche. La recherche filtre localement les lignes affichées.
        toolbar = ctk.CTkFrame(
            page,
            fg_color="transparent",
        )
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        toolbar.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            toolbar,
            height=40,
            placeholder_text=f"Search {page_name.lower()}...",
            fg_color=PANEL,
            border_color=BORDER,
            text_color=TEXT,
            placeholder_text_color=MUTED,
            corner_radius=9,
        )
        self.search_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 12),
        )

        ctk.CTkButton(
            toolbar,
            text="Search",
            width=95,
            height=40,
            corner_radius=9,
            fg_color=PANEL,
            hover_color=PANEL_HOVER,
            border_width=1,
            border_color=BORDER,
            text_color=TEXT,
            command=self.filter_current_table,
        ).grid(row=0, column=1, sticky="e")

        # Main table container.
        # Conteneur principal du tableau.
        self.table_frame = ctk.CTkFrame(
            page,
            fg_color=PANEL,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        self.table_frame.grid(row=2, column=0, sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)

        # Store the original data separately so repeated searches work.
        # Conserve les données originales pour permettre plusieurs recherches.
        self.current_table_columns = []
        self.current_table_rows = []
        self.current_table_name = None

        candidates = self.PAGE_TABLES[page_name]

        try:
            table_name, columns, rows = self.database.read_table(
                candidates,
                limit=200,
            )
        except (FileNotFoundError, sqlite3.Error) as error:
            self.show_message(
                self.table_frame,
                f"Could not read database: {error}",
            )
            return

        # Display an informative message if the expected table is missing.
        # Affiche un message explicite si la table attendue est absente.
        if table_name is None:
            self.show_message(
                self.table_frame,
                (
                    f"No table found for '{page_name}'.\n\n"
                    "Check the table names in cf_tech.db. "
                    "This interface tries common English and French names."
                ),
            )
            return

        self.current_table_name = table_name
        self.current_table_columns = columns
        self.current_table_rows = rows

        self.table_title = ctk.CTkLabel(
            self.table_frame,
            text=f"Table: {table_name}",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=MUTED,
        )
        self.table_title.pack(anchor="w", padx=18, pady=(15, 5))

        self.data_area = ctk.CTkScrollableFrame(
            self.table_frame,
            fg_color="transparent",
        )
        self.data_area.pack(fill="both", expand=True, padx=8, pady=8)

        self.draw_data_table(
            self.data_area,
            self.current_table_columns,
            self.current_table_rows,
        )

        self.result_label = ctk.CTkLabel(
            self.table_frame,
            text=f"{len(rows)} records displayed",
            font=ctk.CTkFont(size=10),
            text_color=MUTED,
        )
        self.result_label.pack(anchor="w", padx=18, pady=(0, 15))

    def draw_data_table(self, parent, columns, rows):
        """
        Render database columns and records as a visual table.
        Affiche les colonnes et les enregistrements sous forme de tableau.
        """
        # Clear the previous table before drawing filtered results.
        # Efface l'ancien tableau avant d'afficher les résultats filtrés.
        for child in parent.winfo_children():
            child.destroy()

        if not columns:
            self.show_message(parent, "No columns were found in this table.")
            return

        # Table header.
        # En-tête du tableau.
        header = ctk.CTkFrame(
            parent,
            fg_color="#1B2942",
            corner_radius=8,
        )
        header.pack(fill="x", padx=4, pady=(4, 8))

        for index, column in enumerate(columns):
            header.grid_columnconfigure(index, weight=1)

            ctk.CTkLabel(
                header,
                text=column.upper(),
                font=ctk.CTkFont(size=9, weight="bold"),
                text_color=MUTED,
                anchor="w",
            ).grid(
                row=0,
                column=index,
                sticky="ew",
                padx=10,
                pady=12,
            )

        if not rows:
            self.show_message(parent, "This table contains no records.")
            return

        # Create one visual row for each database record.
        # Crée une ligne visuelle pour chaque enregistrement.
        for values in rows:
            row_frame = ctk.CTkFrame(
                parent,
                fg_color="transparent",
            )
            row_frame.pack(fill="x", padx=4, pady=2)

            for index, value in enumerate(values):
                row_frame.grid_columnconfigure(index, weight=1)

                ctk.CTkLabel(
                    row_frame,
                    text=value,
                    font=ctk.CTkFont(size=11),
                    text_color=TEXT,
                    anchor="w",
                    wraplength=220,
                ).grid(
                    row=0,
                    column=index,
                    sticky="ew",
                    padx=10,
                    pady=12,
                )

            # Separator between records.
            # Séparateur entre les enregistrements.
            ctk.CTkFrame(
                parent,
                height=1,
                fg_color=BORDER,
            ).pack(fill="x", padx=4)

    def filter_current_table(self):
        """
        Filter the current page's records without changing the database.
        Filtre les enregistrements de la page sans modifier la base de données.
        """
        query = self.search_entry.get().strip().lower()

        # Search across every displayed column.
        # Recherche dans toutes les colonnes affichées.
        if not query:
            filtered_rows = self.current_table_rows
        else:
            filtered_rows = [
                row
                for row in self.current_table_rows
                if any(query in value.lower() for value in row)
            ]

        self.draw_data_table(
            self.data_area,
            self.current_table_columns,
            filtered_rows,
        )

        if (
            hasattr(self, "result_label")
            and self.result_label.winfo_exists()
        ):
            self.result_label.configure(
                text=f"{len(filtered_rows)} records displayed"
            )

    # -----------------------------------------------------
    # UI helpers / Fonctions utilitaires de l'interface
    # -----------------------------------------------------

    @staticmethod
    def show_message(parent, message):
        """
        Display an informational message in a container.
        Affiche un message informatif dans un conteneur.
        """
        ctk.CTkLabel(
            parent,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color=MUTED,
            justify="left",
            wraplength=650,
        ).pack(anchor="w", padx=20, pady=20)

    def render_small_table(self, parent, columns, rows):
        """
        Display a compact session preview on the dashboard.
        Affiche un aperçu compact des sessions sur le tableau de bord.
        """
        for row in rows:
            display_values = [
                f"{columns[index]}: {value}"
                for index, value in enumerate(row[:3])
            ]

            ctk.CTkLabel(
                parent,
                text="   •   ".join(display_values),
                font=ctk.CTkFont(size=11),
                text_color=MUTED,
                anchor="w",
                justify="left",
                wraplength=750,
            ).pack(fill="x", padx=20, pady=6)


# =========================================================
# Entry point / Point d'entrée
# =========================================================

if __name__ == "__main__":
    # Create the application and start the GUI event loop.
    # Crée l'application et démarre la boucle d'événements graphique.
    app = CFTechApp()
    app.mainloop()
