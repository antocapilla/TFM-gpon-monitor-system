const ConfigurationModal = ({ isOpen, onClose, configuration, setConfiguration, selectedMetrics, setSelectedMetrics, metricLabels, handleConfigSave }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold mb-4">Configuración de Monitorización</h2>
        <div className="mb-4">
          <label htmlFor="collectionInterval" className="block text-gray-700 font-bold mb-2">
            Intervalo de Recopilación (minutos):
          </label>
          <input
            type="number"
            id="collectionInterval"
            className="w-full p-2 border border-gray-300 rounded-md"
            value={configuration.interval}
            onChange={(e) => setConfiguration({...configuration, interval: parseInt(e.target.value)})}
          />
        </div>
        <div className="mb-4">
          <label htmlFor="metrics" className="block text-gray-700 font-bold mb-2">
            Métricas a Monitorizar:
          </label>
          <select
            id="metrics"
            className="w-full p-2 border border-gray-300 rounded-md"
            multiple
            value={selectedMetrics}
            onChange={(e) =>
              setSelectedMetrics(
                Array.from(e.target.selectedOptions, (option) => option.value)
              )
            }
          >
            {Object.entries(metricLabels).map(([key, label]) => (
              <option key={key} value={key}>
                {label}
              </option>
            ))}
          </select>
        </div>
        <div className="flex justify-end">
          <button
            className="bg-blue-500 text-white px-4 py-2 rounded-md shadow-md mr-2"
            onClick={handleConfigSave}
          >
            Guardar
          </button>
          <button
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded-md shadow-md"
            onClick={onClose}
          >
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfigurationModal;