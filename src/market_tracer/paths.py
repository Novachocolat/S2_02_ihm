# ==============================================================
# Chemins des ressources de l'application
# Tous les chemins sont ancrés à la racine du projet : l'application
# fonctionne donc quel que soit le dossier depuis lequel elle est lancée.
# ==============================================================

from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]

ASSETS_DIR = ROOT_DIR / "assets"
IMG_DIR = ASSETS_DIR / "img"
JSON_DIR = ASSETS_DIR / "json"

LICENCE_PATH = ROOT_DIR / "LICENCE"
DB_PATH = ROOT_DIR / "market_tracer.db"

APP_ICON = IMG_DIR / "logo_v1.png"
LOGO_EXT = IMG_DIR / "logo_ext_v1.png"
BANNER_HORIZONTAL = IMG_DIR / "mt_banner_h.png"
DEFAULT_PRODUCTS_JSON = JSON_DIR / "liste_produits.json"


def banner_path(number: int) -> Path:
    """Chemin de la bannière verticale numéro `number` (page de connexion)."""
    return IMG_DIR / f"mt_banner_{number}.png"
