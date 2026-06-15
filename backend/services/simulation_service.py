"""Servicio de simulación: delega en el paquete ``propagation``.

La lógica física (ray tracing con Sionna RT / modelo analítico multi-pared y la
asignación de canales WiFi por coloreo de grafos) vive en ``propagation``. Este
servicio es una fachada fina que conecta la API con dicho paquete.
"""
from typing import List, Optional

from models.manager_model import ONTPosition
from propagation import SimulationParams, channels, run as run_propagation


class SimulationService:
    def __init__(self, params: Optional[SimulationParams] = None):
        self.params = params or SimulationParams()

    def run_simulation(self, geojson_data, onts: List[ONTPosition], scale):
        """Mapa de propagación de señal (heatmap) + asignación de canales."""
        return run_propagation(geojson_data, onts, scale, params=self.params)

    def allocate_wifi_channels(self, onts: List[ONTPosition], scale=None):
        """Asignación de canales WiFi por coloreo de grafos."""
        ont_dicts = [{"serial": o.serial, "x": o.x, "y": o.y} for o in onts]
        return channels.allocate_channels(ont_dicts, scale)
