# Registro de Cambios

## Regla de documentación (obligatoria)
Cualquier cambio futuro en el proyecto debe quedar documentado en esta carpeta `/documentacion`. Agrega una entrada en este archivo (`cambios.md`) cada vez que modifiques, crees o elimines componentes.

---

## [2026-09-16] Fix defensivo: lectura segura de filtros y paginación en Usuarios y Catálogos

### Contexto
Resolución del fallo que bloqueaba el renderizado de datos en las tablas de Usuarios y Catálogos (`loadUsers()` y `loadProducts()`), donde se lanzaba la excepción `Uncaught TypeError: Cannot read properties of null (reading 'value')`. La causa residía en lecturas directas del DOM (`document.getElementById('...').value`) sin comprobar la existencia previa del elemento en el HTML (filtros de fecha `#filter-from`, `#filter-to`, `#filter-product-from`, `#filter-product-to` y controles de paginación).

### Solución aplicada

#### 1. Frontend JavaScript (`frontend/js/users.js` y `frontend/js/catalog.js`)
- **Lectura defensiva con encadenamiento opcional**: Se sustituyeron todas las lecturas directas por el patrón `document.getElementById('campo')?.value || ''`.
- **Valores seguros por defecto en paginación**: Se implementó `parseInt(document.getElementById('per-page')?.value || String(state.pageSize || 10), 10) || 10` para garantizar que la construcción de query params (`limit`, `offset`, `page`) nunca reciba `NaN` o valores inválidos ante la ausencia temporal del elemento.
- **Protección de renderizado**: Verificación `if (!tbody) return;` al inicio de `loadUsers()` y `loadProducts()` para prevenir errores en ciclos de renderizado desacoplados.

#### 2. Frontend HTML (`frontend/index.html`)
- **Filtros de rango de fechas sincronizados**:
  - En Usuarios (`#users-view`): Se agregaron los input groups etiquetados con icono de calendario para `#filter-from` ("Desde") y `#filter-to` ("Hasta").
  - En Catálogos (`#catalog-view`): Se agregaron los input groups para `#filter-product-from` ("Desde") y `#filter-product-to` ("Hasta").
- **Barras de paginación reactiva**:
  - Se añadieron los bloques `#users-pagination` (con `#users-page-size`, `#users-prev-page`, `#users-page-info`, `#users-next-page`) y `#products-pagination` (con `#products-page-size`, `#products-prev-page`, `#products-page-info`, `#products-next-page`).
- **Modales de detalle**:
  - Se agregaron los modales `#user-detail-modal` y `#product-detail-modal` con `data-bs-backdrop="static"` y `data-bs-keyboard="false"`.

### Verificación
- `node --check frontend/js/users.js`: OK.
- `node --check frontend/js/catalog.js`: OK.
- Inspección de IDs: Todos los elementos requeridos por los scripts existen idénticos en `frontend/index.html`.
- Pruebas backend: `10 passed in 1.10s`.

---

## [2026-09-15] Corrección visual de cabeceras de tabla: contraste, fondos corporativos y homologación transversal

### Contexto
Corrección del problema de contraste y visibilidad en los títulos de columnas (`<thead>`, `<th>`) en las tablas de Usuarios, Catálogos (Productos y Categorías) y Caja. Las cabeceras aparecían con texto en blanco o transparente sobre fondo blanco debido al sombreado interno por defecto de Bootstrap 5 (`box-shadow: inset ...`) que cubría el fondo de los `<thead>`, sumado a la falta de asignación explícita de `background-color` y anulación de `box-shadow` a nivel de celda `<th>`.

### Solución aplicada

#### 1. Estilos CSS (`frontend/css/style.css`)
- **Regla base de alto contraste para cabeceras (`table thead th`, `.table thead th`)**: Asigna `color: #1E293B !important` (texto oscuro) y `background-color: #F8FAFC !important` (gris claro suave) con `box-shadow: none !important`, garantizando legibilidad inmediata en cualquier tabla que no tenga clase corporativa.
- **Cabeceras corporativas (`.thead-catalog`, `.thead-cash`, `.thead-users`)**:
  - Asignación directa y explícita de `background-color` y gradiente corporativo RNF24 a `thead`, `tr` y a las celdas `th` (`#0284C7`/`#0369A1` para Catálogos, `#0D7377`/`#0A5C5E` para Caja y Usuarios).
  - Eliminación del box-shadow nativo de Bootstrap con `box-shadow: none !important` en `th`.
  - Color de texto blanco puro garantizado con `color: #FFFFFF !important` en `th`, enlaces `a`, `span` e iconos `i`.
  - Esquinas suavemente redondeadas en los extremos (`th:first-child`, `th:last-child`).
- **Interacción y ordenamiento (`th.sortable`)**:
  - Efecto hover no destructivo mediante `filter: brightness(1.12)` y `color: #FFFFFF !important` con subrayado sutil en cabeceras corporativas (evita que el texto cambie a azul oscuro sobre fondo azul/verde).
  - Iconos de ordenamiento (`.sort-icon`) con color blanco `#FFFFFF !important` en cabeceras corporativas y `#64748B` en cabeceras claras.

#### 2. Homologación de plantillas (`frontend/index.html`)
- **Módulo de Usuarios (`#users-view`)**: Se incorpora la clase corporativa `<thead class="thead-users">`, se homologa a 7 columnas (`ID`, `Nombre`, `Usuario`, `Rol`, `Estado`, `Fecha Reg.`, `Acciones`), con cabeceras ordenables (`th.sortable`, `data-sort`, `.sort-icon`).
- **Módulo de Catálogos (`#catalog-view`)**: En la tabla de Productos se homologan las 8 cabeceras ordenables con sus atributos `data-sort` correspondientes (`ID`, `Nombre`, `Subcategoría`, `Precio Detalle`, `Stock`, `Estado`, `Fecha Reg.`, `Acciones`). En Categorías se agrega cabecera de `Acciones`.
- **Módulo de Caja (`#cash-view`)**: Verificación y homologación del estilo visual `.thead-cash` sobre las 9 columnas de turnos.

### Restricciones respetadas
- Paleta corporativa RNF24 intacta.
- Cero `alert()` o `confirm()` nativos.
- Auth Guard, paginación reactiva y validaciones sin alteraciones.

### Verificación
- `node --check` sobre `app.js`, `users.js`, `catalog.js` y `cash_register.js`: OK.
- `python -m pytest tests/test_cash_service.py -v`: 10 passed in 1.13s.
- Verificación visual: Títulos de columnas perfectamente legibles, con contraste nítido, sin texto invisible ni blanco sobre blanco.

---

## [2026-09-15] Módulo de Caja: apertura, cierre de turnos, consulta de estado e historial SPA

### Contexto
Implementación integral de punta a punta del Módulo de Caja (apertura y cierre de turnos, consulta reactiva de estado e historial paginado de turnos) para el sistema POS *Tienda el Regalito*. Se adoptó la arquitectura empresarial DERCAS (Domain, Entities, Repositories, Use Cases, Adapters, Services) con Unit of Work asíncrono, eliminación de lazy loading con `selectinload`, controladores delgados sin lógica de negocio, y en frontend una vista SPA con Auth Guard, modales defensivos con backdrop estático, dirty check, 422 inline errors y paleta corporativa RNF24 (cero `alert()`/`confirm()` nativos).

### Base de Datos y Migraciones
| Componente | Detalle |
|------------|---------|
| `backend/app/db/models.py` | Enriquecimiento del modelo `TurnoCaja` con `monto_cierre` (`DECIMAL(10,2)`) y `notas` (`VARCHAR(255)`). Mantiene relaciones con `Caja` y `Usuario`. |
| `backend/alembic/versions/0004_caja_y_turno_caja_mejoras.py` | Migración aditiva para añadir columnas `monto_cierre` y `notas` en `turno_caja`. Creación y vinculación de secuencias PostgreSQL (`turno_caja_id_turno_seq`, `caja_id_caja_seq`) para auto-incremento de IDs. |
| `database/init.sql` | Actualización del DDL inicial con `monto_cierre`, `notas`, sequences para `id_caja` e `id_turno`, y estado por defecto de caja 1 en `'Activa'`. |

