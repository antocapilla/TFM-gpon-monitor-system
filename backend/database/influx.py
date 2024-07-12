from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

# Asume que InfluxDB está corriendo en el mismo host que el servicio de Docker
INFLUXDB_URL = "http://influxdb:8086"
INFLUXDB_TOKEN = "mytoken"  # Este es el token que definimos en docker-compose.yml
INFLUXDB_ORG = "myorg"
INFLUXDB_BUCKET = "network_monitoring"

client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)
query_api = client.query_api()

def query_data(query: str):
    print("Ejecutando consulta:", query)  # Para depuración
    return query_api.query(query)

def write_points(points):
    write_api.write(bucket=INFLUXDB_BUCKET, record=points)