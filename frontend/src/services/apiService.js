import { API_BASE_URL } from '../config';

const FAKE_MONITORING_CONFIGURATION = {
    collectionInterval: 5,
    enable: true,
}

const FAKE_BUILDINGS = [
    {
      id: 'Edificio 1',
      floors: [
        { 
          id: 'Planta 1', 
          url: '/static/media/edificioA-planta1.c0461ddad20ac0d62f04.jpg',
          drawings: [],
          onts: [
            { id: 'ONT-1', connectedUsers: 30, bandwidth: 100, uptime: 99.5 },
            { id: 'ONT-2', connectedUsers: 25, bandwidth: 80, uptime: 98.7 },
          ],
        },
        {
          id: 'Planta 2',
          url: '/static/media/planta2.fd861a43eb086c53dae7.png',
          drawings: [],
          onts: [
            { id: 'ONT-3', connectedUsers: 40, bandwidth: 120, uptime: 99.8 },
            { id: 'ONT-4', connectedUsers: 35, bandwidth: 110, uptime: 99.2 },
          ],
        },
      ],
    },
    {
      id: 'Edificio 2',
      floors: [
        {
          id: 'Planta 1',
          drawings: [],
          onts: [],
        },
      ],
    },
  ];

  // Función para obtener los datos de los edificios
  export const getMonitoringConfiguration = async () => {
    // Aquí iría la llamada a la API para obtener los datos de los edificios
    // const response = await fetch('API_BASE_URL');
    // const data = await response.json();
    // return data;
  
    // Devolver los datos de ejemplo por ahora
    return FAKE_MONITORING_CONFIGURATION;
  };
  
  // Función para obtener los datos de los edificios
  export const getBuildingData = async () => {
    // Aquí iría la llamada a la API para obtener los datos de los edificios
    // const response = await fetch('API_BASE_URL');
    // const data = await response.json();
    // return data;
  
    // Devolver los datos de ejemplo por ahora
    return FAKE_BUILDINGS;
  };
  
  // Función para crear un nuevo edificio
  export const createBuilding = async (buildingData) => {
    // Aquí iría la llamada a la API para crear un nuevo edificio
    // const response = await fetch('API_BASE_URL', {
    //   method: 'POST',
    //   body: JSON.stringify(buildingData),
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    // });
    // const data = await response.json();
    // return data;
  
    // Simular la creación del edificio por ahora
    const newBuilding = {
      id: Math.floor(Math.random() * 1000),
      name: buildingData.name,
      floors: [],
    };
    FAKE_BUILDINGS.push(newBuilding);
    return newBuilding;
  };
  
  // Función para agregar una planta a un edificio
  export const addFloorToBuilding = async (buildingId, floorData) => {
    // Aquí iría la llamada a la API para agregar una planta al edificio
    // const response = await fetch(`API_BASE_URL/${buildingId}/floors`, {
    //   method: 'POST',
    //   body: JSON.stringify(floorData),
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    // });
    // const data = await response.json();
    // return data;
  
    // Simular la adición de la planta por ahora
    const building = FAKE_BUILDINGS.find((building) => building.id === buildingId);
    if (building) {
      const newFloor = {
        id: Math.floor(Math.random() * 1000),
        name: floorData.name,
        drawings: [],
        onts: [],
      };
      building.floors.push(newFloor);
      return newFloor;
    }
    return null;
  };
  
  // Función para agregar datos de dibujo a una planta
  export const addDrawingsToFloor = async (buildingId, floorId, drawingsData) => {
    // Aquí iría la llamada a la API para agregar los datos de dibujo a la planta
    // const response = await fetch(`API_BASE_URL/${buildingId}/floors/${floorId}/drawings`, {
    //   method: 'POST',
    //   body: JSON.stringify(drawingsData),
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    // });
    // const data = await response.json();
    // return data;
  
    // Simular la adición de los datos de dibujo por ahora
    const building = FAKE_BUILDINGS.find((building) => building.id === buildingId);
    if (building) {
      const floor = building.floors.find((floor) => floor.id === floorId);
      if (floor) {
        floor.drawings = drawingsData;
        return floor.drawings;
      }
    }
    return null;
  };
  
  // Función para agregar una ONT a una planta
  export const addOntToFloor = async (buildingId, floorId, ontData) => {
    // Aquí iría la llamada a la API para agregar una ONT a la planta
    // const response = await fetch(`API_BASE_URL/${buildingId}/floors/${floorId}/onts`, {
    //   method: 'POST',
    //   body: JSON.stringify(ontData),
    //   headers: {
    //     'Content-Type': 'application/json',
    //   },
    // });
    // const data = await response.json();
    // return data;
  
    // Simular la adición de la ONT por ahora
    const building = FAKE_BUILDINGS.find((building) => building.id === buildingId);
    if (building) {
      const floor = building.floors.find((floor) => floor.id === floorId);
      if (floor) {
        const newOnt = {
          id: Math.floor(Math.random() * 1000),
          ...ontData,
        };
        floor.onts.push(newOnt);
        return newOnt;
      }
    }
    return null;
  };