### Backend (DERCAS & Unit of Work)
| Archivo | Cambio |
|---------|--------|
| `backend/app/schemas/schemas.py` | Definición de esquemas Pydantic v2: `CajaOut`, `TurnoUsuarioOut`, `TurnoApertura`, `TurnoCierre`, `TurnoResponse`, `TurnoFilter` y `TurnoList` (con validaciones de montos > 0). |
| `backend/app/interfaces/repositories.py` | Contratos abstractos `CajaRepository` (`get_by_id`, `list_active`, `save`) y `TurnoCajaRepository` (`get_by_id`, `get_active_by_user`, `get_active_by_caja`, `save`, `search`, `count_search`). |
| `backend/app/interfaces/services.py` | Contrato abstracto `CashRegisterService` (`abrir_caja`, `cerrar_caja`, `get_estado_actual`, `list_turnos`, `list_cajas`). |
| `backend/app/repositories/cash_repository.py` | Implementación de repositorios con SQLAlchemy 2.0 asíncrono. Uso de `_TURNO_LOADS = (selectinload(TurnoCaja.caja), selectinload(TurnoCaja.usuario))` para erradicar `MissingGreenletError`. Ordenamiento seguro por diccionario `_SORTABLE`. |
| `backend/app/services/cash_service.py` | Lógica de negocio de caja: verificación de caja activa, prevención de apertura simultánea por el mismo usuario o en caja ocupada, cálculo de fecha y monto de cierre, consulta de estado actual, listado y conteo. |
| `backend/app/api/deps.py` | Registro de `cajas: CajaRepository` y `turnos: TurnoCajaRepository` en `UnitOfWork` y `SqlAlchemyUnitOfWork`. Proveedor de dependencias `get_cash_service`. |
| `backend/app/api/cash_register.py` | Router delgado (`/api/caja`) con endpoints `POST /apertura`, `POST /cierre`, `GET /estado-actual`, `GET /turnos`, `GET /cajas`. Sin lógica de negocio ni bloques try/except. |

### Frontend (SPA, Reactividad y UX Defensiva)
| Archivo | Cambio |
|---------|--------|
| `frontend/index.html` | Enlace de navegación Caja (`data-nav="cash"`); vista principal `#cash-view` (`data-main-view="cash"`); tarjeta visual de estado actual (badge ABIERTA / CERRADA, detalles de cajero, caja, fecha y monto, botones contextuales "Abrir Caja" y "Cerrar Caja"); filtros de rango de fechas con etiquetas "Desde" y "Hasta" e icono `bi-calendar-event`; tabla de historial con cabeceras ordenables (`th.sortable`); paginador reactivo `#cash-pagination`; modales `#open-cash-modal` y `#close-cash-modal` con `data-bs-backdrop="static"` y `data-bs-keyboard="false"`. Inclusión de `js/cash_register.js`. |
| `frontend/css/style.css` | Clase de estilo `.thead-cash` con fondo `var(--rosa-fucsia-dark)` y texto blanco para la cabecera de la tabla de turnos. |
| `frontend/js/app.js` | Registro de `'cash'` en `mainViews`; invocación de `showCashModule()` en `renderView`; soporte en `openModule` para mapear módulo `'caja'` a vista `'cash'`. |
| `frontend/js/cash_register.js` | Módulo reactivo completo: carga de cajas activas y estado actual al iniciar; apertura/cierre de turnos mediante fetch JWT; dirty check (`cashFormHasData`) y cierre seguro con `confirmModal`; traducción de validaciones 422 a errores inline (`translateCashValidation`); renderizado y ordenamiento dinámico de historial con iconos asc/desc; paginación interactiva con selector de tamaño de página; protección `beforeunload`. |

### Restricciones y Estándares Respetados
- **Cero alertas nativas:** Todos los mensajes usan `showToast()` (éxito, advertencia, error) y los diálogos de confirmación usan `confirmModal()`.
- **Auth Guard:** Integración total con `sessionStorage.getItem('token')` y redirección en 401.
- **Paleta RNF24:** Botones en celeste `#38BDF8`, rosado `#F472B6`, verde `#34D399` y estilos visuales consistentes con el diseño del sistema.
- **Modales Defensivos:** Cierre controlado por backdrop estático y confirmación en caso de datos no guardados.
- **Prevención Greenlet:** Serialización Pydantic libre de lazy loading gracias a `selectinload`.

### Verificación
- `backend/tests/test_cash_service.py`: 10 pruebas unitarias asíncronas aprobadas (`10 passed in 0.98s`) validando apertura, cierre, excepciones por caja ocupada/usuario con turno activo, consulta de estado y paginación.
- Verificación de compilación: `python -m py_compile` sin advertencias en todos los módulos backend.
- Verificación de sintaxis JS: `node --check frontend/js/app.js` y `node --check frontend/js/cash_register.js` exitosos.
- Integración real con base de datos PostgreSQL: validado ciclo de apertura (id 1, monto Q100.00), consulta de estado y cierre (monto Q325.50).
- Inspección OpenAPI: Las 5 rutas de `/api/caja/*` registradas satisfactoriamente en FastAPI.

---

## [2026-09-15] Homologación transversal Usuarios y Catálogos: claridad de filtros de fecha, columna de fecha y ordenamiento por columnas relacionadas

### Contexto
Mejoras visuales y funcionales aplicadas de forma transversal a los Módulos de Usuarios y de Catálogos (Productos) para aumentar la claridad de los filtros de fecha, mostrar la fecha de registro en las tablas y completar el ordenamiento sobre columnas relacionadas. Se conservaron intactos el Auth Guard, el dirty check (`formHasData`/`catalogFormHasData`), el `beforeunload`, la paginación reactiva, los modales defensivos (backdrop estático), los toasts y la paleta corporativa RNF24 (cero `alert()`/`confirm()` nativos).

### Frontend (`frontend/index.html`)
| Cambio | Detalle |
|--------|---------|
| Filtros de fecha etiquetados | En Usuarios y Productos, los inputs `date` se envuelven en **input groups** con icono de calendario (`bi-calendar-event`) y etiqueta visible **"Desde"** / **"Hasta"** (`#filter-from`/`#filter-to`, `#filter-product-from`/`#filter-product-to`). |
| Columna "Fecha Reg." | Se agrega la columna **"Fecha Reg."** antes de "Acciones" en las tablas de Usuarios y Productos, como cabecera ordenable (`th.sortable` con `data-sort="fecha_creacion"` y tooltip "Ordenar por fecha"). |
| Cabecera Rol ordenable | En Usuarios, la cabecera "Rol" pasa a `th.sortable` con `data-sort="rol"`. |

### Frontend (JS)
| Archivo | Cambio |
|---------|--------|
| `frontend/js/users.js` | Helper `formatDate()` (DD/MM/YYYY); renderiza la celda "Fecha Reg." por fila; `updateSortIndicators()` y el wiring de ordenamiento se acotan a `#users-view th.sortable` (evita colisiones con la tabla de productos). |
| `frontend/js/catalog.js` | Helper `formatDate()` (DD/MM/YYYY, autocontenido); renderiza la celda "Fecha Reg." por fila. |

### Backend (`backend/app/repositories/user_repository.py`)
| Cambio | Detalle |
|--------|---------|
| Ordenamiento por Rol | `_SORTABLE` agrega `"rol": Rol.nombre`; `search()` hace `join(Usuario.rol)` solo cuando `sort_by == "rol"` (ordenamiento seguro vía diccionario de columnas permitidas, sin inyección). Se importa `Rol`. |

### Restricciones respetadas
- Auth Guard, SPA (`navigateTo`/`renderView`/`mainViews`), dirty check, `beforeunload`, paginación, modales defensivos y toasts intactos.
- Paleta RNF24 y validación inline 422 conservadas. Sin `alert()`/`confirm()` nativos.

### Verificación
- `node --check frontend/js/users.js` y `frontend/js/catalog.js`: OK.
- `python -m py_compile` sobre repositorios modificados: OK.
- Prueba de repositorio (SQLite en memoria): ordenamiento por `rol` asc/desc en Usuarios y por `fecha_creacion`, `id_producto`, `stock`, `precio_detalle`, `subcategoria`, `nombre`, `estado` en Productos, sin errores SQL.
- `from app.main import app` / `app.openapi()`: OK (18 rutas).

---

## [2026-09-15] Módulo de Catálogos: paginación reactiva, ordenamiento de columnas, filtro de fechas y modal de detalle

### Contexto
Homologación del Módulo de Catálogos (Productos) con las mejoras de reporte inteligente ya implementadas en Usuarios: paginación con `limit`/`offset`, ordenamiento asc/desc de columnas, filtros de fecha (`created_from`/`created_to`) y un modal informativo de solo lectura para consultar la ficha completa del producto. Se conservaron intactos el Auth Guard, el Hash Routing SPA (`mainViews`), el dirty check (`catalogFormHasData`), el `beforeunload`, los spinners de guardado y los toasts; se mantiene la paleta corporativa RNF24 (celeste, rosado, verde) y la validación inline de errores 422 (cero `alert()`/`confirm()` nativos).

