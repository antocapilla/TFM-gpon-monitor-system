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

export const getMonitoringDataByDevice = (deviceId) => 
  errorInterceptor(fetch(`${API_BASE_URL}/monitoring/data/${deviceId}`));

export const getMonitoringData = (startDate, endDate) => {
  let url = `${API_BASE_URL}/monitoring/data`;
  if (startDate && endDate) {
    url += `?start_date=${startDate}&end_date=${endDate}`;
  } else if (startDate) {
    url += `?start_date=${startDate}`;
  } else if (endDate) {
    url += `?end_date=${endDate}`;
  }
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

export const getLatestMonitoringDataOfFloor = (buildingName, floorName) => 
  errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings/${encodeURIComponent(buildingName)}/floors/${encodeURIComponent(floorName)}`));

export const getLatestMonitoringDataOfBuilding = (buildingName) => 
  errorInterceptor(fetch(`${API_BASE_URL}/manager/buildings/${encodeURIComponent(buildingName)}`));

export const startDataCollection = () => 
  errorInterceptor(fetch(`${API_BASE_URL}/monitoring/start-data-collection`, {
    method: 'POST',
  }));