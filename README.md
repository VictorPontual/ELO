# ELO

## Requisitos

- Docker Desktop (Windows/Linux/macOS)
- Git
- Opcional para desenvolvimento sem Docker: Python 3.12+ e PostgreSQL 16+

## Hospedagem local (Docker)

O `docker-compose.yml` sobe o app (gunicorn) e um Postgres em container,
servindo por HTTP na rede interna. As migracoes e o `collectstatic` rodam
automaticamente no start.

1) Clone o repositorio
```
git clone <URL_DO_REPO>
cd ELO
```

2) Crie o arquivo `.env` na raiz do projeto
```
DJANGO_SECRET_KEY=uma-chave-forte
DJANGO_DEBUG=False
# Inclua o IP/hostname do servidor (ex.: localhost,127.0.0.1,192.168.0.10):
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DJANGO_CSRF_TRUSTED_ORIGINS=
DJANGO_SECURE_SSL=False

DB_NAME=elo
DB_USER=postgres
DB_PASSWORD=uma-senha-forte
DB_HOST=db
DB_PORT=5432

EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=senha-de-app
EMAIL_USE_TLS=True
DEFAULT_FROM_EMAIL=seu-email@gmail.com
```

3) Suba os containers
```
docker compose up -d --build
```

4) Crie o admin (primeira vez)
```
docker compose exec web python manage.py createsuperuser
```

5) Acesse pela rede
- `http://IP-DO-SERVIDOR:8000/` (ou http://localhost:8000/ na propria maquina)

### Observacoes

- **HTTPS (opcional):** atras de um proxy reverso (Nginx/Traefik), defina no
  `.env` `DJANGO_SECURE_SSL=True` e `DJANGO_CSRF_TRUSTED_ORIGINS=https://seu-dominio`.
- **Avisos periodicos:** agende no host (cron no Linux ou Agendador de Tarefas no
  Windows) o comando:
  ```
  docker compose exec -T web python manage.py enviar_avisos
  ```
- **Atualizar apos mudancas no codigo:**
  ```
  docker compose up -d --build
  ```
- **Erro "password authentication failed"** ao subir pela primeira vez apos ter
  usado outra senha: o volume do Postgres foi criado com a senha antiga. Resete
  (apaga o banco):
  ```
  docker compose down -v
  docker compose up -d --build
  ```

## Instalacao e execucao (local sem Docker)

1) Clone o repositorio
```
git clone <URL_DO_REPO>
cd ELO
```

2) Crie e ative a venv
```
python -m venv .venv
.
venv\Scripts\Activate.ps1
```

3) Instale dependencias
```
pip install -r requirements.txt
```

4) Configure o `.env`
```
DJANGO_SECRET_KEY=uma-chave-forte
DJANGO_DEBUG=True
DB_NAME=elo
DB_USER=elo_user
DB_PASSWORD=senha
DB_HOST=localhost
DB_PORT=5432
```

5) Rode migracoes e suba o servidor
```
cd elo
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

6) Acesse
- http://127.0.0.1:8000/