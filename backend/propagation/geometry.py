"""Conversión del plano GeoJSON (2D, en píxeles) a geometría física (metros).

El frontend almacena las plantas como GeoJSON donde las coordenadas están en
**píxeles** de la imagen del plano. ``scale`` es el factor metros/píxel. Aquí
normalizamos todo a metros para alimentar tanto el motor Sionna RT (escena 3D)
como el modelo analítico multi-pared.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

from . import materials


@dataclass
class WallSegment:
    """Segmento de pared en metros, con su material asociado."""
    p1: Tuple[float, float]
    p2: Tuple[float, float]
    material: materials.Material

    @property
    def length(self) -> float:
        return float(np.hypot(self.p2[0] - self.p1[0], self.p2[1] - self.p1[1]))


@dataclass
class FloorGeometry:
    walls: List[WallSegment]
    bounds_m: Tuple[float, float, float, float]   # (min_x, min_y, max_x, max_y) en metros
    scale: float                                  # metros por píxel

    @property
    def width_m(self) -> float:
        return self.bounds_m[2] - self.bounds_m[0]

    @property
    def depth_m(self) -> float:
        return self.bounds_m[3] - self.bounds_m[1]

    def to_pixels(self, x_m: float, y_m: float) -> Tuple[float, float]:
        """Convierte metros de vuelta a píxeles (espacio del GeoJSON/heatmap)."""
        return x_m / self.scale, y_m / self.scale


def _iter_rings(geojson: Dict[str, Any]):
    """Genera ``(coords, material_key)`` para cada geometría con paredes."""
    for feature in geojson.get("features", []):
        geometry = feature.get("geometry") or {}
        material_key = (feature.get("properties") or {}).get("material")
        gtype = geometry.get("type")
        if gtype == "Polygon":
            for ring in geometry.get("coordinates", []):
                yield ring, material_key
        elif gtype == "LineString":
            yield geometry.get("coordinates", []), material_key
        elif gtype == "MultiLineString":
            for line in geometry.get("coordinates", []):
                yield line, material_key


def parse_geojson(geojson: Dict[str, Any], scale: Optional[float]) -> FloorGeometry:
    """Convierte el GeoJSON de una planta en :class:`FloorGeometry` (metros)."""
    if not geojson or not geojson.get("features"):
        raise ValueError("GeoJSON vacío o sin 'features'; no hay geometría que simular.")

    scale = float(scale) if scale else 1.0

    walls: List[WallSegment] = []
    xs: List[float] = []
    ys: List[float] = []

    for ring, material_key in _iter_rings(geojson):
        material = materials.resolve(material_key)
        for i in range(len(ring) - 1):
            (x1, y1), (x2, y2) = ring[i][:2], ring[i + 1][:2]
            p1 = (x1 * scale, y1 * scale)
            p2 = (x2 * scale, y2 * scale)
            # Descartar segmentos degenerados (longitud ~0).
            if np.hypot(p2[0] - p1[0], p2[1] - p1[1]) < 1e-6:
                continue
            walls.append(WallSegment(p1, p2, material))
            xs.extend([p1[0], p2[0]])
            ys.extend([p1[1], p2[1]])

    if not walls:
        raise ValueError("El GeoJSON no contiene segmentos de pared válidos.")

    bounds = (min(xs), min(ys), max(xs), max(ys))
    return FloorGeometry(walls=walls, bounds_m=bounds, scale=scale)
