// RealtimeData.js
const RealtimeData = ({ tableData, selectedMetrics, metricLabels, handleItemClick }) => {
  const updatedMetricLabels = {
    ...metricLabels,
    connectedHosts: 'Hosts Conectados',
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-4">
      <h2 className="text-xl font-bold mb-2">Datos en Tiempo Real</h2>
      <table className="table-auto w-full">
        <thead>
          <tr>
            <th className="px-4 py-2">ID</th>
            {selectedMetrics.map((metric) => (
              <th key={metric} className="px-4 py-2">
                {updatedMetricLabels[metric]}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {tableData.map((item) => (
            <tr
              key={item._id || item.name || item.serial}
              className="cursor-pointer hover:bg-gray-100"
              onClick={() => handleItemClick(item)}
            >
              <td className="border px-4 py-2">{item._id || item.name || item.serial}</td>
              {selectedMetrics.map((metric) => (
                <td key={metric} className="border px-4 py-2">
                  {item[metric]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default RealtimeData;