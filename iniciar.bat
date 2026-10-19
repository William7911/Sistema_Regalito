@echo off
echo =========================================
echo    Iniciando Sistema Regalito (Produccion)
echo =========================================
echo.

echo [1/2] Entrando a la carpeta...
cd /d "C:\Users\abima\OneDrive\Desktop\Sistema_Regalito\Sistema_Regalito"

echo [2/2] Levantando contenedores...
docker compose -f docker-compose.prod.yml up -d

echo.
echo Esperando arranque...
timeout /t 5 /nobreak > NUL

echo.
echo Abriendo navegador...
start "" "http://localhost:9090"

echo.
pause