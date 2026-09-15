# Tienda el Regalito POS — Documentación General

## 1. Arquitectura

Aplicación web **POS (Punto de Venta)** con arquitectura de **backend por capas** y **frontend estático** servido por el propio backend.

```
Sistema_Regalito/
├── backend/                 # API REST (FastAPI, Python)
│   └── app/
│       ├── main.py          # Punto de entrada + handlers de error globales
│       ├── api/             # CAPA CONTROLLERS (routers FastAPI, delgados, sin try/except)
│       │   ├── auth.py          # Login (JWT)
│       │   ├── cash_register.py # Apertura/cierre de caja
│       │   ├── categories.py    # CRUD Categorías
│       │   ├── products.py      # CRUD + filtros Productos
│       │   ├── roles.py         # CRUD Roles
│       │   ├── departments.py   # CRUD Departamentos
│       │   ├── users.py         # CRUD + filtros Usuarios
│       │   └── deps.py          # DI + patrón Unit of Work (UoW)
│       ├── services/        # CAPA SERVICIOS (lógica de negocio)
│       │   ├── category_service.py
│       │   ├── product_service.py
│       │   ├── role_service.py
│       │   ├── department_service.py
│       │   └── user_service.py
│       ├── repositories/    # CAPA REPOSITORIOS (acceso a datos async)
│       │   ├── category_repository.py
│       │   ├── product_repository.py
│       │   ├── role_repository.py
│       │   ├── department_repository.py
│       │   └── user_repository.py
│       ├── interfaces/      # CAPA CONTRATOS (ABC: repositorios y servicios)
│       │   ├── repositories.py
│       │   └── services.py
│       ├── db/              # CAPA MODELOS/ENTIDADES + configuración BD
│       │   ├── database.py  # Motor async + get_db (DI)
│       │   └── models.py    # Entidades SQLAlchemy
│       ├── schemas/         # CAPA DTOs (Pydantic v2)
│       │   └── schemas.py
│       └── core/            # Configuración y seguridad
│           ├── config.py
│           └── security.py
│   ├── alembic/             # Migraciones versionadas (Alembic)
│   └── tests/               # Pruebas unitarias (pytest + aiosqlite)
├── database/init.sql        # Esquema y datos iniciales (PostgreSQL, solo volumen nuevo)
├── frontend/                # HTML/CSS/JS estáticos (incluye módulo Usuarios)
└── documentacion/           # Documentación del proyecto
```

## 2. Tecnologías detectadas

| Capa | Tecnología |
|------|-----------|
| Lenguaje | Python 3.13 |
| Framework backend | FastAPI + Uvicorn |
| Base de datos | PostgreSQL 15 (Docker, puerto 5433) |
| ORM | SQLAlchemy 2.x (asíncrono, `asyncpg`) |
| Migraciones | Alembic |
| Validación / DTOs | Pydantic v2 (`ConfigDict`, `from_attributes`) |
| Autenticación | JWT (`python-jose`) + OAuth2 + `passlib`/`bcrypt` (fijar `bcrypt==4.0.1`) |
| Configuración | `pydantic-settings` |
| Pruebas | `pytest` + `pytest-asyncio` + `aiosqlite` |

## 3. Arquitectura por capas (reglas)

- **Controllers (`app/api/`)**: solo reciben la petición, llaman a la interfaz del servicio y devuelven JSON con el código HTTP correcto (200, 201, 400, 404, 500). **Cero lógica y cero try/except**.
- **Services (`app/services/`)**: contienen todas las validaciones y reglas de negocio.
- **Repositories (`app/repositories/`)**: único punto de acceso a datos. Acceso asíncrono (`async/await`). Uso de SQLAlchemy `select()` (seguro contra inyección SQL, sin string concatenado).
- **Interfaces (`app/interfaces/`)**: contratos `ABC` de servicios y repositorios.
- **DTOs (`app/schemas/`)**: los modelos de BD nunca se exponen directamente al cliente.
- **Inyección de dependencias + Unit of Work (UoW)**: en `app/api/deps.py`. El `UnitOfWork` agrupa la transacción y expone los repositorios del módulo de Usuarios. Los repositorios de Roles/Departamentos/Usuarios NO hacen commit: el UoW decide `commit()`/`rollback()`.
- **Manejo de errores global**: handlers de `HTTPException` y `Exception` (500) registrados en `main.py`. Los controladores no manejan errores.

## 4. Reglas de negocio

- **Cero datos quemados**: los dropdowns de Rol y Departamento se llenan desde la BD. Al crear/editar un usuario, el rol y el departamento se validan contra la base de datos (deben existir y estar activos).
- **Eliminación lógica (Soft Delete)**: no se ejecuta `DELETE`. Se usa el campo booleano `is_active` (`true`/`false`) en todas las entidades.
- **Filtros inteligentes**:
  - Productos (`GET /api/productos`): `name`, `sku`, `barcode`, `is_active`, `category_id`, `created_from`, `created_to`, `limit`, `offset`.
  - Usuarios (`GET /api/usuarios`): `name`, `lastname`, `code`, `is_active`, `role_id`, `department_id`, `created_from`, `created_to`, `limit`, `offset`.
