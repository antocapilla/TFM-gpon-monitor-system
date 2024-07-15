import json
from datetime import datetime, timedelta
import random

def generate_bulk_ont_data(config=None):
    if config is None:
        config = {}
    
    serials = config.get('serials', ["MKPGb4e1aa3d", "STGUe0e57a18", "STGUe0e59110", "STGUe0e66ee0"])
    interval_minutes = config.get('interval_minutes', 5)
    total_duration_minutes = config.get('total_duration_minutes', 1440)
    start_time = config.get('start_time', datetime(2024, 7, 11, 21, 0, 0))

    def generate_traffic(base_value, interval_minutes):
        change_rate = 0.8 + random.random() * 0.4  # 80% to 120% of base value
        return int(base_value * change_rate * (interval_minutes / 5))  # Adjust for interval

    def update_with_trend(value, trend, trend_direction, base_change):
        change = base_change * (0.8 + random.random() * 0.4)  # 80% to 120% of base change
        new_value = value + trend_direction * change
        return max(0, round(new_value))  # Ensure non-negative

    def initialize_ont(serial):
        return {
            "serial": serial,
            "wans": [
                {
                    "index": str(i),
                    "connectionStatus": "Connected",
                    "externalIPAddress": f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}",
                    "name": ["INTERNET", "TV"][i],
                    "natEnabled": random.choice([True, False]),
                    "addressingType": "DHCP",
                    "bytesReceived": random.randint(0, 1000000000),
                    "bytesSent": random.randint(0, 1000000000),
                    "uptime": random.randint(0, 3600),
                    "connectedWLANs": ["0", "1"],
                    "trend": random.choice(["increase", "decrease", "stable"]),
                    "trendDirection": 1,
                } for i in range(2)
            ],
            "wifi": [
                {
                    "interfaceIndex": str(i),
                    "ssid": f"ONT4W{i}{'_5G' if i == 1 else ''}",
                    "enable": True,
                    "status": "Up",
                    "channel": 6 if i == 0 else 44,
                    "totalAssociations": random.randint(0, 10),
                    "totalBytesReceived": random.randint(0, 1000000000),
                    "totalBytesSent": random.randint(0, 1000000000),
                    "trend": random.choice(["increase", "decrease", "stable"]),
                    "trendDirection": 1,
                } for i in range(2)
            ],
            "hosts": [
                {
                    "hostIndex": str(i),
                    "active": True,
                    "addressSource": "DHCP",
                    "clientID": "0",
                    "hostName": f"Device-{random.randint(100000, 999999)}",
                    "iPAddress": f"192.168.1.{10 + i}",
                    "interfaceType": "802.11",
                    "wlanId": str(i % 2),
                    "leaseTimeRemaining": 86400,
                    "macAddress": ':'.join(['{:02x}'.format(random.randint(0, 255)) for _ in range(6)]),
                    "userClassID": "0",
                    "vendorClassID": "0"
                } for i in range(5)
            ],
            "deviceInfo": {
                "softwareVersion": "V4.0.9-240524" if serial.startswith("MKPG") else "E10.V1.1.270",
                "upTime": random.randint(0, 86400)
            },
            "gpon": {
                "biasCurrent": random.randint(5, 15),
                "rxPower": -random.randint(15, 20),
                "status": "Up",
                "txPower": random.randint(1, 4),
                "transceiverTemperature": random.randint(25, 35)
            },
            "floor": f"Floor {random.randint(1, 10)}",
            "building": f"Building {random.choice(['A', 'B', 'C', 'D'])}"
        }

    def update_ont(ont, timestamp, interval_minutes):
        # Update WANs
        for wan in ont["wans"]:
            wan["bytesReceived"] += generate_traffic(1000000, interval_minutes)  # 1 MB base per 5 minutes
            wan["bytesSent"] += generate_traffic(800000, interval_minutes)  # 800 KB base per 5 minutes
            wan["uptime"] += interval_minutes * 60

            # Simulate occasional reconnects
            if random.random() < 0.01:  # 1% chance of reconnect
                wan["uptime"] = 0

        # Update WiFi
        for wifi in ont["wifi"]:
            wifi["totalAssociations"] = update_with_trend(wifi["totalAssociations"], wifi["trend"], wifi["trendDirection"], 1)
            wifi["totalBytesReceived"] += generate_traffic(500000, interval_minutes)  # 500 KB base per 5 minutes
            wifi["totalBytesSent"] += generate_traffic(400000, interval_minutes)  # 400 KB base per 5 minutes

        # Update hosts
        ont["hosts"] = [
            {
                **host,
                "active": random.random() > 0.1,
                "leaseTimeRemaining": max(0, host["leaseTimeRemaining"] - interval_minutes * 60)
            } for host in ont["hosts"]
        ]

        # Update GPON
        ont["gpon"]["biasCurrent"] = update_with_trend(ont["gpon"]["biasCurrent"], "stable", 1, 0.1)
        ont["gpon"]["rxPower"] = update_with_trend(ont["gpon"]["rxPower"], "stable", 1, 0.05)
        ont["gpon"]["txPower"] = update_with_trend(ont["gpon"]["txPower"], "stable", 1, 0.05)
        ont["gpon"]["transceiverTemperature"] = update_with_trend(ont["gpon"]["transceiverTemperature"], "stable", 1, 0.2)

        # Update device info
        ont["deviceInfo"]["upTime"] += interval_minutes * 60

        # Update trends (change direction every 6 hours)
        if timestamp.hour % 6 == 0 and timestamp.minute == 0:
            for wan in ont["wans"]:
                wan["trendDirection"] *= -1
            for wifi in ont["wifi"]:
                wifi["trendDirection"] *= -1

        ont["timestamp"] = timestamp.isoformat()
        return ont

    onts = [initialize_ont(serial) for serial in serials]

    all_data = []
    end_time = start_time + timedelta(minutes=total_duration_minutes)
    current_time = start_time

    while current_time <= end_time:
        onts = [update_ont(ont, current_time, interval_minutes) for ont in onts]
        all_data.extend(onts)
        current_time += timedelta(minutes=interval_minutes)

    return all_data

def generate_and_save():
    data = generate_bulk_ont_data({
        "serials": ["MKPGb4e1aa3d", "STGUe0e57a18", "STGUe0e59110", "STGUe0e66ee0"],
        "interval_minutes": 5,
        "total_duration_minutes": 1440,  # 24 hours
        "start_time": datetime(2024, 7, 11, 21, 0, 0)
    })
    with open('realistic_test_monitoring_data.json', 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Data saved to realistic_test_monitoring_data.json. Total records: {len(data)}")

if __name__ == "__main__":
    generate_and_save()