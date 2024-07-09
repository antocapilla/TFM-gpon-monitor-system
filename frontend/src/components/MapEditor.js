import React, { useState, useEffect, useCallback, useRef } from 'react';
import { MapContainer, ImageOverlay, FeatureGroup, GeoJSON, useMapEvents, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import { EditControl } from 'react-leaflet-draw';
import L from 'leaflet';
import { getAvailableONTs, addOntToFloor, getFloorByName, deleteONTFromFloor } from '../services/apiService';

import ontIconUrl from '../assets/ont-icon.png';

const DEFAULT_GEOJSON_DATA = {
  type: 'FeatureCollection',
  features: [],
};

const Modal = ({ isOpen, onClose, children }) => {
  if (!isOpen) return null;
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-[9999]">
      <div className="bg-white p-6 rounded-lg shadow-xl max-w-md w-full z-[10000]">
        {children}
        <button
          className="mt-4 w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50"
          onClick={onClose}
        >
          Cerrar
        </button>
      </div>
    </div>
  );
};

const MapEditor = ({ floorPlanUrl, initialGeoJsonData, onSaveGeoJsonData, buildingName, floorName }) => {
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
  const [zoomLevel, setZoomLevel] = useState(0);
  const [isEditMode, setIsEditMode] = useState(false);
  const [isAddONTMode, setIsAddONTMode] = useState(false);
  const [selectedONT, setSelectedONT] = useState(null);
  const [availableONTs, setAvailableONTs] = useState([]);
  const [error, setError] = useState(null);
  const [geoJsonData, setGeoJsonData] = useState(initialGeoJsonData || DEFAULT_GEOJSON_DATA);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [onts, setONTs] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const mapRef = useRef(null);
  const [scale, setScale] = useState(1);
  const [scaleLine, setScaleLine] = useState(null);
  const [isAdjustingScale, setIsAdjustingScale] = useState(false);
  const [currentZoom, setCurrentZoom] = useState(zoomLevel);

  useEffect(() => {
    const loadFloorData = async () => {
      setIsLoading(true);
      try {
        const floorData = await getFloorByName(buildingName, floorName);
        setONTs(floorData.onts || []);
        setGeoJsonData(floorData.geoJsonData || DEFAULT_GEOJSON_DATA);
        setScale(floorData.scale || 1);
      } catch (error) {
        console.error('Error loading floor data:', error);
        setError('Error al cargar los datos del piso.');
      } finally {
        setIsLoading(false);
      }
    };

    loadFloorData();
  }, [buildingName, floorName]);

  useEffect(() => {
    if (floorPlanUrl) {
      const img = new Image();
      img.crossOrigin = "anonymous";
      img.src = floorPlanUrl;
      img.onload = () => {
        setImageDimensions({ width: img.width, height: img.height });
        const zoomAdjustment = -2;
        setZoomLevel(zoomAdjustment);
      };
      img.onerror = (e) => {
        console.error('Error loading image:', e);
        setError(`Error al cargar el plano del piso. URL: ${floorPlanUrl}. Por favor, verifique la URL y los permisos de acceso.`);
      };
    } else {
      setError('No se ha proporcionado un plano del piso.');
    }
  }, [floorPlanUrl]);

  useEffect(() => {
    const fetchAvailableONTs = async () => {
      try {
        const availableONTs = await getAvailableONTs(buildingName, floorName);
        setAvailableONTs(availableONTs);
      } catch (error) {
        console.error('Error fetching available ONTs:', error);
        setError('Error al obtener las ONTs disponibles.');
      }
    };

    fetchAvailableONTs();
  }, [buildingName, floorName]);

  const handleEditClick = useCallback(() => {
    setIsEditMode(true);
  }, []);

  const handleCancelClick = useCallback(() => {
    setIsEditMode(false);
    setIsAddONTMode(false);
    setSelectedONT(null);
    setIsAdjustingScale(false);
    setScaleLine(null);
  
    const loadFloorData = async () => {
      try {
        const floorData = await getFloorByName(buildingName, floorName);
        setONTs(floorData.onts || []);
        setGeoJsonData(floorData.geoJsonData || DEFAULT_GEOJSON_DATA);
        setScale(floorData.scale || 1);
      } catch (error) {
        console.error('Error loading floor data:', error);
        setError('Error al cargar los datos del piso.');
      }
    };
  
    loadFloorData();
  }, [buildingName, floorName]);

  const handleAddONTClick = useCallback(() => {
    setIsAddONTMode(true);
    setIsModalOpen(true);
  }, []);

  const handleONTSelection = useCallback((ont) => {
    setSelectedONT(ont);
    setIsModalOpen(false);
    if (mapRef.current) {
      mapRef.current.getContainer().style.cursor = 'crosshair';
    }
  }, []);

  const addONT = useCallback(async (serial, x, y) => {
    try {
      await addOntToFloor(buildingName, floorName, { serial, x, y });
      const newONT = { serial, x, y };
      setONTs(prevONTs => [...prevONTs, newONT]);
      setIsAddONTMode(false);
      setSelectedONT(null);
      if (mapRef.current) {
        mapRef.current.getContainer().style.cursor = '';
      }
    } catch (error) {
      console.error('Error adding ONT:', error);
      setError('Error al añadir la ONT. Por favor, intente nuevamente.');
    }
  }, [buildingName, floorName]);

  const handleAcceptClick = useCallback(async () => {
    try {
      await onSaveGeoJsonData(buildingName, floorName, geoJsonData, onts, scale);
      
      setIsEditMode(false);
      setIsAddONTMode(false);
      setIsAdjustingScale(false);
      setScaleLine(null);
    } catch (error) {
      console.error('Error saving data:', error);
      setError('Error al guardar los datos. Por favor, intente nuevamente.');
    }
  }, [buildingName, floorName, geoJsonData, onts, onSaveGeoJsonData, scale]);

  const deleteONT = useCallback(async (serial) => {
    try {
      await deleteONTFromFloor(buildingName, floorName, serial);
      setONTs(prevONTs => prevONTs.filter(ont => ont.serial !== serial));
    } catch (error) {
      console.error('Error deleting ONT:', error);
      setError('Error al eliminar la ONT. Por favor, intente nuevamente.');
    }
  }, [buildingName, floorName]);

  const MapEvents = () => {
    const map = useMapEvents({
      click: (e) => {
        if (isAddONTMode && selectedONT) {
          addONT(selectedONT, e.latlng.lng, e.latlng.lat);
        } else if (isAdjustingScale) {
          if (scaleLine.length === 0) {
            setScaleLine([e.latlng]);
          } else {
            const newScaleLine = [...scaleLine, e.latlng];
            setScaleLine(newScaleLine);

            if (newScaleLine.length === 2) {
              const distance = map.distance(newScaleLine[0], newScaleLine[1]);
              const userScale = prompt('Ingrese la distancia real en metros:');
              if (userScale) {
                setScale(parseFloat(userScale) / distance);
                setIsAdjustingScale(false);
                setScaleLine(null);
                if (mapRef.current) {
                  mapRef.current.getContainer().style.cursor = '';
                }
              }
            }
          }
        }
      },
      zoomend: () => {
        setCurrentZoom(map.getZoom());
      },
    });

    return null;
  };

  const ONTMarkers = () => {
    const ontIcon = new L.Icon({
      iconUrl: ontIconUrl,
      iconSize: [25, 41],
      iconAnchor: [12, 41],
      popupAnchor: [1, -34],
      shadowSize: [41, 41]
    });

    return onts.map(ont => (
      <Marker
        key={ont.serial}
        position={[ont.y, ont.x]}
        icon={ontIcon}
      >
        <Popup>
          <div>
            <p><strong>ONT Serial:</strong> {ont.serial}</p>
            <p><strong>Position:</strong> ({ont.x.toFixed(2)}, {ont.y.toFixed(2)})</p>
            {isEditMode && (
              <button
                className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600 focus:outline-none mt-2"
                onClick={() => deleteONT(ont.serial)}
              >
                Eliminar ONT
              </button>
            )}
          </div>
        </Popup>
      </Marker>
    ));
  };

  const ScaleLegend = () => {
    const map = useMap();
    if (scale === 1) return null;
  
    const scaleWidth = 100; // Ancho fijo de 100 pixels
    const mapScale = map.options.crs.scale(currentZoom);
    const realDistance = (scaleWidth / mapScale) * scale;
  
    return (
      <div className="absolute bottom-8 left-8 bg-white p-2 rounded shadow z-[1000]">
        <div style={{ width: `${scaleWidth}px`, height: '5px', backgroundColor: 'black' }} />
        <p className="text-sm mt-1">{realDistance.toFixed(2)} metros</p>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Error: </strong>
        <span className="block sm:inline">{error}</span>
      </div>
    );
  }

  if (imageDimensions.width === 0 || imageDimensions.height === 0) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg overflow-hidden">
      <div className="space-x-2 mb-4">
        {!isEditMode ? (
          <button
            className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 focus:outline-none"
            onClick={handleEditClick}
          >
            Editar
          </button>
        ) : (
          <>
            <button
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 focus:outline-none"
              onClick={handleAcceptClick}
            >
              Aceptar
            </button>
            <button
              className="px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600 focus:outline-none"
              onClick={handleCancelClick}
            >
              Cancelar
            </button>
          </>
        )}
      </div>
      
      <div className="relative" style={{ height: 'calc(100vh - 200px)' }}>
        <MapContainer
          ref={mapRef}
          center={[imageDimensions.height / 2, imageDimensions.width / 2]}
          zoom={zoomLevel}
          style={{ height: '100%', width: '100%' }}
          crs={L.CRS.Simple}
        >
          <ImageOverlay url={floorPlanUrl} bounds={[[0, 0], [imageDimensions.height, imageDimensions.width]]} />
          <FeatureGroup>
            <GeoJSON data={geoJsonData} />
            {isEditMode && (
              <EditControl
                position="topright"
                onCreated={(e) => {
                  const newFeature = e.layer.toGeoJSON();
                  setGeoJsonData(prevData => ({
                    ...prevData,
                    features: [...prevData.features, newFeature]
                  }));
                }}
                onEdited={(e) => {
                  const editedLayers = e.layers.toGeoJSON();
                  setGeoJsonData(prevData => ({
                    ...prevData,
                    features: prevData.features.map(f => {
                      const editedFeature = editedLayers.features.find(ef => ef.id === f.id);
                      return editedFeature || f;
                    })
                  }));
                }}
                onDeleted={(e) => {
                  const deletedLayers = e.layers.toGeoJSON();
                  setGeoJsonData(prevData => ({
                    ...prevData,
                    features: prevData.features.filter(f => !deletedLayers.features.some(df => df.id === f.id))
                  }));
                }}
                draw={{
                  polygon: true,
                  polyline: true,
                  rectangle: true,
                  circle: false,
                  marker: false,
                  circlemarker: false,
                }}
              />
            )}
          </FeatureGroup>
          <ONTMarkers />
          <MapEvents />
  
          {isAdjustingScale && scaleLine && scaleLine.length === 1 && (
            <Marker 
              position={scaleLine[0]}
              icon={L.divIcon({className: 'bg-blue-500 w-3 h-3 rounded-full border-2 border-white'})}
            />
          )}
          {isAdjustingScale && scaleLine && scaleLine.length === 2 && (
            <Polyline positions={scaleLine} color="red" weight={3} />
          )}
          <ScaleLegend />
        </MapContainer>

        {isEditMode && (
          <div className="absolute bottom-4 right-4 z-[1000] space-y-2">
            <button
              className="px-4 py-2 bg-purple-500 text-white rounded-md hover:bg-purple-600 focus:outline-none"
              onClick={handleAddONTClick}
            >
              Añadir ONT
            </button>
            <button
              className="px-4 py-2 bg-yellow-500 text-white rounded-md hover:bg-yellow-600 focus:outline-none"
              onClick={() => {
                setIsAdjustingScale(true);
                setScaleLine([]);
                if (mapRef.current) {
                  mapRef.current.getContainer().style.cursor = 'crosshair';
                }
              }}
            >
              Ajustar Escala
            </button>
          </div>
        )}
      </div>

      <Modal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)}>
        <h2 className="text-xl font-bold mb-4">Seleccionar ONT</h2>
        <select 
          value={selectedONT || ''}
          onChange={(e) => handleONTSelection(e.target.value)}
          className="w-full p-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">Seleccionar ONT</option>
          {availableONTs.map(ont => (
            <option key={ont} value={ont}>{ont}</option>
          ))}
        </select>
      </Modal>

      {/* {scale !== 1 && (
        <div className="mt-4 p-2 bg-blue-100 rounded">
          <p>Escala actual: 1 metro = {scale.toFixed(2)} unidades en el mapa</p>
        </div>
      )} */}
    </div>
  );
};

export default MapEditor;