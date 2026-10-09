# ==============================================================
# Débogage de l'algorithme avec un exemple
# Lancement : python -m market_tracer.core.algorithm_demo
# Développé par D. MELOCCO
# ==============================================================

import sys

from market_tracer.core import algorithm
from market_tracer.paths import JSON_DIR


def main():
    json_path = str(JSON_DIR / "test_algo.json")
    shopping_list = ["Calculatrice", "Citrouille", "Brocolis"]  # exemple de liste de course

    cells = algorithm.load_cells(json_path)
    grid, entry, caisses = algorithm.load_grid_from_json(json_path)

    # 1. Trouver les coordonnées des articles de la liste
    shopping_points = algorithm.find_shopping_points(cells, shopping_list, grid)
    if not shopping_points:
        print("Aucun article de la liste trouvé dans le plan.")
        sys.exit(1)

    # 2. Trouver l'ordre optimal (brute force si peu d'articles)
    ordered_points = algorithm.order_points(entry, shopping_points)

    # 3. Ajouter la caisse la plus proche à la fin
    last_point = ordered_points[-1] if ordered_points else entry
    nearest_accessible_caisse = algorithm.find_nearest_accessible_caisse(grid, last_point, caisses)
    if nearest_accessible_caisse is None:
        print("Aucune caisse accessible trouvée.")
        sys.exit(1)
    full_points = [entry] + ordered_points + [nearest_accessible_caisse]

    # 4. Calculer le chemin complet
    full_path = algorithm.find_full_path(grid, full_points)

    # Débogage
    print("Entrée :", entry)
    print("Rayons à visiter :", shopping_points)
    print("Caisses :", caisses)

    if full_path:
        print(f"Chemin optimisé trouvé ({len(full_path)} étapes).")
        total_distance = algorithm.calculate_total_distance(full_path)
        print(f"Distance totale du chemin : {total_distance:.2f} mètres")
        algorithm.visualize_path(grid, full_path, full_points, cells)
    else:
        print("Aucun chemin trouvé :(")


if __name__ == "__main__":
    main()
