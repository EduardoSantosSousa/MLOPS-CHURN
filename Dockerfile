FROM quay.io/astronomer/astro-runtime:12.6.0

# Instale ferramentas do sistema necessárias para compilar pacotes Python (como pandas)
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libffi-dev \
    libpq-dev \
    python3-dev \
    curl \
    && apt-get clean

# Volte para o usuário airflow (padrão da imagem)
USER astro

# Instale as dependências Python
RUN pip install apache-airflow-providers-google
