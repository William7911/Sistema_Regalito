# Registro de Cambios

## Regla de documentación (obligatoria)
Cualquier cambio futuro en el proyecto debe quedar documentado en esta carpeta `/documentacion`. Agrega una entrada en este archivo (`cambios.md`) cada vez que modifiques, crees o elimines componentes.

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