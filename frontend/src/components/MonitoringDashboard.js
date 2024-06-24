import React from 'react';
import Map from './Map';
import MetricsPanel from './MetricsPanel';
import UsageHistory from './UsageHistory';
import Alerts from './Alerts';
import ReportGenerator from './ReportGenerator';

const MonitoringDashboard = () => {
  return (
    <div className="flex flex-col h-screen">
      <div className="flex-grow grid grid-cols-3 gap-4 p-4">
        <div className="col-span-2">
          <Map />
        </div>
        <div className="col-span-1">
          <MetricsPanel />
          <Alerts />
        </div>
      </div>
      <div className="flex justify-around p-4">
        <UsageHistory />
        <ReportGenerator />
      </div>
    </div>
  );
};

export default MonitoringDashboard;