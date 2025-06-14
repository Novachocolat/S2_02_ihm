# ==============================================================
# Modèle pour la fenêtre du client
# Développé par D. MELOCCO
# Dernière modification : 13/06/2025
# ==============================================================

import json
import os

def charger_produits_json(filepath):
    """Charge le fichier JSON des produits."""
    if not os.path.isfile(filepath):
        return {}
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

def exporter_liste_json(liste, filepath):
    """Exporte la liste de courses au format JSON."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(liste, f, ensure_ascii=False, indent=2)

def importer_liste_json(filepath):
    """Imprte une liste de courses depuis un fichier JSON."""
    if not os.path.isfile(filepath):
        return []
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)