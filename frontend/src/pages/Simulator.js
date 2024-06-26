import React, { useState, useEffect, useCallback } from 'react';
import { getBuildingData } from '../services/apiService';
import ContourMap from '../components/ContourMap';
import ConfigurationModal from '../components/ConfigurationModal';
import { io } from 'socket.io-client';
import { API_BASE_URL } from '../config';

const SIMULATION_TYPES = {
  SIGNAL_PROPAGATION: 'Propagación de señal',
  CHANNEL_INTERFERENCE: 'Interferencia de canales',
  WIFI_CHANNEL_ALLOCATION: 'Asignación de canales WiFi'
};

const Simulator = () => {
  const [buildings, setBuildings] = useState([]);
  const [selectedBuilding, setSelectedBuilding] = useState(null);
  const [selectedFloor, setSelectedFloor] = useState(null);
  const [selectedSimulation, setSelectedSimulation] = useState(null);
  const [simulationResult, setSimulationResult] = useState(null);
  const [error, setError] = useState(null);
  const [isConfigModalOpen, setIsConfigModalOpen] = useState(false);
  const [simulationProgress, setSimulationProgress] = useState(0);
  const [socket, setSocket] = useState(null);

  useEffect(() => {
    const fetchBuildings = async () => {
      try {
        const data = await getBuildingData();
        console.log('Fetched building data:', data);
        setBuildings(data);
      } catch (error) {
        console.error('Error fetching building data:', error);
        setError('Error al cargar los datos de los edificios.');
      }
    };
    fetchBuildings();

    // Configurar socket.io
    console.log('Connecting to socket at:', API_BASE_URL);
    const newSocket = io(API_BASE_URL);
    setSocket(newSocket);

    return () => {
      console.log('Disconnecting socket');
      newSocket.disconnect();
    };
  }, []);

  useEffect(() => {
    if (socket) {
      socket.on('connect', () => {
        console.log('Socket connected');
      });

      socket.on('disconnect', () => {
        console.log('Socket disconnected');
      });

      socket.on('simulation_progress', (data) => {
        console.log('Received simulation progress:', data);
        setSimulationProgress(data.progress);
      });

      socket.on('simulation_result', (data) => {
        console.log('Received simulation result:', data);
        setSimulationResult(data);
        setSimulationProgress(100);
      });

      socket.on('simulation_error', (data) => {
        console.error('Received simulation error:', data);
        setError(data.error);
        setSimulationProgress(0);
      });
    }
  }, [socket]);

  const handleBuildingChange = (e) => {
    const building = buildings.find(b => b.name === e.target.value);
    console.log('Selected building:', building);
    setSelectedBuilding(building);
    setSelectedFloor(null);
    setSimulationResult(null);
    setError(null);
  };

  const handleFloorChange = (e) => {
    const floor = selectedBuilding.floors.find(f => f.name === e.target.value);
    console.log('Selected floor:', floor);
    setSelectedFloor(floor);
    setSimulationResult(null);
  };

  const handleSimulationChange = (e) => {
    console.log('Selected simulation:', e.target.value);
    setSelectedSimulation(e.target.value);
    setSimulationResult(null);
  };

  const handleConfigModalOpen = () => {
    setIsConfigModalOpen(true);
  };

  const handleConfigModalClose = () => {
    setIsConfigModalOpen(false);
  };

  const handleConfigSubmit = (config) => {
    setIsConfigModalOpen(false);
    setSimulationProgress(0);
    setSimulationResult(null);
    setError(null);

    if (socket) {
      const simulationData = {
        config: {
          ...config,
          width: selectedFloor.width,
          height: selectedFloor.height
        },
        building: selectedBuilding.name,
        floor: selectedFloor.name
      };
      console.log('Emitting start_simulation event:', simulationData);
      socket.emit('start_simulation', simulationData);
    }
  };

  const renderSimulationResult = useCallback(() => {
    if (!simulationResult) return null;

    switch (selectedSimulation) {
      case SIMULATION_TYPES.SIGNAL_PROPAGATION:
      case SIMULATION_TYPES.CHANNEL_INTERFERENCE:
        return (
          <ContourMap 
            geoJsonData={selectedFloor.geoJsonData} 
            simulationData={simulationResult.received_power} 
            width={800} 
            height={600} 
          />
        );

      case SIMULATION_TYPES.WIFI_CHANNEL_ALLOCATION:
        return (
          <table className="min-w-full bg-white">
            <thead>
              <tr>
                <th className="px-4 py-2">ONT ID</th>
                <th className="px-4 py-2">Posición X</th>
                <th className="px-4 py-2">Posición Y</th>
                <th className="px-4 py-2">Canal WiFi</th>
              </tr>
            </thead>
            <tbody>
              {simulationResult.rays_data.map((result, index) => (
                <tr key={index}>
                  <td className="border px-4 py-2">{result.ontId}</td>
                  <td className="border px-4 py-2">{result.x.toFixed(2)}</td>
                  <td className="border px-4 py-2">{result.y.toFixed(2)}</td>
                  <td className="border px-4 py-2">{result.channel}</td>
                </tr>
              ))}
            </tbody>
          </table>
        );

      default:
        return null;
    }
  }, [simulationResult, selectedSimulation, selectedFloor]);

  return (
    <div className="flex-1 p-4">
      <div className="bg-white p-4 rounded-md shadow-md">
        <h2 className="text-lg font-bold mb-4">Simulador de Configuración</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
          <select onChange={handleBuildingChange} className="border p-2 rounded">
            <option value="">Seleccione un edificio</option>
            {buildings.map(b => (
              <option key={b.name} value={b.name}>{b.name}</option>
            ))}
          </select>
          <select onChange={handleFloorChange} className="border p-2 rounded" disabled={!selectedBuilding}>
            <option value="">Seleccione una planta</option>
            {selectedBuilding?.floors.map(f => (
              <option key={f.name} value={f.name}>{f.name}</option>
            ))}
          </select>
          <select onChange={handleSimulationChange} className="border p-2 rounded">
            <option value="">Seleccione una simulación</option>
            {Object.values(SIMULATION_TYPES).map(s => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
        </div>
        <button 
          onClick={handleConfigModalOpen} 
          className="bg-blue-500 text-white px-4 py-2 rounded mb-4"
          disabled={!selectedBuilding || !selectedFloor || !selectedSimulation}
        >
          Configurar y Ejecutar Simulación
        </button>
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
            <span className="block sm:inline">{error}</span>
          </div>
        )}
        {simulationProgress > 0 && simulationProgress < 100 && (
          <div className="mb-4">
            <p>Progreso de la simulación: {simulationProgress}%</p>
            <div className="w-full bg-gray-200 rounded-full h-2.5 dark:bg-gray-700">
              <div className="bg-blue-600 h-2.5 rounded-full" style={{width: `${simulationProgress}%`}}></div>
            </div>
          </div>
        )}
        {simulationResult && (
          <div className="mt-4">
            <h3 className="text-md font-semibold mb-2">Resultado de la Simulación</h3>
            {renderSimulationResult()}
          </div>
        )}
      </div>
      <ConfigurationModal 
        isOpen={isConfigModalOpen}
        onClose={handleConfigModalClose}
        onSubmit={handleConfigSubmit}
      />
    </div>
  );
};

export default Simulator;