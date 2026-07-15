FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências de sistema do python-ldap (usado pela integração LDAP).
# libldap2-dev/libsasl2-dev/gcc são necessárias para compilar; libldap-common
# e libsasl2-2 são o runtime. Sem elas o pip install falha no container slim.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc libldap2-dev libsasl2-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN python -m pip install --no-cache-dir -r requirements.txt

COPY . ./
