import numpy as np
from typing import Literal

def mana_curve_similarity(deck, n, ccg : Literal["MTG","HS"]):
    """
    Calcula qué tan cercana es la curva de maná del mazo 'deck' 
    a la curva de maná óptima escalada para un mazo de tamaño n.

    Parámetros:
        - deck: lista de cartas (objetos MTGCard), cada carta tiene .convertedManaCost (CMC)
        - n: tamaño total del mazo (int)
    
    Retorna:
        - score de similitud: valor en [0, 1], 1 es curva perfecta, 0 muy diferente.
    """

    # Curva de maná óptima (valores de ejemplo en porcentaje)
    # Bins: 0-1, 2, 3, 4, 5+
    optimal_curve_pct = np.array([0.10, 0.35, 0.25, 0.15, 0.15]) if ccg == "MTG" else np.array([0.15, 0.26, 0.24, 0.19, 0.16])

    # Escalar para n cartas
    optimal_curve_counts = optimal_curve_pct * n

    # Obtener CMCs del mazo actual
    cmcs = np.array([min(card.convertedManaCost, 5) for card in deck])  # CMC max 5+

    # Contar cartas en los bins definidos
    bins = [0, 1, 2, 3, 4, 100]  # último bin es 5+
    current_curve_counts, _ = np.histogram(cmcs, bins=bins)

    # Si el mazo actual es menor que n (parcial), escalar para comparación
    scale_factor = n / max(len(deck), 1)
    current_curve_scaled = current_curve_counts * scale_factor

    # Calcular similitud como 1 - error relativo absoluto promedio
    error = np.abs(current_curve_scaled - optimal_curve_counts)
    max_error = optimal_curve_counts.sum()
    similarity = 1 - (error.sum() / max_error)

    # Limitar entre 0 y 1
    similarity = max(0.0, min(1.0, similarity))

    return similarity
