"""Modelo de propagación analítico multi-pared (COST-231 MWM / ITU-R P.1238).

Sirve de respaldo (fallback) cuando Sionna RT no está disponible. Para cada
punto de la rejilla y cada ONT calcula:

    PL(dB) = PL_espacio_libre(d) + Σ atenuación_de_cada_pared_atravesada

y el RSS = Potencia_Tx − PL. Combina los ONT por "mejor servidor" (máximo RSS).

Es determinista, rápido (vectorizado en NumPy) y está respaldado por
recomendaciones ITU, aunque no modela reflexiones/multitrayecto como el ray
tracing.
"""
from __future__ import annotations

from typing import List, Tuple

import numpy as np

from .geometry import FloorGeometry
from .params import SimulationParams
from . import materials

_C = 299_792_458.0  # velocidad de la luz [m/s]


def _wall_arrays(geom: FloorGeometry, frequency_hz: float):
    """Devuelve (C, D, losses) con extremos de pared y atenuación por pared [dB]."""
    c = np.array([w.p1 for w in geom.walls], dtype=float)   # [N, 2]
    d = np.array([w.p2 for w in geom.walls], dtype=float)   # [N, 2]
    losses = np.array(
        [materials.loss_for(w.material, frequency_hz) for w in geom.walls],
        dtype=float,
    )
    return c, d, losses


def _segments_cross(a, b, c, d) -> np.ndarray:
    """Test vectorizado: ¿el segmento A-B cruza cada segmento C[i]-D[i]?

    ``a``, ``b`` son puntos (2,); ``c``, ``d`` son arrays [N, 2]. Devuelve un
    booleano [N]. Usa el signo de los productos cruzados (orientación).
    """
    def cross(o, p, q):
        return (p[..., 0] - o[..., 0]) * (q[..., 1] - o[..., 1]) - \
               (p[..., 1] - o[..., 1]) * (q[..., 0] - o[..., 0])

    a = np.asarray(a, float)
    b = np.asarray(b, float)
    d1 = cross(c, d, a[None, :])
    d2 = cross(c, d, b[None, :])
    d3 = cross(a[None, :], b[None, :], c)
    d4 = cross(a[None, :], b[None, :], d)
    return ((d1 * d2) < 0) & ((d3 * d4) < 0)


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

    wall_c, wall_d, wall_losses = _wall_arrays(geom, params.frequency_hz)
    wavelength = _C / params.frequency_hz
    dz = params.tx_height - params.rx_height

    rss = np.full((ys.size, xs.size), -150.0)
    for ont in onts_m:
        ont = np.asarray(ont, float)
        for iy, y in enumerate(ys):
            for ix, x in enumerate(xs):
                point = np.array([x, y])
                d2 = np.hypot(point[0] - ont[0], point[1] - ont[1])
                dist = max(np.sqrt(d2 ** 2 + dz ** 2), 0.1)

                fspl = 20.0 * np.log10(4.0 * np.pi * dist / wavelength)
                crossed = _segments_cross(ont, point, wall_c, wall_d)
                wall_loss = float(wall_losses[crossed].sum())

                rx = params.tx_power_dbm - fspl - wall_loss
                if rx > rss[iy, ix]:
                    rss[iy, ix] = rx

    return xs, ys, rss
