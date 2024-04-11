import numpy as np
import matplotlib.pyplot as plt
import pygame
import math
import random
from abc import ABC, abstractmethod
from pyqtree import Index
from pygame.locals import *
from scipy.constants import mu_0, epsilon_0, pi

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
            rays.append(Ray(self.location, direction))
        return rays

    def visualize(self, display):
        pass

class Collision:
    def __init__(self, ray, point, wall):
        self.point = point
        self.wall = wall
        self.ray = ray

class Ray(Visualizable):
    def __init__(self, start_point, direction, polarization="TE"):
        self.start_point = start_point
        self.direction = direction
        self.end_point = None
        self.polarization = polarization
        # self.power = power
        self.path = []
        self.num_reflections = 0
        self.num_transmissions = 0

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

    def visualize(self, display, scale):
        if self.end_point is not None:
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

    def initialize_grid(self):
        x = np.linspace(0, self.dimensions[0], self.resolution)
        y = np.linspace(0, self.dimensions[1], self.resolution)
        grid = np.meshgrid(x, y)
        return grid

    def visualize(self, display):
        pass

class Simulator:
    def __init__(self, environment, tx_antenna, rx_grid, num_rays, max_reflections, max_transmissions):
        self.environment = environment
        self.tx_antenna = tx_antenna
        self.rx_grid = rx_grid
        self.num_rays = num_rays
        self.max_reflections = max_reflections
        self.max_transmissions = max_transmissions
        self.rays = []
        self.reflected_rays = []
        self.quadtree = Index(bbox=(0, 0, environment.dimensions[0], environment.dimensions[1]))

    def launch_rays(self):
        self.rays = []
        rays = self.tx_antenna.launch_rays(self.num_rays)

        for ray in rays:
            self.propagate_ray(ray)
        
        return self.rays  # Devolver la combinación de rayos originales y reflejados
 

    def propagate_ray(self, ray):
        # Calcular la siguiente colision
        collision = self.find_closest_collision(ray)

        if (ray.num_reflections > self.max_reflections or ray.num_transmissions > self.max_transmissions): # Hardcode: deberia de ser en funcion de la amplitud del rayo
            self.rays.append(ray)
            return # End propagation

        if collision:
            # Logica de propagacion
            
            # Calcula el rayo reflejado
            reflected_ray = self.reflect_ray(ray, collision)
            # Propagar el rayo reflejado
            self.propagate_ray(reflected_ray)
            
            # Manipula el rayo original para representar la transmisión y calcula el rayo reflectado
            self.refract_ray(ray, collision)
            # Propagar el rayo transmitido
            self.propagate_ray(ray)
        else:
            return

    def find_closest_collision(self, ray):
        closest_collision = None
        closest_distance = 1000
        for obstacle in self.environment.obstacles:
            collision = ray.collide(obstacle)
            if collision:
                distance = math.dist(ray.start_point, collision.point)
                if distance < closest_distance:
                    closest_distance = distance
                    closest_collision = collision
        if closest_collision:
            ray.end_point = closest_collision.point
            ray.path.append(ray.end_point)
            return closest_collision
            

    def reflect_ray(self, ray, collision):
        # Calcular el vector normal de la pared en el punto de colisión
        normal = collision.wall.normal_direction

        # Normalizar el vector normal
        normal_magnitude = math.sqrt(normal[0]**2 + normal[1]**2)
        normal = (normal[0] / normal_magnitude, normal[1] / normal_magnitude)

        # Calcular el ángulo de incidencia
        incident_angle = math.acos(np.dot(ray.direction, normal))

        # Calcular el coeficiente de reflexión según la polarización
        if ray.polarization == 'TE':
            reflection_coefficient = self.calculate_reflection_coefficient_TE(incident_angle, collision.wall.material)
        elif ray.polarization == 'TM':
            reflection_coefficient = self.calculate_reflection_coefficient_TM(incident_angle, collision.wall.material)

        # Calcular la dirección del rayo reflejado
        reflected_direction = (
            ray.direction[0] - 2 * np.dot(ray.direction, normal) * normal[0],
            ray.direction[1] - 2 * np.dot(ray.direction, normal) * normal[1]
        )

        # Crear el nuevo rayo reflejado
        reflected_ray = Ray(collision.point, reflected_direction)
        reflected_ray.num_reflections = ray.num_reflections + 1
        reflected_ray.num_transmissions = ray.num_transmissions
        reflected_ray.path = ray.path
        reflected_ray.path.append(collision.point)
        # reflected_ray.power = ray.power * abs(reflection_coefficient)**2

        return reflected_ray

    def refract_ray(self, ray, collision):
        # Calcular el vector normal de la pared en el punto de colisión
        normal = collision.wall.normal_direction

        # Normalizar el vector normal
        normal_magnitude = math.sqrt(normal[0]**2 + normal[1]**2)
        normal = (normal[0] / normal_magnitude, normal[1] / normal_magnitude)

        # Calcular el ángulo de incidencia
        incident_angle = math.acos(np.dot(ray.direction, normal))

        # Calcular el coeficiente de transmisión según la polarización
        if ray.polarization == 'TE':
            transmission_coefficient = self.calculate_transmission_coefficient_TE(incident_angle, collision.wall.material)
        elif ray.polarization == 'TM':
            transmission_coefficient = self.calculate_transmission_coefficient_TM(incident_angle, collision.wall.material)

        # Calcular el ángulo de refracción utilizando la ley de Snell
        refracted_angle = self.calculate_refracted_angle(incident_angle, collision.wall.material)

        # Calcular la dirección del rayo refractado
        refracted_direction = (
            math.cos(refracted_angle) * normal[0] - math.sin(refracted_angle) * normal[1],
            math.sin(refracted_angle) * normal[0] + math.cos(refracted_angle) * normal[1]
        )

        # Crear el nuevo rayo refractado
        refracted_ray = Ray(collision.point, refracted_direction)
        ray.end_point = collision.point
        ray.path.append(collision.point)
        ray.num_transmissions += 1

        # refracted_ray.power = ray.power * abs(transmission_coefficient)**2

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

import random

def create_random_walls(width, height, num_walls=10, min_wall_height=50, min_wall_distance=20):
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


# Ejemplo de uso
if __name__ == "__main__":
    # Crear el entorno con las dimensiones en metros
    width, height = 800, 600
    environment = Environment(dimensions=(width, height))

    # Crear paredes aleatorias
    walls = initializeBorders(width, height)
    randomWalls = create_random_walls(width, height)
    walls = randomWalls + walls
    for wall in walls:
        environment.add_obstacle(wall)

    # Crear la antena transmisora
    tx_antenna = Antenna(location=(400, 300), tx_power=10, radiation_pattern=None, frequency=2.4e9)

    # Crear la cuadrícula de receptores
    rx_grid = ReceiverGrid(dimensions=(width, height), resolution=50)

    # Crear el simulador
    simulator = Simulator(environment, tx_antenna, rx_grid, num_rays=2, max_reflections=0, max_transmissions=2)

    # Crear el visualizador
    visualizer = SimulationVisualizer(simulator)

    # Ejecutar la simulación
    visualizer.ray_launching(fps=30)

    