from models.monitoring_model import ONTData
from typing import List

class SWHService:
    @staticmethod
    def get_available_onts() -> List[str]:
        # Implementar la lógica para obtener la lista de ONTs disponibles del SWH
        # Por ahora, retornamos una lista de ejemplo
        return ["MKPGb4e1aa3d", "STGUe0e57a18", "STGUe0e59110", "STGUe0e66ee0"]
    
    @staticmethod
    def collect_ont_data(ont_serial: str) -> ONTData:
        # Implementar la lógica para recolectar datos de una ONT específica
        # Por ahora, retornamos datos de ejemplo
        return ONTData(
            serial=ont_serial,
            timestamp="2023-07-07T12:00:00Z",
            wans=[],
            wifi=[],
            hosts=[],
            deviceInfo={"softwareVersion": "1.0.0"}
        )

    @staticmethod
    def collect_and_store_ont_data():
        # Implementar la lógica para recolectar y almacenar datos de todas las ONTs
        # Esta función se puede llamar periódicamente para actualizar los datos
        pass