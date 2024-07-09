// En components/DeleteConfirmationModal.js

import React from 'react';

const DeleteConfirmationModal = ({ isOpen, onClose, onConfirm, level, building, floor, ont }) => {
  if (!isOpen) return null;

  let message = "¿Estás seguro de que quieres borrar los datos ";
  switch(level) {
    case 'buildings':
      message += "de todos los edificios?";
      break;
    case 'floors':
      message += `del edificio ${building}?`;
      break;
    case 'onts':
      message += `del piso ${floor} en el edificio ${building}?`;
      break;
    case 'ont':
      message += `de la ONT ${ont}?`;
      break;
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center">
      <div className="bg-white p-6 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Confirmar borrado</h2>
        <p className="mb-4">{message}</p>
        <div className="flex justify-end space-x-2">
          <button
            className="px-4 py-2 bg-gray-200 rounded"
            onClick={onClose}
          >
            Cancelar
          </button>
          <button
            className="px-4 py-2 bg-red-500 text-white rounded"
            onClick={onConfirm}
          >
            Borrar
          </button>
        </div>
      </div>
    </div>
  );
};

export default DeleteConfirmationModal;