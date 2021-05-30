FROM python:3.7.10-slim

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY ./src /app/src

WORKDIR /app

ENTRYPOINT ["python", "src/main.py", "--data", "mnt/data", "--configuration", "mnt/configuration/configuration.json", "--logs", "mnt/logs/main.log"]