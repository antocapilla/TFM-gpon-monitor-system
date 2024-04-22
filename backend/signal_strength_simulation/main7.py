import numpy as np
import matplotlib.pyplot as plt

# Definir los parámetros del sistema
n1 = 1.0  # Índice de refracción del medio 1
n2 = 1.5  # Índice de refracción del medio 2

# Definir el punto fuente y los obstáculos
source = np.array([0, 0])  # Coordenadas del punto fuente
obstacles = [
    {'center': np.array([5, 5]), 'radius': 2},
    {'center': np.array([10, -3]), 'radius': 1.5}
]

# Definir los ángulos de los rayos
angles = np.linspace(0, 2*np.pi, 100)

# Crear la figura y los ejes
fig, ax = plt.subplots()

# Dibujar los obstáculos
for obstacle in obstacles:
    circle = plt.Circle(obstacle['center'], obstacle['radius'], fill=False)
    ax.add_artist(circle)

# Lanzar los rayos y calcular las refracciones
for angle in angles:
    # Definir el vector de dirección del rayo
    direction = np.array([np.cos(angle), np.sin(angle)])
    
    # Propagar el rayo hasta que salga del rango de ploteo
    ray = [source]
    current_point = source
    while True:
        # Encontrar el obstáculo más cercano en la dirección del rayo
        min_distance = float('inf')
        closest_obstacle = None
        for obstacle in obstacles:
            # Calcular la distancia y el punto de intersección con el obstáculo
            oc = current_point - obstacle['center']
            a = np.dot(direction, direction)
            b = 2 * np.dot(oc, direction)
            c = np.dot(oc, oc) - obstacle['radius']**2
            discriminant = b**2 - 4*a*c
            if discriminant >= 0:
                t = (-b - np.sqrt(discriminant)) / (2*a)
                if t > 0:
                    intersection = current_point + t * direction
                    distance = np.linalg.norm(intersection - current_point)
                    if distance < min_distance:
                        min_distance = distance
                        closest_obstacle = obstacle
        
        # Si no hay obstáculos en la dirección del rayo, propagar hasta el límite del rango de ploteo
        if closest_obstacle is None:
            limit_distance = max(abs(ax.get_xlim()[1] - current_point[0]), abs(ax.get_ylim()[1] - current_point[1]))
            limit_point = current_point + limit_distance * direction
            ray.append(limit_point)
            break
        
        # Calcular el punto de intersección con el obstáculo más cercano
        intersection = current_point + min_distance * direction
        ray.append(intersection)
        
        # Calcular el ángulo de incidencia y refracción
        normal = (intersection - closest_obstacle['center']) / closest_obstacle['radius']
        cos_theta1 = -np.dot(direction, normal)
        sin_theta2 = n1/n2 * np.sqrt(1 - cos_theta1**2)
        cos_theta2 = np.sqrt(1 - sin_theta2**2)
        
        # Calcular la nueva dirección del rayo refractado
        refracted_direction = n1/n2 * direction + (n1/n2 * cos_theta1 - cos_theta2) * normal
        direction = refracted_direction
        
        # Actualizar el punto actual
        current_point = intersection
    
    # Dibujar el rayo
    ray = np.array(ray)
    ax.plot(ray[:, 0], ray[:, 1], 'b-', linewidth=0.5)

# Dibujar el punto fuente
ax.plot(source[0], source[1], 'ro', markersize=5)

# Configurar los límites de los ejes y las etiquetas
ax.set_xlim(-10, 20)
ax.set_ylim(-10, 20)
ax.set_aspect('equal')
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_title('Lanzado de rayos desde un punto fuente')

# Mostrar la gráfica
plt.show()