const Summary = ({ latestValues, selectedMetrics, metricLabels }) => (
    <div className="bg-white rounded-lg shadow-md p-4 mb-4">
      <h2 className="text-xl font-bold mb-2">Resumen</h2>
      <div className="grid grid-cols-3 gap-4">
        {selectedMetrics.map((key) => (
          latestValues[key] !== undefined && (
            <div key={key}>
              <p className="text-gray-600">{metricLabels[key]}:</p>
              <p className="text-lg font-bold">{latestValues[key]}</p>
            </div>
          )
        ))}
      </div>
    </div>
  );

export default Summary;