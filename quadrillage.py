# ==============================================================
# Market Tracer - Quadrillage
# ==============================================================
# Importations
import sys, json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout,
    QWidget, QSlider, QPushButton, QHBoxLayout, QGroupBox,
    QMessageBox, QListWidget, QListWidgetItem
)
from PyQt6.QtGui import QDrag, QPixmap, QFont, QBrush, QPen, QFont, QColor
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

        # Couleurs des obstacles du plan :
        self.color_types = {
            'Rayon': QColor(0, 0, 255, 120),
            'Caisse': QColor(255, 255, 0, 120),
            'Entrée': QColor(255, 0, 0, 120),
            'Mur': QColor(128, 128, 128, 120),
        }

        # Ajout de tous les rayons principaux du JSON :
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

    # Charger le plan :
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

    # Dessiner les cellules :
    def draw_grid(self):
        if not self.image_item:
            return

        for item in self.scene.items():
            if isinstance(item, QGraphicsPixmapItem):
                continue
            self.scene.removeItem(item)

        rect = self.image_item.boundingRect()

        for (row, col), color in self.colored_cells.items():
            x = col * self.grid_size
            y = row * self.grid_size
            cell_rect = QRectF(x, y, self.grid_size, self.grid_size)
            self.scene.addRect(cell_rect, QPen(Qt.PenStyle.NoPen), QBrush(color))

            if (row, col) in self.objects_in_cells:
                obj = self.objects_in_cells[(row, col)]
                emoji = self.emoji_mapping.get(obj, "❌")
                text_item = self.scene.addText(emoji)
                font = QFont()
                font.setPointSize(int(self.grid_size * 0.6))
                text_item.setFont(font)
                text_item.setPos(x + self.grid_size * 0.1, y + self.grid_size * 0.1)

        pen = QPen(Qt.GlobalColor.red) # Changer la couleur
        pen.setWidth(2) # Changer la taille

        x = 0
        while x <= rect.width():
            self.scene.addLine(x, 0, x, rect.height(), pen)
            x += self.grid_size

        y = 0
        while y <= rect.height():
            self.scene.addLine(0, y, rect.width(), y, pen)
            y += self.grid_size

    def set_grid_size(self, size):
        self.grid_size = size
        self.draw_grid()

    def set_current_color(self, color_type):
        self.current_color_type = color_type

    def color_cell_at_position(self, scene_pos):
        x = scene_pos.x()
        y = scene_pos.y()

        col = int(x // self.grid_size)
        row = int(y // self.grid_size)
        cell_key = (row, col)
        
        # Limiter à une seule entrée
        # TODO : À corriger
        if self.current_color_type == 'Entrée':
            if self.entrance_number >= 1:
                QMessageBox.warning(self, "Erreur", "Il ne peut y avoir qu'une seule entrée.")
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

    # Réinitialiser le quadrillage :
    def reset_colored_cells(self):
        self.colored_cells.clear()
        self.objects_in_cells.clear()
        self.draw_grid()

    # Drag & Drop :
    def mousePressEvent(self, event):
        if not self.image_item:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_painting = True
            scene_pos = self.mapToScene(event.pos())
            self.color_cell_at_position(scene_pos)

    def mouseMoveEvent(self, event):
        if self.is_painting:
            scene_pos = self.mapToScene(event.pos())
            self.color_cell_at_position(scene_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_painting = False

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        if not self.image_item:
            return

        data = event.mimeData().text()
        # On récupère le nom du rayon (clé du mapping) et non un sous-produit (pour l'instant)
        # Si le drag contient un objet JSON, on prend la clé principale
        try:
            obj = json.loads(data)
            if isinstance(obj, dict) and "name" in obj:
                obj_name = obj["name"]
            elif isinstance(obj, str):
                obj_name = obj
            else:
                obj_name = str(obj)
        except Exception:
            obj_name = data.strip().replace('"', '').replace("'", "").strip()

        # Si le nom n'est pas dans le mapping, on essaie de le "nettoyer"
        # (ex: si on droppe "Légumes" ou '{"name": "Légumes"}')
        if obj_name not in self.emoji_mapping:
            # On tente de récupérer le rayon à partir d'un sous-produit
            # (ex: "🥦 Brocolis" => "Légumes")
            for rayon in self.emoji_mapping:
                if rayon in obj_name:
                    obj_name = rayon
                    break
            else:
                obj_name = "Autre"

        scene_pos = self.mapToScene(event.position().toPoint())
        col = int(scene_pos.x() // self.grid_size)
        row = int(scene_pos.y() // self.grid_size)
        cell_key = (row, col)

        if self.colored_cells.get(cell_key) == self.color_types["Rayon"]:
            self.objects_in_cells[cell_key] = obj_name
            self.draw_grid()
        else:
            QMessageBox.warning(self, "Attention", "Vous ne pouvez déposer que sur des Rayons (bleus).")

    def export_cells_to_json(self, path):
        data = []
        for (row, col), color in self.colored_cells.items():
            # Trouver le type de la cellule
            for type_str, type_color in self.color_types.items():
                if color == type_color:
                    cell_data = {
                        "row": row,
                        "col": col,
                        "type": type_str
                    }
                    # Si c'est un rayon, on ajoute l'objet (ou "NULL")
                    if type_str == "Rayon":
                        obj = self.objects_in_cells.get((row, col), None)
                        cell_data["object"] = obj if obj is not None else "NULL"
                    data.append(cell_data)
                    break

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def import_cells_from_json(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.colored_cells.clear()
            self.objects_in_cells.clear()
            self.entrance_number = 0
            for cell in data:
                row = cell.get("row")
                col = cell.get("col")
                type_str = cell.get("type")
                obj = cell.get("object")
                if type_str in self.color_types:
                    self.colored_cells[(row, col)] = self.color_types[type_str]
                    if obj:
                        self.objects_in_cells[(row, col)] = obj
                    if type_str == "Entrée":
                        self.entrance_number = 1
            self.draw_grid()
        except Exception as e:
            print(f"Erreur lors de l'importation : {e}")

# Récupérer le texte brut :
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

# Vue temporaire :
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
        for label, color in [
            ("Rayon", 'Rayon'), ("Caisse", 'Caisse'),
            ("Entrée", 'Entrée'), ("Mur", 'Mur'), ("Gomme", 'Gomme')]:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, c=color: self.grid_view.set_current_color(c))
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

        # Slider tout à droite
        self.slider = QSlider(Qt.Orientation.Vertical)
        self.slider.setMinimum(25)
        self.slider.setMaximum(100)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.grid_view.set_grid_size)
        main_layout.addWidget(self.slider)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "", "Images (*.png *.jpg *.bmp *.jpeg)")
        if file_name:
            self.grid_view.load_image(file_name)

    def confirm_reset(self):
        reply = QMessageBox.question(self, "Confirmation",
            "Êtes-vous sûr de vouloir tout réinitialiser ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.grid_view.reset_colored_cells()

    def export_cells(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Exporter en JSON", "", "JSON (*.json)")
        if file_name:
            self.grid_view.export_cells_to_json(file_name)
            QMessageBox.information(self, "Export", "Exportation réussie !")

    def import_cells(self):
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
            if isinstance(data, list):
                for item in data:
                    text = item if isinstance(item, str) else json.dumps(item)
                    self.json_list.addItem(QListWidgetItem(text))
            elif isinstance(data, dict):
                for key in data:
                    self.json_list.addItem(QListWidgetItem(str(key)))
            else:
                self.json_list.addItem(QListWidgetItem(str(data)))
        except Exception as e:
            QMessageBox.warning(self, "Erreur", f"Erreur de chargement JSON : {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(1000, 600)
    win.show()
    sys.exit(app.exec())
