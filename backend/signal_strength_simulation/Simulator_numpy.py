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
import cmath
from numba import njit
import time
from line_profiler import LineProfiler

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
        self.start_point = np.array(start_point)
        self.end_point = np.array(end_point)
        self.material = material

        # Calcular el vector normal de la pared
        dx, dy = self.end_point - self.start_point
        self.normal_direction = np.array([-dy, dx])  # Vector normal perpendicular a la pared

    def visualize(self, display, scale):
        start_point_scaled = (int(self.start_point[0] * scale[0]), int(self.start_point[1] * scale[1]))
        end_point_scaled = (int(self.end_point[0] * scale[0]), int(self.end_point[1] * scale[1]))
        thickness_scaled = int(self.material.thickness * scale[0])

        pygame.draw.line(display, BLACK, start_point_scaled, end_point_scaled, 1)

class Antenna(Visualizable):
    def __init__(self, location, tx_power, radiation_pattern, frequency):
        self.location = np.array(location)
        self.tx_power = tx_power
        self.radiation_pattern = radiation_pattern
        self.frequency = frequency

    def launch_rays(self, num_rays):
        rays = []
        for i in range(num_rays):
            angle = i * 2 * math.pi / num_rays  # Calcular el ángulo en radianes
            direction = (math.cos(angle), math.sin(angle))
            rays.append(Ray(self.location, direction))
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
    def __init__(self, start_point, direction, polarization="TE", power=1.0):
        self.start_point = np.array(start_point)
        self.direction = np.array(direction)
        self.end_point = None
        self.polarization = polarization
        self.alpha = 1 + 0j
        self.power = power
        self.path_loss = 0
        self.path = [self.start_point]
        self.num_reflections = 0
        self.num_transmissions = 0
        self.reflection_prod = 1 + 0j
        self.transmission_prod = 1 + 0j
        self.distance = 0
        self.total_delay = 0

    def __repr__(self):
        return f"Ray: Position ('{self.start_point}', {self.end_point}) Path: ('{self.path}'); Reflections and transmisions: ('{self.num_reflections}',''{self.num_transmissions})"

    
    def collide(self, wall):
        wx1, wy1 = wall.start_point
        wx2, wy2 = wall.end_point
        rx3, ry3 = self.start_point
        rx4, ry4 = self.start_point + self.direction

        denominator = (wx1 - wx2) * (ry3 - ry4) - (wy1 - wy2) * (rx3 - rx4)

        if denominator == 0:
            return False

        t = ((wx1 - rx3) * (ry3 - ry4) - (wy1 - ry3) * (rx3 - rx4)) / denominator
        u = -((wx1 - wx2) * (wy1 - ry3) - (wy1 - wy2) * (wx1 - rx3)) / denominator

        if 0 < t < 1 and u > 0:
            px, py = wall.start_point + t * (wall.end_point - wall.start_point)
            return Collision(self, np.array([px, py]), wall)
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
        self.cell_size = self.dimensions[0] / self.resolution  # Tamaño de la celda de la cuadrícula
        self.received_power = np.zeros_like(self.grid[0])

    def initialize_grid(self):
        x = np.linspace(0, self.dimensions[0], self.resolution)
        y = np.linspace(0, self.dimensions[1], self.resolution)
        grid = np.meshgrid(x, y)
        return grid
    
    def get_rays_in_cell(self, cell_coords):
        cell_bbox = (cell_coords[0], cell_coords[1], cell_coords[0] + self.cell_size, cell_coords[1] + self.cell_size)
        return self.simulator.quadtree.intersect(cell_bbox)  # Obtener los rayos que intersectan la celda

    def register_rays(self):
        for i in range(self.resolution):
            for j in range(self.resolution):
                cell_coords = (i * self.cell_size, j * self.cell_size)
                rays_in_cell = self.get_rays_in_cell(cell_coords)
                
                received_power = self.calculate_received_power(rays_in_cell, frecuency=2.4e9)
                self.received_power[j, i] += 10**(received_power / 10)
    
    def calculate_received_power(self, rays, frequency, calculation_point):
        # Velocidad de la luz (m/s)
        c = 3e8

        # Frecuencia angular
        omega = 2 * np.pi * frequency

        # Inicializar la potencia recibida total
        total_power = 0

        # Iterar sobre cada rayo
        for ray in rays:
            # Calcular la distancia desde el punto final del rayo hasta el punto de cálculo
            distance = math.dist(ray.end_point, calculation_point)

            # Calcular el retardo de propagación desde el punto final del rayo hasta el punto de cálculo
            delay = distance / c

            # Calcular el término exponencial
            exp_term = cmath.exp(1j * omega * delay)

            # Calcular la corrección de amplitud compleja
            correction_factor = distance * exp_term

            # Aplicar la corrección a la amplitud compleja del rayo
            corrected_alpha = ray.alpha * correction_factor

            # Calcular la potencia del rayo utilizando la amplitud compleja corregida
            ray_power = abs(corrected_alpha) ** 2

            # Sumar la potencia del rayo a la potencia total recibida
            total_power += ray_power

        return total_power


    def visualize(self, display, scale):
        return super().visualize(display, scale)
        
    # def plot(self):
    #     fig, ax = plt.subplots()
    #     im = ax.imshow(self.received_power, cmap='viridis', origin='lower', extent=[0, self.dimensions[0], 0, self.dimensions[1]])
    #     ax.set_xlabel('X (m)')
    #     ax.set_ylabel('Y (m)')
    #     ax.set_title('Received Power (dBm)')
    #     fig.colorbar(im, ax=ax, label='Received Power (dBm)')
    #     plt.show()

