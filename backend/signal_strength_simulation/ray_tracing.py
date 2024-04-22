import math
import matplotlib.pyplot as plt
import numpy as np

class Ray:
    def __init__(self, start_pos, direction):
        self.start_pos = start_pos
        self.end_pos = None
        self.direction = direction
    
    def __str__(self):
        return f"Ray(start={self.start_pos}, end={self.end_pos}, direction={self.direction})"

class Intersection:
    def __init__(self, point, normal):
        self.point = point
        self.normal = normal

def simulate_ray_to_point(start_pos, end_pos, obstacles):
    direction = calculate_direction(start_pos, end_pos)
    ray = Ray(start_pos, direction)
    intersection = find_closest_intersection(start_pos, direction, obstacles)
    
    if intersection is not None:
        ray.end_pos = intersection.point
    else:
        ray.end_pos = end_pos
    
    return ray

def calculate_direction(start_pos, end_pos):
    direction = (end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
    magnitude = math.sqrt(direction[0]**2 + direction[1]**2)
    if magnitude == 0:
        return (0, 0)
    normalized_direction = (direction[0] / magnitude, direction[1] / magnitude)
    return normalized_direction

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
    # Obtener los vértices del obstáculo
    vertices = obstacle['vertices']
    
    # Verificar si el rayo intersecta con cada arista del obstáculo
    for i in range(len(vertices)):
        j = (i + 1) % len(vertices)
        edge_start = vertices[i]
        edge_end = vertices[j]
        
        # Calcular el vector de la arista
        edge_vec = (edge_end[0] - edge_start[0], edge_end[1] - edge_start[1])
        
        # Calcular el vector normal a la arista
        edge_normal = (-edge_vec[1], edge_vec[0])
        
        # Calcular el denominador de la fórmula de intersección
        denominator = dot_product(edge_normal, direction)
        
        if denominator == 0:
            continue
        
        # Calcular el numerador de la fórmula de intersección
        numerator = dot_product(edge_normal, (start_pos[0] - edge_start[0], start_pos[1] - edge_start[1]))
        
        # Calcular el parámetro t de la intersección
        t = -numerator / denominator
        
        if t < 0:
            continue
        
        # Calcular el punto de intersección
        intersection_point = (start_pos[0] + t * direction[0], start_pos[1] + t * direction[1])
        
        # Verificar si el punto de intersección está dentro del segmento de la arista
        if is_point_on_edge(intersection_point, edge_start, edge_end):
            return Intersection(intersection_point, edge_normal)
    
    return None

def is_point_on_edge(point, edge_start, edge_end):
    # Verificar si un punto está sobre un segmento de arista
    
    # Calcular los vectores del punto a los extremos de la arista
    vec1 = (point[0] - edge_start[0], point[1] - edge_start[1])
    vec2 = (edge_end[0] - point[0], edge_end[1] - point[1])
    
    # Calcular el producto cruz de los vectores
    cross_product = vec1[0] * vec2[1] - vec1[1] * vec2[0]
    
    # Si el producto cruz es cercano a cero, el punto está sobre la arista
    return abs(cross_product) < 1e-6

def dot_product(vec1, vec2):
    return vec1[0] * vec2[0] + vec1[1] * vec2[1]

def calculate_distance(point1, point2):
    # Calcular la distancia euclidiana entre dos puntos
    
    dx = point2[0] - point1[0]
    dy = point2[1] - point1[1]
    distance = math.sqrt(dx**2 + dy**2)
    
    return distance