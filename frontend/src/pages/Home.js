import React from 'react';
import Sidebar from '../components/Sidebar';

function Home() {
  return (
    <div className="container mx-auto px-4">
      <Sidebar />
      <div className="my-10">
        <h1 className="text-5xl font-bold text-custom-dark-blue text-center mb-10">
          Bienvenido a SpaceManager
        </h1>
        <div className="space-y-10">
          {/* Sección de Gestión de Espacios */}
          <section className="bg-custom-blue shadow-xl rounded-lg p-6 text-white">
            <h2 className="text-3xl font-bold mb-4">Gestión de Espacios</h2>
            <p className="text-lg mb-4">
            Herramienta para la organización y gestión de espacios físicos. Permite cargar mapas de planta y definir zonas específicas dentro de edificios.
            </p>
            {/* Ilustración o componente visual para Gestión de Espacios */}
          </section>
          
          {/* Sección de Simulador de Configuración */}
          <section className="bg-custom-grey shadow-xl rounded-lg p-6 text-custom-dark-blue">
            <h2 className="text-3xl font-bold mb-4">Simulador de Configuración</h2>
            <p className="text-lg mb-4">
            Facilita la planificación de la colocación de dispositivos y la simulación de la señal. Ayuda a optimizar la disposición y configuración antes de la implementación física.
            </p>
            {/* Ilustración o componente visual para Simulador de Configuración */}
          </section>

          {/* Sección de Monitoreo en Tiempo Real */}
          <section className="bg-custom-dark-blue shadow-xl rounded-lg p-6 text-white">
            <h2 className="text-3xl font-bold mb-4">Monitoreo en Tiempo Real</h2>
            <p className="text-lg mb-4">
              Proporciona capacidades de seguimiento en tiempo real de dispositivos y señales dentro de los espacios gestionados. Ofrece información actualizada sobre el estado y rendimiento de cada dispositivo.
            </p>
            {/* Ilustración o componente visual para Monitoreo en Tiempo Real */}
          </section>
        </div>
      </div>
    </div>
  );
}

export default Home;
