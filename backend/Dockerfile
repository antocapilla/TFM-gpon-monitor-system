FROM python:3.9

# Instalar dependencias del sistema necesarias para Pygame y otras bibliotecas
RUN apt-get update && apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libfreetype6-dev \
    libportmidi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
# Crear el directorio para las uploads
RUN mkdir -p uploads

# Asegurarse de que el directorio tenga los permisos correctos
RUN chmod 777 uploads

# Usa el puerto que asigne la plataforma ($PORT) o 8000 en local.
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]