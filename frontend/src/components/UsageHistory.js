// UsageHistory.js
import React from 'react';
import { Line } from 'react-chartjs-2';

const UsageHistory = ({ usageHistory }) => {
  const chartData = {
    labels: usageHistory.map((entry) => new Date(entry.timestamp).toLocaleTimeString()),
    datasets: [
      {
        label: 'Usuarios conectados',
        data: usageHistory.map((entry) => entry.connectedUsers),
        fill: false,
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  return React.createElement(
    'div',
    null,
    React.createElement('h3', { className: 'text-md font-bold mb-2' }, 'Historial de uso'),
    React.createElement(Line, { data: chartData })
  );
};

export default UsageHistory;