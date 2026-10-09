# ==============================================================
# Market Tracer - Quadrillage (app n°1)
# Développé par David Melocco et Simon Leclercq-Speter
# Exportation et importation par Lysandre Pace-Boulnois
# Dernière modification : 13/06/2025
# ==============================================================

import json

from PyQt6.QtCore import Qt, QRectF, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QPen, QPixmap
from PyQt6.QtWidgets import (
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsView, QMessageBox, QToolTip
)

from market_tracer.constants import (
    CELL_CHECKOUT, CELL_ENTRANCE, CELL_SHELF, CELL_STOCK, CELL_WALL,
    DRAG_SEPARATOR, TOOL_ERASER
)

# Couleurs des éléments du plan
COLOR_TYPES = {
    CELL_SHELF: QColor(0, 0, 255, 120),      # Bleu pour les rayons
    CELL_CHECKOUT: QColor(255, 255, 0, 120),  # Jaune pour les caisses
    CELL_ENTRANCE: QColor(255, 0, 0, 120),    # Rouge pour l'entrée
    CELL_WALL: QColor(128, 128, 128, 120),    # Gris pour les murs
    CELL_STOCK: QColor(0, 255, 0, 120),       # Vert pour les stocks
}

# Émoji affiché sur une case selon la catégorie du produit (tous les rayons du JSON)
DEFAULT_CATEGORY = "Autre"
EMOJI_BY_CATEGORY = {
    "Fruits": "🍎",
    "Légumes": "🥦",
    "Viandes": "🍖",
    "Poissons": "🐟",
    "Boulangerie": "🥖",
    "Fromages": "🧀",
    "Boissons": "🥤",
    "Produits laitiers": "🥛",
    "Rayon frais": "🥪",
    "Crèmerie": "🧈",
    "Conserves": "🥫",
    "Apéritifs": "🍘",
    "Épicerie": "🛒",
    "Épicerie sucrée": "🍬",
    "Petit déjeuner": "🥐",
    "Articles Maison": "🧹",
    "Hygiène": "🧴",
    "Bureau": "🖊️",
    "Animaux": "🐾",
    DEFAULT_CATEGORY: "📦",
}

# Types de cases pouvant contenir un produit
PRODUCT_CELL_TYPES = (CELL_SHELF, CELL_STOCK)


