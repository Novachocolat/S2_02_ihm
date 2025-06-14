# ==============================================================
# Contrôleur pour la fenêtre du client
# Développé par D. MELOCCO
# Dernière modification : 13/06/2025
# ==============================================================

from PyQt6.QtWidgets import QFileDialog, QMessageBox
from models.customerModel import (
    charger_produits_json, exporter_liste_json, importer_liste_json
)
from views.customerView import CustomerView

class CustomerController:
    """Contrôleur pour la fenêtre du client"""
    def __init__(self, articles_json_path, shop_id, role="Client"):
        """Initialise le contrôleur du client."""
        self.view = CustomerView()
        self.liste_courses = []
        self.articles_json_path = "json/liste_produits.json" # TODO: Choisir un chemin vers une liste de produits personnalisée.
        self.shop_id = shop_id
        self.role = role
        self.view.setWindowTitle(f"Market Tracer - {self.role}")

        # Connexion des signaux
        self.view.btn_ajouter.clicked.connect(self.ajouter_article)
        self.view.btn_retirer.clicked.connect(self.retirer_article)
        self.view.btn_vider_liste.clicked.connect(self.vider_liste)
        self.view.btn_exporter.clicked.connect(self.exporter_liste)
        self.view.btn_importer.clicked.connect(self.importer_liste)
        self.view.filtre_combo.currentTextChanged.connect(self.view.filtrer_produits)
        self.view.search_input.textChanged.connect(self.view.rechercher_produits)
        self.view.btn_generer.clicked.connect(self.generer_parcours)
        self.view.btn_deconnexion.clicked.connect(self.deconnexion)
        self.view.menubar.actions()[0].menu().actions()[0].triggered.connect(self.exporter_liste)
        self.view.menubar.actions()[0].menu().actions()[1].triggered.connect(self.importer_liste)
        self.view.menubar.actions()[1].menu().actions()[0].triggered.connect(self.open_about)
        self.view.menubar.actions()[1].menu().actions()[1].triggered.connect(self.open_help)
        self.view.menubar.actions()[1].menu().actions()[2].triggered.connect(self.open_licence)
        self.view.slider_zoom.valueChanged.connect(lambda v: self.view.grid_overlay.set_zoom(v / 100.0))

        # Chargements initiaux
        self.charger_produits()
        self.charger_plan()

    def charger_produits(self):
        """Charge les produits depuis le fichier JSON et les affiche dans la vue."""
        import json
        produits = charger_produits_json(self.articles_json_path)
        self.view.afficher_produits_depuis_json(json.dumps(produits))

    def charger_plan(self):
        """Charge le plan du magasin et l'affiche dans la vue."""
        from models.adminModel import get_shop_data
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
        file_name, _ = QFileDialog.getSaveFileName(self.view, "Exporter la liste", "", "JSON (*.json)")
        if file_name:
            exporter_liste_json(self.liste_courses, file_name)
            self.view.status_bar.setText("Liste exportée.")

    def importer_liste(self):
        """Importe une liste de courses depuis un fichier JSON."""
        file_name, _ = QFileDialog.getOpenFileName(self.view, "Importer une liste", "", "JSON (*.json)")
        if file_name:
            self.liste_courses = importer_liste_json(file_name)
            self.view.courses_list.clear()
            for article in self.liste_courses:
                self.view.courses_list.addItem(article)
            self.view.status_bar.setText("Liste importée.")

    def generer_parcours(self):
        """Génère le parcours optimisé pour la liste de courses."""
        import os
        import sys
        import importlib.util

        if not self.liste_courses:
            QMessageBox.warning(self.view, "Avertissement", "La liste de courses est vide.")
            return

        # Import dynamique de l'algorithme pour éviter les problèmes de dépendances
        algo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'algorithm.py'))
        spec = importlib.util.spec_from_file_location("algorithm", algo_path)
        algorithm = importlib.util.module_from_spec(spec)
        sys.modules["algorithm"] = algorithm
        spec.loader.exec_module(algorithm)

        # Récupère le chemin du plan du magasin depuis la base de données
        from models.adminModel import get_shop_data
        shop_data = get_shop_data(self.shop_id)
        plan_path = shop_data[1] if shop_data and len(shop_data) > 2 else ""
        if not plan_path or not os.path.exists(plan_path):
            QMessageBox.warning(self.view, "Erreur", "Plan du magasin introuvable.")
            return

        # Charge le plan et la liste de courses
        with open(plan_path, "r", encoding="latin-1") as f:
            data = algorithm.json.load(f)
        cells = data["cells"]
        grid, entry, caisses = algorithm.load_grid_from_json(plan_path)

        # Vérifie si l'utilisateur a le droit d'accéder aux stocks ou seulement aux rayons
        if self.role == "Employé":
            allowed_types = ("Rayon", "Stock")
        else:
            allowed_types = ("Rayon",)

        # 1. Trouver les coordonnées des articles de la liste
        shopping_points = algorithm.find_shopping_points(cells, self.liste_courses, grid, allowed_types)
        if not shopping_points:
            QMessageBox.warning(self.view, "Erreur", "Aucun article de la liste trouvé dans le plan.")
            return

        # 2. Trouver l'ordre optimal (brute force si peu d'articles)
        if len(shopping_points) <= 5:
            ordered_points = algorithm.brute_force(entry, shopping_points)[1:]  # sans le départ
        else:
            ordered_points = []
            current = entry
            remaining = shopping_points.copy()
            while remaining:
                next_point = min(remaining, key=lambda p: algorithm.calculate_heuristic(current, p))
                ordered_points.append(next_point)
                remaining.remove(next_point)
                current = next_point

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
        from controllers.loginController import LoginController
        self.login_controller = LoginController()
        self.login_controller.view.show()
        self.view.close()

    def open_about(self):
        """Ouvre la fenêtre 'À propos'."""
        from aboutWindow import AboutWindow
        self.about_window = AboutWindow()
        self.about_window.show()

    def open_help(self):
        """Ouvre la fenêtre d'aide."""
        from helpWindow import HelpWindow
        self.help_window = HelpWindow()
        self.help_window.show()

    def open_licence(self):
        """Ouvre la fenêtre de licence."""
        from licenceWindow import LicenceWindow
        self.licence_window = LicenceWindow()
        self.licence_window.show()