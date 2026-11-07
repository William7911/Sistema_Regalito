# Tienda El Regalito — Sistema POS y Gestión de Inventarios

Sistema integral de Punto de Venta (POS), control de inventarios, compras, caja, facturación y reportes para **Tienda el Regalito** (Guatemala).

---

## Requisitos Previos

- [Docker](https://docs.docker.com/get-docker/) y Docker Compose (incluidos con Docker Desktop en Windows/Mac o Docker Engine en Linux).
- Git.

---

## Despliegue con un Solo Comando

### 1. Clonar el repositorio
```bash
git clone <URL_DEL_REPOSITORIO>
cd Sistema_Regalito/Sistema_Regalito
```

### 2. Configurar variables de entorno (opcional)
Si no existe el archivo `.env`, se puede copiar la plantilla de ejemplo:
```bash
cp .env.example .env
```
*(En Windows también se genera automáticamente al ejecutar `iniciar.bat`)*.

### 3. Iniciar el sistema
Puede utilizar el archivo por lotes en Windows:
```cmd
iniciar.bat
```
O directamente con Docker Compose:
```bash
docker compose -f docker-compose.prod.yml up -d --build
```

El sistema realiza automáticamente y de forma segura:
1. Inicialización de la base de datos PostgreSQL con todas las tablas y datos geográficos/semilla mediante `database/init.sql`.
2. Verificación de salud del contenedor de base de datos (`healthcheck`).
3. Sincronización automática de versiones de Alembic (`alembic stamp/upgrade head`) al arrancar el backend.
4. Despliegue del servidor backend FastAPI (4 workers) y frontend estático servido a través de Nginx.

### 4. Acceder al sistema
Abra su navegador web en:
**[http://localhost:9090](http://localhost:9090)**

## Comandos Útiles

- **Ver estado de los servicios:**
  ```bash
  docker compose -f docker-compose.prod.yml ps
  ```
- **Ver logs en tiempo real:**
  ```bash
  docker compose -f docker-compose.prod.yml logs -f
  ```
- **Detener los servicios sin perder datos:**
  ```bash
  docker compose -f docker-compose.prod.yml stop
  ```
