import numpy as np
import matplotlib.pyplot as plt
import pygame
import math
import random
from abc import ABC, abstractmethod
from pyqtree import Index
from pygame.locals import *
from scipy.constants import mu_0, epsilon_0, pi
import copy
import time
import cmath
from tqdm import tqdm


# Definir constantes de colores
BLACK = (0, 0, 0)
BACKGROUND = (223, 208, 187)
RAYS = (148, 61, 44)
RAYS_2 = (204, 121, 82)

class Visualizable(ABC):
    @abstractmethod
    def visualize(self, display, scale):
        pass

class Environment(Visualizable):
    def __init__(self, dimensions, obstacles=None, materials=None):
        self.dimensions = dimensions
        self.obstacles = obstacles if obstacles else []
        self.materials = materials if materials else []

    def add_obstacle(self, obstacle):
        self.obstacles.append(obstacle)

    def visualize(self, display, scale):
        for obstacle in self.obstacles:
            obstacle.visualize(display, scale)

class Material:
    def __init__(self, permittivity, conductivity, thickness):
        self.permittivity = permittivity
        self.conductivity = conductivity
        self.thickness = thickness

class Wall(Visualizable):
    def __init__(self, start_point, end_point, material):
        self.start_point = start_point
        self.end_point = end_point
        self.material = material

        # Calcular el vector normal de la pared
        dx = end_point[0] - start_point[0]
        dy = end_point[1] - start_point[1]
        self.normal_direction = (-dy, dx)  # Vector normal perpendicular a la pared

    def visualize(self, display, scale):
        start_point_scaled = (int(self.start_point[0] * scale[0]), int(self.start_point[1] * scale[1]))
        end_point_scaled = (int(self.end_point[0] * scale[0]), int(self.end_point[1] * scale[1]))
        thickness_scaled = int(self.material.thickness * scale[0])

        pygame.draw.line(display, BLACK, start_point_scaled, end_point_scaled, 1)

class Antenna(Visualizable):
    def __init__(self, location, tx_power, radiation_pattern, frequency):
        self.location = location
        self.tx_power = tx_power
        self.radiation_pattern = radiation_pattern
        self.frequency = frequency

    def launch_rays(self, num_rays):
        rays = []
        for i in range(num_rays):
            angle = i * 2 * math.pi / num_rays  # Calcular el ángulo en radianes
            direction = (math.cos(angle), math.sin(angle))
            rays.append(Ray(self.location, direction, self.tx_power/num_rays))
        return rays

    def visualize(self, display):
        pass

class Collision:
    def __init__(self, ray, point, wall):
        self.point = point
        self.wall = wall
        self.ray = ray
    
    def __repr__(self) -> str:
        return f"Collision: Point ('{self.point}')"

