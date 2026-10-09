# ==============================================================
# Petits composants d'interface réutilisés par les vues et fenêtres
# ==============================================================

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtWidgets import QFrame, QGroupBox, QLabel, QMessageBox, QPushButton, QSlider, QVBoxLayout

from market_tracer.paths import APP_ICON, LOGO_EXT

LOGOUT_BUTTON_STYLE = (
    "background: #ff3c2f; color: #fff; font-weight: bold; padding: 4px 16px; border-radius: 6px;"
)


def app_icon() -> QIcon:
    """Icône des fenêtres de l'application."""
    return QIcon(str(APP_ICON))


def logo_label(width: int = 400, height: int = 100) -> QLabel:
    """Étiquette contenant le logo de l'application, centré et redimensionné."""
    logo = QLabel()
    pixmap = QPixmap(str(LOGO_EXT))
    pixmap = pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    logo.setPixmap(pixmap)
    logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
    return logo


def bold_label(text: str, point_size: int) -> QLabel:
    """Étiquette en gras (Arial)."""
    label = QLabel(text)
    label.setFont(QFont("Arial", point_size, QFont.Weight.Bold))
    return label


def separator(shape: QFrame.Shape) -> QFrame:
    """Ligne de séparation (QFrame.Shape.HLine ou QFrame.Shape.VLine)."""
    line = QFrame()
    line.setFrameShape(shape)
    line.setFrameShadow(QFrame.Shadow.Sunken)
    line.setLineWidth(1)
    line.setMidLineWidth(0)
    return line


def command_button(text: str, layout) -> QPushButton:
    """Bouton de commande standard ajouté à `layout`."""
    button = QPushButton(text)
    button.setMinimumHeight(25)
    layout.addWidget(button)
    return button


def logout_button() -> QPushButton:
    """Bouton rouge de déconnexion."""
    button = QPushButton("Déconnexion")
    button.setStyleSheet(LOGOUT_BUTTON_STYLE)
    return button


def horizontal_slider(minimum: int, maximum: int, value: int) -> QSlider:
    """Curseur horizontal borné."""
    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setMinimum(minimum)
    slider.setMaximum(maximum)
    slider.setValue(value)
    return slider


def list_entry(entry_id: int, label: str) -> str:
    """Texte d'une ligne de liste « id - libellé »."""
    return f"{entry_id} - {label}"


def list_entry_id(text: str) -> int:
    """Extrait l'identifiant d'une ligne de liste créée par `list_entry`."""
    return int(text.split(" - ")[0])


def wrap_in_side_frame(layout) -> QFrame:
    """Place `layout` dans un cadre de largeur bornée (colonnes gauche et droite des vues)."""
    frame = QFrame()
    frame.setLayout(layout)
    frame.setMinimumWidth(240)
    frame.setMaximumWidth(320)
    return frame


def zoom_group_box(grid_overlay, with_grid_size: bool):
    """Groupe « Zoom » relié à `grid_overlay`.

    Returns:
        tuple: (groupe, curseur de taille de grille ou None, curseur de zoom).
    """
    zoom_box = QGroupBox("Zoom")
    zoom_box.setMinimumWidth(220)
    zoom_layout = QVBoxLayout()
    zoom_layout.setContentsMargins(10, 10, 10, 10)

    slider_grid = None
    if with_grid_size:
        label_grid_size = QLabel("Grille :\nAjuste la taille des cases sur le quadrillage")
        label_grid_size.setWordWrap(True)
        zoom_layout.addWidget(label_grid_size)
        slider_grid = horizontal_slider(25, 100, 50)
        zoom_layout.addWidget(slider_grid)

    label_zoom = QLabel("Zoom :\nAgrandit ou réduit le plan")
    label_zoom.setWordWrap(True)
    zoom_layout.addWidget(label_zoom)
    slider_zoom = horizontal_slider(10, 300, 50)
    grid_overlay.set_zoom(slider_zoom.value() / 100.0)
    zoom_layout.addWidget(slider_zoom)

    zoom_box.setLayout(zoom_layout)
    return zoom_box, slider_grid, slider_zoom


def ask_yes_no(parent, title: str, text: str) -> bool:
    """Affiche une boîte de confirmation Oui / Non et retourne True si l'utilisateur répond Oui."""
    reply = QMessageBox.question(
        parent, title, text,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    )
    return reply == QMessageBox.StandardButton.Yes
