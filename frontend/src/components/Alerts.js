import React from 'react';

const Alerts = () => {
  return (
    <div className="bg-white shadow-md rounded-lg p-4 mt-4">
      <h2 className="text-lg font-bold mb-4">Alertas</h2>
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
        <strong className="font-bold">Alta concentración de usuarios</strong>
        <span className="block sm:inline">Se ha detectado una alta concentración de usuarios en el área de recepción.</span>
      </div>
    </div>
  );
};

export default Alerts;