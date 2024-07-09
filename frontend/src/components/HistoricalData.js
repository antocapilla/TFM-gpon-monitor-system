import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
const HistoricalData = ({ isLoading, error, timeSeriesData, startDate, setStartDate, endDate, setEndDate, selectedMetrics, metricLabels, formatTimestamp }) => (
    <div className="bg-white rounded-lg shadow-md p-4 mb-4">
      <h2 className="text-xl font-bold mb-2">Datos Históricos</h2>
      <div className="mb-4">
        {/* <input
          type="date"
          id="startDate"
          className="w-full p-2 border border-gray-300 rounded-md mb-2"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
        />
        <input
          type="date"
          id="endDate"
          className="w-full p-2 border border-gray-300 rounded-md"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
        /> */}
      </div>
      {isLoading ? (
        <div>Cargando datos...</div>
      ) : error ? (
        <div className="text-red-500">{error}</div>
      ) : timeSeriesData.length > 0 ? (
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={timeSeriesData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="timestamp" 
              tickFormatter={formatTimestamp}
              type="category"
              allowDuplicatedCategory={false}
            />
            <YAxis />
            <Tooltip labelFormatter={formatTimestamp} />
            <Legend />
            {selectedMetrics.map((metric) => (
              <Line
                key={metric}
                type="monotone"
                dataKey={metric}
                name={metricLabels[metric]}
                stroke={`#${Math.floor(Math.random() * 16777215).toString(16)}`}
                activeDot={{ r: 8 }}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <div>No hay datos disponibles para el período seleccionado.</div>
      )}
    </div>
  );

export default HistoricalData;