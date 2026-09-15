# AGENTS.md — Instrucciones para Agentes y Asistentes de Desarrollo

## Contexto del proyecto
POS "Tienda el Regalito" — backend **FastAPI (Python 3.13)** con **PostgreSQL 15** y **SQLAlchemy 2.x asíncrono** (`asyncpg`). Migraciones con **Alembic**. Frontend estático servido por el backend. Docker para la BD.

## Estado del Módulo de Usuarios (último avance)
- CRUD de **Roles**, **Departamentos** y **Usuarios** (con eliminación lógica y filtros).
- `User` normalizado: `name`, `lastname`, `code`, `username`, `password_hash`, `role_id`, `department_id`, `is_active`.
- Dropdowns de Rol/Departamento en el frontend se llenan desde la BD (`frontend/js/users.js`), cero datos quemados.

## Convenciones de desarrollo (obligatorias)

1. **Arquitectura por capas** (no romperla):
   - `app/api/` → Controllers (delgados, cero lógica, cero try/except). Solo reciben petición, llaman al servicio y devuelven JSON con códigos HTTP correctos.
   - `app/services/` → Lógica de negocio y validaciones.
   - `app/repositories/` → Único punto de acceso a datos (async/await, SQLAlchemy `select()`).
   - `app/interfaces/` → Contratos `ABC` de servicios y repositorios.
   - `app/db/models.py` → Entidades SQLAlchemy.
   - `app/schemas/` → DTOs Pydantic v2. Nunca exponer entidades de BD al cliente.

2. **Acceso a datos**: siempre asíncrono (`async def` + `await`). Usar `select()` de SQLAlchemy 2.x. Prohibido concatenar strings SQL (seguridad contra inyección).

3. **Inyección de dependencias + Unit of Work**: ensamblar repositorios y servicios en `app/api/deps.py`; usar la sesión async de `app/db/database.py#get_db`. El `UnitOfWork` (en `deps.py`) agrupa transacciones: los repositorios del módulo de Usuarios NO hacen commit; los servicios llaman `uow.commit()`/`uow.rollback()`.

4. **Manejo de errores**: usar los handlers globales de `main.py` (HTTPException y Exception→500). Los controladores NO deben tener try/except.

5. **Reglas de negocio**:
   - Cero datos quemados: consultar roles/departamentos/categorías/productos desde la BD.
   - Soft delete: nunca `DELETE`; usar campo `is_active`.
   - Filtros de productos: `name`, `sku`, `barcode`, `is_active`, `category_id`, `created_from`, `created_to`.
   - Filtros de usuarios: `name`, `lastname`, `code`, `is_active`, `role_id`, `department_id`, `created_from`, `created_to`.
   - Contraseñas siempre en hash (`bcrypt`, fijar `bcrypt==4.0.1`).

6. **Esquema de BD**: al cambiar modelos, actualizar **Alembic** (generar/ajustar migración) Y `database/init.sql`. Recordar que `init.sql` solo corre en volumen nuevo; usar `alembic upgrade head` para entornos con datos.

## Pruebas
- Framework: `pytest` + `pytest-asyncio` (modo auto) + `aiosqlite`.
- Correr siempre después de cambios: `python -m pytest -q` (desde `backend/`).
- Las pruebas usan SQLite en memoria; no requieren PostgreSQL. Hay fixture `db_session` y `uow` en `tests/conftest.py`.

## Documentación (regla estricta)
- TODO cambio futuro debe registrarse en la carpeta `/documentacion`.
- `documentacion/cambios.md`: registrar cada cambio/componente creado/modificado.
- `documentacion/general.md`: arquitectura y configuración de BD.

## Antes de hacer cambios
1. Lee este archivo y `documentacion/cambios.md` para conocer el estado actual.
2. Respeta las convenciones anteriores y las tecnologías ya instaladas.
3. Verifica con las pruebas y actualiza la documentación al terminar.