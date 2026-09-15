# Registro de Cambios

## Regla de documentación (obligatoria)
Cualquier cambio futuro en el proyecto debe quedar documentado en esta carpeta `/documentacion`. Agrega una entrada en este archivo (`cambios.md`) cada vez que modifiques, crees o elimines componentes.

---

## [2026-09-14] Avance: Módulo de Usuarios (Roles, Departamentos, Usuarios)

### Contexto
Se desarrolló el módulo de **Usuarios**: mantenimiento (CRUD) de **Roles** y **Departamentos**, CRUD de **Usuarios** con eliminación lógica y filtros inteligentes. Se incorporó el patrón **Unit of Work**, **handlers de error globales** y **migraciones Alembic**.

### Componentes creados
| Archivo | Capa | Descripción |
|---------|------|-------------|
| `backend/app/repositories/role_repository.py` | Repositorio | Acceso a datos async de Roles (flush-only) |
| `backend/app/repositories/department_repository.py` | Repositorio | Acceso a datos async de Departamentos (flush-only) |
| `backend/app/repositories/user_repository.py` | Repositorio | Acceso a datos async de Usuarios (filtros + `selectinload`) |
| `backend/app/services/role_service.py` | Servicio | Lógica de negocio de Roles (usa UoW) |
| `backend/app/services/department_service.py` | Servicio | Lógica de negocio de Departamentos (usa UoW) |
| `backend/app/services/user_service.py` | Servicio | Lógica de negocio de Usuarios (valida rol/depto en BD, hashea password) |
| `backend/app/api/roles.py` | Controller | CRUD de Roles |
| `backend/app/api/departments.py` | Controller | CRUD de Departamentos |
| `backend/app/api/users.py` | Controller | CRUD de Usuarios + filtros |
| `backend/alembic.ini`, `alembic/env.py`, `alembic/script.py.mako` | Migraciones | Configuración de Alembic async |
| `backend/alembic/versions/0001_*.py` | Migraciones | Migración aditiva (roles, departments, normaliza users) |
| `backend/tests/test_role_service.py` | Pruebas | Tests de servicios de Roles |
| `backend/tests/test_department_service.py` | Pruebas | Tests de servicios de Departamentos |
| `backend/tests/test_user_service.py` | Pruebas | Tests de servicios de Usuarios |
| `frontend/js/users.js` | Frontend | JS que consume Roles/Departamentos y gestiona Usuarios |

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `backend/app/db/models.py` | Nuevas entidades `Role` y `Department`; `User` normalizado (name, lastname, code, role_id, department_id; se quita `role` texto) |
| `backend/app/schemas/schemas.py` | DTOs de `Role`, `Department`, `UserCreate/Update/Response/Filter/List` |
| `backend/app/interfaces/repositories.py` | ABC de `RoleRepository`, `DepartmentRepository`, `UserRepository` |
| `backend/app/interfaces/services.py` | ABC de `RoleService`, `DepartmentService`, `UserService` |
| `backend/app/api/deps.py` | Clase `UnitOfWork` + `get_role_service`, `get_department_service`, `get_user_service` |
| `backend/app/api/auth.py` | Login carga `role` con `selectinload` para el token |
| `backend/app/main.py` | Routers de roles/departamentos/usuarios + handlers de error globales |
| `backend/requirements.txt` | Se agregó `alembic` y se fijó `bcrypt==4.0.1` (compatibilidad con passlib) |
| `backend/tests/conftest.py` | Fixture `uow` de prueba |
| `database/init.sql` | Esquema con `roles`, `departments`, `users` normalizado + seeds |
| `frontend/index.html` | Vista del módulo Usuarios (formulario + tabla + filtros) y enlace del sidebar |
| `documentacion/general.md`, `cambios.md`, `agents.md` | Actualizados |

### Reglas de negocio implementadas
- Rol y Departamento validados contra la BD (existen y están activos) al crear/editar usuario.
- Eliminación lógica (soft delete) vía `is_active` en Roles, Departamentos y Usuarios.
- Filtros de usuarios por `name`, `lastname`, `code`, `is_active`, `role_id`, `department_id` y rangos de fecha.
- Unicidad de `name` (roles/departamentos) y `code`/`username` (usuarios).
- Contraseña siempre almacenada como hash (`bcrypt`); nunca se expone en respuestas.

