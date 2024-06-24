import React from 'react';

const MetricsPanel = () => {
  return (
    <div className="bg-white shadow-md rounded-lg p-4">
      <h2 className="text-lg font-bold mb-4">Métricas en tiempo real</h2>
      <div className="grid grid-cols-2 gap-4">
        <div className="bg-gray-100 rounded-lg p-4">
          <p className="text-gray-600">Usuarios conectados</p>
          <h3 className="text-2xl font-bold">1,245</h3>
        </div>
        <div className="bg-gray-100 rounded-lg p-4">
          <p className="text-gray-600">Tráfico de datos</p>
          <h3 className="text-2xl font-bold">12.5 GB</h3>
        </div>
      </div>
    </div>
  );
};

export default MetricsPanel;