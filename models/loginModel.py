# ==============================================================
# Modèle pour la fenêtre de connexion
# Développé par D. MELOCCO, L. PACE--BOULNOIS
# Dernière modification : 13/06/2025
# ==============================================================

import sqlite3

def init_db():
    """Initialise la base de données et crée les tables nécessaires."""
    with sqlite3.connect("market_tracer.db") as conn:
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
        c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('gerant', '1234', 'Gérant')")
        c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES ('employe', 'abcd', 'Employé')")
        conn.commit()

def get_user(username, password, role):
    """Récupère un utilisateur de la base de données en fonction du nom d'utilisateur, mot de passe et rôle."""
    with sqlite3.connect("market_tracer.db") as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=? AND password=? AND role=?", (username, password, role))
        return c.fetchone()

def set_first_login(user_id, value):
    """Met à jour le statut de premier login d'un utilisateur."""
    with sqlite3.connect("market_tracer.db") as conn:
        c = conn.cursor()
        c.execute("UPDATE users SET first_login=? WHERE id=?", (value, user_id))
        conn.commit()

def get_shop_info(shop_id):
    """Récupère les informations d'un magasin à partir de son ID."""
    with sqlite3.connect("market_tracer.db") as conn:
        c = conn.cursor()
        c.execute("SELECT articles_json, chemin FROM shops WHERE id=?", (shop_id,))
        return c.fetchone()

def get_nb_shops():
    """Retourne le nombre de magasins dans la base de données."""
    with sqlite3.connect("market_tracer.db") as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM shops")
        return c.fetchone()[0]

def get_articles_json(shop_id):
    """Récupère le JSON des articles d'un magasin à partir de son ID."""
    with sqlite3.connect("market_tracer.db") as conn:
        c = conn.cursor()
        c.execute("SELECT articles_json FROM shops WHERE id=?", (shop_id,))
        result = c.fetchone()
        return result[0] if result else None