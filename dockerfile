# Usar una imagen base de Python 3.11
FROM python:3.11

# Actualizar el sistema e instalar dependencias necesarias
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Crear un directorio de trabajo en el contenedor
WORKDIR /app

# Copiar el archivo requirements.txt para instalar dependencias
COPY requirements.txt /app/

# Instalar las dependencias de Python desde requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Ultralytics directamente con pip
RUN pip install --no-cache-dir ultralytics

# Copiar el resto de los archivos del proyecto
COPY . /app/

# Exponer el puerto que va a usar la aplicación
EXPOSE 8000

# Ejecutar los archivos estáticos (si tienes archivos estáticos)
RUN python manage.py collectstatic --noinput

# Comando para ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "proydjango.wsgi:application", "--bind", "0.0.0.0:8000"]
