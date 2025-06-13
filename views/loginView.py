# ==============================================================
# Vue pour la fenêtre de connexion
# Développé par D. MELOCCO, L. PACE--BOULNOIS
# Dernière modification : 13/06/2025
# ==============================================================

from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QVBoxLayout, QGridLayout, QFrame, QMessageBox
)
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt
import random as rand

class LoginView(QWidget):
    """Vue pour la fenêtre de connexion"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Market Tracer - Connexion")
        self.setWindowIcon(QIcon("img/logo_v1.png"))
        self.setFixedSize(800, 600)
        self.selected_role = "Gérant"
        self.rand_banner = rand.randrange(1, 6)
        self.setup_ui()

    def setup_ui(self):
        """Configure l'interface utilisateur de la fenêtre de connexion."""

        # Configuration de la fenêtre principale
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Création du cadre gauche pour le formulaire de connexion
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
        for role in ["Gérant", "Employé", "Client"]:
            btn = QPushButton(role)
            btn.setCheckable(True)
            btn.setMaximumWidth(110)
            btn.setStyleSheet("""
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
            """)
            self.role_buttons[role] = btn
            role_layout.addWidget(btn)
        self.role_buttons["Gérant"].setChecked(True)
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
        self.user_input.setStyleSheet("background: #bdbdbd; border-radius: 4px; padding: 6px; color: #222;")
        self.pass_label = QLabel("Mot de passe")
        self.pass_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        self.pass_input = QLineEdit()
        self.pass_input.setMaximumWidth(310)
        self.pass_input.setPlaceholderText("Entrez votre mot-de-passe")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setStyleSheet("background: #bdbdbd; border-radius: 4px; padding: 6px; color: #222;")
        form_layout.addWidget(self.user_label, 0, 0)
        form_layout.addWidget(self.user_input, 1, 0)
        form_layout.addWidget(self.pass_label, 2, 0)
        form_layout.addWidget(self.pass_input, 3, 0)
        left_layout.addLayout(form_layout)
        left_layout.addSpacing(20)

        # Bouton de connexion
        self.login_btn = QPushButton("Se connecter")
        self.login_btn.setStyleSheet("""
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
        """)
        left_layout.addWidget(self.login_btn)

        # Bouton pour ouvrir une session
        self.enter_btn = QPushButton("Ouvrir une session")
        self.enter_btn.setStyleSheet("""
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
        """)
        self.enter_btn.hide()
        left_layout.addWidget(self.enter_btn)
        left_layout.addSpacing(40)

        # Message d'erreur
        self.error_label = QLabel("")
        self.error_label.setStyleSheet("color: red;")
        left_layout.addWidget(self.error_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        # Footer
        footer= QLabel("Powered by Place Holder")
        footer.setStyleSheet("color: #888; font-size: 12px; margin-top: 40px;")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(footer)

        # Création du cadre droit pour la bannière
        right_frame = QFrame()
        right_frame.setMinimumWidth(300)
        right_layout = QVBoxLayout(right_frame)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Chargement de l'image de la bannière
        img_label = QLabel()
        pixmap = QPixmap(f"img/mt_banner_{self.rand_banner}.png") # Choix aléatoire de la bannière

        # Vérification si l'image a été chargée correctement
        if pixmap.isNull():
            QMessageBox.critical(self, "Erreur", "L'image de la bannière n'a pas pu être chargée.")
            return

        # Redimensionnement de l'image
        pixmap = pixmap.scaled(300, 580)
        img_label.setPixmap(pixmap)
        img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(img_label)

        # Ajout des cadres gauche et droit au layout principal
        main_layout.addWidget(left_frame, stretch=3)
        main_layout.addWidget(right_frame, stretch=2)