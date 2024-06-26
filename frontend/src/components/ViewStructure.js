import React from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faChevronDown, faChevronUp, faTimes } from '@fortawesome/free-solid-svg-icons';
import { NavLink } from 'react-router-dom';

const ViewStructure = ({ buildings, onExpandBuilding, onAddBuilding, onAddFloor, onDeleteBuilding, onDeleteFloor, selectedFloor, onSelectFloor }) => {
  if (!buildings) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <p className="text-center text-gray-500">Cargando edificios...</p>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <div className="flow-root">
        <ul className="divide-y divide-gray-200">
          {buildings.map((building) => (
            <li key={building.name} className="py-3 sm:py-4">
              <div className="flex items-center space-x-4">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {building.name}
                  </p>
                  <p className="text-sm text-gray-500 truncate">
                    {`${building.floors.length} floors`}
                  </p>
                </div>
                <div>
                  <FontAwesomeIcon
                    icon={building.expanded ? faChevronUp : faChevronDown}
                    className="text-gray-400 cursor-pointer"
                    onClick={() => onExpandBuilding(building)}
                  />
                </div>
                <div>
                  <FontAwesomeIcon
                    icon={faTimes}
                    className="text-gray-400 cursor-pointer"
                    onClick={() => onDeleteBuilding(building)}
                  />
                </div>
              </div>
              {building.expanded && (
                <div className="mt-2">
                  {building.floors.map((floor) => (
                    <div key={floor.name} className={`flex justify-between items-center px-4 py-2 text-sm rounded-lg text-gray-700 bg-gray-50 hover:bg-gray-100 ${selectedFloor === floor.name ? 'bg-gray-200' : ''}`} onClick={() => onSelectFloor(floor, building)}>
                      <span>{floor.name}</span>
                      <FontAwesomeIcon
                        icon={faTimes}
                        className="text-red-500 cursor-pointer"
                        onClick={(e) => {
                          e.stopPropagation();
                          onDeleteFloor(building, floor);
                        }}
                      />
                    </div>
                  ))}
                  <button
                    className="w-full text-sm text-white bg-custom-blue hover:bg-custom-blue-2 mt-4 py-2 rounded-lg"
                    onClick={() => onAddFloor(building)}
                  >
                    Agregar Planta
                  </button>
                </div>
              )}
            </li>
          ))}
        </ul>
      </div>
      <div className="mt-6">
        <button
          className="w-full text-sm text-white bg-custom-dark-blue hover:bg-custom-dark-blue-2 py-2 rounded-lg"
          onClick={onAddBuilding}
        >
          Agregar Edificio
        </button>
      </div>
    </div>
  );
};

export default ViewStructure;