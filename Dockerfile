# THE GENERAL CONTAINER FOR CONNECTING ALL THE ENVIRONMENTS 😈
FROM ubuntu:22.04
FROM python:3.12.3-bullseye

#SYSTEM
ARG DEBIAN_FRONTEND=noninteractive
RUN usermod -s /bin/bash root
RUN apt-get update 

#RUST
RUN apt-get install curl nano build-essential cargo libstd-rust-dev -y

#JS 
RUN apt-get install -y nodejs npm
RUN npm install -g pm2 
ENV PWD /app
WORKDIR /app

# WANT TO HAVE TO REBUILD THE WHOLE IMAGE EVERY TIME WE CHANGE THE REQUIREMENTS
COPY ./requirements.txt /app/requirements.txt
COPY ./setup.py /app/setup.py
COPY ./README.md /app/README.md

# git install commune
RUN git clone https://github.com/commune-ai/commune.git /app/commune
RUN pip install -e ./commune

RUN pip install -e ./ 
# THIS IS FOR THE LOCAL PACKAG
COPY ./ /app
# IMPORT EVERYTHING ELSE
ENTRYPOINT [ "tail", "-f", "/dev/null"]