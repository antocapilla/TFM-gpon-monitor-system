import asyncio
import logging
from tqdm import tqdm
from signal_strength_simulation.Simulator import Simulator, Environment, Antenna, ReceiverGrid, Wall, Material
from services.manager_service import ManagerService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class SimulationService:
    @staticmethod
    async def run_simulation(sio, sid, config, building_name, floor_name):
        try:
            print(f"Entering run_simulation. SID: {sid}, Building: {building_name}, Floor: {floor_name}")
            print(f"Received config: {config}")
            
            # Obtener datos del edificio y el piso
            building = ManagerService.get_building_by_name(building_name)
            if not building:
                logger.error(f"Building {building_name} not found")
                raise ValueError(f"Building {building_name} not found")
            
            floor = next((f for f in building.floors if f.name == floor_name), None)
            if not floor:
                logger.error(f"Floor {floor_name} not found in building {building_name}")
                raise ValueError(f"Floor {floor_name} not found in building {building_name}")
            
            if not floor.geoJsonData:
                logger.error(f"No geoJsonData found for floor {floor_name}")
                raise ValueError(f"No geoJsonData found for floor {floor_name}")

            logger.info("Creating simulation environment")
            environment = Environment(dimensions=(config['width'], config['height']))
            
            # Convertir geoJsonData a paredes para la simulación
            print(f"Converting geoJsonData to walls. Features count: {len(floor.geoJsonData['features'])}")
            for feature in floor.geoJsonData['features']:
                if feature['geometry']['type'] == 'LineString':
                    coords = feature['geometry']['coordinates']
                    start_point = coords[0]
                    end_point = coords[-1]
                    wall = Wall(start_point, end_point, Material(2.8, 0.0001, 0.15))
                    environment.add_obstacle(wall)
            print(f"Walls added to environment: {len(environment.obstacles)}")
            
            logger.info("Creating antenna and receiver grid")
            tx_antenna = Antenna(
                location=(config['tx_x'], config['tx_y']),
                tx_power=config['tx_power'],
                radiation_pattern=None,
                frequency=config['frequency']
            )
            print(f"Antenna created at location: ({config['tx_x']}, {config['tx_y']})")
            
            rx_grid = ReceiverGrid(dimensions=(config['width'], config['height']), resolution=config['resolution'])
            print(f"Receiver grid created with dimensions: ({config['width']}, {config['height']}) and resolution: {config['resolution']}")
            
            logger.info("Initializing simulator")
            simulator = Simulator(
                environment,
                tx_antenna,
                rx_grid,
                num_rays=config['num_rays'],
                max_path_loss=config['max_path_loss'],
                max_reflections=config['max_reflections'],
                max_transmissions=config['max_transmissions']
            )
            print(f"Simulator initialized with num_rays: {config['num_rays']}, max_path_loss: {config['max_path_loss']}, max_reflections: {config['max_reflections']}, max_transmissions: {config['max_transmissions']}")

            total_steps = config['num_rays'] + (config['resolution'] ** 2)
            progress_bar = tqdm(total=total_steps, desc="Simulation Progress")

            async def update_progress():
                progress = int((progress_bar.n / total_steps) * 100)
                print(f"Emitting simulation progress: {progress}%")
                await sio.emit('simulation_progress', {'progress': progress}, room=sid)

            def progress_callback():
                progress_bar.update(1)
                asyncio.create_task(update_progress())

            logger.info("Launching rays")
            simulator.launch_rays(progress_callback=progress_callback)
            
            logger.info("Generating contour map")
            simulator.generate_contour_map(progress_callback=progress_callback)

            progress_bar.close()

            logger.info("Exporting simulation data")
            received_power = rx_grid.received_power.tolist()
            rays_data, walls_data = simulator.export_simulation_data()

            logger.info("Simulation completed. Sending results.")
            print(f"Received power matrix shape: {len(received_power)}x{len(received_power[0])}")
            print(f"Rays data count: {len(rays_data)}")
            print(f"Walls data count: {len(walls_data)}")
            await sio.emit('simulation_result', {
                'received_power': received_power,
                'rays_data': rays_data,
                'walls_data': walls_data
            }, room=sid)

        except Exception as e:
            logger.error(f"Error in simulation: {str(e)}", exc_info=True)
            await sio.emit('simulation_error', {'error': str(e)}, room=sid)