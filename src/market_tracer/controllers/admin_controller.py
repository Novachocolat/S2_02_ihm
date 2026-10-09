# ==============================================================
# Contrôleur pour la fenêtre d'administration du gérant
# Développé par D. MELOCCO, L. PACE--BOULNOIS, S. LECLERCQ-SPETER, N. COLIN
# Dernière modification : 13/06/2025
# ==============================================================

import io
import json
import os

from PyQt6.QtWidgets import QFileDialog, QMessageBox

from market_tracer.constants import (
    CELL_CHECKOUT, CELL_ENTRANCE, CELL_SHELF, CELL_STOCK, TOOL_ERASER
)
from market_tracer.dialogs.add_article_dialog import AddArticleDialog
from market_tracer.dialogs.configure_window import ConfigureWindow
from market_tracer.dialogs.employe_manager_dialog import EmployeManagerDialog
from market_tracer.dialogs.shop_manager_dialog import ShopManagerDialog
from market_tracer.models.admin_model import (
    get_employees_shop_id, get_shop_articles_by_id, get_shop_data,
    update_articles_json, update_shop_image
)
from market_tracer.ui_helpers import ask_yes_no
from market_tracer.views.admin_view import AdminView
from market_tracer.windows.about_window import AboutWindow
from market_tracer.windows.help_window import HelpWindow
from market_tracer.windows.licence_window import LicenceWindow

IMAGE_FILTER = "Images (*.png *.jpg *.bmp *.jpeg)"
JSON_FILTER = "JSON (*.json)"

# Outils de dessin du plan (boutons de la colonne de droite)
PLAN_TOOLS = (CELL_SHELF, CELL_STOCK, CELL_CHECKOUT, CELL_ENTRANCE, TOOL_ERASER)


