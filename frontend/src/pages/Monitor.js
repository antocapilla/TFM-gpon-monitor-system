import React, { useState, useEffect } from 'react';
import { format, parseISO } from 'date-fns';
import { getBuildingData, getTimeSeriesData, getLatestValues, getMonitoringConfig, updateMonitoringConfig, deleteMonitoringData } from '../services/apiService';
import Summary from '../components/Summary';
import TabSelector from '../components/TabSelector';
import RealtimeData from '../components/RealtimeData';
import HistoricalData from '../components/HistoricalData';
import Connectivity from '../components/Connectivity';
import Breadcrumb from '../components/BreadCrumb';  // Añadida esta importación
import ConfigurationModal from '../components/ConfigurationModal';  // Añadida esta importación
import DeleteConfirmationModal from '../components/DeleteConfirmationModal';  // Añadida esta importación
import { Tabs, TabList, Tab, TabPanel } from 'react-tabs';
import 'react-tabs/style/react-tabs.css';

const metricLabels = {
  totalBytesReceived: 'Bytes Recibidos WAN',
  totalBytesSent: 'Bytes Enviados WAN',
  totalWifiBytesReceived: 'Bytes Recibidos WiFi',
  totalWifiBytesSent: 'Bytes Enviados WiFi',
  totalWifiAssociations: 'Clientes Conectados WiFi',
  activeWANs: 'WANs Activas',
  activeWiFiInterfaces: 'Interfaces WiFi Activas',
  connectedHosts: 'Hosts Conectados',
  failedConnections: 'Conexiones Fallidas',
  deviceCount: 'Número de ONTs',
  avgTransceiverTemperature: 'Temperatura Promedio GPON (°C)',
  avgRxPower: 'Potencia Promedio Rx (dBm)',
  avgTxPower: 'Potencia Promedio Tx (dBm)',
};


