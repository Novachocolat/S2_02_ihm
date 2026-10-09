# ==============================================================
# Constantes partagées de l'application
# ==============================================================

# Rôles des utilisateurs
ROLE_ADMIN = "Gérant"
ROLE_EMPLOYEE = "Employé"
ROLE_CUSTOMER = "Client"
ROLES = (ROLE_ADMIN, ROLE_EMPLOYEE, ROLE_CUSTOMER)

# Types de cases du plan
CELL_SHELF = "Rayon"
CELL_STOCK = "Stock"
CELL_CHECKOUT = "Caisse"
CELL_ENTRANCE = "Entrée"
CELL_WALL = "Mur"
TOOL_ERASER = "Gomme"  # Outil (et non type de case) : efface la case

# Filtre de catégories
ALL_CATEGORIES = "Toutes les catégories"

# Format de date affiché / enregistré pour la création d'un magasin
DATE_FORMAT = "dd/MM/yyyy"

# Séparateur « catégorie::produit » utilisé pour le glisser-déposer
DRAG_SEPARATOR = "::"
