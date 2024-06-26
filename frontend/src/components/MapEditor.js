import React, { useState, useEffect, useCallback } from 'react';
import { MapContainer, ImageOverlay, FeatureGroup, GeoJSON } from 'react-leaflet';
import { EditControl } from 'react-leaflet-draw';
import L from 'leaflet';

const DEFAULT_GEOJSON_DATA = {
  type: 'FeatureCollection',
  features: [],
};

const MapEditor = ({ floorPlanUrl, initialGeoJsonData = DEFAULT_GEOJSON_DATA, onSaveGeoJsonData, buildingName, floorName }) => {
  console.log('MapEditor rendered. Props:', { 
    floorPlanUrl, 
    initialGeoJsonData: JSON.stringify(initialGeoJsonData, null, 2),
    buildingName, 
    floorName 
  });

  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
  const [zoomLevel, setZoomLevel] = useState(0);
  const [isEditMode, setIsEditMode] = useState(false);
  const [error, setError] = useState(null);

  const [geoJsonData, setGeoJsonData] = useState(() => {
    console.log('Initializing geoJsonData state with:', JSON.stringify(initialGeoJsonData, null, 2));
    return initialGeoJsonData;
  });

  useEffect(() => {
    console.log('useEffect triggered. floorPlanUrl:', floorPlanUrl);
    if (floorPlanUrl) {
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.src = floorPlanUrl;
      img.onload = () => {
        console.log('Image loaded successfully. Dimensions:', { width: img.width, height: img.height });
        setImageDimensions({ width: img.width, height: img.height });
        const zoomAdjustment = -2;
        setZoomLevel(zoomAdjustment);
      };
      img.onerror = (e) => {
        console.error('Error loading image:', e);
        setError(`Error al cargar el plano del piso. URL: ${floorPlanUrl}. Por favor, verifique la URL y los permisos de acceso.`);
      };
    } else {
      console.warn('No floorPlanUrl provided');
      setError('No se ha proporcionado un plano del piso.');
    }
  }, [floorPlanUrl]);

  const handleEditClick = useCallback(() => {
    console.log('Edit button clicked');
    setIsEditMode(true);
  }, []);

  const handleSaveClick = useCallback(async () => {
    console.log('Save button clicked. Current geoJsonData:', JSON.stringify(geoJsonData, null, 2));
    try {
      await onSaveGeoJsonData(buildingName, floorName, geoJsonData);
      setIsEditMode(false);
    } catch (error) {
      console.error('Error saving geoJsonData:', error);
      setError('Error al guardar los datos GeoJSON. Por favor, intente nuevamente.');
    }
  }, [buildingName, floorName, geoJsonData, onSaveGeoJsonData]);

  const handleCancelClick = useCallback(() => {
    console.log('Cancel button clicked');
    setGeoJsonData(initialGeoJsonData);
    setIsEditMode(false);
  }, [initialGeoJsonData]);

  const handleCreated = useCallback((e) => {
    console.log('New feature created:', e.layer.toGeoJSON());
    const newFeature = e.layer.toGeoJSON();
    setGeoJsonData((prevGeoJsonData) => ({
      ...prevGeoJsonData,
      features: [...(prevGeoJsonData.features || []), newFeature],
    }));
  }, []);

  const handleEdited = useCallback((e) => {
    console.log('Features edited:', e.layers.toGeoJSON());
    const editedFeatures = e.layers.toGeoJSON().features;
    setGeoJsonData((prevGeoJsonData) => ({
      ...prevGeoJsonData,
      features: prevGeoJsonData.features.map((feature) => {
        const editedFeature = editedFeatures.find((f) => f.id === feature.id);
        return editedFeature || feature;
      }),
    }));
  }, []);

  const handleDeleted = useCallback((e) => {
    console.log('Features deleted:', e.layers.toGeoJSON());
    const deletedLayers = e.layers;
    setGeoJsonData((prevGeoJsonData) => ({
      ...prevGeoJsonData,
      features: prevGeoJsonData.features.filter((feature) => {
        const featureLayer = L.geoJSON(feature);
        return !deletedLayers.hasLayer(featureLayer);
      }),
    }));
  }, []);

  console.log('Current state before render:', { imageDimensions, zoomLevel, isEditMode, geoJsonData, error });


  return (
    <div className="relative bg-custom-grey-2 p-4 rounded-md shadow-lg" style={{ width: '100%', height: '500px' }}>
      {error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error: </strong>
          <span className="block sm:inline">{error}</span>
        </div>
      ) : imageDimensions.width === 0 || imageDimensions.height === 0 ? (
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-gray-900"></div>
        </div>
      ) : (
        <MapContainer
          center={[imageDimensions.height / 2, imageDimensions.width / 2]}
          zoom={zoomLevel}
          minZoom={-5}
          style={{ height: '100%', width: '100%' }}
          crs={L.CRS.Simple}
        >
          <ImageOverlay url={floorPlanUrl} bounds={[[0, 0], [imageDimensions.height, imageDimensions.width]]} />
          <FeatureGroup>
            <GeoJSON data={geoJsonData} />
            {isEditMode && (
              <EditControl
                position="bottomright"
                onCreated={handleCreated}
                onEdited={handleEdited}
                onDeleted={handleDeleted}
                draw={{
                  polygon: true,
                  polyline: true,
                  rectangle: false,
                  circle: false,
                  marker: false,
                  circlemarker: false,
                }}
              />
            )}
          </FeatureGroup>
        </MapContainer>
      )}
      <div className="absolute top-4 right-4 space-x-2">
        {!isEditMode ? (
          <button
            className="px-4 py-2 text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none"
            onClick={handleEditClick}
          >
            Editar
          </button>
        ) : (
          <>
            <button
              className="px-4 py-2 text-white bg-green-500 rounded-md hover:bg-green-600 focus:outline-none"
              onClick={handleSaveClick}
            >
              Aceptar cambios
            </button>
            <button
              className="px-4 py-2 text-white bg-red-500 rounded-md hover:bg-red-600 focus:outline-none"
              onClick={handleCancelClick}
            >
              Cancelar
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default MapEditor;