class Ray(Visualizable):
    def __init__(self, start_point, direction, power=1.0, polarization="TE", ):
        self.start_point = start_point
        self.direction = direction
        self.end_point = None
        self.polarization = polarization
        self.alpha = 1 + 0j
        self.distance = 0  # Distancia total recorrida por el rayo en metros
        self.power = power
        self.path_loss = 0  # Pérdida de trayectoria acumulada
        self.path = [start_point]
        self.num_reflections = 0
        self.num_transmissions = 0
        # self.reflection_prod = 1 + 0j  # Producto de los coeficientes de reflexión
        # self.transmission_prod = 1 + 0j  # Producto de los coeficientes de transmisión
        # self.total_delay = 0  # Retardo total del rayo

    def __repr__(self):
        return f"Ray: Position ('{self.start_point}', {self.end_point}) Path: ('{self.path}'); Reflections and transmisions: ('{self.num_reflections}',''{self.num_transmissions})"

    def collide(self, wall):
        # based off line segment intersection formula found at https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection
        
        # set variables associated with formula
        wx1 = wall.start_point[0]
        wy1 = wall.start_point[1]
        wx2 = wall.end_point[0]
        wy2 = wall.end_point[1]

        rx3 = self.start_point[0]
        ry3 = self.start_point[1]
        rx4 = self.start_point[0] + self.direction[0]
        ry4 = self.start_point[1] + self.direction[1]


        # numerator and denominator for the line-line intersection formula that calculates intersection of wall and ray.
        n = (wx1 - rx3) * (ry3 - ry4) - (wy1 - ry3) * (rx3 - rx4)
        d = (wx1 - wx2) * (ry3 - ry4) - (wy1 - wy2) * (rx3 - rx4)

        # check for invalid denominator
        if d == 0:
            return False

        t = n / d
        u = ((wx2 - wx1) * (wy1 - ry3) - (wy2 - wy1) * (wx1 - rx3)) / d

        # determines if there is a collision and returns intersection point as tuple
        if (t > 0 and t < 1 and u > 0):
            px = (wx1 + t * (wx2 - wx1))
            py = (wy1 + t * (wy2 - wy1))

            return Collision(self, (px, py), wall)
        else:
            return False

    # def visualize(self, display, scale):
    #     if len(self.path) > 1:
    #         points_scaled = [(int(point[0] * scale[0]), int(point[1] * scale[1])) for point in self.path]
    #         pygame.draw.lines(display, RAYS, False, points_scaled)  # Dibujar la trayectoria completa
    #     else:
    #         print("Not enough points to draw the ray path")
    #         print(self.path)

    def visualize(self, display, scale):
        if self.start_point and self.end_point is not None:
            start_point_scaled = (int(self.start_point[0] * scale[0]), int(self.start_point[1] * scale[1]))
            end_point_scaled = (int(self.end_point[0] * scale[0]), int(self.end_point[1] * scale[1]))
            pygame.draw.line(display, RAYS, start_point_scaled, end_point_scaled)
        else:
            print("endpoint None")

class ReceiverGrid(Visualizable):
    def __init__(self, dimensions, resolution):
        self.dimensions = dimensions
        self.resolution = resolution
        self.grid = self.initialize_grid()
        self.cell_size = (self.dimensions[0] / self.resolution, self.dimensions[1] / self.resolution)  # Tamaño de la celda de la cuadrícula
        self.received_power = np.zeros_like(self.grid[0])

    def initialize_grid(self):
        x = np.linspace(0, self.dimensions[0], self.resolution)
        y = np.linspace(0, self.dimensions[1], self.resolution)
        grid = np.meshgrid(x, y)
        return grid
    
    def calculate_received_power_in_cell(self, rays, frequency, calculation_point):
        c = 3e8
        wavelength = c / frequency
        total_power = 0
        for ray in rays:
            distance_correction = math.dist(ray.end_point, calculation_point)
            distance = ray.distance - distance_correction
            path_loss = (4 * np.pi * distance / wavelength) ** 2  # Free-space path loss
            ray_power = ray.power * (abs(ray.alpha) ** 2) / path_loss
            total_power += ray_power
        
        return total_power

    def visualize(self, display, scale):
        return super().visualize(display, scale)

