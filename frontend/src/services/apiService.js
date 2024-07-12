import { API_BASE_URL } from '../config';

const errorInterceptor = async (promise) => {
  try {
    const response = await promise;
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

export const getBuildingData = () => 
  errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings`));

export const getFloorByName = (buildingName, floorName) => 
  errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings/${encodeURIComponent(buildingName)}/floors/${encodeURIComponent(floorName)}`));

export const createBuilding = (name) => 
  errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name }),
  }));

export const addFloorToBuilding = (buildingName, floorName) => 
  errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings/${encodeURIComponent(buildingName)}/floors`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name: floorName }),
  }));

  export const getAvailableONTs = () => 
    errorInterceptor(fetch(`${API_BASE_URL}/manager/available-onts`));
  
  export const addOntToFloor = (buildingName, floorName, ontData) => 
    errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings/${encodeURIComponent(buildingName)}/floors/${encodeURIComponent(floorName)}/onts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ontData),
    }));
  
  export const updateONTPosition = (buildingName, floorName, ontSerial, position) => 
    errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings/${encodeURIComponent(buildingName)}/floors/${encodeURIComponent(floorName)}/onts/${encodeURIComponent(ontSerial)}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(position),
    }));

export const updateFloor = (buildingName, floorName, floorData) => 
  errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings/${encodeURIComponent(buildingName)}/floors/${encodeURIComponent(floorName)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(floorData),
  }));


export const uploadFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  return errorInterceptor(fetch(`${API_BASE_URL}/files/upload`, {
    method: 'POST',
    body: formData,
  }));
};

export const updateFloorUrl = (buildingName, floorName, url) => {
  const data = { name: floorName, url, drawings: [] };
  console.log(`Updating floor URL: ${JSON.stringify(data)}`);
  return errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings/${encodeURIComponent(buildingName)}/floors/${encodeURIComponent(floorName)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }));
}

export const updateFloorDrawings = (buildingName, floorName, drawings) => {
  const data = { name: floorName, drawings };
  console.log(`Updating floor drawings: ${JSON.stringify(data)}`);
  return errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings/${encodeURIComponent(buildingName)}/floors/${encodeURIComponent(floorName)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }));
}

export const updateFloorGeoJsonData = (buildingName, floorName, geoJsonData) => {
  const data = { name: floorName, geoJsonData };
  console.log(`Updating floor drawings: ${JSON.stringify(data)}`);
  return errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings/${encodeURIComponent(buildingName)}/floors/${encodeURIComponent(floorName)}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  }));
}

export const deleteBuilding = (buildingName) => 
  errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings/${encodeURIComponent(buildingName)}`, {
    method: 'DELETE',
  }));

export const deleteFloor = (buildingName, floorName) => 
  errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings/${encodeURIComponent(buildingName)}/floors/${encodeURIComponent(floorName)}`, {
    method: 'DELETE',
  }));

export const deleteONTFromFloor = (buildingName, floorName, ontSerial) => 
  errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings/${encodeURIComponent(buildingName)}/floors/${encodeURIComponent(floorName)}/onts/${encodeURIComponent(ontSerial)}`, {
    method: 'DELETE'
  }));

// Actualizar o agregar las siguientes funciones para el monitoreo

export const deleteMonitoringData = (level, building, floor, ont) => {
  let url = `${API_BASE_URL}/monitoring/delete?`;
  if (building) url += `&building=${encodeURIComponent(building)}`;
  if (floor) url += `&floor=${encodeURIComponent(floor)}`;
  if (ont) url += `&serial=${encodeURIComponent(ont)}`;
  
  return errorInterceptor(fetch(url, { method: 'DELETE' }))
    .then(data => {
      console.log('Deleted data:', data);
      return data;
    });
};

export const getTimeSeriesData = (currentLevel, selectedBuilding, selectedFloor, selectedONT, startDate, endDate) => {
  let url = `${API_BASE_URL}/monitoring/time-series?`;
  
  switch(currentLevel) {
    case 'buildings':
      // No añadimos parámetros, obtendremos datos para todos los edificios
      break;
    case 'floors':
      if (selectedBuilding) url += `&building=${encodeURIComponent(selectedBuilding)}`;
      break;
    case 'onts':
      if (selectedBuilding) url += `&building=${encodeURIComponent(selectedBuilding)}`;
      if (selectedFloor) url += `&floor=${encodeURIComponent(selectedFloor)}`;
      break;
    case 'ont':
      if (selectedONT) url += `&serial=${encodeURIComponent(selectedONT)}`;
      break;
  }

  if (startDate) url += `&start_date=${encodeURIComponent(startDate)}`;
  if (endDate) url += `&end_date=${encodeURIComponent(endDate)}`;
  
  console.log('Fetching time series data from URL:', url);
  
  return errorInterceptor(fetch(url))
    .then(data => {
      console.log('Time series data received:', data);
      return data;
    });
};



export const getLatestValues = (serial, floor, building) => {
  console.log('Fetching latest values for:', { serial, floor, building });
  let url = `${API_BASE_URL}/monitoring/latest-values`;
  if (serial) url += `?serial=${encodeURIComponent(serial)}`;
  else if (floor) url += `?floor=${encodeURIComponent(floor)}`;
  else if (building) url += `?building=${encodeURIComponent(building)}`;

  console.log('Fetching latest values from URL:', url);
  
  return errorInterceptor(fetch(url));
};

export const getMonitoringConfig = () => 
  errorInterceptor(fetch(`${API_BASE_URL}/monitoring/config`));

export const updateMonitoringConfig = (config) => 
  errorInterceptor(fetch(`${API_BASE_URL}/monitoring/config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  }));

// En apiService.js

export const runSimulation = async (buildingName, floorName, simulationType) => {
  const response = await fetch(`${API_BASE_URL}/simulator/run-simulation`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      building_name: buildingName,
      floor_name: floorName,
      simulation_type: simulationType,
    }),
  });

  if (!response.ok) {
    console.error("Network response was not ok", response);
    throw new Error('Network response was not ok');
  }

  const result = await response.json();
  console.log("Simulation API Result:", result);
  return result;
};