# ==============================================================
# Accès à la base de données SQLite locale
# ==============================================================

import sqlite3
from contextlib import contextmanager
from typing import Iterator

from market_tracer.paths import DB_PATH


@contextmanager
def connect() -> Iterator[sqlite3.Connection]:
    """Ouvre la base de données, valide les modifications puis ferme la connexion."""
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()
