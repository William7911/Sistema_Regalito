# constitution.md — Reglas Maestras del Proyecto Tienda el Regalito POS

> Este documento es de cumplimiento **obligatorio** para cualquier agente de IA (o desarrollador) que trabaje en este repositorio.
> Ninguna directriz aquí puede ser ignorada, debilitada ni revertida sin aprobación explícita del dueño del proyecto.

---

## 1. Arquitectura — Patrón DERCAS

El proyecto usa **exclusivamente** el patrón de capas **DERCAS**:

| Capa | Responsabilidad |
|------|----------------|
| **Controllers** (API) | Reciben la petición HTTP, validan entrada con DTOs, llaman al servicio correspondiente y devuelven la respuesta. **Cero lógica de negocio.** Cero `try/except` propios. |
| **Services** | Contienen **toda** la lógica de negocio. Orquestan repositorios. Nunca tocan la sesión de base de datos directamente. |
| **Repositories** | Acceso a datos (SQLAlchemy 2.x async). Solo consultas y mutaciones. No contienen reglas de negocio. No hacen `commit`; eso es responsabilidad del Unit of Work. |
| **Unit of Work (UoW)** | Agrupa repositorios y decide `commit` o `rollback`. Se inyecta vía `Depends()` en FastAPI. |
| **Interfaces (ABC)** | Cada repositorio y servicio tiene su contrato abstracto en `interfaces/`. Facilita pruebas y sustitución. |
| **DTOs (Schemas)** | Pydantic v2. Toda entrada y salida tipada estrictamente. |

### Reglas inviolables de arquitectura

- **Cero lógica de negocio en controladores.** Si un controlador hace más que llamar a un servicio, es un error.
- **Cero acceso directo a la BD desde controladores.** Todo pasa por el repositorio.
- **Los repositorios no hacen `commit`.** El Unit of Work decide cuándo persiste.
- **Las dependencias se inyectan** mediante `Depends()` de FastAPI. No se instancian servicios ni repositorios manualmente dentro de controladores.

---

## 2. Principios de Diseño

Aplicar en **cada cambio**, sin excepción:

- **SOLID** — Single Responsibility, Open/Closed, Liskov Substitution, Interface Segregation, Dependency Inversion.
- **DRY** — No duplicar lógica. Si algo se repite en dos lugares, extraerlo a una función o servicio compartido.
- **KISS** — La solución más simple que resuelve el problema es la correcta. Evitar sobre-ingeniería.

---

## 3. Backend

| Ítem | Regla |
|------|-------|
| **Lenguaje** | Python 3.13 |
| **Framework** | FastAPI (última versión estable compatible) |
| **ORM** | SQLAlchemy 2.x con driver `asyncpg` (async nativo) |
| **Carga de relaciones** | **Siempre** usar `selectinload` (o `joinedload` cuando sea apropiado). **Prohibido** el lazy loading implícito que cause `MissingGreenletError`. |
| **Contraseñas** | `passlib` con `bcrypt==4.0.1`. No actualizar bcrypt a 5.x sin validar compatibilidad. |
| **JWT** | Expiración configurada en `settings.ACCESS_TOKEN_EXPIRE_MINUTES` (actualmente 480 min = 8 h). No hardcodear en el código. |
| **Auditoría** | Toda acción crítica (login, CRUD de usuarios, ventas, mermas, cierres, cambios de precio) debe registrarse en `bitacora_auditoria` vía `audit_service.log_action()`. |
| **Fuerza bruta** | Bloqueo persistido en BD (`intento_login`). 5 intentos fallidos → bloqueo 5 min → HTTP 429. Manejado por `LoginSecurityService`. |
| **Concurrencia de stock** | Todo descuento de `inventario_sucursal.stock_actual` debe usar `SELECT FOR UPDATE` (bloqueo pesimista). |
| **Migraciones** | Solo Alembic. Aditivas, reversibles con `downgrade`, sincronizadas en `database/init.sql`. Numeradas secuencialmente (`0001`, `0002`, …). |
| **Variables de entorno** | Toda configuración sensible vive en `.env` y se accede a través de `app/core/config.py`. Nada hardcodeado. |

---

## 4. DTOs — Pydantic v2

