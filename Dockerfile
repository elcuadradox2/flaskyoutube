# Usa una imagen base de Python
FROM python:3.11-slim

# Instala ffmpeg y otras dependencias necesarias
RUN apt-get update && apt-get install -y ffmpeg

# Configura el directorio de trabajo
WORKDIR /app

# Copia el contenido del proyecto a la imagen
COPY . /app

# Instala las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto de la aplicación
EXPOSE 5000

# Comando de inicio
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