def _read_json_file(path):
    """Retourne le contenu du fichier `path` s'il s'agit d'un fichier .json existant, sinon None."""
    if path and path.endswith('.json') and os.path.isfile(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return None


class AdminController:
    """Contrôleur pour la fenêtre d'administration du gérant"""
    def __init__(self, user_id):
        """Initialise le contrôleur d'administration."""
        self.user_id = user_id
        self.view = AdminView()
        self._connect_signals()
        self.load_shop_data()

    def _connect_signals(self):
        """Relie les widgets et les actions de menu de la vue aux méthodes du contrôleur."""
        view = self.view

        # Stocks
        view.btn_ajouter.clicked.connect(self.ouvrir_dialog_ajout_article)
        view.btn_retirer.clicked.connect(self.confirm_remove)
        view.filtre_combo.currentTextChanged.connect(view.filtrer_produits)
        view.search_input.textChanged.connect(view.rechercher_produits)

        # Plan
        view.btn_ouvrir_image.clicked.connect(self.ouvrir_image_plan)
        view.btn_reinitialiser.clicked.connect(self.confirm_reset)
        view.btn_exporter.clicked.connect(self.exporter_quadrillage_json)
        view.btn_importer.clicked.connect(self.importer_quadrillage_json)
        view.btn_deconnexion.clicked.connect(self.deconnexion)
        view.slider_grid.valueChanged.connect(view.grid_overlay.set_grid_size)
        view.slider_zoom.valueChanged.connect(lambda v: view.grid_overlay.set_zoom(v / 100.0))

        # Menus
        view.action_charger.triggered.connect(self.ouvrir_gestion_magasins)
        view.action_configurer.triggered.connect(self.ouvrir_configurer_magasin)
        view.action_gestion_employes.triggered.connect(self.ouvrir_gestion_employes)
        view.action_ouvrir_plan.triggered.connect(self.ouvrir_image_plan)
        view.action_reinitialiser_plan.triggered.connect(self.confirm_reset)
        view.action_exporter_json.triggered.connect(self.exporter_quadrillage_json)
        view.action_importer_json.triggered.connect(self.importer_quadrillage_json)
        view.action_about.triggered.connect(self.open_about)
        view.action_doc.triggered.connect(self.open_help)
        view.action_licence.triggered.connect(self.open_licence)

        # Outils plan
        view.btn_deplacer.clicked.connect(lambda: view.grid_overlay.set_pan_mode(True))
        for btn, tool in [
            (view.btn_rayon, CELL_SHELF),
            (view.btn_stock, CELL_STOCK),
            (view.btn_caisse, CELL_CHECKOUT),
            (view.btn_entree, CELL_ENTRANCE),
            (view.btn_supprimer, TOOL_ERASER)
        ]:
            btn.clicked.connect(lambda checked, t=tool: self.set_plan_mode(t))

    def load_shop_data(self):
        """Charge les données du magasin et les affiche dans la vue."""
        result = get_shop_data(self.user_id)

        # Vérifie si les données du magasin ont été récupérées avec succès
        if result:
            articles_json, plan_json, plan_image_path = result

            # Charge les catégories et les produits depuis le JSON des articles
            articles_json_content = _read_json_file(articles_json)
            if articles_json_content is not None:
                self.view.afficher_stocks_depuis_json(articles_json_content)

            # Charge le plan du magasin
            if plan_image_path:
                self.view.grid_overlay.load_image(plan_image_path)

            # Charge le quadrillage
            plan_json_content = _read_json_file(plan_json)
            if plan_json_content is not None:
                self.view.grid_overlay.import_cells_from_json_content(plan_json_content)
                self.view.slider_grid.setValue(self.view.grid_overlay.grid_size)

    def set_plan_mode(self, mode):
        """Change le mode de plan en fonction du bouton cliqué."""
        if mode in PLAN_TOOLS:
            self.view.grid_overlay.set_current_color(mode)
            self.view.grid_overlay.set_pan_mode(False)

    def ouvrir_dialog_ajout_article(self):
        """Ouvre le dialogue pour ajouter un nouvel article."""
        dialog = AddArticleDialog(self.view.categories, self.view)

        if dialog.exec():
            nom, categorie = dialog.get_data()
            if nom and categorie:
                key = f"{categorie.lower()}::{nom.lower()}"
                if key in self.view.produit_categorie_map:
                    QMessageBox.warning(self.view, "Doublon", f"L'article '{nom}' existe déjà dans la catégorie '{categorie}'.")
                    return
                self.view.stocks_list.addItem(nom)
                self.view.produit_categorie_map[key] = (categorie, nom)
                self.view.categories.add(categorie)
                self.view.maj_filtre_categories()
                self.sauvegarder_articles_json()
            else:
                QMessageBox.warning(self.view, "Erreur", "Veuillez remplir tous les champs.")

    def confirm_remove(self):
        """Confirme la suppression de l'article sélectionné."""
        # Vérifie si un article est sélectionné
        if not self.view.stocks_list.currentItem():
            QMessageBox.warning(self.view, "Aucun article sélectionné", "Veuillez sélectionner un article à retirer.")
            return

        if ask_yes_no(self.view, "Confirmation", "Êtes-vous sûr de vouloir retirer ce produit ?"):
            self.retirer_article_selectionne()

    def retirer_article_selectionne(self):
        """Retire l'article sélectionné de la liste des stocks."""
        item = self.view.stocks_list.currentItem()
        if not item:
            return
        nom = item.text()
        key_to_remove = None
        for key, (_, nom_map) in self.view.produit_categorie_map.items():
            if nom_map == nom:
                key_to_remove = key
                break
        if key_to_remove:
            del self.view.produit_categorie_map[key_to_remove]
            self.view.stocks_list.takeItem(self.view.stocks_list.row(item))
            self.sauvegarder_articles_json()

    def sauvegarder_articles_json(self):
        """Sauvegarde les articles et leurs catégories dans la base de données."""
        data = {}
        for _, (cat, nom) in self.view.produit_categorie_map.items():
            data.setdefault(cat, []).append(nom)
        articles_json_content = json.dumps(data, ensure_ascii=False, indent=2)
        update_articles_json(self.user_id, articles_json_content)

    def ouvrir_image_plan(self):
        """Ouvre un dialogue pour choisir une image de plan et la charge dans le quadrillage."""
        file_name, _ = QFileDialog.getOpenFileName(self.view, "Choisir un plan", "", IMAGE_FILTER)
        if file_name:
            self.view.grid_overlay.load_image(file_name)
            update_shop_image(self.user_id, file_name)

    def confirm_reset(self):
        """Affiche une boîte de dialogue de confirmation pour réinitialiser le quadrillage."""
        if ask_yes_no(self.view, "Confirmation", "Êtes-vous sûr de vouloir tout réinitialiser ?"):
            self.view.grid_overlay.reset_colored_cells()

    def exporter_quadrillage_json(self):
        """Exporte le quadrillage actuel en JSON."""
        if self.view.grid_overlay.image_item is None:
            QMessageBox.warning(self.view, "Erreur", "Veuillez d'abord charger une image de plan avant d'exporter un JSON.")
            return
        file_name, _ = QFileDialog.getSaveFileName(self.view, "Exporter en JSON", "", JSON_FILTER)
        if file_name:
            buffer = io.StringIO()
            self.view.grid_overlay.export_cells_to_json(buffer)
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(buffer.getvalue())
            buffer.close()
            QMessageBox.information(self.view, "Export", "Exportation réussie !")

    def importer_quadrillage_json(self):
        """Importe un quadrillage depuis un fichier JSON."""
        if self.view.grid_overlay.image_item is None:
            QMessageBox.warning(self.view, "Erreur", "Veuillez d'abord charger une image de plan avant d'importer un JSON.")
            return
        file_name, _ = QFileDialog.getOpenFileName(self.view, "Importer JSON", "", JSON_FILTER)
        if file_name:
            self.view.grid_overlay.import_cells_from_json(file_name)
            QMessageBox.information(self.view, "Import", "Importation réussie !")

    def ouvrir_configurer_magasin(self):
        """Ouvre la fenêtre de configuration du magasin."""
        dialog = ConfigureWindow(self.user_id, self.view)
        if dialog.exec():
            self.load_shop_data()

    def ouvrir_gestion_employes(self):
        """Ouvre la fenêtre de gestion des employés."""
        shop_id = get_employees_shop_id(self.user_id)
        if shop_id:
            dlg = EmployeManagerDialog(shop_id, self.view)
            dlg.exec()
        else:
            QMessageBox.warning(self.view, "Erreur", "Aucun magasin associé à ce compte.")

    def ouvrir_gestion_magasins(self):
        """Ouvre la fenêtre de gestion des magasins."""
        dlg = ShopManagerDialog(self.user_id, self.view)
        if dlg.exec() and hasattr(dlg, "selected_shop_id"):
            articles_json = get_shop_articles_by_id(dlg.selected_shop_id)
            if articles_json:
                self.view.afficher_stocks_depuis_json(articles_json)

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
