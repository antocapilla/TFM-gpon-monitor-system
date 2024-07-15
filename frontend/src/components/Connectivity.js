import React, { useState, useEffect } from 'react';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Tabs, TabList, Tab, TabPanel } from 'react-tabs';
import 'react-tabs/style/react-tabs.css';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8', '#82ca9d'];

const mockData = {
  wan_services: {
    Internet: {
      active_connections: 150,
      total_bandwidth: 1000,
      status: "Active",
      bytesReceived: 5000000000,
      bytesSent: 2000000000,
      uptime: 2592000, // 30 days in seconds
      latency: 15 // ms
    },
    VoIP: {
      active_connections: 50,
      total_bandwidth: 100,
      status: "Active",
      bytesReceived: 500000000,
      bytesSent: 300000000,
      uptime: 2591000,
      latency: 10
    },
    IPTV: {
      active_connections: 75,
      total_bandwidth: 500,
      status: "Active",
      bytesReceived: 10000000000,
      bytesSent: 500000000,
      uptime: 2590000,
      latency: 20
    }
  },
  wlan_networks: {
    "Guest-WiFi": {
      connected_clients: 100,
      max_clients: 200,
      total_traffic: 500,
      channels: [1, 6, 11],
      frequency_band: "2.4GHz",
      totalBytesReceived: 2000000000,
      totalBytesSent: 1000000000,
      signal_strength: -65 // dBm
    },
    "Staff-WiFi": {
      connected_clients: 40,
      max_clients: 100,
      total_traffic: 200,
      channels: [36, 40],
      frequency_band: "5GHz",
      totalBytesReceived: 1500000000,
      totalBytesSent: 750000000,
      signal_strength: -55
    },
    "IoT-Network": {
      connected_clients: 150,
      max_clients: 300,
      total_traffic: 50,
      channels: [1],
      frequency_band: "2.4GHz",
      totalBytesReceived: 500000000,
      totalBytesSent: 250000000,
      signal_strength: -70
    }
  },
  historical_data: {
    bandwidth_usage: [
      { date: '2023-01-01', Internet: 800, VoIP: 80, IPTV: 400 },
      { date: '2023-01-02', Internet: 850, VoIP: 85, IPTV: 420 },
      { date: '2023-01-03', Internet: 900, VoIP: 90, IPTV: 450 },
      { date: '2023-01-04', Internet: 950, VoIP: 95, IPTV: 480 },
      { date: '2023-01-05', Internet: 1000, VoIP: 100, IPTV: 500 }
    ],
    client_connections: [
      { date: '2023-01-01', 'Guest-WiFi': 80, 'Staff-WiFi': 30, 'IoT-Network': 120 },
      { date: '2023-01-02', 'Guest-WiFi': 85, 'Staff-WiFi': 35, 'IoT-Network': 130 },
      { date: '2023-01-03', 'Guest-WiFi': 90, 'Staff-WiFi': 38, 'IoT-Network': 140 },
      { date: '2023-01-04', 'Guest-WiFi': 95, 'Staff-WiFi': 39, 'IoT-Network': 145 },
      { date: '2023-01-05', 'Guest-WiFi': 100, 'Staff-WiFi': 40, 'IoT-Network': 150 }
    ]
  }
};

