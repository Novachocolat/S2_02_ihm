# ==============================================================
# Vue pour la fenêtre de connexion
# Développé par D. MELOCCO, L. PACE--BOULNOIS
# Dernière modification : 13/06/2025
# ==============================================================

import random

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QMessageBox, QPushButton,
    QVBoxLayout, QWidget
)

from market_tracer.constants import ROLE_ADMIN, ROLES
from market_tracer.paths import banner_path
from market_tracer.ui_helpers import app_icon

ROLE_BUTTON_STYLE = """
    QPushButton {
        background: #4be39a;
        color: #222;
        border-radius: 6px;
        min-width: 100px;
        min-height: 36px;
        font-size: 16px;
    }
    QPushButton:checked {
        border: 2px solid #222;
        background: #111;
        color: #fff;
    }
"""

INPUT_STYLE = "background: #bdbdbd; border-radius: 4px; padding: 6px; color: #222;"

ACTION_BUTTON_STYLE = """
    QPushButton {
        background: #bdbdbd;
        color: #222;
        border-radius: 4px;
        min-height: 36px;
        font-size: 18px;
    }
    QPushButton:pressed {
        background: #888;
    }
"""

BANNER_COUNT = 5


class LoginView(QWidget):
    """Vue pour la fenêtre de connexion"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Market Tracer - Connexion")
        self.setWindowIcon(app_icon())
        self.setFixedSize(800, 600)
        self.selected_role = ROLE_ADMIN
        self.rand_banner = random.randrange(1, BANNER_COUNT + 1)
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface utilisateur de la fenêtre de connexion."""

        # Configuration de la fenêtre principale
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        left_frame = self._build_login_form()
        right_frame = self._build_banner()
        if right_frame is None:  # Bannière introuvable : le message d'erreur est déjà affiché
            return

        # Ajout des cadres gauche et droit au layout principal
        main_layout.addWidget(left_frame, stretch=3)
        main_layout.addWidget(right_frame, stretch=2)

    def _build_login_form(self):
        """Cadre gauche : formulaire de connexion."""
        left_frame = QFrame()
        left_layout = QVBoxLayout(left_frame)
        left_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Création du titre
        title = QLabel("Connexion")
        title.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title.setStyleSheet("margin-top: 40px; margin-bottom: 20px;")
        left_layout.addWidget(title, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Création des boutons de rôle
        role_layout = QHBoxLayout()
        self.role_buttons = {}
        for role in ROLES:
            btn = QPushButton(role)
            btn.setCheckable(True)
            btn.setMaximumWidth(110)
            btn.setStyleSheet(ROLE_BUTTON_STYLE)
            self.role_buttons[role] = btn
            role_layout.addWidget(btn)
        self.role_buttons[ROLE_ADMIN].setChecked(True)
        left_layout.addLayout(role_layout, stretch=0)
        left_layout.setAlignment(role_layout, Qt.AlignmentFlag.AlignHCenter)
        left_layout.addSpacing(20)

        # Formulaire de connexion
        form_layout = QGridLayout()
        form_layout.setVerticalSpacing(15)

        # Création des champs de saisie
        self.user_label = QLabel("Nom d'utilisateur")
        self.user_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.user_input = QLineEdit()
        self.user_input.setMaximumWidth(310)
        self.user_input.setPlaceholderText("Entrez votre nom d'utilisateur")
        self.user_input.setStyleSheet(INPUT_STYLE)
        self.pass_label = QLabel("Mot de passe")
        self.pass_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.pass_input = QLineEdit()
        self.pass_input.setMaximumWidth(310)
        self.pass_input.setPlaceholderText("Entrez votre mot-de-passe")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet(INPUT_STYLE)
        form_layout.addWidget(self.user_label, 0, 0)
        form_layout.addWidget(self.user_input, 1, 0)
        form_layout.addWidget(self.pass_label, 2, 0)
        form_layout.addWidget(self.pass_input, 3, 0)
        left_layout.addLayout(form_layout)
        left_layout.addSpacing(20)

        # Bouton de connexion
        self.login_btn = QPushButton("Se connecter")
        self.login_btn.setStyleSheet(ACTION_BUTTON_STYLE)
        left_layout.addWidget(self.login_btn)

        # Bouton pour ouvrir une session
        self.enter_btn = QPushButton("Ouvrir une session")
        self.enter_btn.setStyleSheet(ACTION_BUTTON_STYLE)
        self.enter_btn.hide()
        left_layout.addWidget(self.enter_btn)
        left_layout.addSpacing(40)

        # Message d'erreur
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        left_layout.addWidget(self.error_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Footer
        footer = QLabel("Powered by Place Holder")
        footer.setStyleSheet("color: #888; font-size: 12px; margin-top: 40px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(footer)
        return left_frame

    def _build_banner(self):
        """Cadre droit : bannière choisie aléatoirement (None si l'image est introuvable)."""
        right_frame = QFrame()
        right_frame.setMinimumWidth(300)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Chargement de l'image de la bannière
        img_label = QLabel()
        pixmap = QPixmap(str(banner_path(self.rand_banner)))

        # Vérification si l'image a été chargée correctement
        if pixmap.isNull():
            QMessageBox.critical(self, "Erreur", "L'image de la bannière n'a pas pu être chargée.")
            return None

        # Redimensionnement de l'image
        pixmap = pixmap.scaled(300, 580)
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(img_label)
        return right_frame