class GridOverlay(QGraphicsView):
    """Vue graphique avec un quadrillage et des cellules coloriées pour un plan de marché."""
    grid_modified = pyqtSignal()

    def __init__(self):
        """Initialise la vue avec une scène graphique, un quadrillage et des cellules coloriées."""
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.image_item = None
        self.grid_size = 50
        self.entrance_number = 0

        self.colored_cells = {}     # (row, col) -> QColor
        self.objects_in_cells = {}  # (row, col) -> {"category": ..., "product": ...}
        self.setMouseTracking(True)

        # Coefficient de zoom
        self.zoom_factor = 1.0

        self.current_color_type = CELL_SHELF
        self.is_painting = False
        self.setAcceptDrops(True)

        self.is_panning = False
        self.last_pan_point = None

        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setInteractive(True)

    # ----------------------------------------------------------
    # Image, grille et zoom
    # ----------------------------------------------------------
    def load_image(self, path):
        """Charge une image et l'affiche dans la vue avec un quadrillage.

        Args:
            path (str): chemin d'accès à l'image.
        """
        pixmap = QPixmap(path)
        if pixmap.isNull():
            print("Erreur de chargement d'image")
            return

        self.scene.clear()
        self.colored_cells.clear()
        self.objects_in_cells.clear()

        # Créer l'image
        self.image_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.image_item)
        self.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.draw_grid()
        self.resetTransform()
        self.scale(self.zoom_factor, self.zoom_factor)

    def draw_grid(self):
        """Dessine le quadrillage et les cellules colorées sur l'image chargée."""
        if not self.image_item:
            return

        # Supprime tout sauf l'image de fond
        for item in self.scene.items():
            if isinstance(item, QGraphicsPixmapItem):
                continue
            self.scene.removeItem(item)
        rect = self.image_item.boundingRect()

        self._draw_cells()

        pen = QPen(Qt.GlobalColor.red)
        pen.setWidth(2)

        x = 0
        while x <= rect.width():
            self.scene.addLine(x, 0, x, rect.height(), pen)
            x += self.grid_size

        y = 0
        while y <= rect.height():
            self.scene.addLine(0, y, rect.width(), y, pen)
            y += self.grid_size

        self.grid_modified.emit()

    def _draw_cells(self):
        """Dessine les cases coloriées, avec l'émoji du produit qu'elles contiennent."""
        for (row, col), color in self.colored_cells.items():
            x = col * self.grid_size
            y = row * self.grid_size
            cell_rect = QRectF(x, y, self.grid_size, self.grid_size)
            self.scene.addRect(cell_rect, QPen(Qt.PenStyle.NoPen), QBrush(color))

            # Affichage de l'émoji centré si objet présent
            if (row, col) in self.objects_in_cells:
                category = self.objects_in_cells[(row, col)]["category"]
                emoji = EMOJI_BY_CATEGORY.get(category, "")
                if emoji:
                    self._draw_centered_emoji(emoji, x, y)

    def _draw_centered_emoji(self, emoji, x, y):
        """Dessine `emoji` au centre de la case dont le coin supérieur gauche est (x, y)."""
        font = QFont()
        font.setPointSize(int(self.grid_size * 0.7))

        # Mesure de l'émoji avant de le positionner
        temp_text_item = self.scene.addText(emoji)
        temp_text_item.setFont(font)
        text_rect = temp_text_item.boundingRect()
        self.scene.removeItem(temp_text_item)

        text_item = self.scene.addText(emoji)
        text_item.setFont(font)
        text_item.setPos(
            x + (self.grid_size - text_rect.width()) / 2,
            y + (self.grid_size - text_rect.height()) / 2,
        )

    def set_grid_size(self, size):
        """Définit la taille de la grille et redessine le quadrillage.

        Args:
            size (int): taille de la grille en pixels.
        """
        self.grid_size = size
        self.draw_grid()

    def set_zoom(self, factor):
        """Ajuste le zoom global du plan."""
        self.resetTransform()
        self.scale(factor, factor)
        self.zoom_factor = factor

    def _cell_key_at(self, scene_pos):
        """Retourne la clé (ligne, colonne) de la case située à `scene_pos`."""
        col = int(scene_pos.x() // self.grid_size)
        row = int(scene_pos.y() // self.grid_size)
        return (row, col)

    # ----------------------------------------------------------
    # Modes et édition des cases
    # ----------------------------------------------------------
    def set_pan_mode(self, enable):
        """Définit le mode de déplacement (pan) de la vue.

        Args:
            enable (bool): True pour activer le mode de déplacement, False pour le désactiver.
        """
        self.is_panning = enable
        if enable:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def set_current_color(self, color_type):
        """Définit le type de case (ou l'outil gomme) utilisé pour peindre."""
        self.current_color_type = color_type

    def color_cell_at_position(self, scene_pos):
        """Colore une cellule à la position donnée dans la scène."""
        x, y = scene_pos.x(), scene_pos.y()

        # Empêcher de colorier hors du plan
        if not self.image_item:
            return
        rect = self.image_item.boundingRect()
        if not (0 <= x < rect.width() and 0 <= y < rect.height()):
            return  # Ignore si hors de l'image

        cell_key = self._cell_key_at(scene_pos)

        # Limiter à une seule entrée
        if self.current_color_type == CELL_ENTRANCE:
            if self.entrance_number >= 1:
                QMessageBox.warning(self, "Erreur", "Il ne peut y avoir qu'une seule entrée.")
                self.is_painting = False
                return
            self.entrance_number = 1

        # Si on est en mode gomme, on supprime la cellule
        if self.current_color_type == TOOL_ERASER:
            if self.colored_cells.get(cell_key) == COLOR_TYPES[CELL_ENTRANCE]:
                self.entrance_number = 0
            self.colored_cells.pop(cell_key, None)
            self.objects_in_cells.pop(cell_key, None)
        else:
            self.colored_cells[cell_key] = COLOR_TYPES[self.current_color_type]

        self.draw_grid()
        self.grid_modified.emit()

    def reset_colored_cells(self):
        """Réinitialise le quadrillage en supprimant toutes les cellules coloriées et les objets."""
        self.colored_cells.clear()
        self.objects_in_cells.clear()
        self.draw_grid()
        self.grid_modified.emit()

    # ----------------------------------------------------------
    # Évènements souris et glisser-déposer
    # ----------------------------------------------------------
    def mousePressEvent(self, event):
        """Gère l'appui de la souris pour le déplacement ou la peinture."""
        if not self.image_item:
            return

        # Mode de déplacement
        if self.is_panning:
            if event.button() == Qt.MouseButton.LeftButton:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.last_pan_point = event.pos()
        else:
            if event.button() == Qt.MouseButton.LeftButton:
                self.is_painting = True
                scene_pos = self.mapToScene(event.pos())
                self.color_cell_at_position(scene_pos)

    def mouseMoveEvent(self, event):
        """Gère le mouvement de la souris pour afficher des informations sur les cellules ou peindre."""
        scene_pos = self.mapToScene(event.pos())
        cell_key = self._cell_key_at(scene_pos)

        if self.is_panning and self.last_pan_point:
            delta = event.pos() - self.last_pan_point
            self.last_pan_point = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        elif self.is_painting:
            self.color_cell_at_position(scene_pos)
        else:
            self._show_cell_tooltip(cell_key, event)

    def _show_cell_tooltip(self, cell_key, event):
        """Affiche le produit contenu dans la case survolée (rayon ou stock), sinon masque l'infobulle."""
        cell_color = self.colored_cells.get(cell_key)
        if cell_color in [COLOR_TYPES[cell_type] for cell_type in PRODUCT_CELL_TYPES]:
            obj_data = self.objects_in_cells.get(cell_key)
            if obj_data:
                QToolTip.showText(event.globalPosition().toPoint(), f"Produit : {obj_data['product']}", self)
                return
        QToolTip.hideText()

    def mouseReleaseEvent(self, event):
        """Gère le relâchement de la souris pour arrêter le déplacement ou la peinture."""
        if self.is_panning:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self.last_pan_point = None
        elif event.button() == Qt.MouseButton.LeftButton:
            self.is_painting = False

    def dragEnterEvent(self, event):
        """Gère l'entrée d'un objet dans la vue pour le drag & drop."""
        event.accept()

    def dragMoveEvent(self, event):
        """Gère le mouvement d'un objet pendant le drag & drop."""
        event.accept()

    def dropEvent(self, event):
        """Gère le dépôt d'un objet dans la vue pour le drag & drop."""
        if not self.image_item:
            return

        category_name, obj_name = self._parse_dropped_text(event.mimeData().text())
        cell_key = self._cell_key_at(self.mapToScene(event.position().toPoint()))

        # On autorise les dépôts sur Rayon ET Stock
        cell_color = self.colored_cells.get(cell_key)
        if any(cell_color == COLOR_TYPES[cell_type] for cell_type in PRODUCT_CELL_TYPES):
            self.objects_in_cells[cell_key] = {"category": category_name, "product": obj_name}
            self.draw_grid()
            self.grid_modified.emit()
        else:
            QMessageBox.warning(self, "Attention", "Vous ne pouvez déposer que sur des Rayons ou Stocks.")

    @staticmethod
    def _parse_dropped_text(data):
        """Extrait (catégorie, produit) du texte glissé « catégorie::produit »."""
        if DRAG_SEPARATOR in data:
            category, product = data.split(DRAG_SEPARATOR, 1)
            category_name = category.strip()
            obj_name = product.strip()
        else:
            category_name = DEFAULT_CATEGORY
            obj_name = data.strip().replace('"', '').replace("'", "").strip()

        # L'émoji de la catégorie est affiché dans le graphique
        if category_name not in EMOJI_BY_CATEGORY:
            category_name = DEFAULT_CATEGORY
        return category_name, obj_name

    # ----------------------------------------------------------
    # Exportation et importation
    # ----------------------------------------------------------
    def export_cells_to_json(self, path_or_buffer):
        """Exporte les cellules coloriées et les objets en JSON."""
        data = {
            "grid_size": self.grid_size,
            "cells": []
        }
        for (row, col), color in self.colored_cells.items():
            for type_str, type_color in COLOR_TYPES.items():
                if color.rgba() == type_color.rgba():
                    cell_data = {
                        "row": row,
                        "col": col,
                        "type": type_str
                    }
                    if type_str in PRODUCT_CELL_TYPES:
                        obj_data = self.objects_in_cells.get((row, col), None)
                        cell_data["object"] = {
                            "category": obj_data["category"],
                            "product": obj_data["product"]
                        } if obj_data else None
                    data["cells"].append(cell_data)
                    break
        try:
            if hasattr(path_or_buffer, "write"):
                json.dump(data, path_or_buffer, indent=2, ensure_ascii=False)
            else:
                with open(path_or_buffer, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de l'exportation : {e}")
            QMessageBox.warning(self, "Erreur", f"Erreur lors de l'exportation : {e}")

    def import_cells_from_json(self, path):
        """Importe les cellules coloriées et les objets depuis un fichier JSON.

        Args:
            path (str): chemin d'accès au fichier JSON.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._import_cells_from_data(data)
        except Exception as e:
            print(f"Erreur lors de l'importation : {e}")

    def import_cells_from_json_content(self, json_content):
        """Importe les cellules coloriées et les objets depuis une chaîne JSON.

        Args:
            json_content (str): chaîne JSON contenant les données des cellules.
        """
        try:
            data = json.loads(json_content)
            self._import_cells_from_data(data)
        except Exception as e:
            print(f"Erreur lors de l'importation (content) : {e}")

    def _import_cells_from_data(self, data):
        """Importe les cellules coloriées et les objets depuis un dictionnaire ou une liste."""
        self.colored_cells.clear()
        self.objects_in_cells.clear()
        self.entrance_number = 0
        if isinstance(data, dict) and "grid_size" in data:
            self.set_grid_size(data["grid_size"])
        cells = data["cells"] if isinstance(data, dict) and "cells" in data else data
        for cell in cells:
            row = cell.get("row")
            col = cell.get("col")
            type_str = cell.get("type")
            obj = cell.get("object")
            if type_str in COLOR_TYPES:
                self.colored_cells[(row, col)] = COLOR_TYPES[type_str]
                if obj:
                    if isinstance(obj, dict):
                        self.objects_in_cells[(row, col)] = {
                            "category": obj.get("category", DEFAULT_CATEGORY),
                            "product": obj.get("product", "")
                        }
                    else:
                        self.objects_in_cells[(row, col)] = {
                            "category": DEFAULT_CATEGORY,
                            "product": obj
                        }
                if type_str == CELL_ENTRANCE:
                    self.entrance_number = 1
        self.draw_grid()
