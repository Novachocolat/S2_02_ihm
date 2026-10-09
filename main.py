# ==============================================================
# Fichier principal de l'application
# Développé par D. MELOCCO
# Dernière modification : 13/06/2025
# Lancement : python main.py
# ===============================================================

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from market_tracer.app import main

if __name__ == "__main__":
    main()
