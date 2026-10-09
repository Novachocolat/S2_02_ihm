# ==============================================================
# Modèle pour la fenêtre de connexion
# Développé par D. MELOCCO, L. PACE--BOULNOIS
# Dernière modification : 13/06/2025
# ==============================================================

from market_tracer.constants import ROLE_ADMIN, ROLE_EMPLOYEE
from market_tracer.database import connect


def init_db():
    """Initialise la base de données et crée les tables nécessaires."""
    with connect() as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                password TEXT,
                role TEXT,
                shop_id INTEGER,
                first_login INTEGER DEFAULT 1
            )
        ''')
        c.execute("""
            CREATE TABLE IF NOT EXISTS shops (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT,
                auteur TEXT,
                date_creation TEXT,
                apropos TEXT,
                chemin TEXT,
                articles_json TEXT,
                user_id INTEGER,
                plan_json TEXT,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        """)
        c.executemany(
            "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
            [("gerant", "1234", ROLE_ADMIN), ("employe", "abcd", ROLE_EMPLOYEE)],
        )


def get_user(username, password, role):
    """Récupère un utilisateur en fonction du nom d'utilisateur, du mot de passe et du rôle."""
    with connect() as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?", (username, password, role))
        return c.fetchone()


def set_first_login(user_id, value):
    """Met à jour le statut de premier login d'un utilisateur."""
    with connect() as conn:
        conn.execute("UPDATE users SET first_login=? WHERE id=?", (value, user_id))