- **Uso obligatorio** de Pydantic v2 para **todos** los esquemas de entrada y salida.
- Los tipos deben ser estrictos: usar `int`, `str`, `Decimal`, `datetime`, `UUID`, etc. según corresponda. Prohibido `Any` sin justificación documentada.
- Los esquemas viven en `app/schemas/`. Un archivo por dominio (e.g. `user_schema.py`, `product_schema.py`).
- Nunca devolver modelos SQLAlchemy directamente desde un controlador — siempre pasar por un DTO de respuesta.

---

## 5. Frontend

| Ítem | Regla |
|------|-------|
| **Lenguaje** | Vanilla JavaScript (ES2022+). Sin frameworks pesados (React, Vue, Angular, etc.). |
| **Diálogos** | **Cero** `alert()`, `confirm()`, `prompt()`. Usar exclusivamente modales Bootstrap con `data-bs-backdrop="static"`. |
| **Notificaciones** | Usar Toast (componente Bootstrap o equivalente ligero). Nunca interrumpir el flujo del usuario con bloqueos síncronos. |
| **Peticiones HTTP** | `fetch()` nativo con interceptores para manejar JWT expirado (→ redirect a login limpiando sesión). |
| **Estado de sesión** | Token JWT en `localStorage`. Al recibir HTTP 401, limpiar token y redirigir al login (reutilizar lógica de logout existente en `app.js`). |
| **Versionado de assets** | Usar query string de versión en `<script src="js/archivo.js?v=X.Y">` para forzar recarga al desplegar. |

---

## 6. Pruebas

| Ítem | Regla |
|------|-------|
| **Framework** | `pytest` + `pytest-asyncio` |
| **Base de datos en tests** | `aiosqlite` en memoria. **No** se requiere PostgreSQL para ejecutar la suite. |
| **Cobertura** | Toda funcionalidad nueva debe tener al menos una prueba. Las rutas críticas (auth, ventas, stock, permisos) deben tener pruebas de error y de éxito. |
| **Integridad** | **Prohibido** falsear pruebas, crear aserciones vacías (`assert True`) o deshabilitar tests para que pasen. Si un test falla, se corrige el código o el test, no se evade. |
| **Aislamiento** | Cada test debe ser independiente. No depender del orden de ejecución. Usar fixtures para setup/teardown. |
| **Concurrencia** | Las pruebas de concurrencia de stock deben verificar el comportamiento real de `SELECT FOR UPDATE`, no simularlo con mocks. |

---

## 7. Base de Datos

| Ítem | Regla |
|------|-------|
| **Motor principal** | PostgreSQL (fuente de verdad definitiva). Puerto `5433` en entorno Docker local. |
| **Motor local (offline)** | SQLite (`pos_local.db`) — solo caché de lectura y cola de escritura offline. **No** es fuente de verdad. |
| **Secuencias** | Todas las PKs tipo `INT` usan secuencias (`GENERATED BY DEFAULT AS IDENTITY` o `SERIAL`). No se asignan IDs manualmente. |
| **Unicidad** | Todo campo que el sistema trata como único (username, código de barras, número de DTE) debe tener `UNIQUE CONSTRAINT` en la BD, no solo validación en aplicación. |
| **Índices en FK** | PostgreSQL no indexa FK automáticamente. Toda FK usada en filtros, joins o reportes frecuentes debe tener su índice explícito. |
| **No negatividad** | Los campos de cantidad y stock tienen `CHECK (columna >= 0)` a nivel de BD. |

---

## 8. Control de Cambios

- **Todo cambio debe documentarse** en `documentacion/cambios.md` con: causa raíz, solución implementada y verificación realizada.
- **Ninguna mejora revierte trabajo anterior.** Si hay conflicto con algo ya implementado, detener y consultar al dueño del proyecto antes de continuar.
- Antes de implementar cualquier cambio que afecte la BD, verificar que los datos existentes no violan las nuevas restricciones.

---

## 9. Flujo de Trabajo del Agente

1. Leer este archivo antes de cualquier tarea.
2. Identificar el alcance exacto de la tarea. No tocar nada fuera de él.
3. Si hay ambigüedad o un trade-off importante, **preguntar antes de asumir**.
4. Ejecutar la suite completa de pruebas (`pytest`) antes y después de cada cambio.
5. Documentar en `cambios.md` al finalizar.
6. Esperar confirmación del usuario antes de pasar a la siguiente fase en tareas multi-fase.

---

*Versión 1.0 — Creado: 2026-10-04*
