# Dockerfile
FROM python:3.11-slim

# Set environment variables to prevent Python from writing .pyc files & Ensure Python output is not buffered
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copia todo o resto da aplicação
COPY . .

# Copia o requirements e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Expõe a porta do Flask
EXPOSE 5000

# Inicia sua aplicação
CMD ["python", "application.py"]
