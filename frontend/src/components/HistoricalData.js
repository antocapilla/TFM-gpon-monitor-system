import React from 'react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, Label } from 'recharts';

const HistoricalData = ({ isLoading, error, timeSeriesData, startDate, setStartDate, endDate, setEndDate, selectedMetric, setSelectedHistoricalMetric, metricLabels, formatTimestamp }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-4 mb-4">
      <h2 className="text-xl font-bold mb-2">Datos Históricos</h2>

      <div className="mb-4 grid grid-cols-3 gap-4 items-center">
        {/* Metric Selector */}
        <div>
          <label htmlFor="metricSelect" className="block text-sm font-medium text-gray-700">Métrica:</label>
          <select
            id="metricSelect"
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            value={selectedMetric}
            onChange={(e) => setSelectedHistoricalMetric(e.target.value)}
          >
            {Object.keys(metricLabels).map((metric) => (
              <option key={metric} value={metric}>
                {metricLabels[metric]}
              </option>
            ))}
          </select>
        </div>

        {/* Date Range Inputs */}
        <div className="col-span-2 flex space-x-2">
          <div>
            <label htmlFor="startDate" className="block text-sm font-medium text-gray-700">Desde:</label>
            <input
              type="date"
              id="startDate"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
            />
          </div>
          <div>
            <label htmlFor="endDate" className="block text-sm font-medium text-gray-700">Hasta:</label>
            <input
              type="date"
              id="endDate"
              className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
            />
          </div>
        </div>
      </div>

      {/* Gráfica (Responsive) */}
      {isLoading ? (
        <div>Cargando datos...</div>
      ) : error ? (
        <div className="text-red-500">{error}</div>
      ) : timeSeriesData.length > 0 ? (
        <ResponsiveContainer width="100%" height={400}>  {/* Use ResponsiveContainer */}
          <LineChart data={timeSeriesData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={formatTimestamp}
              type="category"
              allowDuplicatedCategory={false}
            />
            <YAxis>
              <Label value={metricLabels[selectedMetric]} position="insideLeft" angle={-90} />
            </YAxis>
            <Tooltip labelFormatter={formatTimestamp} />
            <Legend />
            <Line
              type="monotone"
              dataKey={selectedMetric}
              name={metricLabels[selectedMetric]}
              stroke="#8884d8"
              strokeWidth={2}
              activeDot={{ r: 8 }}
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div>No hay datos disponibles para el período seleccionado.</div>
      )}
    </div>
  );
};

export default HistoricalData;