### Backend (habilitación de fecha, ordenamiento y columnas relacionadas)
| Archivo | Cambio |
|---------|--------|
| `backend/app/db/models.py` | `Producto` gana la columna `fecha_creacion` (`DateTime`, `server_default=func.now()`, no nulo) para soportar los filtros de fecha. |
| `database/init.sql` | `producto` ahora incluye `fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW()`. |
| `backend/alembic/versions/0003_agregar_fecha_creacion_a_producto.py` | **Nueva migración aditiva** que agrega `fecha_creacion` a `producto` (preserva datos); aplicable con `alembic upgrade head`. |
| `backend/app/schemas/schemas.py` | `ProductoFilter` agrega `created_from`, `created_to` (`datetime`) y `sort_by`, `sort_dir` (`asc`/`desc`); `ProductoOut` expone `fecha_creacion`. |
| `backend/app/repositories/product_repository.py` | `search`/`count_search` aplican filtros de rango sobre `fecha_creacion`; ordenamiento dinámico con `_SORTABLE` (diccionario permitido) y joins seguros (`_apply_order_joins`) para `subcategoria`, `precio_detalle` y `stock`. |
| `backend/app/services/product_service.py` | `list_products`/`count_products` propagan los nuevos parámetros al repositorio. |
| `backend/app/interfaces/repositories.py` | Contratos `search`/`count_search` actualizados con los nuevos parámetros. |

### Frontend (lista interactiva + modal de detalle)
| Archivo | Cambio |
|---------|--------|
| `frontend/index.html` | En la tabla de Productos: columna **ID**; cabeceras ordenables (`th.sortable` con `data-sort` para ID, Nombre, Subcategoría, Precio Detalle, Stock y Estado); dos inputs `type=date` (`#filter-product-from`, `#filter-product-to`); botón "Ver" (ojo) por fila; barra de paginación `#products-pagination` (prev/next, página actual y selector `#products-page-size` 5/10/20/50); **nuevo modal `#product-detail-modal`** de solo lectura con `data-bs-backdrop="static"` y `data-bs-keyboard="false"` (matriz, variante, precios e inventario por sucursal). |
| `frontend/js/catalog.js` | Estado `productsState` (página, tamaño, total, sort); `loadProducts` envía `created_from`, `created_to`, `sort_by`, `sort_dir`, `limit`, `offset` y usa `data.total`; nuevas funciones `renderProductPagination()`, `goToProductPage()`, `toggleProductSort()`, `updateProductSortIndicators()` y `viewProductDetail()`; wiring de paginación, ordenamiento y filtro (resetea a página 1). |

### Restricciones respetadas
- Auth Guard / SPA (`navigateTo`/`renderView`/`mainViews`) intactos: solo se tocaron `loadProducts` y funciones nuevas.
- Dirty check (`catalogFormHasData`/`safeCloseCatalogModal`), `beforeunload`, spinners (`setProductSaving`/`setCategorySaving`), toasts Bootstrap y `confirmModal` sin cambios.
- Paleta RNF24 (`thead-catalog`, `btn-celeste`, `btn-verde`, `btn-outline-rosado`) y validación inline 422 (`translateValidation`/`renderCatalogFieldErrors`) conservadas.
- `#product-detail-modal` usa **backdrop estático** (regla de modales del proyecto).
- Sin `alert()`/`confirm()` nativos.

### Verificación
- `node --check frontend/js/catalog.js`: OK.
- `python -m py_compile` sobre los archivos backend modificados: OK.
- `from app.main import app` / `app.openapi()`: OK (18 rutas); `GET /api/productos` expone `created_from`, `created_to`, `sort_by`, `sort_dir`, `limit`, `offset`.
- Prueba de repositorio contra SQLite en memoria: ordenamiento por `nombre`, `subcategoria`, `precio_detalle` y `stock` (asc/desc) y conteo con filtros, sin errores SQL.
- Nota: `test_*_service.py` siguen apuntando a los modelos pre-DERCAS y fallan en colección; es un pendiente **anterior** a este cambio, no introducido aquí.

### Nota de aplicación
- Entorno nuevo: basta `docker compose up -d db` (usa `init.sql`).
- Entorno con datos: `alembic upgrade head` (desde `backend/`) aplica la columna `fecha_creacion` de `producto`.

---

## [2026-09-15] Módulo de Usuarios: filtros de fecha, paginación reactiva, ordenamiento de columnas y modal de detalle

### Contexto
Mejora del listado de usuarios para manejo de grandes volúmenes de datos: filtros de rango de fecha, paginación con `limit`/`offset`, ordenamiento asc/desc por columnas y un modal informativo de solo lectura. Se conservaron intactos el Auth Guard, el dirty check, el `beforeunload`, el sistema de toasts y la confirmación no nativa (cero `alert()`/`confirm()`).

### Backend (habilitación de filtros de fecha y ordenamiento)
| Archivo | Cambio |
|---------|--------|
| `backend/app/db/models.py` | `Usuario` gana la columna `fecha_creacion` (`DateTime`, `server_default=func.now()`, no nulo) para soportar los filtros de fecha. |
| `database/init.sql` | `usuario` ahora incluye `fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW()`. |
| `backend/alembic/versions/0002_agregar_fecha_creacion_a_usuario.py` | **Nueva migración aditiva** que agrega `fecha_creacion` a `usuario` (preserva datos); aplicable con `alembic upgrade head`. |
| `backend/app/schemas/schemas.py` | `UserFilter` agrega `created_from`, `created_to` (`datetime`) y `sort_by`, `sort_dir` (`asc`/`desc`); `UserResponse` expone `fecha_creacion`. |
| `backend/app/repositories/user_repository.py` | `search`/`count_search` aplican filtros de rango sobre `fecha_creacion` y ordenamiento dinámico sobre columnas permitidas (`id_usuario`, `nombre_completo`, `username`, `estado`, `fecha_creacion`). |
| `backend/app/services/user_service.py` | `list_users`/`count_users` propagan los nuevos parámetros al repositorio. |
| `backend/app/interfaces/repositories.py` | Contratos `search`/`count_search` actualizados con los nuevos parámetros. |

### Frontend (lista interactiva + modal de detalle)
| Archivo | Cambio |
|---------|--------|
| `frontend/index.html` | Dos inputs `type=date` (`#filter-from`, `#filter-to`) en la barra de filtros; cabeceras de tabla ordenables (`th.sortable` con `data-sort`); barra de paginación `#users-pagination` (prev/next, página actual y selector `#users-page-size`); botón "Ver" (ojo) por fila; **nuevo modal `#user-detail-modal`** de solo lectura con `data-bs-backdrop="static"` y `data-bs-keyboard="false"`. |
| `frontend/css/style.css` | Estilos `th.sortable` (cursor puntero, hover y `.sort-icon` para indicadores asc/desc). |
| `frontend/js/users.js` | Estado `usersState` (página, tamaño, total, sort); `loadUsers` envía `created_from`, `created_to`, `sort_by`, `sort_dir`, `limit`, `offset` y usa `data.total`; nuevas funciones `renderPagination()`, `goToPage()`, `toggleSort()`, `updateSortIndicators()` y `viewUserDetail()`; wiring de paginación, ordenamiento y filtro (resetea a página 1). |

### Restricciones respetadas
- Auth Guard / `navigateTo` intactos: solo se tocaron `loadUsers` y funciones nuevas.
- Dirty check (`formHasData`/`safeCloseUserModal`), listener `beforeunload`, `setSaving` con spinner, toasts Bootstrap y `confirmModal` sin cambios.
- `#user-detail-modal` usa **backdrop estático** (regla de modales del proyecto).
- Sin `alert()`/`confirm()` nativos.

### Verificación
- `node --check frontend/js/users.js`: OK.
- `python -m py_compile` sobre los archivos backend modificados: OK.
- `from app.main import app` / `app.openapi()`: OK (18 rutas); `GET /api/usuarios` expone `created_from`, `created_to`, `sort_by`, `sort_dir`, `limit`, `offset`.
- Nota: `test_user_service.py` (y demás `test_*_service.py`) siguen apuntando a los modelos pre-DERCAS (`Role`, `Department`, `UserCreate` antiguo) y fallan en colección; es un pendiente **anterior** a este cambio, no introducido aquí.

### Nota de aplicación
- Entorno nuevo: basta `docker compose up -d db` (usa `init.sql`).
- Entorno con datos: `alembic upgrade head` (desde `backend/`) aplica la columna `fecha_creacion`.

---

## [2026-09-15] Fix de UX — falso positivo al cerrar el formulario de Usuario y posición del diálogo de confirmación

### Contexto
Dos problemas de comportamiento/diseño en el módulo de Usuarios:
1. **Falso positivo en el dirty check:** al abrir "Nuevo Usuario" y pulsar la X o "Cancelar" sin escribir nada, se mostraba "¿Tienes datos sin guardar..." en lugar de cerrar de inmediato.
2. **Posición del diálogo de confirmación:** el modal de confirmación se superponía tapando los campos y quedaba desfasado/cortado respecto al modal de fondo.

### Causa raíz
1. `formHasData()` considera como "datos" cualquier `select` con valor no vacío. En `resetUserForm()` se forzaba `estado = 'Activo'` al abrir el formulario, por lo que el select de estado no estaba vacío y el dirty check creía que había información.
2. `#confirm-modal` compartía el mismo `z-index` (1055) que `#user-modal` abierto; su backdrop (1040) quedaba por debajo del modal de usuario (1055), sin oscurecerlo y superponiendo el diálogo sobre los campos.