class Simulator:
    def __init__(self, environment, tx_antenna, rx_grid, num_rays, max_path_loss, max_reflections, max_transmissions):
        self.environment = environment
        self.tx_antenna = tx_antenna
        self.rx_grid = rx_grid
        self.num_rays = num_rays
        self.max_path_loss = max_path_loss
        self.max_reflections = max_reflections
        self.max_transmissions = max_transmissions
        self.rays = []
        self.reflected_rays = []
        self.quadtree = Index(bbox=(0, 0, environment.dimensions[0], environment.dimensions[1]))

    def launch_rays(self):
        self.rays = []
        rays = self.tx_antenna.launch_rays(self.num_rays)
        start = time.time()

        with tqdm(total=self.num_rays, desc="Launching rays", unit="ray") as pbar:
            for ray in rays:
                self.propagate_ray(ray)
                pbar.update(1)

        print(f"Launched {len(self.rays)} rays in {time.time() - start:.2f} seconds")
        return self.rays

    def find_closest_collision(self, ray):
        obstacles = self.environment.obstacles

        closest_collision = None
        closest_distance = 1000
        for obstacle in obstacles:
            collision = ray.collide(obstacle)
            if collision:
                distance = math.dist(ray.start_point, collision.point)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_collision = collision
        if closest_collision:
            ray.end_point = closest_collision.point
            # ray.path.append(ray.end_point)
            return closest_collision
            
    def propagate_ray(self, ray):
        # Verificar si el path loss del rayo está por encima del umbral
        if ray.path_loss > self.max_path_loss:
            return

        # Calcular la siguiente colisión
        collision = self.find_closest_collision(ray)

        if collision is not None:
            # Actualizar el rayo original con la distancia y el path loss
            distance = math.dist(ray.start_point, collision.point)
            ray.end_point = collision.point
            ray.distance += distance

            # Actualizar el path loss del rayo
            frequency = self.tx_antenna.frequency
            wavelength = 3e8 / frequency
            path_loss = (4 * np.pi * ray.distance / wavelength) ** 2
            ray.path_loss = path_loss

            # Verificar si el path loss excede el umbral
            if ray.path_loss > self.max_path_loss:
                self.rays.append(ray)
                return

            # Calcular los coeficientes de reflexión y transmisión
            dot_product = np.dot(ray.direction, collision.wall.normal_direction)
            dot_product = np.clip(dot_product, -1.0, 1.0)  # Clip the dot product to the valid range [-1, 1]
            incident_angle = math.acos(dot_product)
            reflection_coefficient, transmission_coefficient, refracted_angle = self.calculate_coefficients1(incident_angle, collision.wall.material, ray.polarization)

            # Calcular y propagar el rayo reflejado
            reflected_ray = self.reflect_ray(ray, collision, reflection_coefficient)
            self.propagate_ray(reflected_ray)

            # Calcular y propagar el rayo refractado
            if ray.num_reflections == 0:
                refracted_ray = self.refract_ray(ray, collision, transmission_coefficient, refracted_angle)
                self.propagate_ray(refracted_ray)

            self.rays.append(ray)  # Agrega el rayo original al final
        else:
            self.rays.append(ray)
    
    def reflect_ray(self, ray, collision, reflection_coefficient):
        # Calcular el vector normal de la pared en el punto de colisión
        normal = collision.wall.normal_direction

        # Normalizar el vector normal
        normal_magnitude = math.sqrt(normal[0]**2 + normal[1]**2)
        normal = (normal[0] / normal_magnitude, normal[1] / normal_magnitude)

        # Calcular la dirección del rayo reflejado
        reflected_direction = (
            ray.direction[0] - 2 * np.dot(ray.direction, normal) * normal[0],
            ray.direction[1] - 2 * np.dot(ray.direction, normal) * normal[1]
        )

        # Actualizar el rayo original para representar la reflexión
        reflected_ray = copy.deepcopy(ray)
        reflected_ray.start_point = collision.point
        reflected_ray.path.append(collision.point)
        reflected_ray.direction = reflected_direction
        reflected_ray.alpha *= 0.8  # Valor fijo para alpha en la reflexión
        # reflected_ray.alpha *= reflection_coefficient
        reflected_ray.num_reflections += 1

        return reflected_ray

    def refract_ray(self, ray, collision, transmission_coefficient, refracted_angle):
        # Calcular el vector normal de la pared en el punto de colisión
        normal = collision.wall.normal_direction

        # Normalizar el vector normal
        normal_magnitude = math.sqrt(normal[0]**2 + normal[1]**2)
        normal = (normal[0] / normal_magnitude, normal[1] / normal_magnitude)

        # Calcular la dirección del rayo refractado (puedes ajustar esto según tus necesidades)
        refracted_direction = ray.direction

        # Crear el rayo transmitido
        refracted_ray = copy.deepcopy(ray)
        refracted_ray.path.append(collision.point)
        refracted_ray.start_point = collision.point
        # refracted_ray.direction = refracted_direction
        refracted_ray.alpha *= 0.6  # Valor fijo para alpha en la refracción
        # refracted_ray.alpha *= transmission_coefficient
        refracted_ray.num_transmissions += 1

        return refracted_ray
    
    def calculate_coefficients(self, incident_angle, material, polarization):
        epsilon_r = material.permittivity
        conductivity = material.conductivity
        thickness = material.thickness
        frequency = self.tx_antenna.frequency
        
        # Calcular la permitividad compleja
        epsilon_complex = epsilon_r - 1j * conductivity / (2 * np.pi * frequency * epsilon_0)
        
        # Calcular el índice de refracción complejo
        n_complex = np.sqrt(epsilon_complex)
        
        # Calcular los ángulos de incidencia y transmisión
        sin_theta_i = np.sin(incident_angle)
        cos_theta_i = np.cos(incident_angle)
        sin_theta_t = sin_theta_i / n_complex.real
        cos_theta_t = np.sqrt(1 - sin_theta_t**2)
        
        # Calcular los coeficientes de reflexión y transmisión de Fresnel
        if polarization == 'TE':
            r_perpendicular = (cos_theta_i - n_complex * cos_theta_t) / (cos_theta_i + n_complex * cos_theta_t)
            t_perpendicular = 2 * cos_theta_i / (cos_theta_i + n_complex * cos_theta_t)
            reflection_coefficient = r_perpendicular
            transmission_coefficient = t_perpendicular
        elif polarization == 'TM':
            r_parallel = (n_complex * cos_theta_i - cos_theta_t) / (n_complex * cos_theta_i + cos_theta_t)
            t_parallel = 2 * n_complex * cos_theta_i / (n_complex * cos_theta_i + cos_theta_t)
            reflection_coefficient = r_parallel
            transmission_coefficient = t_parallel
        
        # Calcular el coeficiente de propagación
        k = 2 * np.pi * frequency * n_complex / 299792458  # Usar la velocidad de la luz en m/s
        propagation_coefficient = np.exp(-1j * k * thickness * cos_theta_t)
        
        # Aplicar el coeficiente de propagación al coeficiente de transmisión
        transmission_coefficient *= propagation_coefficient
        
        # Calcular el ángulo de refracción
        refracted_angle = np.arcsin(sin_theta_t.real)
        
        return reflection_coefficient, transmission_coefficient, refracted_angle

    def calculate_coefficients1(self, incident_angle, material, polarization):
        epsilon_r = material.permittivity
        conductivity = material.conductivity
        frequency = self.tx_antenna.frequency

        # Calcular la permitividad compleja
        epsilon_complex = epsilon_r - 1j * conductivity / (2 * np.pi * frequency * epsilon_0)

        # Calcular el ángulo de refracción
        sin_theta_i = np.sin(incident_angle)
        cos_theta_i = np.cos(incident_angle)
        sin_theta_t = sin_theta_i / np.sqrt(epsilon_complex.real)
        cos_theta_t = np.sqrt(1 - sin_theta_t ** 2)

        # Calcular los coeficientes de reflexión y transmisión de Fresnel
        if polarization == 'TE':
            reflection_coefficient = (cos_theta_i - np.sqrt(epsilon_complex - sin_theta_i ** 2)) / (
                        cos_theta_i + np.sqrt(epsilon_complex - sin_theta_i ** 2))
            transmission_coefficient = 2 * cos_theta_i / (cos_theta_i + np.sqrt(epsilon_complex - sin_theta_i ** 2))
        elif polarization == 'TM':
            reflection_coefficient = (epsilon_complex * cos_theta_i - np.sqrt(epsilon_complex - sin_theta_i ** 2)) / (
                        epsilon_complex * cos_theta_i + np.sqrt(epsilon_complex - sin_theta_i ** 2))
            transmission_coefficient = 2 * epsilon_complex * cos_theta_i / (
                        epsilon_complex * cos_theta_i + np.sqrt(epsilon_complex - sin_theta_i ** 2))

        # Calcular el coeficiente de propagación
        k = 2 * np.pi * frequency * np.sqrt(epsilon_complex) / 299792458  # Usar la velocidad de la luz en m/s
        propagation_coefficient = np.exp(-1j * k * material.thickness * cos_theta_t)

        # Aplicar el coeficiente de propagación al coeficiente de transmisión
        transmission_coefficient *= propagation_coefficient

        refracted_angle = np.arcsin(sin_theta_t.real)

        return reflection_coefficient, transmission_coefficient, refracted_angle

    def calculate_coefficients2(self, incident_angle, material, polarization):
        epsilon_r = material.permittivity
        conductivity = material.conductivity
        frequency = self.tx_antenna.frequency
        
        # Calcular la permitividad compleja
        epsilon_complex = epsilon_r - 1j * conductivity / (2 * np.pi * frequency * epsilon_0)
        
        # Calcular el índice de refracción complejo
        n_complex = np.sqrt(epsilon_complex)
        
        # Calcular los ángulos de incidencia y transmisión
        sin_theta_i = np.sin(incident_angle)
        cos_theta_i = np.cos(incident_angle)
        sin_theta_t = sin_theta_i / n_complex.real
        cos_theta_t = np.sqrt(1 - sin_theta_t**2)
        
        # Calcular los coeficientes de reflexión y transmisión de Fresnel
        if polarization == 'TE':
            r_perpendicular = (cos_theta_i - n_complex * cos_theta_t) / (cos_theta_i + n_complex * cos_theta_t)
            t_perpendicular = 2 * cos_theta_i / (cos_theta_i + n_complex * cos_theta_t)
            reflection_coefficient = r_perpendicular
            transmission_coefficient = t_perpendicular
        elif polarization == 'TM':
            r_parallel = (n_complex * cos_theta_i - cos_theta_t) / (n_complex * cos_theta_i + cos_theta_t)
            t_parallel = 2 * n_complex * cos_theta_i / (n_complex * cos_theta_i + cos_theta_t)
            reflection_coefficient = r_parallel
            transmission_coefficient = t_parallel
        
        # Calcular el coeficiente de propagación
        k = 2 * np.pi * frequency * n_complex / 299792458  # Usar la velocidad de la luz en m/s
        propagation_coefficient = np.exp(-1j * k * material.thickness * cos_theta_t)
        
        # Aplicar el coeficiente de propagación al coeficiente de transmisión
        transmission_coefficient *= propagation_coefficient
        
        # Calcular el ángulo de refracción
        refracted_angle = np.arcsin(sin_theta_t.real)
        
        return reflection_coefficient, transmission_coefficient, refracted_angle

    def generate_contour_map(self):
        total_cells = self.rx_grid.resolution ** 2

        # Calcular las coordenadas de la celda del transmisor
        tx_cell_x = int(self.tx_antenna.location[0] // self.rx_grid.cell_size[0])
        tx_cell_y = int(self.tx_antenna.location[1] // self.rx_grid.cell_size[1])

        # Definir el radio de la zona alrededor del transmisor (en número de celdas)
        tx_zone_radius = 0.1

        with tqdm(total=total_cells, desc="Generating contour map", unit="cell") as pbar:
            for i in range(self.rx_grid.resolution):
                for j in range(self.rx_grid.resolution):
                    cell_coords = (i * self.rx_grid.cell_size[0], j * self.rx_grid.cell_size[1])
                    cell_bbox = (cell_coords[0], cell_coords[1], cell_coords[0] + self.rx_grid.cell_size[0], cell_coords[1] + self.rx_grid.cell_size[1])

                    # Verificar si la celda actual está dentro de la zona alrededor del transmisor
                    if abs(i - tx_cell_x) <= tx_zone_radius and abs(j - tx_cell_y) <= tx_zone_radius:
                        # Asignar un valor predeterminado (por ejemplo, -100 dBm) a las celdas dentro de la zona del transmisor
                        self.rx_grid.received_power[j, i] = -30
                    
                    else:
                        # Obtener los rayos que intersectan con la celda actual
                        rays_in_cell = []
                        for ray in self.rays:
                            if self.ray_intersects_cell(ray, cell_bbox):
                                rays_in_cell.append(ray)

                        # Calcular el punto de cálculo para la celda actual
                        calculation_point = (cell_coords[0] + self.rx_grid.cell_size[0] / 2, cell_coords[1] + self.rx_grid.cell_size[1] / 2)

                        received_power = self.rx_grid.calculate_received_power_in_cell(rays_in_cell, self.tx_antenna.frequency, calculation_point)

                        # Agregar una pequeña constante al valor de received_power antes de calcular el logaritmo
                        received_power_dbm = 10 * math.log10(received_power / 1e-3 + 1e-12)  # Convertir a dBm

                        if received_power_dbm > 0:
                            # Real coordinates of the center of the cell
                            print("Real coordinates of the center of the cell:", cell_coords[0] + self.rx_grid.cell_size[0] / 2, cell_coords[1] + self.rx_grid.cell_size[1] / 2)

                        self.rx_grid.received_power[j, i] = received_power_dbm

                    pbar.update(1)

        self.plot()

    
    def ray_intersects_cell(self, ray, cell_bbox):
        # Verificar si el rayo intersecta con la celda
        x1, y1 = ray.start_point
        x2, y2 = ray.end_point
        cell_x1, cell_y1, cell_x2, cell_y2 = cell_bbox
        
        # Verificar si el rayo está completamente fuera de la celda
        if (x1 < cell_x1 and x2 < cell_x1) or (x1 > cell_x2 and x2 > cell_x2) or (y1 < cell_y1 and y2 < cell_y1) or (y1 > cell_y2 and y2 > cell_y2):
            return False
        
        # Verificar si el rayo está completamente dentro de la celda
        if cell_x1 <= x1 <= cell_x2 and cell_x1 <= x2 <= cell_x2 and cell_y1 <= y1 <= cell_y2 and cell_y1 <= y2 <= cell_y2:
            return True
        
        # Verificar si el rayo cruza alguno de los bordes de la celda
        if self.ray_intersects_line(ray, (cell_x1, cell_y1, cell_x2, cell_y1)) or \
        self.ray_intersects_line(ray, (cell_x2, cell_y1, cell_x2, cell_y2)) or \
        self.ray_intersects_line(ray, (cell_x2, cell_y2, cell_x1, cell_y2)) or \
        self.ray_intersects_line(ray, (cell_x1, cell_y2, cell_x1, cell_y1)):
            return True
        
        return False

    def ray_intersects_line(self, ray, line):
        # Verificar si el rayo intersecta con una línea
        x1, y1 = ray.start_point
        x2, y2 = ray.end_point
        x3, y3, x4, y4 = line
        
        # Calcular el determinante
        det = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
        if det == 0:
            return False
        
        # Calcular los parámetros t y u
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / det
        u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / det
        
        # Verificar si la intersección está dentro de los segmentos
        if 0 <= t <= 1 and 0 <= u <= 1:
            return True
        
        return False

    def plot(self):
        fig, ax = plt.subplots(figsize=(8, 4.8))
        X, Y = self.rx_grid.grid
        print(self.rx_grid.received_power)
        contour_levels = np.linspace(-80, -30, 100)  # Ajusta los valores mínimo y máximo según tus necesidades
        contour = ax.contourf(X, Y, self.rx_grid.received_power, levels=contour_levels, cmap='RdYlGn')
        fig.colorbar(contour, ax=ax, label='Potencia de señal recibida (dBm)')
        
        ax.plot(self.tx_antenna.location[0], self.tx_antenna.location[1], 'ro', markersize=10, label='Antena transmisora')
        
        for obstacle in self.environment.obstacles:
            start_x = obstacle.start_point[0]
            start_y = obstacle.start_point[1]
            end_x = obstacle.end_point[0]
            end_y = obstacle.end_point[1]
            ax.plot([start_x, end_x], [start_y, end_y], 'k-', linewidth=2)
        
        ax.set_xlim(0, self.environment.dimensions[0])
        ax.set_ylim(0, self.environment.dimensions[1])
        ax.set_xlabel('Distancia (m)')
        ax.set_ylabel('Distancia (m)')
        ax.set_title('Mapa de calor de la señal de RF con obstáculos')
        ax.legend()
        fig.tight_layout()
        plt.show()

    def update_tx_position(self, new_position):
        self.tx_antenna.location = new_position

    def export_simulation_data(self):
        rays_data = [(ray.start_point, ray.end_point) for ray in self.rays]
        walls_data = [(wall.start_point, wall.end_point) for wall in self.environment.obstacles]
        return rays_data, walls_data
    
class SimulationVisualizer:
    def __init__(self, simulator):
        self.simulator = simulator
        self.display = self.initialize_display()
        self.width, self.height = self.display.get_size()
        self.scale = self.calculate_scale()

    def initialize_display(self):
        pygame.init()
        screen_info = pygame.display.Info()
        self.width, self.height = int(screen_info.current_w * 0.5), int(screen_info.current_h * 0.5)
        display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('2DRayLaunching')
        display.fill(BACKGROUND)  # Cambiar el color de fondo a blanco
        self.clock = pygame.time.Clock()

        return display

    def calculate_scale(self):
        return (self.width / self.simulator.environment.dimensions[0],
                self.height / self.simulator.environment.dimensions[1])

    def update_tx_position(self):
        mouse_pos = pygame.mouse.get_pos()
        tx_pos_scaled = (mouse_pos[0] / self.scale[0], mouse_pos[1] / self.scale[1])
        self.simulator.update_tx_position(tx_pos_scaled)

    def ray_launching(self, fps=6):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if(event.key == K_r):
                        self.update_tx_position()
                        self.simulator.launch_rays()
                        
            self.display.fill(BACKGROUND)

            
            # Renderizar el texto con la posición del mouse
            x, y = pygame.mouse.get_pos()
            font = pygame.font.Font(None, 36)
            texto = font.render(f"Posición del Mouse: ({x}, {y})", True, (255, 255, 255))
            self.simulator.environment.visualize(self.display, self.scale)
            self.display.blit(texto, (10, 10))

            for ray in self.simulator.rays:
                ray.visualize(self.display, self.scale)
            
            pygame.display.update()
            self.clock.tick(fps)

        pygame.quit()

def plot_simulation(rays_data, walls_data, dimensions):
    plt.figure(figsize=(8, 6))
    for wall_start, wall_end in walls_data:
        plt.plot([wall_start[0], wall_end[0]], [wall_start[1], wall_end[1]], 'k-', linewidth=2)
    for ray_start, ray_end in rays_data:
        plt.plot([ray_start[0], ray_end[0]], [ray_start[1], ray_end[1]], 'b-', alpha=0.5)
    plt.xlim(0, dimensions[0])
    plt.ylim(0, dimensions[1])
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Ray Launching Simulation')
    plt.grid(True)
    plt.show()

def initializeBorders(width, height):
    walls = []
    material = Material(2.8, 0.0001, 0.15)

    # initialize border walls
    walls.append(Wall((0, 0), (width - 1, 0), material))  # top Wall
    walls.append(Wall((0, 0), (0, height - 1), material))  # left Wall
    walls.append(Wall((0, height - 1), (width - 1, height - 1), material))  # bottom Wall
    walls.append(Wall((width - 1, 0), (width - 1, height - 1), material))  # right Wall

    return walls

def create_random_walls(width, height, num_walls=20, min_wall_height=5, min_wall_distance=2):
    walls = []
    material = Material(2.8, 0.0001, 5)

    for _ in range(num_walls):
        # Generar una pared horizontal o vertical aleatoriamente
        orientation = random.choice(['horizontal', 'vertical'])

        if orientation == 'horizontal':
            # Generar una pared horizontal
            start_x = random.randint(min_wall_distance, width - min_wall_distance)

            # Verificar si el rango de valores para end_x es válido
            max_end_x = width - min_wall_distance
            if start_x + min_wall_height <= max_end_x:
                end_x = random.randint(start_x + min_wall_height, max_end_x)
            else:
                # El rango de valores para end_x es inválido, omitir esta pared
                continue

            start_y = random.randint(min_wall_distance, height - min_wall_distance)
            end_y = start_y
        else:
            # Generar una pared vertical
            start_x = random.randint(min_wall_distance, width - min_wall_distance)
            end_x = start_x
            start_y = random.randint(min_wall_distance, height - min_wall_distance)

            # Verificar si el rango de valores para end_y es válido
            max_end_y = height - min_wall_distance
            if start_y + min_wall_height <= max_end_y:
                end_y = random.randint(start_y + min_wall_height, max_end_y)
            else:
                # El rango de valores para end_y es inválido, omitir esta pared
                continue

        start_point = (start_x, start_y)
        end_point = (end_x, end_y)
        walls.append(Wall(start_point, end_point, material))

    return walls

def initialize_realistic_map(width, height, material):
    walls = []

    # Paredes exteriores
    walls.append(Wall((0, 0), (width, 0), material))  # Pared superior
    walls.append(Wall((0, 0), (0, height), material))  # Pared izquierda
    walls.append(Wall((0, height), (width, height), material))  # Pared inferior
    walls.append(Wall((width, 0), (width, height), material))  # Pared derecha

    # Habitación 1 (Sala de estar)
    walls.append(Wall((width * 0.1, height * 0.1), (width * 0.1, height * 0.6), material))  # Pared izquierda
    walls.append(Wall((width * 0.1, height * 0.1), (width * 0.5, height * 0.1), material))  # Pared superior
    walls.append(Wall((width * 0.5, height * 0.1), (width * 0.5, height * 0.4), material))  # Pared derecha
    walls.append(Wall((width * 0.3, height * 0.4), (width * 0.5, height * 0.4), material))  # Pared inferior

    # Habitación 2 (Cocina)
    walls.append(Wall((width * 0.6, height * 0.6), (width * 0.6, height * 0.9), material))  # Pared izquierda
    walls.append(Wall((width * 0.6, height * 0.6), (width * 0.9, height * 0.6), material))  # Pared superior
    walls.append(Wall((width * 0.9, height * 0.6), (width * 0.9, height * 0.9), material))  # Pared derecha

    # Habitación 3 (Dormitorio)
    walls.append(Wall((width * 0.1, height * 0.7), (width * 0.1, height * 0.9), material))  # Pared izquierda
    walls.append(Wall((width * 0.1, height * 0.7), (width * 0.4, height * 0.7), material))  # Pared superior
    walls.append(Wall((width * 0.4, height * 0.7), (width * 0.4, height * 0.9), material))  # Pared derecha

    # Pasillo 1
    walls.append(Wall((width * 0.5, height * 0.4), (width * 0.5, height * 0.6), material))  # Pared izquierda
    walls.append(Wall((width * 0.5, height * 0.6), (width * 0.6, height * 0.6), material))  # Pared inferior

    # Pasillo 2
    walls.append(Wall((width * 0.3, height * 0.4), (width * 0.3, height * 0.7), material))  # Pared derecha
    walls.append(Wall((width * 0.1, height * 0.6), (width * 0.3, height * 0.6), material))  # Pared superior

    # Puertas
    walls.append(Wall((width * 0.5, height * 0.4), (width * 0.5, height * 0.45), material))  # Puerta Sala de estar - Pasillo 1
    walls.append(Wall((width * 0.6, height * 0.6), (width * 0.65, height * 0.6), material))  # Puerta Cocina - Pasillo 1
    walls.append(Wall((width * 0.3, height * 0.6), (width * 0.3, height * 0.65), material))  # Puerta Dormitorio - Pasillo 2
    walls.append(Wall((width * 0.1, height * 0.6), (width * 0.1, height * 0.65), material))  # Puerta Sala de estar - Pasillo 2

    return walls


# Ejemplo de uso
if __name__ == "__main__":
    # Crear el entorno con las dimensiones en metros
    width, height = 14, 8
    environment = Environment(dimensions=(width, height))

    # Crear paredes aleatorias
    # walls = initializeBorders(width, height)
    # randomWalls = create_random_walls(width, height)
    # walls = randomWalls + walls

    walls = initialize_realistic_map(width, height, material=Material(2.8, 0.0001, 0.15))

    for wall in walls:
        environment.add_obstacle(wall)

    tx_antenna = Antenna(location=(4.2, 2), tx_power=0.03, radiation_pattern=None, frequency=2.4e9)

    rx_grid = ReceiverGrid(dimensions=(width, height), resolution=30)

    simulator = Simulator(environment, tx_antenna, rx_grid, num_rays=1440, max_path_loss=1e6, max_reflections=2, max_transmissions=1)
    simulator.launch_rays()
    simulator.generate_contour_map()

    # visualizer = SimulationVisualizer(simulator)
    # visualizer.ray_launching(fps=30)

