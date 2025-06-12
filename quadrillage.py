# ==============================================================
# Market Tracer - Quadrillage
# ==============================================================
# Importations
import sys, json
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QGraphicsView,
    QGraphicsScene, QGraphicsPixmapItem, QVBoxLayout,
    QWidget, QSlider, QPushButton, QHBoxLayout, QGroupBox, QMessageBox
)
from PyQt6.QtGui import QPixmap, QPen, QColor, QBrush
from PyQt6.QtCore import Qt, QRectF

# Image avec grille et cellules coloriées
class GridOverlay(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.image_item = None
        self.grid_size = 50

        self.colored_cells = {}
        self.setMouseTracking(True)

        self.color_types = {
            'Rayon': QColor(0, 0, 255, 120),
            'Caisse': QColor(255, 255, 0, 120),
            'Entrée': QColor(255, 0, 0, 120),
        }

        self.current_color_type = 'Rayon'
        self.is_painting = False

# Charge l'image depuis le chemin donné
    def load_image(self, path):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            print("Erreur de chargement d'image")
            return

        self.scene.clear()
        self.colored_cells.clear()

        self.image_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(self.image_item)
        self.setSceneRect(QRectF(pixmap.rect()))
        self.fitInView(self.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        self.draw_grid()

# Dessine la grille sur l'image
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

        pen = QPen(Qt.GlobalColor.red)
        pen.setWidth(1)

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

# Définit la couleur
    def set_current_color(self, color_type):
        self.current_color_type = color_type

# Colorie la cellule à la position donnée
    def color_cell_at_position(self, scene_pos):
        x = scene_pos.x()
        y = scene_pos.y()

        col = int(x // self.grid_size)
        row = int(y // self.grid_size)
        cell_key = (row, col)

        if self.current_color_type == 'Gomme':
            if cell_key in self.colored_cells:
                del self.colored_cells[cell_key]
        else:
            color = self.color_types[self.current_color_type]
            self.colored_cells[cell_key] = color

        self.draw_grid()

# Gère le clic de la souris pour colorier les cellules
    def mousePressEvent(self, event):
        if not self.image_item:
            return

        if event.button() == Qt.MouseButton.LeftButton:
            self.is_painting = True
            scene_pos = self.mapToScene(event.pos())
            self.color_cell_at_position(scene_pos)

# Permet de colorier les cases en maintenant le clic
    def mouseMoveEvent(self, event):
        if self.is_painting:
            scene_pos = self.mapToScene(event.pos())
            self.color_cell_at_position(scene_pos)

# Gère le relâchement du clic de la souris
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_painting = False

# Réinitialise les case colorées
    def reset_colored_cells(self):
        self.colored_cells.clear()
        self.draw_grid()

    def export_cells_to_json(self, path):
            # On inverse le dictionnaire pour avoir le type sous forme de texte
            color_to_type = {v.name(): k for k, v in self.color_types.items()}
            data = []
            for (row, col), color in self.colored_cells.items():
                # On retrouve le type à partir de la couleur
                type_str = None
                for k, v in self.color_types.items():
                    if color == v:
                        type_str = k
                        break
                if not type_str:
                    type_str = "Inconnu"
                data.append({
                    "row": row,
                    "col": col,
                    "type": type_str
                })
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

    def import_cells_from_json(self, path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.colored_cells.clear()
                for cell in data:
                    row = cell.get("row")
                    col = cell.get("col")
                    type_str = cell.get("type")
                    if type_str in self.color_types:
                        self.colored_cells[(row, col)] = self.color_types[type_str]
                self.draw_grid()
            except Exception as e:
                print(f"Erreur lors de l'importation : {e}")

# Affichage de la fenêtre principale avec les boutons et la grille
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image avec grille et cellules coloriées")

        self.grid_view = GridOverlay()

        open_btn = QPushButton("Ouvrir une image")
        open_btn.clicked.connect(self.open_image)

        reset_btn = QPushButton("Réinitialiser")
        reset_btn.clicked.connect(self.confirm_reset)
        
        export_btn = QPushButton("Exporter en JSON")
        export_btn.clicked.connect(self.export_cells)

        import_btn = QPushButton("Importer JSON")
        import_btn.clicked.connect(self.import_cells)

        self.slider = QSlider(Qt.Orientation.Vertical)
        self.slider.setMinimum(10)
        self.slider.setMaximum(200)
        self.slider.setValue(50)
        self.slider.valueChanged.connect(self.grid_view.set_grid_size)

        color_buttons = QVBoxLayout()

        btn_rayon = QPushButton("Rayon (Bleu)")
        btn_rayon.clicked.connect(lambda: self.grid_view.set_current_color('Rayon'))
        color_buttons.addWidget(btn_rayon)

        btn_caisse = QPushButton("Caisse (Jaune)")
        btn_caisse.clicked.connect(lambda: self.grid_view.set_current_color('Caisse'))
        color_buttons.addWidget(btn_caisse)

        btn_entree = QPushButton("Entrée (Rouge)")
        btn_entree.clicked.connect(lambda: self.grid_view.set_current_color('Entrée'))
        color_buttons.addWidget(btn_entree)

        btn_gomme = QPushButton("Gomme")
        btn_gomme.clicked.connect(lambda: self.grid_view.set_current_color('Gomme'))
        color_buttons.addWidget(btn_gomme)

        color_group = QGroupBox("Outils")
        color_group.setLayout(color_buttons)

        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()
        left_layout.addWidget(open_btn)
        left_layout.addWidget(reset_btn)
        left_layout.addWidget(export_btn)
        left_layout.addWidget(import_btn)
        left_layout.addWidget(color_group)
        main_layout.addLayout(left_layout)

        main_layout.addWidget(self.grid_view)
        main_layout.addWidget(self.slider)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

# Ouvre une image depuis les fichiers
    def open_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Choisir une image", "", "Images (*.png *.jpg *.bmp *.jpeg)")
        if file_name:
            self.grid_view.load_image(file_name)

# Valide la rénitialisation
    def confirm_reset(self):
        reply = QMessageBox.question(
            self, "Confirmation",
            "Êtes-vous sûr de vouloir réinitialiser toutes les cases colorées ?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.grid_view.reset_colored_cells()

    def export_cells(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Exporter les cellules en JSON", "", "JSON (*.json)")
        if file_name:
            self.grid_view.export_cells_to_json(file_name)
            QMessageBox.information(self, "Export", "Exportation réussie !")

    def import_cells(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Importer les cellules depuis un JSON", "", "JSON (*.json)")
        if file_name:
            self.grid_view.import_cells_from_json(file_name)
            QMessageBox.information(self, "Import", "Importation réussie !")

# Window
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(1200, 800)
    win.show()
    sys.exit(app.exec())
