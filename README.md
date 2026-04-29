# ELO

## Requisitos

- Windows 10/11
- Git
- Docker Desktop (recomendado)
- Opcional para execucao local: Python 3.12+ e PostgreSQL 16+

## Instalacao e execucao (Docker)

1) Clone o repositorio
```
git clone <URL_DO_REPO>
cd ELO
```

2) Crie o arquivo `.env` na raiz do projeto
```
DJANGO_SECRET_KEY=uma-chave-forte
DJANGO_DEBUG=True
DB_NAME=elo
DB_USER=elo_user
DB_PASSWORD=senha
DB_HOST=db
DB_PORT=5432
```

3) Suba os containers
```
docker compose up --build
```

4) Rode as migracoes e crie o admin
```
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

5) Acesse o sistema
- http://localhost:8000/

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