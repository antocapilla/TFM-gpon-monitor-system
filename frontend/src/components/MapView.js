import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, ImageOverlay, FeatureGroup, useMap } from 'react-leaflet';
import { EditControl } from 'react-leaflet-draw';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import 'leaflet-draw/dist/leaflet.draw.css';
import ontIcon from '../assets/icono-ont.png';
import { point, lineString, polygon } from '@turf/helpers';
import { Marker, Polyline, Polygon } from 'react-leaflet';
import { useLeafletContext } from '@react-leaflet/core'
import FileUpload from './FileUpload';

const MyFeatureGroup = ({ drawings, addDrawing, updateDrawing, deleteDrawing }) => {
  const featureGroupRef = useRef();
  const map = useMap();
  const context = useLeafletContext();

  useEffect(() => {
    const onDrawCreated = (e) => {
      const layer = e.layer;
      let coordinates;
    
      // Extraer y ajustar las coordenadas según el tipo de geometría
      if (layer instanceof L.Marker) {
        // Para marcadores, Leaflet ya usa [lat, lng]
        coordinates = [layer.getLatLng().lat, layer.getLatLng().lng];
      } if (layer instanceof L.Polyline && !(layer instanceof L.Polygon)) {
        // Convertir cada LatLng a un array y asegurarse de que se estructuran como arrays de arrays
        coordinates = layer.getLatLngs().map(latlng => [latlng.lat, latlng.lng]);
        // Si `getLatLngs` devuelve un nivel más profundo de arrays para líneas compuestas, necesitas ajustar esto.
      }
      if (layer instanceof L.Polygon) {
        // Para polígonos, asegurar el manejo de un array de arrays para el anillo exterior
        coordinates = [layer.getLatLngs().map(ring => ring.map(ll => [ll.lat, ll.lng]))];
      }
    
      const drawing = {
        type: 'Feature',
        properties: {
          id: layer._leaflet_id, // O cualquier otro identificador único
        },
        geometry: {
          type: layer instanceof L.Marker ? "Point" :
                layer instanceof L.Polygon ? "Polygon" :
                layer instanceof L.Polyline ? "LineString" : "Unknown",
          coordinates: coordinates,
        },
      };

      console.log("Creating drawing: ", drawing.properties.id)
    
      addDrawing(drawing);
    };
    
    const onDrawEdited = (e) => {
      e.layers.eachLayer((layer) => {
        const editedDrawing = layerToGeoJSON(layer);
        console.log("Edited Drawing: ", editedDrawing)
        updateDrawing(editedDrawing.properties.id, editedDrawing);
      });
    };

    const onDrawDeleted = (e) => {
      const layers = e.layers;
      layers.eachLayer((layer) => {
          const geoJsonLayer = layerToGeoJSON(layer);
          console.log("Deleted Drawing: ", geoJsonLayer)
          deleteDrawing(geoJsonLayer.properties.id);
      });
  
      
    };

    map.on('draw:created', onDrawCreated);
    map.on('draw:edited', onDrawEdited);
    map.on('draw:deleted', onDrawDeleted);

    return () => {
      map.off('draw:created', onDrawCreated);
      map.off('draw:edited', onDrawEdited);
      map.off('draw:deleted', onDrawDeleted);
    };
  }, [map, addDrawing, updateDrawing, deleteDrawing]);

  return (
    <FeatureGroup ref={featureGroupRef}>
      {drawings.map((drawing) => {
        console.log("Painting Coordinates: ", drawing.properties.id)
        const { geometry } = drawing;
        const { id } = drawing.properties;

        // Convertir GeoJSON a Leaflet
        if (geometry.type === 'Point') {
          return <Marker key={id} position={geometry.coordinates} />;
        } else if (geometry.type === 'LineString') {
          // Asegúrate de que para LineString, las coordenadas se manejen adecuadamente como un array de [lat, lng]
          return <Polyline key={id} positions={geometry.coordinates} />;
        } else if (geometry.type === 'Polygon') {
          // Para Polygon, Leaflet espera un array de arrays de coordenadas para el primer anillo
          // Aquí, asegúrate de que geometry.coordinates ya es un array de arrays como se espera
          return <Polygon key={id} positions={geometry.coordinates} />;
        }
        return null;
      })}
      <EditControl
        position="topright"
        draw={{
          rectangle: false,
          circle: false,
          circlemarker: false,
          marker: true,
          polyline: true,
          polygon: true,
        }}
      />
    </FeatureGroup>
  );
};

