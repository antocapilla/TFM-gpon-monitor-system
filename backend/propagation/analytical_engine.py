"""Modelo de propagación analítico multi-pared (COST-231 MWM / ITU-R P.1238).

Sirve de respaldo (fallback) cuando Sionna RT no está disponible. Para cada
punto de la rejilla y cada ONT calcula:

    PL(dB) = PL_espacio_libre(d) + Σ atenuación_de_cada_pared_atravesada

y el RSS = Potencia_Tx − PL. Combina los ONT por "mejor servidor" (máximo RSS).

Es determinista, rápido (totalmente vectorizado en NumPy) y está respaldado por
recomendaciones ITU, aunque no modela reflexiones/multitrayecto como el ray
tracing.
"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np

from . import materials
from .geometry import FloorGeometry
from .params import SimulationParams

_C = 299_792_458.0  # velocidad de la luz [m/s]


def _wall_arrays(geom: FloorGeometry, frequency_hz: float):
    """Devuelve (C, D, losses): extremos de pared [N,2] y atenuación/pared [N] dB."""
    c = np.array([w.p1 for w in geom.walls], dtype=float)
    d = np.array([w.p2 for w in geom.walls], dtype=float)
    losses = np.array(
        [materials.loss_for(w.material, frequency_hz) for w in geom.walls],
        dtype=float,
    )
    return c, d, losses


def _cross(o, p, q):
    """Producto cruzado 2D (orientación) con broadcasting."""
    return (p[..., 0] - o[..., 0]) * (q[..., 1] - o[..., 1]) - \
           (p[..., 1] - o[..., 1]) * (q[..., 0] - o[..., 0])


def _wall_losses_per_point(origin, points, wall_c, wall_d, losses) -> np.ndarray:
    """Suma de atenuaciones de las paredes cruzadas por cada LOS origin→points.

    ``points`` es [P, 2]; ``wall_c``/``wall_d`` son [N, 2]. Devuelve [P].
    Test de intersección segmento-segmento vectorizado sobre [P, N].
    """
    a = np.asarray(origin, float)[None, None, :]   # [1,1,2]
    b = points[:, None, :]                          # [P,1,2]
    c = wall_c[None, :, :]                           # [1,N,2]
    d = wall_d[None, :, :]                           # [1,N,2]

    d1 = _cross(c, d, a)        # [1,N]
    d2 = _cross(c, d, b)        # [P,N]
    d3 = _cross(a, b, c)        # [P,N]
    d4 = _cross(a, b, d)        # [P,N]
    crosses = ((d1 * d2) < 0) & ((d3 * d4) < 0)     # [P,N]
    return crosses @ losses                          # [P]


def compute_radio_map(
    geom: FloorGeometry,
    onts_m: List[Tuple[float, float]],
    params: SimulationParams,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Calcula la rejilla de RSS (dBm) con el modelo multi-pared."""
    min_x, min_y, max_x, max_y = geom.bounds_m
    res = params.resolution_m
    xs = np.arange(min_x + res / 2.0, max_x, res)
    ys = np.arange(min_y + res / 2.0, max_y, res)
    if xs.size == 0:
        xs = np.array([(min_x + max_x) / 2.0])
    if ys.size == 0:
        ys = np.array([(min_y + max_y) / 2.0])

    grid_x, grid_y = np.meshgrid(xs, ys)             # [ny, nx]
    points = np.column_stack((grid_x.ravel(), grid_y.ravel()))  # [P, 2]

    wall_c, wall_d, wall_losses = _wall_arrays(geom, params.frequency_hz)
    wavelength = _C / params.frequency_hz
    dz = params.tx_height - params.rx_height

    best = np.full(points.shape[0], -np.inf)
    for ont in onts_m:
        ont = np.asarray(ont, float)
        horiz = np.hypot(points[:, 0] - ont[0], points[:, 1] - ont[1])
        dist = np.maximum(np.sqrt(horiz ** 2 + dz ** 2), 0.1)

        fspl = 20.0 * np.log10(4.0 * np.pi * dist / wavelength)
        wall_loss = _wall_losses_per_point(ont, points, wall_c, wall_d, wall_losses)

        rx = params.tx_power_dbm - fspl - wall_loss
        best = np.maximum(best, rx)

    return xs, ys, best.reshape(grid_x.shape)
