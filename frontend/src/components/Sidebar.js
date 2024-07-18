import React from 'react';
import { Link } from 'react-router-dom';
import logo from '../assets/logo.png'; // Ajusta esta ruta a la ubicación correcta de tu imagen

const Sidebar = ({ isOpen, setIsOpen }) => {
  return (
    <div className={`bg-custom-blue text-white w-64 space-y-6 py-7 px-2 absolute inset-y-0 left-0 transform ${isOpen ? 'translate-x-0' : '-translate-x-full'} transition duration-200 ease-in-out`}>
      {/* Logo o título del Sidebar */}
      <div className="text-white text-2xl font-semibold text-center">
        <img src={logo} alt="Logo" className="mx-auto" />
      </div>
      {/* Navegación */}
      <nav>
        <Link to="/" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-custom-dark-blue">Home</Link>
        <Link to="/manager" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-custom-dark-blue">Gestión de Espacios</Link>
        <Link to="/simulator" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-custom-dark-blue">Simulador de Configuración</Link>
        <Link to="/monitor" className="block py-2.5 px-4 rounded transition duration-200 hover:bg-custom-dark-blue">Monitoreo en Tiempo Real</Link>
      </nav>
      {/* Botón para ocultar el Sidebar */}
      <button
        onClick={() => setIsOpen(false)}
        className="w-full bg-custom-grey hover:bg-custom-blue text-white font-bold py-2 px-4 rounded"
      >
        Ocultar Sidebar
      </button>
    </div>
  );
};

export default Sidebar;
