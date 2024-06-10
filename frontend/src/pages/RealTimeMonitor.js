import React, { useState } from 'react';
import ViewStructure from '../components/ViewStructure';
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

function RealTimeMonitor() {
  return (
    <div className="flex-1 p-4">
      <div className="bg-white p-4 rounded-md shadow-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-bold">Simulador de Configuracion</h2>
        </div>
        <MapEditor/>
      </div>
    </div>
  );
}

export default RealTimeMonitor;