class Simulator:
    def __init__(self, environment, tx_antenna, rx_grid, num_rays, min_power, max_reflections, max_transmissions):
        self.environment = environment
        self.tx_antenna = tx_antenna
        self.rx_grid = rx_grid
        self.num_rays = num_rays
        self.min_power = min_power
        self.max_reflections = max_reflections
        self.max_transmissions = max_transmissions
        self.rays = []
        self.reflected_rays = []
        self.quadtree = Index(bbox=(0, 0, environment.dimensions[0], environment.dimensions[1]))

    def launch_rays(self):
        self.rays = []
        self.quadtree = Index(bbox=(0, 0, self.environment.dimensions[0], self.environment.dimensions[1]))  # Reiniciar el Quadtree
        rays = self.tx_antenna.launch_rays(self.num_rays)

        start = time.time()
        for ray in rays:
            self.propagate_ray(ray)
        
        print(time.time() - start)
        # print(len(self.rays))
        return self.rays

    def find_closest_collision(self, ray):
        obstacles = self.environment.obstacles

        collisions = [ray.collide(obstacle) for obstacle in obstacles]
        valid_collisions = [collision for collision in collisions if collision]

        if valid_collisions:
            distances = [np.linalg.norm(np.array(collision.point) - np.array(ray.start_point)) for collision in valid_collisions]
            closest_collision = valid_collisions[np.argmin(distances)]
            ray.end_point = closest_collision.point
            return closest_collision
            
    def propagate_ray(self, ray):
        # Verificar si la potencia del rayo está por debajo del umbral
        # if ray.num_reflections > self.max_reflections or ray.num_transmissions > self.max_transmissions:
        #     return

        power = abs(ray.alpha)**2
        if ray.num_reflections > self.max_reflections or ray.num_transmissions > self.max_transmissions: #or power < self.min_power:
            return

        # Calcular la siguiente colisión
        collision = self.find_closest_collision(ray)

        if collision:
            distance = np.linalg.norm(np.array(collision.point) - np.array(ray.start_point))
            ray.alpha *= self.calculate_complex_amplitude(distance, self.tx_antenna.frequency)
            ray.end_point = collision.point

            # Calcular y propagar el rayo reflejado
            reflected_ray = self.reflect_ray(ray, collision)
            self.propagate_ray(reflected_ray)

            # Calcular y propagar el rayo refractado
            refracted_ray = self.refract_ray(ray, collision)
            self.propagate_ray(refracted_ray)
            self.rays.append(ray) # Agrega el rayo original al final
            # print(ray.start_point, ray.end_point)
            # self.quadtree.insert(ray, (ray.start_point[0], ray.start_point[1], ray.end_point[0],ray.end_point[1])) # Agrega el rayo refractado al final
        else:
            # Insertar el rayo en el Quadtree al final de su propagación
            # self.quadtree.insert(ray, ray.end_point)
            self.rays.append(ray)
    
    def calculate_complex_amplitude(self, distance, frequency):
        # Speed of light in air (m/s)
        speed_of_light = 299792458
        
        # Calculate the propagation delay of the segment
        delay = distance / speed_of_light
        
        # Calculate the angular frequency
        omega = 2 * cmath.pi * frequency
        
        # Calculate the free-space path loss attenuation
        attenuation = 1 / distance
        
        # Calculate the phase shift
        phase_shift = cmath.exp(-1j * omega * delay)
        
        # Calculate the complex amplitude of the segment
        complex_amplitude = attenuation * phase_shift
        
        return complex_amplitude

    def reflect_ray(self, ray, collision):
        normal = np.array(collision.wall.normal_direction, dtype=float)  # Convertir a tipo flotante
        normal /= np.linalg.norm(normal)

        incident_angle = np.arccos(np.dot(ray.direction, normal))

        if ray.polarization == 'TE':
            reflection_coefficient = self.calculate_reflection_coefficient_TE(incident_angle, collision.wall.material)
        elif ray.polarization == 'TM':
            reflection_coefficient = self.calculate_reflection_coefficient_TM(incident_angle, collision.wall.material)

        reflected_direction = ray.direction - 2 * np.dot(ray.direction, normal) * normal

        reflected_ray = copy.deepcopy(ray)
        reflected_ray.distance += np.linalg.norm(ray.start_point - collision.point)
        reflected_ray.start_point = collision.point
        reflected_ray.path.append(collision.point)
        reflected_ray.direction = reflected_direction
        reflected_ray.alpha *= reflection_coefficient
        reflected_ray.num_reflections += 1

        return reflected_ray

    def refract_ray(self, ray, collision):
        normal = np.array(collision.wall.normal_direction, dtype=float)  # Convertir a tipo flotante
        normal /= np.linalg.norm(normal)

        incident_angle = np.arccos(np.dot(ray.direction, normal))

        if ray.polarization == 'TE':
            transmission_coefficient = self.calculate_transmission_coefficient_TE(incident_angle, collision.wall.material)
        elif ray.polarization == 'TM':
            transmission_coefficient = self.calculate_transmission_coefficient_TM(incident_angle, collision.wall.material)

        refracted_angle = self.calculate_refracted_angle(incident_angle, collision.wall.material)
        refracted_direction = np.array([
            np.cos(refracted_angle) * normal[0] - np.sin(refracted_angle) * normal[1],
            np.sin(refracted_angle) * normal[0] + np.cos(refracted_angle) * normal[1]
        ])

        refracted_ray = copy.deepcopy(ray)
        refracted_ray.path.append(collision.point)
        refracted_ray.start_point = collision.point
        refracted_ray.alpha *= transmission_coefficient
        refracted_ray.num_transmissions += 1

        return refracted_ray

    def calculate_reflection_coefficient_TE(self, incident_angle, material):
        epsilon_r = material.permittivity
        conductivity = material.conductivity
        frequency = self.tx_antenna.frequency

        eta = np.sqrt(epsilon_r - 1j * conductivity / (2 * np.pi * frequency * epsilon_0))
        cos_theta_t = np.sqrt(1 - (1 / eta)**2 * (1 - np.cos(incident_angle)**2))

        reflection_coefficient = (np.cos(incident_angle) - eta * cos_theta_t) / (np.cos(incident_angle) + eta * cos_theta_t)

        return reflection_coefficient
    
    def calculate_reflection_coefficient_TM(self, incident_angle, material):
        epsilon_r = material.permittivity
        conductivity = material.conductivity
        frequency = self.tx_antenna.frequency

        eta = np.sqrt(epsilon_r - 1j * conductivity / (2 * np.pi * frequency * epsilon_0))
        cos_theta_t = np.sqrt(1 - (1 / eta)**2 * (1 - np.cos(incident_angle)**2))

        reflection_coefficient = (eta * np.cos(incident_angle) - cos_theta_t) / (eta * np.cos(incident_angle) + cos_theta_t)

        return reflection_coefficient
    
    def calculate_transmission_coefficient_TE(self, incident_angle, material):
        epsilon_r = material.permittivity
        conductivity = material.conductivity
        frequency = self.tx_antenna.frequency

        eta = np.sqrt(epsilon_r - 1j * conductivity / (2 * np.pi * frequency * epsilon_0))
        cos_theta_t = np.sqrt(1 - (1 / eta)**2 * (1 - np.cos(incident_angle)**2))

        transmission_coefficient = 2 * np.cos(incident_angle) / (np.cos(incident_angle) + eta * cos_theta_t)

        return transmission_coefficient
    
    def calculate_transmission_coefficient_TM(self, incident_angle, material):
        epsilon_r = material.permittivity
        conductivity = material.conductivity
        frequency = self.tx_antenna.frequency

        eta = np.sqrt(epsilon_r - 1j * conductivity / (2 * np.pi * frequency * epsilon_0))
        cos_theta_t = np.sqrt(1 - (1 / eta)**2 * (1 - np.cos(incident_angle)**2))

        transmission_coefficient = 2 * eta * np.cos(incident_angle) / (eta * np.cos(incident_angle) + cos_theta_t)

        return transmission_coefficient
    
    def calculate_refracted_angle(self, incident_angle, material):
        epsilon_r = material.permittivity
        conductivity = material.conductivity
        frequency = self.tx_antenna.frequency

        eta = np.sqrt(epsilon_r - 1j * conductivity / (2 * np.pi * frequency * epsilon_0))
        refracted_angle = np.arcsin(np.sin(incident_angle) / eta.real)

        return refracted_angle

    def generate_contour_map(self):
        for i in range(self.rx_grid.resolution):
            for j in range(self.rx_grid.resolution):
                cell_coords = (i * self.rx_grid.cell_size, j * self.rx_grid.cell_size)
                cell_bbox = (cell_coords[0], cell_coords[1], cell_coords[0] + self.rx_grid.cell_size, cell_coords[1] + self.rx_grid.cell_size)
                rays_in_cell = self.quadtree.intersect(cell_bbox)
                
                # Calcular el punto de cálculo para la celda actual
                calculation_point = (cell_coords[0] + self.rx_grid.cell_size / 2, cell_coords[1] + self.rx_grid.cell_size / 2)
                
                received_power = self.rx_grid.calculate_received_power(rays_in_cell, frequency=2.4e9, calculation_point=calculation_point)
                
                # Agregar una pequeña constante al valor de received_power antes de calcular el logaritmo
                received_power_dbm = 10 * math.log10(received_power + 1e-12) + 30  # Convertir a dBm
                
                self.rx_grid.received_power[j, i] = received_power_dbm
        
        self.plot()

    def plot(self):
        fig, ax = plt.subplots(figsize=(8, 4.8))
        X, Y = self.rx_grid.grid
        contour = ax.contourf(X, Y, self.rx_grid.received_power, cmap='RdYlGn')
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
        self.width, self.height = int(screen_info.current_w * 0.9), int(screen_info.current_h * 0.9)
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
    material = Material(2.8, 0.0001, 5)

    # initialize border walls
    walls.append(Wall((0, 0), (width - 1, 0), material))  # top Wall
    walls.append(Wall((0, 0), (0, height - 1), material))  # left Wall
    walls.append(Wall((0, height - 1), (width - 1, height - 1), material))  # bottom Wall
    walls.append(Wall((width - 1, 0), (width - 1, height - 1), material))  # right Wall

    return walls

def create_random_walls(width, height, num_walls=20, min_wall_height=50, min_wall_distance=20):
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
    width, height = 800, 600
    environment = Environment(dimensions=(width, height))

    # Crear paredes aleatorias
    walls = initializeBorders(width, height)
    randomWalls = create_random_walls(width, height)
    walls = randomWalls + walls

    walls = initialize_realistic_map(width, height, material=Material(2.8, 0.0001, 5))

    for wall in walls:
        environment.add_obstacle(wall)

    # Crear la antena transmisora
    tx_antenna = Antenna(location=(500, 400), tx_power=10, radiation_pattern=None, frequency=2.4e9)

    # Crear la cuadrícula de receptores
    rx_grid = ReceiverGrid(dimensions=(width, height), resolution=50)

    # añadir resolucion angular
    # Crear el simulador
    simulator = Simulator(environment, tx_antenna, rx_grid, num_rays=360, min_power=1e-6, max_reflections=2, max_transmissions=1)
    # simulator.launch_rays()
    # simulator.generate_contour_map()


    # Crear el visualizador
    visualizer = SimulationVisualizer(simulator)
    visualizer.ray_launching(fps=30)

