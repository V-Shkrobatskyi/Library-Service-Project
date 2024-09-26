FROM python:3.12.4-slim
LABEL maintainer="vetali5700@gmail.com"

ENV PYTHOUNNBUFFERED 1

WORKDIR app/

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
RUN mkdir -p /app/media/uploads

RUN adduser \
    --disabled-password \
    --no-create-home \
    django_user

USER django_user
