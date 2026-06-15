"""Parámetros de configuración de la simulación de propagación."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SimulationParams:
    # Radio
    frequency_hz: float = 5.0e9       # banda WiFi (5 GHz por defecto)
    tx_power_dbm: float = 20.0        # EIRP típica de un AP/ONT WiFi
    # Geometría 3D (metros)
    wall_height: float = 2.7
    wall_thickness: float = 0.1
    tx_height: float = 2.5            # ONT/AP cerca del techo
    rx_height: float = 1.5           # altura del usuario
    # Rejilla del mapa de cobertura
    resolution_m: float = 0.5         # tamaño de celda del heatmap [m]
    # Ray tracing (Sionna RT)
    max_depth: int = 5                # nº máx. de interacciones por rayo
    samples_per_tx: int = 1_000_000   # rayos lanzados por transmisor
    diffraction: bool = True
    refraction: bool = True

    @property
    def is_5ghz(self) -> bool:
        return self.frequency_hz >= 4.0e9
