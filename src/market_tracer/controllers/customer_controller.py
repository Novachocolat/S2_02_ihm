# ==============================================================
# Contrôleur pour la fenêtre du client
# Développé par D. MELOCCO
# Dernière modification : 13/06/2025
# ==============================================================

import json
import os

from PyQt6.QtWidgets import QFileDialog, QMessageBox

from market_tracer.constants import CELL_SHELF, CELL_STOCK, ROLE_CUSTOMER, ROLE_EMPLOYEE
from market_tracer.models.admin_model import get_shop_data
from market_tracer.models.customer_model import (
    charger_produits_json, exporter_liste_json, importer_liste_json
)
from market_tracer.paths import DEFAULT_PRODUCTS_JSON
from market_tracer.views.customer_view import CustomerView
from market_tracer.windows.about_window import AboutWindow
from market_tracer.windows.help_window import HelpWindow
from market_tracer.windows.licence_window import LicenceWindow

LIST_FILTER = "JSON (*.json)"


class CustomerController:
    """Contrôleur pour la fenêtre du client (et de l'employé)"""
    def __init__(self, shop_id, role=ROLE_CUSTOMER, articles_json_path=DEFAULT_PRODUCTS_JSON):
        """Initialise le contrôleur du client.

        Args:
            shop_id (int): identifiant du magasin affiché.
            role (str): rôle de l'utilisateur (client ou employé).
            articles_json_path (str): liste de produits proposés. TODO: la rendre personnalisable par magasin.
        """
        self.view = CustomerView()
        self.liste_courses = []
        self.articles_json_path = articles_json_path
        self.shop_id = shop_id
        self.role = role
        self.view.setWindowTitle(f"Market Tracer - {self.role}")

        self._connect_signals()

        # Chargements initiaux
        self.charger_produits()
        self.charger_plan()

    def _connect_signals(self):
        """Relie les widgets et les actions de menu de la vue aux méthodes du contrôleur."""
        view = self.view

        view.btn_ajouter.clicked.connect(self.ajouter_article)
        view.btn_retirer.clicked.connect(self.retirer_article)
        view.btn_vider_liste.clicked.connect(self.vider_liste)
        view.btn_exporter.clicked.connect(self.exporter_liste)
        view.btn_importer.clicked.connect(self.importer_liste)
        view.filtre_combo.currentTextChanged.connect(view.filtrer_produits)
        view.search_input.textChanged.connect(view.rechercher_produits)
        view.btn_generer.clicked.connect(self.generer_parcours)
        view.btn_deconnexion.clicked.connect(self.deconnexion)
        view.slider_zoom.valueChanged.connect(lambda v: view.grid_overlay.set_zoom(v / 100.0))

        # Menus
        view.action_exporter.triggered.connect(self.exporter_liste)
        view.action_importer.triggered.connect(self.importer_liste)
        view.action_about.triggered.connect(self.open_about)
        view.action_doc.triggered.connect(self.open_help)
        view.action_licence.triggered.connect(self.open_licence)

    def charger_produits(self):
        """Charge les produits depuis le fichier JSON et les affiche dans la vue."""
        produits = charger_produits_json(self.articles_json_path)
        self.view.afficher_produits_depuis_json(json.dumps(produits))

    def charger_plan(self):
        """Charge le plan du magasin et l'affiche dans la vue."""
        # NOTE : `get_shop_data` cherche le magasin par identifiant d'utilisateur ;
        # le comportement historique (identifiant du magasin passé en paramètre) est conservé.
        shop_data = get_shop_data(self.shop_id)

        # Récupère le chemin du plan du magasin
        plan_path = shop_data[2] if shop_data and len(shop_data) > 2 else ""
        if plan_path:
            self.view.grid_overlay.load_image(plan_path)

    def ajouter_article(self):
        """Ajoute l'article sélectionné à la liste de courses."""
        item = self.view.stocks_list.currentItem()

        # Vérifie si l'article est sélectionné et s'il n'est pas déjà dans la liste
        if item and item.text() not in self.liste_courses:
            self.liste_courses.append(item.text())
            self.view.courses_list.addItem(item.text())
            self.view.status_bar.setText(f"Ajouté : {item.text()}")

    def retirer_article(self):
        """Retire l'article sélectionné de la liste de courses."""
        item = self.view.courses_list.currentItem()

        # Vérifie si l'article est sélectionné dans la liste de courses
        if item:
            self.liste_courses.remove(item.text())
            self.view.courses_list.takeItem(self.view.courses_list.row(item))
            self.view.status_bar.setText(f"Retiré : {item.text()}")

    def vider_liste(self):
        """Vide la liste de courses."""
        self.liste_courses.clear()
        self.view.courses_list.clear()
        self.view.status_bar.setText("Liste vidée.")

    def exporter_liste(self):
        """Exporte la liste de courses au format JSON."""
        file_name, _ = QFileDialog.getSaveFileName(self.view, "Exporter la liste", "", LIST_FILTER)
        if file_name:
            exporter_liste_json(self.liste_courses, file_name)
            self.view.status_bar.setText("Liste exportée.")

    def importer_liste(self):
        """Importe une liste de courses depuis un fichier JSON."""
        file_name, _ = QFileDialog.getOpenFileName(self.view, "Importer une liste", "", LIST_FILTER)
        if file_name:
            self.liste_courses = importer_liste_json(file_name)
            self.view.courses_list.clear()
            for article in self.liste_courses:
                self.view.courses_list.addItem(article)
            self.view.status_bar.setText("Liste importée.")

    def generer_parcours(self):
        """Génère le parcours optimisé pour la liste de courses."""
        if not self.liste_courses:
            QMessageBox.warning(self.view, "Avertissement", "La liste de courses est vide.")
            return

        # Import différé : l'algorithme dépend de numpy et matplotlib, inutiles tant
        # qu'aucun parcours n'est demandé.
        from market_tracer.core import algorithm

        # Récupère le chemin du plan du magasin depuis la base de données
        shop_data = get_shop_data(self.shop_id)
        plan_path = shop_data[1] if shop_data and len(shop_data) > 2 else ""
        if not plan_path or not os.path.exists(plan_path):
            QMessageBox.warning(self.view, "Erreur", "Plan du magasin introuvable.")
            return

        # Charge le plan et la liste de courses.
        # Les cellules sont lues en latin-1 (comportement historique), la grille en UTF-8.
        cells = algorithm.load_cells(plan_path, encoding="latin-1")
        grid, entry, caisses = algorithm.load_grid_from_json(plan_path)

        # Vérifie si l'utilisateur a le droit d'accéder aux stocks ou seulement aux rayons
        if self.role == ROLE_EMPLOYEE:
            allowed_types = (CELL_SHELF, CELL_STOCK)
        else:
            allowed_types = (CELL_SHELF,)

        # 1. Trouver les coordonnées des articles de la liste
        shopping_points = algorithm.find_shopping_points(cells, self.liste_courses, grid, allowed_types)
        if not shopping_points:
            QMessageBox.warning(self.view, "Erreur", "Aucun article de la liste trouvé dans le plan.")
            return

        # 2. Trouver l'ordre optimal (brute force si peu d'articles)
        ordered_points = algorithm.order_points(entry, shopping_points)

        # 3. Ajouter la caisse la plus proche à la fin
        last_point = ordered_points[-1] if ordered_points else entry
        nearest_accessible_caisse = algorithm.find_nearest_accessible_caisse(grid, last_point, caisses)
        if nearest_accessible_caisse is None:
            QMessageBox.warning(self.view, "Erreur", "Aucune caisse accessible trouvée.")
            return
        full_points = [entry] + ordered_points + [nearest_accessible_caisse]

        # 4. Calculer le chemin complet
        full_path = algorithm.find_full_path(grid, full_points)

        if full_path:
            total_distance = algorithm.calculate_total_distance(full_path)
            self.view.status_bar.setText(f"Parcours généré ({len(full_path)} étapes, {total_distance:.2f} m).")
            algorithm.visualize_path(grid, full_path, full_points, cells)
        else:
            QMessageBox.warning(self.view, "Erreur", "Aucun chemin trouvé pour cette liste.")

    def deconnexion(self):
        """Déconnecte l'utilisateur et ouvre la fenêtre de connexion."""
        # Import différé : le contrôleur de connexion importe celui-ci
        from market_tracer.controllers.login_controller import LoginController
        self.login_controller = LoginController()
        self.login_controller.view.show()
        self.view.close()

    def open_about(self):
        """Ouvre la fenêtre 'À propos'."""
        self.about_window = AboutWindow()
        self.about_window.show()

    def open_help(self):
        """Ouvre la fenêtre d'aide."""
        self.help_window = HelpWindow()
        self.help_window.show()

    def open_licence(self):
        """Ouvre la fenêtre de licence."""
        self.licence_window = LicenceWindow()
        self.licence_window.show()