### Solución aplicada
| Archivo | Cambio |
|---------|--------|
| `frontend/index.html` | El select `#estado` ahora tiene como valor por defecto un placeholder vacío (`-- Estado --`, value `""`); al abrir un formulario nuevo todos los campos quedan vacíos → se cierra de inmediato. |
| `frontend/js/users.js` | `resetUserForm()` ya no fuerza `estado='Activo'` (depende del `reset()` al placeholder vacío). `saveUser()` solo incluye `estado` en el payload si el usuario eligió una opción (`if (estadoSel.value)`), evitando sobrescribir el valor en edición. `confirmModal()` eleva el `z-index` del diálogo (`2000`) y de su último backdrop (`1990`) para mostrarse centrado, completo y sobre cualquier modal abierto. |
| `frontend/css/style.css` | Regla `#confirm-modal.modal { z-index: 2000; }` como respaldo; se conserva el centrado nativo `modal-dialog-centered`. |

### Verificación
- `node --check frontend/js/users.js`: OK.
- Prueba manual: abrir "Nuevo Usuario" y pulsar X/Cancelar sin escribir → cierra directamente (sin confirmación). Escribir un dato y pulsar X → muestra la confirmación centrada, por encima del modal, completamente visible.

---

### Contexto
Dos incidencias derivadas de la migración Database First (DERCAS):
1. Al aplicar `init.sql` mediante PowerShell, los acentos y eñes de los catálogos semilla se corrompieron (p. ej. `Cristalería` → `Cristaler??a`). Diagnóstico en BD: los caracteres acentuados quedaron como dos bytes `0x3F` (`??`).
2. El backend ya expone el nuevo esquema `Usuario` (`id_usuario`, `id_rol`, `nombre_completo`, `username`, `estado`), pero el frontend de Usuarios seguía esperando los atributos obsoletos (`name`, `lastname`, `code`, `department_id`, `is_active`), lo que pintaba `undefined` y badges incorrectos.

### Incidencia 1 — Caracteres corruptos en BD
Se creó `database/fix_encoding.sql` con los `UPDATE` de los catálogos semilla (`categoria`, `subcategoria`, `producto`) hacia los textos UTF-8 correctos. Se aplicó y verificó contra el contenedor `regalito_db` (resultado: `Cristalería`, `Ropa Bebé`, `Muñecas`, `Vestido de Niña 2T`, `Muñeca de Trapo Artesanal`).

Comando de aplicación (evita el re-corrimiento por el pipe de PowerShell usando `docker cp`, que copia los bytes tal cual):
```powershell
docker cp .\database\fix_encoding.sql regalito_db:/tmp/fix_encoding.sql
docker exec -e PGPASSWORD=Regalito_2026 regalito_db psql -U regalito_admin -d regalito_pos -v ON_ERROR_STOP=1 -f /tmp/fix_encoding.sql
```
Alternativa vía pipe (forzando UTF-8 en PowerShell):
```powershell
$OutputEncoding = New-Object System.Text.UTF8Encoding $false
Get-Content -Raw -Encoding UTF8 .\database\fix_encoding.sql | docker exec -i -e PGPASSWORD=Regalito_2026 regalito_db psql -U regalito_admin -d regalito_pos -v ON_ERROR_STOP=1
```

### Incidencia 2 — Migración del módulo de Usuarios (frontend)
| Archivo | Cambio |
|---------|--------|
| `frontend/index.html` | Tabla de usuarios: columnas **ID / Nombre / Usuario / Rol / Estado** (se elimina la columna Departamento). Filtros: **Nombre / Rol** (dropdown desde `/api/roles`) **/ Estado**. `#user-modal`: campos `nombre_completo`, `username`, `password`, `id_rol` (dropdown) y `estado` (Activo/Inactivo); se eliminó el select de Departamento y el checkbox `is_active`. |
| `frontend/js/users.js` | `loadUsers` mapea `id_usuario`, `nombre_completo`, `username`, `rol.nombre`, y badge con `estado === 'Activo'`. `loadRoles` usa `id_rol`/`nombre`. Nuevo `loadRoleFilter` para el filtro de la tabla. `saveUser` envía claves exactas de `UsuarioCreate`/`UsuarioUpdate` (`nombre_completo`, `username`, `id_rol`, `estado`, y `password` solo en creación o si cambia en edición). `editUser`/`resetUserForm` adaptados. Se eliminaron `DEPARTMENTS_API` y `loadDepartments`. |

Se conservaron intactos los estándares defensivos: `safeCloseUserModal()`, `formHasData()`, listener `beforeunload`, `setSaving` con spinner, toasts Bootstrap, modal de confirmación no nativo y traducción inline de errores 422 con `translateValidation()`.

### Verificación
- `node --check frontend/js/users.js`: OK.
- `grep` en `index.html`: sin IDs obsoletos (`filter-code`, `lastname`, `code`, `role_id`, `department_id`, `is_active`).
- `docker exec ... psql` (SELECT sobre `categoria`, `subcategoria`, `producto`): textos correctos (sin `??`).

---

### Contexto
El login fallaba con "Credenciales incorrectas o usuario inactivo" usando `admin` / `admin123`. La lógica de autenticación (`auth.py`) ya era correcta (consulta por `Usuario.username`, valida `usuario.password_hash` y `usuario.estado == "Activo"`). La **causa raíz** era que el hash bcrypt sembrado en `database/init.sql` **no correspondía a `admin123`** (se verificó que `security.verify_password("admin123", hash_antiguo)` → `False`).

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `database/init.sql` | Hash de los 3 usuarios semilla (`admin`, `cajera`, `bodega`) reemplazado por un hash bcrypt válido de `admin123`. |

### Detalle
- Hash antiguo (no coincide con `admin123`): `$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW`
- Hash nuevo (válido para `admin123`): `$2b$12$igeDz03pyYibOqQO3WJCY.a/XKMHvAAZ2sfh13w.YT7hurdmKFlpG`
- Generado con `security.get_password_hash("admin123")` y verificado con `security.verify_password("admin123", nuevo_hash)` → `True`.

### Verificación
- `python -m py_compile` sobre `backend/app`: OK.
- `from app.main import app`: OK.

### Nota de aplicación
Para la BD actual (sin recrear el contenedor) aplicar en la base de datos:
```sql
UPDATE usuario
SET password_hash = '$2b$12$igeDz03pyYibOqQO3WJCY.a/XKMHvAAZ2sfh13w.YT7hurdmKFlpG'
WHERE username IN ('admin', 'cajera', 'bodega');
```

---

### Contexto
Se eliminaron las referencias obsoletas que impedían a Uvicorn arrancar. Los módulos restantes (Usuarios, Roles, Departamentos y Caja) ahora apuntan a los modelos relacionales de `backend/app/db/models.py` (Database First). `import app.main` ya no lanza excepciones y el OpenAPI se construye (18 rutas).

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `backend/app/schemas/schemas.py` | `Role` → `Rol` (`id_rol`, `nombre`, `descripcion`, `estado`); `Department` → `DepartamentoGeografico` (`id_departamento`, `nombre`); `User*` → `Usuario` (`id_usuario`, `id_rol`, `nombre_completo`, `username`, `estado`); caja → `TurnoApertura`/`TurnoCierre`/`TurnoResponse`. |
| `backend/app/interfaces/repositories.py` | Contratos `RoleRepository`→`Rol`, `DepartmentRepository`→`DepartamentoGeografico`, `UserRepository`→`Usuario` (se quita `get_by_code`; filtros simplificados a `name`/`is_active`/`role_id`). |
| `backend/app/repositories/role_repository.py` | Consultas sobre `Rol` (`id_rol`, `nombre`, `estado`). |
| `backend/app/repositories/department_repository.py` | Consultas sobre `DepartamentoGeografico`. |
| `backend/app/repositories/user_repository.py` | Consultas sobre `Usuario` (`id_usuario`, `nombre_completo`, `id_rol`, `estado`) con `selectinload(Usuario.rol)` (evita `MissingGreenlet`). |
| `backend/app/services/role_service.py` | CRUD sobre `Rol` (soft delete vía `estado="Inactivo"`). |
| `backend/app/services/department_service.py` | CRUD sobre `DepartamentoGeografico`; sin soft delete (el modelo no tiene `estado`). |
| `backend/app/services/user_service.py` | CRUD sobre `Usuario`; valida `id_rol` contra la BD; hashea `password_hash`; soft delete vía `estado`. |
| `backend/app/api/users.py`, `roles.py`, `departments.py` | Import y anotación `Usuario` en `get_current_user`. |
| `backend/app/api/cash_register.py` | Apertura/cierre sobre `TurnoCaja` (`id_caja`, `id_usuario`, `monto_apertura`, `fecha_apertura`, `fecha_cierre`, `estado`); valida existencia de `Caja`. |

