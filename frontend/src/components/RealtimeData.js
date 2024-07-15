import React, { useState, useEffect } from 'react';
import ConfigurationModal from '../components/ConfigurationModal';
import DeleteConfirmationModal from '../components/DeleteConfirmationModal';

const RealtimeData = ({
    tableData,
    selectedMetrics,
    setSelectedMetrics,
    metricLabels,
    handleItemClick,
    configuration,
    setConfiguration,
    handleConfigSave,
    isModalOpen,
    setIsModalOpen,
    isDeleteModalOpen,
    setIsDeleteModalOpen,
    currentLevel,
    selectedBuilding,
    selectedFloor,
    selectedONT,
    handleDelete
}) => {
    return (
        <div className="bg-white rounded-lg shadow-md p-4 mb-4">
            <h2 className="text-3xl font-bold mb-6 text-gray-800">Datos en Tiempo Real</h2>

            

            {/* Data Table */}
            <div className="overflow-x-auto scrollbar-thin scrollbar-thumb-gray-300 scrollbar-track-gray-100"> 
                <table className="table-auto w-full whitespace-nowrap"> {/* Apply whitespace-nowrap to the table */}
                    <thead>
                        <tr>
                            <th className="px-4 py-2 sticky left-0 bg-white w-fit">ID</th>
                            {selectedMetrics.map((metric) => (
                                <th key={metric} className="px-4 py-2">
                                    {metricLabels[metric]}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {tableData.map((item) => (
                            <tr
                                key={item._id || item.name || item.serial}
                                className="cursor-pointer hover:bg-gray-100 py-2"
                                onClick={() => handleItemClick(item)}
                            >
                                <td className="border px-4 py-2 align-middle">{item._id || item.name || item.serial}</td>
                                {selectedMetrics.map((metric) => (
                                    <td key={metric} className="border px-4 py-2 align-middle">
                                        <div className="truncate max-w-[150px]"> {/* Limit width and truncate */}
                                            {item[metric]}
                                        </div>
                                    </td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
                <div className="h-4"></div> {/* Add spacing below the table */}
            </div> 

            {/* Buttons */}
            <div className="mb-4 flex justify-end space-x-2">
                <button
                    className="bg-red-500 text-white px-4 py-2 rounded-md shadow-md"
                    onClick={() => setIsDeleteModalOpen(true)}
                >
                    Borrar Datos
                </button>
                <button
                    className="bg-blue-500 text-white px-4 py-2 rounded-md shadow-md"
                    onClick={() => setIsModalOpen(true)}
                >
                    Configuración
                </button>
            </div>

            {/* Configuration Modal */}
            <ConfigurationModal
                isOpen={isModalOpen}
                onClose={() => setIsModalOpen(false)}
                configuration={configuration}
                setConfiguration={setConfiguration}
                selectedMetrics={selectedMetrics}
                setSelectedMetrics={setSelectedMetrics}
                metricLabels={metricLabels}
                handleConfigSave={handleConfigSave}
            />

            {/* Delete Confirmation Modal */}
            <DeleteConfirmationModal
                isOpen={isDeleteModalOpen}
                onClose={() => setIsDeleteModalOpen(false)}
                onConfirm={handleDelete}
                level={currentLevel}
                building={selectedBuilding}
                floor={selectedFloor}
                ont={selectedONT}
            />
        </div>
    );
};

export default RealtimeData;
