FROM python:3.13-slim

# Evitar la creación de archivos .pyc y forzar logs sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production

# Crear y establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para compilar paquetes si es requerido
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copiar el archivo de requerimientos e instalar dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código fuente del backend
COPY . .

# Exponer el puerto donde corre la API
EXPOSE 8000

# Comando para iniciar la aplicación en modo producción (con 4 workers y sin reload)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
