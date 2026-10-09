# ==============================================================
# Liste avec glisser-déposer
# Développé par David Melocco et Simon Leclercq-Speter
# ==============================================================

from PyQt6.QtCore import QMimeData
from PyQt6.QtGui import QDrag
from PyQt6.QtWidgets import QListWidget


class DraggableListWidget(QListWidget):
    """Liste déroulante avec des éléments pouvant être glissés et déposés."""
    def startDrag(self, supportedActions):
        """Démarre le drag & drop de l'élément sélectionné."""
        item = self.currentItem()
        if not item:
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(item.text())
        drag.setMimeData(mime)
        drag.exec(supportedActions)
