FROM python:3.11.4-slim-buster as base
MAINTAINER Eugene Kovalenko, keugenemail@gmail.com

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_DISABLE_PIP_VERSION_CHECK 1

EXPOSE 8000

RUN pip install --upgrade pip

FROM base AS prod

COPY requirements/prod-requirements.txt /
RUN pip install -r /prod-requirements.txt

WORKDIR /app
COPY . .

#CMD ["gunicorn", "--bind","0.0.0.0:8000", "config.wsgi:application"]

FROM base AS dev

COPY requirements/dev-requirements.txt /
RUN pip install -r /dev-requirements.txt

WORKDIR /app
COPY . .
