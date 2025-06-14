# ==============================================================
# Contrôleur pour la fenêtre d'administration du gérant
# Développé par D. MELOCCO, L. PACE--BOULNOIS, S. LECLERCQ-SPETER, N. COLIN
# Dernière modification : 13/06/2025
# ==============================================================

from PyQt6.QtWidgets import QMessageBox, QFileDialog
from models.adminModel import (
    get_shop_data, update_shop_image, update_articles_json,
    get_employees_shop_id, get_shop_articles_by_id
)
from views.adminView import AdminView

from addArticleDialog import AddArticleDialog
from shopManagerDialog import ShopManagerDialog
from employeManagerDialog import EmployeManagerDialog
import json
import os

class AdminController:
    """Contrôleur pour la fenêtre d'administration du gérant"""
    def __init__(self, user_id):
        """Initialise le contrôleur d'administration."""
        self.user_id = user_id
        self.view = AdminView()
        self.categories = set() # Pour stocker les catégories d'articles
        self.produit_categorie_map = {} # Pour stocker les produits avec leur catégorie

        # Connexion des signaux
        self.view.btn_ajouter.clicked.connect(self.ouvrir_dialog_ajout_article)
        self.view.btn_retirer.clicked.connect(self.confirm_remove)
        self.view.filtre_combo.currentTextChanged.connect(self.filtrer_stocks)
        self.view.search_input.textChanged.connect(self.rechercher_stocks)
        self.view.btn_ouvrir_image.clicked.connect(self.ouvrir_image_plan)
        self.view.btn_reinitialiser.clicked.connect(self.confirm_reset)
        self.view.btn_exporter.clicked.connect(self.exporter_quadrillage_json)
        self.view.btn_importer.clicked.connect(self.importer_quadrillage_json)
        self.view.btn_deconnexion.clicked.connect(self.deconnexion)
        self.view.menubar.actions()[0].menu().actions()[0].triggered.connect(self.ouvrir_gestion_magasins)
        self.view.menubar.actions()[1].menu().actions()[0].triggered.connect(self.ouvrir_configurer_magasin)
        self.view.menubar.actions()[1].menu().actions()[1].triggered.connect(self.ouvrir_gestion_employes)
        self.view.menubar.actions()[2].menu().actions()[0].triggered.connect(self.ouvrir_image_plan)
        self.view.menubar.actions()[2].menu().actions()[1].triggered.connect(self.confirm_reset)
        self.view.menubar.actions()[2].menu().actions()[2].triggered.connect(self.exporter_quadrillage_json)
        self.view.menubar.actions()[2].menu().actions()[3].triggered.connect(self.importer_quadrillage_json)
        self.view.menubar.actions()[3].menu().actions()[0].triggered.connect(self.open_about)
        self.view.menubar.actions()[3].menu().actions()[1].triggered.connect(self.open_help)
        self.view.menubar.actions()[3].menu().actions()[2].triggered.connect(self.open_licence)
        self.view.slider_grid.valueChanged.connect(lambda v: self.view.grid_overlay.set_grid_size(v))
        self.view.slider_zoom.valueChanged.connect(lambda v: self.view.grid_overlay.set_zoom(v / 100.0))

        # Outils plan
        self.view.btn_deplacer.clicked.connect(lambda: self.view.grid_overlay.set_pan_mode(True))
        for btn, color in [
            (self.view.btn_rayon, 'Rayon'),
            (self.view.btn_stock, 'Stock'),
            (self.view.btn_caisse, 'Caisse'),
            (self.view.btn_entree, 'Entrée'),
            (self.view.btn_supprimer, 'Gomme')
        ]:
            btn.clicked.connect(lambda checked, c=color: self.set_plan_mode(c))

        # Chargement des données
        self.load_shop_data()

    def load_shop_data(self):
        """Charge les données du magasin et les affiche dans la vue."""
        result = get_shop_data(self.user_id)
        
        # Vérifie si les données du magasin ont été récupérées avec succès
        if result:
            articles_json, plan_json, plan_image_path = result
            # Charge les catégories et les produits depuis le JSON des articles
            if articles_json and articles_json.endswith('.json') and os.path.isfile(articles_json):
                with open(articles_json, "r", encoding="utf-8") as f:
                    articles_json_content = f.read()
                self.view.afficher_stocks_depuis_json(articles_json_content)

            # Charge le plan du magasin
            if plan_image_path:
                self.view.grid_overlay.load_image(plan_image_path)

            # Charge le quadrillage
            if plan_json and plan_json.endswith('.json') and os.path.isfile(plan_json):
                with open(plan_json, "r", encoding="utf-8") as f:
                    plan_json_content = f.read()
                self.view.grid_overlay.import_cells_from_json_content(plan_json_content)
                self.view.slider_grid.setValue(self.view.grid_overlay.grid_size)
    
    def set_plan_mode(self, mode):
        """Change le mode de plan en fonction du bouton cliqué."""
        if mode == 'Rayon':
            self.view.grid_overlay.set_current_color('Rayon')
            self.view.grid_overlay.set_pan_mode(False)
        elif mode == 'Stock':
            self.view.grid_overlay.set_current_color('Stock')
            self.view.grid_overlay.set_pan_mode(False)
        elif mode == 'Caisse':
            self.view.grid_overlay.set_current_color('Caisse')
            self.view.grid_overlay.set_pan_mode(False)
        elif mode == 'Entrée':
            self.view.grid_overlay.set_current_color('Entrée')
            self.view.grid_overlay.set_pan_mode(False)
        elif mode == 'Gomme':
            self.view.grid_overlay.set_current_color('Gomme')
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
        item = self.view.stocks_list.currentItem()
        
        # Vérifie si un article est sélectionné
        if not item:
            QMessageBox.warning(self.view, "Aucun article sélectionné", "Veuillez sélectionner un article à retirer.")
            return

        # Affiche une boîte de dialogue de confirmation
        reply = QMessageBox.question(self.view, "Confirmation",
            "Êtes-vous sûr de vouloir retirer ce produit ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.retirer_article_selectionne()

    def retirer_article_selectionne(self):
        """Retire l'article sélectionné de la liste des stocks."""
        item = self.view.stocks_list.currentItem()
        if not item:
            return
        nom = item.text()
        key_to_remove = None
        for key, (cat, nom_map) in self.view.produit_categorie_map.items():
            if nom_map == nom:
                key_to_remove = key
                break
        if key_to_remove:
            del self.view.produit_categorie_map[key_to_remove]
            self.view.stocks_list.takeItem(self.view.stocks_list.row(item))
            self.sauvegarder_articles_json()

    def sauvegarder_articles_json(self):
        """Sauvegarde les articles et leurs catégories dans un fichier JSON."""
        data = {}
        for key, (cat, nom) in self.view.produit_categorie_map.items():
            data.setdefault(cat, []).append(nom)
        articles_json_content = json.dumps(data, ensure_ascii=False, indent=2)
        update_articles_json(self.user_id, articles_json_content)

    def filtrer_stocks(self, categorie):
        """Filtre les stocks en fonction de la catégorie sélectionnée."""
        self.view.stocks_list.clear()
        texte = self.view.search_input.text().lower()
        for key, (cat, nom) in self.view.produit_categorie_map.items():
            if (categorie == "Toutes les catégories" or cat.lower() == categorie.lower()) and texte in nom.lower():
                self.view.stocks_list.addItem(nom)

    def rechercher_stocks(self, texte):
        """Recherche les stocks en fonction du texte saisi."""
        texte = texte.lower()
        categorie = self.view.filtre_combo.currentText()
        self.view.stocks_list.clear()
        for key, (cat, nom) in self.view.produit_categorie_map.items():
            if (categorie == "Toutes les catégories" or cat == categorie) and texte in nom.lower():
                self.view.stocks_list.addItem(nom)

    def ouvrir_image_plan(self):
        """Ouvre un dialogue pour choisir une image de plan et la charge dans le quadrillage."""
        file_name, _ = QFileDialog.getOpenFileName(self.view, "Choisir un plan", "", "Images (*.png *.jpg *.bmp *.jpeg)")
        if file_name:
            self.view.grid_overlay.load_image(file_name)
            update_shop_image(self.user_id, file_name)

    def confirm_reset(self):
        """Affiche une boîte de dialogue de confirmation pour réinitialiser le quadrillage."""
        reply = QMessageBox.question(self.view, "Confirmation",
            "Êtes-vous sûr de vouloir tout réinitialiser ?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.view.grid_overlay.reset_colored_cells()

    def exporter_quadrillage_json(self):
        """Exporte le quadrillage actuel en JSON."""
        if self.view.grid_overlay.image_item is None:
            QMessageBox.warning(self.view, "Erreur", "Veuillez d'abord charger une image de plan avant d'exporter un JSON.")
            return
        file_name, _ = QFileDialog.getSaveFileName(self.view, "Exporter en JSON", "", "JSON (*.json)")
        if file_name:
            import io
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
        file_name, _ = QFileDialog.getOpenFileName(self.view, "Importer JSON", "", "JSON (*.json)")
        if file_name:
            self.view.grid_overlay.import_cells_from_json(file_name)
            QMessageBox.information(self.view, "Import", "Importation réussie !")

    def ouvrir_configurer_magasin(self):
        """Ouvre la fenêtre de configuration du magasin."""
        from configureWindow import ConfigureWindow
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