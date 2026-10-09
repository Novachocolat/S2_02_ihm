# ==============================================================
# Fenêtre de démonstration du quadrillage (hors application)
# Lancement : python -m market_tracer.widgets.grid_demo
# Développé par David Melocco et Simon Leclercq-Speter
# ==============================================================

import json
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QFileDialog, QGroupBox, QHBoxLayout, QLabel, QListWidgetItem,
    QMainWindow, QMessageBox, QPushButton, QSlider, QVBoxLayout, QWidget
)

from market_tracer.constants import (
    CELL_CHECKOUT, CELL_ENTRANCE, CELL_SHELF, CELL_STOCK, CELL_WALL, TOOL_ERASER
)
from market_tracer.widgets.draggable_list import DraggableListWidget
from market_tracer.widgets.grid_overlay import GridOverlay


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
            ("Rayon", CELL_SHELF), ("Caisse", CELL_CHECKOUT),
            ("Entrée", CELL_ENTRANCE), ("Mur", CELL_WALL), ("Stock", CELL_STOCK), ("Gomme", TOOL_ERASER)]:
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
