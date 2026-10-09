# ==============================================================
# Catalogue de produits (catégories, filtre, recherche) partagé
# entre la vue du gérant et la vue du client / employé
# ==============================================================

import json

from market_tracer.constants import ALL_CATEGORIES


class ProductCatalogMixin:
    """Gère la liste `stocks_list` des produits groupés par catégorie.

    La classe qui l'utilise doit définir `stocks_list`, `filtre_combo`,
    `search_input` et `status_bar`, puis appeler `_init_catalog()`.
    """

    def _init_catalog(self):
        """Initialise les structures de données du catalogue."""
        self.categories = set()  # Ensemble pour stocker les catégories de produits
        self.produit_categorie_map = {}  # "catégorie::produit" -> (catégorie, produit)

    def _load_catalog(self, json_content, status_ok, empty_message, status_error):
        """Charge le catalogue depuis un contenu JSON {catégorie: [produits]}.

        Args:
            json_content (str): contenu JSON.
            status_ok (str): message de la barre d'état en cas de succès ({count} = nombre de produits).
            empty_message (str): ligne affichée dans la liste en cas d'échec.
            status_error (str): message de la barre d'état en cas d'échec.
        """
        self.stocks_list.clear()
        self.produit_categorie_map = {}
        self.categories = set()
        try:
            data = json.loads(json_content)
            for categorie, produits in data.items():
                self.categories.add(categorie)
                for produit in produits:
                    key = f"{categorie.lower()}::{produit.lower()}"
                    self.stocks_list.addItem(produit)
                    self.produit_categorie_map[key] = (categorie, produit)
            self.maj_filtre_categories()
            self.status_bar.setText(status_ok.format(count=self.stocks_list.count()))
        except Exception:
            self.stocks_list.addItem(empty_message)
            self.status_bar.setText(status_error)

    def maj_filtre_categories(self):
        """Met à jour la liste des catégories dans le filtre."""
        self.filtre_combo.blockSignals(True)
        self.filtre_combo.clear()
        self.filtre_combo.addItem(ALL_CATEGORIES)
        for cat in sorted(self.categories, key=lambda x: x.lower()):
            self.filtre_combo.addItem(cat)
        self.filtre_combo.blockSignals(False)

    def filtrer_produits(self, categorie):
        """Filtre les produits affichés en fonction de la catégorie sélectionnée."""
        self.stocks_list.clear()
        texte = self.search_input.text().lower()
        for _, (cat, nom) in self.produit_categorie_map.items():
            if (categorie == ALL_CATEGORIES or cat.lower() == categorie.lower()) and texte in nom.lower():
                self.stocks_list.addItem(nom)

    def rechercher_produits(self, texte):
        """Recherche des produits en fonction du texte entré dans le champ de recherche."""
        texte = texte.lower()
        categorie = self.filtre_combo.currentText()
        self.stocks_list.clear()
        for _, (cat, nom) in self.produit_categorie_map.items():
            if (categorie == ALL_CATEGORIES or cat == categorie) and texte in nom.lower():
                self.stocks_list.addItem(nom)
