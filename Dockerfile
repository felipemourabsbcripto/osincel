FROM python:3.11-slim

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    jq \
    net-tools \
    dnsutils \
    whois \
    nmap \
    && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia arquivos do projeto
COPY . /app/

# Instala dependências Python
RUN pip install --no-cache-dir flask gunicorn

# Expondo porta
EXPOSE 8080

# Comando para iniciar a API
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "app:app"]
