
"""CF-Tech - Training Management Interface.

Standalone graphical interface reading data from the SQLite database
cf_tech.db. All database access is read-only.
"""

from pathlib import Path
import sqlite3
import tkinter as tk

import customtkinter as ctk


# =========================================================
# Configuration
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "cf_tech.db"

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

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
# Database access
# =========================================================

class Database:
    """Read-only access to the CF-Tech SQLite database."""

    def __init__(self, database_path: Path):
        self.database_path = database_path

    def connect(self):
        """Open the existing database without creating a new one."""
        if not self.database_path.exists():
            raise FileNotFoundError(
                f"Database not found: {self.database_path}"
            )

        connection = sqlite3.connect(
            f"{self.database_path.as_uri()}?mode=ro",
            uri=True,
            timeout=5,
        )
        connection.row_factory = sqlite3.Row
        return connection

    def get_tables(self):
        """Return the available user tables."""
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
        """Return column names for a validated table."""
        tables = self.get_tables()

        if table_name not in tables:
            return []

        with self.connect() as connection:
            # Table names cannot be bound as SQL parameters.
            # Check membership in the actual database tables first.
            rows = connection.execute(
                f'PRAGMA table_info("{table_name}")'
            ).fetchall()

        return [row["name"] for row in rows]

    def find_table(self, candidates):
        """Find a table using case-insensitive candidate names."""
        tables = self.get_tables()
        lookup = {name.lower(): name for name in tables}

        for candidate in candidates:
            if candidate.lower() in lookup:
                return lookup[candidate.lower()]

        return None

    def read_table(self, candidates, limit=200):
        """Read a table if one of its candidate names exists."""
        table_name = self.find_table(candidates)

        if table_name is None:
            return None, [], []

        columns = self.get_table_columns(table_name)

        if not columns:
            return table_name, [], []

        with self.connect() as connection:
            # table_name was obtained from sqlite_master and checked.
            rows = connection.execute(
                f'SELECT * FROM "{table_name}" LIMIT ?',
                (limit,),
            ).fetchall()

        return table_name, columns, [
            [self.format_value(row[column]) for column in columns]
            for row in rows
        ]

    @staticmethod
    def format_value(value):
        """Convert database values into display-friendly text."""
        if value is None:
            return "—"

        text_value = str(value)

        if len(text_value) > 100:
            return text_value[:97] + "..."

        return text_value

    def count_rows(self, candidates):
        """Count records in a matching table, or return None."""
        table_name = self.find_table(candidates)

        if table_name is None:
            return None

        with self.connect() as connection:
            result = connection.execute(
                f'SELECT COUNT(*) FROM "{table_name}"'
            ).fetchone()

        return result[0]


# =========================================================
# Main application
# =========================================================

