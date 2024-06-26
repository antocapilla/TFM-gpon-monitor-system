import React, { useEffect, useState } from 'react';
import ViewStructure from '../components/ViewStructure';
import MapViewEditor from '../components/MapView'; // No eliminar, lleva a errores
import MapEditor from '../components/MapEditor';
import FileUpload from '../components/FileUpload';
import NameModal from '../components/NameModal';
import {   getBuildingData, 
  createBuilding, 
  addFloorToBuilding, 
  deleteBuilding, 
  deleteFloor, 
  updateFloorGeoJsonData,
  updateFloorUrl,
  uploadFile
} from '../services/apiService';

function Manager() {
  const [buildings, setBuildings] = useState([]);
  const [selectedFloor, setSelectedFloor] = useState(null);
  const [selectedBuilding, setSelectedBuilding] = useState(null);
  const [isNameModalOpen, setIsNameModalOpen] = useState(false);
  const [nameModalType, setNameModalType] = useState('');
  const [currentBuilding, setCurrentBuilding] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchBuildingData();
  }, []);

  const fetchBuildingData = async () => {
    try {
      const data = await getBuildingData();
      const updatedBuildings = data.map(newBuilding => {
        const existingBuilding = buildings.find(b => b.name === newBuilding.name);
        return existingBuilding 
          ? { ...newBuilding, expanded: existingBuilding.expanded }
          : { ...newBuilding, expanded: false };
      });
      setBuildings(updatedBuildings);
      
      // Actualizar selectedBuilding y selectedFloor si existen
      if (selectedBuilding && selectedFloor) {
        const updatedBuilding = updatedBuildings.find(b => b.name === selectedBuilding.name);
        if (updatedBuilding) {
          setSelectedBuilding(updatedBuilding);
          const updatedFloor = updatedBuilding.floors.find(f => f.name === selectedFloor.name);
          if (updatedFloor) {
            setSelectedFloor(updatedFloor);
          }
        }
      }
    } catch (error) {
      console.error('Error fetching building data:', error);
      setError('Error fetching building data. Please try again.');
    }
  };

  const handleExpandBuilding = (buildingToExpand) => {
    setBuildings(buildings.map(building => {
      if (building.name === buildingToExpand.name) {
        return { ...building, expanded: !building.expanded };
      }
      return building;
    }));
  };

  const handleAddBuilding = () => {
    setNameModalType('building');
    setIsNameModalOpen(true);
  };

  const handleAddFloor = (building) => {
    setNameModalType('floor');
    setCurrentBuilding(building);
    setIsNameModalOpen(true);
  };

  const handleNameSubmit = async (name) => {
    setIsNameModalOpen(false);
    try {
      if (nameModalType === 'building') {
        await createBuilding(name);
      } else if (nameModalType === 'floor' && currentBuilding) {
        await addFloorToBuilding(currentBuilding.name, name);
      }
      await fetchBuildingData();
    } catch (error) {
      console.error(`Error ${nameModalType === 'building' ? 'creating building' : 'adding floor'}:`, error);
      setError(`Error ${nameModalType === 'building' ? 'creating building' : 'adding floor'}. Please try again.`);
    }
    setCurrentBuilding(null);
  };

  const handleDeleteBuilding = async (buildingToDelete) => {
    try {
      await deleteBuilding(buildingToDelete.name);
      await fetchBuildingData();
    } catch (error) {
      console.error('Error deleting building:', error);
      setError('Error deleting building. Please try again.');
    }
  };

  const handleDeleteFloor = async (building, floorToDelete) => {
    try {
      await deleteFloor(building.name, floorToDelete.name);
      await fetchBuildingData();
    } catch (error) {
      console.error('Error deleting floor:', error);
      setError('Error deleting floor. Please try again.');
    }
  };

  const handleFileUpload = async (file) => {
    if (!selectedBuilding || !selectedFloor) {
      console.error('No building or floor selected');
      setError('Please select a building and floor before uploading a file.');
      return;
    }

    try {
      const uploadResponse = await uploadFile(file);
      if (uploadResponse && uploadResponse.file_url) {
        console.log('File uploaded successfully. URL:', uploadResponse.file_url);
        await updateFloorUrl(selectedBuilding.name, selectedFloor.name, uploadResponse.file_url);
        await fetchBuildingData();  // Esto actualizará la información en el componente
      } else {
        throw new Error('Invalid response from file upload');
      }
    } catch (error) {
      console.error('Error in file upload process:', error);
      setError('Error uploading file. Please try again.');
    }
  };

  const onSaveGeoJsonData = async (buildingName, floorName, geoJsonData) => {
    try {
      await updateFloorGeoJsonData(buildingName, floorName, geoJsonData);
      await fetchBuildingData();
    } catch (error) {
      console.error('Error saving GeoJSON data:', error);
      setError('Error saving GeoJSON data. Please try again.');
    }
  };

  const selectedBuildingFloor = selectedBuilding?.floors.find(floor => floor.name === selectedFloor?.name);
  const floorPlanUrl = selectedBuildingFloor?.url;
  const floorGeoJsonData = selectedBuildingFloor?.geoJsonData;

  console.log('Selected floor:', selectedFloor?.name);
  console.log('Selected building floor:', selectedBuildingFloor?.name);
  console.log('Floor plan URL:', floorPlanUrl);
  console.log('Floor GeoJSON data:', JSON.stringify(floorGeoJsonData, null, 2));
  console.log('GeoJSON features count:', floorGeoJsonData?.features?.length || 0);

  return (
    <div className="flex-1 p-4">
      {error && <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error!</strong>
        <span className="block sm:inline"> {error}</span>
      </div>}
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
              onSelectFloor={(floor, building) => {
                setSelectedFloor(floor);
                setSelectedBuilding(building);
              }}
            />
          </div>
          <div className="flex-1 ml-4">
            {selectedFloor && selectedBuilding && (
              <h3 className="text-xl font-semibold mb-4 bg-blue-100 p-2 rounded">
                {selectedBuilding.name} - {selectedFloor.name}
              </h3>
            )}
            {!isNameModalOpen && selectedFloor ? (
              floorPlanUrl ? (
                <MapEditor 
                  floorPlanUrl={floorPlanUrl}
                  initialGeoJsonData={floorGeoJsonData || { type: 'FeatureCollection', features: [] }}
                  onSaveGeoJsonData={onSaveGeoJsonData}
                  buildingName={selectedBuilding?.name}
                  floorName={selectedFloor.name}
                />
              ) : (
                <FileUpload 
                  onFileUploaded={handleFileUpload}
                />
              )
            ) : (
              <div className="bg-yellow-100 border-l-4 border-yellow-500 text-yellow-700 p-4" role="alert">
                <p className="font-bold">Atención</p>
                <p>Seleccione una planta para comenzar.</p>
              </div>
            )}
          </div>
        </div>
      </div>
      <NameModal 
        isOpen={isNameModalOpen}
        onClose={() => {
          setIsNameModalOpen(false);
          setCurrentBuilding(null);
        }}
        onSubmit={handleNameSubmit}
        title={`Introduce un nombre para ${nameModalType === 'building' ? 'el edificio' : 'la planta'}`}
      />
    </div>
  );
}

export default Manager;