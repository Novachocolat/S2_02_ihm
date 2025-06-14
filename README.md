
*Version du 14/06/2025*

![Logo](img/logo_ext_v1.png)


# Market Tracer — 1.0

Market Tracer est un outil compétent qui aide à la gestion des stocks des supermarchés et qui permet à leurs clients fidèles de faire leurs courses efficacement.

## Développeurs

**Équipe n°15 :**

- [David](https://www.github.com/ThFoxY) ![Développeur](https://img.shields.io/badge/Développeur-4BCE97) ![Doc](https://img.shields.io/badge/Doc-B3B9C4)
- [Lysandre](https://www.github.com/Novachocolat) ![Développeur](https://img.shields.io/badge/Développeur-4BCE97) ![Leader](https://img.shields.io/badge/Leader-579DFF)
- [Noé](https://github.com/Kiizer861) ![Développeur](https://img.shields.io/badge/Développeur-4BCE97)
- [Simon](https://github.com/KoshyMVP) ![Développeur](https://img.shields.io/badge/Développeur-4BCE97)


## 🤝 Nos partenaires

Ce logiciel est utilisé par les plus grandes chaînes de magasins :

- Lidl
- Auchan
- Carrefour


## 📄 Documentation

Pour apprendre à utiliser l'application, rendez-vous ici : [Documentation](https://github.com/Novachocolat/S2_02_ihm/blob/main/DOC.md)


## ✏️ Rapports
Pour voir les comptes-rendus des avancements par séance, rendez-vous ici : [Rapports](https://github.com/Novachocolat/S2_02_ihm/blob/main/RAPPORTS.md)

## ⚙️ Fonctionnalités

### Application n°1 :

**Objectif :** Positionner les articles/produits dans le magasin par le gérant.

* **Gérer un magasin :**
    * Nom du magasin, gestionnaire(s) du magasin, date de création, informations relatives au magasin.
    * Charger et afficher le plan du magasin (image), les articles/produits (.json) et le quadrillage (.json).
    * Choisir les articles/produits vendus par le magasin.
    * Associer à chaque article/produit une position dans le magasin (case du quadrillage) via drag & drop.
    * Ajouter des articles/produits ou les retirer de la liste des stocks.
    * Gestion des employés pour l'accès aux stocks.

* **Enregistrer un magasin :**
    * Enregistrement automatisé par base de données locale.
    * Exportations et importations des fichiers sources.

### Application n°2 :

**Objectif :** Déterminer le chemin le plus efficace pour faire ses courses dans un magasin choisi.

* Choix du magasin.
* Voir le plan du magasin.
* Établir une liste de course.
* Afficher le chemin le plus efficace.
* Exporter en format image le chemin.


## ➕ Additions

* Quadrillage automatique du plan.
* Accès sécurisé pour gérant et employé.
* Sauvegarde automatique.
* Mode clair/sombre automatique selon vos préférences.

## 🚧 W.I.P (Work In Progress)

* L'ajout de plusieurs magasins est malheureusement buggué.
* L'algorithme A* fonctionne, mais cela dépend de ses envies.
* Organisation dans des fichiers (entre fenêtres et pop-ups).
* Rédaction d'une meilleure documentation.
* Ajout de raccourcis clavier, de menus et de logs.
* Améliorer la résistance de la base de données.
* Prévenir les erreurs et les crashs, écrire des tests unitaires.


## Git

Clonez le projet

```bash
  git clone https://https://github.com/Novachocolat/S2_02_ihm.git
```

Choisissez un répertoire

```bash
  cd S2_02_ihm
```

Installez la bibliothèque **PyQt6**

```bash
  pip install pyqt6
```
