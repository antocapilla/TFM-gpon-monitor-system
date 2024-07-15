const fs = require('fs');

const generateBulkONTData = (config = {}) => {
  const {
    serials = ["MKPGb4e1aa3d", "STGUe0e57a18", "STGUe0e59110", "STGUe0e66ee0"],
    intervalMinutes = 5,
    totalDurationMinutes = 1440,
    startTime = new Date('2024-07-11T21:00:00Z')
  } = config;

  const generateTraffic = (baseValue, intervalMinutes) => {
    const changeRate = 0.8 + Math.random() * 0.4; // 80% to 120% of base value
    return Math.floor(baseValue * changeRate * (intervalMinutes / 5)); // Adjust for interval
  };

  const updateWithTrend = (value, trend, trendDirection, baseChange) => {
    const change = baseChange * (0.8 + Math.random() * 0.4); // 80% to 120% of base change
    const newValue = value + trendDirection * change;
    return Math.max(0, Math.round(newValue)); // Ensure non-negative
  };

  const initializeONT = (serial) => ({
    serial,
    wans: Array.from({ length: 2 }, (_, i) => ({
      index: i.toString(),
      connectionStatus: 'Connected',
      externalIPAddress: `192.168.${Math.floor(Math.random() * 256)}.${Math.floor(Math.random() * 256)}`,
      name: ['INTERNET', 'TV'][i],
      natEnabled: true,
      addressingType: 'DHCP',
      bytesReceived: Math.floor(Math.random() * 1000000000),
      bytesSent: Math.floor(Math.random() * 1000000000),
      uptime: Math.floor(Math.random() * 3600),
      connectedWLANs: ['0', '1'],
      trend: Math.random() < 0.5 ? 'increase' : (Math.random() < 0.5 ? 'decrease' : 'stable'),
      trendDirection: 1,
    })),
    wifi: Array.from({ length: 2 }, (_, i) => ({
      interfaceIndex: i.toString(),
      ssid: `ONT4W${i}${i === 1 ? '_5G' : ''}`,
      enable: true,
      status: 'Up',
      channel: i === 0 ? 6 : 44,
      totalAssociations: Math.floor(Math.random() * 10),
      totalBytesReceived: Math.floor(Math.random() * 1000000000),
      totalBytesSent: Math.floor(Math.random() * 1000000000),
      trend: Math.random() < 0.5 ? 'increase' : (Math.random() < 0.5 ? 'decrease' : 'stable'),
      trendDirection: 1,
    })),
    hosts: Array.from({ length: 5 }, (_, i) => ({
      hostIndex: i.toString(),
      active: true,
      addressSource: 'DHCP',
      clientID: '0',
      hostName: `Device-${Math.random().toString(36).substring(2, 8)}`,
      iPAddress: `192.168.1.${10 + i}`,
      interfaceType: '802.11',
      wlanId: (i % 2).toString(),
      leaseTimeRemaining: 86400,
      macAddress: Array.from({length: 6}, () => Math.floor(Math.random() * 256).toString(16).padStart(2, '0')).join(':'),
      userClassID: '0',
      vendorClassID: '0'
    })),
    deviceInfo: {
      softwareVersion: serial.startsWith('MKPG') ? 'V4.0.9-240524' : 'E10.V1.1.270',
      upTime: Math.floor(Math.random() * 86400)
    },
    gpon: {
      biasCurrent: Math.floor(Math.random() * 10) + 5,
      rxPower: -(Math.floor(Math.random() * 5) + 15),
      status: 'Up',
      txPower: Math.floor(Math.random() * 3) + 1,
      transceiverTemperature: Math.floor(Math.random() * 10) + 25
    },
    floor: `Floor ${Math.floor(Math.random() * 10) + 1}`,
    building: `Building ${['A', 'B', 'C', 'D'][Math.floor(Math.random() * 4)]}`
  });

  let onts = serials.map(initializeONT);

  const updateONT = (ont, timestamp, intervalMinutes) => {
    // Update WANs
    ont.wans.forEach(wan => {
      wan.bytesReceived += generateTraffic(1000000, intervalMinutes); // 1 MB base per 5 minutes
      wan.bytesSent += generateTraffic(800000, intervalMinutes);    // 800 KB base per 5 minutes
      wan.uptime += intervalMinutes * 60;

      // Simulate occasional reconnects
      if (Math.random() < 0.01) { // 1% chance of reconnect
        wan.uptime = 0;
      }
    });

    // Update WiFi
    ont.wifi.forEach(wifi => {
      wifi.totalAssociations = updateWithTrend(wifi.totalAssociations, wifi.trend, wifi.trendDirection, 1);
      wifi.totalBytesReceived += generateTraffic(500000, intervalMinutes); // 500 KB base per 5 minutes
      wifi.totalBytesSent += generateTraffic(400000, intervalMinutes);    // 400 KB base per 5 minutes
    });

    // Update hosts
    ont.hosts = ont.hosts.map(host => ({
      ...host,
      active: Math.random() > 0.1,
      leaseTimeRemaining: Math.max(0, host.leaseTimeRemaining - intervalMinutes * 60)
    }));

    // Update GPON
    ont.gpon.biasCurrent = updateWithTrend(ont.gpon.biasCurrent, 'stable', 1, 0.1);
    ont.gpon.rxPower = updateWithTrend(ont.gpon.rxPower, 'stable', 1, 0.05);
    ont.gpon.txPower = updateWithTrend(ont.gpon.txPower, 'stable', 1, 0.05);
    ont.gpon.transceiverTemperature = updateWithTrend(ont.gpon.transceiverTemperature, 'stable', 1, 0.2);

    // Update device info
    ont.deviceInfo.upTime += intervalMinutes * 60;

    // Update trends (change direction every 6 hours)
    if (timestamp.getHours() % 6 === 0 && timestamp.getMinutes() === 0) {
      ont.wans.forEach(wan => {
        wan.trendDirection *= -1;
      });
      ont.wifi.forEach(wifi => {
        wifi.trendDirection *= -1;
      });
    }

    return {
      ...ont,
      timestamp: timestamp.toISOString()
    };
  };

  const generateAllData = () => {
    const allData = [];
    const endTime = new Date(startTime.getTime() + totalDurationMinutes * 60000);

    for (let currentTime = new Date(startTime); currentTime <= endTime; currentTime.setMinutes(currentTime.getMinutes() + intervalMinutes)) {
      onts = onts.map(ont => updateONT(ont, currentTime, intervalMinutes));
      const currentData = onts.map(ont => ({...ont, timestamp: currentTime.toISOString()}));
      allData.push(...currentData);
    }

    return allData;
  };

  return {
    generateAndSave: () => {
      const data = generateAllData();
      fs.writeFileSync('realistic_test_monitoring_data.json', JSON.stringify(data, null, 2));
      console.log(`Data saved to realistic_test_monitoring_data.json. Total records: ${data.length}`);
    }
  };
};

// Uso del generador
const generator = generateBulkONTData({
  serials: ["MKPGb4e1aa3d", "STGUe0e57a18", "STGUe0e59110", "STGUe0e66ee0"],
  intervalMinutes: 5,
  totalDurationMinutes: 1440, // 24 horas
  startTime: new Date('2024-07-11T21:00:00Z')
});

generator.generateAndSave();
