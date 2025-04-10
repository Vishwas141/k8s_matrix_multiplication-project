# Dockerfile.app
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY custom_app.py .

CMD ["python", "custom_app.py"]
