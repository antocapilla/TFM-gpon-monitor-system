// ReportGenerator.js
import React from 'react';

const ReportGenerator = () => {
  return React.createElement(
    'div',
    { className: 'bg-white shadow-md rounded-lg p-4' },
    React.createElement('h2', { className: 'text-lg font-bold mb-4' }, 'Generar informe'),
    React.createElement(
      'div',
      null,
      React.createElement(
        'label',
        { htmlFor: 'start-date', className: 'block font-medium text-gray-700' },
        'Fecha de inicio'
      ),
      React.createElement('input', {
        type: 'date',
        id: 'start-date',
        name: 'start-date',
        className: 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-300 focus:ring focus:ring-indigo-200 focus:ring-opacity-50',
      })
    ),
    React.createElement(
      'button',
      {
        type: 'button',
        className: 'mt-4 inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500',
      },
      'Generar informe'
    )
  );
};

export default ReportGenerator;