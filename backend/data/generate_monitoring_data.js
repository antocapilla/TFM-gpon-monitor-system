const fs = require('fs');

const generateBulkONTData = (config = {}) => {
  const {
    serials = ["MKPGb4e1aa3d", "STGUe0e57a18", "STGUe0e59110", "STGUe0e66ee0"],
    intervalMinutes = 5,
    totalDurationMinutes = 1440,
    errorProbability = 0.25,
    startTime = new Date('2024-07-11T21:00:00Z')
  } = config;

  const generateWAN = (index, timestamp) => ({
    index: index.toString(),
    connectionStatus: Math.random() > 0.2 ? 'Connected' : 'Disconnected',
    externalIPAddress: Math.random() > 0.5 ? `192.168.3.${20 + Math.floor(Math.random() * 10)}` : '',
    name: ['INTERNET', 'TV', 'VOIP', 'EKCAST', 'default wan'][Math.floor(Math.random() * 5)],
    natEnabled: Math.random() > 0.5,
    addressingType: Math.random() > 0.5 ? 'DHCP' : 'Static',
    bytesReceived: Math.floor(Math.random() * 100000000),
    bytesSent: Math.floor(Math.random() * 100000000),
    uptime: Math.floor((timestamp - startTime) / 1000),
    connectedWLANs: Array.from({length: Math.floor(Math.random() * 3)}, () => Math.floor(Math.random() * 10).toString())
  });

  const generateWiFi = (index) => ({
    interfaceIndex: index.toString(),
    ssid: Math.random() > 0.3 ? `ONT4W${Math.floor(Math.random() * 10)}${Math.random() > 0.5 ? '_5G' : ''}` : 'Empty',
    enable: true,
    status: Math.random() > 0.1 ? 'Up' : 'Down',
    channel: Math.random() > 0.5 ? 44 : 11,
    totalAssociations: Math.floor(Math.random() * 10),
    totalBytesReceived: Math.floor(Math.random() * 1000000),
    totalBytesSent: Math.floor(Math.random() * 1000000)
  });

  const generateHost = (index) => ({
    hostIndex: index.toString(),
    active: Math.random() > 0.5,
    addressSource: 'DHCP',
    clientID: '0 ',
    hostName: `HUAWEI_${['P30', 'P40', 'Mate 20', 'P smart 2019'][Math.floor(Math.random() * 4)]}-${Math.random().toString(36).substring(2, 10)}`,
    iPAddress: `192.168.0.${Math.floor(Math.random() * 254) + 1}`,
    interfaceType: '802.11',
    wlanId: Math.random() > 0.5 ? Math.floor(Math.random() * 10).toString() : null,
    leaseTimeRemaining: Math.floor(Math.random() * 100000),
    macAddress: Array.from({length: 6}, () => Math.floor(Math.random() * 256).toString(16).padStart(2, '0')).join(':'),
    userClassID: '0 ',
    vendorClassID: '0 '
  });

  let onts = serials.map(serial => ({
    serial,
    wans: Array.from({length: Math.floor(Math.random() * 5) + 1}, (_, i) => generateWAN(i + 1, startTime)),
    wifi: Array.from({length: 10}, (_, i) => generateWiFi(i + 1)),
    hosts: Array.from({length: Math.floor(Math.random() * 20) + 1}, (_, i) => generateHost(i + 1)),
    deviceInfo: {
      softwareVersion: serial.startsWith('MKPG') ? 'V4.0.9-240524' : 'E10.V1.1.270',
      upTime: 0
    },
    gpon: {
      biasCurrent: Math.floor(Math.random() * 20),
      rxPower: -Math.floor(Math.random() * 20),
      status: 'Up',
      txPower: Math.floor(Math.random() * 5),
      transceiverTemperature: Math.floor(Math.random() * 200)
    }
  }));

  const updateData = (timestamp) => {
    return onts.map(ont => {
      if (Math.random() < errorProbability) {
        return {
          serial: ont.serial,
          timestamp: timestamp.toISOString(),
          error: "Request timed out",
          deviceInfo: {
            softwareVersion: ont.deviceInfo.softwareVersion,
            upTime: Math.floor((timestamp - startTime) / 1000)
          }
        };
      }

      // Update WANs
      ont.wans.forEach(wan => {
        if (wan.connectionStatus === 'Connected') {
          wan.bytesReceived += Math.floor(Math.random() * 1000000);
          wan.bytesSent += Math.floor(Math.random() * 1000000);
          wan.uptime = Math.floor((timestamp - startTime) / 1000);
        }
      });

      // Update WiFi
      ont.wifi.forEach(wifi => {
        if (wifi.status === 'Up') {
          wifi.totalAssociations = Math.floor(Math.random() * 10);
          wifi.totalBytesReceived += Math.floor(Math.random() * 100000);
          wifi.totalBytesSent += Math.floor(Math.random() * 100000);
        }
      });

      // Update hosts
      ont.hosts.forEach(host => {
        host.active = Math.random() > 0.5;
        if (host.active) {
          host.leaseTimeRemaining = Math.max(0, host.leaseTimeRemaining - intervalMinutes * 60);
        }
      });

      // Update GPON
      ont.gpon.rxPower = -Math.floor(Math.random() * 20);
      ont.gpon.txPower = Math.floor(Math.random() * 5);
      ont.gpon.transceiverTemperature = Math.floor(Math.random() * 200);

      // Update device info
      ont.deviceInfo.upTime = Math.floor((timestamp - startTime) / 1000);

      return {
        ...ont,
        timestamp: timestamp.toISOString()
      };
    });
  };

  const generateAllData = () => {
    const allData = [];
    const endTime = new Date(startTime.getTime() + totalDurationMinutes * 60000);

    for (let currentTime = new Date(startTime); currentTime <= endTime; currentTime.setMinutes(currentTime.getMinutes() + intervalMinutes)) {
      allData.push(...updateData(currentTime));
    }

    return allData;
  };

  return {
    generateAndSave: () => {
      const data = generateAllData();
      fs.writeFileSync('test_monitoring_data.json', JSON.stringify(data, null, 2));
      console.log(`Data saved to test_monitoring_data.json. Total records: ${data.length}`);
    }
  };
};

// Uso del generador
const generator = generateBulkONTData({
  serials: ["MKPGb4e1aa3d", "STGUe0e57a18", "STGUe0e59110", "STGUe0e66ee0"],
  intervalMinutes: 5,
  totalDurationMinutes: 1440, // 24 horas
  errorProbability: 0.25,
  startTime: new Date('2024-07-11T21:00:00Z')
});

generator.generateAndSave();