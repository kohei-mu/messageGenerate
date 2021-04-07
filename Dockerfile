FROM continuumio/anaconda3:latest

RUN apt-get update \
&& apt-get upgrade -y \
&& apt-get install -y vim \
                      sudo \
                      iputils-ping \
                      net-tools \
                      cron \
                      libpq-dev \
		      git \
&& pip install -U pip \
&& pip install fastapi  \
               uvicorn \
               jinja2 \
               python-multipart \
               aiofiles
WORKDIR /projects

