import numpy as np
import matplotlib.pyplot as plt

# Definir la posición de la fuente de luz
source_pos = np.array([0.0, 0.0])

# Definir los segmentos en el plano
segments = np.array([
    [[2.0, -1.0], [2.0, 1.0]],  # Segmento vertical
    [[4.0, -1.0], [4.0, 1.0]],  # Segmento vertical
    [[-1.0, -2.0], [5.0, -2.0]],  # Segmento horizontal
])

# Definir los ángulos de los rayos
num_rays = 20
angles = np.linspace(0, 2*np.pi, num_rays)

# Definir la longitud máxima de los rayos
max_length = 10.0

# Propagar los rayos y detectar colisiones
rays = []
for angle in angles:
    direction = np.array([np.cos(angle), np.sin(angle)])
    ray = np.array([source_pos, direction])
    
    # Matriz de transferencia inicial (identidad)
    transfer_matrix = np.eye(2)
    
    # Verificar colisiones con los segmentos
    for segment in segments:
        # Calcular la intersección entre el rayo y el segmento
        v1 = segment[1] - segment[0]
        v2 = ray[0] - segment[0]
        v3 = np.array([-v1[1], v1[0]])  # Vector perpendicular a v1
        
        denom = np.dot(v3, ray[1])
        if np.abs(denom) > 1e-6:  # Evitar división por cero
            t = np.dot(v3, v2) / denom
            if 0 <= t <= max_length:
                # Hay una intersección válida
                intersection = ray[0] + t * ray[1]
                
                # Actualizar la matriz de transferencia
                transfer_matrix = np.array([[1, t], [0, 1]]) @ transfer_matrix
                
                # Actualizar el rayo
                ray[0] = intersection
                ray[1] = ray[1]
    
    # Aplicar la matriz de transferencia final al rayo
    ray_end = transfer_matrix @ np.array([0, 1])
    ray_end = ray[0] + ray_end[1] * ray[1]
    rays.append(np.array([ray[0], ray_end]))

# Graficar los rayos y los segmentos
plt.figure()
plt.plot(source_pos[0], source_pos[1], 'ro')  # Fuente de luz

for segment in segments:
    plt.plot(segment[:, 0], segment[:, 1], 'k-')

for ray in rays:
    plt.plot(ray[:, 0], ray[:, 1], 'b-', linewidth=0.5)

plt.xlabel('X')
plt.ylabel('Y')
plt.title('Propagación de rayos en 2D con colisiones (matrices de transferencia)')
plt.grid(True)
plt.axis('equal')
plt.show()