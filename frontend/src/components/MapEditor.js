import React, { useState, useEffect } from 'react';
import { MapContainer, ImageOverlay, FeatureGroup, GeoJSON } from 'react-leaflet';
import { EditControl } from 'react-leaflet-draw';
import L from 'leaflet';
import DEFAULT_FLOOR_PLAN from '../assets/edificioA/planta2.png'

const DEFAULT_INITIAL_DRAWINGS = {
  type: 'FeatureCollection',
  features: [],
};



const MapEditor = ({ floorPlanUrl = DEFAULT_FLOOR_PLAN, initialDrawings = DEFAULT_INITIAL_DRAWINGS, onSaveDrawings }) => {
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
  const [zoomLevel, setZoomLevel] = useState(0);
  const [isEditMode, setIsEditMode] = useState(false);
  const [drawings, setDrawings] = useState(() => {
    const storedDrawings = localStorage.getItem('drawings');
    return storedDrawings ? JSON.parse(storedDrawings) : initialDrawings;
  });

  useEffect(() => {
    if (floorPlanUrl) {
      const img = new Image();
      img.src = floorPlanUrl;
      img.onload = () => {
        setImageDimensions({ width: img.width, height: img.height });
        const ratio = img.width / img.height;
        const zoomAdjustment = -2;
        setZoomLevel(zoomAdjustment);
      };
    }
  }, [floorPlanUrl]);

  if (imageDimensions.width === 0 || imageDimensions.height === 0) {
    return null;
  }

  const bounds = [[0, 0], [imageDimensions.height, imageDimensions.width]];

  const handleEditClick = () => {
    setIsEditMode(true);
  };

  const handleSaveClick = () => {
    onSaveDrawings(drawings);
    setIsEditMode(false);
  };

  const handleCancelClick = () => {
    setDrawings(initialDrawings);
    setIsEditMode(false);
  };

  const handleCreated = (e) => {
    const newFeature = e.layer.toGeoJSON();
    setDrawings((prevDrawings) => ({
      ...prevDrawings,
      features: [...prevDrawings.features, newFeature],
    }));
  };

  const handleEdited = (e) => {
    const editedFeatures = e.layers.toGeoJSON();
    setDrawings((prevDrawings) => ({
      ...prevDrawings,
      features: prevDrawings.features.map((feature) => {
        const editedFeature = editedFeatures.features.find((f) => f.id === feature.id);
        return editedFeature || feature;
      }),
    }));
  };

  const handleDeleted = (e) => {
    const deletedLayers = e.layers;
    setDrawings((prevDrawings) => ({
      ...prevDrawings,
      features: prevDrawings.features.filter((feature) => {
        const featureLayer = L.geoJSON(feature);
        return !deletedLayers.hasLayer(featureLayer);
      }),
    }));
  };

  return (
    <div className="relative bg-custom-grey-2 p-4 rounded-md shadow-lg" style={{ width: '100%', height: '500px' }}>
      <MapContainer
        center={[imageDimensions.height / 2, imageDimensions.width / 2]}
        zoom={zoomLevel}
        minZoom={-5}
        style={{ height: '100%', width: '100%' }}
        crs={L.CRS.Simple}
      >
        <ImageOverlay url={floorPlanUrl} bounds={bounds} />
        <FeatureGroup>
          <GeoJSON data={drawings} />
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
      <div className="absolute top-4 right-4 space-x-2">
        {!isEditMode && (
          <button
            className="px-4 py-2 text-white bg-blue-500 rounded-md hover:bg-blue-600 focus:outline-none"
            onClick={handleEditClick}
          >
            Editar
          </button>
        )}
        {isEditMode && (
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