# ==============================================================
# Market Tracer - Quadrillage avec zoom synchrone
# ==============================================================
# Importations
import sys, json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout,
    QWidget, QSlider, QPushButton, QHBoxLayout, QGroupBox,
    QMessageBox, QListWidget, QListWidgetItem, QLabel, QToolTip
)
from PyQt6.QtGui import QDrag, QPixmap, QFont, QBrush, QPen, QColor
from PyQt6.QtCore import QMimeData, Qt, QRectF

# Image avec grille et cellules coloriées
class GridOverlay(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.image_item = None
        self.grid_size = 50
        self.entrance_number = 0

        self.colored_cells = {}
        self.objects_in_cells = {}
        self.setMouseTracking(True)

        # Zoom plan + grille
        self.zoom_factor = 1.0

        # Couleurs des éléments du plan 
        self.color_types = {
            'Rayon': QColor(0, 0, 255, 120),
            'Caisse': QColor(255, 255, 0, 120),
            'Entrée': QColor(255, 0, 0, 120),
            'Mur': QColor(128, 128, 128, 120),
        }

        # Ajout de tous les rayons principaux du JSON 
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

    # Charger le plan
    def load_image(self, path):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            print("Erreur de chargement d'image")
            return

        self.scene.clear()
        self.colored_cells.clear()
        self.objects_in_cells.clear()

        self.image_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.image_item)
        self.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.draw_grid()
        self.resetTransform()
        self.scale(self.zoom_factor, self.zoom_factor)

    # Dessiner les cellules
    def draw_grid(self):
        if not self.image_item:
            return

        for item in self.scene.items():
            if isinstance(item, QGraphicsPixmapItem):
                continue
            self.scene.removeItem(item)

        rect = self.image_item.boundingRect()

        # Dessiner les cases colorées
        for (row, col), color in self.colored_cells.items():
            x = col * self.grid_size
            y = row * self.grid_size
            cell_rect = QRectF(x, y, self.grid_size, self.grid_size)
            self.scene.addRect(cell_rect, QPen(Qt.PenStyle.NoPen), QBrush(color))

            if (row, col) in self.objects_in_cells:
                obj_data = self.objects_in_cells[(row, col)]
                category = obj_data["category"]
                emoji = self.emoji_mapping.get(category, "")
                text_item = self.scene.addText(emoji)
                font = QFont()
                font.setPointSize(int(self.grid_size * 0.6))
                text_item.setFont(font)
                text_item.setPos(x + self.grid_size * 0.1, y + self.grid_size * 0.1)

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

    # Définit la taille de la grille
    def set_grid_size(self, size):
        self.grid_size = size
        self.draw_grid()
        
    # Définit le mode de déplacement
    def set_pan_mode(self, enable):
        self.is_panning = enable
        if enable:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

    # Définit la couleur 
    def set_current_color(self, color_type):
        self.current_color_type = color_type

    # Colore une cellule à la position de la souris 
    def color_cell_at_position(self, scene_pos):
        x = scene_pos.x()
        y = scene_pos.y()

        col = int(x // self.grid_size)
        row = int(y // self.grid_size)
        cell_key = (row, col)
        
        # Limiter à une seule entrée
        if self.current_color_type == 'Entrée':
            if self.entrance_number >= 1:
                QMessageBox.warning(self, "Erreur", "Il ne peut y avoir qu'une seule entrée.")
                self.is_painting = False
                return
            self.entrance_number = 1

        if self.current_color_type == 'Gomme':
            if self.colored_cells.get(cell_key) == self.color_types['Entrée']:
                self.entrance_number = 0
            self.colored_cells.pop(cell_key, None)
            self.objects_in_cells.pop(cell_key, None)
        else:
            color = self.color_types[self.current_color_type]
            self.colored_cells[cell_key] = color

        self.draw_grid()

    # Réinitialiser le quadrillage
    def reset_colored_cells(self):
        self.colored_cells.clear()
        self.objects_in_cells.clear()
        self.draw_grid()

    # Drag & Drop
    def mousePressEvent(self, event):
        if not self.image_item:
            return

        if self.is_panning:
            if event.button() == Qt.MouseButton.LeftButton:
                self.setCursor(Qt.CursorShape.ClosedHandCursor)
                self.last_pan_point = event.pos()
        else:
            if event.button() == Qt.MouseButton.LeftButton:
                self.is_painting = True
                scene_pos = self.mapToScene(event.pos())
                self.color_cell_at_position(scene_pos)

    # Gère le mouvement de la souris
    def mouseMoveEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        col = int(scene_pos.x() // self.grid_size)
        row = int(scene_pos.y() // self.grid_size)
        cell_key = (row, col)

        # Afficher l'info de la case
        if self.is_panning and self.last_pan_point:
            delta = event.pos() - self.last_pan_point
            self.last_pan_point = event.pos()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
        elif self.is_painting:
            self.color_cell_at_position(scene_pos)
        else:
            if self.colored_cells.get(cell_key) == self.color_types['Rayon']:
                obj_data = self.objects_in_cells.get(cell_key)
                if obj_data:
                    product_name = obj_data["product"]
                    QToolTip.showText(event.globalPosition().toPoint(), f"Produit : {product_name}", self)
                else:
                    QToolTip.hideText()
            else:
                QToolTip.hideText()


    # Gère le relâchement de la souris
    def mouseReleaseEvent(self, event):
        if self.is_panning:
            self.setCursor(Qt.CursorShape.OpenHandCursor)
            self.last_pan_point = None
        elif event.button() == Qt.MouseButton.LeftButton:
            self.is_painting = False

    # Gère le drag 
    def dragEnterEvent(self, event):
        event.accept()

    # Gère le mouvement du drag
    def dragMoveEvent(self, event):
        event.accept()

    # Gère le drop d'un objet
    def dropEvent(self, event):
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

        if self.colored_cells.get(cell_key) == self.color_types["Rayon"]:
            self.objects_in_cells[cell_key] = {"category": category_name, "product": obj_name}
            self.draw_grid()
        else:
            QMessageBox.warning(self, "Attention", "Vous ne pouvez déposer que sur des Rayons (bleus).")


    # Exporte vers un fichier JSON
    def export_cells_to_json(self, path):
        data = {
            "grid_size": self.grid_size,
            "cells": []
        }
        
        # On ajoute les cases colorées et les objets
        for (row, col), color in self.colored_cells.items():
            for type_str, type_color in self.color_types.items():
                if color == type_color:
                    cell_data = {
                        "row": row,
                        "col": col,
                        "type": type_str
                    }
                    if type_str == "Rayon":
                        obj_data = self.objects_in_cells.get((row, col), None)
                        if obj_data:
                            # On sauvegarde à la fois la catégorie et le produit
                            cell_data["object"] = {
                                "category": obj_data["category"],
                                "product": obj_data["product"]
                            }
                        else:
                            cell_data["object"] = None
                    data["cells"].append(cell_data)
                    break

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


    # Importer les cases depuis un fichier JSON
    def import_cells_from_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.colored_cells.clear()
            self.objects_in_cells.clear()
            self.entrance_number = 0

            if isinstance(data, dict) and "grid_size" in data:
                self.grid_size = data["grid_size"]
                self.slider.setValue(self.grid_size)

            cells = data["cells"] if isinstance(data, dict) and "cells" in data else data

            #On restaure les cases colorées
            for cell in cells:
                row = cell.get("row")
                col = cell.get("col")
                type_str = cell.get("type")
                obj = cell.get("object")
                if type_str in self.color_types:
                    self.colored_cells[(row, col)] = self.color_types[type_str]
                    if obj:
                        # On restaure bien les deux champs : category et product
                        if isinstance(obj, dict):
                            self.objects_in_cells[(row, col)] = {
                                "category": obj.get("category", "Autre"),
                                "product": obj.get("product", "")
                            }
                        else:
                            # Ancienne version simple : rétrocompatibilité
                            self.objects_in_cells[(row, col)] = {
                                "category": "Autre",
                                "product": obj
                            }
                    if type_str == "Entrée":
                        self.entrance_number = 1
            self.draw_grid()
        except Exception as e:
            print(f"Erreur lors de l'importation : {e}")


    # Nouvelle méthode pour appliquer le zoom
    def set_zoom(self, factor):
        self.zoom_factor = factor
        self.resetTransform()
        self.scale(factor, factor)

# Récupérer le texte brut
class DraggableListWidget(QListWidget):
    def startDrag(self, supportedActions):
        item = self.currentItem()
        if not item:
            return
        drag = QDrag(self)
        mime = QMimeData()
        mime.setText(item.text())
        drag.setMimeData(mime)
        drag.exec(supportedActions)

# Vue principale 
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

        # Bloc boutons
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

        # Bloc outils couleurs
        color_buttons = QVBoxLayout()

        # Bouton Déplacer
        btn_main = QPushButton("Déplacer")
        btn_main.clicked.connect(lambda: self.set_main_mode())
        color_buttons.addWidget(btn_main)

        # Boutons pour les couleurs
        for label, color in [
            ("Rayon", 'Rayon'), ("Caisse", 'Caisse'),
            ("Entrée", 'Entrée'), ("Mur", 'Mur'), ("Gomme", 'Gomme')]:

            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, c=color: self.set_paint_mode(c))
            color_buttons.addWidget(btn)

        color_group = QGroupBox("Outils")
        color_group.setLayout(color_buttons)
        button_layout.addWidget(color_group)

        buttons_group = QGroupBox("Commandes")
        buttons_group.setLayout(button_layout)

        # Layout général horizontal
        main_layout = QHBoxLayout()
        main_layout.addWidget(json_group)
        main_layout.addWidget(buttons_group)
        main_layout.addWidget(self.grid_view)

        # Slider taille de la grille
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


        # Slider pour le zoom global
        zoom_layout = QVBoxLayout()

        self.zoom_slider = QSlider(Qt.Orientation.Vertical)
        self.zoom_slider.setMinimum(10)
        self.zoom_slider.setMaximum(300)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.on_zoom_changed)

        self.zoom_label = QLabel("100%")
        self.zoom_label.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        zoom_layout.addWidget(self.zoom_slider)
        zoom_layout.addWidget(self.zoom_label)

        zoom_group = QWidget()
        zoom_group.setLayout(zoom_layout)
        main_layout.addWidget(zoom_group)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)
        
    # Modes de la grille 
    def set_main_mode(self):
        self.grid_view.set_pan_mode(True)

    # Modes de peinture
    def set_paint_mode(self, color_type):
        self.grid_view.set_pan_mode(False)
        self.grid_view.set_current_color(color_type)
        
    # Gère le changement de taille de la grille
    def on_grid_size_changed(self, value):
        self.grid_view.set_grid_size(value)
        self.grid_label.setText(f"Grille: {value} px")

    # Gère le zoom
    def on_zoom_changed(self, value):
        factor = value / 100.0
        self.grid_view.set_zoom(factor)
        self.zoom_label.setText(f"{value}%")
    # Ouvrir une image
    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "", "Images (*.png *.jpg *.bmp *.jpeg)")
        if file_name:
            self.grid_view.load_image(file_name)
            self.zoom_slider.setValue(50)  # Ouvre à 50%

    #Confirme la réinitialisation
    def confirm_reset(self):
        reply = QMessageBox.question(self, "Confirmation",
            "Êtes-vous sûr de vouloir tout réinitialiser ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.grid_view.reset_colored_cells()

    # Exporter et importer les cases
    def export_cells(self):
        # Vérifie qu'une image de plan est chargée
        if self.grid_view.image_item is None:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord charger une image de plan avant d'exporter un JSON.")
            return

        file_name, _ = QFileDialog.getSaveFileName(self, "Exporter en JSON", "", "JSON (*.json)")
        if file_name:
            self.grid_view.export_cells_to_json(file_name)
            QMessageBox.information(self, "Export", "Exportation réussie !")

    # Importe les cases du JSON
    def import_cells(self):
        if self.grid_view.image_item is None:
            QMessageBox.warning(self, "Erreur", "Veuillez d'abord charger une image de plan avant d'importer un JSON.")
            return

        file_name, _ = QFileDialog.getOpenFileName(self, "Importer JSON", "", "JSON (*.json)")
        if file_name:
            self.grid_view.import_cells_from_json(file_name)
            QMessageBox.information(self, "Import", "Importation réussie !")

    # Charge une liste JSON d'objets
    def load_json_list(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Charger un JSON d'objets", "", "JSON (*.json)")
        if not file_name:
            return
        # Vérifie que le fichier existe
        try:
            with open(file_name, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.json_list.clear()
            if isinstance(data, dict):
                for category, items in data.items():
                    for item in items:
                        # On stocke la catégorie et le nom du produit dans le texte
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
    win.resize(1200, 700)
    win.show()
    sys.exit(app.exec())
