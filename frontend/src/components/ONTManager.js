import React, { useState, useEffect } from 'react';
import { getAvailableONTs, addONTToFloor, updateONTPosition } from '../services/apiService';

const ONTManager = ({ building, floor }) => {
  const [availableONTs, setAvailableONTs] = useState([]);
  const [selectedONT, setSelectedONT] = useState('');
  const [position, setPosition] = useState({ x: 0, y: 0 });

  useEffect(() => {
    const fetchAvailableONTs = async () => {
      const onts = await getAvailableONTs();
      setAvailableONTs(onts);
    };
    fetchAvailableONTs();
  }, []);

  const handleAddONT = async () => {
    if (selectedONT) {
      await addONTToFloor(building.name, floor.name, { serial: selectedONT, ...position });
      // Aquí puedes añadir lógica para actualizar el estado local o recargar los datos
    }
  };

  const handlePositionChange = (e) => {
    setPosition({ ...position, [e.target.name]: parseFloat(e.target.value) });
  };

  return (
    <div>
      <h3>Añadir ONT a {floor.name}</h3>
      <select value={selectedONT} onChange={(e) => setSelectedONT(e.target.value)}>
        <option value="">Seleccionar ONT</option>
        {availableONTs.map(ont => (
          <option key={ont} value={ont}>{ont}</option>
        ))}
      </select>
      <input
        type="number"
        name="x"
        value={position.x}
        onChange={handlePositionChange}
        placeholder="Posición X"
      />
      <input
        type="number"
        name="y"
        value={position.y}
        onChange={handlePositionChange}
        placeholder="Posición Y"
      />
      <button onClick={handleAddONT}>Añadir ONT</button>
    </div>
  );
};

export default ONTManager;