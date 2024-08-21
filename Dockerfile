FROM python:3.11.0

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1
# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Configurar el directorio de trabajo en el contenedor
WORKDIR /app

# Instalar dependencias de sistema necesarias para psycopg2-binary
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    gcc \
    postgresql \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip
# Instala Cython
RUN pip install --no-cache-dir cython


# Copiar requirements.txt e instalar dependencias
COPY requirements.txt /app/
RUN pip3 install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación al contenedor
COPY . /app/

# Variable de entorno para apuntar a dev.py
ENV DJANGO_SETTINGS_MODULE=scraper.settings.dev

# Expone el puerto en el que la aplicación estará escuchando
EXPOSE 8000

# Configura el entrypoint para ejecutar el script de inicio
#ENTRYPOINT ["/app/entrypoint.sh"]

# Especificar el comando para ejecutar la aplicación con Gunicorn
CMD ["sh", "-c", "gunicorn scraper.wsgi:application --bind 0.0.0.0:8000"]