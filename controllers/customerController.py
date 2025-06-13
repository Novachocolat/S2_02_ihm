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
    def __init__(self, articles_json_path, shop_id):
        """Initialise le contrôleur du client."""
        self.view = CustomerView()
        self.liste_courses = []
        self.articles_json_path = "json/liste_produits.json" # TODO: Choisir un chemin vers une liste de produits personnalisée.
        self.shop_id = shop_id

        # Connexion des signaux
        self.view.btn_ajouter.clicked.connect(self.ajouter_article)
        self.view.btn_retirer.clicked.connect(self.retirer_article)
        self.view.btn_vider_liste.clicked.connect(self.vider_liste)
        self.view.btn_exporter.clicked.connect(self.exporter_liste)
        self.view.btn_importer.clicked.connect(self.importer_liste)
        self.view.filtre_combo.currentTextChanged.connect(self.view.filtrer_produits)
        self.view.search_input.textChanged.connect(self.view.rechercher_produits)
        self.view.btn_generer.clicked.connect(self.generer_parcours)
        self.view.btn_exporter_parcours.clicked.connect(self.exporter_parcours)
        self.view.btn_deconnexion.clicked.connect(self.deconnexion)
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
        """Génère un parcours optimal dans le magasin en fonction de la liste de courses."""
        # TODO: Implémenter la logique de génération de parcours

    def exporter_parcours(self):
        """Exporte le parcours généré."""
        # TODO: Implémenter l'export du parcours

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