# ==============================================================
# Algorithme A* (Altération de : https://www.datacamp.com/fr/tutorial/a-star-algorithm?dc_referrer=https%3A%2F%2Fwww.google.com%2F)
# Développé par D. MELOCCO
# Dernière modification : 14/06/2025
# ==============================================================

from typing import List, Tuple, Dict
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt
import json # Sauvegarder les données en format .json
import heapq # Queue prioritaire pour explorer les meilleurs chemins en premier.
from itertools import (
    count, # Évite la comparaison directe des dictionnaires nativement
    permutations # Teste tous les ordres possibles (brute force)
)

def calculate_heuristic(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """Distance entre deux points"""
    return sqrt(
        (pos2[0] - pos1[0])**2
        +
        (pos2[1] - pos1[1])**2
    )

def calculate_total_distance(path: List[Tuple[int, int]], cell_size: float = 1.0) -> float:
    """Distance totale du parcours en mètres"""
    return sum(
        sqrt((x2 - x1)**2 + (y2 - y1)**2) * cell_size
        for (x1, y1), (x2, y2) in zip(path[:-1], path[1:])
    )

def get_valid_neighbors(grid: np.ndarray, position: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Obtient les prochains positions possibles"""
    x, y = position
    directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                  (0, 1), (1, -1), (1, 0), (1, 1)]
    neighbors = []
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1] and grid[nx, ny] == 0:
            neighbors.append((nx, ny))
    return neighbors

def reconstruct_path(node: Dict) -> List[Tuple[int, int]]:
    """Construction du parcours"""
    path = []
    while node:
        path.append(node['position'])
        node = node['parent']
    return path[::-1]

def load_grid_from_json(json_path: str) -> Tuple[np.ndarray, Tuple[int, int], List[Tuple[int, int]]]:
    """Charge la grille, la position de l'entrée et la liste des caisses depuis un fichier JSON."""
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
        cells = data["cells"]

    # Trouver la taille max de la grille
    max_row = max(cell["row"] for cell in cells) + 1
    max_col = max(cell["col"] for cell in cells) + 1

    # Créer la matrice correspondante
    grid = np.zeros((max_row, max_col), dtype=int)
    entry = None # Nombre d'entrée
    caisses = [] # Caisses
    for cell in cells:
        row, col, typ = cell["row"], cell["col"], cell["type"]
        # Obstacles
        if typ == "Rayon" or typ == "Mur":
            grid[row, col] = 1
        if typ == "Entrée":
            entry = (row, col)
        if typ == "Caisse":
            caisses.append((row, col))
    return grid, entry, caisses

def find_nearest_goal(grid: np.ndarray, start: Tuple[int, int], goals: List[Tuple[int, int]]) -> Tuple[List[Tuple[int, int]], Tuple[int, int]]:
    """Trouve le chemin le plus court de l'entrée à la caisse la plus proche."""
    min_path = None
    min_goal = None
    min_len = float('inf')
    for goal in goals:
        path = find_path(grid, start, goal)
        if path and len(path) < min_len:
            min_len = len(path)
            min_path = path
            min_goal = goal
    return min_path, min_goal

def find_path(grid: np.ndarray, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
    """Exploration de chemin avec l'agorithme A* de l'entrée aux caisses"""
    open_heap = []
    counter = count()  # Évite la comparaison directe des dictionnaires nativement

    start_node = {
        'position': start,
        'g': 0,
        'h': calculate_heuristic(start, goal),
        'f': 0,
        'parent': None
    }
    start_node['f'] = start_node['g'] + start_node['h']
    heapq.heappush(open_heap, (start_node['f'], next(counter), start_node))
    visited: Dict[Tuple[int, int], float] = {start: 0}

    while open_heap:
        _, _, current = heapq.heappop(open_heap)
        current_pos = current['position']

        if current_pos == goal:
            return reconstruct_path(current)

        for neighbor_pos in get_valid_neighbors(grid, current_pos):
            tentative_g = current['g'] + calculate_heuristic(current_pos, neighbor_pos)

            if neighbor_pos not in visited or tentative_g < visited[neighbor_pos]:
                visited[neighbor_pos] = tentative_g
                neighbor = {
                    'position': neighbor_pos,
                    'g': tentative_g,
                    'h': calculate_heuristic(neighbor_pos, goal),
                    'f': tentative_g + calculate_heuristic(neighbor_pos, goal),
                    'parent': current
                }
                heapq.heappush(open_heap, (neighbor['f'], next(counter), neighbor))

    return []

# ==============================================================
# Visualisation
# ==============================================================
def visualize_path(grid: np.ndarray, path: List[Tuple[int, int]], points: List[Tuple[int, int]], 
                   cells: list = None):
    """Visualisation du parcours via un graphique

    Args:
        grid (np.ndarray): le quadrillage du magasin
        path (List[Tuple[int, int]]): le parcours de l'algorithme A*
        waypoints (List[Tuple[int, int]]): les points où passe l'algorithme A*
        cells (list, optional): les cellules (par défaut aucune)
    """
    plt.figure(figsize=(10, 5))

    # Affichage des couleurs
    if cells is not None:
        color_map = {
            "Rayon": "#4A90E2",
            "Mur": "#222222",
            "Caisse": "#E67E22",
            "Entrée": "#27AE60",
        }
        for cell in cells:
            row, col, typ = cell["row"], cell["col"], cell["type"]
            if typ in color_map:
                plt.gca().add_patch(
                    plt.Rectangle((col-0.5, row-0.5), 1, 1, color=color_map[typ], alpha=0.7)
                )

    # Affiche le quadrillage pour les cases libres
    plt.imshow(grid, cmap='Greys', alpha=0.2)

    # Affiche le parcours
    if path:
        path = np.array(path)
        plt.plot(path[:, 1], path[:, 0], 'b-', linewidth=2, label='Parcours')
        plt.plot(path[0, 1], path[0, 0], 'go', markersize=10, label='Entrée')
        plt.plot(path[-1, 1], path[-1, 0], 'ro', markersize=10, label='Caisse')
    
    # Numérote les points de passage dans l'ordre
    for idx, pt in enumerate(points):
        plt.text(pt[1], pt[0], str(idx+1), color="black", fontsize=14, fontweight='bold',
                 ha='center', va='center', bbox=dict(facecolor='white', edgecolor='none', alpha=0.7))

    plt.legend(fontsize=10)
    plt.title("Votre parcours")
    plt.show()

def find_full_path(grid: np.ndarray, points: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    """Trouve le parcours complet

    Args:
        grid (np.ndarray): le quadrillage du magasin
        points (List[Tuple[int, int]]): les points où passe l'algorithme A*

    Returns:
        List[Tuple[int, int]]: le parcours de l'algorithme A*
    """
    full_path = []
    for i in range(len(points) - 1):
        segment = find_path(grid, points[i], points[i + 1])
        if not segment:
            print(f"Pas de chemin entre {points[i]} et {points[i+1]}")
            return []
        full_path.extend(segment if i == 0 else segment[1:])
    return full_path

def find_accessible_neighbor(grid: np.ndarray, row: int, col: int):
    """Renvoie la première case voisine disponible d'un obstacle"""
    for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx, ny = row + dx, col + dy
        if 0 <= nx < grid.shape[0] and 0 <= ny < grid.shape[1]:
            if grid[nx, ny] == 0:
                return (nx, ny)
    return None

def find_nearest_accessible_caisse(grid, start, caisses):
    """Cherche la case libre la plus proche d'une caisse"""
    accessibles = []
    for caisse in caisses:
        access = find_accessible_neighbor(grid, caisse[0], caisse[1])
        if access:
            accessibles.append(access)
    if not accessibles:
        return None
    path, goal = find_nearest_goal(grid, start, accessibles)
    return goal

def find_shopping_points(cells, shopping_list, grid, allowed_types=("Rayon",)):
    """Retourne la liste des coordonnées à visiter pour chaque élément de la liste de courses."""
    points = []
    for item in shopping_list:
        found = False
        for cell in cells:
            if cell.get("type") in allowed_types:
                obj = cell.get("object")
                if (isinstance(obj, str) and obj.lower() == item.lower()) or \
                   (isinstance(obj, dict) and obj.get("product", "").lower() == item.lower()):
                    row, col = cell["row"], cell["col"]
                    access = find_accessible_neighbor(grid, row, col)
                    if access:
                        points.append(access)
                    else:
                        print(f"⚠️  Aucun accès libre autour du {cell.get('type').lower()} '{item}' en ({row},{col})")
                    found = True
                    break
        if not found:
            print(f"⚠️  Article '{item}' introuvable dans le plan.")
    return points

def brute_force(start, points):
    """Trouve l'ordre optimal pour visiter tous les points (petite liste seulement)."""
    min_path = None
    min_len = float('inf')
    for perm in permutations(points):
        path = [start] + list(perm)
        total = sum(calculate_heuristic(path[i], path[i+1]) for i in range(len(path)-1))
        if total < min_len:
            min_len = total
            min_path = path
    return min_path

# ==============================================================
# Débogage avec un exemple
# ==============================================================
if __name__ == "__main__":
    json_path = "json/test_algo.json"
    shopping_list = ["Calculatrice", "Citrouille", "Brocolis"] # exemple de liste de course

    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)
    cells = data["cells"]
    grid, entry, caisses = load_grid_from_json(json_path)

    # 1. Trouver les coordonnées des articles de la liste
    shopping_points = find_shopping_points(cells, shopping_list, grid)
    if not shopping_points:
        print("Aucun article de la liste trouvé dans le plan.")
        exit(1)

    # 2. Trouver l'ordre optimal (brute force si peu d'articles)
    if len(shopping_points) <= 5:
        ordered_points = brute_force(entry, shopping_points)[1:]  # sans le départ
    else:
        # Heuristique : ordre du plus proche à chaque étape
        ordered_points = []
        current = entry
        remaining = shopping_points.copy()
        while remaining:
            next_point = min(remaining, key=lambda p: calculate_heuristic(current, p))
            ordered_points.append(next_point)
            remaining.remove(next_point)
            current = next_point

    # 3. Ajouter la caisse la plus proche à la fin
    if ordered_points:
        last_point = ordered_points[-1]
    else:
        last_point = entry
    nearest_accessible_caisse = find_nearest_accessible_caisse(grid, last_point, caisses)
    if nearest_accessible_caisse is None:
        print("Aucune caisse accessible trouvée.")
        exit(1)
    full_points = [entry] + ordered_points + [nearest_accessible_caisse]

    # 4. Calculer le chemin complet
    full_path = find_full_path(grid, full_points)
    
    # Débogage
    print("Entrée :", entry)
    print("Rayons à visiter :", shopping_points)
    print("Caisses :", caisses)

    if full_path:
        print(f"Chemin optimisé trouvé ({len(full_path)} étapes).")
        total_distance = calculate_total_distance(full_path)
        print(f"Distance totale du chemin : {total_distance:.2f} mètres")
        visualize_path(grid, full_path, full_points, cells)
    else:
        print("Aucun chemin trouvé :(")