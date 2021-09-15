FROM python:3.6-slim

ENV GUNICORN_WORKERS=1
ENV GUNICORN_TREADS=1
ENV GUNICORN_BIND="0.0.0.0:8000"
ENV GUNICORN_TIMEOUT=400

ENV GOOGLE_OAUTH_CLIENT_ID="id"
ENV GOOGLE_OAUTH_CLIENT_SECRET="45KR4lNuAJL8DtB3GGrvgkBu"
ENV SQLALCHEMY_DATABASE_URI="sqlite:///:memory:"

WORKDIR /home/src/app
COPY . /home/src/app

RUN pip install -r requirements.txt
RUN pip install -e .


CMD gunicorn \
  --workers=$GUNICORN_WORKERS \
  --bind=$GUNICORN_BIND \
  --threads=$GUNICORN_TREADS \
  --timeout=$GUNICORN_TIMEOUT \
  --proxy-protocol \
  --forwarded-allow-ips="10.0.2.100,127.0.0.1" \
  --log-syslog \
  --access-logfile - \
  --error-logfile - \
  --log-level="debug" \
  application:application

