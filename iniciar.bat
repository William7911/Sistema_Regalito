@echo off
echo =========================================
echo    Iniciando Sistema Regalito POS...
echo =========================================
echo.

echo [1/2] Levantando Base de Datos en Docker...
docker-compose up -d db
echo.

echo [2/2] Levantando Servidor Backend (FastAPI)...
cd backend
python -m uvicorn app.main:app --reload --port 8000

pause
