# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Set environment variables to prevent Python from writing .pyc files & Ensure Python output is not buffered
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH="/app"

# Antes do COPY . .
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*
 

# Copia todo o resto da aplicação
COPY . .

# Install the package in editable mode
RUN pip install --no-cache-dir -e .

# Expõe a porta do Flask
EXPOSE 5000

# Inicia sua aplicação
CMD ["python", "application.py"]
