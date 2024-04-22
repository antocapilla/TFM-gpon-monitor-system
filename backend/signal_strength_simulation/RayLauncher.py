import pygame
import math
import random
from pyqtree import Index

from pygame.locals import *

# define RayLauncher class
class RayLauncher:
    # constructor for new RayLauncher object
    def __init__(self, start_point, n):
        self.start_point = start_point
        self.rays = []
        self.n = n
        self.quadtree = None  # Agrega el atributo quadtree
        for i in range(0, 360, int(360 / n)):
            direction = (math.cos(math.radians(i)), math.sin(math.radians(i)))
            self.rays.append(Ray(self.start_point, direction))

    # draws RayLauncher by checking for ray collisions and drawing rays appropriately
    def launchRays(self, walls):
        reflected_rays = []
        
        # Inicializa el quadtree con los límites adecuados
        self.quadtree = Index(bbox=(0, 0, pygame.display.get_surface().get_width(), pygame.display.get_surface().get_height()))
        
        for ray in self.rays:
            ray.start_point = self.start_point
            closest = 1000000
            closestPoint = None
            reflected_ray = None
            for wall in walls:
                intersection = ray.collide(wall)
                if intersection != False:
                    distance = math.sqrt((ray.start_point[0] - intersection[0])**2 + (ray.start_point[1] - intersection[1])**2)
                    if distance < closest:
                        closest = distance
                        closestPoint = intersection[:2]
                        reflection_coeff = intersection[2]
                        reflected_ray = intersection[3]

            if closestPoint is not None:
                ray.end_point = closestPoint
                reflected_rays.append(reflected_ray)  # Agrega el rayo reflejado a la lista
                self.quadtree.insert(ray, bbox=(ray.start_point[0], ray.start_point[1], ray.end_point[0], ray.end_point[1]))  # Inserta el rayo en el quadtree

        # print(len(reflected_rays))
        return self.rays  # Devuelve la lista de rayos reflejados

# define Ray class
class Ray:
    # constructor for new Ray object
    def __init__(self, start_point, direction):
        self.start_point = start_point
        self.end_point = None
        self.direction = direction
        self.los = True

    # function to check if and where a ray collides with a wall object
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

            # Calcula el ángulo de incidencia
            incident_angle = math.atan2(self.direction[1], self.direction[0])
            wall_angle = math.atan2(wall.end_point[1] - wall.start_point[1], wall.end_point[0] - wall.start_point[1])
            angle = incident_angle - wall_angle

            # Calcula el coeficiente de reflexión de Fresnel
            epsilon_r = wall.epsilon_r
            sin_angle = math.sin(angle)
            cos_angle = math.cos(angle)
            sqrt_term = math.sqrt(epsilon_r - sin_angle**2)
            r_perp = (cos_angle - sqrt_term) / (cos_angle + sqrt_term)
            r_par = (epsilon_r * cos_angle - sqrt_term) / (epsilon_r * cos_angle + sqrt_term)
            reflection_coeff = (r_perp**2 + r_par**2) / 2

            # Genera un nuevo rayo reflejado
            reflected_dirX = self.direction[0] * math.cos(2 * angle) - self.direction[1] * math.sin(2 * angle)
            reflected_dirY = self.direction[0] * math.sin(2 * angle) + self.direction[1] * math.cos(2 * angle)
            reflected_ray = Ray((px, py), (reflected_dirX, reflected_dirY))
            reflected_ray.los = False

            return (px, py, reflection_coeff, reflected_ray)
        else:
            return False

# define wall class
class Wall:
    # constructor for Wall object
    def __init__(self, start_point, end_point, epsilon_r=4.0, color=(255, 255, 255), width=5):
        self.start_point = start_point
        self.end_point = end_point
        self.epsilon_r = epsilon_r  # Permitividad relativa del material
        self.color = color
        self.width = width

    # draws Wall
    def show(self, surface):
        pygame.draw.line(surface, self.color, self.start_point, self.end_point, self.width)

def drawElements(display, walls, rays):
    # draw Walls
    for wall in walls:
        wall.show(display)
    
    for ray in rays:
        if ray.end_point is not None:
            pygame.draw.line(display, (255, 255, 255), ray.start_point, ray.end_point)

def initializeWalls(width, height):
    walls = []

    # initialize border walls
    walls.append(Wall((0, 0), (width - 1, 0)))  # top Wall
    walls.append(Wall((0, 0), (0, height - 1)))  # left Wall
    walls.append(Wall((0, height - 1), (width - 1, height - 1)))  # bottom Wall
    walls.append(Wall((width - 1, 0), (width - 1, height - 1)))  # right Wall

    # initialize random non-border walls (currently randomizes between 0 and 10 walls, but can be modified as needed)
    random_walls = createRandomWalls(width, height)
    walls.extend(random_walls)  # Añade cada pared individual en lugar de añadir la lista completa

    return walls

def createRandomWalls(width, height):
    walls = []
    for i in range(random.randint(0, 10)):
        walls.append(Wall((random.randint(0, width), random.randint(0,height)), (random.randint(0, width), random.randint(0,height))))
    return walls

def simulateRayLaunching(
    fps = 30,
    num_rays = 360,
    epsilon_r = 4.0,
    tx_position = (500, 500)
    ):
    # initialize pygame
    pygame.init()
    clock = pygame.time.Clock()

    # setup pygame display
    screen_info = pygame.display.Info()
    height, width = int(screen_info.current_h * 0.9), int(screen_info.current_w * 0.9)
    display = pygame.display.set_mode((width, height))
    pygame.display.set_caption('2DRayLaunching')
    display.fill((0,0,0))
    
    # initialize walls
    walls = initializeWalls(width, height)

    # initialize RayLauncher and its associated rays
    transmisor = RayLauncher(tx_position, num_rays)

    # main loop
    running = True

    while running:
        # fill screen with black
        display.fill((0,0,0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:   
                running = False
            elif event.type == pygame.KEYDOWN:
                # regenerates new walls
                if event.key == K_r:
                    # clear non-border walls
                    del walls[4:len(walls)]
                    # regenerate new non-border walls
                    random_walls = createRandomWalls(width, height)
                    walls.extend(random_walls)

        # set x & y position of RayLauncher to the current mouse position
        transmisor.start_point = pygame.mouse.get_pos()
        # print(pygame.mouse.get_pos())
        # transmisor.start_point = (width/2, height/2) # Fijamos en el centro el transmisor

        # Launch the arrays and calculate reflections
        rays = transmisor.launchRays(walls)# Consulta el quadtree para obtener los rayos visibles en la pantalla
        
        # visible_area = (130, 410, 425, 160)
        # visible_rays = transmisor.quadtree.intersect(visible_area)
        visible_rays = transmisor.quadtree.intersect((0, 0, display.get_width(), display.get_height()))



        drawElements(display, walls, visible_rays)  # Pasa el transmisor como argumento

        #update display
        pygame.display.update()
        clock.tick(fps)

    pygame.quit()
    quit()
   
def main():
    simulateRayLaunching()

if __name__ == "__main__":
    main()