### Notas
- `auth.py` y `deps.get_current_user` ya operaban sobre `Usuario` (ajuste previo del módulo de Catálogos).
- `DepartamentoGeografico` no tiene `estado`, por lo que el endpoint de desactivación de departamentos es un no-op (se devuelve el registro).
- El frontend del módulo Usuarios (`frontend/js/users.js`) aún usa la estructura antigua (`name`, `lastname`, `code`, `department_id`, `is_active`); queda pendiente su migración al nuevo `Usuario` en una iteración posterior.

### Verificación
- `python -m py_compile` en todo `backend/app`: OK.
- `python -c "from app.main import app"` / `import app.main`: OK (sin excepciones).
- `app.openapi()`: OK (18 paths).

---

### Contexto
El **Frontend del Módulo de Catálogos** (Productos y Categorías) se refactorizó quirúrgicamente para conectarse a la base de datos relacional reconstruida en Database First. La creación/edición de un producto ahora inserta de forma **anidada y atómica** `Producto -> VarianteProducto -> InventarioSucursal` en una sola petición. Además se **estableció la paleta de colores corporativa oficial** (celeste, rosado y verde — RNF24) para los botones y cabeceras de tabla del módulo.

> Reglas quirúrgicas respetadas: se conservaron intactos el `data-bs-backdrop="static"` de los modales, el Auth Guard y el listener `beforeunload`.

### Componentes modificados (backend)
| Archivo | Cambio |
|---------|--------|
| `backend/app/schemas/schemas.py` | Esquemas anidados `ProductoCreate` (con `variante` y `inventario`), `ProductoUpdate`, `ProductoOut`, `ProductoFilter`, `ProductoList`; catálogos `CategoriaOut`, `SubcategoriaOut`, `UnidadMedidaOut`, `SucursalOut`, `AreaBodegaOut`. Se reemplazaron los antiguos `Product`/`Category`. |
| `backend/app/api/products.py` | `POST /api/productos` recibe el payload anidado; `PUT`/`GET`/`DELETE` y filtros (`name`, `barcode`, `subcategoria_id`, `is_active`) adaptados al nuevo esquema. |
| `backend/app/api/categories.py` | CRUD de Categorías con modelo `Categoria` (`id_categoria`, `nombre`, `estado`). |
| `backend/app/api/catalogos.py` | **Nuevo router** `GET /api/catalogos/{subcategorias,unidades,sucursales,areas}` para poblar los dropdowns (cero datos quemados). |
| `backend/app/services/product_service.py` | Inserción anidada atómica (valida subcategoría, unidad, sucursal y área contra la BD; unicidad de código de barras). |
| `backend/app/services/catalogo_service.py` | **Nuevo** servicio para los catálogos de apoyo. |
| `backend/app/services/category_service.py` | Adaptado al modelo `Categoria`. |
| `backend/app/repositories/product_repository.py` | Repositorio de `Producto`/`VarianteProducto`/`InventarioSucursal` con `selectinload` (evita `MissingGreenlet`) y `add_*` + `commit()` para atomicidad. |
| `backend/app/repositories/category_repository.py` | Adaptado a `Categoria`. |
| `backend/app/interfaces/services.py`, `repositories.py` | Contratos actualizados (incluye nuevo `CatalogoService`). |
| `backend/app/api/deps.py` | `get_product_service` sin inyectar categorías; nuevo `get_catalogo_service`; `get_current_user` sobre `Usuario`. |
| `backend/app/api/auth.py` | Login sobre `Usuario` (`rol`, `estado`). |
| `backend/app/main.py` | Registro del router `catalogos`. |

### Componentes modificados (frontend)
| Archivo | Cambio |
|---------|--------|
| `frontend/index.html` | `#product-modal` rediseñado en secciones **Matriz** (subcategoría, unidad, nombre, descripción), **Variante** (código de barras, talla, color), **Precios** (detalle y mayoreo obligatorios RF05, costo promedio) e **Inventario** (sucursal, área, stock actual y mínimo para alertas RF09). Botones y cabeceras de tabla del módulo con paleta RNF24 (`btn-verde`, `btn-celeste`, `thead-catalog`, acciones `btn-outline-rosado`). |
| `frontend/css/style.css` | Design tokens oficiales: `--color-celeste` `#38BDF8`, `--color-rosado` `#F472B6`, `--color-verde` `#34D399` + clases `.btn-celeste/.btn-rosado/.btn-verde`, `.btn-outline-*` y `.thead-catalog`. |
| `frontend/js/catalog.js` | Payload anidado `ProductoCreate` en una sola petición; población de dropdowns desde `/api/catalogos/*`; área dependiente de la sucursal; listado con la estructura relacional; se mantiene la traducción amigable de errores 422 y el dirty check / beforeunload / SPA. |

### Detalle de la inserción anidada
El payload de creación es un único objeto JSON:
```json
{
  "id_subcategoria": 1, "id_unidad": 1, "nombre": "...", "descripcion": "...",
  "variante": { "codigo_barras": "...", "talla": "...", "color": "...",
                "precio_detalle": 85.00, "precio_mayoreo": 75.00, "costo_promedio": 52.00 },
  "inventario": { "id_sucursal": 1, "id_area": 1, "stock_actual": 24, "stock_minimo": 8 }
}
```
En el backend, `ProductoCreate` valida con Pydantic (errores 422 inline) y el servicio inserta producto → variante → inventario dentro de la misma transacción (`commit()` atómico).

### Verificación
- `python -m py_compile` sobre todos los archivos backend modificados: OK.
- `node --check frontend/js/catalog.js`: sin errores de sintaxis.

### Pendiente / notas (fuera del alcance de esta tarea)
- El módulo **Catálogos** queda completo y consistente con el esquema DERCAS. Sin embargo, la **app aún no importa** porque los módulos de **Roles/Departamentos/Usuarios y Caja (`cash_register.py`)** siguen referenciando los modelos antiguos (`Role`, `Department`, `User`, `CashRegister`) eliminados en la migración Database First. Esa migración de servicios/repositorios de esos módulos queda para una iteración posterior (como ya estaba documentado).
- La pestaña de Categorías quedó sobre `Categoria` (`nombre`, `estado`); el modelo relacional no tiene `description`, por lo que la columna "Descripción" se muestra como `-`.

---

### Contexto
Aplicación del enfoque **Database First** a partir del Diccionario de Datos oficial del DERCAS. Se reconstruyó por completo el esquema de la base de datos (7 módulos, 42 tablas, 214 campos) y se mapeó a modelos SQLAlchemy asíncronos. Solo backend; no se tocaron Frontend ni Controladores.

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `database/init.sql` | Esquema completo (43 tablas DDL) + datos semilla contextualizados al negocio (Cristalería, Ropa, Juguetes, Hogar) |
| `backend/app/db/models.py` | Mapeo de los 43 modelos SQLAlchemy con relaciones (`relationship`) y claves foráneas explícitas |

### 1. Esquema DDL (`database/init.sql`)
- **43 tablas** organizadas en 7 módulos: Seguridad y Auditoría, Sucursales/Ubicación/Clientes, Catálogo e Inventario, Movimientos y Mermas, Caja/Turnos/Tesorería, Ventas/Cobros/Facturación, Compras y Proveedores.
- Tipos de datos exactos (`INT`, `VARCHAR(n)`, `DECIMAL(n,2)`, `DATE`, `TIMESTAMP`), PK y FK respetando el diccionario. Tablas asociativas con PK compuesta (`rol_permiso`).
- **Datos semilla** contextualizados:
  - Roles (Administradora, Cajero, Bodeguero), usuarios iniciales (`admin`/`cajera`/`bodega`, password `admin123`), permisos y `rol_permiso`.
  - Categorías reales: **Cristalería, Ropa, Juguetes, Hogar** (+ subcategorías Vasos, Floreros, Ropa Bebé, Muñecas, Deco Hogar). Unidades de medida (UND, PAR, DOC, CJ).
  - 2+ productos con variantes e inventario: **Juego de Vasos de Cristal**, **Vestido de Niña 2T**, **Muñeca de Trapo Artesanal**, cada uno con `variante_producto` e `inventario_sucursal`.
  - Catálogos de apoyo: sucursal, áreas de bodega, departamentos/municipios, tipos de cliente, proveedores, métodos de pago, denominaciones de efectivo, motivos de merma y tipos de movimiento de caja.

### 2. Modelos SQLAlchemy (`backend/app/db/models.py`)
- Mapeo de los **43 modelos** con `Column` tipado y `ForeignKey` (se mantiene el estilo declarativo del proyecto).
- **Relaciones** bidireccionales clave: `Producto -> VarianteProducto -> InventarioSucursal -> AlertaStock`, `Categoria -> Subcategoria -> Producto`, etc.
- Relaciones con doble FK resueltas explícitamente con `foreign_keys=[...]` (`TrasladoInventario`, `CierreCajaCiegas`).
- Las relaciones se cargan de forma perezosa; el eager loading con `selectinload` (para evitar `MissingGreenlet`) se aplica a nivel de repositorio, igual que el patrón ya usado en `user_repository.py`.

### Verificación
- `configure_mappers()` de SQLAlchemy: **43 modelos** mapeados sin errores.
- `init.sql` con DDL + seeds referencialmente consistentes (FK hacia datos semilla insertados).

