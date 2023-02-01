FROM python:3.10
RUN apt-get update -y
RUN apt-get upgrade -y

RUN pip install --upgrade pip


WORKDIR /mono_card_balance

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt ./
RUN pip install -r requirements.txt


COPY . .
