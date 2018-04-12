FROM python:3.6
ENV PYTHONUNBUFFERED 1
RUN mkdir /src
WORKDIR /src
RUN pip install virtualenv
RUN apt-get update
RUN apt-get -y install procmail