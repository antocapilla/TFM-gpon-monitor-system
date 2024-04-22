import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import math

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

def trace_rays(device_pos, X, Y, obstacles):
    rays = []
    
    # Parámetros del lanzamiento de rayos
    num_rays = 360  # Número de rayos a lanzar (uno cada grado)
    max_depth = 5  # Máxima profundidad de recursión (número de reflexiones/transmisiones)
    
    # Ángulos de lanzamiento de los rayos (en radianes)
    launch_angles = [math.radians(angle) for angle in range(num_rays)]
    
    for angle in launch_angles:
        # Punto de inicio del rayo (posición del dispositivo)
        start_pos = device_pos
        
        # Dirección inicial del rayo
        direction = (math.cos(angle), math.sin(angle))
        
        # Lanzar el rayo
        ray = launch_ray(start_pos, direction, obstacles, max_depth)
        
        # Agregar el rayo a la lista de rayos
        rays.append(ray)
    
    return rays

def launch_ray(start_pos, direction, obstacles, max_depth):
    # Crear un nuevo rayo
    ray = Ray(start_pos, direction)
    
    # Verificar la intersección con obstáculos
    closest_intersection = find_closest_intersection(start_pos, direction, obstacles)
    
    if closest_intersection is not None:
        # Actualizar el punto final del rayo
        ray.end_pos = closest_intersection.point
        
        # Verificar si se alcanzó la máxima profundidad de recursión
        if max_depth > 0:
            # Calcular la nueva dirección del rayo reflejado o transmitido
            new_direction = calculate_reflected_direction(direction, closest_intersection.normal)
            
            # Lanzar un nuevo rayo desde el punto de intersección
            reflected_ray = launch_ray(closest_intersection.point, new_direction, obstacles, max_depth - 1)
            
            # Agregar el rayo reflejado o transmitido al rayo actual
            ray.add_child(reflected_ray)
    
    return ray

def find_closest_intersection(start_pos, direction, obstacles):
    closest_intersection = None
    min_distance = float('inf')
    
    for obstacle in obstacles:
        intersection = intersect_ray_obstacle(start_pos, direction, obstacle)
        
        if intersection is not None:
            distance = calculate_distance(start_pos, intersection.point)
            
            if distance < min_distance:
                min_distance = distance
                closest_intersection = intersection
    
    return closest_intersection

def intersect_ray_obstacle(start_pos, direction, obstacle):
    # Implementación del cálculo de intersección entre un rayo y un obstáculo utilizando la recta paramétrica y la ecuación del plano
    
    # Obtener los vértices del obstáculo
    vertices = obstacle['vertices']
    
    # Calcular el vector normal del plano del obstáculo
    v1 = (vertices[1][0] - vertices[0][0], vertices[1][1] - vertices[0][1])
    v2 = (vertices[2][0] - vertices[0][0], vertices[2][1] - vertices[0][1])
    normal = (v1[1] * v2[0] - v1[0] * v2[1], v1[0] * v2[1] - v1[1] * v2[0])
    
    # Calcular el parámetro t de la intersección utilizando la ecuación del plano
    denominator = normal[0] * direction[0] + normal[1] * direction[1]
    if denominator == 0:
        return None
    
    t = ((vertices[0][0] - start_pos[0]) * normal[0] + (vertices[0][1] - start_pos[1]) * normal[1]) / denominator
    
    # Verificar si la intersección está dentro de los límites del obstáculo
    if t < 0:
        return None
    
    intersection_point = (start_pos[0] + t * direction[0], start_pos[1] + t * direction[1])
    
    if not is_point_inside_obstacle(intersection_point, vertices):
        return None
    
    return Intersection(intersection_point, normal)

def is_point_inside_obstacle(point, vertices):
    # Verificar si un punto está dentro de un obstáculo utilizando el algoritmo de ray casting
    
    inside = False
    for i in range(len(vertices)):
        j = (i + 1) % len(vertices)
        if ((vertices[i][1] > point[1]) != (vertices[j][1] > point[1])) and (point[0] < (vertices[j][0] - vertices[i][0]) * (point[1] - vertices[i][1]) / (vertices[j][1] - vertices[i][1]) + vertices[i][0]):
            inside = not inside
    
    return inside

def calculate_reflected_direction(incident_direction, surface_normal):
    # Calcular la dirección del rayo reflejado utilizando la ley de reflexión
    
    dot_product = incident_direction[0] * surface_normal[0] + incident_direction[1] * surface_normal[1]
    reflected_direction = (incident_direction[0] - 2 * dot_product * surface_normal[0],
                           incident_direction[1] - 2 * dot_product * surface_normal[1])
    
    return reflected_direction

