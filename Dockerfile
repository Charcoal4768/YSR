FROM python:3.13-slim

WORKDIR /YSR

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app", "--worker-class", "eventlet", "--workers", "4"]