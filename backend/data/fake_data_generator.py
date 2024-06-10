# data/fake_data_generator.py

import random
from datetime import datetime, timedelta

def generate_fake_monitoring_data(num_devices, num_records):
    devices = [f"device_{i}" for i in range(1, num_devices + 1)]
    data = []

    for _ in range(num_records):
        for device_id in devices:
            timestamp = datetime.now() - timedelta(minutes=random.randint(0, 59))
            record = {
                "device_id": device_id,
                "timestamp": timestamp,
                "data": {
                    "temperature": random.uniform(20, 30),
                    "humidity": random.uniform(40, 60),
                    "cpu_usage": random.uniform(0, 100),
                    "memory_usage": random.uniform(0, 100)
                }
            }
            data.append(record)

    return data