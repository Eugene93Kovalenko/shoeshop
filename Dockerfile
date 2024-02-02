FROM python:3.11.4-slim-buster
MAINTAINER Eugene Kovalenko, keugenemail@gmail.com

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

WORKDIR /app

RUN pip install --upgrade pip
COPY requirements.txt /app/requirements.txt
RUN pip install -r requirements.txt

COPY shoeshop_project /app

EXPOSE 8000