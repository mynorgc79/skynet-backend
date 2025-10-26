# syntax=docker/dockerfile:1
FROM python:3.8-alpine
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apk update \
    # psycopg2 dependencies
    && apk add --virtual build-deps gcc python3-dev musl-dev \
    && apk add postgresql-dev \
    # Pillow dependencies
    && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
    # CFFI dependencies
    && apk add libffi-dev py-cffi \
    # Translations dependencies
    && apk add gettext \
    # https://docs.djangoproject.com/en/dev/ref/django-admin/#dbshell
    && apk add postgresql-client
WORKDIR /code
COPY requirements/requirements.txt /code/
RUN python -m pip install -r requirements.txt
COPY . /code/

# ----------------------------------------------------------------------
# PASO FALTANTE Y CRÍTICO: Comando de Ejecución
# ----------------------------------------------------------------------

# 1. EXPONER el puerto. 
# Render usa la variable de entorno $PORT, pero un puerto por defecto como 8000 es común.
EXPOSE 8000

# 2. Comando para iniciar el servidor Gunicorn.
# DEBES reemplazar 'tu_proyecto' con el nombre de tu directorio de Django 
# (el que contiene settings.py y wsgi.py).
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "tu_proyecto.wsgi:application"]