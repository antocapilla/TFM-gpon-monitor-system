import math
import matplotlib.pyplot as plt
import numpy as np

# Clase para representar un segmento
class Segment:
    def __init__(self, origin, direction, length, thickness, dielectric):
        self.origin = origin
        self.direction = direction
        self.length = length
        self.thickness = thickness
        self.dielectric = dielectric

# Función para reorganizar los segmentos en líneas
def reorganize_segments(segments):
    lines = []
    for segment in segments:
        added = False
        for line in lines:
            if line.direction == segment.direction and line.origin[1] == segment.origin[1]:
                line.length = max(line.length, segment.origin[0] + segment.length)
                added = True
                break
        if not added:
            lines.append(segment)
    return lines

# Función para calcular el ángulo de incidencia
def calculate_incident_angle(ray_direction, segment_direction):
    dot_product = ray_direction[0] * segment_direction[0] + ray_direction[1] * segment_direction[1]
    ray_mag = math.sqrt(ray_direction[0]**2 + ray_direction[1]**2)
    segment_mag = math.sqrt(segment_direction[0]**2 + segment_direction[1]**2)
    incident_angle = math.acos(dot_product / (ray_mag * segment_mag))
    return incident_angle

# Función para trazar un rayo
def trace_ray(origin, direction, segments, max_reflections, max_refractions, ray_coordinates):
    if max_reflections <= 0 and max_refractions <= 0:
        return

    ray_coordinates.append(origin)

    nearest_intersection = None
    nearest_segment = None

    for segment in segments:
        # Determinar la intersección con el segmento
        denom = (direction[0] * segment.direction[1] - direction[1] * segment.direction[0])
        if abs(denom) < 1e-6:
            continue
        t = (segment.direction[1] * (segment.origin[0] - origin[0]) - 
             segment.direction[0] * (segment.origin[1] - origin[1])) / denom
        u = (direction[1] * (segment.origin[0] - origin[0]) - 
             direction[0] * (segment.origin[1] - origin[1])) / denom
        if 0 <= t and 0 <= u <= segment.length:
            intersection = (origin[0] + t * direction[0], origin[1] + t * direction[1])
            if nearest_intersection is None or t < nearest_intersection[0]:
                nearest_intersection = (t, intersection)
                nearest_segment = segment

    if nearest_intersection is not None:
        ray_coordinates.append(nearest_intersection[1])

        # Calcular el ángulo de incidencia
        incident_angle = calculate_incident_angle(direction, nearest_segment.direction)

        # Calcular los campos eléctricos reflejado y refractado
        # ...

        # Trazar los rayos reflejado y refractado recursivamente
        if max_reflections > 0:
            reflected_direction = (direction[0] - 2 * math.cos(incident_angle) * nearest_segment.direction[0],
                                    direction[1] - 2 * math.cos(incident_angle) * nearest_segment.direction[1])
            trace_ray(nearest_intersection[1], reflected_direction, segments, max_reflections - 1, max_refractions, ray_coordinates)

        if max_refractions > 0:
            refracted_direction = (direction[0] * nearest_segment.dielectric, direction[1] * nearest_segment.dielectric)
            trace_ray(nearest_intersection[1], refracted_direction, segments, max_reflections, max_refractions - 1, ray_coordinates)

# Función principal
def main():
    # Definir los segmentos en el entorno indoor
    segments = [
        Segment((1, 1), (1, 0), 8, 0.2, 3.25),  # Pared horizontal inferior
        Segment((1, 1), (0, 1), 4, 0.2, 3.25),  # Pared vertical izquierda
        Segment((9, 1), (0, 1), 4, 0.2, 3.25),  # Pared vertical derecha
        Segment((1, 5), (1, 0), 8, 0.2, 3.25),  # Pared horizontal superior
        Segment((5, 2), (5, 4), 8, 0.2, 3.25),  # Pared vertical#
    ]

    # Trazar el rayo desde el transmisor hasta el receptor
    transmitter = (2, 2)
    receiver = (8, 4)

    # Direccion de prueba
    direction = (receiver[0] - transmitter[0], receiver[1] - transmitter[1])
    direction_norm = math.sqrt(direction[0]**2 + direction[1]**2)
    direction = (direction[0] / direction_norm, direction[1] / direction_norm)

    max_reflections = 5
    max_refractions = 3
    ray_coordinates = []
    trace_ray(transmitter, direction, segments, max_reflections, max_refractions, ray_coordinates)

    # Visualización
    fig, ax = plt.subplots()

    # Dibujar segmentos
    for segment in segments:
        x = [segment.origin[0], segment.origin[0] + segment.length * segment.direction[0]]
        y = [segment.origin[1], segment.origin[1] + segment.length * segment.direction[1]]
        ax.plot(x, y, 'k-', linewidth=2)

    # Dibujar rayos
    ray_coordinates = list(ray_coordinates)
    for i in range(len(ray_coordinates) - 1):
        x = [ray_coordinates[i][0], ray_coordinates[i+1][0]]
        y = [ray_coordinates[i][1], ray_coordinates[i+1][1]]
        ax.plot(x, y, 'r-', linewidth=1)

    # Dibujar transmisor y receptor
    ax.plot(transmitter[0], transmitter[1], 'ro', label='Transmisor')
    ax.plot(receiver[0], receiver[1], 'bo', label='Receptor')

    # Configurar límites y etiquetas de los ejes
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 6)
    ax.set_xlabel('Eje X')
    ax.set_ylabel('Eje Y')
    ax.set_title('Trazado de Rayos')
    ax.legend()

    # Mostrar la gráfica
    plt.show()
if __name__ == "__main__":
    main()