### Patrones incorporados
- **Unit of Work** en `deps.py`: agrupa la transacción; repositorios del módulo no hacen commit.
- **Exception Handler global** en `main.py` (HTTPException y Exception → 500). Controladores sin try/except.
- **Alembic**: migración `0001` aditiva que crea `roles`/`departments`, agrega columnas a `users` y hace backfill sin borrar datos.

### Verificación
- `python -m pytest -q` desde `backend/`: **29 pruebas pasan**.

### Pendiente / notas
- Para entornos con datos existentes ejecutar `alembic upgrade head` (desde `backend/`). Para entorno nuevo basta `docker-compose up -d db` (usa `init.sql`).
- `bcrypt` debe quedar en `4.0.1` (versiones 5.x rompen `passlib`).
- El frontend usa el token JWT guardado en `localStorage['jwt_token']`; el login carga el rol desde la relación `User.role`.

---

## [2026-09-14] Avance: Módulo de Productos y Categorías + Migración a async

### Contexto
Se desarrolló el módulo de **Productos** y el mantenimiento de **Categorías**, y se migró el acceso a datos de SQLAlchemy síncrono a **asíncrono (async/await)** para todo el backend.

### Componentes creados
| Archivo | Capa | Descripción |
|---------|------|-------------|
| `backend/app/interfaces/repositories.py` | Contratos | ABC de repositorios de `Category` y `Product` |
| `backend/app/interfaces/services.py` | Contratos | ABC de servicios de `Category` y `Product` |
| `backend/app/repositories/category_repository.py` | Repositorio | Acceso a datos async de Categorías |
| `backend/app/repositories/product_repository.py` | Repositorio | Acceso a datos async de Productos (filtros inteligentes) |
| `backend/app/services/category_service.py` | Servicio | Lógica de negocio de Categorías |
| `backend/app/services/product_service.py` | Servicio | Lógica de negocio de Productos |
| `backend/app/api/categories.py` | Controller | CRUD de Categorías (endpoints) |
| `backend/app/api/products.py` | Controller | CRUD de Productos + filtros |
| `backend/app/api/deps.py` | DI | Inyección de dependencias + `get_current_user` |
| `backend/tests/conftest.py` | Pruebas | Fixture de BD async en memoria |
| `backend/tests/test_category_service.py` | Pruebas | Tests de servicios de Categorías |
| `backend/tests/test_product_service.py` | Pruebas | Tests de servicios de Productos |
| `backend/pytest.ini` | Config | Configuración de pytest (modo async) |
| `documentacion/general.md` | Docs | Arquitectura y configuración |
| `documentacion/cambios.md` | Docs | Este registro |
| `agents.md` | Docs | Instrucciones para agentes/IA |

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `backend/requirements.txt` | Se agregaron `asyncpg`, `pytest`, `pytest-asyncio`, `aiosqlite`, `httpx` |
| `backend/app/db/database.py` | Motor asíncrono (`create_async_engine`) + `get_db` async |
| `backend/app/db/models.py` | Nueva entidad `Category`; `Product` gana `sku` y `category_id` (FK) |
| `backend/app/schemas/schemas.py` | DTOs de `Category`, `Product`, `ProductFilter`, `ProductList` |
| `backend/app/api/auth.py` | Migrado a async |
| `backend/app/api/cash_register.py` | Migrado a async; `get_current_user` movido a `deps.py` |
| `backend/app/main.py` | Registro del router de categorías |
| `database/init.sql` | Tabla `categories`, columna `category_id`/`sku` en `products`, seeds |

### Reglas de negocio implementadas
- Categoría validada contra la BD al crear/editar un producto (cero datos quemados).
- Eliminación lógica (soft delete) vía campo `is_active`.
- Filtros de productos por `name`, `sku`, `barcode`, `is_active`, `category_id` y rangos de fecha.
- Unicidad de `name` (categorías), `sku` y `barcode` (productos).

### Verificación
- `python -m pytest -q` desde `backend/`: **12 pruebas pasan**.

### Pendiente / notas
- Recrear el volumen de Postgres (`docker-compose down -v && docker-compose up -d db`) para aplicar `init.sql` actualizado.
- Considerar migraciones versionadas con Alembic para entornos con datos existentes.
- El frontend (`frontend/js/app.js`) aún usa el formato previo de producto; debe actualizarse para enviar `category_id`/`sku`.