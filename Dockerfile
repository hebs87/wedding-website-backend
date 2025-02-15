# syntax=docker/dockerfile:1
FROM python:3.13
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y cron
RUN apt-get upgrade -y

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY ./ /code/

# Collect statics
RUN mkdir -p /var/log/project
RUN touch /var/log/project/django.log
RUN SECRET_KEY=itdoesntreallymatter LOG_PATH=/var/log/project/django.log