- **Unicidad**: `name` de categorías/roles/departamentos; `sku` y `barcode` de productos; `code`, `username` de usuarios.

### Frontend — Módulo de Usuarios (estándar empresarial)
El formulario se muestra en un **modal de Bootstrap** (`#user-modal`). `frontend/js/users.js` implementa:
- **Validación visual inline**: los errores **422** se muestran debajo de cada campo (`.invalid-feedback`) con traducción al español (`translateValidation`); los **400** y errores generales en `#user-form-alert`.
- **Errores 422**: `renderFieldErrors()` recorre `errorData.detail`, extrae el campo con `err.loc[err.loc.length - 1]`, agrega `is-invalid` y coloca `err.msg` traducido en su `.invalid-feedback`.
- **Notificaciones Toast** (`showToast`): reemplazan todo `alert()` de éxito/error; **confirmación no nativa** (`confirmModal`) reemplaza `confirm()`.
- **Micro-interacciones**: limpieza de errores en tiempo real (`input`/`change`), envío con **Enter**, autofocus en el primer campo y **reseteo impecable** al cerrar el modal (`hidden.bs.modal` → `resetUserForm()`).
- **Defensivo**: `.trim()` en campos de texto y **bloqueo del botón Guardar** con spinner (`setSaving`) para evitar dobles clics.
- **Estado vacío**: `#users-empty` muestra "No hay usuarios registrados" cuando la tabla está vacía.
- IDs de los campos alineados a Pydantic (`name`, `lastname`, `code`, `username`, `password`, `role_id`, `department_id`, `is_active`); `role_id`/`department_id` se envían como enteros (`parseInt(..., 10)`); en edición se excluye `password` si va vacío.

## 5. Base de datos

### Conexión
Definida en `app/core/config.py` (variable `DATABASE_URL`, con `.env`). Por defecto:

```
postgresql://regalito_admin:Regalito_2026@localhost:5433/regalito_pos
```

`app/db/database.py` convierte la URL a `postgresql+asyncpg://` y crea el motor asíncrono.

### Levantar la base de datos (Docker)
```bash
docker-compose up -d db
```

### `init.sql` (solo volumen nuevo)
Solo se ejecuta la primera vez que el volumen se crea. Contiene el esquema completo (incluye `roles`, `departments`, `users` normalizado, `categories`, `products`, `cash_registers`) y datos semilla.

### Migraciones con Alembic (entornos con datos existentes)
El esquema actualizado del Módulo de Usuarios se aplica de forma **aditiva** (preserva datos) con la migración `0001`:

```bash
# desde backend/
alembic upgrade head
```

> Si ya tenías un volumen con datos y no quieres migrar, puedes recrearlo: `docker-compose down -v && docker-compose up -d db` (pierde los datos).

## 6. Ejecución del backend

```bash
pip install -r backend/requirements.txt
uvicorn app.main:app --reload --port 8000   # desde backend/
```

Swagger/OpenAPI disponible en `http://localhost:8000/docs`.

## 7. Pruebas

```bash
# desde backend/
python -m pytest -q
```

Las pruebas usan SQLite en memoria (`aiosqlite`), no requieren PostgreSQL. Cubren la capa de servicios (Categorías, Productos, Roles, Departamentos, Usuarios).

## 8. Endpoints principales

| Método | Ruta | Descripción |
|--------|------|-------------|
| POST | `/api/auth/login` | Autenticación (token JWT) |
| GET/POST | `/api/categorias` | Listar / crear categorías |
| GET/PUT/DELETE | `/api/categorias/{id}` | Obtener / editar / desactivar categoría |
| GET/POST | `/api/productos` | Listar (con filtros) / crear producto |
| GET/PUT/DELETE | `/api/productos/{id}` | Obtener / editar / desactivar producto |
| GET | `/api/productos/barcode/{barcode}` | Buscar producto por código de barras |
| GET/POST | `/api/roles` | Listar / crear roles |
| GET/PUT/DELETE | `/api/roles/{id}` | Obtener / editar / desactivar rol |
| GET/POST | `/api/departamentos` | Listar / crear departamentos |
| GET/PUT/DELETE | `/api/departamentos/{id}` | Obtener / editar / desactivar departamento |
| GET/POST | `/api/usuarios` | Listar (con filtros) / crear usuario |
| GET/PUT/DELETE | `/api/usuarios/{id}` | Obtener / editar / desactivar usuario |
| POST | `/api/caja/apertura` | Abrir caja |
| POST | `/api/caja/cierre-ciegas` | Cerrar caja |