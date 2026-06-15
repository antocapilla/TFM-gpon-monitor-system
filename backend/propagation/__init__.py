"""Paquete de simulación de propagación de señal RF para plantas de edificio.

Motor principal: Sionna RT (ray tracing diferenciable, GPU). Respaldo: modelo
analítico multi-pared (COST-231 / ITU-R P.1238). Incluye además la asignación
de canales WiFi por coloreo de grafos.
"""
from .engine import run
from .params import SimulationParams
from . import channels

__all__ = ["run", "SimulationParams", "channels"]
