const TabSelector = ({ selectedTab, setSelectedTab }) => (
    <div className="mb-4">
      <button
        className={`px-4 py-2 rounded-l ${
          selectedTab === 'realtime' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
        }`}
        onClick={() => setSelectedTab('realtime')}
      >
        Datos en Tiempo Real
      </button>
      <button
        className={`px-4 py-2 rounded-r ${
          selectedTab === 'historical' ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-700'
        }`}
        onClick={() => setSelectedTab('historical')}
      >
        Datos Históricos
      </button>
    </div>
  );

export default TabSelector