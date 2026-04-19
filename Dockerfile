FROM python:3.12-slim

# Dependencias de sistema para matplotlib y kaleido
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/

# Los imports de Flask usan rutas planas (from config import ...)
# PYTHONPATH apunta a app/ para que sigan funcionando sin cambios
ENV PYTHONPATH=/app/app

EXPOSE 5000

CMD ["python", "-m", "flask", "--app", "api", "run", "--host", "0.0.0.0", "--port", "5000"]
