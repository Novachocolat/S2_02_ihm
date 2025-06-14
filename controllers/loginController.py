# ==============================================================
# Contrôleur pour la fenêtre de connexion
# Développé par D. MELOCCO, L. PACE--BOULNOIS, S. LECLERCQ-SPETER
# Dernière modification : 13/06/2025
# ==============================================================

from PyQt6.QtWidgets import QMessageBox
from models.loginModel import (
    get_user, set_first_login, get_shop_info, get_nb_shops, get_articles_json
)
from views.loginView import LoginView

class LoginController:
    """Contrôleur pour la fenêtre de connexion"""
    def __init__(self):
        """Initialise le contrôleur de connexion."""
        self.view = LoginView()
        for role, btn in self.view.role_buttons.items():
            btn.clicked.connect(lambda checked, r=role: self.select_role(r))
        self.view.login_btn.clicked.connect(self.try_login)
        self.view.pass_input.returnPressed.connect(self.try_login)
        self.view.enter_btn.clicked.connect(self.enter_as_client)
        self.view.selected_role = "Gérant"

    def select_role(self, role):
        """Sélectionne le rôle de l'utilisateur et met à jour l'interface en conséquence."""
        self.view.selected_role = role
        for r, btn in self.view.role_buttons.items():
            btn.setChecked(r == role)
        if role == "Client":
            self.view.login_btn.hide()
            self.view.enter_btn.show()
            self.view.user_label.hide()
            self.view.user_input.hide()
            self.view.pass_label.hide()
            self.view.pass_input.hide()
        else:
            self.view.login_btn.show()
            self.view.enter_btn.hide()
            self.view.user_label.show()
            self.view.user_input.show()
            self.view.pass_label.show()
            self.view.pass_input.show()

    def try_login(self):
        """Tente de connecter l'utilisateur en fonction des informations saisies."""
        from configureWindow import ConfigureWindow
        from controllers.customerController import CustomerController
        username = self.view.user_input.text()
        password = self.view.pass_input.text()

        role = self.view.selected_role
        user = get_user(username, password, role)
        
        # Si l'utilisateur existe, on récupère ses informations
        if user:
            # Si l'utilisateur est un gérant
            if role == "Gérant":
                user_id, _, _, _, _, first_login = user
                # Si c'est le premier login, on ouvre la fenêtre de configuration de magasin
                if first_login:
                    self.configure_window = ConfigureWindow(user_id, parent=self.view)
                    self.configure_window.exec()
                    self.open_admin_window(user_id)
                    set_first_login(user_id, 0)
                # Sinon, on ouvre la fenêtre d'administration
                else:
                    self.open_admin_window(user_id)

            # Si l'utilisateur est un employé
            elif role == "Employé":
                shop_id = user[4]
                if shop_id:
                    self.employee_window = CustomerController("json/liste_produits.json", shop_id, "Employé")
                    self.employee_window.view.show()
                    self.view.close()
                else:
                    QMessageBox.warning(self.view, "Erreur", "Aucun magasin associé à ce compte employé.")
            self.view.close()
        else:
            self.view.error_label.setText("Nom d'utilisateur, mot de passe ou rôle incorrect.")

    def enter_as_client(self):
        """Ouvre la fenêtre client si un magasin est disponible."""
        self.open_client_window()
        self.view.close()

    def open_client_window(self):
        """Ouvre la fenêtre client en sélectionnant un magasin."""
        from shopSelectorDialog import ShopSelectorDialog
        from controllers.customerController import CustomerController
        nb_shops = get_nb_shops()
        if nb_shops == 0:
            QMessageBox.warning(self.view, "Aucun magasin", "Aucun magasin n'est disponible pour les clients.")
            return
        dlg = ShopSelectorDialog(self.view)
        if dlg.exec() and dlg.selected_shop_id:
            self.client_window = CustomerController("json/liste_produits.json", dlg.selected_shop_id, "Client")
            self.client_window.view.show()

    def open_admin_window(self, user_id):
        """Ouvre la fenêtre d'administration pour le gérant."""
        from controllers.adminController import AdminController
        self.admin_controller = AdminController(user_id)
        self.admin_controller.view.show()