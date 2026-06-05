FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY analytics ./analytics
COPY batch_processing ./batch_processing
COPY config ./config
COPY deployment ./deployment
COPY docs ./docs
COPY storage ./storage
COPY visualization ./visualization
COPY README.md .

EXPOSE 8080

CMD ["python", "visualization/flask_app.py"]
