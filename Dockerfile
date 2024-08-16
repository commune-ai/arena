# THE GENERAL CONTAINER FOR CONNECTING ALL THE ENVIRONMENTS 😈
FROM ubuntu:22.04
FROM python:3.12.3-bullseye


ENV PWD /app

#SYSTEM
ARG DEBIAN_FRONTEND=noninteractive
RUN usermod -s /bin/bash root
RUN apt-get update 

#RUST
RUN apt-get install curl nano build-essential cargo libstd-rust-dev -y

#JS 
RUN apt-get install -y nodejs npm
RUN npm install -g pm2 
WORKDIR /app
# COPY THE SCRIPTS
COPY ./scripts /app/scripts
RUN chmod +x /app/scripts/install.sh
# THIS IS FOR THE LOCAL PACKAG
COPY ./ /app
# git install commune
RUN ./scripts/install.sh
RUN  pip install -e ./ --break-system-packages
# IMPORT EVERYTHING ELSE
ENTRYPOINT [ "tail", "-f", "/dev/null"]