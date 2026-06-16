"""Motor de propagación basado en Sionna RT (ray tracing diferenciable).

Construye una escena 3D a partir de la planta, coloca un transmisor por cada ONT
y calcula un *radio map* (mapa de cobertura) con :class:`RadioMapSolver`. Devuelve
una rejilla de RSS combinado (mejor servidor) en dBm sobre coordenadas en metros.

Sionna RT es una dependencia pesada (Mitsuba 3 + Dr.Jit + TensorFlow/PyTorch) y
se beneficia mucho de GPU. Si no está instalado, :func:`is_available` devuelve
``False`` y el orquestador recurre al modelo analítico.
"""
from __future__ import annotations

import importlib.util
from typing import List, Tuple

import numpy as np

from .geometry import FloorGeometry
from .params import SimulationParams
from . import scene_builder


def is_available() -> bool:
    """¿Está instalado Sionna RT? (sin importar la librería pesada)."""
    return importlib.util.find_spec("sionna.rt") is not None


def compute_radio_map(
    geom: FloorGeometry,
    onts_m: List[Tuple[float, float]],
    params: SimulationParams,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calcula el mapa de cobertura con Sionna RT.

    Args:
        geom: geometría de la planta (metros).
        onts_m: posiciones (x, y) de los ONT en metros.
        params: parámetros de simulación.

    Returns:
        ``(xs_m, ys_m, rss_dbm)`` donde ``xs_m``/``ys_m`` son las coordenadas X/Y
        (metros) de los centros de celda y ``rss_dbm`` es la matriz [ny, nx] de
        nivel de señal del mejor servidor en dBm.
    """
    from sionna.rt import (
        load_scene_from_string,
        PlanarArray,
        Transmitter,
        RadioMapSolver,
    )

    xml = scene_builder.build_scene_xml(
        geom,
        wall_height=params.wall_height,
        wall_thickness=params.wall_thickness,
    )
    scene = load_scene_from_string(xml)
    scene.frequency = params.frequency_hz

    # Antenas isotrópicas verticales para un mapa de cobertura agnóstico al modelo.
    scene.tx_array = PlanarArray(num_rows=1, num_cols=1, pattern="iso", polarization="V")
    scene.rx_array = PlanarArray(num_rows=1, num_cols=1, pattern="iso", polarization="V")

    for i, (x, y) in enumerate(onts_m):
        scene.add(Transmitter(
            name=f"ont-{i}",
            position=[float(x), float(y), params.tx_height],
            power_dbm=params.tx_power_dbm,
        ))

    min_x, min_y, max_x, max_y = geom.bounds_m
    center = [(min_x + max_x) / 2.0, (min_y + max_y) / 2.0, params.rx_height]
    size = [max(max_x - min_x, params.resolution_m),
            max(max_y - min_y, params.resolution_m)]

    solver = RadioMapSolver()
    radio_map = solver(
        scene,
        center=center,
        orientation=[0.0, 0.0, 0.0],
        size=size,
        cell_size=[params.resolution_m, params.resolution_m],
        samples_per_tx=params.samples_per_tx,
        max_depth=params.max_depth,
        refraction=params.refraction,
        diffraction=params.diffraction,
    )

    cell_centers = np.array(radio_map.cell_centers)   # [ny, nx, 3] en metros
    rss = np.array(radio_map.rss)                     # [num_tx, ny, nx] en watts

    # Mejor servidor: la potencia recibida es la del ONT más fuerte en cada celda.
    best_rss_w = rss.max(axis=0)
    with np.errstate(divide="ignore"):
        rss_dbm = 10.0 * np.log10(best_rss_w) + 30.0
    rss_dbm = np.where(np.isfinite(rss_dbm), rss_dbm, -120.0)

    xs_m = cell_centers[0, :, 0]
    ys_m = cell_centers[:, 0, 1]
    return xs_m, ys_m, rss_dbm
