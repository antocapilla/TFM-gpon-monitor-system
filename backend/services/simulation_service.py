import numpy as np
import math
from typing import List
from models.manager_model import ONTPosition

class SimulationService:
    def __init__(self):
        self.NUM_RAYS = 360
        self.NUM_REFLECTIONS = 3
        self.MAX_DISTANCE = 1000  # Ajustado para escala de píxeles

    def process_geojson(self, geojson_data):
        walls = []
        for feature in geojson_data['features']:
            geometry = feature['geometry']
            if geometry['type'] == 'Polygon':
                walls.extend(self.polygon_to_lines(geometry['coordinates'][0]))
            elif geometry['type'] == 'LineString':
                walls.extend(self.linestring_to_lines(geometry['coordinates']))
        return walls

    def polygon_to_lines(self, polygon):
        return [np.array([polygon[i], polygon[i+1]]) for i in range(len(polygon)-1)]

    def linestring_to_lines(self, linestring):
        return [np.array([linestring[i], linestring[i+1]]) for i in range(len(linestring)-1)]

    def generate_rays(self, origin, walls_points):
        angles = np.linspace(0, 2 * np.pi, self.NUM_RAYS, endpoint=False)
        directions = np.column_stack((np.cos(angles), np.sin(angles)))

        all_rays = []

        for i in range(self.NUM_RAYS):
            ro = origin
            rd = directions[i]
            amplitude = 1.0

            ray_segments = []
            last_wall_index = -1

            for _ in range(self.NUM_REFLECTIONS + 1):
                end_point = ro + self.MAX_DISTANCE * rd

                intersection_points, valid_intersections, t, wall_normals = self.collider(walls_points, np.array([ro]), np.array([rd]))

                if last_wall_index != -1:
                    valid_intersections[0][last_wall_index] = False

                valid_points = intersection_points[0][valid_intersections[0]]
                valid_t = t[0][valid_intersections[0]]

                if len(valid_points) > 0:
                    nearest_index = np.argmin(valid_t)
                    nearest_point = valid_points[nearest_index]
                    nearest_normal = wall_normals[valid_intersections[0]][nearest_index]

                    ray_segments.append((amplitude, ro, nearest_point))

                    continuation_amplitude = amplitude * 0.5
                    continuation_end_point = nearest_point + self.MAX_DISTANCE * rd
                    ray_segments.append((continuation_amplitude, nearest_point, continuation_end_point))

                    ro = nearest_point
                    rd = rd - 2 * np.dot(rd, nearest_normal) * nearest_normal
                    amplitude *= 0.75

                    last_wall_index = np.where(valid_intersections[0])[0][nearest_index]
                else:
                    ray_segments.append((amplitude, ro, end_point))
                    break

            all_rays.extend(ray_segments)

        return all_rays

    def collider(self, walls_points, ray_origins, ray_directions):
        wall_vectors = walls_points[:, 1] - walls_points[:, 0]
        wall_normals = np.column_stack((-wall_vectors[:, 1], wall_vectors[:, 0]))
        wall_normals = wall_normals / np.linalg.norm(wall_normals, axis=1)[:, np.newaxis]

        diff_points = walls_points[:, 0] - ray_origins[:, np.newaxis, :]

        numerator = np.einsum('ijk,jk->ij', diff_points, wall_normals)
        denominator = np.einsum('ij,kj->ik', ray_directions, wall_normals) 

        with np.errstate(divide='ignore', invalid='ignore'):
            t = np.where(denominator != 0, numerator / denominator, np.inf)

        intersection_points = ray_origins[:, np.newaxis, :] + t[..., np.newaxis] * ray_directions[:, np.newaxis, :]

        wall_lengths = np.linalg.norm(wall_vectors, axis=1)
        wall_directions = wall_vectors / wall_lengths[:, np.newaxis]

        relative_positions = intersection_points - np.expand_dims(walls_points[:, 0], axis=0)
        projections = np.einsum('ijk,jk->ij', relative_positions, wall_directions)

        valid_intersections = (projections >= 0) & (projections <= wall_lengths) & (t >= 0)

        return intersection_points, valid_intersections, t, wall_normals

    def calculate_signal_strength(self, origin, point, scale):
        distance = np.linalg.norm(point - origin) * scale
        # Calculamos la potencia en dBm primero
        power_dbm = max(-100, -20 * math.log10(distance) - 40)
        # Convertimos dBm a watts
        power_watts = 10 ** ((power_dbm - 30) / 10)
        return power_watts

    def run_simulation(self, geojson_data, onts: List[ONTPosition], scale):
        self.walls_points = self.process_geojson(geojson_data)
        
        all_coords = np.vstack(self.walls_points)
        min_x, min_y = np.min(all_coords, axis=0)
        max_x, max_y = np.max(all_coords, axis=0)

        resolution = 10  # Ajustar según necesidad
        x_values = np.arange(min_x, max_x, resolution)
        y_values = np.arange(min_y, max_y, resolution)
        grid_x, grid_y = np.meshgrid(x_values, y_values)
        grid_points = np.column_stack((grid_x.ravel(), grid_y.ravel()))

        heatmap_data = []
        for point in grid_points:
            max_signal = -float('inf')
            for ont in onts:
                origin = np.array([ont.x, ont.y])
                signal = self.calculate_signal_strength(origin, point, scale)
                max_signal = max(max_signal, signal)
            heatmap_data.append({
                'lng': float(point[0]),
                'lat': float(point[1]),
                'value': float(max_signal)
            })

        return {
            'heatmapData': heatmap_data,
            'geoJsonData': geojson_data,
            'onts': [{'serial': ont.serial, 'x': ont.x, 'y': ont.y} for ont in onts]
        }

    def allocate_wifi_channels(self, onts: List[ONTPosition]):
        channels = [1, 6, 11]  # Canales no superpuestos en 2.4 GHz
        allocation = []
        for i, ont in enumerate(onts):
            channel = channels[i % len(channels)]
            allocation.append({
                'serial': ont.serial,
                'x': ont.x,
                'y': ont.y,
                'channel': channel,
                'status': 'Online',
                'connectedClients': np.random.randint(0, 10),
                'signalStrength': np.random.randint(-80, -30)
            })
        return allocation
