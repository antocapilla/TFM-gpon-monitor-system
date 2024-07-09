import React, { useState, useEffect } from 'react';
import { format, parseISO } from 'date-fns';
import { getBuildingData, getTimeSeriesData, getLatestValues, getMonitoringConfig, updateMonitoringConfig, deleteMonitoringData } from '../services/apiService';
import Summary from '../components/Summary';
import TabSelector from '../components/TabSelector';
import RealtimeData from '../components/RealtimeData';
import HistoricalData from '../components/HistoricalData';
import ConfigurationModal from '../components/ConfigurationModal';
import Breadcrumb from '../components/BreadCrumb';
import DeleteConfirmationModal from '../components/DeleteConfirmationModal';

const metricLabels = {
  totalBytesReceived: 'Bytes Recibidos',
  totalBytesSent: 'Bytes Enviados',
  totalWifiAssociations: 'Asociaciones WiFi',
  activeWANs: 'WANs Activas',
  activeWiFiInterfaces: 'Interfaces WiFi Activas',
  connectedHosts: 'Hosts Conectados',
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
  const [selectedMetrics, setSelectedMetrics] = useState(Object.keys(metricLabels));
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [configuration, setConfiguration] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);

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

  return (
    <div className="container mx-auto">
      <h1 className="text-2xl font-bold mb-4">Monitorización</h1>
      
      <Breadcrumb 
        currentLevel={currentLevel}
        selectedBuilding={selectedBuilding}
        selectedFloor={selectedFloor}
        selectedONT={selectedONT}
        handleBreadcrumbClick={handleBreadcrumbClick}
      />
      <Summary 
        latestValues={latestValues}
        selectedMetrics={selectedMetrics}
        metricLabels={metricLabels}
      />
      <TabSelector 
        selectedTab={selectedTab}
        setSelectedTab={setSelectedTab}
      />
      
      {selectedTab === 'realtime' && (
        <RealtimeData 
          tableData={tableData}
          selectedMetrics={selectedMetrics}
          metricLabels={metricLabels}
          handleItemClick={handleItemClick}
        />
      )}
      
      {selectedTab === 'historical' && (
        <HistoricalData 
          isLoading={isLoading}
          error={error}
          timeSeriesData={timeSeriesData}
          startDate={startDate}
          setStartDate={setStartDate}
          endDate={endDate}
          setEndDate={setEndDate}
          selectedMetrics={selectedMetrics}
          metricLabels={metricLabels}
          formatTimestamp={formatTimestamp}
        />
      )}
      
      <button
        className="fixed bottom-4 right-4 bg-blue-500 text-white px-4 py-2 rounded-md shadow-md"
        onClick={() => setIsModalOpen(true)}
      >
        Configuración
      </button>

      <div className="fixed bottom-4 right-4 flex space-x-2">
        <button
          className="bg-red-500 text-white px-4 py-2 rounded-md shadow-md"
          onClick={() => setIsDeleteModalOpen(true)}
        >
          Borrar Datos
        </button>
        <button
          className="bg-blue-500 text-white px-4 py-2 rounded-md shadow-md"
          onClick={() => setIsModalOpen(true)}
        >
          Configuración
        </button>
      </div>
      
      <ConfigurationModal 
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        configuration={configuration}
        setConfiguration={setConfiguration}
        selectedMetrics={selectedMetrics}
        setSelectedMetrics={setSelectedMetrics}
        metricLabels={metricLabels}
        handleConfigSave={handleConfigSave}
      />

      <DeleteConfirmationModal 
        isOpen={isDeleteModalOpen}
        onClose={() => setIsDeleteModalOpen(false)}
        onConfirm={handleDelete}
        level={currentLevel}
        building={selectedBuilding}
        floor={selectedFloor}
        ont={selectedONT}
      />
    </div>
  );
}

export default Monitor;