@echo off
setlocal enabledelayedexpansion

echo ======================================================================
echo           TIENDA EL REGALITO POS - INICIO DE PRODUCCION
echo ======================================================================
echo.

cd /d "%~dp0"

REM Verificar que Docker este instalado y en ejecucion
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker no esta instalado o Docker Desktop no esta abierto.
    echo Abre Docker Desktop, espera a que diga "Running" y vuelve a intentar.
    pause
    exit /b 1
)

REM Crear .env a partir de .env.example si no existe
if not exist ".env" (
    echo [INFO] Archivo .env no encontrado. Creando a partir de .env.example...
    copy ".env.example" ".env" >nul
    echo [INFO] Archivo .env creado con exito.
)

REM Uso normal: iniciar.bat        (rapido, no reconstruye)
REM Tras cambiar codigo: iniciar.bat build   (reconstruye el backend)
set BUILD=
if /i "%1"=="build" set BUILD=--build

echo [INFO] Levantando contenedores en segundo plano...
echo (Conserva los volumenes y datos de la base de datos)
docker compose -f docker-compose.prod.yml up -d %BUILD%

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Ocurrio un error al levantar los servicios.
    pause
    exit /b 1
)

echo [INFO] Esperando a que el sistema arranque...
timeout /t 15 /nobreak >nul

REM Reiniciar nginx para que reconozca el backend actual (evita el error 502)
docker compose -f docker-compose.prod.yml restart frontend_nginx >nul 2>&1
timeout /t 3 /nobreak >nul

start "" "http://localhost:9090"

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