function Monitor() {
  const [tableData, setTableData] = useState([]);
  const [timeSeriesData, setTimeSeriesData] = useState([]);
  const [latestValues, setLatestValues] = useState({});
  const [buildings, setBuildings] = useState([]);
  const [selectedBuilding, setSelectedBuilding] = useState(null);
  const [selectedFloor, setSelectedFloor] = useState(null);
  const [selectedONT, setSelectedONT] = useState(null);
  const [currentLevel, setCurrentLevel] = useState('buildings');
  const [selectedTab, setSelectedTab] = useState('realtime');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [configuration, setConfiguration] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [selectedHistoricalMetric, setSelectedHistoricalMetric] = useState(Object.keys(metricLabels)[0]);
  const [selectedMetrics, setSelectedMetrics] = useState(Object.keys(metricLabels));
  const [activeTab, setActiveTab] = useState(0);


  useEffect(() => {
    const fetchData = async () => {
      try {
        const buildingData = await getBuildingData();
        setBuildings(buildingData);
        const config = await getMonitoringConfig();
        setConfiguration(config);
      } catch (error) {
        console.error("Error fetching initial data:", error);
      }
    };
    fetchData();
  }, []);

  useEffect(() => {
    const fetchMonitoringData = async () => {
      try {
        const lvData = await getLatestValues(selectedONT, selectedFloor, selectedBuilding);
        setLatestValues(lvData || {});

        let newTableData = [];
        switch(currentLevel) {
          case 'buildings':
            newTableData = await Promise.all(buildings.map(async (building) => {
              return await getLatestValues(null, null, building.name);
            }));
            break;
          case 'floors':
            console.log('fetching floors: ', selectedBuilding);
            const building = buildings.find(b => b.name === selectedBuilding);
            newTableData = await Promise.all((building?.floors || []).map(async (floor) => {
              return await getLatestValues(null, floor.name, selectedBuilding);
            }));
            break;
          case 'onts':
            const floor = buildings.find(b => b.name === selectedBuilding)?.floors.find(f => f.name === selectedFloor);
            newTableData = await Promise.all((floor?.onts || []).map(async (ont) => {
              return await getLatestValues(ont.serial, selectedFloor, selectedBuilding);
            }));
            break;
          case 'ont':
            newTableData = [await getLatestValues(selectedONT, selectedFloor, selectedBuilding)];
            break;
        }
        setTableData(newTableData.filter(Boolean));
      } catch (error) {
        console.error("Error fetching monitoring data:", error);
      }
    };
    fetchMonitoringData();
  }, [buildings, currentLevel, selectedBuilding, selectedFloor, selectedONT]);

  useEffect(() => {
    const fetchTimeSeriesData = async () => {
      if (selectedTab !== 'historical') return;
      
      setIsLoading(true);
      setError(null);
      try {
        const data = await getTimeSeriesData(
          currentLevel, 
          selectedBuilding, 
          selectedFloor, 
          selectedONT, 
          startDate ? new Date(startDate).toISOString() : null,
          endDate ? new Date(endDate).toISOString() : null
        );
        
        if (data.length === 0) {
          setError('No hay datos disponibles para el período seleccionado.');
        } else {
          setTimeSeriesData(data);
        }
      } catch (err) {
        console.error('Error fetching time series data:', err);
        setError(`Error al cargar los datos históricos: ${err.message}`);
      } finally {
        setIsLoading(false);
      }
    };
  
    fetchTimeSeriesData();
  }, [selectedTab, currentLevel, selectedBuilding, selectedFloor, selectedONT, startDate, endDate]);

  const formatTimestamp = (timestamp) => {
    if (!timestamp) return '';
    try {
      return format(parseISO(timestamp), 'dd/MM/yyyy HH:mm');
    } catch (error) {
      console.error('Error formatting timestamp:', timestamp, error);
      return 'Invalid Date';
    }
  };

  const handleItemClick = (item) => {
    switch(currentLevel) {
      case 'buildings':
        setSelectedBuilding(item.name || item._id);
        setCurrentLevel('floors');
        break;
      case 'floors':
        setSelectedFloor(item.name || item._id);
        setCurrentLevel('onts');
        break;
      case 'onts':
        setSelectedONT(item.serial || item._id);
        setCurrentLevel('ont');
        break;
    }
  };

  const handleBreadcrumbClick = (level) => {
    switch(level) {
      case 'buildings':
        setSelectedBuilding(null);
        setSelectedFloor(null);
        setSelectedONT(null);
        setCurrentLevel('buildings');
        break;
      case 'floors':
        setSelectedFloor(null);
        setSelectedONT(null);
        setCurrentLevel('floors');
        break;
      case 'onts':
        setSelectedONT(null);
        setCurrentLevel('onts');
        break;
    }
  };

  const handleConfigSave = async () => {
    try {
      await updateMonitoringConfig(configuration);
      setIsModalOpen(false);
    } catch (error) {
      console.error("Error updating configuration:", error);
    }
  };

  const handleDelete = async () => {
    try {
      await deleteMonitoringData(currentLevel, selectedBuilding, selectedFloor, selectedONT);
      // Actualizar los datos después de borrar
      // fetchMonitoringData();
      setIsDeleteModalOpen(false);
    } catch (error) {
      console.error("Error deleting data:", error);
      // Aquí podrías mostrar un mensaje de error al usuario
    }
  };

  const handleTabSelect = (index) => {
    const tabs = ['realtime', 'historical', 'connectivity'];
    setSelectedTab(tabs[index]);
    setActiveTab(index);
  };

  return (
    <div className="container mx-auto p-4 bg-gray-100">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Monitorización de Red</h1>

      <Breadcrumb
        currentLevel={currentLevel}
        selectedBuilding={selectedBuilding}
        selectedFloor={selectedFloor}
        selectedONT={selectedONT}
        handleBreadcrumbClick={handleBreadcrumbClick}
      />

      <Tabs selectedIndex={['realtime', 'historical', 'connectivity'].indexOf(selectedTab)} onSelect={handleTabSelect}>
        <TabList className="flex mb-4" >
        <Tab className={`px-4 py-2 rounded-t-lg mr-2 cursor-pointer ${activeTab === 0 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-800'}`}>Tiempo Real</Tab>
        <Tab className={`px-4 py-2 rounded-t-lg mr-2 cursor-pointer ${activeTab === 1 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-800'}`}>Histórico</Tab>
        <Tab className={`px-4 py-2 rounded-t-lg mr-2 cursor-pointer ${activeTab === 2 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-800'}`}>Conectividad</Tab>
        </TabList>
        

        <TabPanel>
          <div className="bg-white p-4 rounded-lg shadow">
            <Summary
              latestValues={latestValues}
              selectedMetrics={selectedMetrics}
              metricLabels={metricLabels}
              currentLevel={selectedBuilding || selectedFloor || selectedONT}
            />
            <RealtimeData
              tableData={tableData}
              selectedMetrics={selectedMetrics}
              metricLabels={metricLabels}
              setSelectedMetrics={setSelectedMetrics}
              handleItemClick={handleItemClick}
              configuration={configuration}
              setConfiguration={setConfiguration}
              handleConfigSave={handleConfigSave}
              isModalOpen={isModalOpen}
              setIsModalOpen={setIsModalOpen}
              isDeleteModalOpen={isDeleteModalOpen}
              setIsDeleteModalOpen={setIsDeleteModalOpen}
              currentLevel={currentLevel}
              selectedBuilding={selectedBuilding}
              selectedFloor={selectedFloor}
              selectedONT={selectedONT}
              handleDelete={handleDelete}
            />
          </div>
        </TabPanel>

        <TabPanel>
          <div className="bg-white p-4 rounded-lg shadow">
            {/* <Summary
              latestValues={latestValues}
              selectedMetrics={selectedMetrics}
              metricLabels={metricLabels}
            /> */}
            <HistoricalData
              isLoading={isLoading}
              error={error}
              timeSeriesData={timeSeriesData}
              startDate={startDate}
              setStartDate={setStartDate}
              endDate={endDate}
              setEndDate={setEndDate}
              selectedMetric={selectedHistoricalMetric}
              metricLabels={metricLabels}
              formatTimestamp={formatTimestamp}
              setSelectedHistoricalMetric={setSelectedHistoricalMetric}
            />
          </div>
        </TabPanel>

        <TabPanel>
          <Connectivity 
            level={currentLevel}
            building={selectedBuilding}
            floor={selectedFloor}
            ont={selectedONT}
          />
        </TabPanel>
      </Tabs>

      {/* Modales */}
      {isModalOpen && (
        <ConfigurationModal
          isOpen={isModalOpen}
          onClose={() => setIsModalOpen(false)}
          configuration={configuration}
          setConfiguration={setConfiguration}
          handleConfigSave={handleConfigSave}
        />
      )}

      {isDeleteModalOpen && (
        <DeleteConfirmationModal
          isOpen={isDeleteModalOpen}
          onClose={() => setIsDeleteModalOpen(false)}
          onConfirm={handleDelete}
          level={currentLevel}
          building={selectedBuilding}
          floor={selectedFloor}
          ont={selectedONT}
        />
      )}
    </div>
  );


}

export default Monitor;