# ==============================================================
# Modèle des employés d'un magasin
# Développé par L. PACE--BOULNOIS
# ==============================================================

from market_tracer.constants import ROLE_EMPLOYEE
from market_tracer.database import connect


def list_employees(shop_id):
    """Liste les employés (id, nom d'utilisateur) d'un magasin."""
    with connect() as conn:
        c = conn.cursor()
        c.execute("SELECT id, username FROM users WHERE role=? AND shop_id=?", (ROLE_EMPLOYEE, shop_id))
        return c.fetchall()


def add_employee(shop_id, username, password):
    """Ajoute un employé à un magasin."""
    with connect() as conn:
        conn.execute(
            "INSERT INTO users (username, password, role, shop_id) VALUES (?, ?, ?, ?)",
            (username, password, ROLE_EMPLOYEE, shop_id),
        )


def update_employee(employee_id, username, password):
    """Modifie le nom d'utilisateur et le mot de passe d'un employé."""
    with connect() as conn:
        conn.execute("UPDATE users SET username=?, password=? WHERE id=?", (username, password, employee_id))


def delete_employee(employee_id):
    """Supprime un employé."""
    with connect() as conn:
        conn.execute("DELETE FROM users WHERE id=?", (employee_id,))
