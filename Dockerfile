# Usa la imagen base de Python
FROM python:3.11.0

# Configuraciones de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configurar el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias de sistema necesarias
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    postgresql \
    libpq-dev \
    wget \
    curl \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Instala Cython y actualiza pip
RUN pip install --upgrade pip
RUN pip install --no-cache-dir cython

# Copiar requirements.txt e instalar dependencias de Python
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación al contenedor
COPY . /app/

# Variable de entorno para apuntar a dev.py
ENV DJANGO_SETTINGS_MODULE=scraper.settings.dev

# Expone el puerto en el que la aplicación estará escuchando
EXPOSE 8000

# Comando de inicio de Gunicorn
CMD ["sh", "-c", "gunicorn scraper.wsgi:application --bind 0.0.0.0:8000"]