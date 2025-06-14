# ==============================================================

# Market Tracer - Quadrillage (app n°1)
# Développé par David Melocco et Simon Leclercq-Speter
# Dernière modification : 13/06/2025

# ==============================================================

# Importations
import sys
import json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QGraphicsView, QGraphicsScene,
    QGraphicsPixmapItem, QVBoxLayout, QWidget, QSlider, QPushButton, QHBoxLayout,
    QGroupBox, QMessageBox, QListWidget, QListWidgetItem, QLabel, QToolTip
)
from PyQt6.QtGui import QDrag, QPixmap, QFont, QBrush, QPen, QColor
from PyQt6.QtCore import QMimeData, Qt, QRectF, pyqtSignal

# ==============================================================
# Quadrillage avec des cellules colorées
# ==============================================================
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

        self.colored_cells = {}
        self.objects_in_cells = {}
        self.setMouseTracking(True)

        # Coefficient de zoom
        self.zoom_factor = 1.0

        # Couleurs des éléments du plan 
        self.color_types = {
            'Rayon': QColor(0, 0, 255, 120), # Bleu pour les rayons
            'Caisse': QColor(255, 255, 0, 120), # Jaune pour les caisses
            'Entrée': QColor(255, 0, 0, 120), # Rouge pour l'entrée
            'Mur': QColor(128, 128, 128, 120), # Gris pour les murs
            'Stock': QColor(0, 255, 0, 120), # Vert pour les stocks
        }

        # Tous les rayons du JSON 
        self.emoji_mapping = {
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
            "Autre": "📦"
        }

        self.current_color_type = 'Rayon'
        self.is_painting = False
        self.setAcceptDrops(True)

        self.is_panning = False
        self.last_pan_point = None

        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setInteractive(True)

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

        # Cases coloriées et émojis
        for (row, col), color in self.colored_cells.items():
            x = col * self.grid_size
            y = row * self.grid_size
            cell_rect = QRectF(x, y, self.grid_size, self.grid_size)
            self.scene.addRect(cell_rect, QPen(Qt.PenStyle.NoPen), QBrush(color))

            # Affichage de l'émoji centré si objet présent
            if (row, col) in self.objects_in_cells:
                obj_data = self.objects_in_cells[(row, col)]
                category = obj_data["category"]
                emoji = self.emoji_mapping.get(category, "")
                if emoji:
                    font = QFont()
                    font.setPointSize(int(self.grid_size * 0.7))
                    temp_text_item = self.scene.addText(emoji)
                    temp_text_item.setFont(font)
                    text_rect = temp_text_item.boundingRect()
                    self.scene.removeItem(temp_text_item)
                    text_item = self.scene.addText(emoji)
                    text_item.setFont(font)
                    offset_x = x + (self.grid_size - text_rect.width()) / 2
                    offset_y = y + (self.grid_size - text_rect.height()) / 2
                    text_item.setPos(offset_x, offset_y)

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

    def set_grid_size(self, size):
        """Définit la taille de la grille et redessine le quadrillage.

        Args:
            size (int): taille de la grille en pixels.
        """
        self.grid_size = size
        self.draw_grid()

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

        col, row = int(x // self.grid_size), int(y // self.grid_size)
        cell_key = (row, col)

        # Limiter à une seule entrée
        if self.current_color_type == 'Entrée':
            if self.entrance_number >= 1:
                QMessageBox.warning(self, "Erreur", "Il ne peut y avoir qu'une seule entrée.")
                self.is_painting = False
                return
            self.entrance_number = 1

        # Si on est en mode gomme, on supprime la cellule
        if self.current_color_type == 'Gomme':
            if self.colored_cells.get(cell_key) == self.color_types['Entrée']:
                self.entrance_number = 0
            self.colored_cells.pop(cell_key, None)
            self.objects_in_cells.pop(cell_key, None)
        else:
            color = self.color_types[self.current_color_type]
            self.colored_cells[cell_key] = color

        self.draw_grid()
        self.grid_modified.emit()

    def reset_colored_cells(self):
        """Réinitialise le quadrillage en supprimant toutes les cellules coloriées et les objets."""
        self.colored_cells.clear()
        self.objects_in_cells.clear()
        self.draw_grid()
        self.grid_modified.emit()

    # Drag & Drop
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
        col = int(scene_pos.x() // self.grid_size)
        row = int(scene_pos.y() // self.grid_size)
        cell_key = (row, col)

        # Afficher des informations sur la cellule
        if self.is_panning and self.last_pan_point:
            delta = event.pos() - self.last_pan_point
            self.last_pan_point = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        elif self.is_painting:
            self.color_cell_at_position(scene_pos)
        else:
            if self.colored_cells.get(cell_key) in [self.color_types['Rayon'], self.color_types['Stock']]:
                obj_data = self.objects_in_cells.get(cell_key)
                if obj_data:
                    product_name = obj_data["product"]
                    QToolTip.showText(event.globalPosition().toPoint(), f"Produit : {product_name}", self)
                else:
                    QToolTip.hideText()
            else:
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

        data = event.mimeData().text()

        # On récupère la catégorie et le produit depuis le texte drag & drop
        if "::" in data:
            category, product = data.split("::", 1)
            obj_name = product.strip()  
        else:
            obj_name = data.strip().replace('"', '').replace("'", "").strip()

        # On garde l'emoji sur la catégorie pour l'afficher dans le graphique
        category_name = category.strip() if "::" in data else "Autre"

        if category_name not in self.emoji_mapping:
            category_name = "Autre"

        scene_pos = self.mapToScene(event.position().toPoint())
        col = int(scene_pos.x() // self.grid_size)
        row = int(scene_pos.y() // self.grid_size)
        cell_key = (row, col)

        # On autorise les dépôts sur Rayon ET Stock
        allowed_types = ["Rayon", "Stock"]  
        cell_color = self.colored_cells.get(cell_key)

        if any(cell_color == self.color_types[cell_type] for cell_type in allowed_types):
            self.objects_in_cells[cell_key] = {"category": category_name, "product": obj_name}
            self.draw_grid()
            self.grid_modified.emit()
        else:
            QMessageBox.warning(self, "Attention", "Vous ne pouvez déposer que sur des Rayons ou Stocks.")

# ==============================================================
# Exportation et importation par Lysandre Pace-Boulnois
# ==============================================================
    def export_cells_to_json(self, path_or_buffer):
        """Exporte les cellules coloriées et les objets en JSON."""
        data = {
            "grid_size": self.grid_size,
            "cells": []
        }
        for (row, col), color in self.colored_cells.items():
            for type_str, type_color in self.color_types.items():
                if color.rgba() == type_color.rgba():
                    cell_data = {
                        "row": row,
                        "col": col,
                        "type": type_str
                    }
                    if type_str in ["Rayon", "Stock"]:
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

    def export_cells_to_json_string(self):
        """Exporte les cellules coloriées et les objets en JSON sous forme de chaîne."""
        import io
        buffer = io.StringIO()
        self.export_cells_to_json(buffer)
        return buffer.getvalue()

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
            self.grid_size = data["grid_size"]
            self.set_grid_size(self.grid_size)
        cells = data["cells"] if isinstance(data, dict) and "cells" in data else data
        for cell in cells:
            row = cell.get("row")
            col = cell.get("col")
            type_str = cell.get("type")
            obj = cell.get("object")
            if type_str in self.color_types:
                self.colored_cells[(row, col)] = self.color_types[type_str]
                if obj:
                    if isinstance(obj, dict):
                        self.objects_in_cells[(row, col)] = {
                            "category": obj.get("category", "Autre"),
                            "product": obj.get("product", "")
                        }
                    else:
                        self.objects_in_cells[(row, col)] = {
                            "category": "Autre",
                            "product": obj
                        }
                if type_str == "Entrée":
                    self.entrance_number = 1
        self.draw_grid()

    def set_zoom(self, factor):
        """Ajuste le zoom global du plan."""
        self.resetTransform()
        self.scale(factor, factor)
        self.zoom_factor = factor

# ==============================================================
# Liste déroulante avec drag & drop
# ==============================================================
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

# ==============================================================
# Programme principal
# ==============================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Quadrillage")

        self.grid_view = GridOverlay()

        # Bloc JSON gauche
        self.json_list = DraggableListWidget()
        self.json_list.setDragEnabled(True)

        load_json_btn = QPushButton("Charger les produits")
        load_json_btn.clicked.connect(self.load_json_list)

        json_layout = QVBoxLayout()
        json_layout.addWidget(load_json_btn)
        json_layout.addWidget(self.json_list)
        json_group = QGroupBox("Objets")
        json_group.setFixedWidth(180)
        json_group.setLayout(json_layout)
        button_layout = QVBoxLayout()
        open_btn = QPushButton("Charger un plan")
        open_btn.clicked.connect(self.open_image)
        button_layout.addWidget(open_btn)
        reset_btn = QPushButton("Réinitialiser")
        reset_btn.clicked.connect(self.confirm_reset)
        button_layout.addWidget(reset_btn)
        export_btn = QPushButton("Exporter en JSON")
        export_btn.clicked.connect(self.export_cells)
        button_layout.addWidget(export_btn)
        import_btn = QPushButton("Importer JSON")
        import_btn.clicked.connect(self.import_cells)
        button_layout.addWidget(import_btn)
        color_buttons = QVBoxLayout()
        btn_main = QPushButton("Déplacer")
        btn_main.clicked.connect(lambda: self.set_main_mode())
        color_buttons.addWidget(btn_main)
        for label, color in [
            ("Rayon", 'Rayon'), ("Caisse", 'Caisse'),
            ("Entrée", 'Entrée'), ("Mur", 'Mur'), ("Stock", 'Stock'), ("Gomme", 'Gomme')]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, c=color: self.set_paint_mode(c))
            color_buttons.addWidget(btn)
        color_group = QGroupBox("Outils")
        color_group.setLayout(color_buttons)
        button_layout.addWidget(color_group)
        buttons_group = QGroupBox("Commandes")
        buttons_group.setLayout(button_layout)
        main_layout = QHBoxLayout()
        main_layout.addWidget(json_group)
        main_layout.addWidget(buttons_group)
        main_layout.addWidget(self.grid_view)
        grid_layout = QVBoxLayout()
        self.slider = QSlider(Qt.Orientation.Vertical)
        self.slider.setMinimum(25)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.on_grid_size_changed)
        self.grid_view.slider = self.slider
        self.grid_label = QLabel(f"Grille: {self.slider.value()} px")
        self.grid_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        grid_layout.addWidget(self.slider)
        grid_layout.addWidget(self.grid_label)
        grid_group = QWidget()
        grid_group.setLayout(grid_layout)
        main_layout.addWidget(grid_group)
        zoom_layout = QVBoxLayout()
        self.zoom_slider = QSlider(Qt.Orientation.Vertical)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(300)
        self.zoom_slider.setValue(50)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)
        self.zoom_label = QLabel("50%")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        zoom_layout.addWidget(self.zoom_slider)
        zoom_layout.addWidget(self.zoom_label)
        zoom_group = QWidget()
        zoom_group.setLayout(zoom_layout)
        main_layout.addWidget(zoom_group)
        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def set_main_mode(self):
        self.grid_view.set_pan_mode(True)

    def set_paint_mode(self, color_type):
        self.grid_view.set_pan_mode(False)
        self.grid_view.set_current_color(color_type)

    def on_grid_size_changed(self, value):
        self.grid_view.set_grid_size(value)
        self.grid_label.setText(f"Grille: {value} px")

    def on_zoom_changed(self, value):
        factor = value / 100.0
        self.grid_view.set_zoom(factor)
        self.zoom_label.setText(f"{value}%")

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "", "Images (*.png *.jpg *.bmp *.jpeg)")
        if file_name:
            self.grid_view.load_image(file_name)
            self.zoom_slider.setValue(50)

    def confirm_reset(self):
        reply = QMessageBox.question(self, "Confirmation",
            "Êtes-vous sûr de vouloir tout réinitialiser ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.grid_view.reset_colored_cells()

    def export_cells(self):
        if self.grid_view.image_item is None:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord charger une image de plan avant d'exporter un JSON.")
            return
        file_name, _ = QFileDialog.getSaveFileName(self, "Exporter en JSON", "", "JSON (*.json)")
        if file_name:
            self.grid_view.export_cells_to_json(file_name)
            QMessageBox.information(self, "Export", "Exportation réussie !")

    def import_cells(self):
        if self.grid_view.image_item is None:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord charger une image de plan avant d'importer un JSON.")
            return
        file_name, _ = QFileDialog.getOpenFileName(self, "Importer JSON", "", "JSON (*.json)")
        if file_name:
            self.grid_view.import_cells_from_json(file_name)
            QMessageBox.information(self, "Import", "Importation réussie !")

    def load_json_list(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Charger un JSON d'objets", "", "JSON (*.json)")
        if not file_name:
            return
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.json_list.clear()
            if isinstance(data, dict):
                for category, items in data.items():
                    for item in items:
                        text = f"{category}::{item}"
                        self.json_list.addItem(QListWidgetItem(text))
            elif isinstance(data, list):
                for item in data:
                    self.json_list.addItem(QListWidgetItem(str(item)))
            else:
                self.json_list.addItem(QListWidgetItem(str(data)))
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur de chargement JSON : {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(1200, 768)
    win.show()
    sys.exit(app.exec())