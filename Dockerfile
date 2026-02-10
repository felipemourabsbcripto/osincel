FROM ubuntu:22.04

# Evita prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependências necessárias
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    jq \
    python3 \
    python3-pip \
    net-tools \
    dnsutils \
    whois \
    nmap \
    git \
    && rm -rf /var/lib/apt/lists/*

# Cria diretório da aplicação
WORKDIR /app

# Copia os arquivos do projeto
COPY . /app/

# Torna o script executável
RUN chmod +x /app/start.sh

# Porta exposta (se necessário para web)
EXPOSE 8080

# Comando padrão
CMD ["/bin/bash", "/app/start.sh"]
