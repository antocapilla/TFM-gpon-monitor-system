"""Construcción de una escena Mitsuba/Sionna RT a partir de la geometría 2D.

Las paredes 2D se "extruyen" verticalmente hasta la altura de techo para obtener
una escena 3D. Se usan shapes ``rectangle`` integrados de Mitsuba (no hace falta
generar mallas PLY): cada pared es un rectángulo vertical y el suelo/techo son
rectángulos horizontales. El material radio se asigna vía BSDF
``itu-radio-material``, siguiendo la convención de las escenas de Sionna RT.
"""
from __future__ import annotations

from typing import List

import numpy as np

from .geometry import FloorGeometry, WallSegment


def _matrix_str(m: np.ndarray) -> str:
    return " ".join(str(float(v)) for v in m.flatten())


def _wall_transform(wall: WallSegment, height: float) -> np.ndarray:
    """Matriz 4x4 que coloca un ``rectangle`` unitario como pared vertical.

    El rectángulo local ocupa [-1,1]x[-1,1] en el plano XY (normal +Z). Lo
    mapeamos a una pared cuyo eje horizontal sigue la dirección de la pared y
    cuyo eje vertical es Z.
    """
    p1 = np.array(wall.p1, dtype=float)
    p2 = np.array(wall.p2, dtype=float)
    direction = p2 - p1
    length = np.linalg.norm(direction)
    t = direction / length                  # tangente horizontal (eje X local)
    n = np.array([t[1], -t[0]])             # normal horizontal (eje Z local)
    center = (p1 + p2) / 2.0
    return np.array([
        [t[0] * length / 2.0, 0.0,            n[0], center[0]],
        [t[1] * length / 2.0, 0.0,            n[1], center[1]],
        [0.0,                 height / 2.0,   0.0,  height / 2.0],
        [0.0,                 0.0,            0.0,  1.0],
    ])


def _slab_transform(bounds, z: float) -> np.ndarray:
    """Matriz para un ``rectangle`` horizontal (suelo/techo) a la cota ``z``."""
    min_x, min_y, max_x, max_y = bounds
    return np.array([
        [(max_x - min_x) / 2.0, 0.0,                   0.0, (min_x + max_x) / 2.0],
        [0.0,                   (max_y - min_y) / 2.0, 0.0, (min_y + max_y) / 2.0],
        [0.0,                   0.0,                   1.0, z],
        [0.0,                   0.0,                   0.0, 1.0],
    ])


def _shape_xml(shape_id: str, transform: np.ndarray, bsdf_id: str) -> str:
    return (
        f'<shape type="rectangle" id="{shape_id}">'
        f'<transform name="to_world"><matrix value="{_matrix_str(transform)}"/></transform>'
        f'<ref id="{bsdf_id}" name="bsdf"/>'
        f'</shape>'
    )


def build_scene_xml(
    geom: FloorGeometry,
    wall_height: float = 2.7,
    wall_thickness: float = 0.1,
    floor_material: str = "concrete",
) -> str:
    """Genera el XML de la escena Mitsuba lista para ``load_scene_from_string``."""
    # BSDFs: un material radio ITU por cada tipo presente + suelo/techo.
    itu_types = {floor_material}
    for wall in geom.walls:
        itu_types.add(wall.material.sionna_name.replace("itu_", ""))

    bsdfs: List[str] = []
    for itu_type in sorted(itu_types):
        bsdfs.append(
            f'<bsdf type="itu-radio-material" id="{itu_type}">'
            f'<string name="type" value="{itu_type}"/>'
            f'<float name="thickness" value="{wall_thickness}"/>'
            f'</bsdf>'
        )

    shapes: List[str] = []
    for i, wall in enumerate(geom.walls):
        bsdf_id = wall.material.sionna_name.replace("itu_", "")
        shapes.append(_shape_xml(f"wall-{i}", _wall_transform(wall, wall_height), bsdf_id))

    # Suelo y techo cubriendo todo el bounding box de la planta.
    shapes.append(_shape_xml("floor", _slab_transform(geom.bounds_m, 0.0), floor_material))
    shapes.append(_shape_xml("ceiling", _slab_transform(geom.bounds_m, wall_height), floor_material))

    return (
        '<scene version="2.1.0">'
        + "".join(bsdfs)
        + "".join(shapes)
        + "</scene>"
    )
