import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import { format, parseISO } from 'date-fns';

import { getBuildingData, getMonitoringConfiguration } from '../services/apiService';

const metricLabels = {
  connectedUsers: 'Usuarios Conectados',
  bandwidth: 'Ancho de Banda (Mbps)',
  uptime: 'Uptime (%)',
};

function RealTimeMonitor() {
  const [usageData, setUsageData] = useState([]);
  const [buildings, setBuildings] = useState([]);
  const [selectedBuilding, setSelectedBuilding] = useState(null);
  const [selectedFloor, setSelectedFloor] = useState(null);
  const [selectedONT, setSelectedONT] = useState(null);
  const [selectedTab, setSelectedTab] = useState('realtime');
  const [selectedMetrics, setSelectedMetrics] = useState(['connectedUsers', 'bandwidth', 'uptime']);
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [collectionInterval, setCollectionInterval] = useState(5);
  const [configuration, setConfiguration] = useState({});

  useEffect(() => {
    const fetchBuildingData = async () => {
      const data = await getBuildingData();
      setBuildings(data);
    };

    const fetchConfiguration = async () => {
      const config = await getMonitoringConfiguration();
      setConfiguration(config);
    };

    fetchBuildingData();
    fetchConfiguration();
  }, []);

  useEffect(() => {
    // Simular la obtención de datos de uso en tiempo real
    const fetchUsageData = () => {
      const newUsageData = generateFakeUsageData();
      setUsageData(newUsageData);
    };

    fetchUsageData();
    const intervalId = setInterval(fetchUsageData, configuration.collectionInterval * 60 * 1000);
    return () => clearInterval(intervalId);
  }, [configuration.collectionInterval]);

  // Genera datos de uso falsos para simular la obtención de datos en tiempo real
  const generateFakeUsageData = () => {
    const newUsageData = [];
    const ontIds = ['ONT-1', 'ONT-2', 'ONT-3', 'ONT-4', 'ONT-5', 'ONT-6', 'ONT-7', 'ONT-8'];
    const startTime = new Date('2023-06-17T10:00:00');
    const endTime = new Date('2023-06-17T12:00:00');
    const interval = 5 * 60 * 1000; // 5 minutos en milisegundos

    for (let time = startTime; time <= endTime; time = new Date(time.getTime() + interval)) {
      ontIds.forEach((ontId) => {
        const connectedUsers = Math.floor(Math.random() * 50) + 10;
        const bandwidth = Math.floor(Math.random() * 100) + 50;
        const uptime = Math.random() * 2 + 97;
        newUsageData.push({ ontId, timestamp: time.toISOString(), connectedUsers, bandwidth, uptime });
      });
    }

    return newUsageData;
  };

  // Obtener los datos de resumen según el nivel seleccionado
  const getSummaryData = () => {
    if (selectedONT) {
      const ontData = buildings
        .find((building) => building.id === selectedBuilding)
        .floors.find((floor) => floor.id === selectedFloor)
        .onts.find((ont) => ont.id === selectedONT);
      return {
        connectedUsers: ontData.connectedUsers,
        bandwidth: ontData.bandwidth,
        uptime: ontData.uptime,
      };
    } else if (selectedFloor) {
      const floorData = buildings
        .find((building) => building.id === selectedBuilding)
        .floors.find((floor) => floor.id === selectedFloor);
      const connectedUsers = floorData.onts.reduce((sum, ont) => sum + ont.connectedUsers, 0);
      const bandwidth = floorData.onts.reduce((sum, ont) => sum + ont.bandwidth, 0);
      const uptime = floorData.onts.reduce((sum, ont) => sum + ont.uptime, 0) / floorData.onts.length;
      return {
        connectedUsers,
        bandwidth,
        uptime,
      };
    } else if (selectedBuilding) {
      const selectedBuildingData = buildings.find((building) => building.id === selectedBuilding);
      const connectedUsers = selectedBuildingData.floors.reduce(
        (sum, floor) => sum + floor.onts.reduce((ontSum, ont) => ontSum + ont.connectedUsers, 0),
        0
      );
      const bandwidth = selectedBuildingData.floors.reduce(
        (sum, floor) => sum + floor.onts.reduce((ontSum, ont) => ontSum + ont.bandwidth, 0),
        0
      );
      const uptime =
        selectedBuildingData.floors.reduce(
          (sum, floor) => sum + floor.onts.reduce((ontSum, ont) => ontSum + ont.uptime, 0),
          0
        ) /
        selectedBuildingData.floors.reduce((sum, floor) => sum + floor.onts.length, 0);
      return {
        connectedUsers,
        bandwidth,
        uptime,
      };
    } else {
      const connectedUsers = buildings.reduce(
        (sum, building) =>
          sum +
          building.floors.reduce(
            (floorSum, floor) => floorSum + floor.onts.reduce((ontSum, ont) => ontSum + ont.connectedUsers, 0),
            0
          ),
        0
      );
      const bandwidth = buildings.reduce(
        (sum, building) =>
          sum +
          building.floors.reduce(
            (floorSum, floor) => floorSum + floor.onts.reduce((ontSum, ont) => ontSum + ont.bandwidth, 0),
            0
          ),
        0
      );
      const uptime =
        buildings.reduce(
          (sum, building) =>
            sum +
            building.floors.reduce(
              (floorSum, floor) => floorSum + floor.onts.reduce((ontSum, ont) => ontSum + ont.uptime, 0),
              0
            ),
          0
        ) /
        buildings.reduce(
          (sum, building) => sum + building.floors.reduce((floorSum, floor) => floorSum + floor.onts.length, 0),
          0
        );
      return {
        connectedUsers,
        bandwidth,
        uptime,
      };
    }
  };

  // Obtener los datos de la tabla según el nivel seleccionado
  const getTableData = () => {
    if (selectedONT) {
      return buildings
        .find((building) => building.id === selectedBuilding)
        .floors.find((floor) => floor.id === selectedFloor)
        .onts.find((ont) => ont.id === selectedONT);
    } else if (selectedFloor) {
      return buildings
        .find((building) => building.id === selectedBuilding)
        .floors.find((floor) => floor.id === selectedFloor).onts;
    } else if (selectedBuilding) {
      return buildings.find((building) => building.id === selectedBuilding).floors;
    } else {
      return buildings;
    }
  };

  // Obtener los datos de resumen para una fila de la tabla
  const getRowSummary = (item) => {
    if (selectedBuilding) {
      if (selectedFloor) {
        return {
          connectedUsers: item.connectedUsers,
          bandwidth: item.bandwidth,
          uptime: item.uptime,
        };
      } else {
        const connectedUsers = item.onts.reduce((sum, ont) => sum + ont.connectedUsers, 0);
        const bandwidth = item.onts.reduce((sum, ont) => sum + ont.bandwidth, 0);
        const uptime = item.onts.reduce((sum, ont) => sum + ont.uptime, 0) / item.onts.length;
        return {
          connectedUsers,
          bandwidth,
          uptime,
        };
      }
    } else {
      const connectedUsers = item.floors.reduce(
        (sum, floor) => sum + floor.onts.reduce((ontSum, ont) => ontSum + ont.connectedUsers, 0),
        0
      );
      const bandwidth = item.floors.reduce(
        (sum, floor) => sum + floor.onts.reduce((ontSum, ont) => ontSum + ont.bandwidth, 0),
        0
      );
      const uptime =
        item.floors.reduce(
          (sum, floor) => sum + floor.onts.reduce((ontSum, ont) => ontSum + ont.uptime, 0),
          0
        ) /
        item.floors.reduce((sum, floor) => sum + floor.onts.length, 0);
      return {
        connectedUsers,
        bandwidth,
        uptime,
      };
    }
  };

  // Obtener los datos del gráfico según el nivel seleccionado y las métricas seleccionadas
  const getChartData = () => {
    let chartData = [];
    if (selectedONT) {
      chartData = usageData.filter((data) => data.ontId === selectedONT);
    } else if (selectedFloor) {
      const ontIds = buildings
        .find((building) => building.id === selectedBuilding)
        .floors.find((floor) => floor.id === selectedFloor)
        .onts.map((ont) => ont.id);
      chartData = usageData.filter((data) => ontIds.includes(data.ontId));
    } else if (selectedBuilding) {
      const ontIds = buildings
        .find((building) => building.id === selectedBuilding)
        .floors.flatMap((floor) => floor.onts.map((ont) => ont.id));
      chartData = usageData.filter((data) => ontIds.includes(data.ontId));
    } else {
      chartData = usageData;
    }
  
    // Filtrar los datos según el rango de fechas seleccionado
    if (startDate && endDate) {
      const startTimestamp = new Date(startDate).getTime();
      const endTimestamp = new Date(endDate).getTime();
      chartData = chartData.filter(
        (data) => new Date(data.timestamp).getTime() >= startTimestamp && new Date(data.timestamp).getTime() <= endTimestamp
      );
    }
  
    // Agrupar los datos por timestamp y calcular los valores promedio de las métricas seleccionadas
    const groupedData = chartData.reduce((result, data) => {
      const timestamp = data.timestamp;
      if (!result[timestamp]) {
        result[timestamp] = { timestamp };
        selectedMetrics.forEach((metric) => {
          result[timestamp][metric] = 0;
        });
        result[timestamp].count = 0;
      }
      selectedMetrics.forEach((metric) => {
        result[timestamp][metric] += data[metric];
      });
      result[timestamp].count++;
      return result;
    }, {});
  
    const aggregatedData = Object.values(groupedData).map((data) => {
      const aggregatedValues = {};
      selectedMetrics.forEach((metric) => {
        aggregatedValues[metric] = data[metric] / data.count;
      });
      return {
        timestamp: data.timestamp,
        ...aggregatedValues,
      };
    });
  
    return aggregatedData;
  };

  // Formatear la marca de tiempo para mostrarla en un formato legible
  const formatTimestamp = (timestamp) => {
    return format(parseISO(timestamp), 'dd/MM/yyyy HH:mm');
  };

  // Renderizar la página principal
  return (
    <div className="container mx-auto">
      <h1 className="text-2xl font-bold mb-4">Monitorización</h1>
      {/* Breadcrumb */}
      <div className="text-sm mb-4">
        <span
          className={`cursor-pointer ${!selectedBuilding ? 'font-bold' : ''}`}
          onClick={() => {
            setSelectedBuilding(null);
            setSelectedFloor(null);
            setSelectedONT(null);
          }}
        >
          General
        </span>
        {selectedBuilding && (
          <>
            {' > '}
            <span
              className={`cursor-pointer ${selectedBuilding && !selectedFloor ? 'font-bold' : ''}`}
              onClick={() => {
                setSelectedFloor(null);
                setSelectedONT(null);
              }}
            >
              {selectedBuilding}
            </span>
          </>
        )}
        {selectedFloor && (
          <>
            {' > '}
            <span
              className={`cursor-pointer ${selectedFloor && !selectedONT ? 'font-bold' : ''}`}
              onClick={() => setSelectedONT(null)}
            >
              {selectedFloor}
            </span>
          </>
        )}
        {selectedONT && (
          <>
            {' > '}
            <span className="font-bold">{selectedONT}</span>
          </>
        )}
      </div>
      {/* Resumen */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-4">
        <h2 className="text-xl font-bold mb-2">Resumen</h2>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <p className="text-gray-600">Usuarios Conectados:</p>
            <p className="text-lg font-bold">{getSummaryData().connectedUsers}</p>
          </div>
          <div>
            <p className="text-gray-600">Ancho de Banda Total:</p>
            <p className="text-lg font-bold">{getSummaryData().bandwidth} Mbps</p>
          </div>
          <div>
            <p className="text-gray-600">Uptime Promedio:</p>
            <p className="text-lg font-bold">{getSummaryData().uptime.toFixed(2)}%</p>
          </div>
        </div>
      </div>
      {/* Tabs */}
      <div className="mb-4">
        <button
          className={`px-4 py-2 rounded-l ${
            selectedTab === 'realtime' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
          }`}
          onClick={() => setSelectedTab('realtime')}
        >
          Datos en Tiempo Real
        </button>
        <button
          className={`px-4 py-2 rounded-r ${
            selectedTab === 'historical' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
          }`}
          onClick={() => setSelectedTab('historical')}
        >
          Datos Históricos
        </button>
      </div>
      {/* Tabla de Datos en Tiempo Real */}
      {selectedTab === 'realtime' && (
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">
          <h2 className="text-xl font-bold mb-2">Datos en Tiempo Real</h2>
          <table className="table-auto w-full">
            <thead>
              <tr>
                <th className="px-4 py-2">ID</th>
                {selectedMetrics.map((metric) => (
                  <th key={metric} className="px-4 py-2">
                    {metricLabels[metric]}
                  </th>
                ))}
              </tr>
              </thead>
            <tbody>
              {Array.isArray(getTableData()) ? (
                getTableData().map((item) => (
                  <tr
                    key={item.id}
                    className="cursor-pointer hover:bg-gray-100"
                    onClick={() => {
                      if (selectedBuilding) {
                        if (selectedFloor) {
                          setSelectedONT(item.id);
                        } else {
                          setSelectedFloor(item.id);
                        }
                      } else {
                        setSelectedBuilding(item.id);
                      }
                    }}
                  >
                    <td className="border px-4 py-2">{item.id}</td>
                    {selectedMetrics.map((metric) => (
                      <td key={metric} className="border px-4 py-2">
                        {metric === 'uptime'
                          ? `${getRowSummary(item)[metric].toFixed(2)}%`
                          : getRowSummary(item)[metric]}
                      </td>
                    ))}
                  </tr>
                ))
              ) : (
                <tr>
                  <td className="border px-4 py-2">{getTableData().id}</td>
                  {selectedMetrics.map((metric) => (
                    <td key={metric} className="border px-4 py-2">
                      {metric === 'uptime'
                        ? `${getTableData()[metric].toFixed(2)}%`
                        : getTableData()[metric]}
                    </td>
                  ))}
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
      {/* Gráfico de Datos Históricos */}
      {selectedTab === 'historical' && (
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">
          <h2 className="text-xl font-bold mb-2">Datos Históricos</h2>
          <div className="mb-4">
            <label htmlFor="startDate" className="block text-gray-700 font-bold mb-2">
              Fecha de Inicio:
            </label>
            <input
              type="date"
              id="startDate"
              className="w-full p-2 border border-gray-300 rounded-md"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          <div className="mb-4">
            <label htmlFor="endDate" className="block text-gray-700 font-bold mb-2">
              Fecha de Fin:
            </label>
            <input
              type="date"
              id="endDate"
              className="w-full p-2 border border-gray-300 rounded-md"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
          <LineChart width={800} height={400} data={getChartData()}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="timestamp" tickFormatter={formatTimestamp} />
            <YAxis />
            <Tooltip labelFormatter={formatTimestamp} />
            <Legend />
            {selectedMetrics.map((metric) => (
              <Line
                key={metric}
                type="monotone"
                dataKey={metric}
                stroke={`#${Math.floor(Math.random() * 16777215).toString(16)}`}
                activeDot={{ r: 8 }}
              />
            ))}
          </LineChart>
        </div>
      )}
      {/* Botón de Configuración */}
      <button
        className="fixed bottom-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-md shadow-md"
        onClick={() => setIsModalOpen(true)}
      >
        Configuración
      </button>
      {/* Modal de Configuración */}
      {isModalOpen && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold mb-4">Configuración de Monitorización</h2>
            <div className="mb-4">
              <label htmlFor="collectionInterval" className="block text-gray-700 font-bold mb-2">
                Intervalo de Recopilación (minutos):
              </label>
              <input
                type="number"
                id="collectionInterval"
                className="w-full p-2 border border-gray-300 rounded-md"
                value={collectionInterval}
                onChange={(e) => setCollectionInterval(parseInt(e.target.value))}
              />
            </div>
            <div className="mb-4">
              <label htmlFor="metrics" className="block text-gray-700 font-bold mb-2">
                Métricas a Monitorizar:
              </label>
              <select
                id="metrics"
                className="w-full p-2 border border-gray-300 rounded-md"
                multiple
                value={selectedMetrics}
                onChange={(e) =>
                  setSelectedMetrics(
                    Array.from(e.target.selectedOptions, (option) => option.value)
                  )
                }
              >
                {Object.keys(metricLabels).map((metric) => (
                  <option key={metric} value={metric}>
                    {metricLabels[metric]}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex justify-end">
              <button
                className="bg-blue-500 text-white px-4 py-2 rounded-md shadow-md mr-2"
                onClick={() => setIsModalOpen(false)}
              >
                Guardar
              </button>
              <button
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md shadow-md"
                onClick={() => setIsModalOpen(false)}
              >
                Cancelar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
export default RealTimeMonitor;