### Comando para aplicar la nueva base de datos (limpiar volumen)
```
docker compose down -v
docker compose up -d db
```
> `down -v` borra el volumen `postgres_data` y fuerza a re-ejecutar `database/init.sql` desde cero.

### Pendiente / notas
- Los controladores y repositorios actuales referencian el modelo anterior (`User`, `Role`, `Product`, etc.). Este paso es únicamente DDL+models; la migración de servicios/repositorios a los nuevos nombres (id_*, tablas en snake_case) queda para una iteración posterior, según lo indicado en la tarea.

---

## [2026-09-15] Módulo de Catálogos (Productos y Categorías) — construido sobre la plantilla de Usuarios

### Contexto
Desarrollo del frontend del módulo de **Catálogos** (Productos y Categorías) del POS. Se construyó reutilizando el módulo de **Usuarios** (`frontend/js/users.js` y `#user-modal`) como **plantilla exacta** para garantizar los mismos estándares de calidad, UX defensiva y arquitectura ya resueltos: modales defensivos, validación inline, integración SPA y protección de pérdida de datos. No se repiten errores previos ni se reinventan patrones.

### Componentes creados
| Archivo | Descripción |
|---------|-------------|
| `frontend/js/catalog.js` | Lógica del módulo (Productos + Categorías) siguiendo la plantilla de `users.js` |
| `frontend/index.html` | Vista `#catalog-view` (`data-main-view="catalog"`) con tabs Productos/Categorías, tablas responsivas, estados vacíos, filtros y los modales `#product-modal` / `#category-modal` |

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `frontend/js/app.js` | `mainViews` agrega `catalog` (hash routing); `renderView()` llama a `showCatalogModule()`; `moduleLabels` mapea `catalog` |
| `frontend/js/users.js` | El binding de `[data-bs-close-modal]` se acotó a `#user-modal [data-bs-close-modal]` para no interferir con los modales de catálogos |
| `frontend/index.html` | Enlace del sidebar "Catálogos" (`data-nav="catalog"` + `navigateTo('catalog')`); tarjeta del dashboard (`data-module="catalog"`); `<script src="js/catalog.js">` |

### 1. Estructura HTML (replicando el módulo Usuarios)
- Contenedor principal con `data-main-view="catalog"`.
- **Tabs** Productos / Categorías; cada tab con **tabla responsiva** y su **estado vacío** ("No hay productos/categorías...") que oculta el `table-responsive` cuando no hay registros.
- Modales **defensivos**: `#product-modal` y `#category-modal` con `data-bs-backdrop="static"` y `data-bs-keyboard="false"`.
- `id` de inputs/selects **coinciden con el schema de Pydantic** (`name`, `sku`, `barcode`, `category_id`, `price`, `current_stock`, `min_stock`, `description`); debajo de cada uno su `<div class="invalid-feedback" id="error-{campo}">`.

### 2. Lógica JavaScript (replicando users.js)
- **Integración SPA**: vista registrada en `mainViews` (soporta Hash Routing y recarga de página).
- **Dirty Check**: `catalogFormHasData(formId)` + `safeCloseCatalogModal(formId, modalId)`; los botones "Cancelar" y "X" interceptan el cierre (`data-bs-close-modal`) y piden confirmación estandarizada si hay datos.
- **Unload Guard**: listener `beforeunload` protege contra recargas (F5) con un modal sucio abierto.
- **Micro-interacciones**: limpieza de errores en tiempo real (`input`/`change`), envío con **Enter** (form real) y bloqueo del botón Guardar con **spinner**.
- **Cero alertas nativas**: se reutilizan `showToast()` y `confirmModal()` (globales de `users.js`); se prohíbe `alert()`/`confirm()`.
- **Acceso a campos con ámbito de formulario**: `inputFor(formId, fieldId)`/`feedbackFor(formId, fieldId)` evitan colisiones porque `name` (y otros) se repiten entre formularios.

### 3. Integración con el Backend (API Fetch)
- **Productos** (`/api/productos`): payload actualizado con la migración — `category_id` parseado a entero y `sku` (nulo si vacío), además de `name`, `barcode`, `price`, `current_stock`, `min_stock` y `is_active` en edición.
- **Categorías** (`/api/categorias`): payload con `name`, `description` e `is_active` en edición.
- **Manejo de errores**: `handleCatalogApiError()` reutiliza `translateValidation()` para inyectar los mensajes 422 (Pydantic) en los `.invalid-feedback` y el banner general para errores 400 (p. ej. **SKU/barcode duplicado**).

### Verificación
- `node --check frontend/js/catalog.js`, `frontend/js/app.js` y `frontend/js/users.js`: sin errores de sintaxis.
- Probar en navegador: navegar a Catálogos desde sidebar y dashboard; crear/editar/desactivar productos y categorías; cerrar modales con datos (confirmación) y vacíos (directo); recargar página en `#catalog`; errores 422 inline y 400 en banner.

---

## [2026-09-15] Estandarización y Navegación del Panel Principal (Dashboard)

### Contexto
Refactorización y optimización de la vista del Panel Principal (Dashboard): homologación completa de los accesos directos con la barra lateral, interactividad + navegación SPA y preparación de las tarjetas de KPIs para recibir métricas asíncronas del backend.

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `frontend/index.html` | Cuadrícula "Módulos del Sistema" homologada a 8 módulos con `data-module` + `onclick="openModule(...)"`; etiquetas alineadas al sidebar; tarjetas KPI con `data-metric` e `id="metric-*"` |
| `frontend/js/app.js` | Nueva función `openModule(moduleKey)` que navega si el módulo existe o muestra un toast de "en construcción" para los pendientes |

### 1. Homologación y completitud de accesos directos
La cuadrícula "Módulos del Sistema" ahora refleja exactamente los módulos del menú lateral (8 tarjetas, cuadrícula simétrica `col-6 col-md-4 col-lg-3` = 2 filas de 4):
- POS / Ventas, Inventario / Bodega, Compras, Caja, Usuarios / Personal, Catálogos, **Reportes** (icono `bi-bar-chart-fill`), **Configuración** (icono `bi-gear-fill`).

### 2. Interactividad y navegación SPA
- Tarjetas convertidas en `<button>` clicables con cursor puntero y microinteracción hover (`module-btn:hover`: elevación y borde teal).
- `openModule(moduleKey)`:
  - Módulo existente (p. ej. `users`): llama a `navigateTo('users')` → conmuta la vista, sincroniza el hash en la URL y marca como activo el elemento del sidebar.
  - Módulos en desarrollo (Reportes, Caja, Compras, etc.): muestra un **toast** "El módulo X se encuentra en construcción" (`showToast`, tipo `info`), sin cambiar de pantalla ni dejar la interfaz congelada.

### 3. KPIs y métricas resumidas
- Cada tarjeta superior (Ventas, Stock, Cuentas, Clientes) cuenta con `data-metric` y un `<h3 id="metric-*">` listos para recibir datos asíncronos cuando se conecte el endpoint de métricas del backend.

### Verificación
- `node --check frontend/js/app.js`: sin errores de sintaxis.
- Probar en navegador: clic en "Usuarios / Personal" navega y activa el sidebar; clic en Reportes/Caja muestra toast de "en construcción"; KPIs con ids únicos.

---

## [2026-09-15] Persistencia de Ruta en Recarga (Hash Routing SPA)

### Contexto
Mejora del sistema de enrutamiento SPA para que la aplicación conserve la vista activa tras recargar la página, sincronizando la URL (hash) con la vista en pantalla y soportando los botones de avance/retroceso del navegador.

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `frontend/js/app.js` | Hash routing: `parseHash()`, `renderView()`, `navigateTo()` actualiza `location.hash`, listener `hashchange`; `showDashboard()` restaura la vista desde la URL |

### 1. Sincronización de la URL con la vista activa
- `navigateTo(viewKey)` actualiza `location.hash` (p. ej. `#usuarios`, `#dashboard`) **sin recargar** la página. Si el hash ya coincide con la vista solicitada, renderiza directamente.

### 2. Restauración de vista al inicializar
- Tras confirmar la sesión activa (Auth Guard), `showDashboard()` lee el hash con `parseHash()` y llama a `renderView()`.
- `parseHash()`: lee el identificador del hash; si es una vista válida (`mainViews`) navega a ella y activa su elemento en el sidebar; si está vacío, es la raíz o una ruta desconocida, normaliza al **Panel Principal** (`dashboard`).

### 3. Soporte de navegación del navegador
- Listener `hashchange`: al avanzar/retroceder con los botones del navegador, sincroniza la vista en pantalla con la nueva ruta (conmutando contenedores y `setActiveNav()`).
- `renderView()` evita doble renderizado (guard `currentView`) para que `hashchange` no recargue módulos duplicadamente.

