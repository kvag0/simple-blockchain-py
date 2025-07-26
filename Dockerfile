FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt ./
RUN python3 -m pip install -r requirements.txt
COPY . .
# O CMD será executado pelo docker-compose