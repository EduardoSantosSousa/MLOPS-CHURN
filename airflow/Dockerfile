FROM quay.io/astronomer/astro-runtime:12.6.0

# Install system tools needed to compile Python packages (such as pandas)
USER root
RUN apt-get update && apt-get install -y \
    build-essential \
    gcc \
    libffi-dev \
    libpq-dev \
    python3-dev \
    curl \
    && apt-get clean

# Switch back to airflow user (default image)
USER astro

# Install Python dependencies
RUN pip install apache-airflow-providers-google
