import React, { useState, useEffect } from 'react';
import ContourMap from '../components/ContourMap';
import { getBuildingData, runSimulation } from '../services/apiService';

const SIMULATION_TYPES = {
  SIGNAL_PROPAGATION: 'Propagación de señal',
  WIFI_CHANNEL_ALLOCATION: 'Asignación de canales WiFi'
};

const Simulator = () => {
  const [buildings, setBuildings] = useState([]);
  const [selectedBuilding, setSelectedBuilding] = useState('');
  const [selectedFloor, setSelectedFloor] = useState('');
  const [selectedSimulation, setSelectedSimulation] = useState('');
  const [simulationResult, setSimulationResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getBuildingData();
        setBuildings(data);
      } catch (err) {
        setError('Error al cargar los datos de los edificios.');
      }
    };
    fetchData();
  }, []);

  const generateRandomChannelAllocation = (onts) => {
    const channels2_4GHz = [1, 6, 11]; // Canales no superpuestos en 2.4 GHz
    const channels5GHz = [36, 40, 44, 48, 52, 56, 60, 64]; // Algunos canales comunes en 5 GHz
    
    return onts.map(ont => ({
      serial: ont.serial,
      status: Math.random() > 0.1 ? 'Online' : 'Offline',
      channel2_4: channels2_4GHz[Math.floor(Math.random() * channels2_4GHz.length)],
      channel5: channels5GHz[Math.floor(Math.random() * channels5GHz.length)],
      connectedClients: Math.floor(Math.random() * 20),
      signalStrength2_4: -Math.floor(Math.random() * 30 + 50), // Entre -50 y -80 dBm
      signalStrength5: -Math.floor(Math.random() * 20 + 40), // Entre -40 y -60 dBm
    }));
  };

  const handleBuildingChange = (e) => {
    setSelectedBuilding(e.target.value);
    setSelectedFloor('');
    setSelectedSimulation('');
    setSimulationResult(null);
  };

  const handleFloorChange = (e) => {
    setSelectedFloor(e.target.value);
    setSimulationResult(null);
  };

  const handleSimulationChange = (e) => {
    setSelectedSimulation(e.target.value);
    setSimulationResult(null);
  };

  const handleRunSimulation = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await runSimulation(selectedBuilding, selectedFloor, selectedSimulation);
      setSimulationResult(result);
      // console.log("Simulation result:", result); // For debugging
    } catch (err) {
      setError('Error al ejecutar la simulación. Por favor, intente nuevamente.');
      console.error("Simulation error:", err); // For debugging
    } finally {
      setIsLoading(false);
    }
  };

  const generateFakeHeatmapData = (geoJsonData, onts) => {
    const bounds = getBounds(geoJsonData);
    const [[x0, y0], [x1, y1]] = bounds;
    const points = [];
    const numPoints = 1000;

    for (let i = 0; i < numPoints; i++) {
      const lng = x0 + Math.random() * (x1 - x0);
      const lat = y0 + Math.random() * (y1 - y0);

      let maxIntensity = 0;
      onts.forEach(ont => {
        const distance = Math.sqrt(Math.pow(lng - ont.x, 2) + Math.pow(lat - ont.y, 2));
        const intensity = Math.max(0, 1 - distance / 200);  // 200 unidades de distancia máxima
        maxIntensity = Math.max(maxIntensity, intensity);
      });

      points.push({ lng, lat, value: maxIntensity });
    }

    return points;
  };

  const getBounds = (geoJsonData) => {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    geoJsonData.features.forEach(feature => {
      const coordinates = feature.geometry.type === "Polygon" 
        ? feature.geometry.coordinates[0] 
        : feature.geometry.coordinates;
      coordinates.forEach(coord => {
        minX = Math.min(minX, coord[0]);
        minY = Math.min(minY, coord[1]);
        maxX = Math.max(maxX, coord[0]);
        maxY = Math.max(maxY, coord[1]);
      });
    });
    return [[minX, minY], [maxX, maxY]];
  };

  const renderSimulationResult = () => {
    if (!simulationResult || !simulationResult.result) return null;

    console.log("Simulation Result:", simulationResult);

    switch (selectedSimulation) {
      case SIMULATION_TYPES.SIGNAL_PROPAGATION:
        return (
          <div className="mt-4 text-center">
            <h3 className="text-xl font-semibold mb-4">Mapa de propagación de señal</h3>
            <ContourMap 
              width={800} 
              height={600} 
              heatmapData={simulationResult.result.heatmapData}
              geoJsonData={simulationResult.result.geoJsonData}
              onts={simulationResult.result.onts}
            />
            {/* <ContourMap width={800} height={600} /> */}
          </div>
        );
        case SIMULATION_TYPES.WIFI_CHANNEL_ALLOCATION:
        const channelAllocation = generateRandomChannelAllocation(simulationResult.result.onts);
        return (
          <div className="mt-4">
            <h3 className="text-xl font-semibold mb-4">Asignación de canales WiFi</h3>
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Seleccionar
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    ONT ID
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Estado
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Canal 2.4 GHz
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Canal 5 GHz
                  </th>
                  <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Clientes Conectados
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {channelAllocation.map((result, index) => (
                  <tr key={index}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <input
                        type="checkbox"
                        className="form-checkbox h-5 w-5 text-blue-600"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">{result.serial}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${result.status === 'Online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                        {result.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">{result.channel2_4}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{result.channel5}</td>
                    <td className="px-6 py-4 whitespace-nowrap">{result.connectedClients}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            
            {/* Botón de mock añadido aquí */}
            <div className="mt-4 flex justify-center">
              <button
                className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              >
                Enviar configuración a dispositivos
              </button>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="container mx-auto p-4 grid grid-cols-1 md:grid-cols-3 gap-4">
      <h1 className="text-3xl font-bold mb-6 col-span-3 text-center">Simulador de Configuración</h1>
  
      {/* Sidebar for controls */}
      <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 order-2 md:order-1 md:col-span-1"> 
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="building">
            Edificio
          </label>
          <select
            id="building"
            value={selectedBuilding}
            onChange={handleBuildingChange}
            className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
          >
            <option value="">Seleccione un edificio</option>
            {buildings.map(building => (
              <option key={building.name} value={building.name}>{building.name}</option>
            ))}
          </select>
        </div>
  
        <div className="mb-4">
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="floor">
            Planta
          </label>
          <select
            id="floor"
            value={selectedFloor}
            onChange={handleFloorChange}
            className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            disabled={!selectedBuilding}
          >
            <option value="">Seleccione una planta</option>
            {selectedBuilding && buildings.find(b => b.name === selectedBuilding).floors.map(floor => (
              <option key={floor.name} value={floor.name}>{floor.name}</option>
            ))}
          </select>
        </div>
  
        <div className="mb-4"> 
          <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="simulation">
            Tipo de Simulación
          </label>
          <select
            id="simulation"
            value={selectedSimulation}
            onChange={handleSimulationChange}
            className="shadow border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
            disabled={!selectedFloor}
          >
            <option value="">Seleccione una simulación</option>
            {Object.entries(SIMULATION_TYPES).map(([key, value]) => (
              <option key={key} value={value}>{value}</option>
            ))}
          </select>
        </div>
  
        <div className="flex items-center justify-center">
          <button
            onClick={handleRunSimulation}
            disabled={!selectedSimulation || isLoading}
            className={`bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline ${
              (!selectedSimulation || isLoading) ? 'opacity-50 cursor-not-allowed' : ''
            }`}
          >
            {isLoading ? 'Ejecutando...' : 'Ejecutar Simulación'}
          </button>
        </div>
      </div>
  
      {/* Main area for simulation results */}
      <div className="col-span-3 md:col-span-2 order-1 md:order-2">
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
            <strong className="font-bold">Error: </strong>
            <span className="block sm:inline">{error}</span>
          </div>
        )}
  
        <div className="border rounded-md p-4 flex flex-col h-full"> 
          {!simulationResult && (
            <div className="flex-grow flex items-center justify-center text-gray-500">
              Seleccione un edificio y una planta para comenzar la simulación
            </div>
          )}
          {simulationResult && renderSimulationResult()}
        </div>
      </div>
    </div>
  );
};

export default Simulator;