### 4. Directriz para futuros módulos
> **Persistencia de Ruta en Recarga (Hash Routing SPA):** todo módulo nuevo debe soportar restauración automática de vista al refrescar el navegador, agregando su clave al arreglo `mainViews` en `frontend/js/app.js` (con su contenedor `[data-main-view]` y enlace del sidebar `[data-nav]`). El enrutado SPA queda a cargo de `navigateTo()`/`renderView()`.

### Verificación
- `node --check frontend/js/app.js`: sin errores de sintaxis.
- Probar en navegador: con sesión activa navegar a Usuarios y recargar (debe restaurar Usuarios); botones atrás/adelante sincronizan la vista; hash vacío/desconocido carga el Panel Principal.

---

## [2026-09-15] Auth Guard + Navegación SPA con sincronización del Sidebar

### Contexto
Refactorización funcional de la navegación del sistema y del control de acceso en el frontend: se añadió un **Auth Guard** que valida la sesión antes de renderizar cualquier vista administrativa, un manejo global de respuestas **401** y una navegación SPA centralizada que conmuta contenedores y sincroniza el elemento activo del menú lateral.

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `frontend/index.html` | Vistas marcadas con `data-main-view` (`dashboard`, `users`); enlaces del sidebar con `data-nav` + `onclick="navigateTo(...)"`; el botón "← Panel" usa `navigateTo('dashboard')` |
| `frontend/js/app.js` | `hasActiveSession()`, `showLogin()`, `handleUnauthorized()`, interceptor global de `fetch` para 401, `navigateTo()`, `setActiveNav()`; logout usa `showLogin()` |
| `frontend/js/users.js` | `showUsersModule()` se reduce a cargar datos (la conmutación la maneja `navigateTo`); `goToDashboard()` delega en `navigateTo('dashboard')` |

### 1. Control de acceso y redirección (Auth Guard)
- **Al inicializar** la app (`DOMContentLoaded`): si existe `jwt_token` → `showDashboard()`; si no → `showLogin()` (se oculta el sistema y se muestra el Login por defecto, impidiendo el renderizado del Panel y de submódulos).
- **`navigateTo()`** también valida la sesión: sin sesión activa fuerza `showLogin()` (defensa en profundidad).
- **Manejo 401**: interceptor global de `fetch` detecta cualquier respuesta 401 (excepto el propio login) → `handleUnauthorized()` limpia la sesión local y muestra el Login de inmediato. Aplica a todas las peticiones de `users.js` de forma transversal.

### 2. Navegación interna y sincronización visual (SPA)
- **`navigateTo(viewKey)`**: conmuta la visibilidad de los contenedores `[data-main-view]` y llama a `setActiveNav()`.
- **`setActiveNav()`**: resalta únicamente el módulo en pantalla (`nav-link.active` + `text-white` + `aria-current`) y desmarca "Panel Principal" al ir a "Usuarios / Personal" y viceversa.
- **Retorno al Panel**: tanto el enlace del sidebar (`data-nav="dashboard"`) como el botón "← Panel" del módulo de usuarios ejecutan `navigateTo('dashboard')`.
- **Sin recargas**: las transiciones conmutan clases `d-none` entre contenedores sin recargar la página ni alterar la URL.

### 3. Reglas estándar globales para futuros módulos
> **a) Regla de Seguridad:** ninguna vista administrativa debe mostrarse sin comprobación previa de sesión activa (validar `jwt_token` y delegar en el Auth Guard `hasActiveSession()`/`navigateTo()`).

> **b) Regla de Navegación SPA:** todo cambio de módulo debe gestionar obligatoriamente la conmutación de contenedores (`[data-main-view]`) y la actualización dinámica del elemento activo en el menú lateral (`setActiveNav()`), usando la función central `navigateTo()`.

### Verificación
- `node --check frontend/js/app.js` y `node --check frontend/js/users.js`: sin errores de sintaxis.
- Probar en navegador: sin token → Login; con token → Panel (nav activa); navegar a Usuarios y volver al Panel; expirar/invalidar token → redirección automática a Login.

---

## [2026-09-15] Resiliencia de Datos de Entrada (Unload Guard & Modal Trigger Alignment)

### Contexto
Corrección de la inconsistencia en el control de cierre del modal de usuarios y adición de una capa de defensa a nivel de ventana del navegador para evitar la pérdida no intencional de datos ante recargas o cierres de pestaña accidentales.

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `frontend/index.html` | Homologación del `.btn-close` del header: se confirmó que usa `data-bs-close-modal` (firma del selector que enlaza `safeCloseUserModal()`) y no contiene `data-bs-dismiss="modal"`. |
| `frontend/js/users.js` | Nuevo listener global `beforeunload` que interrumpe la salida solo si el modal está desplegado (`#user-modal.show`) y `formHasData()` retorna `true`. |

### 1. Alineación del disparador en cabecera
- El botón `.btn-close` del `#user-modal` usa `data-bs-close-modal`, la misma firma de selector que enlaza `safeCloseUserModal()` en `DOMContentLoaded`, compartiendo idéntico comportamiento defensivo que el botón "Cancelar".
- Se garantiza que NO posee el atributo nativo `data-bs-dismiss="modal"`.

### 2. Guardia de ciclo de vida (beforeunload)
- Se registra `window.addEventListener('beforeunload', ...)` que previene navegación/recarga/cierre de pestaña.
- La alerta del navegador solo se activa si: el modal está visible (`#user-modal` con clase `show`) **y** `formHasData()` es `true`.
- Emplea el estándar defensivo: `event.preventDefault()` + `event.returnValue = ''` para compatibilidad con navegadores modernos.

### 3. Regla obligatoria para formularios transaccionales
> **Regla obligatoria para formularios transaccionales:** todo módulo con captura modal debe enlazar transversalmente los controles de salida (`.btn-close`, botones cancelar) a la rutina de verificación de cambios sucios (dirty check) e integrar el listener `beforeunload` para salvaguardar el estado frente a recargas o cierres de pestaña accidentales.

### Verificación
- `node --check frontend/js/users.js`: sin errores de sintaxis.
- Probar en navegador: abrir modal, ingresar datos y recargar/cerrar pestaña (debe aparecer la alerta del navegador); con modal vacío o cerrado no debe interrumpirse la navegación.

---

## [2026-09-15] Protección contra pérdida de datos en Modales (Static Backdrop y Dirty Form Check)

### Contexto
Implementación de una política estricta de protección de formulario en el modal de Usuarios para prevenir la pérdida accidental de datos capturados al cerrar el modal (clic exterior o tecla Escape) o al pulsar los botones de cierre/cancelar.

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `frontend/index.html` | `#user-modal` ahora usa `data-bs-backdrop="static"` y `data-bs-keyboard="false"` (no cierra con clic exterior ni Escape). Se eliminó `data-bs-dismiss="modal"` del botón "X" (`.btn-close`) y del botón "Cancelar", reemplazado por `data-bs-close-modal` para control manual. |
| `frontend/js/users.js` | Nuevas funciones `formHasData()` y `safeCloseUserModal()`; wiring de los botones `[data-bs-close-modal]` en `DOMContentLoaded`. |

### 1. Bloqueo de cierre accidental (backdrop estático)
- `data-bs-backdrop="static"`: el modal ya no se cierra al hacer clic en el fondo oscuro.
- `data-bs-keyboard="false"`: el modal ya no se cierra con la tecla **Escape**.

### 2. Confirmación defensiva al cerrar
- Se removió el cierre nativo `data-bs-dismiss="modal"` del botón "X" y de "Cancelar" para controlar el evento manualmente mediante `[data-bs-close-modal]`.
- **`formHasData()`**: recorre los campos `input[type=text]`, `input[type=password]`, `textarea` y `select`; devuelve `true` si algún valor tiene texto (`value.trim().length > 0`).
- **`safeCloseUserModal()`**:
  - Si el formulario está **completamente vacío**, cierra el modal de inmediato y limpia errores.
  - Si **contiene datos**, despliega la confirmación no nativa: *"¿Tienes datos sin guardar. ¿Deseas descartar los cambios y salir?"*.
  - Solo al confirmar: `form.reset()`, se remueven las clases `is-invalid`, se vacían los `.invalid-feedback` y se cierra el modal con `modalInstance.hide()`.

### 3. Regla global para futuros módulos (Ventas, Compras, Inventario)
> **Regla estándar de diseño:** Todo modal con formulario de captura debe usar **backdrop estático** (`data-bs-backdrop="static"` + `data-bs-keyboard="false"`) y **confirmación condicional de descarte** si contiene campos completados, replicando `formHasData()` + `safeCloseUserModal()` de `frontend/js/users.js`.

### Verificación
- `node --check frontend/js/users.js`: sin errores de sintaxis.
- Probar en navegador: abrir modal (crear), hacer clic en el fondo y pulsar Escape (no debe cerrar), ingresar datos y pulsar Cancelar/X (debe pedir confirmación), y cerrar con el formulario vacío (debe cerrar al instante).

---

## [2026-09-14] Auditoría y Mejoras de UX/UI Nivel Empresarial (Módulo de Usuarios)