function layerToGeoJSON(layer) {
  let coordinates;
  let type;

  if (layer instanceof L.Marker) {
    const { lat, lng } = layer.getLatLng();
    coordinates = [lng, lat];
    type = "Point";
  } else if (layer instanceof L.Polyline && !(layer instanceof L.Polygon)) {
    coordinates = layer.getLatLngs().map(latlng => [latlng.lng, latlng.lat]);
    type = "LineString";
  } else if (layer instanceof L.Polygon) {
    coordinates = [layer.getLatLngs().map(ring => ring.map(latlng => [latlng.lng, latlng.lat]))];
    type = "Polygon";
  }

  return {
    type: "Feature",
    properties: {
      id: layer._leaflet_id, // Asegurar que cada layer tenga un ID único
    },
    geometry: {
      type: type,
      coordinates: coordinates
    }
  };
}


const MapViewEditor = ({floorPlanUrl}) => {
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
  const [zoomLevel, setZoomLevel] = useState(0);
  //const [floorPlan, setFloorPlan] = useState(floorPlan2);
  const [drawings, setDrawings] = useState(() => {
    const storedDrawings = localStorage.getItem('drawings');
    return storedDrawings ? JSON.parse(storedDrawings) : [];
  });

  useEffect(() => {
    if (floorPlanUrl) {
      // Cargar el mapa usando floorPlanUrl
      const img = new Image();
      img.src = floorPlanUrl;
      img.onload = () => {
        setImageDimensions({ width: img.width, height: img.height });
        const ratio = img.width / img.height;
        const zoomAdjustment = -2; // Ajusta estos valores según tus necesidades
        setZoomLevel(zoomAdjustment);
      };
    }
  }, [floorPlanUrl]);

  if (imageDimensions.width === 0 || imageDimensions.height === 0) {
    return null;
  }

  const bounds = [[0, 0], [imageDimensions.height, imageDimensions.width]];

  const addDrawing = (drawing) => {
    setDrawings((prevState) => {
      const newState = [...prevState, drawing];
      localStorage.setItem('drawings', JSON.stringify(newState));
      return newState;
    });
  };

  const updateDrawing = (id, updatedDrawing) => {
    setDrawings((prevState) => {
      const newState = prevState.map((drawing) => (drawing.properties.id === id ? updatedDrawing : drawing));
      localStorage.setItem('drawings', JSON.stringify(newState));
      return newState;
    });
  };

  const deleteDrawing = (id) => {
    setDrawings((prevState) => {
      const newState = prevState.filter((drawing) => drawing.properties.id !== id);
      localStorage.setItem('drawings', JSON.stringify(newState));
      return newState;
    });
  };

  return (
    <div className="bg-custom-grey-2 p-4 rounded-md shadow-lg" style={{ width: '100%', height: '500px' }}> {/* Aquí aplicamos Tailwind CSS */}
      <MapContainer
        center={[imageDimensions.height / 2, imageDimensions.width / 2]}
        zoom={zoomLevel}
        minZoom={-5}
        style={{ height: '100%', width: '100%' }}
        crs={L.CRS.Simple}
      >
        <ImageOverlay
          url={floorPlanUrl}
          bounds={bounds}
        />
        <MyFeatureGroup
          drawings={drawings}
          addDrawing={addDrawing}
          updateDrawing={updateDrawing}
          deleteDrawing={deleteDrawing}
        />
      </MapContainer>
    </div>
  );
};

export default MapViewEditor;

