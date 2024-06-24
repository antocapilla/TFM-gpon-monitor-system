import React, { useEffect, useState } from 'react';
import ViewStructure from '../components/ViewStructure';
import MapViewEditor from '../components/MapView';
import MapEditor from '../components/MapEditor';
import FileUpload from '../components/FileUpload';
import { getBuildingData, createBuilding, addFloorToBuilding, addDrawingsToFloor } from '../services/apiService';
function SpaceManager() {
  // const [selectedLocation, setSelectedLocation] = useState("Gestion de Espacios")
  const [buildings, setBuildings] = useState([]);
  const [selectedFloor, setSelectedFloor] = useState(null);

  useEffect(() => {
    const fetchBuildingData = async () => {
      const data = await getBuildingData();
      setBuildings(data);
    };

    fetchBuildingData();
  }, []);

  const handleExpandBuilding = (buildingToExpand) => {
    setBuildings(buildings.map(building => {
      if (building.id === buildingToExpand.id) {
        return { ...building, expanded: !building.expanded };
      }
      return building;
    }));
  };

  const handleAddBuilding = async (buildingData) => {
    const newBuilding = await createBuilding(buildingData);
    setBuildings([...buildings, newBuilding]);
  };

  const handleAddFloor = async (buildingId, floorData) => {
    const newFloor = await addFloorToBuilding(buildingId, floorData);
    setBuildings(
      buildings.map((building) => {
        if (building.id === buildingId) {
          return {
            ...building,
            floors: [...building.floors, newFloor],
          };
        }
        return building;
      })
    );
  };

  const handleDeleteBuilding = (buildingToDelete) => {
    setBuildings(buildings.filter(building => building.id !== buildingToDelete.id));
  };

  const handleDeleteFloor = (building, floorToDelete) => {
    setBuildings(buildings.map(building => {
      if (building.id === building.id) {
        return { ...building, floors: building.floors.filter(floor => floor.id !== floorToDelete.id) };
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
      if (building.id === building.id) {
        return {
          ...building,
          floors: building.floors.map(floor => {
            if (floor.id === floorName) {
              return { ...floor, url: newUrl };
            }
            return floor;
          }),
        };
      }
      return building;
    }));
  };

  const selectedBuildingFloor = buildings.flatMap(building => building.floors).find(floor => floor.id === selectedFloor);
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
