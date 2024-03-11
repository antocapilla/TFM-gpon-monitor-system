import React, { useState } from 'react';
import ViewStructure from '../components/ViewStructure';
import MapViewEditor from '../components/MapView';
import MapEditor from '../components/MapEditor';
import FileUpload from '../components/FileUpload';

const INITIAL_BUILDINGS = [
  {
    name: 'Edificio 1',
    floors: [
      { 
        name: 'Planta 1', 
        url: '/static/media/edificioA-planta1.c0461ddad20ac0d62f04.jpg' 
      },
      { name: 'Planta 2', url: '/static/media/planta2.fd861a43eb086c53dae7.png'},
    ],
    expanded: false,
  },
];

function SpaceManager() {
  const [selectedLocation, setSelectedLocation] = useState("Gestion de Espacios")
  const [buildings, setBuildings] = useState(INITIAL_BUILDINGS);
  const [selectedFloor, setSelectedFloor] = useState(null);

  const handleExpandBuilding = (buildingToExpand) => {
    setBuildings(buildings.map(building => {
      if (building.name === buildingToExpand.name) {
        return { ...building, expanded: !building.expanded };
      }
      return building;
    }));
  };

  const handleAddBuilding = () => {
    setBuildings([...buildings, { name: `Edificio ${buildings.length + 1}`, floors: [], expanded: false }]);
  };

  const handleAddFloor = (buildingToAddFloor) => {
    const newFloor = { name: `Nueva Planta ${buildingToAddFloor.floors.length + 1}`, url: null };
    setBuildings(buildings.map(building => {
      if (building.name === buildingToAddFloor.name) {
        return { ...building, floors: [...building.floors, newFloor] };
      }
      return building;
    }));
  };

  const handleDeleteBuilding = (buildingToDelete) => {
    setBuildings(buildings.filter(building => building.name !== buildingToDelete.name));
  };

  const handleDeleteFloor = (building, floorToDelete) => {
    setBuildings(buildings.map(building => {
      if (building.name === building.name) {
        return { ...building, floors: building.floors.filter(floor => floor.name !== floorToDelete.name) };
      }
      return building;
    }));
  };

  const handleFileUpload = (file, buildingName, floorName) => {
    // Lógica para manejar la subida del archivo y actualizar la URL del plano
    // post(api/building/${building}/${floorPlan})
    const newUrl = `/assets/${buildingName}-${floorName}.png`;
    // Actualiza el estado de buildings con la nueva URL
    setBuildings(buildings.map(building => {
      if (building.name === buildingName) {
        return {
          ...building,
          floors: building.floors.map(floor => {
            if (floor.name === floorName) {
              return { ...floor, url: newUrl };
            }
            return floor;
          }),
        };
      }
      return building;
    }));
  };

  const selectedBuildingFloor = buildings.flatMap(building => building.floors).find(floor => floor.name === selectedFloor);
  const floorPlanUrl = selectedBuildingFloor?.url;

  const onSaveDrawings = (drawings) => {
    try {
      // Provisional
      localStorage.setItem('drawings', JSON.stringify(drawings));
      console.log('Dibujos guardados en el almacenamiento local');

      // Enviar un POST con los nuevos drawings
    } catch (error) {
      console.error('Error al guardar los dibujos en el almacenamiento local:', error);
    }
  };

  return (
    <div className="flex-1 p-4">
      <div className="bg-white p-4 rounded-md shadow-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-bold">Gestion de Espacios</h2>
          <div className="flex space-x-2">
            <button className="bg-custom-blue hover:bg-custom-dark-blue text-white font-bold py-2 px-4 rounded">
              Configuracion
            </button>
            <button className="bg-custom-grey hover:bg-custom-blue text-white font-bold py-2 px-4 rounded">
              Borrar
            </button>
          </div>
        </div>
        <div className="flex">
          <div className="w-1/4 bg-custom-grey p-4 rounded-md">
            <h3 className="font-bold mb-2">View Structure</h3>
            <ViewStructure 
              buildings={buildings}
              onExpandBuilding={handleExpandBuilding}
              onAddBuilding={handleAddBuilding}
              onAddFloor={handleAddFloor}
              onDeleteBuilding={handleDeleteBuilding}
              onDeleteFloor={handleDeleteFloor}
              selectedFloor={selectedFloor}
              onSelectFloor={setSelectedFloor}
            />
          </div>
          <div className="flex-1 ml-4">
            {selectedFloor ? (
              floorPlanUrl ? (
                <MapEditor onSaveDrawings={onSaveDrawings}/>
              ) : (
                <FileUpload onFileUploaded={(file) => handleFileUpload(file, selectedBuildingFloor.buildingName, selectedFloor)} />
              )
            ) : (
              <div>Seleccione una planta para comenzar.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default SpaceManager;
