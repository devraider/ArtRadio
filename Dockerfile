# Use the official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.9-alpine

# Allow statements and log messages to immediately appear in the Knative logs
ENV PYTHONUNBUFFERED True

# Copy local code to the container image.
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

# Install production dependencies.

RUN \
  apk add --no-cache postgresql-libs && \
  apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
  python3 -m pip install -r requirements.txt --no-cache-dir && \
  apk --purge del .build-deps
RUN python manage.py migrate
RUN python manage.py collectstatic --no-input

CMD gunicorn artradio.wsgi:application --bind :$PORT --workers 1 --threads 8 --timeout 0