# ==============================================================
# Modèle des magasins (création, listing, suppression)
# Développé par L. PACE--BOULNOIS
# ==============================================================

from market_tracer.database import connect


def get_shop_details(user_id):
    """Retourne les informations détaillées du magasin d'un utilisateur (dict vide si aucun)."""
    with connect() as conn:
        c = conn.cursor()
        c.execute(
            "SELECT nom, auteur, date_creation, apropos, chemin, articles_json, plan_json "
            "FROM shops WHERE user_id=?",
            (user_id,),
        )
        row = c.fetchone()
    if not row:
        return {}
    keys = ("nom", "auteur", "date_creation", "apropos", "chemin", "articles_json", "plan_json")
    return {key: value or "" for key, value in zip(keys, row)}


def save_shop(user_id, nom, auteur, date_creation, apropos, chemin, articles_json, plan_json):
    """Met à jour le magasin de l'utilisateur, ou le crée s'il n'existe pas encore."""
    with connect() as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM shops WHERE user_id=?", (user_id,))
        if c.fetchone():
            c.execute("""
                UPDATE shops SET nom=?, auteur=?, date_creation=?, apropos=?, chemin=?, articles_json=?, plan_json=?
                WHERE user_id=?
            """, (nom, auteur, date_creation, apropos, chemin, articles_json, plan_json, user_id))
        else:
            c.execute("""
                INSERT INTO shops (user_id, nom, auteur, date_creation, apropos, chemin, articles_json, plan_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, nom, auteur, date_creation, apropos, chemin, articles_json, plan_json))


def count_shops():
    """Retourne le nombre de magasins dans la base de données."""
    with connect() as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM shops")
        return c.fetchone()[0]


def list_shops(user_id=None):
    """Liste les magasins (id, nom), ceux d'un utilisateur si `user_id` est donné."""
    with connect() as conn:
        c = conn.cursor()
        if user_id is None:
            c.execute("SELECT id, nom FROM shops")
        else:
            c.execute("SELECT id, nom FROM shops WHERE user_id=?", (user_id,))
        return c.fetchall()


def shop_exists(shop_id):
    """Indique si un magasin existe."""
    with connect() as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM shops WHERE id=?", (shop_id,))
        return c.fetchone() is not None


def delete_shop(shop_id):
    """Supprime un magasin."""
    with connect() as conn:
        conn.execute("DELETE FROM shops WHERE id=?", (shop_id,))
