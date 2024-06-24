FROM python:3.9

WORKDIR /app

RUN pip install --no-cache-dir --upgrade pip

# Instala pymongo explícitamente primero
RUN pip install --no-cache-dir pymongo==4.3.3

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]