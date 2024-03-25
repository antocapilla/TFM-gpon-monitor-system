import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches

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
obstacle_attenuation = 10  # Atenuación por obstáculo en dB (usar solo como ejemplo, realmente se calcularía basado en las propiedades)

def calculate_rx_power(X, Y, device_pos, frequency, tx_power, obstacles, obstacle_attenuation):
    wavelength = 3e8 / frequency  # Longitud de onda en metros
    distance = np.sqrt((X - device_pos[0])**2 + (Y - device_pos[1])**2)
    
    # Paso 1: Trazar rayos desde el transmisor hasta el receptor
    # Implementar el algoritmo de trazado de rayos
    
    # Paso 2: Calcular las pérdidas por reflexión para cada rayo
    # Implementar el cálculo de pérdidas por reflexión
    
    # Paso 3: Calcular las pérdidas por transmisión para cada rayo
    # Implementar el cálculo de pérdidas por transmisión
    
    # Paso 4: Calcular las pérdidas por difracción para cada rayo (opcional)
    # Implementar el cálculo de pérdidas por difracción
    
    # Paso 5: Calcular la atenuación total para cada rayo
    # Sumar las pérdidas por reflexión, transmisión y difracción
    
    # Paso 6: Calcular la contribución de cada rayo en el receptor
    # Considerar la amplitud y fase de cada rayo
    
    # Calcular la pérdida de trayectoria log-distance (solo pérdida por espacio libre)
    path_loss = 20 * np.log10(4 * np.pi * distance / wavelength)
    rx_power = tx_power - path_loss
    
    return rx_power

def calculate_total_rx_power(X, Y, device_positions, frequency, tx_power, obstacles, obstacle_attenuation):
    rx_power_total = np.zeros_like(X)
    for pos in device_positions:
        rx_power = calculate_rx_power(X, Y, pos, frequency, tx_power, obstacles, obstacle_attenuation)
        rx_power_total += 10**(rx_power / 10)  # Sumar las potencias en escala lineal
    rx_power_total_dbm = 10 * np.log10(rx_power_total)  # Convertir a dBm
    return rx_power_total_dbm

def create_heatmap(X, Y, rx_power_total_dbm, device_positions, obstacles):
    plt.figure(figsize=(10, 8))
    contour = plt.contourf(X, Y, rx_power_total_dbm, cmap='coolwarm')
    plt.colorbar(contour, label='Potencia recibida total (dBm)')
    for i, pos in enumerate(device_positions):
        plt.plot(pos[0], pos[1], 'ro', markersize=10, label=f'Dispositivo Wi-Fi {i+1}')
    for obstacle in obstacles:
        vertices = obstacle['vertices']
        poly = patches.Polygon(vertices, fill=False, color='gray', alpha=0.7)
        plt.gca().add_patch(poly)
    plt.xlabel('Distancia (m)')
    plt.ylabel('Distancia (m)')
    plt.title('Mapa de contorno de la señal de RF con obstáculos')
    plt.legend()
    plt.tight_layout()
    plt.show()

def simulate_rf_signal(width, height, resolution, device_positions, frequency, tx_power, obstacles, obstacle_attenuation):
    x = np.linspace(0, width, resolution)
    y = np.linspace(0, height, resolution)
    X, Y = np.meshgrid(x, y)
    rx_power_total_dbm = calculate_total_rx_power(X, Y, device_positions, frequency, tx_power, obstacles, obstacle_attenuation)
    create_heatmap(X, Y, rx_power_total_dbm, device_positions, obstacles)

# Ejecutar la simulación
simulate_rf_signal(width, height, resolution, device_positions, frequency, tx_power, obstacles, obstacle_attenuation)