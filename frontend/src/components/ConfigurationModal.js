import React, { useState } from 'react';

const ConfigurationModal = ({ isOpen, onClose, onSubmit }) => {
  const [config, setConfig] = useState({
    num_rays: 720,
    max_path_loss: 1e7,
    max_reflections: 2,
    max_transmissions: 1,
    tx_power: 0.03,
    frequency: 2.4e9,
    tx_x: 4.2,
    tx_y: 2,
    resolution: 120
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setConfig(prevConfig => ({
      ...prevConfig,
      [name]: name === 'frequency' ? parseFloat(value) * 1e9 : parseFloat(value)
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(config);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="mt-3 text-center">
          <h3 className="text-lg leading-6 font-medium text-gray-900">Configuración de la Simulación</h3>
          <form onSubmit={handleSubmit} className="mt-2">
            <div className="mt-2">
              <label className="block text-sm font-medium text-gray-700">Número de rayos</label>
              <input
                type="number"
                name="num_rays"
                value={config.num_rays}
                onChange={handleChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div className="mt-2">
              <label className="block text-sm font-medium text-gray-700">Máxima pérdida de trayecto</label>
              <input
                type="number"
                name="max_path_loss"
                value={config.max_path_loss}
                onChange={handleChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div className="mt-2">
              <label className="block text-sm font-medium text-gray-700">Máximo de reflexiones</label>
              <input
                type="number"
                name="max_reflections"
                value={config.max_reflections}
                onChange={handleChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div className="mt-2">
              <label className="block text-sm font-medium text-gray-700">Máximo de transmisiones</label>
              <input
                type="number"
                name="max_transmissions"
                value={config.max_transmissions}
                onChange={handleChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div className="mt-2">
              <label className="block text-sm font-medium text-gray-700">Potencia de transmisión (W)</label>
              <input
                type="number"
                name="tx_power"
                value={config.tx_power}
                onChange={handleChange}
                step="0.01"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div className="mt-2">
              <label className="block text-sm font-medium text-gray-700">Frecuencia (GHz)</label>
              <input
                type="number"
                name="frequency"
                value={config.frequency / 1e9}
                onChange={handleChange}
                step="0.1"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div className="mt-2">
              <label className="block text-sm font-medium text-gray-700">Posición X del transmisor</label>
              <input
                type="number"
                name="tx_x"
                value={config.tx_x}
                onChange={handleChange}
                step="0.1"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div className="mt-2">
              <label className="block text-sm font-medium text-gray-700">Posición Y del transmisor</label>
              <input
                type="number"
                name="tx_y"
                value={config.tx_y}
                onChange={handleChange}
                step="0.1"
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div className="mt-2">
              <label className="block text-sm font-medium text-gray-700">Resolución</label>
              <input
                type="number"
                name="resolution"
                value={config.resolution}
                onChange={handleChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm p-2"
              />
            </div>
            <div className="mt-4">
              <button
                type="submit"
                className="inline-flex justify-center w-full rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:text-sm"
              >
                Iniciar Simulación
              </button>
            </div>
          </form>
          <button
            onClick={onClose}
            className="mt-2 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:text-sm"
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfigurationModal;