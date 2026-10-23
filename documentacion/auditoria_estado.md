# Auditoría de Estado: Módulos I, II y III (Base de Datos y Capas DERCAS)

**Fecha:** 2026-10-18  
**Tipo:** Auditoría de solo lectura  
**Alcance:** Tablas de Módulo I (Seguridad y Auditoría), Módulo II (Sucursales, Ubicación y Clientes) y Módulo III (Catálogo e Inventario).

---

## 1. Matriz de Estado por Tabla

> **Nota metodológica:** Conforme a las reglas de auditoría de solo lectura y aislamiento estricto, las columnas cuyos directorios fuente no fueron incluidos en el alcance de lectura (`backend/app/services/`, `backend/app/repositories/`, `backend/tests/`) se consignan formalmente como **No verificado**, evitando suposiciones no respaldadas por los archivos leídos (`models.py`, `main.py`, lista de `api/`, nombres de `alembic/versions/` y nombres de `frontend/js/`).

| Tabla | ¿Modelo SQLAlchemy? | ¿Router y endpoints? | ¿Servicio? | ¿Repositorio? | ¿Vista/JS en frontend? | ¿Tiene campo estado/is_active? | ¿Tests? |
|---|---|---|---|---|---|---|---|
| `rol` | Sí (`Rol`) | Sí (`roles.py` -> `/api/roles`) | No verificado | No verificado | Sí (`users.js`) | Sí (`estado`) | No verificado |
| `usuario` | Sí (`Usuario`) | Sí (`users.py` -> `/api/usuarios`, `auth.py` -> `/api/auth`) | No verificado | No verificado | Sí (`users.js`, `app.js`) | Sí (`estado`) | No verificado |
| `permiso` | Sí (`Permiso`) | Parcial (asociado a `roles.py` / `auth.py`; sin router CRUD dedicado) | No verificado | No verificado | Sí (`users.js`, `app.js`) | No | No verificado |
| `rol_permiso` | Sí (`RolPermiso`) | Parcial (asignación en `roles.py`) | No verificado | No verificado | Sí (`users.js`) | No | No verificado |
| `sesion_usuario` | Sí (`SesionUsuario`) | Parcial (gestión de login/tokens en `auth.py`; sin CRUD dedicado) | No verificado | No verificado | Sí (`app.js`) | No | No verificado |
| `bitacora_auditoria` | Sí (`BitacoraAuditoria`) | No (sin router dedicado en `api/`) | No verificado | No verificado | No | No | No verificado |
| `parametro_sistema` | Sí (`ParametroSistema`) | Sí (`configuracion.py`) | No verificado | No verificado | Sí (`configuracion.js`) | No | No verificado |
| `intento_login` | Sí (`IntentoLogin`) | Parcial (operado internamente en `auth.py`; sin CRUD público) | No verificado | No verificado | Parcial (`app.js`) | No | No verificado |
| `sucursal` | Sí (`Sucursal`) | Parcial (`catalogos.py` / `configuracion.py`; sin router CRUD dedicado) | No verificado | No verificado | Parcial (`catalog.js`, `configuracion.js`) | Sí (`estado`) | No verificado |
| `area_bodega` | Sí (`AreaBodega`) | Parcial (`catalogos.py`; sin router CRUD dedicado) | No verificado | No verificado | Parcial (`catalog.js`, `inventory.js`) | No | No verificado |
| `departamento_geografico` | Sí (`DepartamentoGeografico`) | Sí (`departments.py` -> `/api/departamentos`) | No verificado | No verificado | No verificado | No | No verificado |
| `municipio` | Sí (`Municipio`) | Parcial (`departments.py`; sin router propio) | No verificado | No verificado | No verificado | No | No verificado |
| `tipo_cliente` | Sí (`TipoCliente`) | No (no existe router de clientes en `api/`) | No verificado | No verificado | No | No | No verificado |
| `cliente` | Sí (`Cliente`) | No (no existe router de clientes en `api/`) | No verificado | No verificado | No | No | No verificado |
| `cliente_contacto` | Sí (`ClienteContacto`) | No (sin router en `api/`) | No verificado | No verificado | No | No | No verificado |
| `categoria` | Sí (`Categoria`) | Sí (`categories.py` -> `/api/categorias`) | No verificado | No verificado | Sí (`catalog.js`) | Sí (`estado`) | No verificado |
| `subcategoria` | Sí (`Subcategoria`) | Parcial (`categories.py` / `catalogos.py`; sin router CRUD dedicado) | No verificado | No verificado | Sí (`catalog.js`) | No | No verificado |
| `unidad_medida` | Sí (`UnidadMedida`) | Parcial (`catalogos.py`; sin router CRUD dedicado) | No verificado | No verificado | Sí (`catalog.js`) | No | No verificado |
| `producto` | Sí (`Producto`) | Sí (`products.py` -> `/api/productos`) | No verificado | No verificado | Sí (`catalog.js`) | Sí (`estado`) | No verificado |
| `variante_producto` | Sí (`VarianteProducto`) | Parcial (`products.py` / `inventory.py`; sin router independiente) | No verificado | No verificado | Sí (`catalog.js`, `inventory.js`) | No | No verificado |
| `inventario_sucursal` | Sí (`InventarioSucursal`) | Sí (`inventory.py` -> `/api/inventory` e `/api/inventario`) | No verificado | No verificado | Sí (`inventory.js`) | No | No verificado |
| `historial_precio` | Sí (`HistorialPrecio`) | No (sin router dedicado en `api/`) | No verificado | No verificado | No verificado | No | No verificado |
| `alerta_stock` | Sí (`AlertaStock`) | Sí (`inventory.py` -> endpoints de alertas) | No verificado | No verificado | Sí (`inventory.js`, `notificaciones.js`) | Sí (`estado`) | No verificado |

---

## 2. Hallazgos Específicos

### (a) Tablas sin CRUD (dentro del alcance Módulos I, II y III)
1. **Módulo II - Clientes (`cliente`, `tipo_cliente`, `cliente_contacto`):** Ausencia total de router en `backend/app/api/` (no existen `clientes.py`, `clients.py`, ni `tipo_cliente.py`). Tampoco hay vistas ni scripts en `frontend/js/` para la gestión de clientes.
2. **Módulo II - Ubicación y Espacios (`area_bodega`, `sucursal`):** No tienen endpoints CRUD dedicados en `backend/app/api/` (solo lectura auxiliar en `catalogos.py`).
3. **Módulo I - Seguridad y Auditoría (`bitacora_auditoria`, `sesion_usuario`, `intento_login`):** 
   - `bitacora_auditoria` no tiene controlador expuesto para consulta ni filtrado.
   - `sesion_usuario` e `intento_login` se consumen internamente en `auth.py`, pero carecen de operaciones CRUD administrativas.
   - `permiso` y `rol_permiso` carecen de router CRUD autónomo para crear o modificar permisos (solo asignación indirecta en roles).
4. **Módulo III - Históricos y Auxiliares de Catálogo (`historial_precio`, `unidad_medida`, `subcategoria`):** 
   - `historial_precio` no cuenta con router ni endpoints de consulta/gestión.
   - `unidad_medida` y `subcategoria` se consumen de solo lectura en `catalogos.py`, careciendo de mantenimiento CRUD propio.

### (b) Discrepancias entre `models.py` y el esquema base (nombres en español, 44 tablas)
1. **Total de tablas en `models.py`:** El archivo define **46 clases ORM** con su respectivo `__tablename__`, superando las 44 tablas del esquema de negocio original.
2. **Tablas adicionales de sincronización/arquitectura:** 
   - `sync_cache_metadata` (Módulo 1 / Sync, línea 103).
   - `sync_queue` (Módulo Sync / Offline, línea 614).
3. **Consistencia de nombres en Base de Datos:** Todas las 46 tablas en `models.py` respetan estrictamente la nomenclatura en español, en minúsculas y en singular (`rol`, `usuario`, `producto`, `inventario_sucursal`, `detalle_venta`, etc.).
4. **Estado lógico:** Solo 6 de las 23 tablas auditadas poseen campo explícito de estado (`estado = Column(String(20))`): `rol`, `usuario`, `sucursal`, `categoria`, `producto`, `alerta_stock`. Las restantes tablas maestras (`cliente`, `tipo_cliente`, `unidad_medida`, `subcategoria`, `area_bodega`, `departamento_geografico`, `municipio`) no tienen columna de estado/is_active en `models.py`.

### (c) Uso de nombres en inglés en el código en lugar del esquema en español
Existe una discrepancia híbrida evidente entre el esquema de base de datos (100% español) y los nombres de archivos/módulos en backend y frontend:
1. **Routers en `backend/app/api/` con nombres en inglés:**
   - `users.py` (tabla: `usuario`)
   - `roles.py` (plural inglés/español)
   - `categories.py` (tabla: `categoria`)
   - `products.py` (tabla: `producto`)
   - `departments.py` (tabla: `departamento_geografico`)
   - `inventory.py` (tabla: `inventario_sucursal`)
   - `sales.py` (tabla: `venta`)
   - `cash_register.py` (tabla: `caja` / `turno_caja`)
   - *Nota de mitigación:* `main.py` traduce la mayoría de estos al exponerlos con prefijos en español (`/api/usuarios`, `/api/categorias`, `/api/productos`, `/api/departamentos`, `/api/roles`, `/api/ventas`, `/api/caja`), pero la estructura de código fuente interna permanece en inglés.
2. **Controladores que sí usan español en `backend/app/api/`:**
   - `catalogos.py`, `compras.py`, `configuracion.py`, `mermas.py`, `reportes.py`, `facturacion.py`.
3. **Archivos de lógica en `frontend/js/` con nombres en inglés:**
   - `users.js`, `catalog.js`, `cash_register.js`, `inventory.js`, `pos.js`, `sync.js`.
   - Contrastan con los archivos en español: `compras.js`, `configuracion.js`, `notificaciones.js`, `reportes.js`.

---

## 3. Capas: Cobertura Arquitectónica por Tabla con Router Existente

Esta sección audita en profundidad las tablas de los Módulos I, II y III que cuentan con endpoints/routers activos (`roles`, `users`, `departments`, `categories`, `products`, `inventory`, `configuracion`, `catalogos`):

| Tabla | Router / Endpoint | Schema | Repositorio | Servicio | Interfaz (ABC) | Tests | Filtros | Paginación | Soft Delete |
|---|---|---|---|---|---|---|---|---|---|
| `rol` | `/api/roles` (`roles.py`) | Sí (`schemas.py`: `RoleOut`, `RoleCreate`, `RoleUpdate`) | Sí (`role_repository.py`) | Sí (`role_service.py`) | Sí (`RoleRepository`, `RoleService`) | Sí (`test_rbac.py`) | No (solo `include_inactive`) | No (lista completa) | Sí (`estado="Inactivo"`) |
| `usuario` | `/api/usuarios` (`users.py`) | Sí (`schemas.py`: `UserResponse`, `UserCreate`, `UserFilter`) | Sí (`user_repository.py`) | Sí (`user_service.py`) | Sí (`UserRepository`, `UserService`) | Sí (`test_rbac.py`, `test_security_audit_lockout.py`) | Sí (búsqueda, rol, estado) | Sí (`page`, `page_size`, `count`) | Sí (`estado="Inactivo"`) |
| `parametro_sistema` | `/api/configuracion` (`configuracion.py`) | Sí (`configuracion_schema.py`) | Sí (`configuracion_repository.py`) | Sí (`configuracion_service.py`) | No | Sí (`test_configuracion_service.py`) | No | No (clave/valor) | No |
| `departamento_geografico` | `/api/departamentos` (`departments.py`) | Sí (`schemas.py`: `Department`, `DepartmentCreate`) | Sí (`department_repository.py`) | Sí (`department_service.py`) | Sí (`DepartmentRepository`, `DepartmentService`) | No verificado (`.old` en tests) | No (solo `include_inactive`) | No | Sí en servicio (`deactivate_department`) |
| `sucursal` | `/api/catalogos/sucursales` | Sí (`schemas.py`: `SucursalOut`) | Integrado (`product_repository.py`) | Sí (`catalogo_service.py`) | Sí (`CatalogoService`) | Sí (integración) | No (solo `include_inactive`) | No | No (solo lectura) |
| `area_bodega` | `/api/catalogos/areas` | Sí (`schemas.py`: `AreaBodegaOut`) | Integrado (`product_repository.py`) | Sí (`catalogo_service.py`) | Sí (`CatalogoService`) | Sí (integración) | Sí (`sucursal_id`) | No | No (solo lectura) |
| `categoria` | `/api/categorias` (`categories.py`) | Sí (`schemas.py`: `CategoriaOut`, `CategoriaCreate`) | Sí (`category_repository.py`) | Sí (`category_service.py`) | Sí (`CategoryRepository`, `CategoryService`) | No verificado (`.old` en tests) | No (solo `include_inactive`) | No | Sí (`estado="Inactivo"`) |
| `subcategoria` | `/api/catalogos/subcategorias` | Sí (`schemas.py`: `SubcategoriaOut`) | Integrado (`product_repository.py`) | Sí (`catalogo_service.py`) | Sí (`CatalogoService`) | Sí (integración) | No (solo `include_inactive`) | No | No (solo lectura) |
| `unidad_medida` | `/api/catalogos/unidades` | Sí (`schemas.py`: `UnidadMedidaOut`) | Integrado (`product_repository.py`) | Sí (`catalogo_service.py`) | Sí (`CatalogoService`) | Sí (integración) | No | No | No (solo lectura) |
| `producto` | `/api/productos` (`products.py`) | Sí (`schemas.py`: `ProductoOut`, `ProductoCreate`, `ProductoFilter`) | Sí (`product_repository.py`) | Sí (`product_service.py`) | Sí (`ProductRepository`, `ProductService`) | No verificado (`.old` en tests) | Sí (búsqueda, categoría, sucursal, etc.) | Sí (`page`, `page_size`, `count`) | Sí (`estado="Inactivo"`) |
| `variante_producto` | `/api/productos` (sub-rutas) | Sí (`schemas.py`: `VarianteProductoOut`) | Integrado (`product_repository.py`) | Integrado (`product_service.py`) | Integrado en `ProductRepository` | Sí (en tests de compras/ventas) | Sí (vía código de barras) | Subordinada a producto | No (hereda del producto) |
| `inventario_sucursal` | `/api/inventory` e `/api/inventario` | Sí (`inventory_schema.py`) | Sí (`inventory_repository.py`) | Sí (`inventory_service.py`) | No | Sí (`test_inventory_service.py`, `test_concurrency_stock.py`) | Sí (`id_sucursal`, `low_stock_only`) | Paginación en cliente | No |
| `alerta_stock` | `/api/inventory/alerts` | Sí (`inventory_schema.py`: `AlertaStockResponse`) | Sí (`inventory_repository.py`) | Sí (`inventory_service.py`) | No | Sí (`test_inventario_alertas.py`) | Sí (`id_sucursal`, `estado`) | No | No (cambio de estado) |

---

## 4. Preguntas de Integración Específicas

### (1) ¿A qué tabla apunta `departments.py` / `department_service.py`?
Apunta directamente a la tabla **`departamento_geografico`** (modelo SQLAlchemy `DepartamentoGeografico`).  
Tanto `department_repository.py` como `department_service.py` importan y operan exclusivamente sobre `from app.db.models import DepartamentoGeografico`. La confusión proviene de la traducción literal al inglés (`department` en lugar de `departamento_geografico`).

### (2) ¿Existen endpoints de catálogo (sucursales, subcategorías, unidades, áreas) y qué archivo del frontend los consume?
**Sí, existen** y están implementados en `backend/app/api/catalogos.py` bajo el prefijo `/api/catalogos`:
- `GET /api/catalogos/subcategorias` (retorna `List[SubcategoriaOut]`)
- `GET /api/catalogos/unidades` (retorna `List[UnidadMedidaOut]`)
- `GET /api/catalogos/sucursales` (retorna `List[SucursalOut]`)
- `GET /api/catalogos/areas` (acepta query param opcional `sucursal_id`, retorna `List[AreaBodegaOut]`)

**Archivo del frontend que los consume:**
Es consumido exclusivamente por **`frontend/js/catalog.js`**:
- Línea 16: `const CATALOGOS_API = '/api/catalogos';`
- Línea 362: `${CATALOGOS_API}/subcategorias` (carga selector de subcategorías)
- Línea 373: `${CATALOGOS_API}/unidades` (carga selector de unidades de medida)
- Línea 384: `${CATALOGOS_API}/sucursales` (carga selector de sucursales)
- Línea 399: `${CATALOGOS_API}/areas?sucursal_id=${sucursalId}` (carga áreas dependientes de la sucursal seleccionada)

