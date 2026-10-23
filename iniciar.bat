@echo off
setlocal

echo =========================================
echo    Iniciando Sistema Regalito (Produccion)
echo =========================================
echo.

echo [1/5] Entrando a la carpeta...
cd /d "C:\Users\abima\OneDrive\Desktop\Sistema_Regalito\Sistema_Regalito"

echo [2/5] Levantando la base de datos...
docker compose -f docker-compose.prod.yml up -d db
timeout /t 10 /nobreak > NUL

echo [3/5] Respaldo de la base de datos...
if not exist respaldos mkdir respaldos
for /f %%d in ('powershell -command "Get-Date -Format yyyyMMdd_HHmm"') do set FECHA=%%d
docker exec regalito_db_prod pg_dump -U regalito_admin regalito_pos > respaldos\respaldo_%FECHA%.sql

echo [4/5] Reconstruyendo y levantando todo...
docker compose -f docker-compose.prod.yml up -d --build
timeout /t 10 /nobreak > NUL

echo [5/5] Aplicando migraciones...
docker exec regalito_backend_prod alembic upgrade head

start "" "http://localhost:9090"
echo.
echo Listo. Usuario: admin
pause