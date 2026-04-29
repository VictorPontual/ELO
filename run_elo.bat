@echo off
setlocal

cd /d "%~dp0"

echo Subindo containers...
docker compose up -d

if errorlevel 1 (
  echo Erro ao subir os containers.
  exit /b 1
)

echo Aplicando migracoes...
docker compose exec web python manage.py migrate

if errorlevel 1 (
  echo Erro ao aplicar migracoes.
  exit /b 1
)

echo Abrindo no navegador...
start "" "http://localhost:8000/"

echo Pronto. Para parar: docker compose down