const Connectivity = ({ level, building, floor, ont }) => {
  const [activeTab, setActiveTab] = useState(0);
  const { wan_services, wlan_networks, historical_data } = mockData;

  const wanOverviewData = Object.entries(wan_services).map(([service, stats]) => ({
    name: service,
    value: stats.total_bandwidth
  }));

  const wlanOverviewData = Object.entries(wlan_networks).map(([ssid, stats]) => ({
    name: ssid,
    value: stats.connected_clients
  }));

  const formatBytes = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatUptime = (seconds) => {
    const days = Math.floor(seconds / (3600*24));
    const hours = Math.floor(seconds % (3600*24) / 3600);
    const minutes = Math.floor(seconds % 3600 / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  return (
    <div className="bg-gray-100 min-h-screen">
    <div className="p-4 bg-gray-100 flex">
      <div className="flex-grow">
        <h2 className="text-3xl font-bold mb-6 text-gray-800">Conectividad</h2>
        <Tabs selectedIndex={activeTab} onSelect={index => setActiveTab(index)}>
          <TabPanel>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-4 rounded-lg shadow">
                <h3 className="text-xl font-semibold mb-4">WAN Services Overview</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={wanOverviewData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {wanOverviewData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <h3 className="text-xl font-semibold mb-4">WLAN Networks Overview</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={wlanOverviewData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {wlanOverviewData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>
          </TabPanel>

          <TabPanel>
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-xl font-semibold mb-4">WAN Services Details</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white">
                  <thead>
                    <tr>
                      <th className="px-4 py-2">Service</th>
                      <th className="px-4 py-2">Active Connections</th>
                      <th className="px-4 py-2">Total Bandwidth (Mbps)</th>
                      <th className="px-4 py-2">Status</th>
                      <th className="px-4 py-2">Bytes Received</th>
                      <th className="px-4 py-2">Bytes Sent</th>
                      <th className="px-4 py-2">Uptime</th>
                      <th className="px-4 py-2">Latency (ms)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(wan_services).map(([service, stats]) => (
                      <tr key={service}>
                        <td className="border px-4 py-2">{service}</td>
                        <td className="border px-4 py-2">{stats.active_connections}</td>
                        <td className="border px-4 py-2">{stats.total_bandwidth}</td>
                        <td className="border px-4 py-2">{stats.status}</td>
                        <td className="border px-4 py-2">{formatBytes(stats.bytesReceived)}</td>
                        <td className="border px-4 py-2">{formatBytes(stats.bytesSent)}</td>
                        <td className="border px-4 py-2">{formatUptime(stats.uptime)}</td>
                        <td className="border px-4 py-2">{stats.latency}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </TabPanel>

          <TabPanel>
            <div className="bg-white p-4 rounded-lg shadow">
              <h3 className="text-xl font-semibold mb-4">WLAN Networks Details</h3>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white">
                  <thead>
                    <tr>
                      <th className="px-4 py-2">SSID</th>
                      <th className="px-4 py-2">Connected Clients</th>
                      <th className="px-4 py-2">Max Clients</th>
                      <th className="px-4 py-2">Total Traffic (Mbps)</th>
                      <th className="px-4 py-2">Channels</th>
                      <th className="px-4 py-2">Frequency Band</th>
                      <th className="px-4 py-2">Total Bytes Received</th>
                      <th className="px-4 py-2">Total Bytes Sent</th>
                      <th className="px-4 py-2">Signal Strength (dBm)</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(wlan_networks).map(([ssid, stats]) => (
                      <tr key={ssid}>
                        <td className="border px-4 py-2">{ssid}</td>
                        <td className="border px-4 py-2">{stats.connected_clients}</td>
                        <td className="border px-4 py-2">{stats.max_clients}</td>
                        <td className="border px-4 py-2">{stats.total_traffic}</td>
                        <td className="border px-4 py-2">{stats.channels.join(', ')}</td>
                        <td className="border px-4 py-2">{stats.frequency_band}</td>
                        <td className="border px-4 py-2">{formatBytes(stats.totalBytesReceived)}</td>
                        <td className="border px-4 py-2">{formatBytes(stats.totalBytesSent)}</td>
                        <td className="border px-4 py-2">{stats.signal_strength}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </TabPanel>

          <TabPanel>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white p-4 rounded-lg shadow">
                <h3 className="text-xl font-semibold mb-4">Bandwidth Usage Over Time</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={historical_data.bandwidth_usage}>
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="Internet" stroke="#8884d8" />
                    <Line type="monotone" dataKey="VoIP" stroke="#82ca9d" />
                    <Line type="monotone" dataKey="IPTV" stroke="#ffc658" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div className="bg-white p-4 rounded-lg shadow">
                <h3 className="text-xl font-semibold mb-4">Client Connections Over Time</h3>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={historical_data.client_connections}>
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Line type="monotone" dataKey="Guest-WiFi" stroke="#8884d8" />
                    <Line type="monotone" dataKey="Staff-WiFi" stroke="#82ca9d" />
                    <Line type="monotone" dataKey="IoT-Network" stroke="#ffc658" />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>
          </TabPanel>
        </Tabs>
      </div>
      <div className="flex-shrink-0">
        <Tabs selectedIndex={activeTab} onSelect={index => setActiveTab(index)} >
            <TabList className={'flex flex-col bg-gray-200 p-2 rounded-lg w-fit justify-center'}> 
                <Tab className={`px-4 py-2 mb-2 cursor-pointer ${activeTab === 0 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-800'}`}>
                    Vista General
                </Tab>
                <Tab className={`px-4 py-2 mb-2 cursor-pointer ${activeTab === 1 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-800'}`}>
                    Servicios WAN
                </Tab>
                <Tab className={`px-4 py-2 mb-2 cursor-pointer ${activeTab === 2 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-800'}`}>
                    Redes WLAN
                </Tab>
                <Tab className={`px-4 py-2 mb-2 cursor-pointer ${activeTab === 3 ? 'bg-blue-600 text-white' : 'bg-gray-300 text-gray-800'}`}>
                    Uso Historico
                </Tab>
            </TabList>
        </Tabs>
      </div>
    </div>

    
    
    <div className="mt-8 bg-white p-4 rounded-lg shadow">
    <h3 className="text-xl font-semibold mb-4">Alerts and Notifications</h3>
    <ul className="divide-y divide-gray-200">
      <li className="py-4 flex items-center">
        <span className="h-8 w-8 rounded-full bg-red-100 flex items-center justify-center mr-3">
          <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </span>
        <span className="flex-grow">High bandwidth usage detected on Internet service</span>
        <button className="ml-4 text-sm text-blue-500 hover:text-blue-700">View</button>
      </li>
      <li className="py-4 flex items-center">
        <span className="h-8 w-8 rounded-full bg-yellow-100 flex items-center justify-center mr-3">
          <svg className="h-5 w-5 text-yellow-500" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        </span>
        <span className="flex-grow">Guest-WiFi approaching maximum client capacity</span>
        <button className="ml-4 text-sm text-blue-500 hover:text-blue-700">View</button>
      </li>
    </ul>
    </div>
    <div className="mt-8 bg-white p-4 rounded-lg shadow">
        <h3 className="text-xl font-semibold mb-4">Quick Actions</h3>
        <div className="flex flex-wrap gap-4">
          <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
            Ejecutar Diagnostico de Red
          </button>
          <button className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">
            Optimizar Canales WiFi
          </button>
          <button className="bg-yellow-500 hover:bg-yellow-700 text-white font-bold py-2 px-4 rounded">
            Generar un Reporte de Conectividad
          </button>
        </div>
      </div>
  </div>
  );
};

export default Connectivity;