def calculate_distance(point1, point2):
    # Calcular la distancia euclidiana entre dos puntos
    
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    distance = math.sqrt(dx**2 + dy**2)
    
    return distance

class Ray:
    def __init__(self, start_pos, direction):
        self.start_pos = start_pos
        self.end_pos = None
        self.direction = direction
        self.children = []
    
    def add_child(self, child_ray):
        self.children.append(child_ray)

class Intersection:
    def __init__(self, point, normal):
        self.point = point
        self.normal = normal

def calculate_ht(X, rays, obstacles):
    ht = np.zeros_like(X, dtype=complex)
    for ray in rays:
        # Calcular el retardo del rayo
        delay = calculate_delay(ray)
        
        # Calcular los coeficientes de reflexión y transmisión
        reflection_coefs = calculate_reflection_coefficients(ray, obstacles)
        transmission_coefs = calculate_transmission_coefficients(ray, obstacles)
        
        # Calcular la contribución del rayo a h(t)
        ht += calculate_ray_contribution(ray, reflection_coefs, transmission_coefs, delay, frequency)

def calculate_delay(ray):
    # Calcular el retardo del rayo basado en la longitud del camino
    # ...
    return delay

def calculate_reflection_coefficients(ray, obstacles):
    # Calcular los coeficientes de reflexión para cada pared en la que se refleja el rayo
    # Utilizar las ecuaciones de Fresnel según las propiedades de los materiales
    # ...
    return reflection_coefs

def calculate_transmission_coefficients(ray, obstacles):
    # Calcular los coeficientes de transmisión para cada pared que atraviesa el rayo
    # Utilizar las ecuaciones de Fresnel según las propiedades de los materiales
    # ...
    return transmission_coefs

def calculate_ray_contribution(ray, reflection_coefs, transmission_coefs, delay, frequency):
    # Calcular la contribución del rayo a h(t) según la ecuación (5) de la ITU
    omega = 2 * np.pi * frequency  # Frecuencia angular
    
    # Producto de los coeficientes de reflexión
    reflection_prod = np.prod(reflection_coefs)
    
    # Producto de los coeficientes de transmisión  
    transmission_prod = np.prod(transmission_coefs)
    
    # Factor de atenuación debido a la longitud del camino
    path_attenuation = 1 / ray.path_length
    
    # Exponencial compleja del retardo de fase
    phase_delay = cmath.exp(-1j * omega * delay)
    
    # Contribución completa del rayo a h(t)
    ray_contribution = (reflection_prod * transmission_prod * path_attenuation * 
                        phase_delay * np.eye(1, dtype=complex))
    
    return ray_contribution

def calculate_rx_power_from_ht(ht, tx_power):
    # Calcular la potencia recibida a partir de la respuesta al impulso h(t)
    # ...
    return rx_power

# Calculo complejo
def calculate_rx_power(X, Y, device_pos, frequency, tx_power, obstacles):
    wavelength = 3e8 / frequency  # Longitud de onda en metros
    
    # Paso 1: Trazar rayos desde el transmisor hasta el receptor
    rays = trace_rays(device_pos, X, Y, obstacles)
    
    # Paso 2: Calcular la respuesta al impulso h(t)
    ht = calculate_ht(X, rays, obstacles)
    
    # Paso 3: Calcular la potencia recibida a partir de h(t)
    rx_power = calculate_rx_power_from_ht(ht, tx_power)
    
    return rx_power

# Calculo simplificado
def calculate_rx_power1(X, Y, device_pos, frequency, tx_power, obstacles):
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

def calculate_total_rx_power(X, Y, device_positions, frequency, tx_power, obstacles):
    rx_power_total = np.zeros_like(X)
    for pos in device_positions:
        rx_power = calculate_rx_power1(X, Y, pos, frequency, tx_power, obstacles)
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

def simulate_rf_signal(width, height, resolution, device_positions, frequency, tx_power, obstacles):
    x = np.linspace(0, width, resolution)
    y = np.linspace(0, height, resolution)
    X, Y = np.meshgrid(x, y)
    rx_power_total_dbm = calculate_total_rx_power(X, Y, device_positions, frequency, tx_power, obstacles)
    create_heatmap(X, Y, rx_power_total_dbm, device_positions, obstacles)

# Ejecutar la simulación
simulate_rf_signal(width, height, resolution, device_positions, frequency, tx_power, obstacles)