class CFTechApp(ctk.CTk):
    """CF-Tech graphical interface."""

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
        super().__init__()

        self.database = Database(DATABASE_PATH)
        self.current_page = "Dashboard"
        self.nav_buttons = {}

        self.title("CF-Tech | Training Management")
        self.geometry("1280x800")
        self.minsize(1000, 650)
        self.configure(fg_color=BACKGROUND)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_sidebar()
        self.build_main_area()
        self.show_page("Dashboard")

    # -----------------------------------------------------
    # Sidebar
    # -----------------------------------------------------

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=245,
            corner_radius=0,
            fg_color=SIDEBAR,
        )
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)

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
    # Main area
    # -----------------------------------------------------

    def build_main_area(self):
        self.main_area = ctk.CTkFrame(
            self,
            fg_color=BACKGROUND,
            corner_radius=0,
        )
        self.main_area.grid(row=0, column=1, sticky="nsew")
        self.main_area.grid_columnconfigure(0, weight=1)
        self.main_area.grid_rowconfigure(1, weight=1)

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
    # Page navigation
    # -----------------------------------------------------

    def show_page(self, page):
        self.current_page = page

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

        for widget in self.page_container.winfo_children():
            widget.destroy()

        if page == "Dashboard":
            self.show_dashboard()
        else:
            self.show_data_page(page)

    # -----------------------------------------------------
    # Dashboard
    # -----------------------------------------------------

    def show_dashboard(self):
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

        cards = [
            ("LEARNERS", ["apprenant", "apprenants", "learner", "learners"], "#60A5FA"),
            ("TRAINERS", ["formateur", "formateurs", "trainer", "trainers"], "#A78BFA"),
            ("ROOMS", ["salle", "salles", "room", "rooms"], SUCCESS),
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

        # Training sessions preview
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

        ctk.CTkLabel(
            preview,
            text=f"Database: {DATABASE_PATH.name}",
            font=ctk.CTkFont(size=10),
            text_color=MUTED,
        ).pack(anchor="w", padx=20, pady=(12, 18))

    def safe_count(self, candidates):
        try:
            return self.database.count_rows(candidates)
        except (FileNotFoundError, sqlite3.Error):
            return None

    # -----------------------------------------------------
    # Data pages
    # -----------------------------------------------------

    def show_data_page(self, page_name):
        page = ctk.CTkFrame(
            self.page_container,
            fg_color="transparent",
        )
        page.grid(row=0, column=0, sticky="nsew")
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)

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

        # Decorative button: this is a read-only interface.
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
            command=lambda: self.filter_current_table(),
        ).grid(row=0, column=1, sticky="e")

        self.table_frame = ctk.CTkFrame(
            page,
            fg_color=PANEL,
            corner_radius=14,
            border_width=1,
            border_color=BORDER,
        )
        self.table_frame.grid(row=2, column=0, sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)

        self.current_table_columns = []
        self.current_table_rows = []

        candidates = self.PAGE_TABLES[page_name]

        try:
            table_name, columns, rows = self.database.read_table(
                candidates,
                limit=200,
            )
        except (FileNotFoundError, sqlite3.Error) as error:
            table_name, columns, rows = None, [], []
            self.show_message(
                self.table_frame,
                f"Could not read database: {error}",
            )

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
        """Draw rows using the actual columns from SQLite."""
        for child in parent.winfo_children():
            child.destroy()

        if not columns:
            self.show_message(parent, "No columns were found in this table.")
            return

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

        for values in rows:
            row_frame = ctk.CTkFrame(
                parent,
                fg_color="transparent",
            )
            row_frame.pack(fill="x", padx=4, pady=2)

            for index, value in enumerate(values):
                row_frame.grid_columnconfigure(index, weight=1)

                label = ctk.CTkLabel(
                    row_frame,
                    text=value,
                    font=ctk.CTkFont(size=11),
                    text_color=TEXT,
                    anchor="w",
                    wraplength=220,
                )
                label.grid(
                    row=0,
                    column=index,
                    sticky="ew",
                    padx=10,
                    pady=12,
                )

            ctk.CTkFrame(
                parent,
                height=1,
                fg_color=BORDER,
            ).pack(fill="x", padx=4)

    def filter_current_table(self):
        """Filter the displayed rows locally without changing the database."""
        query = self.search_entry.get().strip().lower()

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

        if hasattr(self, "result_label") and self.result_label.winfo_exists():
            self.result_label.configure(
                text=f"{len(filtered_rows)} records displayed"
            )

    # -----------------------------------------------------
    # UI helpers
    # -----------------------------------------------------

    @staticmethod
    def show_message(parent, message):
        ctk.CTkLabel(
            parent,
            text=message,
            font=ctk.CTkFont(size=12),
            text_color=MUTED,
            justify="left",
            wraplength=650,
        ).pack(anchor="w", padx=20, pady=20)

    def render_small_table(self, parent, columns, rows):
        """Show a compact table preview on the dashboard."""
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
# Entry point
# =========================================================

if __name__ == "__main__":
    app = CFTechApp()
    app.mainloop()
