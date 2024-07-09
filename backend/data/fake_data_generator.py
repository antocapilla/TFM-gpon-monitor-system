from fastapi import APIRouter, BackgroundTasks
from typing import List
from services.monitoring_service import MonitoringService
from models.monitoring_model import ONTData
import random
import string
import datetime

router = APIRouter()

# Dispositivos de ejemplo
ont_devices = [
    {"serial": "MKPGb4e1aa3d", "name": "ONT 1", "floor": "Planta Baja", "building": "Hotel Sunshine"},
    {"serial": "STGUe0e57a18", "name": "ONT 2", "floor": "Planta Baja", "building": "Hotel Sunshine"},
    {"serial": "STGUe0e59110", "name": "ONT 3", "floor": "Primer Piso", "building": "Hotel Sunshine"},
    {"serial": "STGUe0e66ee0", "name": "ONT 4", "floor": "Primer Piso", "building": "Hotel Sunshine"}
]

@router.post("/simulate-ont-data")
def generate_and_store_ont_data(background_tasks: BackgroundTasks):
    background_tasks.add_task(_generate_and_store_ont_data)
    return {"message": "Simulación de datos de ONT iniciada en segundo plano"}

def _generate_and_store_ont_data():
    ont_data = []
    for _ in range(1000):
        for ont in ont_devices:
            data = {
                "serial": ont["serial"],
                "timestamp": datetime.datetime.now().isoformat(),
                "wans": [
                    {
                        "index": str(i+1),
                        "connectionStatus": random.choice(["Connected", "Disconnected"]),
                        "externalIPAddress": f"192.168.{i+1}.{random.randint(1, 254)}",
                        "name": f"WAN_{i+1}",
                        "natEnabled": random.choice([True, False]),
                        "addressingType": random.choice(["Static", "DHCP"]),
                        "bytesReceived": random.randint(0, 12000000),
                        "bytesSent": random.randint(0, 12000000),
                        "uptime": random.randint(0, 100000),
                        "connectedWLANs": [str(random.randint(1, 10)) for _ in range(random.randint(0, 3))]
                    } for i in range(6)
                ],
                "wifi": [
                    {
                        "interfaceIndex": str(i+1),
                        "ssid": f"SSID_{i+1}",
                        "enable": random.choice([True, False]),
                        "status": random.choice(["Up", "Down", "Error"]),
                        "channel": random.randint(1, 48),
                        "totalAssociations": random.randint(0, 100),
                        "totalBytesReceived": random.randint(0, 1000000),
                        "totalBytesSent": random.randint(0, 1000000)
                    } for i in range(10)
                ],
                "hosts": [
                    {
                        "ipAddress": f"192.168.{random.randint(1, 254)}.{random.randint(1, 254)}",
                        "macAddress": ''.join(random.choices(string.hexdigits.upper(), k=12)),
                        "hostname": ''.join(random.choices(string.ascii_uppercase + string.digits, k=random.randint(5, 15)))
                    } for _ in range(random.randint(0, 10))
                ],
                "deviceInfo": {
                    "softwareVersion": random.choice(["V4.0.9-240524", "E10.V1.1.270"])
                },
            }
            ont_data.append(ONTData(**data))
    MonitoringService.create_monitoring_data(ont_data)
    print(f"Se han generado y almacenado {len(ont_data)} registros de ONTData de ejemplo.")