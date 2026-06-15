"""Catálogo de materiales de construcción para la simulación de propagación.

Cada material define:

* ``sionna``: nombre del material radio ITU equivalente en Sionna RT
  (ver ITU-R P.2040 / catálogo ``itu_*`` de Sionna). Se usa cuando el motor
  de ray tracing está disponible.
* ``loss_db``: atenuación de penetración típica (en dB) al atravesar una pared
  de ese material, por banda. Se usa en el modelo multi-pared analítico
  (COST-231 / ITU-R P.1238) cuando Sionna no está disponible.

Los valores de pérdida son representativos de la literatura para tabiques
interiores a 2.4 GHz y 5 GHz. No pretenden ser exactos para cada construcción,
sino dar un orden de magnitud coherente y configurable.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Material:
    key: str
    sionna_name: str       # material radio ITU en Sionna RT
    loss_db_2_4: float     # atenuación por pared a 2.4 GHz [dB]
    loss_db_5: float       # atenuación por pared a 5 GHz [dB]


# Catálogo. Las claves son las que pueden aparecer en
# ``feature.properties.material`` del GeoJSON.
CATALOG: Dict[str, Material] = {
    "concrete":     Material("concrete",     "itu_concrete",     12.0, 16.0),
    "brick":        Material("brick",        "itu_brick",         8.0, 11.0),
    "plasterboard": Material("plasterboard", "itu_plasterboard",  3.0,  4.0),
    "drywall":      Material("drywall",      "itu_plasterboard",  3.0,  4.0),
    "wood":         Material("wood",         "itu_wood",          4.0,  6.0),
    "glass":        Material("glass",        "itu_glass",         3.0,  5.0),
    "metal":        Material("metal",        "itu_metal",        25.0, 30.0),
}

# Material por defecto cuando el GeoJSON no especifica nada: tabique de obra.
DEFAULT_MATERIAL_KEY = "brick"


def resolve(material_key: str | None) -> Material:
    """Devuelve el :class:`Material` para una clave, con fallback al defecto."""
    if material_key:
        mat = CATALOG.get(material_key.lower())
        if mat is not None:
            return mat
    return CATALOG[DEFAULT_MATERIAL_KEY]


def loss_for(material: Material, frequency_hz: float) -> float:
    """Atenuación por pared para la frecuencia dada (interpola por banda)."""
    return material.loss_db_5 if frequency_hz >= 4.0e9 else material.loss_db_2_4
