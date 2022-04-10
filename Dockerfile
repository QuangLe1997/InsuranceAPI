FROM python:3.9-slim as app

COPY requirements.txt .

RUN apt-get update && apt-get -y install libgl1-mesa-glx libgtk2.0-dev && python -m pip install --upgrade pip && python -m pip install -r requirements.txt

WORKDIR /usr/local/app
COPY . /usr/local/app

ENTRYPOINT python main.py
