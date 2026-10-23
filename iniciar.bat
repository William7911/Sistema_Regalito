@echo off
setlocal enabledelayedexpansion

echo ======================================================================
echo           TIENDA EL REGALITO POS - INICIO DE PRODUCCION
echo ======================================================================
echo.

cd /d "%~dp0"

REM Verificar Docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta instalado o no se encuentra en el PATH.
    echo Por favor instala o inicia Docker Desktop y vuelve a intentar.
    pause
    exit /b 1
)

REM Crear .env a partir de .env.example si no existe
if not exist ".env" (
    echo [INFO] Archivo .env no encontrado. Creando a partir de .env.example...
    copy ".env.example" ".env" >nul
    echo [INFO] Archivo .env creado con exito.
)

echo [INFO] Levantando contenedores en segundo plano...
echo (Este comando conserva los volumenes y datos de la base de datos)
docker compose -f docker-compose.prod.yml up -d --build

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Ocurrio un error al levantar los servicios.
    pause
    exit /b 1
)

echo.
echo ======================================================================
echo  Sistema levantado con exito.
echo  Frontend disponible en: http://localhost:9090
echo.
echo  Usuarios semilla:
echo   - Administradora: admin / admin123
echo   - Bodeguero:     bodega / bodega123
echo   - Cajera:        caja / caja123
echo.
echo  ADVERTENCIA: Por seguridad, cambie las contrasenas por defecto
echo  al iniciar sesion en produccion.
echo ======================================================================
pause
