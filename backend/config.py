import os

# URL(s) del frontend permitidas por CORS. Acepta una lista separada por comas.
# Usa "*" para permitir cualquier origen (suficiente para una demo pública).
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
CORS_ORIGINS = os.getenv("CORS_ORIGINS", FRONTEND_URL)

# Conexión a MongoDB. En la nube se inyecta la URI del Mongo gestionado.
MONGO_URI = os.getenv("MONGO_URI", "mongodb://mongo:27017")

# Integración SWH
SWH_API_URL = os.getenv("SWH_API_URL", "http://example.com/swh-api")
SWH_API_USERNAME = os.getenv("SWH_API_USERNAME", "username")
SWH_API_PASSWORD = os.getenv("SWH_API_PASSWORD", "password")

# Intervalo de recopilación de datos en segundos
DATA_COLLECTION_INTERVAL = int(os.getenv("DATA_COLLECTION_INTERVAL", "300"))
