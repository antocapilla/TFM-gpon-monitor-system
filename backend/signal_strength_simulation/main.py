import numpy as np
from power_calculation import calculate_total_rx_power
from visualization import create_heatmap
from ray_tracing import simulate_ray_to_point
from visualization import visualize_rays

# Parámetros de simulación
width = 20  # Ancho en metros
height = 20  # Alto en metros
resolution = 200  # Resolución del mapa
device_positions = [(5, 5), (10, 15), (15, 8)]  # Posiciones (x, y) en metros
frequency = 2.4e9  # Frecuencia en Hz (2.4 GHz)
tx_power = 20  # Potencia de transmisión en dBm

# Obstáculos
obstacles = [
    { # Paredes exteriores (simulado como un obstáculo grande)
        'vertices': [(1, 1), (19, 1), (19, 19), (1, 19)],
        'permittivity': 4,
        'conductivity': 0.02,
        'roughness': 0.1,
        'attenuation': 10
    },
    { # Escritorio 1
        'vertices': [(5, 3), (7, 3), (7, 4), (5, 4)],
        'permittivity': 2.5,
        'conductivity': 0.01,
        'roughness': 0.05,
        'attenuation': 10
    },
    { # Escritorio 2
        'vertices': [(12, 14), (14, 14), (14, 15), (12, 15)],
        'permittivity': 2.5,
        'conductivity': 0.01,
        'roughness': 0.05,
        'attenuation': 10
    },
    { # Partición
        'vertices': [(10, 6), (10, 10), (11, 10), (11, 6)],
        'permittivity': 3,
        'conductivity': 0.015,
        'roughness': 0.05,
        'attenuation': 10
    }
]

def simulate_rf_signal(width, height, resolution, device_positions, frequency, tx_power, obstacles):
    x = np.linspace(0, width, resolution)
    y = np.linspace(0, height, resolution)
    X, Y = np.meshgrid(x, y)
    rx_power_total_dbm = calculate_total_rx_power(X, Y, device_positions, frequency, tx_power, obstacles)
    create_heatmap(X, Y, rx_power_total_dbm, device_positions, obstacles)

# Ejecutar la simulación
# simulate_rf_signal(width, height, resolution, device_positions, frequency, tx_power, obstacles)



start_pos = (5, 5)  # Ejemplo de posición inicial
end_pos = (10, 8)  # Ejemplo de posición final
max_depth = 5  # Ejemplo de profundidad máxima de recursión

ray = simulate_ray_to_point(start_pos, end_pos, obstacles)
visualize_rays([ray], obstacles)