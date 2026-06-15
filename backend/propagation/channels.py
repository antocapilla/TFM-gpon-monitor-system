"""Asignación de canales WiFi mediante coloreo de grafos.

Modela los ONT/AP como nodos de un grafo donde dos nodos son adyacentes si
están lo bastante cerca como para interferirse (radio de cobertura solapado).
El coloreo greedy del grafo minimiza que vecinos compartan canal, y los colores
se mapean a los canales no solapados de cada banda.

Reemplaza tanto el round-robin ciego del servicio anterior como la asignación
aleatoria que hacía el frontend.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

import networkx as nx

# Canales no solapados (anchos de 20 MHz).
CHANNELS_2_4 = [1, 6, 11]
CHANNELS_5 = [36, 40, 44, 48, 52, 56, 60, 64, 100, 104, 108, 112, 116, 132, 136, 140]

# Radio de interferencia por defecto (metros) entre APs de la misma planta.
DEFAULT_ADJACENCY_M = 12.0


def _build_graph(positions_m: List[Tuple[float, float]], adjacency_m: float) -> nx.Graph:
    graph = nx.Graph()
    graph.add_nodes_from(range(len(positions_m)))
    for i in range(len(positions_m)):
        for j in range(i + 1, len(positions_m)):
            (xi, yi), (xj, yj) = positions_m[i], positions_m[j]
            if (xi - xj) ** 2 + (yi - yj) ** 2 < adjacency_m ** 2:
                graph.add_edge(i, j)
    return graph


def allocate_channels(
    onts: List[Dict],
    scale: Optional[float] = None,
    adjacency_m: float = DEFAULT_ADJACENCY_M,
) -> List[Dict]:
    """Asigna canales 2.4 y 5 GHz a cada ONT.

    Args:
        onts: lista de dicts con al menos ``serial``, ``x``, ``y`` (en píxeles).
        scale: metros por píxel (para medir distancias reales). Si es ``None``
            se asume 1.0 (las distancias quedan en unidades del plano).
        adjacency_m: radio de interferencia entre APs.

    Returns:
        Lista de dicts con la asignación por ONT.
    """
    scale = float(scale) if scale else 1.0
    positions_m = [((o.get("x") or 0.0) * scale, (o.get("y") or 0.0) * scale) for o in onts]

    graph = _build_graph(positions_m, adjacency_m)
    coloring = nx.coloring.greedy_color(graph, strategy="largest_first")

    allocation: List[Dict] = []
    for i, ont in enumerate(onts):
        color = coloring.get(i, 0)
        allocation.append({
            "serial": ont.get("serial"),
            "x": ont.get("x"),
            "y": ont.get("y"),
            "channel2_4": CHANNELS_2_4[color % len(CHANNELS_2_4)],
            "channel5": CHANNELS_5[color % len(CHANNELS_5)],
            "interferenceNeighbors": graph.degree(i),
            "status": "Online",
        })
    return allocation
