import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches 

class FloorPlan:
    def __init__(self, width, height, obstacles):
        self.width = width
        self.height = height
        self.obstacles = obstacles

class RayTracing:
    def __init__(self, floor_plan, tx_pos, freq, tx_power):
        self.floor_plan = floor_plan
        self.tx_pos = tx_pos
        self.freq = freq
        self.tx_power = tx_power
        self.propagation_model = self.init_propagation_model()

    def init_propagation_model(self):
        """Initialize the parameters for the propagation model."""
        c = 3e8  # Speed of light
        wavelength = c / self.freq
        return {'wavelength': wavelength}

    def trace_ray(self, pos, angle, max_reflections=5):
        """Trace a ray from the given position and angle, with a maximum number of reflections."""
        rx_pos = pos
        ray_path = [rx_pos]
        total_path_loss = 0
        for _ in range(max_reflections):
            # Check for intersections with obstacles
            intersection, new_angle, obstacle_loss = self.find_intersection(rx_pos, angle)
            if intersection is None:
                break
            rx_pos = intersection
            angle = new_angle
            ray_path.append(rx_pos)
            total_path_loss += obstacle_loss

        # Calculate the signal strength at the final position
        distance = np.linalg.norm(np.array(rx_pos) - np.array(self.tx_pos))
        path_loss = self.calculate_path_loss(distance)
        total_path_loss += path_loss
        return ray_path, total_path_loss

    def find_intersection(self, pos, angle):
        """Find the intersection point of a ray with the nearest obstacle, and the new angle after reflection."""
        min_dist = float('inf')
        nearest_intersection = None
        nearest_angle = angle
        nearest_loss = 0

        for obstacle in self.floor_plan.obstacles:
            if len(obstacle) == 4:
                x1, y1, x2, y2 = obstacle
                loss = 0
            else:
                x1, y1, x2, y2, loss = obstacle
            # Calculate intersection point and new angle
            intersection, new_angle = self.ray_obstacle_intersection(pos, angle, (x1, y1), (x2, y2))
            if intersection is not None:
                dist = np.linalg.norm(np.array(intersection) - np.array(pos))
                if dist < min_dist:
                    min_dist = dist
                    nearest_intersection = intersection
                    nearest_angle = new_angle
                    nearest_loss = loss

        return nearest_intersection, nearest_angle, nearest_loss

    def ray_obstacle_intersection(self, ray_start, ray_angle, obstacle_start, obstacle_end):
        """Calculate the intersection point of a ray and an obstacle, and the new angle after reflection."""
        x1, y1 = ray_start
        x2, y2 = obstacle_start
        x3, y3 = obstacle_end

        # Calculate the slope and intercept of the ray
        m1 = np.tan(ray_angle)
        b1 = y1 - m1 * x1

        # Calculate the slope and intercept of the obstacle
        if x3 - x2 == 0:
            # Vertical obstacle
            if np.cos(ray_angle) == 0:
                return None, None
            x_int = x2
            y_int = m1 * x_int + b1
        else:
            m2 = (y3 - y2) / (x3 - x2)
            b2 = y2 - m2 * x2

            # Find the intersection point
            if m1 == m2:
                return None, None
            x_int = (b2 - b1) / (m1 - m2)
            y_int = m1 * x_int + b1

        # Check if the intersection point is within the obstacle
        if x_int >= min(x2, x3) and x_int <= max(x2, x3) and y_int >= min(y2, y3) and y_int <= max(y2, y3):
            # Calculate the new angle after reflection
            normal_angle = np.arctan2(y3 - y2, x3 - x2)
            incident_angle = np.arctan2(y_int - y1, x_int - x1)
            reflected_angle = 2 * normal_angle - incident_angle
            return (x_int, y_int), reflected_angle
        else:
            return None, None

    def calculate_path_loss(self, distance):
        """Calculate the path loss based on the distance and the propagation model."""
        wavelength = self.propagation_model['wavelength']
        # Ensure distance is non-zero by adding a small epsilon value
        epsilon = 1e-9
        path_loss_db = 20 * np.log10(4 * np.pi * (distance + epsilon) / wavelength)
        return path_loss_db

    def simulate_coverage(self, resolution=0.7, num_rays=1440):
        """Simulate the RF signal coverage in the floor plan."""
        x = np.arange(0, self.floor_plan.width, resolution)
        y = np.arange(0, self.floor_plan.height, resolution)
        X, Y = np.meshgrid(x, y)
        coverage_map = np.zeros_like(X)
        
        for i, x_val in enumerate(x):
            for j, y_val in enumerate(y):
                print(f"Simulating coverage at position ({x_val}, {y_val})...")  # Logging statement
                ray_paths = []
                total_path_loss = 0
                for angle in np.linspace(0, 2*np.pi, num_rays, endpoint=False):
                    ray_path, path_loss = self.trace_ray((x_val, y_val), angle)
                    ray_paths.append(ray_path)
                    total_path_loss += path_loss
                avg_path_loss = total_path_loss / num_rays
                coverage_map[j][i] = self.tx_power - avg_path_loss

        return X, Y, coverage_map


def create_heatmap(X, Y, rx_power_total_dbm, device_positions, obstacles):
    plt.figure(figsize=(8, 4.8))
    contour = plt.contourf(X, Y, rx_power_total_dbm, cmap='RdYlGn')
    plt.colorbar(contour, label='Potencia de señal recibida (dBm)')
    
    for i, pos in enumerate(device_positions):
        plt.plot(pos[0], pos[1], 'ro', markersize=10, label=f'Dispositivo Wi-Fi {i+1}')
    
    for obstacle in obstacles:
        if len(obstacle) == 4:
            x1, y1, x2, y2 = obstacle
        else:
            x1, y1, x2, y2, _ = obstacle
        plt.plot([x1, x2], [y1, y2], 'k-', linewidth=2)
    
    plt.xlabel('Distancia (m)')
    plt.ylabel('Distancia (m)')
    plt.title('Mapa de calor de la señal de RF con obstáculos')
    plt.legend()
    plt.tight_layout()
    plt.show()

def main():
    # Example usage
    obstacles = [
        (0, 0, 10, 0, 5),
        (0, 0, 0, 10, 5),
        (10, 0, 10, 10, 5),
        (0, 10, 10, 10, 5),
        # (2, 1, 2, 5, 5),  # Obstacle 1 with 5 dB loss
        # (4, 2, 6, 2, 3),  # Obstacle 2 with 3 dB loss
        (4, 4, 6, 4, 3),  # Obstacle 3 with 3 dB loss
        # (8, 1, 8, 5, 5)   # Obstacle 4 with 5 dB loss
    ]
    floor_plan = FloorPlan(10, 10, obstacles)
    tx_pos = (6, 6)
    freq = 2.4e9  # 2.4 GHz

    tx_power = 20  # Potencia de transmisión de 20 dBm
    ray_tracer = RayTracing(floor_plan, tx_pos, freq, tx_power)
    X, Y, coverage_map = ray_tracer.simulate_coverage()
    
    # Save the coverage map to a file
    np.savetxt("coverage_map.txt", coverage_map, fmt="%.2f")
    
    # Visualize the coverage map using the create_heatmap function
    create_heatmap(X, Y, coverage_map, [tx_pos], obstacles)

if __name__ == "__main__":
    main()