### Contexto
Auditoría completa del módulo de Usuarios (`frontend/js/users.js` y `frontend/index.html`) para elevarlo a un estándar empresarial: micro-interacciones, programación defensiva y notificaciones no intrusivas.

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `frontend/index.html` | Formulario convertido a **modal Bootstrap** (`#user-modal`); tabla a todo lo ancho con **estado vacío**; **contenedor de Toasts** (`#toast-container`); **modal de confirmación** (`#confirm-modal`); botón Guardar con spinner |
| `frontend/js/users.js` | Micro-interacciones, bloqueo de guardado, Toasts, confirmación no nativa, estado vacío, reseteo al cerrar modal |

### 1. Interacciones fluidas (micro-interacciones)
- **Limpieza de errores en tiempo real**: `initRealtimeValidation()` agrega listeners `input`/`change` a cada campo para remover `is-invalid` y vaciar su `.invalid-feedback` al teclear.
- **Soporte Enter**: el formulario vive dentro de un `<form>` real en el modal, por lo que presionar **Enter** en cualquier campo dispara el `submit` (`saveUser`).
- **Autofocus**: al abrir el modal (crear), se enfoca el primer campo (`name`) tras la transición (`setTimeout`).
- **Reseteo impecable al cerrar**: el evento `hidden.bs.modal` de `#user-modal` ejecuta `resetUserForm()`, que hace `form.reset()`, limpia errores/banner, reinicia el título, obliga la contraseña y recarga los dropdowns (sin dejar rastro de datos anteriores).

### 2. Prevención de errores (Defensive Programming)
- **`.trim()` automático** en `username`, `name`, `lastname` (y `code`) antes de armar el payload para evitar espacios vacíos accidentales.
- **Bloqueo del botón Guardar**: `setSaving(true)` deshabilita `#btn-save-user`, muestra un **spinner de Bootstrap** y cambia el texto a "Guardando...", previniendo dobles clics; se restaura en `finally`.

### 3. Notificaciones y estados (cero alertas nativas)
- **Toasts de Bootstrap**: `showToast(message, type)` reemplaza todo `alert()` de éxito/error; los mensajes se muestran arriba a la derecha y se auto-ocultan (~3.5 s).
- **Confirmación no nativa**: `confirmModal(message)` reemplaza `confirm()` para la desactivación de usuarios (modal de confirmación estética).
- **Estado vacío**: `#users-empty` muestra "No hay usuarios registrados" con icono cuando la tabla no tiene filas (se oculta el `table-responsive`).

### Verificación
- `node --check frontend/js/users.js`: sin errores de sintaxis.
- IDs del HTML únicos (formulario modal, toasts y confirmación sin duplicados).
- Probar en navegador: crear/editar usuario (modal + Enter + spinner), cerrar modal sin datos residuales, desactivar con confirmación y listado vacío.

---

## [2026-09-14] Frontend Usuarios: traductor de mensajes de error de Pydantic

### Contexto
Se agregó en el frontend un **traductor de mensajes de validación de Pydantic** dentro de `translateValidation()`, para que el usuario final vea advertencias en español (p. ej. "Este campo es obligatorio") en lugar de los textos en inglés por defecto del backend, al procesar errores 422 (`errorData.detail`).

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `frontend/js/users.js` | Ampliación de `translateValidation()` con las traducciones específicas solicitadas |

### Detalle de la solución
Se intercepta `err.msg` en el procesamiento de errores 422 y se aplican, en orden:
1. Si `err.msg` es **exactamente** "String should have at least 1 character" → **"Este campo es obligatorio."**.
2. Si `err.msg` **incluye** "String should have at least" y "characters" → se reemplaza por **"Debe tener al menos [N] caracteres."** (extrayendo `N` de la cadena).
3. Si `err.msg` **incluye** "Input should be a valid integer" o "valid integer" → **"Seleccione una opción válida."** (útil para los selects de rol/departamento sin selección).
4. Se conservan otras traducciones útiles ("Field required", "at most", "match pattern", etc.).

El resultado se asigna al `.invalid-feedback` correspondiente (validación inline).

### Verificación
- `node --check frontend/js/users.js`: sin errores de sintaxis.
- Probar manualmente en el navegador: crear usuario con contraseña corta, con rol sin seleccionar y con campos vacíos.

---

## [2026-09-14] Frontend Usuarios: Validación visual inline con Bootstrap

### Contexto
Se reemplazaron los `alert()` nativos del navegador por **validación visual inline con Bootstrap** en el formulario de Usuarios, mejorando la experiencia de usuario (UX): los errores 422 de FastAPI/Pydantic se muestran debajo de cada campo y los errores 400 en un banner general.

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `frontend/index.html` | IDs de campos alineados a Pydantic (`name`, `lastname`, `code`, `username`, `password`, `role_id`, `department_id`, `is_active`); contenedores `.invalid-feedback` debajo de cada campo; banner `#user-form-alert` |
| `frontend/js/users.js` | `clearValidationErrors()`, `renderFieldErrors()`, `showFormBanner()`, traducción de mensajes; se eliminaron los `alert()` nativos |

### Detalle de la solución
1. **IDs coincidentes con Pydantic**: cada `<input>`/`<select>` usa el mismo `id` que la clave del schema backend (ej. `id="name"`, `id="password"`, `id="code"`). Debajo de cada uno hay un `<div class="invalid-feedback" id="error-{campo}">`.
2. **`clearValidationErrors()`**: remueve la clase `is-invalid` de todos los `.form-control`/`.form-select` del formulario, vacía el texto de los `.invalid-feedback` y oculta el banner. Se ejecuta siempre al inicio de `saveUser()`, `editUser()` y `resetUserForm()`.
3. **Errores 422 (Pydantic)**: se recorre `errorData.detail`; por cada `err` se extrae el campo (`err.loc[err.loc.length - 1]`), se busca el elemento por su `id`, se le agrega `is-invalid` y se coloca `err.msg` en su `.invalid-feedback` (con traducción al español de mensajes comunes vía `translateValidation()`).
4. **Errores 400 (p. ej. usuario/código duplicado)**: se muestran en el banner general `#user-form-alert` (clase `alert alert-danger`) encima del formulario.
5. **Sin `alert()` nativos**: los mensajes de éxito también usan el banner (`alert alert-success`).

### Traducciones implementadas (ejemplos)
- "String should have at least 6 characters" → "Debe tener al menos 6 caracteres"
- "Field required" → "Este campo es obligatorio"
- "Input should be a valid integer" → "Debe ser un número entero"

### Verificación
- `node --check frontend/js/users.js`: sin errores de sintaxis.
- Los IDs del formulario en `index.html` coinciden con los campos y contenedores de error usados en `users.js`.
- Probar manualmente en el navegador: crear/editar usuario con contraseña corta (error inline) y con código duplicado (banner general).

---

## [2026-09-14] Frontend Usuarios: manejo de errores y validaciones

### Contexto
Se mejoró `frontend/js/users.js` para presentar errores de forma amigable y garantizar que los datos enviados coincidan exactamente con el schema Pydantic del backend.

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `frontend/js/users.js` | Manejo de errores amigable, tipado de enteros y formato de payload consistente |

### Detalle de la solución
1. **Errores amigables (sin `[object Object]`)**: nueva función `getApiErrorMessage(res, errorData)`.
   - **422 (FastAPI/Pydantic)**: si `errorData.detail` es un arreglo, recorre cada `err`, extrae el campo con `err.loc[err.loc.length - 1]` y su causa con `err.msg`, y los muestra como un listado legible ("• campo: causa"). Se aplica en `loadRoles`, `loadDepartments`, `loadUsers`, `editUser`, `saveUser` y `deactivateUser`.
   - **400 (u otro con `detail` de texto)**: muestra directamente `errorData.detail` (p. ej. "Ya existe un usuario con ese código").
   - Fallback: mensaje genérico si no hay `detail` parseable. Nunca se muestra un objeto serializado.
2. **Tipado y consistencia de datos**:
   - `role_id` y `department_id` se convierten explícitamente a entero con `parseInt(..., 10)`.
   - El payload JSON usa exactamente las claves del schema Pydantic del backend (`schemas.py`): `username`, `password`, `name`, `lastname`, `code`, `role_id`, `department_id`, `is_active`.
   - En **edición**, si la contraseña va vacía se **excluye del payload** (`if (password) payload.password = password`) para no sobrescribirla ni provocar un error de validación. En creación la contraseña siempre se envía.
   - `is_active` se envía en edición desde el checkbox; en creación se fija en `true`.

> **Nota de desalineación corregida:** el requerimiento citaba claves `first_name`, `last_name`, `employee_code`, pero el schema real del backend usa `name`, `lastname`, `code`. Se mantuvo el schema real para no romper la validación de Pydantic.

### Verificación
- No hay cambios de lógica backend; solo frontend. Se recomienda probar manualmente el flujo de crear/editar usuario y los errores 422/400 en el navegador.

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