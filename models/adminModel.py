# ==============================================================
# Modèle pour la fenêtre d'administration du gérant
# Développé par D. MELOCCO, L. PACE--BOULNOIS, S. LECLERCQ-SPETER, N. COLIN
# Dernière modification : 13/06/2025
# ==============================================================

import sqlite3

def get_shop_data(user_id):
    """Récupère les données du magasin pour un utilisateur donné."""
    conn = sqlite3.connect("market_tracer.db")
    c = conn.cursor()
    c.execute("SELECT articles_json, plan_json, chemin FROM shops WHERE user_id=?", (user_id,))
    result = c.fetchone()
    conn.close()
    return result

def update_shop_image(user_id, file_name):
    """Met à jour le chemin de l'image du magasin pour un utilisateur donné."""
    conn = sqlite3.connect("market_tracer.db")
    c = conn.cursor()
    c.execute("UPDATE shops SET chemin=? WHERE user_id=?", (file_name, user_id))
    conn.commit()
    conn.close()

def update_articles_json(user_id, articles_json_content):
    """Met à jour le contenu JSON des articles du magasin pour un utilisateur donné."""
    conn = sqlite3.connect("market_tracer.db")
    c = conn.cursor()
    c.execute("UPDATE shops SET articles_json=? WHERE user_id=?", (articles_json_content, user_id))
    conn.commit()
    conn.close()

def get_employees_shop_id(user_id):
    """Récupère l'ID du magasin associé à un employé donné."""
    conn = sqlite3.connect("market_tracer.db")
    c = conn.cursor()
    c.execute("SELECT id FROM shops WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row[0] if row else None

def get_shop_articles_by_id(shop_id):
    """Récupère les articles JSON d'un magasin à partir de son ID."""
    conn = sqlite3.connect("market_tracer.db")
    c = conn.cursor()
    c.execute("SELECT articles_json FROM shops WHERE id=?", (shop_id,))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None