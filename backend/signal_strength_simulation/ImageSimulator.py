import numpy as np
from typing import List

import numpy as np
import matplotlib.pyplot as plt
from typing import List

class Wall:
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        self.x1, self.y1 = x1, y1
        self.x2, self.y2 = x2, y2

class Ray:
    def __init__(self, x0: float, y0: float, dx: float, dy: float):
        self.x0, self.y0 = x0, y0
        self.dx, self.dy = dx, dy
        self.reflection_points = []

class ImageTree:
    def __init__(self, x_min: float, y_min: float, x_max: float, y_max: float):
        self.x_min, self.y_min = x_min, y_min
        self.x_max, self.y_max = x_max, y_max
        self.walls: List[Wall] = []
        self.children: List[ImageTree] = []

    def add_wall(self, wall: Wall):
        self.walls.append(wall)

    def subdivide(self):
        x_mid = (self.x_min + self.x_max) / 2
        y_mid = (self.y_min + self.y_max) / 2
        self.children = [
            ImageTree(self.x_min, self.y_min, x_mid, y_mid),
            ImageTree(x_mid, self.y_min, self.x_max, y_mid),
            ImageTree(self.x_min, y_mid, x_mid, self.y_max),
            ImageTree(x_mid, y_mid, self.x_max, self.y_max)
        ]

    def find_visible_walls(self, ray: Ray) -> List[Wall]:
        visible_walls = []
        for wall in self.walls:
            if self.intersects(ray, wall):
                visible_walls.append(wall)
        for child in self.children:
            visible_walls.extend(child.find_visible_walls(ray))
        return visible_walls

    def intersects(self, ray: Ray, wall: Wall) -> bool:
        x1, y1 = ray.x0, ray.y0
        x2, y2 = ray.x0 + ray.dx, ray.y0 + ray.dy
        x3, y3 = wall.x1, wall.y1
        x4, y4 = wall.x2, wall.y2

        denom = ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
        if denom == 0:
            return False

        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom

        if 0 <= ua <= 1 and 0 <= ub <= 1:
            return True
        else:
            return False

def trace_ray(image_tree: ImageTree, ray: Ray, max_reflections: int = 3) -> Ray:
    visible_walls = image_tree.find_visible_walls(ray)
    for wall in visible_walls:
        reflection_point = calculate_reflection_point(ray, wall)
        ray.reflection_points.append(reflection_point)
        if len(ray.reflection_points) <= max_reflections:
            new_ray = Ray(reflection_point[0], reflection_point[1], -ray.dx, -ray.dy)
            trace_ray(image_tree, new_ray, max_reflections - 1)
    return ray

def calculate_reflection_point(ray: Ray, wall: Wall) -> (float, float):
    x1, y1 = ray.x0, ray.y0
    x2, y2 = ray.x0 + ray.dx, ray.y0 + ray.dy
    x3, y3 = wall.x1, wall.y1
    x4, y4 = wall.x2, wall.y2

    denom = ((y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1))
    ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
    x_intersect = x1 + ua * (x2 - x1)
    y_intersect = y1 + ua * (y2 - y1)

    return x_intersect, y_intersect

def compute_received_power(rays: List[Ray], tx_power: float, frequency: float, distance: float) -> float:
    total_power = 0
    for ray in rays:
        path_loss = friis_path_loss(tx_power, frequency, distance, len(ray.reflection_points))
        total_power += path_loss
    return total_power

def friis_path_loss(tx_power: float, frequency: float, distance: float, num_reflections: int) -> float:
    c = 299792458  # Speed of light in m/s
    wavelength = c / frequency
    reflection_loss = 0.5  # Assuming 50% loss per reflection
    eps = 1e-10  # Small constant to avoid division by zero
    path_loss = (wavelength / (4 * np.pi * (distance + eps))) ** 2 * (reflection_loss ** num_reflections)
    received_power = tx_power * path_loss
    return received_power

def compute_coverage_map(image_tree: ImageTree, tx_power: float, frequency: float, resolution: int = 100) -> np.ndarray:
    x_coords = np.linspace(image_tree.x_min, image_tree.x_max, resolution)
    y_coords = np.linspace(image_tree.y_min, image_tree.y_max, resolution)
    coverage_map = np.zeros((resolution, resolution))

    for i, x in enumerate(x_coords):
        for j, y in enumerate(y_coords):
            ray = Ray(x, y, 1, 0)
            traced_ray = trace_ray(image_tree, ray)
            distance = np.sqrt((x - traced_ray.x0) ** 2 + (y - traced_ray.y0) ** 2)
            received_power = compute_received_power([traced_ray], tx_power, frequency, distance)
            coverage_map[j, i] = received_power

    return coverage_map

def plot_coverage_map(image_tree: ImageTree, coverage_map: np.ndarray):
    plt.figure(figsize=(8, 8))
    plt.imshow(coverage_map, cmap='viridis', origin='lower',
               extent=[image_tree.x_min, image_tree.x_max, image_tree.y_min, image_tree.y_max])
    plt.colorbar(label='Received Power (W)')

    for wall in image_tree.walls:
        plt.plot([wall.x1, wall.x2], [wall.y1, wall.y2], 'k-', linewidth=2)

    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Coverage Map')
    plt.show()

# Example usage
image_tree = ImageTree(0, 0, 10, 10)
image_tree.add_wall(Wall(1, 2, 10, 2))
image_tree.add_wall(Wall(3, 8, 6, 8))
image_tree.add_wall(Wall(2, 2, 2, 8))
image_tree.add_wall(Wall(8, 2, 8, 8))
image_tree.subdivide()

tx_power = 1  # Transmit power in watts
frequency = 2.4e9  # Frequency in Hz
resolution = 1000  # Resolution of the coverage map

coverage_map = compute_coverage_map(image_tree, tx_power, frequency, resolution)
plot_coverage_map(image_tree, coverage_map)