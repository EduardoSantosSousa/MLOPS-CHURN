# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copia o requirements e instala
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o resto da aplicação
COPY . .

# Expõe a porta do Flask
EXPOSE 5000

# Inicia sua aplicação
CMD ["python", "application.py"]
