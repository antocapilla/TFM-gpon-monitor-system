"""Orquestador de la simulación de propagación.

Selecciona el motor (Sionna RT si está disponible, modelo analítico multi-pared
en caso contrario), ejecuta el mapa de cobertura y empaqueta el resultado en el
formato que consume el frontend.
"""
from __future__ import annotations

import logging
from typing import Dict, List, Optional

import numpy as np

from . import analytical_engine, channels, geometry, sionna_engine
from .params import SimulationParams

logger = logging.getLogger(__name__)


def _ont_list(onts) -> List[Dict]:
    """Normaliza los ONT (objetos Pydantic o dicts) a dicts con serial/x/y."""
    result = []
    for o in onts:
        serial = getattr(o, "serial", None) if not isinstance(o, dict) else o.get("serial")
        x = getattr(o, "x", None) if not isinstance(o, dict) else o.get("x")
        y = getattr(o, "y", None) if not isinstance(o, dict) else o.get("y")
        if x is None or y is None:
            continue
        result.append({"serial": serial, "x": float(x), "y": float(y)})
    return result


def run(
    geojson_data: Dict,
    onts,
    scale: Optional[float],
    params: Optional[SimulationParams] = None,
    force_engine: Optional[str] = None,
) -> Dict:
    """Ejecuta la simulación de propagación de señal.

    Args:
        geojson_data: GeoJSON de la planta (coordenadas en píxeles).
        onts: lista de ONT (modelos o dicts) con ``serial``, ``x``, ``y``.
        scale: metros por píxel.
        params: parámetros de simulación (usa los por defecto si es ``None``).
        force_engine: ``"sionna"`` o ``"analytical"`` para forzar un motor
            (útil en tests). ``None`` = auto.

    Returns:
        Diccionario con ``heatmapData``, ``geoJsonData``, ``onts``,
        ``channelAllocation`` y metadatos.
    """
    params = params or SimulationParams()
    ont_dicts = _ont_list(onts)
    if not ont_dicts:
        raise ValueError("No hay ONT con posición válida para simular.")

    geom = geometry.parse_geojson(geojson_data, scale)
    onts_m = [(o["x"] * geom.scale, o["y"] * geom.scale) for o in ont_dicts]

    # Selección de motor.
    use_sionna = (force_engine == "sionna") or (force_engine is None and sionna_engine.is_available())
    if force_engine == "analytical":
        use_sionna = False

    engine_name = "sionna"
    if use_sionna:
        try:
            xs_m, ys_m, rss_dbm = sionna_engine.compute_radio_map(geom, onts_m, params)
        except Exception:  # pragma: no cover - depende del entorno (GPU/escena)
            logger.exception("Sionna RT falló; usando el modelo analítico multi-pared.")
            use_sionna = False

    if not use_sionna:
        engine_name = "analytical"
        if force_engine != "analytical":
            logger.warning(
                "Sionna RT no disponible: usando el modelo analítico multi-pared "
                "(sin multitrayecto). Instala 'sionna-rt' para el motor de ray tracing."
            )
        xs_m, ys_m, rss_dbm = analytical_engine.compute_radio_map(geom, onts_m, params)

    # Construir el heatmap en coordenadas de píxel (espacio del GeoJSON/frontend).
    rss_dbm = np.clip(rss_dbm, -120.0, 0.0)
    heatmap: List[Dict] = []
    for iy, y_m in enumerate(ys_m):
        for ix, x_m in enumerate(xs_m):
            lng, lat = geom.to_pixels(float(x_m), float(y_m))
            heatmap.append({"lng": lng, "lat": lat, "value": float(rss_dbm[iy, ix])})

    finite = rss_dbm[np.isfinite(rss_dbm)]
    value_range = [float(finite.min()), float(finite.max())] if finite.size else [-120.0, 0.0]

    channel_allocation = channels.allocate_channels(ont_dicts, scale)

    return {
        "engine": engine_name,
        "heatmapData": heatmap,
        "cellSize": params.resolution_m / geom.scale,   # tamaño de celda en píxeles
        "valueRange": value_range,
        "geoJsonData": geojson_data,
        "onts": [{"serial": o["serial"], "name": o["serial"], "x": o["x"], "y": o["y"]}
                 for o in ont_dicts],
        "channelAllocation": channel_allocation,
        "meta": {
            "frequencyHz": params.frequency_hz,
            "txPowerDbm": params.tx_power_dbm,
            "resolutionM": params.resolution_m,
            "scale": geom.scale,
            "numOnts": len(ont_dicts),
        },
    }
