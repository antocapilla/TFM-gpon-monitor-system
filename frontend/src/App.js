import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import Sidebar from './components/Sidebar'; // Asegúrate de importar el componente Sidebar
import Home from './pages/Home';
import Manager from './pages/Manager';
import Simulator from './pages/Simulator';
import Monitor from './pages/Monitor';
import EditablePolygon from './components/MapEditor';

function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(true); // Estado para controlar la visibilidad del Sidebar

  return (
    <Router>
      <div className="flex">
        <Sidebar isOpen={isSidebarOpen} setIsOpen={setIsSidebarOpen} />
        <div className={`flex-1 p-10 ${isSidebarOpen ? 'ml-64' : ''}`}>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/manager" element={<Manager />} />
            <Route path="/simulator" element={<Simulator />} />
            <Route path="/monitor" element={<Monitor />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
