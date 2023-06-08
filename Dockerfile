# syntax=docker/dockerfile:1
FROM python:3

ENV PYTHONUNBUFFERED=1

WORKDIR /code

SHELL ["/bin/bash", "--login", "-c"]

RUN apt-get update

ENV NODE_VERSION=14.17.3
RUN curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.34.0/install.sh | bash
RUN nvm install $NODE_VERSION
RUN nvm alias default $NODE_VERSION
RUN nvm use default
RUN npm install -g yarn

COPY requirements.txt /code/

RUN pip install -r requirements.txt

COPY . /code/

# RUN python manage.py collectstatic --no-input
# RUN python manage.py migrate
# COPY . /code/

