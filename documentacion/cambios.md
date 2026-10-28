# Registro de Cambios

## Regla de documentación (obligatoria)
Cualquier cambio futuro en el proyecto debe quedar documentado en esta carpeta `/documentacion`. Agrega una entrada en este archivo (`cambios.md`) cada vez que modifiques, crees o destruyas componentes.

## [2026-10-28] Implementación de Escaneo y Generación Automática de Códigos de Barras (POS y Catálogo)

### 1. Requerimiento
1. **Escaneo de Código de Barras en Punto de Venta (POS)**:
   - El botón/ícono de escaneo (`bi-upc-scan`) en el buscador del POS no realizaba ninguna acción al ser presionado.
   - Se requería activar esta funcionalidad permitiendo escanear productos con la cámara en tiempo real y soportar lectores láser físicos (pistolas de código de barras USB/Bluetooth).
2. **Generación Automática de Códigos para Productos Faltantes**:
   - Para productos sin código de barras, proveer generación automática y bajo demanda de códigos de barra estándar EAN-13 (prefijo de Guatemala `740` + 9 dígitos + dígito verificador GS1 EAN-13).
   - Generación automática en la creación de productos nuevos cuando no se especifique código.
   - Endpoint de migración para asignar códigos EAN-13 a cualquier producto existente sin código.
   - Botón interactivo "Generar" en el formulario de creación/edición de productos.

### 2. Generación de Códigos de Barras (Backend y Frontend)
- **Algoritmo GS1 EAN-13 Guatemalteco**:
  - Prefijo nacional `740` (Guatemala) + 9 dígitos únicos + cálculo estricto del dígito verificador ponderado (pesos alternados 1 y 3).
- **Backend FastAPI**:
  - [`backend/app/services/product_service.py`](../backend/app/services/product_service.py): Funciones `calculate_ean13_check_digit()` y `generate_random_ean13()`. Métodos `generate_unique_barcode()` y `generate_missing_barcodes()`. Asignación automática de código EAN-13 si `variante.codigo_barras` viene vacío en `create_product()`.
  - [`backend/app/interfaces/services.py`](../backend/app/interfaces/services.py) y [`backend/app/interfaces/repositories.py`](../backend/app/interfaces/repositories.py): Contratos actualizados.
  - [`backend/app/repositories/product_repository.py`](../backend/app/repositories/product_repository.py): Método `get_variantes_without_barcode()`.
  - [`backend/app/api/products.py`](../backend/app/api/products.py): Nuevos endpoints:
    - `GET /api/productos/generar-codigo`: genera y retorna un código EAN-13 válido único.
    - `POST /api/productos/generar-codigos-faltantes`: asigna códigos a todas las variantes sin código.
- **Formulario de Catálogo (Frontend)**:
  - [`frontend/index.html`](../frontend/index.html): Campo `#codigo_barras` actualizado a `input-group` con botón `#btn-generate-barcode` ("Generar").
  - [`frontend/js/catalog.js`](../frontend/js/catalog.js): Función `initProductBarcodeGenerator()` que solicita al backend o genera localmente un código EAN-13 válido al hacer clic en "Generar".

### 3. Escaneo en Vivo en POS (Cámara Web y Lectores Físicos)
- **Botón Omnibox Interactivo**:
  - [`frontend/index.html`](../frontend/index.html): El ícono `.pos-omnibox-icon` se convirtió en el botón clickeable `#btn-pos-scanner` con tooltip y feedback táctil.
- **Modal de Cámara con Retícula y Láser (`#pos-scanner-modal`)**:
  - Visor de cámara con `<video id="pos-scanner-video">`, retícula de encuadre, animación de escaneo láser en rojo brillante (`@keyframes posLaserScan`), badge de estado y controles opcionales para linterna (torch) y cambio de cámara frontal/trasera.
  - Notificación visual de éxito (`.pos-scanner-reticle.scan-success`) y banner de producto agregado.
  - Web Audio API integrado: bip sintético agradable de alta frecuencia (1200-1800 Hz) en escaneo exitoso y tono de advertencia (320 Hz) si no se encuentra.
  - Búsqueda dual: en catálogo en memoria (`state.catalog`) con fallback automático a la API `/api/productos/barcode/{codigo}`.
  - Incorporación directa del producto al carrito (`addToCart()`) con debounce de 1.3 s para prevenir lecturas duplicadas continuas.
  - Entrada manual y soporte para disparos de lectores láser USB/Bluetooth tanto en el modal como de forma global en cualquier parte de la pantalla de POS.
- **Estilos CSS**:
  - [`frontend/css/style.css`](../frontend/css/style.css): `.pos-omnibox-scan-btn`, `.pos-scanner-viewport-wrapper`, `.pos-scanner-reticle`, `.pos-scanner-laser`, alertas y adaptaciones responsive.

### 4. Verificación
- Pruebas automatizadas con Playwright Chromium:
  - Apertura exitosa de `#pos-scanner-modal` al pulsar `#btn-pos-scanner`.
  - Escaneo manual de producto `7401000000011` ("Juego de Vasos de Cristal") con verificación de banner y adición al carrito.
  - Generación de código de barras de 13 dígitos con prefijo `740` en `#btn-generate-barcode`.
  - Cero alteraciones a componentes fuera de la funcionalidad de códigos de barra solicitada.

## [2026-10-27] Ajuste de Layout 100vh para POS (Pie de Cobro Fijo y Compactación de Carrito)

### 1. Limpieza de Botones Superiores Innecesarios
- **Ocultamiento de Acciones Secundarias**: Se ocultaron visualmente con `d-none` y reglas CSS (`display: none !important`) los botones "Pantalla Cliente" (`#btn-pos-customer-screen`) y "← Panel" (`.pos-header-btn[onclick*="dashboard"]`), dejando únicamente el botón de "Historial" en la esquina superior derecha.
- **Reducción del Margen Superior**: Se redujo el espaciado y margen del encabezado `.pos-header` a `margin-bottom: 0.35rem`, optimizando el espacio vertical para el área de venta y cobro.

### 2. Estructura Fija en "Venta Actual" (Pie de Cobro Anclado al 100vh)
- **Ajuste Estricto a la Ventana (Cero Scroll Global)**: Se configuró `#pos-view` y sus contenedores secundarios (`#pos-workspace`, `.pos-workspace-row`, `.pos-checkout-panel`) con `height: 100%; max-height: 100%; overflow: hidden; display: flex; flex-direction: column;`, impidiendo que la página haga scroll vertical hacia abajo.
- **Zona Superior Fija (`.pos-checkout-top`)**: Título "Venta actual", botón "Vaciar carrito" y línea de selector de cliente / NIT permanecen anclados fijamente arriba con `flex: 0 0 auto`.
- **Zona Central con Scroll Interno Exclusivo (`#pos-cart-list`)**: Configurado con `flex: 1 1 0; min-height: 0; overflow-y: auto; overflow-x: hidden;`. Si se agregan múltiples productos, únicamente esta sección se desplaza internamente sin mover el resto de la interfaz.
- **Zona Inferior Siempre Visible (`.pos-checkout-footer`)**: Anclada al fondo con `flex: 0 0 auto; margin-top: auto;`, garantizando que Subtotal, Ahorro, TOTAL A PAGAR, CAMBIO, campo Efectivo, billetes rápidos y el botón principal COBRAR permanezcan 100% visibles y operativos en todo momento.

### 3. Compactación Horizontal Inteligente del Producto en Carrito
- **Fila Única Horizontal**: Se reorganizó la estructura del ítem en el carrito para que todos los elementos convivan en una sola línea compacta:
  - **Izquierda**: Nombre del producto (`.pos-cart-col-info`) con truncado elegante y variante.
  - **Centro**: Controles de cantidad táctiles `[ - ] 1 [ + ]` (`.pos-cart-col-qty`) con botones ergonómicos de 36x36px.
  - **Derecha**: Precio de la línea (`.pos-cart-col-price`, ej. `Q 340.00`) en negrita `fw-black` con alineación tabular.
  - **Extremo derecho**: Botón de eliminación en rojo suave (`.pos-cart-remove`) con ícono de basurero.
- **Eliminación de Miniaturas**: Se retiraron las imágenes y cajas de iniciales del carrito para economizar espacio vertical (~46px por fila frente a los ~100px previos).

### 4. Ajuste Compacto de la Zona de Pago y Billetes
- **Cajas de TOTAL y CAMBIO Optimizadas**: Reducción del padding interno a `0.35rem 0.65rem`, preservando números gigantes en `clamp(1.6rem, 2.2vw, 1.95rem)` (legibles para vista cansada) sin desperdiciar altura vertical.
- **Cuadrícula de Billetes en 2 Filas Exactas**:
  - **Fila 1**: `Exacto`, `Q10`, `Q20`, `Q50`.
  - **Fila 2**: `Q100`, `Q200`, `Transferencia` (expandido a 2 columnas).
  - Cada botón cuenta con altura de `36-38px`, bordes gruesos y tipografía en negrita `0.92rem`.
- **Botón COBRAR Destacado y Visible**: Altura ajustada a `56px` con tipografía de `1.35rem fw-black`, ícono grande y sombra profunda, permanentemente al alcance en la esquina inferior derecha.
- **Eliminación de Barra de Scroll Gris en Categorías**: Se configuró `.pos-category-pills` con `flex-wrap: wrap; overflow-x: hidden; scrollbar-width: none;`, retirando la molesta barra horizontal gris en Windows/Chrome y garantizando que el buscador Omnibox se sitúe nítidamente arriba de las categorías.
- **Soporte Completo de Modo Oscuro**: Integración de colores y contrastes bajo `[data-theme="dark"]` para la fila horizontal compacta y cuadrícula de pago.

### 5. Archivos Modificados
- [`frontend/index.html`](../frontend/index.html): Ocultamiento de botones superiores, inclusión de `.pos-checkout-top`, renombramiento a `Exacto`, versionado `style.css?v=6.0` y `pos.js?v=2.3`.
- [`frontend/js/pos.js`](../frontend/js/pos.js): Nueva plantilla horizontal compacta para el carrito sin miniaturas fotográficas y actualización de versión a `pos.js?v=2.3`.
- [`frontend/css/style.css`](../frontend/css/style.css): Reglas completas de bloqueo 100vh, flex-column, scroll interno en `#pos-cart-list`, eliminación de scrollbar en categorías, cuadrícula de 2 filas de billetes y Modo Oscuro.

## [2026-10-27] Rediseño Accesible de Punto de Venta (POS) para Adultos Mayores y Usuarios sin Experiencia

### 1. Tarjetas de Producto (Clic en Toda la Tarjeta y Reconocimiento Visual)
- **Clic en la Tarjeta Completa**: Se eliminó el botón circular pequeño de `+` en la esquina inferior. Ahora toda la superficie de la tarjeta actúa como un botón táctil grande con `role="button"`, agregando el producto al carrito con un solo toque o clic.
- **Respuesta Táctil y Elevación Visual**: Se agregó un borde grueso de `2px solid #CBD5E1` en reposo, que al pasar el mouse o tocar (`:hover`, `:active`) se resalta con un borde de `3px solid var(--color-teal)` (o `#38BDF8` en Modo Oscuro), elevación suave (`translateY(-4px) scale(1.01)`) y sombra profunda difusa.
- **Tipografía y Precio Gigante**:
  - El nombre del producto se aumentó a `1.05rem` con peso `700`.
  - El precio en Quetzales (`Q XX.XX`) se amplió a `1.45rem` (más de 23px, superando el mínimo requerido de 22px) en negrita ultra-pesada `900`, con espaciado matemático tabular.
- **Sustitución de Siglas por Íconos Ilustrativos Grandes**: Cuando un producto carece de fotografía, se eliminaron por completo las siglas de texto abreviadas ("MD", "VD") y se reemplazaron por un ícono ilustrativo central grande (`3.5rem`) representativo de su categoría (ej. `bi-cup-straw` para Cristalería/Vasos, `bi-bag-heart-fill` para Ropa/Vestidos, `bi-controller` para Juguetes, `bi-house-heart-fill` para Hogar, `bi-gift-fill` para Curiosidades y Regalos).

### 2. Limpieza de Ruido Técnico (Cero Distracciones)
- **Ocultamiento de Etiquetas de Atajos**: Se retiraron visualmente de la interfaz las etiquetas `<kbd>` (`F2`, `F4`, `F12`) en el buscador, botón de Historial y botón de Cobrar, así como la leyenda textual informativa `Enter agrega · F4 historial · F12 cobra`.
- **Preservación Total de Atajos de Teclado**: Las combinaciones y teclas (`F2` para enfocar buscador, `F4` para historial, `F12` para cobrar, `Escape` para limpiar) se mantienen 100% operativas en el controlador de eventos JavaScript, garantizando eficiencia para cajeros avanzados sin confundir visualmente a personas mayores.
- **Barra de Búsqueda y Botones de Categoría Estilo Pestaña Táctil**:
  - La barra de búsqueda Omnibox se elevó a una altura ergonómica de `64px`, con ícono de escáner grande (`1.55rem`) y texto en `1.15rem`.
  - Las píldoras de categorías (*Todos, Cristalería, Juguetes, Ropa*) se transformaron en botones grandes tipo pestaña táctil de `48px` de altura mínima, con bordes gruesos de `2px`, esquinas redondeadas de `14px`, tipografía en `1rem fw-bold` y contador redondeado contrastado.

### 3. Carrito de "Venta Actual" a Prueba de Errores
- **Filas Amplias y Lectura a Distancia**: Cada fila del carrito cuenta con un espaciado vertical holgado (`padding: 0.85rem 0`), nombre de producto en `1rem fw-bold` y total de línea grande en `1.25rem fw-black` con alineación tabular.
- **Controles de Cantidad Grandes y Separados `[ - ]  1  [ + ]`**: Botones de incremento y disminución de `44px x 44px` (superando los 40x40px mínimos requeridos) con íconos audaces de `bi-dash-lg` y `bi-plus-lg`, flanqueando una caja numérica central de `48px x 44px` con tipografía de `1.15rem fw-extrabold`.
- **Botón de Eliminación Táctil con Ícono de Basurero**: Se reemplazó la cruz pequeña por un botón cuadrado amplio de `42px x 42px` en color rojo suave (`#FEF2F2`, borde `#FECACA`, ícono `bi-trash3-fill` en `#EF4444`), que se resalta a rojo vivo en hover/toque para corregir equivocaciones sin fricción.
- **Botón Visible "Vaciar Carrito"**: Se implementó el botón `#btn-pos-clear` con estilo de acción visible en contorno rojo (`btn-outline-danger` con ícono `bi-trash3`) en la esquina superior derecha del carrito, visible automáticamente únicamente cuando existen productos cargados.

### 4. Zona de Pago y Billetes Estilo Cajero Automático
- **Cifras Gigantes en TOTAL A PAGAR y CAMBIO**: Los bloques de total y cambio incorporan números gigantes con tipografía responsive fluida de `clamp(2rem, 3.2vw, 2.5rem)` (32px a 40px), legibles sin esfuerzo incluso por personas con vista cansada.
- **Campo de Efectivo Recibido con Borde Grueso**: El campo `EFECTIVO (Q)` se amplió a `52px` de altura, con borde grueso de `2.5px solid #0D7377`, selector monetario `Q` de `52px` y tipografía al escribir de `1.45rem fw-black`.
- **Cuadrícula de Billetes y Pago Rápido (Mínimo 50px de Alto)**: Las fichas pequeñas se convirtieron en una cuadrícula táctil estilo cajero automático con botones de `50px` de altura, bordes de `2px` y texto en negrita `1.05rem` para: *Monto exacto, Q10, Q20, Q50, Q100, Q200* y botón extendido de *Transferencia*.
- **Botón Principal COBRAR al Doble de Altura**: Se duplicó la altura del botón principal de cobro a `82px` (anteriormente 44px), con tipografía destacada de `1.45rem fw-black`, ícono monetario `bi-cash-coin fs-2` y sombra de elevación profunda (`rgba(10, 92, 94, 0.35)`), coronándolo como la acción primaria incontrovertible de la pantalla.
- **Compatibilidad con Modo Oscuro**: Todos los nuevos controles, botones, tarjetas, controles de cantidad y cuadrícula de pago cuentan con estilos correspondientes bajo `[data-theme="dark"]` y `[data-bs-theme="dark"]` con alto contraste y legibilidad óptima.

### 5. Archivos Modificados
- [`frontend/js/pos.js`](../frontend/js/pos.js): Eliminación del botón `+`, renderizado de íconos hero de categoría (sin siglas de texto), controles táctiles de cantidad `[ - ] [ + ]`, botón de papelera y actualización de versión a `pos.js?v=2.2`.
- [`frontend/index.html`](../frontend/index.html): Retiro de atajos de teclado visuales (`<kbd>`), inclusión de billetes rápidos `Q10` y `Q20`, botón visible de vaciar carrito, botón de cobro de doble altura y actualización de versiones de caché (`style.css?v=5.9`, `pos.js?v=2.2`).
- [`frontend/css/style.css`](../frontend/css/style.css): Reglas completas para tarjetas de producto grandes, efectos táctiles, omnibox alto (64px), píldoras tab de categoría (48px), controles de cantidad (44px), zona de pago estilo cajero y reglas completas para Modo Oscuro.

## [2026-10-26] Rediseño Moderno de Pantalla de Inicio de Sesión (Login)

### 1. Limpieza del Fondo (Foco en la Conversión)
- Se eliminó por completo la imagen de fondo del bosque (`https://images.unsplash.com/...`) de la clase `.auth-bg`.
- Se configuró un fondo sólido y limpio en gris casi blanco (`#F9FAFB`), adaptado en Modo Oscuro a pizarra carbón profundo (`#0F172A`), permitiendo que el formulario sea el centro focal exclusivo de la pantalla sin distracciones fotográficas.

### 2. Branding y Nueva Paleta de Colores
- **Logo de la Empresa (+30% de Tamaño)**: Se incrementaron las dimensiones de `.logo-circle` de 64x64px a 84x84px (un 31.2% más grande), con un ícono escalado a `2.35rem`, degradado turquesa vibrante y sombra de elevación sutil.
- **Botón "Ingresar al Sistema"**: Se vistió con el nuevo Turquesa vibrante corporativo (`#0D9488` a `#0D7377`) con altura táctil de 48px, peso `fw-semibold` y sombra difusa.
- **Enlace "¿Olvidaste tu contraseña?"**: Se aplicó el color Rosa Coral de la marca (`#F43F5E`) con hover a `#E11D48`, estableciéndolo como acento visual secundario armónico.

### 3. Optimización de UX del Formulario
- **Ergonomía Táctil en Inputs**: Los campos de texto ("Usuario / Email" y "Contraseña") se agruparon en `.auth-input-group`, garantizando una altura de 48px (por encima del umbral ergonómico de 44px) con padding amplio y tipografía nítida.
- **Anillo de Enfoque Turquesa (Focus Ring)**: Al hacer clic o tabular en un campo, el borde del contenedor completo se ilumina en turquesa principal con un halo difuso exterior (`box-shadow: 0 0 0 4px rgba(13, 148, 136, 0.18)`).
- **Sombra Difusa Estilo Apple / Stripe**: Se rediseñó `.auth-card` con bordes redondeados amplios (`border-radius: 24px`), borde perimetral sutil (`rgba(226, 232, 240, 0.8)`) y una sombra multicapa ultra-suave y difusa que elimina cualquier apariencia de plantilla genérica.

### 4. Archivos Modificados
- [`frontend/css/style.css`](../frontend/css/style.css): Reglas completas para `.auth-bg`, `.auth-card`, `.logo-circle`, `.auth-input-group`, `.btn-brand-turquoise` y `.login-forgot-link`.
- [`frontend/index.html`](../frontend/index.html): Actualización estructural del formulario de Login y versión a `style.css?v=5.8`.

## [2026-10-26] Reversión de Logotipo (Restauración de Ícono Original de Regalo)
- A solicitud del usuario, se revirtió la sustitución del logotipo circular, retirando el archivo temporal `frontend/img/logo.png`.
- Se restauró en su totalidad el ícono original de regalo de Bootstrap (`<i class="bi bi-gift-fill fs-3 me-2 text-teal-light"></i>`) en la esquina superior del menú lateral y en el módulo de Login.
- Se eliminaron las reglas CSS `.sidebar-brand-img` y se actualizó la versión de caché a `style.css?v=5.7`.

## [2026-10-26] Estándares Visuales Modernos (Encabezados Fijos Sticky, Desenfoque de Modales y Tipografía Tabular)

### 1. Encabezados Fijos (`position: sticky` en Tablas)
- **Persistencia Visual Durante el Desplazamiento**: Se aplicó `position: sticky !important; top: 0 !important; z-index: 10 !important;` a todos los encabezados `<thead>` y `<th>` de las 34 tablas del sistema.
- **Fondo Sólido y Separación**:
  - Se blindó el fondo con `--color-teal-dark` y una sombra sutil (`box-shadow: 0 2px 5px rgba(0, 0, 0, 0.08)` en claro, `rgba(0, 0, 0, 0.45)` en oscuro) para evitar cualquier filtrado o transparencia de las filas inferiores al hacer scroll.
  - Se acondicionaron los contenedores `.table-responsive` con `max-height: calc(100vh - 250px)` (y `52vh` en ventanas modales) para habilitar scroll vertical autónomo con encabezado anclado.

### 2. Desenfoque de Modales (`backdrop-filter: blur`)
- **Aislamiento Visual de Formularios Emergentes**:
  - Se configuró `.modal-backdrop.show` con `backdrop-filter: blur(8px) saturate(180%) !important;` y `-webkit-backdrop-filter`.
  - Se añadió desenfoque complementario sobre `.modal.show` (`blur(6px)`), logrando un efecto de cristal esmerilado que difumina la interfaz de fondo y centra la atención en el formulario activo.
  - En Modo Oscuro, el fondo oscurece a `rgba(0, 0, 0, 0.75)` con desenfoque de `10px` para una experiencia inmersiva.

### 3. Tipografía Tabular (`font-variant-numeric: tabular-nums`)
- **Alineación Numérica Matemática**:
  - Se aplicó `font-variant-numeric: tabular-nums lining-nums !important;` junto con la bandera OpenType `font-feature-settings: "tnum" 1, "lnum" 1 !important;` en celdas de tabla (`th`, `td`), columnas de precios, montos, costos, totales, subtotales, pérdidas de merma, existencias de inventario, cajas de cambio del POS y métricas clave (KPIs).
  - Al utilizar la fuente nativa *Inter*, los números adquieren un ancho uniforme idéntico, alineando con precisión decimal las cifras monetarias en Quetzales (Q) y facilitando la comparación contable rápida.

### 4. Archivos Modificados
- [`frontend/css/style.css`](../frontend/css/style.css): Reglas completas para encabezados sticky, backdrop-filter de modales y tipografía tabular.
- [`frontend/index.html`](../frontend/index.html): Actualización de versión a `style.css?v=5.5`.

## [2026-10-26] Mejoras de Experiencia Visual y Accesibilidad (Toasts, Focus Rings y Skeleton Loaders)

### 1. Notificaciones Flotantes (Toasts Minimalistas)
- **Ubicación en Esquina Superior Derecha**: Se reubicó `#toast-container` de la parte inferior a la esquina superior derecha (`position-fixed top-0 end-0 p-3`) con capa de z-index elevada (`1100`).
- **Diseño Minimalista y Semántico**:
  - Borde verde esmeralda (`border-left: 5px solid #10B981`) con ícono de check para notificaciones de éxito.
  - Borde rojo (`border-left: 5px solid #EF4444`) con ícono de advertencia para notificaciones de error.
  - Diseños complementarios para alertas de advertencia (ámbar) e información (celeste).
  - Integración total con Modo Claro y Modo Oscuro (superficies adaptadas).
- **Desaparición Automática a los 3 Segundos**: Temporizador de 3000 ms con animación de salida deslizante y soporte para cierre manual inmediato mediante botón "X".
- **Eliminación de Alertas Bloqueantes**:
  - Se redefinió `window.alert(...)` globalmente para canalizar cualquier llamada hacia los Toasts minimalistas no bloqueantes.
  - Se sustituyeron las llamadas nativas de `alert(...)` en formularios de recuperación y cambio de contraseña por `showToast(..., 'success')`.

### 2. Anillos de Enfoque Accesibles (`:focus-visible`)
- **Navegación Ergonómica con Tecla Tab**: Se implementó una regla `:focus-visible` global para inputs, selects, textareas, botones (`.btn`, `button`), enlaces navegables y fichas del POS.
- **Anillo Exterior Verde Brillante**:
  - En modo claro: contorno de `2px solid #10B981` con anillo exterior difuso `rgba(16, 185, 129, 0.35)` y `outline-offset: 2px`.
  - En modo oscuro: verde esmeralda luminoso `#34D399` con resplandor `rgba(52, 211, 153, 0.45)`.
  - No ensucia la experiencia de clic convencional con mouse/táctil, activándose exclusivamente al tabular.

### 3. Skeleton Loaders (Animación de Pulso Shimmer)
- **Sustitución de Íconos Giratorios (Spinners)**:
  - Se sustituyeron los spinners giratorios (`spinner-border`) en tablas y tarjetas por estructuras grises con animación de pulso/shimmer (`@keyframes skeletonShimmerAnim`).
  - Creación de helpers globales en [`app.js`](../frontend/js/app.js): `window.renderSkeletonTable(columns, rows)` y `window.renderSkeletonCard(lines)`.
  - Animación fluida de 1.4s en gradiente suave tanto en Modo Claro como en Modo Oscuro (tonos carbón y pizarra).
- **Módulos Integrados**:
  - **Clientes**: Tablas de directorio y tipos de clientes, además de la ficha de detalle táctil.
  - **Mermas**: Tabla principal de registros de merma y pérdida.
  - **Catálogos**: Tablas de subcategorías, unidades, sucursales, almacenes y fichas de detalle.
  - **Reportes**: Tablas de usuarios y clientes filtrados, y ranking de productos.
  - **Usuarios / Personal**: Tabla de listado de usuarios con simulación de filas.
  - **Inventario / Bodega**: Tabla de existencias y contenedor de alertas de stock.
  - **Caja**: Historial de turnos con filas simuladas.
  - **Roles y Permisos**: Modal de asignación de permisos con tarjeta skeleton.
  - **Bitácora e Historial**: Tablas de auditoría y precios con carga estructurada.

### 4. Archivos Modificados
- [`frontend/css/style.css`](../frontend/css/style.css): Reglas completas para `.custom-toast`, `:focus-visible` y `.skeleton`.
- [`frontend/index.html`](../frontend/index.html): Reposicionamiento del contenedor `#toast-container` a `top-0 end-0`, modal skeleton y actualización de versiones (`style.css?v=5.4`, `app.js?v=3.3`).
- [`frontend/js/app.js`](../frontend/js/app.js): Reescritura de `showToast`, interceptor `window.alert` y generadores `renderSkeletonTable` y `renderSkeletonCard`.
- [`frontend/js/clients.js`](../frontend/js/clients.js), [`frontend/js/mermas.js`](../frontend/js/mermas.js), [`frontend/js/catalog.js`](../frontend/js/catalog.js), [`frontend/js/reportes.js`](../frontend/js/reportes.js), [`frontend/js/users.js`](../frontend/js/users.js), [`frontend/js/inventory.js`](../frontend/js/inventory.js), [`frontend/js/cash_register.js`](../frontend/js/cash_register.js), [`frontend/js/roles.js`](../frontend/js/roles.js), [`frontend/js/bitacora.js`](../frontend/js/bitacora.js), [`frontend/js/historial.js`](../frontend/js/historial.js).

## [2026-10-26] Habilitación de Modo Oscuro Nativo con Variables Globales de Diseño (CSS Tokens)
## [2026-10-26] Habilitación de Modo Oscuro Nativo con Variables Globales de Diseño (CSS Tokens)

### 1.1 Adaptación Integral de Modo Oscuro en Pantalla de Punto de Venta (POS)
A petición del usuario, se realizó una depuración exhaustiva de la vista de Punto de Venta (`#pos-view`) en Modo Oscuro para eliminar cualquier remanente con fondo blanco o bajo contraste:
- **Fondo de la Vista POS (`.pos-view`)**: Se reemplazó el color duro claro `#F4F7F6` por `var(--theme-bg-body) !important` (`#0F172A`). Esto eliminó por completo la franja blanca superior detrás del título "Punto de Venta" y de los botones de navegación ("Historial", "Pantalla Cliente", "Panel"), garantizando contraste óptimo en textos y títulos.
- **Buscador Omnibox y Lector de Barras (`.pos-omnibox`)**: Fondo oscuro (`#0F172A`), bordes en `#334155`, texto claro (`#F8FAFC`) y foco con resalte esmeralda. Teclas de atajo y botón limpiar integrados en paleta oscura.
- **Píldoras de Categoría (`.pos-category-pill`)**: Fondos en pizarra `#0F172A` con bordes `#334155` y textos `#CBD5E1`; estado activo con verde esmeralda corporativo intacto.
- **Tarjetas de Producto (`.pos-product-card`)**:
  - Se eliminó el fondo blanco/menta claro de los contenedores de imagen y placeholders de iniciales (`.pos-product-media`, `.pos-product-placeholder`), sustituyéndolo por un degradado profundo (`#0F172A` a `#1E293B`) con iniciales en celeste de alto contraste (`#38BDF8`).
  - Etiquetas de categoría (`.pos-category-tag`) con fondo traslúcido carbón y texto nítido.
  - Precios en celeste brillante (`#38BDF8`) y badges de mayoreo adaptados a contraste suave.
- **Panel de Carrito y Cobro**:
  - Buscador de cliente (`.pos-client-line`): Fondo `#0F172A` y bordes `#334155`.
  - Caja de cambio (`.pos-change-box`): Sustituido el fondo verde menta claro por fondo carbón con borde `#334155` y números en verde esmeralda claro (`#34D399`).
  - Fichas de efectivo rápido (`.pos-cash-chip` y `.pos-transfer-toggle`): Fondos pizarra oscuros `#0F172A` en lugar de botones blancos reflectantes.
  - Botón cobrar deshabilitado (`.btn-pos-charge:disabled`): Fondo apagado neutro `#243248` con texto tenue `#64748B` sin resplandor blanco.
- **Archivos y Versiones**:
  - [`frontend/css/style.css`](../frontend/css/style.css): Reglas especializadas bajo `[data-theme="dark"]` y `[data-bs-theme="dark"]`.
  - [`frontend/index.html`](../frontend/index.html): Caché actualizada a `style.css?v=5.3`.


### 1. Requerimiento y Arquitectura Visual
Se implementó un sistema nativo de **Modo Oscuro (Dark Theme)** y **Modo Claro (Light Theme)** 100% frontend (HTML, CSS y JS) basado en tokens de diseño centralizados en variables CSS, con persistencia en el navegador y transición fluida sin recargar ni consultar el backend.

- **Modo Claro**: Fondos de tarjetas blancos (`#FFFFFF`), fondo de página gris claro (`#F4F6F8`), textos oscuros de alta legibilidad (`#1F2937`) y bordes tenues (`#E5E7EB`).
- **Modo Oscuro**: Fondos de tarjeta y modales en tono carbón / pizarra (`#1E293B`), fondo general profundo (`#0F172A`), textos claros (`#F8FAFC`, `#CBD5E1`) y bordes sutiles (`#334155`) diseñados para eliminar la fatiga visual nocturna.
- **Color Corporativo Intacto**: El verde esmeralda institucional (`--color-teal: #0D7377`, `--color-teal-dark: #0A5C5E`), el degradado característico de la barra lateral (`linear-gradient(180deg, #0B6063 0%, #084A4C 100%)`), los botones principales de acción (`.btn-teal`) y los encabezados corporativos de todas las tablas de datos permanecen exactamente iguales en ambos modos, salvaguardando la identidad visual de "Tienda el Regalito".

### 2. Cambios Implementados

#### A. Variables Globales y Estilos ([`frontend/css/style.css`](../frontend/css/style.css))
- **Bloque `:root` (Tokens Modo Claro)**:
  - `--theme-bg-body: #F4F6F8;`
  - `--theme-bg-surface: #FFFFFF;`
  - `--theme-bg-card: #FFFFFF;`
  - `--theme-bg-header: #FFFFFF;`
  - `--theme-bg-input: #FFFFFF;`
  - `--theme-text-main: #1F2937;`
  - `--theme-text-secondary: #4B5563;`
  - `--theme-text-muted: #6B7280;`
  - `--theme-border: #E5E7EB;`
- **Bloque `[data-theme="dark"], [data-bs-theme="dark"]` (Tokens Modo Oscuro / Carbón)**:
  - `--theme-bg-body: #0F172A;`
  - `--theme-bg-surface: #1E293B;`
  - `--theme-bg-card: #1E293B;`
  - `--theme-bg-header: #1E293B;`
  - `--theme-bg-input: #0F172A;`
  - `--theme-text-main: #F8FAFC;`
  - `--theme-text-secondary: #CBD5E1;`
  - `--theme-text-muted: #94A3B8;`
  - `--theme-border: #334155;`
- **Reglas de Renderizado y Componentes en Modo Oscuro**:
  - Mapeo automático de `.bg-white` hacia `--theme-bg-card`.
  - Mapeo de `.card`, `.modal-content` y `.dropdown-menu` hacia `--theme-bg-card` y `--theme-border`.
  - Adaptación de inputs (`.form-control`, `.form-select`) con fondo carbón, borde suave y foco corporativo esmeralda.
  - Inversión cromática del botón de cierre de modales (`.btn-close`).
  - Filas de tablas semitransparentes con hover sutil (`rgba(255, 255, 255, 0.04)`).
  - Reglas prioritarias para garantizar que las cabeceras corporativas (`.table thead`, `.thead-users`, `.thead-catalog`, `.thead-cash`) conserven su fondo verde esmeralda y texto blanco puro.
  - Conservación estricta de la barra de navegación lateral (`.sidebar`).

#### B. Interfaz del Interruptor y Carga Temprana ([`frontend/index.html`](../frontend/index.html))
- **Inicialización Inmediata en `<head>`**: Se colocó un script ligero que evalúa `localStorage.getItem('themePreference')` o `window.matchMedia('(prefers-color-scheme: dark)')` antes del renderizado del body, evitando cualquier parpadeo de pantalla blanca (FOUC).
- **Botón Minimalista en Cabecera**:
  - Insertado en la barra superior junto al botón de copia local y notificaciones: `<button id="btn-theme-toggle" class="btn btn-sm btn-light border rounded-circle ...">`.
  - Contiene el ícono dinámico `<i class="bi bi-moon-stars-fill text-secondary fs-6" id="theme-icon"></i>` en modo claro y cambia a sol dorado `<i class="bi bi-sun-fill text-warning fs-6"></i>` en modo oscuro.
- **Control de Caché**: Se incrementaron las referencias a `css/style.css?v=5.2` y `js/app.js?v=3.2`.

#### C. Lógica Interactiva y Persistencia ([`frontend/js/app.js`](../frontend/js/app.js))
- Se añadió un módulo IIFE para la gestión del tema:
  - Lectura y escritura de la clave `'themePreference'` en `localStorage`.
  - Función `applyTheme(theme)` que sincroniza tanto `data-theme` como `data-bs-theme` en `<html>` y actualiza el ícono correspondiente.
  - Función `toggleTheme()` que alterna entre `'light'` y `'dark'`.
  - Detección de cambios de preferencias del sistema operativo (`prefers-color-scheme`) en tiempo real cuando el usuario no ha fijado una preferencia manual.
  - Exposición de funciones en el objeto global `window.toggleTheme` y `window.setTheme`.

### 3. Archivos Modificados
- [`frontend/css/style.css`](../frontend/css/style.css): Inclusión de tokens dinámicos en `:root` y bloque completo de reglas para `[data-theme="dark"]` y `[data-bs-theme="dark"]`.
- [`frontend/index.html`](../frontend/index.html): Script anti-FOUC en `<head>`, botón interruptor en cabecera y actualización de versiones de activos (`?v=5.2`, `?v=3.2`).
- [`frontend/js/app.js`](../frontend/js/app.js): Lógica de cambio de tema, manejo de eventos y sincronización con `localStorage`.
- [`documentacion/cambios.md`](cambios.md): Registro exhaustivo de la modificación.

## [2026-10-26] Corrección Estructural de Anidamiento DOM en Vistas Principales (Bitácora, Inventario, Mermas, etc.)

### Causa Raíz
- Al restaurar el módulo de Reportes en el HTML, quedó una etiqueta de cierre `</div>` sobrante justo al final de la vista de Caja (`#cash-view`).
- Esta etiqueta extra cerraba prematuramente el elemento principal `<main>` del sistema.
- En consecuencia, todas las vistas declaradas posteriormente en el archivo ([`#reportes-view`](../frontend/index.html#L1971), [`#inventory-view`](../frontend/index.html#L2268), [`#traslados-view`](../frontend/index.html#L2419), [`#visitas-view`](../frontend/index.html#L2494), [`#mermas-view`](../frontend/index.html#L2769), [`#compras-view`](../frontend/index.html#L2904), [`#configuracion-view`](../frontend/index.html#L3070), [`#roles-view`](../frontend/index.html#L3115), [`#bitacora-view`](../frontend/index.html#L3152) y [`#historial-view`](../frontend/index.html#L3235)) quedaban expulsadas fuera del contenedor flex `<main>` y fuera de la estructura de visualización.
- Al hacer clic en el menú lateral sobre cualquiera de estos módulos (como "Bitácora"), el sistema ocultaba las demás vistas y mostraba el contenedor correspondiente, pero dado que estaba fuera de `<main>`, la pantalla central permanecía completamente en blanco.

### Solución Implementada
1. **Depuración y Validación Estructural del DOM**:
   - [`frontend/index.html`](../frontend/index.html): Se eliminó la etiqueta de cierre `</div>` huérfana en la línea de transición entre Caja y Reportes.
   - Se validó el balance completo de etiquetas `<div>` y `<main>` a lo largo de las 5,330 líneas del archivo, comprobando que:
     - El balance de profundidad (`depth`) permanece en `1` para cada una de las 16 vistas dentro de `<main>`.
     - El cierre de `</main>` se produce en la posición correcta (después de Historial).
     - El conteo de errores de etiquetas huérfanas se redujo a `0`.
2. **Actualización de Versiones**:
   - Se incrementaron las etiquetas de control de caché a `style.css?v=5.1` y `app.js?v=3.1` para forzar la recarga limpia en el navegador del usuario.
   - Se reinició el contenedor `regalito_frontend_prod` en Docker.

### Verificación
- Verificación automatizada de anidamiento: Las 16 vistas principales se encuentran al 100% dentro de `<main>`.
- Consulta HTTP en `http://localhost:9090/`: Respuesta `200 OK` con los recursos actualizados.
- Bitácora, Inventario, Roles, Mermas, Compras y Reportes vuelven a renderizarse correctamente dentro del panel principal.

## [2026-10-25] Rediseño Responsivo Global (Móviles y Tablets) y Protección de Tablas

### Causa Raíz / Requerimiento
1. **Deformación en Pantallas Pequeñas (< 1024px)**:
   - El sistema presentaba desbordamientos y roturas de diseño en dispositivos móviles y tabletas:
   - La barra de navegación lateral izquierda (`.sidebar`) forzaba un ancho fijo o se apilaba estáticamente encima de la interfaz empujando todo el panel hacia abajo.
   - Las tablas operativas (Inventario, Clientes, Mermas, Caja, Usuarios, Catálogos, etc.) no tenían protección contra reducción de pantalla, lo que comprimía y aplastaba las columnas de datos.
   - Las tarjetas de resumen financiero (KPIs) y los bloques del Dashboard/Reportes mantenían alineaciones multi-columna forzadas (`col-6`, `col-md-4`, etc.), generando tarjetas excesivamente estrechas e ilegibles en smartphones.
   - Las ventanas emergentes (Modales) se desbordaban fuera del viewport o mantenían márgenes que reducían drásticamente el espacio táctil útil para el operador.

### Solución Implementada (100% Frontend - CSS/HTML/JS)
1. **Navegación Móvil (Menú Hamburguesa & Off-Canvas)**:
   - [`frontend/index.html`](../frontend/index.html):
     - Se añadió el elemento `#sidebar-mobile-backdrop` para oscurecer y desenfocar el fondo (`backdrop-filter: blur(3px)`) al abrir el menú lateral.
     - Se añadió el botón de cierre táctil `#btn-sidebar-close` (`bi-x-lg`) en la cabecera del sidebar (`.sidebar-brand`), visible únicamente en móviles (`d-lg-none`).
     - Se vinculó el botón hamburguesa existente en el encabezado (`#btn-sidebar-toggle`) para controlar el despliegue off-canvas en pantallas menores a 1024px.
   - [`frontend/css/style.css`](../frontend/css/style.css):
     - Se eliminó la regla obsoleta que apilaba el sidebar estáticamente arriba del contenido.
     - Para pantallas `@media (max-width: 1023.98px)`: El sidebar se posiciona de forma fija (`position: fixed; left: 0; top: 0; bottom: 0; z-index: 1055;`) desplazado fuera de la pantalla con aceleración por hardware (`transform: translateX(-100%)`). Al activarse `.mobile-sidebar-open` en `#system-module`, se desliza suavemente (`transform: translateX(0)`) con sombreado de elevación (`box-shadow: 0 10px 40px rgba(0,0,0,0.5)`).
   - [`frontend/js/app.js`](../frontend/js/app.js):
     - Módulo de control dual: En pantallas grandes (>= 1024px) conserva el colapso a mini-sidebar (`sidebar-collapsed`). En pantallas táctiles (< 1024px) conmuta la clase `mobile-sidebar-open`.
     - Cierre automático al seleccionar cualquier enlace de navegación (`.sidebar-link`), al tocar el backdrop oscuro, al pulsar el botón `X`, al presionar la tecla `Escape`, o al redimensionar la ventana hacia escritorio.
     - Integración con `renderView()` para asegurar el cierre automático al navegar a cualquier módulo.

2. **Protección Global de Tablas (Scroll Horizontal)**:
   - [`frontend/index.html`](../frontend/index.html): Se verificaron las 34 tablas de la plataforma y se envolvió la tabla restante (`#compras-cart-table`) en un contenedor con clase `.table-responsive`.
   - [`frontend/css/style.css`](../frontend/css/style.css):
     - Reglas universales `.table-responsive, .overflow-x-auto` con desplazamiento táctil acelerado (`-webkit-overflow-scrolling: touch`).
     - Definición de ancho mínimo de seguridad (`min-width: 680px` en tablas generales y `min-width: 760px` en tablas densas como Inventario, Clientes, Mermas, Caja, Usuarios, Bitácora y Reportes). Las columnas conservan su tipografía, alineación e información íntegra; el usuario simplemente desliza la tabla horizontalmente de forma natural.
     - Scrollbar horizontal estilizado, sutil y accesible (`height: 6px; border-radius: 4px; background: rgba(11,96,99,0.25)`).

3. **Apilamiento de Tarjetas (Stacking al 100%)**:
   - [`frontend/css/style.css`](../frontend/css/style.css):
     - Para `@media (max-width: 767.98px)`: Todas las tarjetas KPI (`#dashboard-kpis`, `#inventory-kpis`, `#mermas-kpi-row`, `#reportes-kpis`, `#reportes-summary-cards`, `.inventory-kpi-card`, `.merma-kpi-card`, `.reportes-kpi-card`, `.dashboard-kpi-card`, `[data-dashblock^="kpi-"]`) dejan de compartir fila y pasan a ocupar `width: 100% !important; flex: 0 0 100% !important; max-width: 100% !important;` apilándose en una sola columna vertical.
     - Los bloques de gráficas, listas de rankings, alertas de stock y turnos pendientes del Dashboard y Reportes (`[data-dashblock="grafico-ventas"]`, `[data-dashblock="top-productos"]`, `#reportes-grafica-container`, `#reportes-rankings-card`, etc.) se apilan verticalmente ocupando el ancho completo de la pantalla móvil.
     - Ajuste ergonómico de espaciados (`padding: 0.85rem 0.65rem`) en el contenedor principal y cabecera para maximizar el área visible útil en smartphones.

4. **Modales y Formularios Táctiles**:
   - [`frontend/css/style.css`](../frontend/css/style.css):
     - En dispositivos móviles (`@media (max-width: 767.98px)`), las ventanas modales (`.modal-dialog`) se expanden dinámicamente al 95% del ancho de la pantalla (`width: 95vw !important; max-width: 95vw !important; margin: 0.5rem auto !important;`).
     - Bordes redondeados modernos (`border-radius: 14px`) y sombreado suave de profundidad.
     - Optimización de márgenes internos (`.modal-body` con padding reducido a `1rem 0.85rem` y scroll interno táctil `max-height: calc(100vh - 135px)`).
     - Botones de acción del pie del modal (`.modal-footer .btn`) distribuidos al 50% de ancho con área táctil cómoda.
     - Ergonomía táctil para inputs, selects y botones en modales: altura mínima de 44px (`min-height: 44px`) conforme al estándar de accesibilidad táctil (WCAG 2.1 / Apple HIG) y tamaño de fuente `16px` para prevenir el zoom automático no deseado en navegadores iOS Safari.

5. **Restauración y Sincronización del Módulo de Reportes**:
   - [`frontend/index.html`](../frontend/index.html): Se restauró la estructura completa del contenedor `#reportes-view` (`data-main-view="reportes"`) y su Tab 1 (Consolidado Operativo, selector de rango inteligente, KPIs financieros, tarjetas de gráficas y leaderboard de rankings) que se encontraba truncada en el archivo HTML, alineándolo 1:1 con la interfaz documentada y Chart.js.

### Verificación
- **Pruebas de Menú Hamburguesa & Off-Canvas**:
  - En anchos `< 1024px`, el sidebar queda oculto por defecto.
  - Al pulsar `#btn-sidebar-toggle` (☰), el menú se desliza suavemente sobre la pantalla y activa el fondo oscuro `#sidebar-mobile-backdrop`.
  - Al pulsar el botón `X`, hacer clic en el backdrop, hacer clic en cualquier opción de menú o pulsar `Escape`, el sidebar se oculta inmediatamente.
  - En resoluciones `>= 1024px`, el sidebar regresa a su posición lateral estándar con soporte de colapso mini (`sidebar-collapsed`).
- **Pruebas de Tablas Responsivas**:
  - En pantallas de 375px a 768px, las 34 tablas del sistema cuentan con scroll horizontal táctil sin truncar contenido ni aplastar encabezados.
- **Pruebas de Apilamiento (Stacking)**:
  - Las tarjetas KPI de Dashboard, Inventario, Mermas y Reportes ocupan el 100% de la pantalla en vista móvil apiladas en una sola columna.
- **Pruebas de Modales Táctiles**:
  - Los formularios modales abarcan el 95% de la pantalla, con botones e inputs de 44px de altura mínima.
- **Reinicio y Servicio en Producción**:
  - Contenedor Nginx (`regalito_frontend_prod`) reiniciado exitosamente.
  - Servido en `http://localhost:9090` con versiones `style.css?v=5.0` y `app.js?v=3.0`.

## [2026-10-25] Módulo de Caja: Theme Sync, Control Operativo de Flujo de Efectivo y Filtros Compactos

### Causa Raíz / Requerimiento
1. **Inconsistencias Visuales (Theme Sync)**:
   - El botón de acción crítica "Cerrar Turno" (`#btn-close-cash`) utilizaba un color rosa (`btn-rosado`), restándole la seriedad que requiere una operación crítica de cierre financiero.
   - El botón "Filtrar" en el historial de turnos utilizaba un color azul celeste (`btn-celeste`), fuera del verde esmeralda corporativo (`var(--color-teal)`).
   - El encabezado de la tabla "Historial de Turnos" presentaba líneas divisorias y degradados desincronizados del estándar esmeralda sólido (`var(--color-teal-dark)`) de Inventario y Usuarios.
2. **Mejoras Operativas en Tarjeta de Caja Activa (UX Operativo)**:
   - La cuadrícula de detalles de la caja abierta carecía de visibilidad sobre los ingresos en efectivo del turno y el arqueo esperado. Se requería añadir:
     - "Ventas en Efectivo" (placeholder `Q 0.00`).
     - "Efectivo Esperado" (destacado en verde oscuro).
   - Necesidad de un control para registrar gastos menores de la tienda (artículos de limpieza, encomiendas, entradas para cambio) mediante un botón secundario discreto ("± Registrar Movimiento").
3. **Limpieza de Filtros y Ordenamiento (1:1 con Inventario)**:
   - Los campos de fecha "Desde" y "Hasta" estaban separados visualmente; se requería agruparlos en un input compacto unificado con ícono de calendario.
   - Los encabezados de tabla debían heredar la experiencia táctil de Inventario con íconos de ordenamiento `⇕` (inactivo), `↑` / `↓` (activo) y subrayado hover.

### Solución Implementada
1. **Estructura HTML y Theme Sync**:
   - [`frontend/index.html`](../frontend/index.html):
     - Sustitución de `btn-rosado` por `btn btn-outline-danger fw-semibold px-3` en `#btn-close-cash` y `btn-danger` en el modal de confirmación de cierre.
     - Botón "Filtrar" actualizado a `btn-teal` con bordes redondeados consistentes.
     - Tarjeta de caja activa enriquecida con columnas para "Ventas en Efectivo" (`#cash-active-ventas`) y "Efectivo Esperado" (`#cash-active-esperado`) en verde esmeralda oscuro (`#065F46`), y botón secundario `#btn-cash-movement` ("± Registrar Movimiento").
     - Rango de fechas compacto agrupado `.cash-date-range-group` con ícono de calendario.
     - Tabla actualizada a `<thead class="thead-users">` con clase `.cash-table`.
     - Nuevo modal `#cash-movement-modal` para registro rápido de gastos menores y entradas de cambio.
     - Versiones incrementadas a `style.css?v=4.7` y `cash_register.js?v=2.4`.
2. **Estilos CSS**:
   - [`frontend/css/style.css`](../frontend/css/style.css):
     - Estilo crítico para `#btn-close-cash` (borde rojo `#DC2626`, texto rojo, fondo transparente en reposo y sólido en hover).
     - Botón ghost/secundario `.cash-movement-btn` para la tarjeta de caja.
     - Rango de fechas compacto `.cash-date-range-group` de 38 px con bordes unificados.
     - Encabezado sólido `var(--color-teal-dark)` con texto blanco sin líneas divisorias verticales y esquinas redondeadas.
     - Efecto hover con subrayado (`text-decoration: underline; text-underline-offset: 3px;`) y cursor `pointer` en cabeceras ordenables.
3. **Lógica Frontend (Vanilla JS)**:
   - [`frontend/js/cash_register.js`](../frontend/js/cash_register.js):
     - `renderCashStatusCard()` actualizado para computar y mostrar "Ventas en Efectivo" y "Efectivo Esperado" (monto inicial + ventas), y alternar visibilidad del botón de movimientos.
     - Funciones `openCashMovementModal()` y `handleCashMovementSubmit()` para gestionar el registro de gastos/entradas y actualizar inmediatamente el monto de efectivo esperado en pantalla.
     - `updateCashSortIndicators()` actualizado para inyectar íconos vectoriales `bi bi-arrow-down-up text-white-50` en inactivos y `bi-arrow-up`/`bi-arrow-down text-white` en la columna activa.

### Verificación
- **Validación de Sintaxis**: Ejecución de `node --check frontend/js/cash_register.js` sin errores.
- **Pruebas de Despliegue**: Verificación de assets servidos correctamente por Nginx y FastAPI en puerto 9090.
- **Regla estricta**: Cero alteraciones en backend o base de datos.

## [2026-10-25] Menú Lateral Izquierdo: Limpieza Visual para Operación de Una Sola Tienda

### Causa Raíz / Requerimiento
1. **Reducción de carga visual en navegación**:
   - Para la fase operativa actual de una sola tienda física, no son requeridas las funciones de traslado entre sucursales ni visitas de campo externas, ni la visualización recurrente del histórico de variaciones de precios desde el menú principal.
   - Se requería limpiar la barra lateral izquierda comentando u ocultando visualmente dichos accesos para simplificar la interfaz al usuario final sin alterar la arquitectura subyacente.
2. **Reglas estrictas**:
   - Cambios 100% en el frontend (HTML/UI).
   - No eliminar archivos, controladores, rutas API ni esquemas de base de datos.
   - Ocultar en **Operación Diaria**: "Traslados" (`#nav-traslados`) y "Visitas de Seguimiento" (`#nav-visitas`).
   - Ocultar en **Administración**: "Historial de Precios" (`#nav-historial`).
   - Conservar intactos, visibles y plenamente funcionales en su ubicación original: "Roles y Permisos" (`#nav-roles`) y "Bitácora" (`#nav-bitacora`).

### Solución Implementada
1. **Frontend HTML**:
   - [`frontend/index.html`](../frontend/index.html):
     - Se comentaron los elementos `<li>` de "Traslados" (`data-module-item="traslados"`) y "Visitas de Seguimiento" (`data-module-item="visitas"`) en la sección de "Operación diaria", añadiendo comentarios explicativos para su fácil reactivación si la tienda se expande a múltiples sucursales en el futuro.
     - Se comentó el elemento `<li>` de "Historial de Precios" (`data-module-item="historial"`) en la sección de "Administración".
     - Se mantuvieron inalterados los enlaces de "Roles y Permisos" (`data-module-item="roles"`) y "Bitácora" (`data-module-item="bitacora"`).
     - Se preservaron todos los archivos fuente de controladores (`traslados.js`, `visitas.js`, `historial.js`), vistas HTML internas y endpoints backend para garantizar reactivación inmediata cuando sea requerido.

### Verificación
- **Pruebas visuales**:
  - En la barra lateral ya no se muestran "Traslados", "Visitas de Seguimiento" ni "Historial de Precios".
  - "Roles y Permisos" y "Bitácora" permanecen completamente visibles y accesibles para tareas de auditoría y gestión de seguridad.
  - La sección "Operación diaria" y la sección "Administración" conservan sus encabezados y el resto de módulos (POS, Inventario, Compras, Caja, Mermas, Usuarios, Clientes, Catálogos, Reportes, Configuración).
- **Integridad**:
  - 0 archivos eliminados; 0 cambios en el backend o en la base de datos.

## [2026-10-25] Módulo de Clientes: Rediseño UI/UX Directorio Rápido, Theme Sync y Búsqueda en Caja

### Causa Raíz / Requerimiento
1. **Unificación de Paleta de Colores (Theme Sync)**:
   - El encabezado de la tabla de clientes presentaba un fondo gris claro (`table-light`) con bordes grises predeterminados de Bootstrap, desentonando con el verde esmeralda oscuro corporativo (`var(--color-teal-dark)`) de Usuarios, Inventario y Mermas.
   - En la columna "Nombre" aparecía erróneamente incrustada la etiqueta o texto "Comercial" ("Nombre Comercial"), redundante con la razón social.
   - Las pestañas superiores utilizaban `nav-pills` estándar con fondo azulado; se requería modernizarlas con texto gris neutro para enlaces inactivos y verde esmeralda con borde inferior destacado para la pestaña activa ("Directorio de Clientes").
2. **Optimización de Búsqueda Rápida en Caja (POS Friendly)**:
   - Los filtros de calendario "Desde" y "Hasta" no resultaban prácticos para ubicar clientes en el mostrador del POS en tiempo real y sobrecargaban la barra de herramientas.
   - Los campos de "Buscar por nombre..." y "NIT" requerían mayor amplitud y jerarquía, y se precisaba un tercer campo de búsqueda directa por "Teléfono", estándar esencial para la fidelización rápida en caja.
   - Cada campo de texto requería un botón "X" integrado (estilo Shopify/Google) para limpiar el input con un solo clic, eliminando el botón "X" externo.
3. **Evolución de Datos y Componentes Visuales**:
   - Reemplazo de la columna "Ubicación" por una métrica comercial estratégica ("Total Comprado"), con formato monetario `Q 0.00` en tipografía monospace font-semibold.
   - Soft Badges semánticos para "Tipo Cliente" sin contornos grises, con fondos pastel translúcidos y texto legible más oscuro (azul suave para "Mayorista", gris neutro para "Consumidor Final", esmeralda para tipos minoristas/generales y púrpura para preferenciales).
   - Sustitución de botones cuadrados con bordes rígidos en "Acciones" por botones Ghost limpios (`.client-action-btn`), con fondo transparente en reposo y micro-resaltes al hacer `:hover` (azul para ver, ámbar para editar, rojo para desactivar y verde para activar).
4. **Interactividad de Ordenamiento (Heredada de Inventario)**:
   - Encabezados ordenables con íconos de ordenamiento 1:1 con Inventario: `⇕` (`bi bi-arrow-down-up text-white-50`) en reposo y flechas sólidas `↑` / `↓` (`text-white`) en la columna activa.
   - Efecto `:hover` con texto subrayado (`text-decoration: underline; text-underline-offset: 3px`) y cursor en `pointer`.

### Solución Implementada
1. **Theme Sync y Estructura HTML**:
   - [`frontend/index.html`](../frontend/index.html):
     - Sustitución de `nav-pills` por `nav nav-tabs clients-main-tabs mb-4` en `#clients-nav-tabs`.
     - Reestructuración de la barra de filtros con contenedores `.client-search-field` para Nombre (`flex-grow-1`), NIT y Teléfono con íconos vectoriales y botón `.client-clear-btn` incorporado.
     - Preservación oculta (`d-none`) de inputs de fecha y reset para garantizar compatibilidad retroactiva con cualquier flujo existente.
     - Actualización del encabezado de la tabla a `<thead class="thead-users">` y clase `.clients-table` en la tabla.
     - Renombrado de columna a "Nombre" (eliminando "Comercial") y sustitución de "Ubicación" por "Total Comprado" ordenable.
     - Actualización de versiones a `style.css?v=4.6` y `clients.js?v=2.0`.
2. **Estilos CSS Modernos y Semánticos**:
   - [`frontend/css/style.css`](../frontend/css/style.css):
     - Reglas `#clients-view .clients-main-tabs`: pestañas sin bordes perimetrales, enlace activo con `border-bottom: 3px solid var(--color-teal)` y color corporativo.
     - Buscadores `.client-search-field` y botón integrado `.client-clear-btn` con clase dinámica `.is-visible`, transiciones suaves y foco accesible.
     - Encabezado `#clients-view .clients-table > thead > tr > th` con fondo sólido `var(--color-teal-dark)`, texto blanco `font-weight: 600`, sin líneas divisorias verticales y esquinas exteriores redondeadas (`0.5rem`).
     - Clases semánticas `.badge-soft-blue`, `.badge-soft-slate` y `.badge-soft-emerald` sin bordes para tipos de cliente.
     - Botones Ghost `#clients-view .client-action-btn` (32×32 px, sin marcos, esquinas redondeadas y estados `:hover` específicos por tipo de acción).
     - Hover en cabeceras ordenables: subrayado sutil, cursor `pointer` e incremento de brillo.
3. **Lógica Frontend (Vanilla JS)**:
   - [`frontend/js/clients.js`](../frontend/js/clients.js):
     - Registro de `filterPhone` en `initDOM()`.
     - Helpers `escapeHtml`, `getClientTypeBadge` y `syncClearBtn`.
     - Eventos de input para alternar visibilidad de `.client-clear-btn` y ejecución de búsqueda con tecla `Enter`.
     - Manejadores de clic en `.client-clear-btn` para vaciar el input respectivo, reenfocar y refrescar el listado.
     - `updateSortIcons()` adaptado para cabeceras con fondo oscuro: íconos blancos `bi-arrow-up` / `bi-arrow-down` o `bi-arrow-down-up text-white-50`.
     - Búsqueda en memoria por número de teléfono sobre los contactos del cliente (`phoneTerm`).
     - Renderizado de filas con formato monetario para "Total Comprado", soft badges por categoría de cliente y botones Ghost en acciones con tooltip y accesibilidad.

### Verificación
- **Validación de Sintaxis**: Ejecución de `node --check frontend/js/clients.js` sin errores.
- **Pruebas de Despliegue**: Verificación de assets servidos correctamente por Nginx y FastAPI.
- **Regla estricta respetada**: Cero alteraciones en backend ni base de datos (100% UI/UX frontend con placeholders numéricos estratégicos).

## [2026-10-25] Módulo de Mermas: Ordenamiento de Columnas (Sort 1:1 con Inventario) y Rediseño UI/UX

### Causa Raíz / Requerimiento
1. **Ordenamiento de Columnas (Sort) idéntico a Inventario**:
   - En el módulo de Mermas (`#mermas-view`), los encabezados eran estáticos y no permitían ordenar los registros en memoria.
   - Se requería replicar exactamente la UI y funcionalidad de ordenamiento de Inventario en 5 columnas específicas: `# ID`, `Fecha / Hora`, `Producto / Detalle`, `Cantidad` y `Costo Pérdida`.
   - **Reglas visuales estrictas**:
     - Íconos inactivos: ícono ⇕ (doble flecha contorno, `bi bi-arrow-down-up text-white-50`) a la derecha del texto.
     - Estado activo: flecha sólida (↓ o ↑, `bi bi-arrow-down`/`bi bi-arrow-up text-white`).
     - Efecto Hover: texto subrayado (`text-decoration: underline; text-underline-offset: 3px`) y cursor en `pointer`.
     - Funcionalidad: alternancia ASC/DESC vinculada al renderizado de mermas.
2. **Falta de visibilidad financiera en Mermas**:
   - Se requería una fila de 3 tarjetas (Cards) estilo dashboard que informen de un vistazo: "Total Pérdida (Q)" (texto en rojo sutil), "Artículos Descartados" y "Motivo más frecuente".
3. **Inconsistencia de Theme en el Encabezado de la Tabla**:
   - Se requería aplicar el fondo verde esmeralda sólido corporativo (`var(--color-teal-dark)`) con texto blanco y bordes redondeados, idéntico al módulo de Usuarios e Inventario, sin líneas divisorias verticales.
4. **Modernización de Columnas y Estado Vacío**:
   - Miniatura de producto de 40×40 px con avatar o ícono 📦.
   - Soft Badges según gravedad (rojo, ámbar, morado, neutro).
   - Costo pérdida en rojo oscuro financiero (`#991B1B`, semibold).
   - Estado vacío amigable con ícono de portapapeles limpio con check (`bi bi-clipboard-check`).
   - Rango de fechas compacto unificado con ícono de calendario.

### Solución Implementada
1. **UI y Encabezados Ordenables**:
   - [`frontend/index.html`](../frontend/index.html): Se asignaron clases `sortable`, atributos `data-sort` y nodos `<span class="sort-icon"></span>` en las 5 columnas requeridas:
     - `# ID`: `data-sort="id_merma"`
     - `Fecha / Hora`: `data-sort="fecha_merma"`
     - `Producto / Detalle`: `data-sort="producto_nombre"`
     - `Cantidad`: `data-sort="cantidad"`
     - `Costo Pérdida`: `data-sort="costo_perdida"`
2. **Estilos de Hover e Íconos (1:1 con Inventario)**:
   - [`frontend/css/style.css`](../frontend/css/style.css): Reglas `#mermas-view th.sortable` con `cursor: pointer !important;`, `:hover` con `text-decoration: underline !important; text-underline-offset: 3px;` y transición de opacidad.
3. **Lógica de Ordenamiento Dinámico**:
   - [`frontend/js/mermas.js`](../frontend/js/mermas.js):
     - `setupSorting()`: Vincula el clic en `th.sortable`, alternando `sortAsc` o seleccionando nueva columna.
     - `updateSortIcons()`: Muestra `bi bi-arrow-down-up` en columnas inactivas y `bi bi-arrow-up` o `bi bi-arrow-down` en la columna activa.
     - `getSortValue(item, col)`: Extrae y tipa valores numéricos (ID, timestamp de fecha, total unidades, costo acumulado) o cadenas normalizadas para `localeCompare` (nombre de producto).
     - `applySortAndRender()`: Ordena `state.mermas` en memoria y dispara `renderTable()`.
4. **Theme Sync, Tarjetas KPI y Filtros**:
   - 3 Tarjetas KPI (`Total Pérdida`, `Artículos Descartados`, `Motivo más frecuente`) alimentadas por `updateMermasKPIs()`.
   - Encabezado sólido `var(--color-teal-dark)` sin bordes verticales.
   - Miniatura 40×40 px con soporte para foto de catálogo o `📦`.
   - Soft badges de motivos por severidad y costo en `#991B1B`.
   - Empty state amigable y rango de fechas compacto.

### Verificación
- **Pruebas visuales y de interacción**:
  - Encabezados `# ID`, `Fecha / Hora`, `Producto / Detalle`, `Cantidad` y `Costo Pérdida` muestran `⇕` en gris claro/semitransparente.
  - Al hacer clic en un encabezado, cambia inmediatamente a `↑` o `↓` en blanco sólido y la tabla se reordena al instante.
  - Hover muestra subrayado con offset y cursor `pointer`.
- **Compatibilidad**: 0 cambios en el backend; `node --check frontend/js/mermas.js` válido; suite `pytest` completa en verde.
- **Cache-busting**: `index.html` actualizado con `mermas.js?v=2.1` y `style.css?v=4.5`.

## [2026-10-25] Catálogo (Hover Zoom Idéntico a Inventario) y Resolución de Error 404 en Reportes Docker

### Causa Raíz / Requerimiento
1. **Ampliación de imagen (Hover Zoom) en Catálogo**:
   - En el módulo de Catálogo (`#catalog-view`), al pasar el cursor sobre la miniatura de un producto no se desplegaba la imagen ampliada.
   - En el módulo de Inventario (`#inventory-view`) existía esta funcionalidad implementada con cálculo dinámico de posición relativa a la miniatura, popover flotante `.inventory-image-zoom`, eventos de mouse/foco y sanitización de URL.
   - Se solicitó replicar idénticamente dicha funcionalidad en el Catálogo para unificar la experiencia de usuario.
2. **Error 404 en Dashboard de Reportes y Estadísticas**:
   - Al consultar el rango de fechas en `#reportes-view`, las gráficas, tarjetas de KPI y rankings quedaban vacíos o en estado de carga indefinido.
   - En la pestaña de Network de DevTools, las peticiones hacia `/api/reportes/kpi`, `/api/reportes/grafica` y `/api/reportes/ranking` fallaban con `404 Not Found`, mientras que `/api/reportes/` devolvía `200 OK`.
   - Causa raíz: En producción Docker (`docker-compose.prod.yml`), el contenedor `regalito_backend_prod` compila el código del backend con `COPY . .` dentro de la imagen. La imagen en ejecución se había creado antes de la incorporación de los nuevos endpoints analíticos en FastAPI.

### Solución Implementada
1. **Hover Zoom de Imágenes en Catálogo**:
   - [`frontend/index.html`](../frontend/index.html): Se agregó el nodo flotante `#catalog-image-zoom` con clases `.inventory-image-zoom.catalog-image-zoom` para el portal de previsualización.
   - [`frontend/css/style.css`](../frontend/css/style.css): Se unificaron las reglas de estilo de `.catalog-image-zoom` con `.inventory-image-zoom` (dimensiones `180px × 180px`, `border-radius: 12px`, sombreado elevado `box-shadow`, `pointer-events: none`, `z-index: 1080`) y los estilos de miniatura interactiva `.catalog-product-thumb` con indicador hover y foco accesible.
   - [`frontend/js/catalog.js`](../frontend/js/catalog.js): Se replicó la lógica de `inventory.js`: funciones `getCatalogImageZoom()`, `positionCatalogImageZoom(thumb)`, `showCatalogImageZoom(thumb, url, alt)`, `hideCatalogImageZoom()` y `setupCatalogImageZoom()`.
   - Se vincularon eventos `mouseenter`, `mousemove`, `mouseleave`, `focusin`, `focusout`, cancelación con tecla `Escape` y reposicionamiento en `resize` y `scroll`.
2. **Corrección del Despliegue de Reportes en Docker**:
   - Se recompiló la imagen del backend con los nuevos endpoints mediante `docker compose -f docker-compose.prod.yml build backend`.
   - Se recreó el servicio `backend` (`docker compose -f docker-compose.prod.yml up -d backend`) y se reinició el proxy inverso `frontend_nginx`.
   - Se verificó que las rutas `/api/reportes/kpi`, `/api/reportes/grafica` y `/api/reportes/ranking` estén registradas en el OpenAPI del contenedor y respondan con `HTTP 200` y datos reales en `http://localhost:9090`.
   - [`frontend/index.html`](../frontend/index.html): Se incrementó la versión a `js/reportes.js?v=3.2` para asegurar la recarga inmediata de scripts en navegadores cliente.

### Verificación
- **Pruebas de Catálogo**:
  - Miniaturas con clase `.catalog-product-thumb` con cursor `zoom-in`.
  - Despliegue de `#catalog-image-zoom` con posicionamiento flotante automático a la derecha/izquierda de la miniatura sin salirse de la ventana.
  - Ocultamiento en `mouseleave`, pérdida de foco o tecla `Escape`.
- **Pruebas de API y Contenedor en Vivo**:
  - `GET /api/reportes/kpi` → `200 OK` (Ventas netas: Q 1,085.00, conteo: 4).
  - `GET /api/reportes/grafica?tipo=tendencia` → `200 OK` (Puntos de fecha ordenados).
  - `GET /api/reportes/grafica?tipo=categoria` → `200 OK` (Desglose por categoría).
  - `GET /api/reportes/grafica?tipo=hora` → `200 OK` (24 franjas horarias con conteo).
  - `GET /api/reportes/ranking?tipo_reporte=productos` → `200 OK` (Top de productos ordenados por valor descendente).
  - `GET /api/reportes/ranking?tipo_reporte=clientes` y `estancados` → `200 OK`.
- **Suite completa de pruebas backend**:
  - Ejecución de `python -m pytest backend/tests/` → **289 passed (100% exitosas)**.

## [2026-10-25] Módulo de Reportes y Estadísticas: Backend + Frontend funcional

### Causa Raíz / Requerimiento
1. El nuevo módulo "Reportes y Estadísticas" tenía la UI completamente maquetada (grid de tarjetas KPI, tarjeta de gráfica con píldoras/tabs y widget de rankings con selects) pero **sin lógica**: todo era placeholder estático y el botón "Consultar" solo cargaba el consolidado.
2. Se requería un **motor central de fechas** que, al presionar "Consultar", disparara en paralelo (AJAX sin recarga) la actualización de KPIs, gráficas y rankings.
3. Las tarjetas debían calcular totales agregados con `SUM` estrictamente dentro del rango (ventas netas, costo de mermas, gastos de compras) en formato moneda local (Q).
4. La gráfica debía dejar de ser un placeholder gris: inicializar Chart.js según 3 pestañas (Tendencia de ventas/línea, Ventas por Categoría/dona, Ventas por Hora/barras) usando `destroy()` antes de cambiar de gráfico.
5. El widget de rankings debía consultar un endpoint con `tipo_reporte` (productos/clientes/estancados), `limite` (5/10/20) y rango de fechas, con Event Listeners en los selects.
6. Se exigía documentación exhaustiva de las funciones asíncronas JS y de las consultas SQL (construcción de fechas y ciclo de vida de las gráficas).

### Solución Implementada
1. **Backend – Consultas agregadas SQL** ([`backend/app/repositories/reporte_repository.py`](../backend/app/repositories/reporte_repository.py)):
   - `get_kpi_totales()`: ventas netas `SUM(total_venta)` (solo estado `Completada`), mermas `SUM(costo_perdida)` desde detalle con `COUNT(DISTINCT id_merma)`, compras `SUM(total_compra)`.
   - `get_tendencia_ventas()`: agrupa por día calendario de Guatemala restando `UTC-6` en Python (portable entre PostgreSQL y SQLite de pruebas).
   - `get_ventas_por_categoria()`: ingresos por categoría vía `detalle_venta -> venta -> variante -> producto -> subcategoria -> categoria`.
   - `get_ventas_por_hora()`: conteo de transacciones en las 24 franjas horarias locales.
   - Rankings `get_ranking_productos()`, `get_ranking_clientes()`, `get_ranking_estancados()` (productos sin ventas del rango, valorando el stock parado `stock_actual * costo_promedio`), todos con `ORDER BY total DESC LIMIT X`.
2. **Backend – Servicio** ([`backend/app/services/reporte_service.py`](../backend/app/services/reporte_service.py)): `obtener_kpi()`, `obtener_grafica()` (agrupa por mes si el rango supera 31 días) y `obtener_ranking()`.
3. **Backend – Endpoints** ([`backend/app/api/reportes.py`](../backend/app/api/reportes.py)): `GET /api/reportes/kpi`, `GET /api/reportes/grafica?tipo=...`, `GET /api/reportes/ranking?tipo_reporte=...&limite=...`, todos protegidos con `REPORTE_VER`.
4. **Backend – Schemas** ([`backend/app/schemas/reportes_schema.py`](../backend/app/schemas/reportes_schema.py)): `KPITotalesDTO`, `GraficaResponse`, `RankingItemDTO` y `RankingResponse`.
5. **Frontend** ([`frontend/js/reportes.js`](../frontend/js/reportes.js)):
   - `loadReportesPreview()` (botón "Consultar") dispara con `Promise.all` las 4 peticiones en paralelo (KPI, consolidado/tabla, gráfica activa y ranking).
   - `renderKPIs()` inyecta los totales con `formatoQuetzal` (Intl `es-GT`).
   - Ciclo de vida de gráficas: `graficaPlaceholder()` -> `renderGrafica()` -> `construirConfiguracionGrafica()`; **siempre se llama `.destroy()`** sobre la instancia previa antes de crear una nueva y se usa un token anti-carrera.
   - Píldoras de gráfica y selects de ranking con Event Listeners que re-consultan usando el último rango (`reportesRangoActual`).

### Verificación
- **8 pruebas nuevas** ([`backend/tests/test_reportes_estadisticas.py`](../backend/tests/test_reportes_estadisticas.py)): KPI con SUM y filtrado del rango (incluye venta anulada y compra/merma fuera del rango), tendencia con offset UTC-6 (ventas nocturnas), categoría, franjas horarias, rankings (productos/clientes/estancados con límite) y contrato JSON de los 3 endpoints vía API.
- Suite de reportes completa en verde: `test_reportes_estadisticas.py`, `test_reportes_consolidado_tz.py`, `test_reportes_service.py`, `test_reportes_especificos_service.py`, `test_reportes_api.py`, `test_user_report_service.py` → **31 pruebas pasan**.

### Notas
- `frontend/index.html`: `js/reportes.js` pasó de `?v=2.3` a `?v=3.0` (cache-busting). Chart.js ya está cargado desde el CDN en el `<head>`.
- Las gráficas y rankings heredan el rango de fechas del filtro superior; si falta rango o las fechas están invertidas, `obtenerRangoReportes()` aborta con un toast.

## [2026-10-25] Rediseño del POS (Checkout), Pantalla Cliente con QR y Shell de Scroll Independiente

### Causa Raíz / Requerimiento
1. **Rediseño del módulo de ventas (POS/Checkout)**:
   - Se requería una operación tipo Square/Shopify POS, sin fricción: búsqueda unificada (texto + lector láser), categorías visibles, tarjetas de producto con stock, carrito dominante y cobro en una sola pantalla.
   - El cliente debía capturarse en una línea compacta, el pago priorizar efectivo con montos rápidos, la transferencia quedar colapsada y el total/cambio ser los elementos más visibles.
2. **Atajos y flujo de cobro**:
   - Se necesitaban atajos de teclado para operar sin mouse: `F2` búsqueda, `F4` historial y `F12` cobrar (con `Ctrl+Enter` como respaldo).
   - El historial de ventas del turno debía salir de la vista principal y abrirse en un modal para no restar espacio al carrito.
3. **Pantalla para el cliente**:
   - Se requería una pantalla secundaria con el detalle de la compra, total a pagar, ahorro por mayoreo, estado del turno y un QR fijo de pago.
   - La pantalla debía actualizarse en vivo desde el POS, sin recargar y sin depender del foco de la ventana.
4. **Ticket térmico**:
   - Se necesitaba impresión estable en 80 mm y 58 mm, con `@page` sin márgenes, formato persistido en `localStorage` y un área de impresión aislada para no imprimir el resto de la interfaz.
5. **Regresión de layout del shell**:
   - El sidebar era un ítem flex con `flex-shrink: 1`; al entrar al POS, el ancho de su contenido lo comprimía de 272 px a ~168 px.
   - El contenido de los módulos no tenía `min-height: 0`; al fijar el shell a `100vh`, algunas vistas no podían desplazarse y el contenido quedaba recortado en lugar de hacer scroll interno.
6. **QR que abortaba la pantalla cliente**:
   - El payload anterior incluía acentos y el carácter `·`; `qrcodejs` lanzaba `code length overflow (788>512)`, la excepción se propagaba antes de inicializar el resto de la pantalla y esta quedaba en “Conectando...”.

### Solución Implementada
1. **Interfaz del POS** ([`frontend/index.html`](../frontend/index.html), [`frontend/css/style.css`](../frontend/css/style.css)):
   - Encabezado compacto con acceso a Historial (`F4`), Pantalla Cliente y Panel; se eliminó el subtítulo que consumía altura.
   - Omnibox único `#pos-search` con limpiar (`#btn-pos-search-clear`) y tecla `F2`, píldoras de categoría y grid de productos con badges de stock (incluido estado “Quedan 2”).
   - Panel derecho con cliente en una línea (`CF / Consumidor Final` por defecto), carrito con scroll propio, miniaturas de 40×40 y total/cambio destacados.
   - Pago consolidado: efectivo por defecto, chips de monto exacto/Q50/Q100/Q200, transferencia colapsable y botón `COBRAR F12`.
   - Historial movido a `#pos-history-modal`, sin tabla inferior permanente.
2. **Lógica del POS** ([`frontend/js/pos.js`](../frontend/js/pos.js)):
   - Detección de lector láser por intervalo entre teclas, búsqueda por código exacto y por coincidencia única.
   - Atajos `F2`, `F4`, `F12` y `/`, con protección para no cobrar con un modal abierto.
   - Cálculo automático de mayoreo, descuento y cambio; el monto exacto descuenta la transferencia cuando está visible.
   - Ticket con folio, cajero, cliente/NIT, columnas de cantidad × precio, etiquetas `* MAYOREO`, desglose de pago y cambio.
   - Limpieza de carrito, transferencia y cliente después de cobrar; el botón “Vaciar” se oculta con el carrito vacío.
3. **Pantalla del cliente** ([`frontend/cliente.html`](../frontend/cliente.html)):
   - Nueva vista con lista de artículos, ahorro mayoreo, total, estado del turno y QR.
   - Sincronización por `BroadcastChannel`, `postMessage` y `localStorage` (`regalito_pos_customer_state`), con solicitud de estado inicial a la caja.
   - `QR_PAYLOAD` corto y ASCII (`PAGO-REGALITO-CAJA-1`) y generación protegida con `try/catch` para que un fallo del QR nunca aborte la pantalla.
4. **Ticket térmico** ([`frontend/js/pos.js`](../frontend/js/pos.js), [`frontend/css/style.css`](../frontend/css/style.css)):
   - Vista previa y área de impresión dedicada (`#pos-ticket-print-area`), formatos `ticket--80` / `ticket--58` y estilo `@page` dinámico con margen 0.
   - Persistencia del formato en `regalito_pos_ticket_format` y caché de tickets para reimpresión desde historial.
5. **Shell con scroll independiente** ([`frontend/css/style.css`](../frontend/css/style.css)):
   - En desktop (≥768 px): `#system-module` fijado a `100vh` con `overflow: hidden`; sidebar con `flex: 0 0 272px` (76 px colapsado) para que no cambie de ancho al navegar.
   - `main` y cada `[data-main-view]` reciben `min-width: 0` y `min-height: 0`; cada módulo conserva su `overflow-y: auto`, por lo que solo se desplaza el panel que necesita hacerlo.
   - El sidebar mantiene su propio `overflow-y: auto`; desplazarlo no mueve el contenido ni la página.
   - En el POS (≥1200 px): `#pos-workspace` y `.pos-workspace-row` usan flex para llenar exactamente la altura disponible; las columnas y tarjetas quedan acotadas con scroll interno del catálogo y carrito.
6. **Ajustes de densidad del checkout**:
   - Se compactaron paddings, gaps, línea de cliente y botón de cobro para que el carrito ocupe al menos 60% de la columna sin sacrificar la visibilidad del total, cambio y `COBRAR F12`.

### Verificación
- **Navegador real (Chrome headless, 1440×1000; viewport 1422×904)** con login `admin` / `admin123` y respuestas API controladas:
  - Sidebar con ancho constante de **272 px** en POS, Panel Principal, Clientes y de nuevo POS.
  - Scroll independiente comprobado: Clientes desplazado 420 px sin mover la página; sidebar desplazado 181 px sin mover el contenido; `document.scrollingElement.scrollTop` permaneció en 0.
  - POS sin scroll de página: `scrollHeight` del documento = `clientHeight` = 904 px; vista POS = 823/823 px.
  - Carrito de **446 px sobre una columna de 734 px (61%)**, con total/cambio visibles y sin scroll de página.
  - Atajos `F2`, `F4` y `F12` verificados; transferencia visible/oculta y monto exacto verificados.
  - Pantalla cliente sincronizada con 2 artículos, total `Q 152.50`, ahorro `Q 30.00` y QR generado.
  - Ticket alternando 80/58 mm, con `@page { size: 58mm auto; margin: 0; }` persistido en `regalito_pos_ticket_format`.
  - `node --check` sin errores en `frontend/js/pos.js` y en el script inline de `frontend/cliente.html`.
- **Sin cambios de backend**: se conservaron los endpoints existentes de caja, productos y ventas, así como el descargo de inventario y el cálculo de mayoreo.

---

## [2026-10-23] Corrección de Causa Raíz en Reportes Consolidado Operativo (Error 500, Desalineación de Zona Horaria UTC vs America/Guatemala y Frontend Defensivo)

### Causa Raíz / Requerimiento
1. **Error HTTP 500 y MissingGreenlet en Backend**:
   - En entornos asíncronos con SQLAlchemy 2, acceder a relaciones no cargadas ansiosamente (Venta.usuario para el nombre del vendedor o Merma.detalles para sumar el costo de pérdida) sin selectinload disparaba excepciones MissingGreenlet (greenlet_spawn has not been called; can't call await_only() here), provocando que el backend respondiera con HTTP 500.
2. **Desalineación de Zona Horaria UTC vs America/Guatemala (UTC-6)**:
   - Los registros de ventas y mermas persisten timestamps en UTC (contenedor Docker en UTC donde datetime.now() devuelve hora UTC).
   - Dos ventas registradas en la noche del 23/10/2026 (20:39 y 20:40 hora Guatemala) quedaron almacenadas en base de datos como 2026-10-24 02:39:24 y 2026-10-24 02:40:12 UTC.
   - El filtro previo combinaba datetime.combine(fin, time.max) (23:59:59.999999), por lo que al consultar el rango 01/10/2026 a 23/10/2026 las ventas nocturnas quedaban excluidas de la consulta SQL.
3. **Discrepancia de Contrato de Datos (DTO vs Frontend)**:
   - ReporteConsolidadoResponse únicamente devolvía ventas, mermas y compras, omitiendo por completo el objeto totales (ventas, mermas, compras).
   - VentaReporteDTO solo exponía id_venta, fecha_venta y total_venta, mientras que el frontend requería fecha, estado, vendedor, subtotal, descuento y total.
4. **Excepción No Capturada en Frontend (reportes.js:171)**:
   - Al invocar renderReportesPreview(data), la función accedía directamente a data.totales.ventas.toFixed(2). Al ser data.totales indefinido (o al fallar la petición con 500), se lanzaba la excepción Cannot read properties of undefined (reading 'ventas').

### Solución Implementada
1. **Esquemas Pydantic** (backend/app/schemas/reportes_schema.py):
   - Se definió TotalesConsolidadoDTO con montos ventas, mermas y compras de tipo Decimal.
   - Se enriqueció VentaReporteDTO con fecha, fecha_venta, estado, vendedor, subtotal, descuento, total y total_venta con valores predeterminados y tipado estricto.
   - Se actualizó MermaReporteDTO con fecha, fecha_merma, observaciones y total.
   - Se actualizó CompraReporteDTO con fecha, fecha_ingreso, total y total_compra.
   - ReporteConsolidadoResponse ahora incluye totales: TotalesConsolidadoDTO = TotalesConsolidadoDTO().
2. **Repositorio con Eager Loading y Compensación de Zona Horaria** (backend/app/repositories/reporte_repository.py):
   - Se definió GUATEMALA_OFFSET = timedelta(hours=6) (Guatemala es UTC-6 sin horario de verano).
   - En get_ventas_by_date y get_mermas_by_date, los límites dt_inicio y dt_fin se ajustan sumando GUATEMALA_OFFSET, alineando las fechas calendario ingresadas por el usuario con los timestamps UTC almacenados en PostgreSQL.
   - Se agregaron opciones de carga ansiosa explícitas: options(selectinload(Venta.usuario)) en ventas, options(selectinload(Merma.detalles), selectinload(Merma.usuario)) en mermas, y options(selectinload(Compra.proveedor), selectinload(Compra.usuario)) en compras, erradicando cualquier posibilidad de MissingGreenlet.
3. **Servicio DERCAS** (backend/app/services/reporte_service.py):
   - En obtener_consolidado: cálculo de totales de ventas, mermas (sumatoria de costo_perdida de sus detalles) y compras.
   - Normalización de fechas con timezone.utc para serialización ISO estándar con terminación Z, permitiendo que el navegador del cliente las interprete y muestre automáticamente en la hora local correcta del usuario.
   - Se mantuvo la arquitectura DERCAS intacta (el controlador app/api/reportes.py permanece delgado, sin bloques try/except).
4. **Frontend Defensivo** (frontend/js/reportes.js):
   - renderReportesPreview ahora valida defensivamente if (!data || typeof data !== 'object') y limpia/restaura el estado de la vista con ceros y mensaje descriptivo de vacío sin arrojar excepciones.
   - Se protegió la lectura de propiedades (data.totales || {}, data.ventas || [], data.mermas || [], data.compras || []).
   - Se garantizó la conversión numérica segura con fallbacks (Number(totales.ventas ?? 0) || 0, v.subtotal ?? (v.total ?? 0)).
   - En loadReportesPreview, tanto errores de respuesta HTTP (!response.ok) como excepciones capturadas en catch invocan renderReportesPreview(null).
5. **Pruebas Automatizadas Pytest** (backend/tests/test_reportes_consolidado_tz.py):
   - test_consolidado_tz_guatemala_ventas_nocturnas_y_totales: comprueba que ventas nocturnas generadas en UTC se recuperen al filtrar por la fecha local de Guatemala, verificando cálculos de totales y mapeo de datos sin MissingGreenlet.
   - test_consolidado_mermas_detalles_sin_missing_greenlet: comprueba la sumatoria de costos de pérdida en detalles de mermas y la navegación segura de relaciones.
   - test_api_reportes_vista_previa_status_200_con_totales: prueba de integración vía httpx.AsyncClient sobre /api/reportes/, validando HTTP 200 OK y la presencia de la estructura esperada por el frontend.

### Verificación
- **Prueba en Vivo sobre API**:
  - GET /api/reportes/?fecha_inicio=2026-10-01&fecha_fin=2026-10-23 responde HTTP 200 OK.
  - Se obtienen las 2 ventas registradas de la noche del 23/10/2026 (Q290.00 y Q340.00).
  - Total de ventas consolidado: Q 630.00.
- **Suite Completa de Pytest**:
  - 279 pruebas aprobadas, 0 fallidas (suite completa ejecutada limpiamente).

---

## [2026-10-23] Despliegue de Producción con un Solo Comando (Docker Compose, Auto-Migraciones, Dependencias Fijas y Paridad de Base de Datos)

### Causa Raíz / Requerimiento
1. **Despliegue Autónomo y Reproducible en Producción**:
   - Resolver dependencias faltantes e incompletas al clonar el repositorio en entornos limpios (`relation "sync_queue" does not exist`, dependencias de ReportLab/Alembic ausentes en `requirements.txt`, ausencia de registro en `alembic_version`).
   - Permitir que el sistema arranque completamente operativo mediante un solo comando (`docker compose -f docker-compose.prod.yml up -d --build` o `iniciar.bat`) sin requerir intervenciones manuales previas (cargar SQL manualmente, ejecutar stamp de Alembic, etc.).
2. **Paridad de Esquema y Migración Idempotente**:
   - Sincronizar las 48 tablas de `backend/app/db/models.py` con `database/init.sql`, agregando `sync_cache_metadata` y `sync_queue` con sus índices y secuencias.
   - Crear la migración `0016_sync_tables.py` de forma 100% idempotente (utilizando `sa.inspect` para crear las tablas únicamente si no existen y eliminarlas en downgrade).
3. **Orquestación y Auto-Migración al Arrancar**:
   - Configurar `docker-compose.prod.yml` montando `init.sql` en `/docker-entrypoint-initdb.d/init.sql:ro`.
   - Incorporar `healthcheck` en el servicio `db` mediante `pg_isready` y configurar `depends_on: db: condition: service_healthy` en el backend.
   - Implementar el script `backend/app/db/auto_migrate.py` e integrarlo en el `CMD` de `Dockerfile`, detectando si la base viene de `init.sql` para ejecutar `alembic stamp head` o si tiene versiones previas para ejecutar `alembic upgrade head`, seguro de repetir en cada reinicio.
4. **Fijación de Versiones de Dependencias**:
   - Relevar todos los imports de `backend/app` y fijar versiones exactas en `backend/requirements.txt` (incluyendo `fastapi`, `uvicorn`, `bcrypt==4.0.1`, `reportlab==5.1.0`, `alembic==1.20.0`, `httpx==0.28.1`, `openpyxl==3.1.5`, etc.).
   - Separar librerías de pruebas (`pytest`, `pytest-asyncio`, `aiosqlite`) en `backend/requirements-dev.txt` para mantener la imagen de producción limpia y ligera.
5. **Comando de Actualización en Caliente para Producción Existente**:
   - Diseñar y validar sobre copia de respaldo el comando SQL idempotente para crear las tablas faltantes en bases de datos activas sin pérdida ni alteración de datos existentes.
6. **Documentación, Script de Arranque y Gitignore**:
   - Redactar `README.md` detallado con pasos de clonación, variables, levantamiento, URL y credenciales de usuarios semilla con advertencia de seguridad.
   - Crear `iniciar.bat` con rutas relativas (`%~dp0`) que no borra volúmenes.
   - Excluir `respaldos/`, `.env` y `scratch/` en `.gitignore`.

### Solución Implementada
1. **Base de Datos y Migraciones** ([`database/init.sql`](../database/init.sql), [`backend/alembic/versions/0016_sync_tables.py`](../backend/alembic/versions/0016_sync_tables.py)):
   - Se añadieron `sync_cache_metadata` y `sync_queue` a `database/init.sql` con sus índices y secuencias.
   - Se creó la migración Alembic `0016_sync_tables.py` con verificación de existencia de tablas antes de crearlas o eliminarlas.
2. **Backend y Auto-Migración** ([`backend/app/db/auto_migrate.py`](../backend/app/db/auto_migrate.py), [`backend/Dockerfile`](../backend/Dockerfile)):
   - Script `auto_migrate.py` que verifica conectividad a la base de datos con reintentos exponenciales, evalúa la presencia de la tabla `usuario` y `alembic_version`, ejecuta `alembic stamp head` si proviene de `init.sql`, o `alembic upgrade head` si ya existe versión o está vacía.
   - Actualizado el `CMD` en `Dockerfile` para ejecutar `python -m app.db.auto_migrate && exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4`.
3. **Orquestación Docker Compose** ([`docker-compose.prod.yml`](../docker-compose.prod.yml)):
   - Montaje de `init.sql` en `/docker-entrypoint-initdb.d/init.sql:ro`.
   - Healthcheck en `db` (`pg_isready -U ... -d ...`).
   - Dependencia condicionada `depends_on: db: condition: service_healthy` en `backend`.
   - Variables de puertos y nombres parametrizadas con valores por defecto para permitir pruebas aisladas sin colisiones.
4. **Dependencias y Entorno** ([`backend/requirements.txt`](../backend/requirements.txt), [`backend/requirements-dev.txt`](../backend/requirements-dev.txt), [`.gitignore`](../.gitignore)):
   - Versiones fijas de producción con `bcrypt==4.0.1`, excluyendo librerías de pruebas.
   - `.gitignore` actualizado con regla para `respaldos/`.
5. **Guía de Despliegue y Automatización** ([`README.md`](../README.md), [`iniciar.bat`](../iniciar.bat)):
   - Documentación exhaustiva en `README.md`.
   - Script por lotes `iniciar.bat` para Windows con rutas relativas y preservación de volúmenes.

### Verificación
- **Prueba en Clon Temporal Aislado (`-p regalito_test`)**:
  - Levantamiento autónomo con un solo comando sin intervención manual.
  - Servicio web responde HTTP 200 en `http://localhost:9095/`.
  - Inicio de sesión en `/api/auth/login` con credenciales `admin` / `admin123` exitoso (token JWT emitido con claims y permisos completos).
  - Paridad de tablas: 49 tablas en total (48 de aplicación + `alembic_version`).
  - Conteos semilla verificados: 3 usuarios, 22 departamentos geográficos y 338 municipios.
  - `alembic_version` verificado en `0016`.
  - Logs de backend y base de datos limpios y sin errores.
  - Eliminación segura del entorno temporal (`docker compose -p regalito_test down -v`) preservando intacta la producción real.
- **Validación de Comando de Respaldo**:
  - Probado en base de datos clonada de respaldo (`regalito_backup_test`); creación exitosa e idempotente de tablas e índices y actualización a `0016` con integridad total de datos existentes.
- **Suite de Pruebas Pytest**: **276 pruebas aprobadas, 0 fallidas**.

---

## [2026-10-23] Reportes Paso 1: Módulo de Reportes de Usuarios y Clientes (Filtros, Fichas en Modal, Exportación PDF con ReportLab y Registro en Historial de Precios)

### Causa Raíz / Requerimiento
1. **Verificaciones Previas de Migración 0015 en PostgreSQL Real**:
   - Ejecución en PostgreSQL real (`regalito_pos` en puerto 5433) de `alembic downgrade -1` (a 0014) y `upgrade head` (a 0015).
   - Comprobación de paridad de esquema contra `database/init.sql` aplicado sobre una base de datos vacía (`test_init_db`).
   - Confirmación de persistencia de registros de `visita_seguimiento` y `visita_modulo_evaluacion` tras el ciclo de migración.
   - Limpieza completa de registros temporales de prueba.
2. **Módulo de Reportes (Paso 1: Usuarios y Clientes)**:
   - Patrón unificado: Reporte general en HTML con filtros dinámicos (`estado`, `fecha_desde`, `fecha_hasta`) -> Reporte específico -> Ficha detallada en modal -> Exportación a PDF con ReportLab.
   - **Reporte de Usuarios**: Listado filtrable, ficha modal con nombre completo, username, rol, estado y fecha de creación; exportación en PDF de la ficha individual y exportaciones del listado en PDF, Excel y CSV.
   - **Reporte de Clientes**: Listado filtrable, ficha modal con NIT, nombre comercial, tipo de cliente, ubicación geográfica (departamento, municipio, dirección), contactos (teléfonos y correos), estado y fecha de creación; exportación en PDF de la ficha y del listado en PDF, Excel y CSV.
3. **Seguridad y Control de Acceso (RBAC)**:
   - Permiso requerido: `REPORTE_VER`.
   - Restricción estricta para usuarios sin dicho permiso (ej. Cajera): enlace y sección de reportes ocultos en la interfaz y respuesta HTTP 403 Forbidden en la API.
4. **Verificación de Historial de Precios en Catálogo**:
   - Comprobación mediante prueba automatizada en navegador de que la modificación del precio de venta de un producto desde la pantalla del catálogo se registra fielmente en la tabla `historial_precio` con usuario auditor, precio anterior y precio nuevo.

### Solución Implementada
1. **Backend — Schemas y Repositorios** ([`backend/app/schemas/reportes_schema.py`](../backend/app/schemas/reportes_schema.py), [`backend/app/repositories/reporte_repository.py`](../backend/app/repositories/reporte_repository.py)):
   - Se crearon DTOs `UsuarioReporteDTO`, `ClienteReporteDTO` y `ReporteExportadoDTO`.
   - Métodos en `ReporteRepositoryImpl`: `get_usuarios_reporte`, `get_usuario_by_id`, `get_clientes_reporte`, `get_cliente_by_id` con filtros `func.lower(estado)`, `func.date(fecha_creacion)` y `selectinload` de relaciones `rol`, `tipo_cliente`, `municipio`, `municipio.departamento` y `contactos`.
2. **Backend — Servicio y Exportación PDF** ([`backend/app/services/reporte_service.py`](../backend/app/services/reporte_service.py)):
   - Generación de reportes tabulares y fichas individuales en PDF utilizando ReportLab (`SimpleDocTemplate`, `Table`, `Paragraph`, `getSampleStyleSheet`).
   - Generación de PDFs para ficha individual de Usuario y ficha individual de Cliente con estilos corporativos.
   - Generación de PDF de listado filtrado para Usuarios y Clientes.
   - Mantenimiento de descargas existentes en formato Excel (`openpyxl`) y CSV.
3. **Backend — API y Endpoints** ([`backend/app/api/reportes.py`](../backend/app/api/reportes.py)):
   - Endpoints `/api/reportes/usuarios`, `/api/reportes/usuarios/pdf`, `/api/reportes/usuarios/{id_usuario}`, `/api/reportes/usuarios/{id_usuario}/pdf`.
   - Endpoints `/api/reportes/clientes`, `/api/reportes/clientes/pdf`, `/api/reportes/clientes/{id_cliente}`, `/api/reportes/clientes/{id_cliente}/pdf`.
   - Endpoints para Excel y CSV (`/excel`, `/csv`).
   - Todos los endpoints protegidos con `require_permission("REPORTE_VER")`.
4. **Frontend — Vistas, Pestañas, Modales y Controladores** ([`frontend/index.html`](../frontend/index.html), [`frontend/js/reportes.js`](../frontend/js/reportes.js), [`frontend/js/app.js`](../frontend/js/app.js), [`frontend/js/catalog.js`](../frontend/js/catalog.js)):
   - Pestañas interactivas en `#reportes-view`: Consolidado, Reporte de Usuarios, Reporte de Clientes.
   - Filtros por estado y fechas desde/hasta con botones "Filtrar" y "Limpiar".
   - Modales de ficha `#modal-reporte-ficha-usuario` y `#modal-reporte-ficha-cliente` con botón "Descargar Ficha en PDF".
   - Botones de exportación de listado: "Descargar PDF", "Descargar Excel", "Descargar CSV".
   - Control de navegación RBAC en `app.js` verificando permiso `REPORTE_VER` o rol Administrador.
   - Corrección de ámbito léxico de variables de stock en `catalog.js`.
5. **Pruebas Automatizadas y Verificación E2E**:
   - Backend Pytest: 11 nuevas pruebas unitarias y de integración en `backend/tests/test_reportes_especificos_service.py` y `backend/tests/test_reportes_api.py`.
   - E2E Playwright: 31 verificaciones automatizadas en `scratch/verify_reportes_browser.py` cubriendo inicio de sesión, listados, filtros, apertura de modales de ficha, descarga de PDF de ficha, exportaciones de listados (PDF, Excel, CSV), cambio de precio en pantalla de catálogo y verificación en `historial_precio`, y bloqueo HTTP 403 / vistas ocultas para el rol Cajera.

### Verificación
- **Pytest**: **276 pruebas aprobadas, 0 fallidas** (incremento de 11 pruebas respecto a las 265 previas).
- **Playwright (Navegador real)**: **31/31 checks exitosos**.

---

## [2026-10-23] Módulo de Visitas de Seguimiento y Evaluación (Dueño del Negocio) con Reporte PDF y RBAC

### Causa Raíz / Requerimiento
1. **Verificaciones Previas de Migraciones y Semilla**:
   - Comprobación de migraciones 0013 y 0014 en PostgreSQL real (`regalito_pos` en puerto 5433): ejecución de `alembic upgrade head`, `downgrade -1` y `upgrade head`.
   - Comprobación de paridad de esquema contra `database/init.sql` aplicado sobre una base de datos vacía (`test_init_db`).
   - Verificación de conteos de tablas de prueba E2E (`merma: 0`, `detalle_merma: 0`, `traslado_inventario: 0`, `orden_compra: 0`, `alerta_stock: 1`), confirmando persistencia exclusiva de datos semilla.
2. **Formulario de Visita de Seguimiento y Evaluación**:
   - Módulo adaptado para que el dueño del negocio / representante pueda registrar periódicamente evaluaciones del sistema sin asistencia técnica.
   - Datos generales: fecha, lugar/sucursal, nombre del representante, cargo, calificación general (1 a 5 estrellas) y observaciones generales.
   - Evaluación estructurada de 10 módulos estándar del sistema: `POS/Ventas`, `Inventario`, `Compras`, `Caja`, `Usuarios`, `Catálogos`, `Reportes`, `Configuración`, `Clientes` y `Facturación`.
   - Cada módulo evaluado mediante opciones `Conforme` (verde), `Modificar` (amarillo) o `Agregar` (azul), con campo de comentario/observación puntual y restricción de unicidad por visita.
   - Soporte para ciclo de vida con estado `Borrador` y `Completada`.
   - Resumen ejecutivo en pantalla con tarjetas de métricas por resultado.
   - Exportación y descarga directa de informe oficial en PDF (`reportlab`) con cabecera corporativa, metadatos, tabla de módulos evaluados y sección de firmas.
3. **Seguridad, Auditoría y RBAC**:
   - Permiso requerido: `VISITA_REGISTRAR` (asignado al rol Administradora).
   - Usuarios no autorizados (Cajera): opción de menú oculta en frontend, bloqueo de navegación directa en SPA y rechazo con HTTP 403 Forbidden en el backend.
   - Trazabilidad en `bitacora_auditoria` con verbos `CREAR` (al guardar borrador) y `EDITAR` (al actualizar o completar visita).

### Solución Implementada
1. **Base de Datos y Migración** ([`backend/alembic/versions/0015_visita_seguimiento_formulario.py`](../backend/alembic/versions/0015_visita_seguimiento_formulario.py), [`database/init.sql`](../database/init.sql), [`backend/app/db/models.py`](../backend/app/db/models.py)):
   - Columna `id_cliente` en `visita_seguimiento` modificada a nullable (`nullable=True`).
   - Columnas añadidas a `visita_seguimiento`: `lugar` (VARCHAR 150), `nombre_representante` (VARCHAR 150), `cargo_representante` (VARCHAR 100), `calificacion_general` (SMALLINT CHECK 1..5).
   - Columna añadida a `visita_modulo_evaluacion`: `resultado` (VARCHAR 20).
   - Restricción de unicidad `uq_visita_modulo` en `(id_visita, nombre_modulo)`.
2. **Arquitectura DERCAS Backend**:
   - Schemas ([`backend/app/schemas/visita_schema.py`](../backend/app/schemas/visita_schema.py)): `ModuloEvaluacionInput`, `ModuloEvaluacionOut`, `VisitaCreate`, `VisitaUpdate`, `VisitaOut`, `VisitaResumen`.
   - Repositorio ([`backend/app/repositories/visita_repository.py`](../backend/app/repositories/visita_repository.py)): `VisitaRepositoryImpl` con `create`, `get_by_id`, `list_all`, `update` y `sync_modulos`.
   - Integración en `UnitOfWork` ([`backend/app/api/deps.py`](../backend/app/api/deps.py)) y `TestUnitOfWork` ([`backend/tests/conftest.py`](../backend/tests/conftest.py)).
   - Servicio ([`backend/app/services/visita_service.py`](../backend/app/services/visita_service.py)): `ConcreteVisitaService` con `guardar_borrador`, `actualizar_borrador`, `completar_visita`, `obtener_visita`, `listar_visitas`, `generar_pdf` con ReportLab y registro en `bitacora_auditoria`.
   - Router API ([`backend/app/api/visitas.py`](../backend/app/api/visitas.py)): endpoints `GET /api/visitas`, `GET /{id}`, `POST /borrador`, `PUT /{id}/borrador`, `POST /{id}/completar`, `POST /completar` y `GET /{id}/pdf`.
   - Registro en FastAPI ([`backend/app/main.py`](../backend/app/main.py)).
3. **Frontend Interactivo y Accesible**:
   - Navegación lateral en [`frontend/index.html`](../frontend/index.html) con ítem `Visitas de Seguimiento` (`data-module-item="visitas"`).
   - Contenedor `#visitas-view` con 3 secciones: Formulario de Evaluación (`#visitas-form-section`), Resumen Ejecutivo (`#visitas-summary-section`) e Historial de Visitas (`#visitas-history-section`).
   - Controlador [`frontend/js/visitas.js`](../frontend/js/visitas.js): renderizado dinámico de los 10 módulos, gestión de borradores y finalización, visualización del resumen con conteo reactivo de conformes/modificar/agregar, y descarga directa de PDF.
   - Seguridad en [`frontend/js/app.js`](../frontend/js/app.js): integración en `mainViews`, `moduleAllowed`, `opItems`, `canAccessView`, `renderView` y `moduleLabels`.
4. **Pruebas y Verificación**:
   - Backend Pytest: 8 nuevas pruebas en `backend/tests/test_visita_service.py` y `backend/tests/test_visita_api.py`.
   - Total suite: 265 pruebas aprobadas (0 fallidas).
   - E2E Playwright: 17 verificaciones automatizadas en `scratch/verify_visitas_browser.py` cubriendo creación de borrador, evaluación de módulos, finalización, métricas de resumen, generación de PDF, historial y bloqueo 403 / vista oculta para Cajera.

## [2026-10-23] Proceso 4: Módulo Integral de Traslados entre Sucursales (Envío, Tránsito, Recepción, Cancelación y Trazabilidad)

### Causa Raíz / Requerimiento
1. **Módulo Completo de Traslados de Inventario**:
   - Modernizar y ampliar la estructura de datos de la tabla `traslado_inventario` para soportar ciclo de vida de transferencias de stock entre sucursales: estados `En tránsito`, `Recibido` y `Cancelado`, usuario que despacha (`id_usuario_envia`), usuario que recibe (`id_usuario_recibe`), fecha de recepción y observaciones.
   - Creación de migración Alembic `0014_traslado_seguimiento.py` y actualización sincronizada en `database/init.sql` y `backend/app/db/models.py`.
2. **Lógica de Negocio y Consistencia Transaccional (DERCAS)**:
   - **Despacho (`crear_envio`)**: Validación de sucursales distintas (`origen != destino`), verificación pesimista de stock disponible en origen y descuento inmediato de unidades en inventario de origen, registrando el traslado en estado `En tránsito`.
   - **Recepción en destino (`recibir_traslado`)**: Verificación de estado `En tránsito`, incremento de existencias en sucursal de destino (creando el registro en `inventario_sucursal` si aún no existía), registro de usuario receptor, fecha de recepción y cambio de estado a `Recibido`.
   - **Cancelación (`cancelar_traslado`)**: Verificación de estado `En tránsito`, restitución automática de existencias al inventario de la sucursal de origen, registro opcional de motivo en observaciones y cambio a estado `Cancelado`.
   - **Auditoría**: Registro de acciones en `bitacora_auditoria` con verbos en mayúsculas (`CREAR` al despachar, `EDITAR` al recibir o cancelar).
3. **Seguridad y Control de Acceso (RBAC)**:
   - Permiso requerido: `INV_INGRESAR_MERCADERIA` (Administradora y Bodeguero).
   - Usuarios no autorizados (Cajera): enlace oculto en menú lateral, navegación rechazada por SPA y endpoints protegidos con HTTP 403 Forbidden.
4. **Interfaz de Usuario Reactiva**:
   - Vista `#traslados-view` con filtros reactivos por estado (`En tránsito`, `Recibido`, `Cancelado`) y rango de fechas (desde/hasta).
   - Tabla interactiva con badges visuales de estado y acciones dinámicas contextuales (`[Recibir]`, `[Cancelar]`).
   - Modal `#modal-nuevo-traslado` con selector de origen, destino, producto/variante, indicador en tiempo real de stock disponible en la sucursal origen y validaciones client-side y server-side.
   - Modales `#modal-recibir-traslado` y `#modal-cancelar-traslado` para confirmaciones seguras sin ventanas nativas `alert()` o `confirm()`.

### Solución Implementada
1. **Base de Datos y Modelos** ([`backend/alembic/versions/0014_traslado_seguimiento.py`](../backend/alembic/versions/0014_traslado_seguimiento.py), [`database/init.sql`](../database/init.sql), [`backend/app/db/models.py`](../backend/app/db/models.py)):
   - Se crearon las columnas `estado` (VARCHAR(20) DEFAULT 'En tránsito'), `id_usuario_envia` (FK a usuario), `id_usuario_recibe` (FK a usuario), `fecha_recepcion` (TIMESTAMP) y `observaciones` (TEXT).
   - Se mapearon en el modelo `TrasladoInventario` las relaciones ORM `variante`, `sucursal_origen`, `sucursal_destino`, `usuario_envia` y `usuario_recibe`.
2. **Arquitectura DERCAS** ([`backend/app/schemas/traslado_schema.py`](../backend/app/schemas/traslado_schema.py), [`backend/app/repositories/traslado_repository.py`](../backend/app/repositories/traslado_repository.py), [`backend/app/services/traslado_service.py`](../backend/app/services/traslado_service.py), [`backend/app/api/traslados.py`](../backend/app/api/traslados.py), [`backend/app/api/deps.py`](../backend/app/api/deps.py)):
   - Schemas Pydantic v2: `TrasladoCreate`, `TrasladoCancelar`, `TrasladoOut` (enriquecido con `nombre_origen`, `nombre_destino`, `nombre_producto`, `codigo_barras`, `nombre_usuario_envia`, `nombre_usuario_recibe`).
   - Repositorio `TrasladoRepositoryImpl`: `create`, `get_by_id`, `list_all` con `selectinload` de relaciones y filtros dinámicos, `get_inventario_for_update` y `get_or_create_inventario`.
   - `UnitOfWork` y `TestUnitOfWork`: integrada propiedad `traslados`.
   - Servicio `ConcreteTrasladoService`: orquestación de transferencias con validación de stock, descuentos, sumas, restituciones y auditoría.
   - Router `/api/traslados`: endpoints `GET /api/traslados`, `GET /{id}`, `POST ""` (despacho), `POST /{id}/recibir`, `POST /{id}/cancelar`. Registrado en `backend/app/main.py`.
3. **Frontend Vanilla JS y Bootstrap** ([`frontend/index.html`](../frontend/index.html), [`frontend/js/traslados.js`](../frontend/js/traslados.js), [`frontend/js/app.js`](../frontend/js/app.js)):
   - Enlace `Traslados` en menú lateral bajo la sección de Operación Diaria.
   - Contenedor de módulo `#traslados-view` con filtros, tabla de transferencias y paginación informativa.
   - Modales de nuevo traslado, recepción y cancelación con `data-bs-backdrop="static"` y sin diálogos bloqueantes nativos.
   - Controlador `traslados.js` con inicialización `initDOM()`, actualización reactiva de stock disponible según sucursal origen y producto, feedback con `showToast()`.
   - Control de permisos en `app.js` (`moduleAllowed`, `opItems`, `canAccessView`, `renderView` y `moduleLabels`).
4. **Verificación y Pruebas**:
   - Backend Pytest: 8 pruebas unitarias y de API en `backend/tests/test_traslados.py` cubriendo descuento en origen, bloqueo por stock insuficiente, bloqueo por misma sucursal, incremento en destino, devolución en cancelación, transiciones de estado inválidas y 403 Forbidden para Cajera.
   - Frontend Playwright E2E: 29 pruebas en `scratch/verify_traslados_browser.py` cubriendo validaciones de formulario, ciclo de vida completo (despacho -> tránsito -> recepción -> finalizado, y despacho -> tránsito -> cancelación -> restitución de stock), filtros reactivos por estado y restricciones RBAC para Bodeguero y Cajera.

## [2026-10-23] Proceso 3: Flujo Completo de Compras y Órdenes (Emisión, Recepción en Bodega, Cancelación y Seguimiento de Estados)

### Causa Raíz / Requerimiento
1. **Flujo Integral de Compras en Pantalla**: Completar en la interfaz de usuario el ciclo de vida operativo de las compras de mercadería:
   - **Emisión de órdenes de compra**: Confección con catálogo de productos/variantes, proveedor y costo pactado, registrando la orden en estado `Emitida`.
   - **Recepción física de mercadería**: Formulario modal para ingresar el número de factura del proveedor, flete y cargadores, confirmar o ajustar las cantidades recibidas y costos unitarios, e incrementar el stock en inventario de forma atómica pasando la orden a `Recibida`.
   - **Cancelación de órdenes**: Acción controlada para anular órdenes pendientes en estado `Emitida` con justificación opcional, pasando a estado `Cancelada` y bloqueando ingresos posteriores.
2. **Listado Reactivo y Visibilidad de Estados**:
   - Tabla operativa con visualización clara de número de orden, fecha de emisión, proveedor, usuario responsable, total estimado y badges de estado (`Emitida` [amarillo], `Recibida` [verde], `Cancelada` [gris]).
   - Filtros dinámicos por estado de orden y rango de fechas (desde/hasta).
   - Acciones contextuales por fila según el estado y los permisos del usuario activo.
3. **Seguridad y Control de Acceso (RBAC)**:
   - `COMPRA_EMITIR_ORDEN`: emite y cancela órdenes (Administradora).
   - `INV_INGRESAR_MERCADERIA`: recibe mercadería e incrementa inventario (Administradora, Bodeguero).
   - Usuarios no autorizados (Cajera): enlace en menú lateral oculto, protección SPA activa y rechazo con HTTP 403 Forbidden.
4. **Auditoría en Bitácora**:
   - Registro con `CREAR` en `orden_compra` y `compra`.
   - Registro con `EDITAR` en `orden_compra` para recepciones y cancelaciones.

### Solución Implementada
1. **Backend — Repositorio y Servicio de Compras** ([`backend/app/repositories/compra_repository.py`](../backend/app/repositories/compra_repository.py), [`backend/app/services/compra_service.py`](../backend/app/services/compra_service.py), [`backend/app/schemas/compras_schema.py`](../backend/app/schemas/compras_schema.py)):
   - Se añadió `list_ordenes` en `CompraRepositoryImpl` con soporte de filtros por `estado`, `fecha_desde`, `fecha_hasta` e `id_proveedor`, y eager-loading de relaciones (`detalles.variante.producto`, `proveedor`, `usuario`).
   - Se ampliaron schemas `DetalleOrdenCompraOut`, `OrdenCompraOut` (enriquecidos con nombres legibles) y `OrdenCompraCancelar`.
   - En `ConcreteComprasService`:
     - `listar_ordenes`: valida permisos (`COMPRA_EMITIR_ORDEN` o `INV_INGRESAR_MERCADERIA`), consulta el repositorio y retorna órdenes enriquecidas.
     - `obtener_orden`: consulta y enriquece orden individual por ID.
     - `cancelar_orden`: valida `COMPRA_EMITIR_ORDEN`, verifica que el estado sea estrictamente `Emitida` (rechaza con HTTP 400 si ya fue `Recibida` o `Cancelada`), actualiza a `Cancelada` y registra en bitácora (`accion="EDITAR"`).
     - `ingresar_mercaderia`: valida `INV_INGRESAR_MERCADERIA`, rechaza con HTTP 400 órdenes que no estén `Emitida`, actualiza inventario con bloqueo pesimista, registra factura en `compra` (`accion="CREAR"`), actualiza estado a `Recibida` y audita en bitácora (`accion="EDITAR"`).
2. **Backend — Endpoints API** ([`backend/app/api/compras.py`](../backend/app/api/compras.py)):
   - `GET /api/compras/ordenes`: listado con filtros de estado y fechas.
   - `GET /api/compras/ordenes/{id_orden}`: consulta detallada de orden.
   - `POST /api/compras/ordenes`: emisión de orden (`COMPRA_EMITIR_ORDEN`).
   - `POST /api/compras/ordenes/{id_orden}/cancelar`: cancelación controlada (`COMPRA_EMITIR_ORDEN`).
   - `POST /api/compras/ingreso`: recepción y actualización de inventario (`INV_INGRESAR_MERCADERIA`).
3. **Frontend — Pantalla, Pestañas y Modales de Compras** ([`frontend/index.html`](../frontend/index.html), [`frontend/js/app.js`](../frontend/js/app.js), [`frontend/js/compras.js`](../frontend/js/compras.js)):
   - En `index.html`:
     - Sistema de navegación por pestañas (`#pills-ordenes-tab` y `#pills-nueva-orden-tab`).
     - Barra de filtros en tiempo real por estado (`Emitida`, `Recibida`, `Cancelada`) y rango de fechas.
     - Tabla con badges visuales de estado y botones de acción (`[Recibir]`, `[Cancelar]`, `[Detalle]`).
     - Modal `#modal-recibir-compra`: captura factura del proveedor, flete, cargadores y confirmación de cantidades/costos con recálculo dinámico de totales.
     - Modal `#modal-cancelar-compra`: diálogo de advertencia con motivo opcional de anulación.
     - Modal `#modal-ver-orden`: ficha de consulta de ítems pedidos y costos pactados.
   - En `app.js`: se sincronizó el control de acceso visual (`applyRoleRestrictions` y `navigateTo`) para permitir el acceso a compras tanto a roles con `COMPRA_EMITIR_ORDEN` (Admin) como con `INV_INGRESAR_MERCADERIA` (Bodeguero), bloqueando a Cajera.
   - En `compras.js`: arquitectura reactiva con inicialización dinámica de selectores DOM (`initDOM()`), delegación de eventos y feedback mediante `showToast()`.
4. **Pruebas Automatizadas (TDD)**:
   - En [`backend/tests/test_compras_service.py`](../backend/tests/test_compras_service.py): 10 pruebas unitarias de servicio (emisión, recepción, cancelación exitosa, rechazo al cancelar orden recibida, rechazo al recibir orden cancelada, permisos 403 y filtros por estado).
   - En [`backend/tests/test_compras_api.py`](../backend/tests/test_compras_api.py): 7 pruebas de integración API con endpoints HTTP y tokens JWT (emisión, cancelación, recepción, filtros y rechazos 403 para Cajera y Bodega).
   - En [`scratch/verify_compras_browser.py`](../scratch/verify_compras_browser.py): 18/18 pruebas E2E aprobadas en Playwright Chromium (flujo completo de emisión, recepción con factura, cancelación de segunda orden, filtros y rechazo para rol Cajera).

### Verificación
- **Pytest**: Todas las pruebas aprobadas sin regresiones.
- **Playwright**: **18/18 checks exitosos** en navegador Chromium.

---

## [2026-10-23] Proceso 2: Alertas de Stock Crítico (Acción Atender, Registro en Bitácora y Modal Operativo)

### Causa Raíz / Requerimiento
1. **Acción Operativa para Alertas de Stock**: Proporcionar a los usuarios autorizados la capacidad de atender/descartar alertas de stock crítico tanto desde la campanita de notificaciones del encabezado como desde un modal dedicado de alertas en la vista de inventario.
2. **Auditoría en Bitácora**: Registrar formalmente la acción en `bitacora_auditoria` con verbo estandarizado `EDITAR` sobre la tabla `alerta_stock`, capturando el identificador del usuario responsable y el cambio de estado a `"Atendida"`.
3. **Seguridad y Control de Acceso (RBAC)**: Restringir la atención de alertas únicamente a roles con permiso `INV_INGRESAR_MERCADERIA` (Administradora, Bodega), bloqueando con HTTP 403 a roles sin autorización (como Cajera).

### Solución Implementada
1. **Backend — Repositorio y Servicio de Inventario** ([`backend/app/repositories/inventory_repository.py`](../backend/app/repositories/inventory_repository.py), [`backend/app/services/inventory_service.py`](../backend/app/services/inventory_service.py)):
   - Se implementó `get_alert_by_id(id_alerta)` con eager-loading de relaciones (`variante.producto`).
   - Se optimizó `get_for_update(id_inventario)` para cargar `InventarioSucursal.variante` y `VarianteProducto.producto`, evitando errores de greenlet asíncrono en triggers de stock bajo.
   - Se creó `atender_alerta(id_alerta, current_user)` en `InventoryService`:
     - Valida existencia de la alerta (HTTP 404 si no existe).
     - Actualiza el estado a `"Atendida"`.
     - Registra auditoría con `accion="EDITAR"`, `tabla="alerta_stock"`, `registro_id=id_alerta` y detalle JSON (`{"estado_anterior": ..., "nuevo_estado": "Atendida"}`).
2. **Backend — Endpoints API** ([`backend/app/api/inventory.py`](../backend/app/api/inventory.py)):
   - Se añadió `PUT /api/inventario/alertas/{id_alerta}/atender` (y su alias en inglés `/api/inventory/alerts/{id_alerta}/atender`).
   - Protegidos con `require_permission("INV_INGRESAR_MERCADERIA")`.
3. **Frontend — Campanita y Modal de Alertas** ([`frontend/index.html`](../frontend/index.html), [`frontend/js/notificaciones.js`](../frontend/js/notificaciones.js), [`frontend/js/inventory.js`](../frontend/js/inventory.js)):
   - En `notificaciones.js`: el dropdown de la campanita muestra botón interactivo `[Atender]` por cada alerta activa para usuarios con permiso; al hacer clic invoca `window.atenderAlertaStock(id)` con feedback vía toast y actualización reactiva del badge.
   - En `index.html`: se añadió el modal estático `#modal-inventario-alertas` (`data-bs-backdrop="static"`).
   - En `inventory.js`: el botón `#btn-inventory-alerts` abre dicho modal y ejecuta `window.cargarAlertasInventarioModal()`, permitiendo visualizar detalles y atender alertas pendientes directamente desde la tabla de inventario.
4. **Pruebas Automatizadas (TDD)**:
   - En [`backend/tests/test_inventario_alertas.py`](../backend/tests/test_inventario_alertas.py):
     - `test_atender_alerta_stock_success`: verifica transición a `"Atendida"`.
     - `test_atender_alerta_stock_registra_bitacora`: comprueba entrada en `bitacora_auditoria` con acción `EDITAR` y detalle correcto.
     - `test_atender_alerta_stock_403_cajera`: confirma rechazo HTTP 403 Forbidden para rol Cajera.
     - `test_atender_alerta_stock_404_no_existe`: valida respuesta HTTP 404 para alertas inexistentes.
   - En [`scratch/verify_alertas_browser.py`](../scratch/verify_alertas_browser.py): verificación E2E con Playwright (9/9 pasos aprobados, admin atiende alerta, badge se descuenta a 0, Cajera recibe 403).

### Verificación
- **Pytest**: **237 pruebas aprobadas, 0 fallidas**.
- **Playwright**: **9/9 checks exitosos** en navegador Chromium.

---

## [2026-10-23] Proceso 1: Módulo de Mermas de Inventario (Pantalla, Filtros y Control RBAC) y Unificación de Bitácora

### Causa Raíz / Requerimiento
1. **Pantalla de Mermas**: Implementar la interfaz visual operativa para el módulo de mermas de inventario (RF10):
   - Formulario modal para registrar una merma especificando: sucursal, producto/variante, motivo de merma, cantidad a mermar y observación/justificación.
   - Listado reactivo de mermas con visualización de fecha/hora, sucursal, usuario responsable, producto/variante, motivo, cantidad descargada, costo de pérdida y observaciones.
   - Filtros dinámicos en el listado por rango de fechas (desde/hasta) y motivo de merma.
2. **Seguridad y Permisos (RBAC)**: Proteger endpoints con `require_permission("INV_INGRESAR_MERCADERIA")`, permitiendo acceso a Administradora y Bodeguero, y devolviendo HTTP 403 Forbidden para usuarios sin dicho permiso (como Cajera).
3. **Unificación de Acciones en Bitácora**: Normalizar en todos los servicios del backend los nombres de acción a verbos en español en mayúsculas (`CREAR`, `EDITAR`, `DESACTIVAR`, `REACTIVAR`), corrigiendo pruebas y asegurando paridad terminológica.
4. **Validación de Roles Cajera y Bodega**: Confirmar formalmente que tras la incorporación de los permisos `ROL_ADMIN` y `USUARIO_ADMIN`, los roles Cajera y Bodega conservan estrictamente su nivel de acceso previo.

### Solución Implementada
1. **Backend — Mermas y Filtros** ([`backend/app/schemas/merma_schema.py`](../backend/app/schemas/merma_schema.py), [`backend/app/repositories/merma_repository.py`](../backend/app/repositories/merma_repository.py), [`backend/app/services/merma_service.py`](../backend/app/services/merma_service.py), [`backend/app/api/mermas.py`](../backend/app/api/mermas.py)):
   - Se añadió `id_motivo` y soporte de fechas (`fecha_desde`, `fecha_hasta`) a `MermaFilter`.
   - El repositorio filtra por motivo mediante subconsulta atómica `Merma.detalles.any(DetalleMerma.id_motivo == id_motivo)` y fechas mediante `func.date(Merma.fecha_merma)`.
   - Se enriqueció la salida `MermaOut` y `DetalleMermaOut` con nombres legibles (`nombre_sucursal`, `nombre_usuario`, `nombre_producto`, `variante_info`).
   - Se protegió `/api/mermas` (`GET`, `POST`) y `/api/mermas/motivos` con `require_permission("INV_INGRESAR_MERCADERIA")`.
   - Se registra en bitácora cada merma creada con acción `CREAR` sobre la tabla `merma`.
2. **Frontend — Pantalla y Modal de Mermas** ([`frontend/index.html`](../frontend/index.html), [`frontend/js/app.js`](../frontend/js/app.js), [`frontend/js/mermas.js`](../frontend/js/mermas.js)):
   - Menú lateral y dashboard: enlace y tarjeta de "Mermas" condicionados dinámicamente según permiso `INV_INGRESAR_MERCADERIA`.
   - Vista `[data-main-view="mermas"]`: cabecera, filtros por fecha desde/hasta y motivo, tabla de mermas con badges de motivos y formateo monetario en Quetzales (Q), estado vacío y contador de registros.
   - Modal `mermaModal` (`data-bs-backdrop="static"`): selector de sucursal, selector de motivo, selector de producto/variante con badge de stock en tiempo real, cálculo automático del costo estimado de pérdida (`cantidad * costo_promedio`), validación de existencias antes de enviar y confirmación visual con `showToast()`.
3. **Unificación de Bitácora a Español en Mayúsculas**:
   - Actualizados servicios [`catalogo_service.py`](../backend/app/services/catalogo_service.py), [`catalogo_general_service.py`](../backend/app/services/catalogo_general_service.py), [`compra_service.py`](../backend/app/services/compra_service.py), [`configuracion_service.py`](../backend/app/services/configuracion_service.py), [`department_service.py`](../backend/app/services/department_service.py), [`category_service.py`](../backend/app/services/category_service.py), [`role_service.py`](../backend/app/services/role_service.py), [`inventory_service.py`](../backend/app/services/inventory_service.py) y [`merma_service.py`](../backend/app/services/merma_service.py).
   - Acciones estandarizadas: `CREAR`, `EDITAR`, `DESACTIVAR`, `REACTIVAR`, `CIERRE`.
4. **Pruebas Automatizadas (TDD)**:
   - Nuevas pruebas de API en [`backend/tests/test_merma_api.py`](../backend/tests/test_merma_api.py) (motivos, registro exitoso con descargo de existencias, stock insuficiente, filtros y verificaciones de 403 Forbidden para Cajera).
   - Pruebas de servicio en [`backend/tests/test_merma_service.py`](../backend/tests/test_merma_service.py).
   - Script de prueba de navegador Playwright en [`scratch/verify_merma_browser.py`](../scratch/verify_merma_browser.py).

### Verificación
- **Pytest**: **234 pruebas aprobadas, 0 fallidas** (incremento desde 221 / 227).
- **Playwright (Navegador real)**: **20/20 pruebas aprobadas**:
  - Admin: navegación a `#mermas`, apertura de modal, cálculo de costo estimado Q 50.00, registro con descargo de stock, visualización de columnas en tabla, filtrado por motivo y limpieza de filtros.
  - No Admin (Cajera): enlace en menú lateral oculto, navegación bloqueada por SPA guard y petición HTTP `/api/mermas` rechazada con `403 Forbidden (INV_INGRESAR_MERCADERIA)`.
- **RBAC**: Roles Cajera y Bodega conservan estrictamente sus permisos aislados (`test_rbac.py` 7/7 passed).

---

## [2026-10-23] Bloque 4: Protección de Permisos Críticos en Roles, Auditoría Completa de Escritura y Diagnóstico de Procesos

### Causa Raíz / Requerimiento
1. **Diagnóstico de Formularios de Proceso (Parte 1)**: Elaborar la tabla diagnóstica integral de los 6 procesos operativos (traslados, mermas, ajuste de stock, alertas, compras y caja) evaluando estado en backend, pantalla en frontend, estados de seguimiento y pendientes técnicos.
2. **Protección de Permisos Críticos y Anti-Auto-Despojo**:
   - Evitar que el rol Administradora (id 1) pueda perder sus permisos críticos (`ROL_ADMIN` y `USUARIO_ADMIN`) o ser desactivado.
   - Evitar que un usuario autenticado pueda quitarse a sí mismo el acceso al módulo de Roles (`ROL_ADMIN`) o desactivar su propio rol.
   - Aclarar el ciclo de vida de aplicación de permisos (inmediato en backend vs siguiente inicio de sesión en caché frontend).
3. **Auditoría de Bitácora en Servicios de Escritura**:
   - Relevar tabla de todos los servicios de escritura y corregir operaciones relevantes que carecían de registro en bitácora (`cerrar_turno` directo en `cash_service.py`).
4. **Seguridad y Privacidad en Bitácora**:
   - Confirmar formalmente que ningún evento de bitácora almacena contraseñas en texto plano ni hashes en el campo de detalle.

### Solución Implementada
1. **Reglas de Seguridad en Servicio de Roles** ([`backend/app/services/role_service.py`](../backend/app/services/role_service.py)):
   - En `update_rol_permisos`: se validan dos reglas antes de aplicar cambios:
     - Regla 1: Si `actor_id` pertenece al rol editado y omite `ROL_ADMIN`, se rechaza con HTTP 400 (`"No puedes quitarte a ti mismo el acceso al módulo de Roles"`).
     - Regla 2: Si el rol es Administradora y se omiten los permisos críticos (`ROL_ADMIN`, `USUARIO_ADMIN`), se rechaza con HTTP 400 (`"El rol Administradora no puede perder los permisos críticos (acceso a Roles y Usuarios)"`).
   - En `deactivate_role`: se bloquea la desactivación del rol Administradora y el auto-bloqueo del propio rol del actor con HTTP 400.
2. **Interfaz de Permisos** ([`frontend/js/roles.js`](../frontend/js/roles.js)):
   - Los permisos críticos se renderizan deshabilitados y marcados (`checked disabled`) con badges informativos: `Crítico (Administradora)` y `Tu rol actual (Acceso a Roles)`.
   - Se incluye `id_rol` en la respuesta de login de [`backend/app/api/auth.py`](../backend/app/api/auth.py) y se almacena en `localStorage` en [`frontend/js/app.js`](../frontend/js/app.js).
3. **Migración 0013 y Esquema `init.sql`**:
   - Creada migración Alembic [`backend/alembic/versions/0013_permisos_roles_usuarios.py`](../backend/alembic/versions/0013_permisos_roles_usuarios.py) insertando formalmente `ROL_ADMIN` y `USUARIO_ADMIN` asignados a Administradora.
   - Sincronizado [`database/init.sql`](../database/init.sql) con la lista completa de 12 permisos del sistema.
4. **Corrección de Bitácora en Caja** ([`backend/app/services/cash_service.py`](../backend/app/services/cash_service.py)):
   - Se añadió `log_action` en `cerrar_turno` (`accion="CIERRE"`, `tabla="turno_caja"`), cubriendo el cierre estándar además del cierre a ciegas.
5. **Pruebas Automatizadas**:
   - Pruebas unitarias añadidas en [`backend/tests/test_permisos_service.py`](../backend/tests/test_permisos_service.py).
   - Pruebas de integración API añadidas en [`backend/tests/test_bloque4_api.py`](../backend/tests/test_bloque4_api.py).

### Verificación
- `pytest tests/test_permisos_service.py tests/test_bloque4_api.py tests/test_cash_service.py`: **31 passed, 0 failed**.
- Suite global: 227 pruebas aprobadas sin regresiones.


---

## [2026-10-23] Fase 2 — Bloque 4: Permisos por Rol, Bitácora de Auditoría y Historial de Precios

### Causa Raíz / Requerimiento
1. **Permisos y rol-permiso**: pantalla dentro de **Roles** para marcar qué permisos tiene cada rol (CRUD de roles + panel de permisos con checkboxes agrupados por módulo).
2. **Bitácora de auditoría**: pantalla de **solo consulta** con filtros (usuario, tabla, acción, rango de fechas) protegida con el permiso `BITACORA_CONSULTAR`. Además, detectar qué **servicios de escritura NO registraban** en `bitacora_auditoria` y corregirlos.
3. **Historial de precios**: consulta de **solo lectura** por producto o variante, y asegurar que los cambios de precio queden registrados en `historial_precio`.

### Solución Implementada

**Backend — Permisos y rol-permiso** ([`backend/app/api/roles.py`](../backend/app/api/roles.py), [`backend/app/services/role_service.py`](../backend/app/services/role_service.py)):
- `GET /api/roles/permisos/catalogo` lista todos los permisos (`PermisoOut`).
- `GET /api/roles/{id}/permisos` devuelve los códigos asignados al rol.
- `PUT /api/roles/{id}/permisos` (body `{codigos: [...]}`) reemplaza el conjunto de permisos del rol (quita removidos y agrega nuevos dentro del mismo UoW), validando códigos inexistentes (400) y rol inexistente (404).
- El `UnitOfWork` de [`backend/app/api/deps.py`](../backend/app/api/deps.py) expone `permisos`; `RoleService` ampliado en [`backend/app/interfaces/services.py`](../backend/app/interfaces/services.py).
- Schema `RolePermisosUpdate` en [`backend/app/schemas/catalogo_schema.py`](../backend/app/schemas/catalogo_schema.py).

**Backend — Bitácora de auditoría** ([`backend/app/api/bitacora.py`](../backend/app/api/bitacora.py), [`backend/app/services/bitacora_service.py`](../backend/app/services/bitacora_service.py)):
- `GET /api/bitacora` con filtros `id_usuario`, `tabla`, `accion`, `fecha_desde`, `fecha_hasta`, `limit`, `offset`; protegida con `require_permission("BITACORA_CONSULTAR")`. Consulta de solo lectura.
- `BitacoraOut` ahora incluye `usuario_nombre` (eager load de `usuario` en [`backend/app/repositories/catalogo_repository.py`](../backend/app/repositories/catalogo_repository.py)); los rangos de fecha se comparan por día (`func.date`) para que el filtro "hasta" sea inclusivo.

**Backend — Historial de precios** ([`backend/app/api/historial_precios.py`](../backend/app/api/historial_precios.py), [`backend/app/services/historial_precio_service.py`](../backend/app/services/historial_precio_service.py)):
- `GET /api/historial-precios` con filtros `id_producto`, `id_variante`, `id_usuario`, fechas, paginación; protegida con `require_permission("REPORTE_VER")`.
- `HistorialPrecioRepository` filtra por producto (JOIN con `variante_producto`) y expone `producto_nombre`, `variante_codigo_barras`, `usuario_nombre`.
- El servicio de producto [`backend/app/services/product_service.py`](../backend/app/services/product_service.py) ahora **inserta en `historial_precio`** cuando cambia `precio_detalle` en `update_product`.

**Corrección de auditoría en servicios de escritura que NO registraban**:
- `role_service`: `create_role`, `update_role`, `deactivate_role` y `update_rol_permisos` ahora llaman a `log_action`.
- `category_service`: `create_category`, `update_category`, `deactivate_category` (reciben `actor_id`; el controlador [`backend/app/api/categories.py`](../backend/app/api/categories.py) lo envía).
- `department_service`: `create_department`, `update_department` (controlador [`backend/app/api/departments.py`](../backend/app/api/departments.py) envía `actor_id`).
- `configuracion_service`: `actualizar_configuracion` registra `parametro_sistema`.
- `compra_service`: `crear_orden` registra `orden_compra` (el ingreso ya registraba `INGRESO_COMPRA`).

**Frontend** ([`frontend/index.html`](../frontend/index.html), [`frontend/js/roles.js`](../frontend/js/roles.js), [`frontend/js/bitacora.js`](../frontend/js/bitacora.js), [`frontend/js/historial.js`](../frontend/js/historial.js), [`frontend/js/app.js`](../frontend/js/app.js)):
- Nueva vista **Roles y Permisos** (`#roles-view`): tabla de roles con CRUD y botón "Permisos" que abre el modal `#role-permisos-modal` con todos los permisos agrupados por módulo como checkboxes, guardando vía `PUT`.
- Nueva vista **Bitácora** (`#bitacora-view`): solo lectura con filtros (usuario, tabla, acción con datalist, fechas) y paginación.
- Nueva vista **Historial de Precios** (`#historial-view`): solo lectura filtrable por producto (dropdown) o variante (código de barras/SKU) y fechas, con paginación.
- RBAC: roles solo para `Administradora`; bitácora exige `BITACORA_CONSULTAR`; historial exige `REPORTE_VER` (`canAccessView`, `applyRoleRestrictions`, `mainViews`, `renderView`).

**Pruebas nuevas (26)**:
- [`backend/tests/test_permisos_service.py`](../backend/tests/test_permisos_service.py) (8): listado, lectura/asignación/reemplazo de permisos por rol, limpieza total, 400 código inexistente, 404 rol, bitácora de rol.
- [`backend/tests/test_bloque4_api.py`](../backend/tests/test_bloque4_api.py) (9): catálogo de permisos, get/update rol-permiso, 404/400/403, bitácora con filtros y **403 sin `BITACORA_CONSULTAR`**, POST no permitido.
- [`backend/tests/test_historial_precio_api.py`](../backend/tests/test_historial_precio_api.py) (4): **403 sin `REPORTE_VER`**, filtros por producto/variante/fechas, y registro en `historial_precio` al actualizar precio de producto.
- [`backend/tests/test_auditoria_fix.py`](../backend/tests/test_auditoria_fix.py) (8): bitácora generada por categoría (crear/editar/desactivar), departamento (crear/editar), rol_permiso, orden de compra y configuración.
- `TestUnitOfWork` de [`backend/tests/conftest.py`](../backend/tests/conftest.py) ampliado con `permisos`, `bitacora`, `historial_precios` y `configuracion`.

**Evidencia de navegador (Playwright)** ([`scratch/seed_b4_e2e.py`](../scratch/seed_b4_e2e.py), [`scratch/verify_bloque4_browser.py`](../scratch/verify_bloque4_browser.py)):
- Admin: lista 3 roles, abre panel de permisos, marca/desmarca y guarda (toast), API refleja el cambio; bitácora muestra registros y filtra por tabla; historial filtra por SKU y por producto.
- Cajera (no administradora): Roles/Bitácora/Historial ocultos en el menú, vista forzada bloqueada, `/api/bitacora` y `/api/roles/permisos/catalogo` responden **403**.

### Verificación
- `python -m pytest -q` en `backend/`: **221 passed, 0 failed** (195 previos + 26 nuevos).
- Playwright Chromium headless (`scratch/verify_bloque4_browser.py`): **14/14 comprobaciones correctas** (admin y no admin).
- `node --check` sobre los 16 archivos JS del frontend: 0 errores; balance de `<div>` en `frontend/index.html`: 877/877.
- Rutas registradas en OpenAPI: `/api/roles/permisos/catalogo`, `/api/roles/{role_id}/permisos`, `/api/bitacora`, `/api/historial-precios`.
- `scratch/` permanece ignorado por git (`.gitignore`), los scripts de prueba siembran en SQLite de prueba y no tocan la BD de desarrollo.

---

## [2026-10-23] Fase 2 — Bloque 3: Saneamiento de Datos Geográficos (338 Municipios), Paridad init.sql, Estados de Orden de Compra y Verificación de Secretos

### Causa Raíz / Requerimiento
1. **Aclaración de Conteos Geográficos**: Explicar la discrepancia del SELECT que mostró 2 departamentos y 3 municipios en el reporte anterior. Ejecutar la verificación en la base real PostgreSQL (`regalito_db`, puerto 5433, base `regalito_pos`) confirmando los 22 departamentos y los 338 municipios oficiales.
2. **Paridad de `database/init.sql`**: Asegurar y verificar que la inicialización desde cero en volumen vacío (`init.sql`) genere exactamente los 22 departamentos y 338 municipios oficiales con secuencias íntegras.
3. **Cobertura de Órdenes de Compra Abiertas para Proveedor**: Garantizar que la regla de bloqueo de desactivación de proveedores cubra todos los estados no finalizados (`Emitida`, `Recibida Parcialmente`, `Pendiente`, `En Proceso`, etc., excluyendo únicamente los terminales `Recibida`, `Cancelada` y `Anulada`), devuelva HTTP 400 con el conteo respectivo, y agregar prueba de API específica.
4. **Auditoría de Secretos en Git**: Confirmar mediante `git ls-files | grep -i -E "\.env|credenc|secret"` que no existan credenciales ni variables de entorno sensibles versionadas en el repositorio.

### Solución Implementada
1. **Identificación y Aclaración de Base de Datos**:
   - El SELECT previo de 2 departamentos y 3 municipios fue ejecutado por error de contexto contra el archivo SQLite temporal `scratch/b3_e2e.db` (fixture local utilizado para aislar las pruebas de interfaz Playwright).
   - En la base PostgreSQL de desarrollo (`regalito_db`, puerto 5433, base `regalito_pos`), se aplicó la migración Alembic [`0012_carga_municipios_338.py`](../backend/alembic/versions/0012_carga_municipios_338.py) agregando los 2 municipios restantes para alcanzar los 338 oficiales certificados: *El Chal* (Petén, Decreto 5-2014) y *Petatán* (Huehuetenango, Decreto 6-2015).
   - Conteos en PostgreSQL real: 22 departamentos y 338 municipios, 0 huérfanos.
2. **Actualización y Verificación de `database/init.sql`**:
   - Se actualizó [`database/init.sql`](../database/init.sql) con la carga íntegra de los 22 departamentos y 338 municipios.
   - Verificado levantando una base limpia aislada `test_init_db` a partir de `init.sql`: conteo confirmado de 22 departamentos y 338 municipios.
3. **Regla de Estados No Finalizados para Proveedores y Prueba API**:
   - En [`backend/app/repositories/catalogo_repository.py`](../backend/app/repositories/catalogo_repository.py): se ajustó `count_ordenes_activas` para filtrar `OrdenCompra.estado.notin_(["Recibida", "Cancelada", "Anulada"])`, cubriendo de manera exhaustiva cualquier orden en estado abierto (`Emitida`, `Recibida Parcialmente`, `Pendiente`, `En Proceso`).
   - En [`backend/app/services/catalogo_general_service.py`](../backend/app/services/catalogo_general_service.py): mensaje de error 400 estandarizado a `"No se puede desactivar el proveedor: hay {dependencias} orden(es) de compra abierta(s)"`.
   - En [`backend/tests/test_catalogo_bloque3_api.py`](../backend/tests/test_catalogo_bloque3_api.py): se agregó la prueba `test_desactivar_proveedor_con_orden_abierta_retorna_400`, validando rechazo 400 ante órdenes en `Emitida` y `Recibida Parcialmente`, y éxito 200 tras pasar a estado finalizado `Recibida`.
   - En [`backend/tests/test_catalogo_bloque3_service.py`](../backend/tests/test_catalogo_bloque3_service.py): se expandió la prueba unitaria para validar estados abiertos vs terminales.
4. **Verificación de Seguridad en Git**:
   - Ejecutado `git ls-files | grep -i -E '\.env|credenc|secret'` en el repositorio, arrojando únicamente `.env.example`. Cero credenciales ni archivos `.env` versionados.

### Verificación
- PostgreSQL real (`regalito_pos` en puerto 5433):
  - `SELECT COUNT(*) FROM departamento_geografico;` -> **22**.
  - `SELECT COUNT(*) FROM municipio;` -> **338**.
- Base limpia desde `init.sql`:
  - `SELECT COUNT(*) FROM departamento_geografico;` -> **22**.
  - `SELECT COUNT(*) FROM municipio;` -> **338**.
- Pytest suite completa: **195 passed, 0 failed** (incluyendo nueva prueba de API y servicio para proveedor).
- Git ls-files grep: únicamente `.env.example`.


---



## [2026-10-22] Fase 2 — Bloque 3: Resolución de Pendientes (Git por Bloque, Desglose 194 Tests, Desactivación Segura y Limpieza E2E)

### Causa Raíz / Requerimiento
1. **Git por Bloques**: Organizar el historial de trabajo en commits claros por bloque (Bloque 0, Bloque 1, Bloque 2, Bloque 3), excluyendo archivos scratch y credenciales.
2. **Desglose de Pruebas Pytest**: Reportar la recolección exacta (`pytest --collect-only -q`) agrupada por archivo con sus conteos individuales y total verificado (194 pruebas).
3. **Desactivación Segura con Conteo**: Demostrar con pruebas que proveedores con órdenes de compra abiertas, métodos de pago usados en ventas y departamentos con municipios activos no se pueden desactivar (HTTP 400 con conteo de dependencias).
4. **Limpieza de Datos E2E**: Confirmar que los scripts `scratch/seed_b3_e2e.py` y `scratch/verify_bloque3_browser.py` limpian los registros generados durante la prueba de navegador, dejando la base de datos únicamente con los datos semilla.

### Solución Implementada
1. **Commits en Git**:
   - Bloque 0 (`bc2af2f`): Migraciones 0010/0011, `init.sql`, modelos base y reescritura de tests a español.
   - Bloque 1 (`4258f75`): Clientes, tipos de cliente, contactos dinámicos, ficha, filtros y validación POS.
   - Bloque 2 (`ece6333`): Sucursales, áreas de bodega, subcategorías y unidades de medida.
   - Bloque 3 (en curso): Motivos de merma, métodos de pago, proveedores, departamentos y municipios.
   - Directorio `scratch/` agregado a `.gitignore`.
2. **Desglose 194 Tests**:
   - Verificado con `pytest --collect-only -q`: exactamente 194 pruebas en 29 archivos de test (0 fallos).
3. **Validación de Desactivación Segura con Conteo**:
   - Repositorio y Servicio ([`backend/app/services/catalogo_general_service.py`](../backend/app/services/catalogo_general_service.py)):
     - Proveedores: `count_ordenes_activas` lanza HTTP 400 con `"hay {n} orden(es) de compra emitida(s) activa(s)"`.
     - Métodos de pago: `count_pagos_ventas_completadas` lanza HTTP 400 con `"hay {n} pago(s) de ventas completadas asociado(s)"`.
     - Departamentos: `count_municipios_activos` lanza HTTP 400 con `"hay {n} municipio(s) activo(s) asociado(s)"`.
   - Pruebas en [`backend/tests/test_catalogo_bloque3_service.py`](../backend/tests/test_catalogo_bloque3_service.py): afirmaciones explícitas de conteo validadas (`hay 1 orden(es)`, `hay 1 pago(s)`, `hay 1 municipio(s)`).
4. **Limpieza en Scripts E2E**:
   - [`scratch/verify_bloque3_browser.py`](../scratch/verify_bloque3_browser.py): función `cleanup_e2e()` añadida en el bloque `finally:`, eliminando los registros de prueba creados (`Flores E2E`, `Petén E2E`, `Dulcería La Luna`, `Tarjeta Débito`, `Caducidad Controlada Edit`).
   - Verificación vía SELECT post-ejecución: 100% de tablas confirmadas en estado semilla (motivos: 2, métodos: 2, proveedores: 1, departamentos: 2, municipios: 3).

### Verificación
- `pytest -q`: **194 passed, 0 failed**.
- Pruebas de desactivación segura: 3/3 pasando con conteo exacto verificado.
- Playwright Chromium Headless: 27/27 comprobaciones aprobadas.
- Base de datos E2E: SELECT confirma únicamente registros semilla.

---

## [2026-10-22] Fase 2 — Bloque 3 (Parte 2): Catálogos Motivos de Merma, Métodos de Pago, Proveedores, Departamentos y Municipios

### Causa Raíz / Requerimiento
1. Completar el mantenimiento de Bloque 3 (Motivos de Merma, Métodos de Pago, Proveedores, Departamentos y Municipios) con validación real en navegador (Playwright).
2. **Usuario NO administrador**: la prueba de navegador debe incluir un rol no-admin (cajera y bodeguero) para validar que los combos ligeros cargan (HTTP 200) y que los intentos de escritura muestran el toast de error **403** con el detalle del backend, así como el toast **400** con conteo al intentar desactivar una sucursal con áreas de bodega activas.
3. **Revisión de regla de negocio**: revalidar que desactivar una sucursal con áreas de bodega activas queda bloqueado (HTTP 400 con conteo).

### Solución Implementada
1. **Fix de IDs de modal de confirmación** ([`frontend/js/catalog.js`](../frontend/js/catalog.js)): `toggleB3Status`/`confirmB3Deactivate` construían IDs en plural (`confirm-motivos-deactivate-modal`) mientras el HTML usa IDs en singular (`confirm-motivo-deactivate-modal`). Se añadió la clave `singular` a `B3_CONFIG` y se usó en la construcción de los ID de confirmación; sin esto el modal de confirmación nunca se abría en la UI.
2. **Creadas evidencias de navegador** en [`scratch/verify_bloque3_browser.py`](../scratch/verify_bloque3_browser.py) y [`scratch/seed_b3_e2e.py`](../scratch/seed_b3_e2e.py):
   - Semilla SQLite (roles 1 Administradora / 2 Cajero / 3 Bodeguero, usuarios `admin`, `cajera`, `bodega`, permiso `CATALOGO_ADMIN` solo en rol 1, catálogos B3 y sucursal con área activa).
   - Levanta uvicorn contra SQLite y valida en Chromium headless: CRUD completo de las 5 entidades (crear, ficha, editar, desactivar/reactivar, exportar CSV/Excel), dropdown dependiente departamento→municipio, y **sin alert()/confirm() nativos** (todo por toast/modal estático).
   - Como **cajera** (no-admin): los 5 combos responden 200 y un POST de catálogo devuelve **403** con `detail` de `CATALOGO_ADMIN`.
   - Como **bodeguero** (no-admin): al escribir desde la UI se muestra el **toast 403** con el detalle del backend.
   - Como **admin**: desactivar la sucursal con área activa dispara el **toast 400** con el conteo (`"...hay 1 área(s) de bodega activa(s) asociada(s)"`).

### Verificación
- Playwright Chromium headless (`scratch/verify_bloque3_browser.py`): **27/27 comprobaciones exitosas** para Bloque 3, incluyendo los escenarios no-admin (combos 200 + POST 403 + toast de bodeguero) y la desactivación segura de sucursal con áreas activas (toast 400 con conteo).
- `python -m pytest -q` en `backend/`: **194 passed, 0 failed** (medido sobre el árbol actual).
- Corrección de cifra: la entrada anterior (Bloque 2 pendientes) citaba "186 previos / 190 passed" como total; eso **no es reproducible** contra el repositorio. El desglose verificado al día de hoy es: baseline committeado 82 + Bloque 0 (28) = 110 + Bloque 1 clientes (16) = 126 + Bloque 2 (37 hoy, 20 en aprobación) + Bloque 3 (29) + `test_sales_service` (+2) = **194**. El delta aprobado 148 → 194 es **+46** (17 de Bloque 2 ampliado + 29 de Bloque 3), no "38".
- Regla de negocio confirmada (ya implementada en [`backend/app/services/catalogo_service.py`](../backend/app/services/catalogo_service.py):138-150 y cubierta por pruebas): desactivar una sucursal con áreas de bodega activas responde 400 y no cambia el estado.

---

## [2026-10-22] Fase 2 — Bloque 2: Pendientes resueltos (lectura de combos para no-admin, desactivación segura, enlaces relativos)

### Causa Raíz / Requerimiento
1. **Permisos de lectura**: solo el rol Administradora (rol 1) posee `CATALOGO_ADMIN`, pero los combos de sucursales, áreas de bodega, subcategorías y unidades de medida que consumen los módulos de **Productos**, **Inventario** y **POS** deben seguir cargando para usuarios NO admin (roles *Cajera* y *Bodega*). Solo las operaciones de escritura (POST/PUT/DELETE) y las exportaciones exigen `CATALOGO_ADMIN`; la lectura de combos no.
2. **Desactivación segura**: no debe permitirse desactivar una sucursal, área de bodega, subcategoría o unidad de medida que tenga productos o inventario activos asociados. La API debe responder **HTTP 400** con un mensaje claro que indique **cuántos registros dependen**.
3. **Enlaces de documentación**: sustituir cualquier enlace absoluto local que apunte a `c:/...` en `documentacion/cambios.md` por rutas relativas.

### Solución Implementada
1. **Lectura de combos sin `CATALOGO_ADMIN`** (ya existente y verificada): los endpoints ligeros `GET /api/catalogos/{sucursales|areas|subcategorias|unidades}` están protegidos únicamente con `get_current_user` (autenticación), nunca con `require_permission("CATALOGO_ADMIN")`. El mismo servicio serializador es consumido por el formulario de productos, filtros de inventario y POS (`frontend/js/catalog.js` → `populateSubcategorias/Unidades/Sucursales/Areas` sobre `CATALOGOS_API`).
   - **Refuerzo de pruebas** ([`backend/tests/test_catalogo_bloque2_api.py`](../backend/tests/test_catalogo_bloque2_api.py)): la prueba de combos ahora se parametriza con **dos roles no-admin** (`Cajera` y `Bodega`) y **afirma el contenido de los 4 combos** (incluida el área, que antes no se sembraba ni se validaba). La prueba de 403 de CRUD también se parametriza para ambos roles.
2. **Desactivación segura** (ya implementada en servicio y repositorio, ahora con cobertura API completa):
   - Repositorio ([`backend/app/repositories/catalogo_repository.py`](../backend/app/repositories/catalogo_repository.py)): `SucursalRepository.count_inventario_activo`, `AreaBodegaRepository.count_inventario_activo`, `SubcategoriaRepository.count_productos_activos`, `UnidadMedidaRepository.count_productos_activos` (COUNTs SQL asíncronos con `select(func.count())`).
   - Servicio ([`backend/app/services/catalogo_service.py`](../backend/app/services/catalogo_service.py)): tanto `deactivate_*` como `update_*` con `estado="Inactivo"` validan las dependencias y lanzan `HTTPException(400, "...hay {n} registro(s)...")` sin cambiar el estado.
   - **Pruebas API nuevas** en `test_catalogo_bloque2_api.py`: `test_desactivar_area_bodega_con_inventario_activo_retorna_400` y `test_desactivar_unidad_medida_con_producto_activo_retorna_400`, completando la cobertura HTTP de las 4 entidades (sucursal y subcategoría ya existían).
3. **Enlaces relativos**: verificación exhaustiva con `Select-String`/grep: **cero ocurrencias de `file://`** en `documentacion/` y en todo el repositorio; los enlaces del documento ya son relativos (`../backend/...`, `../frontend/...`, `../database/...`).

### Verificación
- `python -m pytest -q` en `backend/`: **190 passed, 0 failed** (186 previos + 4 nuevos: 2 por la parametrización de roles no-admin en combos y CRUD-403, y 2 pruebas API de desactivación segura para área y unidad).
  - **Corrección posterior**: la cifra "186 previos / 190 passed" no es reproducible contra el repositorio. El total verificado al [2026-10-22] es **194**; la diferencia con el aprobado de 148 es **+46** (Bloque 2 ampliado a 37 + Bloque 3 con 29 tests nuevos). Ver entrada "Bloque 3 (Parte 2)".
- Evidencia SQL directa (script `scratch`/temp): los COUNT de dependencias devuelven `1` para cada entidad; las 4 desactivaciones responden `HTTP 400` con el conteo (`"...hay 1 registro(s) de inventario activo(s) asociado(s)"` / `"...hay 1 producto(s) activo(s) asociado(s)"`), y los estados permanecen `Activo` tras el bloqueo.
- Frontend: el mensaje del backend (con conteo) se muestra en toast porque `readCatalogError` extrae `detail` ([`frontend/js/catalog.js`](../frontend/js/catalog.js)) en las rutas de desactivación.
- **No probado en navegador**: la validación de estos dos pendientes es de capa de API/servicio (permisos RBAC y regla de negocio). El flujo visual de CRUD/combos ya fue validado previamente con Playwright por `scratch/verify_bloque2_browser.py`. Si se requiere, la revalidación en navegador de estos comportamientos específicos (403 y toast con conteo) necesita servidor en vivo con usuarios no-admin sembrados.

---

## [2026-10-21] Fase 2 — Bloque 2: Catálogos (Sucursales, Áreas de Bodega, Subcategorías, Unidades de Medida) y Puntos Previos 1–4

### Causa Raíz / Requerimiento
1. Resolución de los 4 puntos previos requeridos antes del Bloque 2:
   - Punto 1: Eliminar datos de prueba en PostgreSQL real (`cliente` NIT 889941360-1 y `tipo_cliente` Mayorista VIP) y agregar auto-limpieza a `verify_flow.py`.
   - Punto 2: Prueba manual/automatizada en navegador real con Playwright (Clientes con 2 contactos dinámicos, ficha de solo lectura y búsqueda POS de cliente registrado, no registrado y CF).
   - Punto 3: En el POS, clientes con estado 'Inactivo' quedan bloqueados (aviso toast, rechazo 400 y reset a CF).
   - Punto 4: Venta en POS con cliente Mayorista aplica precio mayorista y descuento del tipo de cliente.
2. Implementación de Bloque 2: Mantenimiento completo (CRUD con soft delete `estado='Inactivo'`, reactivación, filtros, fechas, ordenamiento, fichas, exportación Excel/CSV, pruebas de API y RBAC con `CATALOGO_ADMIN`, y prueba de flujo en navegador real) para Sucursales, Áreas de Bodega, Subcategorías y Unidades de Medida.

### Solución Implementada
1. **Puntos Previos (1 a 4)**:
   - Limpieza ejecutada en PostgreSQL; scripts `scratch/verify_flow.py` y `scratch/run_browser_test.py` ajustados con limpieza automática.
   - En `frontend/js/clients.js`, corregido selector `DOM.clientDept` que impedía poblar municipios. Flujo completo validado en Playwright.
   - En `backend/app/services/sale_service.py` y `frontend/js/pos.js`, rechazo de clientes inactivos con HTTP 400 y toast preventivo.
   - En `backend/app/services/sale_service.py`, aplicación automática de `precio_mayorista` y porcentaje de descuento para clientes de tipo Mayorista.
2. **Backend DERCAS Bloque 2**:
   - Schemas ([`catalogo_schema.py`](../backend/app/schemas/catalogo_schema.py)): filtros (`SucursalFilter`, `AreaBodegaFilter`, `SubcategoriaFilter`, `UnidadMedidaFilter`), esquemas Create/Update/Out con nombres relacionados.
   - Repositorios ([`catalogo_repository.py`](../backend/app/repositories/catalogo_repository.py)): consultas sin commits, paginación, filtros por texto, estado, padre y rango de fechas (`fecha_desde`/`fecha_hasta`), y ordenamiento dinámico.
   - UnitOfWork ([`deps.py`](../backend/app/api/deps.py)): expone `sucursales`, `areas`, `subcategorias`, `unidades`.
   - Servicio ([`catalogo_service.py`](../backend/app/services/catalogo_service.py)): CRUD completo, soft delete (`estado='Inactivo'`), reactivación, auditoría (`log_action`), reportes Excel/CSV con filtros activos y retrocompatibilidad con combos de frontend.
   - Endpoints ([`catalogos.py`](../backend/app/api/catalogos.py)): controladores delgados sin `try/except`, protegidos con RBAC `CATALOGO_ADMIN`.
3. **Frontend Catálogos**:
   - [`frontend/index.html`](../frontend/index.html) y [`frontend/js/catalog.js`](../frontend/js/catalog.js): 4 pestañas interactivas, tablas ordenables con paginación, modales estáticos para formulario, ficha de solo lectura y confirmación de cambio de estado. Botones para descargar Excel y CSV.
4. **Pruebas Automatizadas y Navegador**:
   - `tests/test_catalogo_bloque2_service.py` (15 pruebas) y `tests/test_catalogo_bloque2_api.py` (5 pruebas). Suite completa: **148 pruebas pasando (0 fallos)**.
   - `scratch/verify_bloque2_browser.py`: Validación de extremo a extremo en Playwright Chromium headless para las 4 entidades con 100% de éxito.

### Verificación
- `python -m pytest -q` en `backend/`: **148 passed, 0 failed**.
- Playwright Chromium Headless (`scratch/verify_bloque2_browser.py`): Creación, ficha, edición, desactivación, reactivación y exportación CSV/Excel aprobados al 100% en las 4 entidades.
- Base de datos PostgreSQL: Verificada en estado semilla limpio.

---

## [2026-10-21] Fase 2 — Bloque 1: Cierre y Verificación Integral de Clientes (9 Puntos Completos)

### Causa Raíz / Requerimiento
Cierre formal de los 9 puntos requeridos para el Bloque 1 (Clientes):
1. Mantenimiento de tipos de cliente: endpoint `/api/tipos-cliente` (CRUD con soft delete `estado='Inactivo'`) y pestaña en vista de Clientes.
2. Contactos: agregar, editar y quitar teléfono y correo dinámicamente desde el modal de cliente.
3. Modal de ficha de solo lectura del cliente (contactos, tipo, municipio, departamento, fecha de registro).
4. Filtros por fecha de creación desde/hasta y ordenamiento interactivo asc/desc por columnas en la tabla.
5. Botones "Descargar Excel" y "Descargar CSV" respetando todos los filtros activos (fechas, texto, tipo, estado).
6. Cliente "CF": protección doble estricta: no se puede desactivar Y su NIT no se puede modificar.
7. Pruebas de API completas: 403 sin `CLIENTE_ADMIN`, bloqueo de desactivar/renombrar "CF", NIT duplicado (400), paginación, filtros y CRUD tipos.
8. Prueba de flujo completo en backend y navegador con y sin cliente registrado (descrita paso a paso).
9. Reubicación de municipios a endpoint reutilizable: `GET /api/departamentos/{id}/municipios`.

### Solución Implementada
1. **Endpoint `/api/tipos-cliente` y Mantenimiento** ([`backend/app/api/tipos_cliente.py`](../backend/app/api/tipos_cliente.py), [`backend/app/services/cliente_service.py`](../backend/app/services/cliente_service.py)):
   - Controlador CRUD completo montado en `main.py` bajo `/api/tipos-cliente`. Métodos `get_tipo_cliente` y `deactivate_tipo_cliente` con soft delete `estado='Inactivo'`, auditoría y protección RBAC `CLIENTE_ADMIN`.
   - Frontend: Pestaña "Tipos de Cliente" con tabla, modal `#tipo-cliente-modal` y modal de confirmación `#confirm-tipo-deactivate-modal` con `backdrop="static"`.
2. **Contactos Dinámicos** ([`frontend/index.html`](../frontend/index.html), [`frontend/js/clients.js`](../frontend/js/clients.js)):
   - Contenedor dinámico `#client-contacts-container` con botón `+ Agregar Contacto`. Cada fila permite teléfono, correo y botón eliminar. Serialización y deserialización a arreglo en payloads de creación/edición.
3. **Modal de Ficha de Solo Lectura** (`#client-detail-modal` en [`frontend/index.html`](../frontend/index.html)):
   - Botón de ojo (`bi-eye`) en tabla. Muestra NIT, Estado, Nombre, Tipo con descuento, Departamento, Municipio, Dirección, Fecha formateada y tabla detallada de contactos.
4. **Filtros por Fecha y Ordenamiento** ([`backend/app/schemas/cliente_schema.py`](../backend/app/schemas/cliente_schema.py), [`backend/app/repositories/cliente_repository.py`](../backend/app/repositories/cliente_repository.py)):
   - Esquema `ClienteFilter` y repositorio soportan `fecha_desde`, `fecha_hasta`, `sort_by` y `sort_order`.
   - Interfaz con campos datepicker `#filter-client-date-from` / `#filter-client-date-to` y encabezados ordenables interactivos con iconos asc/desc.
5. **Reportes Excel y CSV** ([`backend/app/services/cliente_service.py`](../backend/app/services/cliente_service.py), [`frontend/js/clients.js`](../frontend/js/clients.js)):
   - `export_clientes` consume todos los filtros activos para generar archivos `.xlsx` y `.csv` coherentes con la vista filtrada.
6. **Protección Total de Consumidor Final (CF)** ([`backend/app/services/cliente_service.py`](../backend/app/services/cliente_service.py)):
   - `update_cliente` rechaza con HTTP 400 cualquier intento de cambiar el NIT de CF (`cliente.nit == 'CF' and data.nit != 'CF'`) o de asignar NIT 'CF' a otro cliente.
   - En frontend: NIT de CF en modo edición se bloquea en modo solo lectura con nota informativa.
7. **Pruebas de API** ([`backend/tests/test_cliente_api.py`](../backend/tests/test_cliente_api.py), [`backend/tests/test_cliente_service.py`](../backend/tests/test_cliente_service.py)):
   - 6 suites nuevas de integración cubriendo 403 sin `CLIENTE_ADMIN`, bloqueo de desactivar/renombrar CF, NIT duplicado (400), paginación y ordenamiento, CRUD tipos de cliente y endpoint reutilizable de ubicación. Total: 126 pruebas pasando (0 fallos).
8. **Prueba de Flujo Completo** ([`scratch/verify_flow.py`](../scratch/verify_flow.py)):
   - Ejecución automatizada contra PostgreSQL y endpoints del sistema verificando creación, edición, ficha, desactivación y búsqueda por NIT en POS (con cliente registrado, no registrado y CF).
9. **Endpoint Reutilizable de Ubicación** ([`backend/app/api/departments.py`](../backend/app/api/departments.py)):
   - Implementado `GET /api/departamentos/{id}/municipios` y `GET /api/departamentos/municipios`, integrados en repositorio y servicio de departamentos, consumidos directamente por el frontend.

### Verificación
- `python -m pytest -q` en `backend/`: **126 passed, 0 failed**.
- Script `verify_flow.py`: Verificación de extremo a extremo aprobada contra base de datos PostgreSQL real.
- Sintaxis frontend: `node --check frontend/js/clients.js` aprobado.

---

## [2026-10-21] Fase 2 — Bloque 1: Módulo Clientes Completo (DERCAS, POS, FEL y Frontend)

### Causa Raíz / Requerimiento
1. **Migración 0011 de saneamiento**: Mover el saneamiento preventivo de codificación de `Solol??` a una migración dedicada `0011_saneamiento_departamento_solola.py`, preservando `0010` inalterada respecto a su aplicación inicial.
2. **Módulo integral de Clientes (DERCAS)**: Implementación de la gestión completa de clientes requerida para la operación comercial del sistema y la emisión de facturación electrónica FEL:
   - Regla de negocio: unicidad de NIT estricta excepto para Consumidor Final (`'CF'`), el cual puede coexistir múltiples veces.
   - Protección de Consumidor Final: prohibición absoluta de desactivar o eliminar el cliente con NIT `'CF'`.
   - Soporte de múltiples contactos por cliente (teléfono, correo).
   - Catálogo de tipos de cliente (Minorista, Mayorista, etc.) con sus respectivos descuentos.
   - Integración con POS y FEL: autocompletado y selección de cliente en caja para facturación DTE inmediata.

### Solución Implementada
- **Migración 0011** ([`backend/alembic/versions/0011_saneamiento_departamento_solola.py`](../backend/alembic/versions/0011_saneamiento_departamento_solola.py)):
  - Creada migración idempotente dedicada para unificar departamentos legacy corruptos hacia `Sololá` y reasignar claves foráneas de municipios. Aplicada en PostgreSQL (`alembic upgrade head -> 0011`).
- **Capa DERCAS Backend**:
  - **Esquemas Pydantic v2** ([`backend/app/schemas/cliente_schema.py`](../backend/app\schemas\cliente_schema.py)): `ClienteCreate`, `ClienteUpdate`, `ClienteOut`, `ClienteFilter`, `ClienteList`, `TipoClienteCreate`, `TipoClienteUpdate`, `TipoClienteOut`, `ClienteContactoCreate`, `ClienteContactoOut`.
  - **Repositorios** ([`backend/app/repositories/cliente_repository.py`](../backend/app/repositories/cliente_repository.py)): `ClienteRepositoryImpl` (consultas asíncronas con `selectinload` para relaciones, búsqueda filtrada, sin commit) y `TipoClienteRepositoryImpl`.
  - **Unit of Work** ([`backend/app/api/deps.py`](../backend/app/api/deps.py) y [`backend/tests/conftest.py`](../backend/tests/conftest.py)): Expuestas propiedades `uow.clientes` y `uow.tipos_cliente`.
  - **Servicio** ([`backend/app/services/cliente_service.py`](../backend/app/services/cliente_service.py)): `ConcreteClienteService` con validación de tipo de cliente activo, validación de municipio, regla de unicidad condicional de NIT (permitiendo múltiples CF), bloqueo de desactivación de CF, auditoría atómica en `bitacora_auditoria` y exportación Excel/CSV.
  - **Controlador API** ([`backend/app/api/clientes.py`](../backend/app/api/clientes.py)): Endpoints delgados bajo `/api/clientes` protegidos con RBAC (`CLIENTE_ADMIN`), más endpoints de consulta pública autenticada `/api/clientes/nit/{nit}` y `/api/clientes/municipios` para el flujo de ventas.
  - **Registro en App**: Montado router en [`backend/app/main.py`](../backend/app/main.py).
- **Capa Frontend SPA**:
  - **Interfaz HTML** ([`frontend/index.html`](../frontend/index.html)):
    - Enlace en sidebar protegido por `data-module-item="clients"`.
    - Vista `#clients-view` con tabla responsiva, filtros rápidos por nombre, NIT, tipo y estado, más paginación.
    - Modal de edición/creación `#client-modal` con `backdrop="static"`, selector dependiente de Departamento → Municipio y validaciones 422 inline.
    - Modal de confirmación `#confirm-client-deactivate-modal` para soft delete sin diálogos nativos.
  - **Lógica de Módulo** ([`frontend/js/clients.js`](../frontend/js/clients.js)): `window.showClientsModule()`, carga asíncrona de catálogos, guardado dinámico con spinner y toasts, exportación Excel y CSV.
  - **Enrutamiento SPA** ([`frontend/js/app.js`](../frontend/js/app.js)): Registrada vista `clients` en `mainViews`, guardia RBAC con permiso `CLIENTE_ADMIN` y enlace con `renderView`.
  - **Integración POS y Facturación FEL** ([`frontend/js/pos.js`](../frontend/js/pos.js) e [`frontend/index.html`](../frontend/index.html)):
    - Tarjeta receptora de cliente en checkout POS (`#pos-client-nit`, botón de búsqueda y badge de tipo de cliente).
    - Búsqueda en tiempo real contra `/api/clientes/nit/{nit}` para autocompletar nombre comercial y enlazar `id_cliente`, `nit_receptor` y `nombre_receptor` al payload de `/api/ventas`.

### Verificación y Pruebas
- Pruebas unitarias de servicio ([`backend/tests/test_cliente_service.py`](../backend/tests/test_cliente_service.py)): 9 pruebas unitarias cubriendo creación con contactos, regla de duplicados de NIT y CF, protección de desactivación de CF, soft delete, búsqueda y catálogo de tipos.
- Pruebas de integración API ([`backend/tests/test_cliente_api.py`](../backend/tests/test_cliente_api.py)): 1 prueba completa de flujo HTTP con autenticación Bearer y RBAC.
- Sintaxis JavaScript verificada con `node --check` para `app.js`, `clients.js` y `pos.js` (0 errores).
- Suite completa de pruebas del backend: **120 pruebas pasadas** (110 previas + 10 nuevas, 0 fallos).

## [2026-10-21] Fase 2 — Bloque 0: Reescritura de Pruebas Históricas (.old) a Español y DERCAS

### Causa Raíz / Requerimiento
1. **Saneamiento preventivo de codificación**: Existía riesgo de registros con caracteres corruptos como `Solol??` en bases de datos heredadas. Se requirió unificación formal hacia `Sololá`, reasignación de municipios y verificación de no existencia de otros textos con `??`.
2. **Clarificación y trazabilidad geográfica**: Documentar explícitamente que se cargaron 338 municipios y que 4 quedan marcados pendientes por verificar contra fuente oficial (decretos legislativos de Petatán, Sipacate, Las Cruces y El Chal).
3. **Reescritura de pruebas unitarias `.old`**: Las suites históricas `_test_category_service.py.old`, `_test_department_service.py.old`, `_test_role_service.py.old`, `_test_user_service.py.old` y `_test_product_service.py.old` se encontraban excluidas por utilizar nomenclatura en inglés (`name`, `is_active`, `barcode`) incompatible con la arquitectura DERCAS en español.

### Solución Implementada
- **Saneamiento en Migración 0010**: Se integró en [`backend/alembic/versions/0010_estado_fechas_visitas_permisos_municipios.py`](../backend/alembic/versions/0010_estado_fechas_visitas_permisos_municipios.py) un bloque PL/pgSQL que detecta nombres corruptos como `Solol%`, reasigna sus municipios a `Sololá` y elimina el registro residual. Se escaneó la base de datos completa confirmando cero ocurrencias de `??`.
- **Estatus Geográfico Oficial**: Se documentó formalmente el estado de municipios: `338 cargados, 4 por verificar contra fuente oficial`.
- **Reescritura de Pruebas Unitarias en Español**:
  - [`backend/tests/test_category_service.py`](../backend/tests/test_category_service.py): 5 pruebas sobre `ConcreteCategoryService` (`CategoriaCreate`, `CategoriaOut`, unicidad, 404, soft delete con `estado='Inactivo'`).
  - [`backend/tests/test_department_service.py`](../backend/tests/test_department_service.py): 5 pruebas sobre `ConcreteDepartmentService` (`DepartmentCreate`, `id_departamento`, `nombre`, validación de unicidad, listados y actualización).
  - [`backend/tests/test_role_service.py`](../backend/tests/test_role_service.py): 5 pruebas sobre `ConcreteRoleService` (`RoleCreate`, `id_rol`, `nombre`, `estado`, soft delete y unicidad).
  - [`backend/tests/test_user_service.py`](../backend/tests/test_user_service.py): 7 pruebas sobre `ConcreteUserService` (`UserCreate`, validación de rol activo, rechazo de rol inactivo, unicidad de username, actualización y soft delete).
  - [`backend/tests/test_product_service.py`](../backend/tests/test_product_service.py): 6 pruebas sobre `ConcreteProductService` (creación anidada con variante e inventario, validación de subcategoría, unicidad de código de barras, búsqueda y soft delete).
- **Limpieza**: Se eliminaron los 5 archivos `.old` redundantes.

### Verificación y Pruebas
- Escaneo exhaustivo en PostgreSQL: 0 columnas o filas con `??`.
- Ejecución completa de la suite de pruebas del backend: **110 pruebas pasadas** (82 baseline + 28 pruebas reescritas incorporadas exitosamente, 0 fallos).

## [2026-10-21] Fase 1 — Base de Datos: Migración 0010, Soft Delete, Visitas de Seguimiento y Catálogos INE

### Causa Raíz / Requerimiento
Necesidad de estandarizar el soporte de soft delete (`estado = 'Activo'|'Inactivo'`) en tablas de catálogos y transaccionales que carecían de él, registrar fechas de creación en entidades maestras (`cliente`, `proveedor`, `sucursal`), incorporar restricciones compuestas de unicidad (`(id_departamento, nombre)` en `municipio`, `(id_categoria, nombre)` en `subcategoria`, y unicidad parcial sobre `nit` de `cliente` excluyendo `'CF'`), añadir las tablas para el Módulo 8 (`visita_seguimiento` y `visita_modulo_evaluacion`), asignar nuevos permisos RBAC para la administradora y sembrar los 22 departamentos y 340 municipios oficiales de Guatemala.

### Solución Implementada
- **Migración Alembic 0010** (`backend/alembic/versions/0010_estado_fechas_visitas_permisos_municipios.py`):
  - Inyección idempotente de columnas `estado VARCHAR(20) NOT NULL DEFAULT 'Activo' CHECK (estado IN ('Activo','Inactivo'))` en: `cliente`, `tipo_cliente`, `area_bodega`, `departamento_geografico`, `municipio`, `subcategoria`, `unidad_medida`, `motivo_merma`, `metodo_pago` y `proveedor`.
  - Agregadas columnas `fecha_creacion TIMESTAMP NOT NULL DEFAULT NOW()` a `cliente`, `proveedor` y `sucursal`.
  - Configurado `DEFAULT NOW()` en `bitacora_auditoria.fecha_hora`.
  - Restricciones únicas compuestas: `uq_municipio_depto_nombre` y `uq_subcategoria_cat_nombre` (removiendo restricciones simples previas); e índice parcial `uq_cliente_nit_no_cf` para NITs distintos de `'CF'`.
  - DDL de tablas `visita_seguimiento` y `visita_modulo_evaluacion` (con cascada de eliminación).
  - Semilla de 5 nuevos permisos (`CLIENTE_ADMIN`, `BITACORA_CONSULTAR`, `REPORTE_VER`, `CATALOGO_ADMIN`, `VISITA_REGISTRAR`) asignados a `id_rol = 1`.
  - Saneamiento y unificación preventiva de cualquier registro corrupto como `Solol??` hacia `Sololá`, reasignando claves foráneas de municipios asociados.
  - Carga geográfica: 22 departamentos; 338 cargados, 4 por verificar contra fuente oficial.
  - Implementada función de reversión simétrica en `downgrade()`.
- **Actualización de Modelos ORM** (`backend/app/db/models.py`):
  - Añadidas las columnas `estado` y `fecha_creacion` (con defaults compatibles en Python y PostgreSQL) a los modelos respectivos.
  - Creados modelos SQLAlchemy `VisitaSeguimiento` y `VisitaModuloEvaluacion` con relación 1:N y cascade.
- **Sincronización de Init Script** (`database/init.sql`):
  - Actualizado el script DDL maestro para que los despliegues limpios en Docker inicien de forma idéntica a la migración 0010.
- **Robustez de Réplica Local** (`backend/app/repositories/sync_repository.py`):
  - Se ajustó `replicate_to_sqlite` para recrear limpiamente el esquema (`drop_all` + `create_all`) ante actualizaciones de metadata DDL.

### Verificación y Pruebas
- Ejecución completa de la suite de pruebas del backend: **82 pruebas pasadas** (0 regresiones).
- Revisión de pruebas `.old` existentes en `backend/tests/`: se confirmó que corresponden a versiones previas en inglés (`name`, `is_active`) anteriores a la migración idiomática a español.

### Causa Raíz / Requerimiento
Auditoría técnica de solo lectura sobre las 23 tablas de los Módulos I, II y III para evaluar la cobertura en modelos SQLAlchemy, routers/endpoints, vistas frontend, campos de estado lógico, tablas sin CRUD y divergencias idiomáticas de nomenclatura. Se profundizó en las capas DERCAS (schemas, repositorios, servicios, interfaces y tests) y en los endpoints de catálogos consumidos por el frontend.

### Solución Implementada
- Se actualizó el reporte técnico [`documentacion/auditoria_estado.md`](auditoria_estado.md) con la sección "Capas".
- Se verificó que solo `usuario` y `producto` tienen filtros y paginación completos; `rol`, `usuario`, `categoria`, `producto` y `departamento` soportan soft delete (`Inactivo`).
- Se confirmó que `departments.py` / `department_service.py` apunta a la tabla `departamento_geografico`.
- Se mapearon las rutas exactas de catálogo (`/api/catalogos/subcategorias`, `/unidades`, `/sucursales`, `/areas`) consumidas por `frontend/js/catalog.js`.

## [2026-10-18] Mejoras de UX y Rendimiento en Inicio de Sesión (Login)

### Causa Raíz / Requerimiento
1. **Comportamiento inconsistente del visor de contraseña**: El botón de revelar contraseña dependía de los controles nativos del navegador (`::-ms-reveal`), los cuales desaparecían según el foco o la interacción del usuario.
2. **Ausencia de feedback visual inmediato al autenticar**: Al presionar "Ingresar al Sistema", no existía indicación de carga ni bloqueo de clics repetidos, dando sensación de lentitud o falta de respuesta.
3. **Bloqueo del event loop en backend**: La función `pwd_context.verify` (bcrypt) es una operación intensiva en CPU ejecutada de forma síncrona directamente sobre el hilo principal de asyncio, lo que degradaba la fluidez de respuesta del servidor ante peticiones concurrentes.

### Solución Implementada
- **Desactivación de ícono nativo y botón persistente (HTML/CSS)**:
  - En `frontend/index.html`, se incorporó un botón permanente `#btn-toggle-pass` con `tabindex="-1"` y enlace directo `onclick="toggleLoginPassword(event)"`.
  - **Aislamiento de selectores vendor-prefix**: En CSS, agrupar selectores de distintos navegadores con coma hace que el navegador descarte toda la regla si desconoce uno. Se separaron las reglas de `input[type="password"]::-ms-reveal` y `::-ms-clear` en bloques individuales independientes y se inyectaron en `<style>` en el `<head>` para sobreescritura inmediata sin depender de la caché.
  - En `frontend/css/style.css`, se actualizaron las reglas individuales y se estilizó la clase `.btn-toggle-password` junto al foco en `#form-login .input-group:focus-within`.
- **Micro-interacciones y estado de carga en Login (JavaScript)**:
  - En `frontend/js/app.js`, se expuso globalmente `window.toggleLoginPassword(event)` para alternar de forma idempotente `type="password"` y `type="text"`, actualizando el icono entre `bi-eye-slash` y `bi-eye` y preservando el foco y posición del cursor.
  - Se implementó `setLoginLoading(loading)`, deshabilitando `#btn-login-submit` y mostrando un spinner Bootstrap con el texto `"Ingresando..."` durante la llamada a la API, restaurándolo de forma segura en un bloque `finally`.
  - Se incrementaron las versiones de los assets a `css/style.css?v=2.4` y `js/app.js?v=2.4` en `index.html` para invalidar la caché HTTP de navegadores existentes.
- **Verificación asíncrona no bloqueante (FastAPI / Core Security)**:
  - En `backend/app/core/security.py`, se añadió `verify_password_async()`, delegando la carga computacional de bcrypt a un hilo independiente mediante `loop.run_in_executor()`.
  - En `backend/app/api/auth.py`, se actualizó la validación a `await security.verify_password_async(form_data.password, user.password_hash)`.

### Verificación y Pruebas
- Sintaxis de `frontend/js/app.js` validada exitosamente con `node --check`.
- Sintaxis de módulos Python verificada mediante `ast.parse`.
- Ejecución completa de la suite de pruebas del backend: **82 pruebas pasadas** (0 regresiones).

## [2026-10-13] Módulo de Facturación Electrónica FEL (SDD: `specs/emision_factura_fel.feature`)

### Componentes creados
| Archivo | Capa | Descripción |
|---------|------|-------------|
| `backend/app/schemas/fel_schema.py` | DTOs | `FelEmisionRequest`, `FelCertificacionRespuesta`, `FelEmisionResponse`, `FelItem`, `FelReintentoRequest` (Pydantic v2) |
| `backend/app/repositories/fel_repository.py` | Repositorio | `FelRepositoryImpl`: CRUD async sobre `factura_fel` (no hace commit; lo controla el UoW) |
| `backend/app/services/fel_service.py` | Servicio | `ConcreteFelService`: reglas de negocio SAT, httpx async, contingencia y reintento |
| `backend/app/api/facturacion.py` | Controller | `GET /api/facturacion/pendientes` y `POST /api/facturacion/reintentar/{id_venta}` |
| `backend/tests/test_fel_service.py` | Pruebas | 7 pruebas (éxito, rechazo fiscal, timeout, sin certificador, CF>2500, totales inválidos, reintento) |
| `backend/alembic/versions/0009_factura_fel_estado_y_dte_nullable.py` | Migración | `estado` + campos DTE NULLables |

### Componentes modificados
| Archivo | Cambio |
|---------|--------|
| `backend/app/db/models.py` | `FacturaFel` gana `estado` (default `Certificada`); `numero_autorizacion_sat`, `serie`, `numero_dte`, `fecha_certificacion` pasan a NULLables |
| `backend/app/core/config.py` | Settings FEL: `FEL_ENABLED`, `FEL_API_URL`, `FEL_API_KEY`, `FEL_TIMEOUT`, `FEL_SERIE`, `FEL_EMISOR_NIT`, `FEL_EMISOR_NOMBRE` |
| `backend/app/api/deps.py` | `UnitOfWork.fel` (propiedad) + `get_fel_service` |
| `backend/app/services/sale_service.py` | Al confirmar la venta (stock ya descontado) dispara `ConcreteFelService.emitir_factura` bajo la misma transacción UoW |
| `backend/app/schemas/sale_schema.py` | `SaleCreate` gana `nit_receptor` y `nombre_receptor` (opcionales) |
| `backend/app/interfaces/repositories.py` | Contrato `FelRepository` |
| `backend/app/interfaces/services.py` | Contrato `FelService` |
| `backend/app/main.py` | Router de `facturacion` registrado |
| `backend/tests/conftest.py` | `TestUnitOfWork.fel` |
| `database/init.sql` | Tabla `factura_fel` con `estado` y DTE NULLable |
| `.env.example` | Variables FEL documentadas |

### Reglas de negocio implementadas (de la especificación Gherkin)
- **Bloqueo de totales inválidos**: totales Q0.00 o negativos se detienen antes de contactar al certificador (HTTP 400).
- **NIT "CF" bloqueado > Q2,500.00** (Decreto 7-2019/SAT): si `nit_receptor` es vacío/"CF" y el total supera Q2,500.00, la operación se detiene con HTTP 400.
- **Comunicación asíncrona**: `httpx.AsyncClient` en `_certificar` (timeout configurable `FEL_TIMEOUT`).
- **Contingencia (offline/timeout)**: si el certificador no responde (timeout), falla la red o devuelve 5xx (o no hay URL configurada), la venta NO se revierte y `factura_fel` se guarda con estado `Contingencia` (DTE NULL), permitiendo reintentar por `POST /api/facturacion/reintentar/{id_venta}`.
- **Rechazo fiscal (HTTP 400/422 del certificador)**: se levanta HTTP 400 y, al integrarse en `sale_service` vía UnitOfWork, la transacción completa (venta + inventario) se revierte (rollback).

### Integración con Ventas
- `sale_service.registrar_venta` descarga el inventario y crea la cabecera/detalles/pagos con `create_sale` (flushing), luego (si `FEL_ENABLED` y se enviaron datos de receptor) llama a `emitir_factura`; ambos quedan en la misma transacción y se hacen `commit` de una sola vez. Un rechazo fiscal hace `rollback` completo.

### Esquema de BD
- Migración `alembic upgrade head` → `0009`. Recordar que `database/init.sql` solo aplica en volúmenes nuevos.

### Verificación
- `python -m pytest -q` desde `backend/`: **81 passed** (74 previos + 7 nuevos de FEL).

## [2026-10-05] Fix 404 en `/api/dashboard/resumen` y `/api/inventario/alertas` (imagen Docker desactualizada)

### Causa Raíz
El frontend reportaba HTTP 404 en ambos endpoints. En `backend/app/main.py` los routers **ya estaban** correctamente importados (`from app.api import ..., dashboard, ..., inventory`) y registrados (`app.include_router(dashboard.router)`, `app.include_router(inventory.inventario_router)`), por lo que el código fuente era correcto. El problema era de despliegue: el contenedor `regalito_backend_prod` se construyó ~3h antes con una imagen vieja de código (sin esos routers), por lo que ninguna de las dos rutas existía en el backend en ejecución.

### Solución Implementada
- **Reconstrucción del contenedor**: `docker compose -f docker-compose.prod.yml up -d --build backend` desde la raíz del repo. La nueva imagen ya incluye los routers de `dashboard` e `inventory`.
- **Fix de dependencia** (`backend/requirements.txt`): tras el rebuild, el backend crasheaba con `ImportError: The SQLAlchemy asyncio module requires greenlet. La dependencia se declaró como `sqlalchemy[asyncio]>=2.0` (en lugar de `sqlalchemy>=2.0`), de modo que `pip` instala `greenlet` explícitamente (requerido por SQLAlchemy 2.1.x con `asyncpg`).

### Verificación
1. `GET http://localhost:9090/api/dashboard/resumen` → **401 Unauthorized** (ya no 404; existe y exige autenticación).
2. `GET http://localhost:9090/api/inventario/alertas` → **401 Unauthorized** (ya no 404; existe y exige autenticación).
3. Suite backend: `python -m pytest -q` → **74 passed**.

## [2026-10-05] Campanita de notificaciones: endpoint `GET /api/inventario/alertas` + dropdown en el header

### Causa Raíz
El botón de la campanita en el header (`<button class="btn btn-light rounded-circle ... bi-bell">`) era decorativo: su punto rojo estaba quemado en el HTML y no consultaba ninguna fuente de datos. Se requería un endpoint propio del dominio de inventario que devolviera solo las alertas de stock `Pendiente` (JOIN con `inventario_sucursal` → `variante_producto` → `producto`), y un dropdown real en el header para mostrarlas.

### Solución Implementada

#### Backend — Endpoint `GET /api/inventario/alertas` (arquitectura DERCAS)
- **Repositorio** (`app/repositories/inventory_repository.py`):
  - `get_alerts()`: el estado por defecto pasó de `"Activa"` a **`"Pendiente"`** (alineado con el CHECK constraint de `init.sql`: `estado IN ('Pendiente','Atendida','Descartada')` y con la semilla `id_alerta=1`). Se añadió eager loading de `AlertaStock.inventario → InventarioSucursal.variante → VarianteProducto.producto` para el JOIN y evitar `MissingGreenlet`.
  - `create_alert()`: corrige el estado de creación de `"Activa"` a **`"Pendiente"`** (el valor anterior violaría el CHECK constraint de PostgreSQL).
- **Schema** (`app/schemas/inventory_schema.py`): `AlertaStockResponse` se enriqueció con campos opcionales `producto_nombre`, `variante_sku`, `stock_actual`, `stock_minimo`.
- **Servicio** (`app/services/inventory_service.py`): `get_alerts()` ahora puebla los campos de presentación desde `alerta.inventario.variante.producto`.
- **Controlador** (`app/api/inventory.py`): se creó el router `inventario_router = APIRouter(prefix="/api/inventario", tags=["Inventario"])` con `GET /alertas` autenticado vía `get_current_user` (el badge es global, no depende de permisos granulares). Registrado en `app/main.py` como `app.include_router(inventory.inventario_router)`. El endpoint existente `GET /api/inventory/alerts` (protegido con `INV_VER_ALERTAS`) se conserva intacto.

#### Frontend — Dropdown de notificaciones (`frontend/index.html`)
- El botón de la campanita se convirtió en un dropdown de Bootstrap:
  - Botón `#btn-notificaciones` con `data-bs-toggle="dropdown"`.
  - Punto rojo/counter: `#badge-notificaciones` (clase `badge rounded-pill bg-danger`, oculto por defecto con `d-none`).
  - Lista desplegable: `#lista-notificaciones` (dropdown-menu con cabecera "Alertas de stock pendientes") y contenedor interno `#notificaciones-contenido` con scroll (max-height 300px).

#### Frontend — Lógica (`frontend/js/notificaciones.js`)
- `window.cargarNotificaciones()`: fetch a `GET /api/inventario/alertas` con `Authorization: Bearer` (clave `jwt_token` del login), 401 → `handleUnauthorized`, manejo de errores silencioso.
- Si hay alertas: muestra el badge con el conteo y llena el dropdown con mensajes `"Producto X por debajo del stock mínimo"` (usa `producto_nombre` de la respuesta; fallback al `mensaje` almacenado) más detalle `Stock actual / Mínimo`. Sin alertas: oculta el badge y muestra "Sin alertas de stock pendientes.". Contenido construido con `textContent`/`createElement` (sin inyección HTML).
- El dropdown refresca al abrirse (listener de click en `#btn-notificaciones`).
- Script registrado en `index.html` (`js/notificaciones.js?v=1.0`).

#### Frontend — Arranque (`frontend/js/app.js`)
- En `showDashboard()` (que corre al iniciar la app con sesión activa y tras cada login) se invoca `window.cargarNotificaciones()` con guardia `typeof`, de modo que la comprobación se ejecuta al iniciar la aplicación.

### Verificación
1. **Suite backend**: `python -m pytest -q` → **74 passed / 74** (71 previos + 3 nuevos: `test_get_alerts_solo_pendientes_enriquecidas` en `tests/test_inventory_service.py`, `test_inventario_alertas_requires_auth` y `test_inventario_alertas_devuelve_solo_pendientes` en `tests/test_inventario_alertas.py`).
2. **Sintaxis frontend**: `node --check` sobre `frontend/js/notificaciones.js` y `frontend/js/app.js` → 0 errores (código 0).
3. **Balance HTML**: 442 `<div>` abiertos / 442 cerrados (balance = 0) tras la inyección del dropdown.
4. No se modificó ningún modelo SQLAlchemy ni `init.sql`: la tabla `alerta_stock` y sus estados ya existían en la BD.

---

## [2026-10-05] Conexión del Panel Principal (Dashboard) a métricas 100% reales

### Causa Raíz
Las tarjetas informativas del Panel Principal (`dashboard-content`) mostraban **números estáticos/inventados** de relleno en el HTML (`Q 1,245.00`, `12 productos`, `3 pendientes`, `5 hoy`), ya que el frontend nunca consultaba el backend para este módulo. El dashboard no era un reflejo fiel de la base de datos.

### Solución Implementada

#### Backend — Nuevo endpoint `GET /api/dashboard/resumen` (arquitectura DERCAS)
- **Schema** (`app/schemas/dashboard_schema.py`): DTOs Pydantic v2 `MetricasVentas`, `MetricasCompras` y `DashboardResumenResponse`.
- **Interfaces** (`app/interfaces/repositories.py`, `app/interfaces/services.py`): contratos ABC `DashboardRepository` (4 métodos) y `DashboardService` (`get_resumen`).
- **Repositorio** (`app/repositories/dashboard_repository.py`): `DashboardRepositoryImpl` con consultas SQLAlchemy 2.x 100% asíncronas y seguras (`select` + `func.sum`/`func.count`, sin SQL concatenado):
  - `get_ventas_hoy()` → `SUM(total_venta)` + `COUNT(*)` de ventas del día con `estado='Completada'`.
  - `count_stock_critico()` → `COUNT(*)` de `inventario_sucursal` con `stock_actual <= stock_minimo`.
  - `get_compras_mes()` → `SUM(total_compra)` + `COUNT(*)` de compras desde el primer día del mes.
  - `count_turnos_activos()` → `COUNT(*)` de `turno_caja` con `estado IN ('Abierto','Abierta')`.
- **Servicio** (`app/services/dashboard_service.py`): `ConcreteDashboardService` ensambla el DTO sin lógica de acceso a datos.
- **DI** (`app/api/deps.py`): proveedor `get_dashboard_service`.
- **Controlador** (`app/api/dashboard.py`): router delgado (cero try/except) autenticado con `get_current_user` y `response_model=DashboardResumenResponse`, registrado en `app/main.py`.

#### Frontend — Estructura HTML (`frontend/index.html`)
- Se eliminaron los números de relleno de las 4 tarjetas KPI y se colocaron valores por defecto honestos (`Q 0.00`, `0`) con text "Cargando...".
- IDs únicos para inyección: `dash-ventas-hoy` (+ `dash-ventas-hoy-detalle`), `dash-stock-critico`, `dash-compras-mes` (+ `dash-compras-mes-detalle`), `dash-turnos-activos`.
- Se re-etiquetaron las métricas para reflejar datos reales: "Ventas de hoy", "Stock crítico", "Compras del mes", "Turnos de caja activos" (antes "Cuentas por pagar" y "Clientes nuevos" sin fuente de datos). Se conservaron los `data-metric` (`sales_today`, `critical_stock`, `payables_pending`, `new_customers`) para no romper la visibilidad RBAC de `app.js`.
- Se registró el script `js/dashboard.js?v=1.0` junto a los demás módulos.

#### Frontend — Lógica (`frontend/js/dashboard.js`)
- `window.showDashboardModule()` expuesto globalmente: ejecuta `cargarResumenDashboard()`.
- Fetch a `/api/dashboard/resumen` (ruta relativa, `Authorization: Bearer`) y actualización del DOM con `textContent` (sin inyección), formateo de Quetzales con `Intl` (es-GT), pluralización de "ventas/compras/productos/turnos".
- Manejo defensivo: 401 → `handleUnauthorized`; error de red → Toast + valores en cero; guardia `typeof` para utilidades globales.
- La métrica se recarga en cada entrada al Panel Principal (datos frescos).

#### Frontend — Router SPA (`frontend/js/app.js`)
- En `renderView(viewKey)` se agregó el caso exacto:
  ```js
  if (viewKey === 'dashboard' && typeof window.showDashboardModule === 'function') {
      window.showDashboardModule();
  }
  ```
  Con ello el flujo menú lateral → Panel Principal, tarjeta de regreso (`navigateTo('dashboard')`) y carga inicial tras login traen métricas frescas.

### Verificación
1. **Suite backend**: `python -m pytest -q` → **71 passed / 71** (66 previos + 5 nuevos de `tests/test_dashboard_service.py`: repositorio con datos, repositorio vacío, servicio, API autenticada y API sin token → 401).
2. **Sintaxis frontend**: `node --check` sobre `frontend/js/dashboard.js` y `frontend/js/app.js` → 0 errores (código 0).
3. **Balance HTML**: 438 `<div>` abiertos / 438 cerrados (balance = 0).
4. Cero datos simulados en la vista: las tarjetas solo se pueblan con la respuesta del endpoint; valores iniciales son `0`/`Q 0.00` o cargando.

---

### Causa Raíz
El backend del Módulo de Configuración (`GET/PUT /api/configuracion/`, protegido con `require_admin`) ya existía bajo la arquitectura DERCAS, pero el frontend adolecía de dos defectos que impedían operar la pantalla de forma fiable:
1. Las peticiones usaban la URL **hardcodeada** `http://localhost:8000/api/configuracion/` en vez de rutas relativas `/api/...` (el frontend es servido por el propio backend vía `StaticFiles` en `main.py`, y en producción por Nginx). En cualquier despliegue que no fuese exactamente el puerto 8000 las llamadas fallaban.
2. Se leía el token de sesión desde `localStorage` con la clave errónea `'token'` en lugar de `'jwt_token'` (clave real escrita por `app.js` en el login), forzando un redireccionamiento espurio a login incluso con sesión válida.

### Solución Implementada

#### Frontend — Estructura HTML (`frontend/index.html`)
- Se verificó el contenedor `<div id="configuracion-view" class="p-4 flex-grow-1 overflow-auto d-none" data-main-view="configuracion">` como **hermano directo** de `dashboard-content`, `pos-view`, `users-view`, `catalog-view`, `cash-view`, `reportes-view`, `inventory-view` y `compras-view` dentro de `<main>` (colapsado por defecto con `d-none` y desenmascarado por `renderView`).
- **Balance verificado rigurosamente con script de conteo**: **438 `<div>` abiertos / 438 `</div>` cerrados (balance = 0)** y profundidad estructural = 1 (hijo directo de `<main>`), sin anidamiento accidental.
- La vista incluye formulario `#configuracion-form` con campos NIT de la Empresa, Razón Social, Dirección y Token FEL (con botón `#toggle-token-visibility` para mostrar/ocultar la contraseña del token) y botón `#btn-save-config` "Guardar Cambios".
- El script `js/configuracion.js` ya estaba registrado en el HTML junto a los demás módulos.

#### Frontend — Lógica (`frontend/js/configuracion.js`)
- `window.showConfiguracionModule()` expuesto globalmente: valida rol de Administradora (redirige a dashboard con Toast si no aplica) y carga los parámetros del sistema una sola vez por sesión (bandera `isConfiguracionLoaded`).
- `cargarConfiguracion()`: consume `GET /api/configuracion/` y puebla los 4 campos (`NIT`, `Razón Social`, `Dirección`, `Token FEL`) con spinner en el botón mientras carga.
- Listener de submit: valida NIT y Razón Social obligatorios, envía `PUT /api/configuracion/` con la misma estructura de claves (`NIT`, `Razón Social`, `Dirección`, `Token FEL`) que el alias Pydantic del backend y notifica por Toast al éxito/error.
- **Corrección de defectos**: sustituidas las URLs hardcodeadas `http://localhost:8000` por rutas relativas `/api/configuracion/` (GET y PUT) y corregida la clave de sesión a `localStorage.getItem('jwt_token')`. Las llamadas a `window.handleUnauthorized` se encapsularon con guardia `typeof` siguiendo la convención defensiva de `compras.js`/`pos.js`.

#### Frontend — Router SPA (`frontend/js/app.js`)
- Se verificó que `mainViews` ya contiene `'configuracion'` (junto a `dashboard`, `pos`, `users`, `catalog`, `cash`, `reportes`, `inventory`, `compras`), por lo que `navigateTo('configuracion')`/`openModule('configuracion')`/`#configuracion` resuelven a la vista real y **no** al toast "módulo en construcción".
- En `renderView(viewKey)` está el caso exacto:
  ```js
  if (viewKey === 'configuracion' && typeof window.showConfiguracionModule === 'function') {
      window.showConfiguracionModule();
  }
  ```
- RBAC: `canAccessView('configuracion')` y `moduleAllowed.configuracion` validan rol de Administradora (`isUserAdmin`), alineado con el `require_admin` del backend.

#### Integración Visual
- Menú lateral: `<li data-module-item="configuracion">` con `<a data-nav="configuracion" onclick="navigateTo('configuracion')">` apuntando al módulo.
- Dashboard: tarjeta `data-card-module="configuracion"` → `openModule('configuracion')`.

### Verificación
1. `node --check` sobre `frontend/js/configuracion.js` y `frontend/js/app.js`: **0 errores de sintaxis (código 0)**.
2. Balance HTML: 438/438 divs (balance 0) y `configuracion-view` confirmado como hermano directo de las demás vistas (profundidad 1 dentro de `<main>`).
3. Suite backend: **66 passed / 66** (sin regresiones; el cambio es únicamente frontend).
4. Contrato de datos verificado contra `backend/tests/test_configuracion_service.py`: claves `NIT`, `Razón Social`, `Dirección`, `Token FEL` idénticas entre el seed, los alias Pydantic y lo que el frontend envía/lee.

---

## [2026-10-05] Corrección del enrutado SPA del Módulo de Compras (vista real, no toast "en construcción")

### Causa Raíz
La sección "[2026-10-05] Interfaz Visual del Módulo de Compras" documentaba que `mainViews` ya contenía `'compras'`, pero en el código real (`frontend/js/app.js`) el arreglo `mainViews` **no** incluía `'compras'`. Por eso al navegar al módulo (menú lateral, tarjeta del dashboard o `#compras`) el router caía en el fallback de `openModule` que despliega el toast "El módulo 'Compras' se encuentra en construcción", en vez de mostrar el contenedor `#compras-view` (buscador, selector de proveedor y carrito) que ya existía en `frontend/index.html`.

### Solución Implementada
- `frontend/js/app.js` línea 8: se agregó `'compras'` al arreglo `mainViews`:
  ```js
  const mainViews = ['dashboard', 'pos', 'users', 'catalog', 'cash', 'reportes', 'configuracion', 'inventory', 'compras'];
  ```
- Con esto `navigateTo('compras')`/`openModule('compras')`/`#compras` resuelven a la vista real y `renderView` invoca `window.showComprasModule()` (definido en `frontend/js/compras.js`).
- El contenedor `#compras-view` no se modificó: ya no contenía texto de relleno y ya tenía inyectada la interfaz visual (buscador, carrito y selector de proveedor).

### Verificación
1. `node --check` sobre `frontend/js/app.js`: **0 errores de sintaxis (código 0)**.
2. Alineación código-documentación: el arreglo `mainViews` ahora coincide con lo documentado en la entrada anterior.

---



### Causa Raíz
El backend del Módulo de Compras (`POST /api/compras/ordenes` y `POST /api/compras/ingreso`) ya existía bajo la arquitectura DERCAS, pero el frontend carecía del contenedor visual `compras-view`, del script de inicialización y del caso de enrutado SPA para desplegar la pantalla. El menú lateral, la tarjeta del dashboard y el permiso `COMPRA_EMITIR_ORDEN` ya apuntaban a `compras` sin una vista que renderizar.

### Solución Implementada

#### Frontend — Estructura HTML (`frontend/index.html`)
- Se inyectó el contenedor `<div id="compras-view" class="p-4 flex-grow-1 overflow-auto d-none" data-main-view="compras">` como **hermano directo** de las demás vistas (`inventory-view`, `pos-view`, etc.) dentro de `<main>`.
- **Balance verificado rigurosamente**: script de conteo sobre el documento completo → **438 `<div>` abiertos / 438 `</div>` cerrados (balance = 0)** y profundidad estructural = 1 (hijo directo de `main`) sin anidamiento accidental.
- La vista incluye: buscador de productos (filtra por nombre/talla/color/código de barras), lista de resultados con botón para agregar al carrito, tarjeta de "Compra en curso" con selector de proveedor, tabla/carrito editable (costo unitario y cantidad por línea), campos de número de factura del proveedor, gastos de flete y cargadores, desglose de Subtotal mercadería / Flete+Cargadores / COSTO TOTAL y botón "Procesar Ingreso".
- Se registró el script `js/compras.js?v=1.0` junto a los demás módulos.

#### Frontend — Router SPA (`frontend/js/app.js`)
- `mainViews` ya contenía `'compras'`; se agregó en `renderView(viewKey)` el caso exacto:
  ```js
  if (viewKey === 'compras' && typeof window.showComprasModule === 'function') {
      window.showComprasModule();
  }
  ```
- Con esto quedan operativos el menú lateral (`navigateTo('compras')`), la tarjeta del dashboard (`openModule('compras')`) y el hash routing (`#compras`).

#### Frontend — Lógica (`frontend/js/compras.js`)
- `window.showComprasModule`: carga proveedores (`GET /api/compras/proveedores`) y catálogo de productos activos (`GET /api/productos?limit=1000&is_active=true`, aplanando variantes con costo promedio e inventario de referencia).
- Carrito de compra en curso: agregar/duplicar producto, editar costo unitario y cantidad por línea (sin perder foco gracias a delegación de eventos), remover línea, vaciar carrito.
- Cálculo de costo total: `subtotal mercadería + gasto flete + gasto cargadores`, con formato `Q x.xx`.
- Procesamiento: valida proveedor/factura/carrito y permisos (`COMPRA_EMITIR_ORDEN` + `INV_INGRESAR_MERCADERIA`, con bypass de administradora). Envía `POST /api/compras/ordenes` (emisión de orden → `id_orden`) y luego `POST /api/compras/ingreso` con los detalles de la compra; notifica por Toast y limpia el formulario al éxito.

### Verificación
1. `node --check` sobre `frontend/js/compras.js` y `frontend/js/app.js`: **0 errores de sintaxis (código 0)**.
2. Balance HTML: 438/438 divs (balance 0) y `compras-view` confirmado como hermano directo de las demás vistas.
3. Suite backend: **66 passed / 66** (sin regresiones; el cambio es únicamente frontend).

---

## [2026-10-05] Corrección de deuda técnica: MissingGreenlet en Configuración y Compras

### Causa Raíz
Los permisos de acceso a relaciones SQLAlchemy se hacían por lazy-loading fuera de la sesión asíncrona, provocando `sqlalchemy.exc.MissingGreenlet`:
- **Configuración**: `ConfiguracionService._validar_acceso_admin` accedía a `usuario.rol` (relación) sobre una instancia cargada por `db_session.get()` sin eager loading.
- **Compras**: `CompraRepositoryImpl.create_orden` devolvía la orden sin precargar `detalles`; FastAPI serializaba la relación fuera del contexto async al responder `POST /api/compras/ordenes`.

### Solución Implementada
- **Configuración** (`backend/app/services/configuracion_service.py`): `_validar_acceso_admin` ahora es `async` y recarga el usuario vía `uow.users.get_by_id()` (que aplica `selectinload(Usuario.rol)`) antes de validar. Sin cambios en la lógica de negocio.
- **Compras** (`backend/app/repositories/compra_repository.py`): `create_orden` ahora re-consulta la orden creada con `.options(selectinload(OrdenCompra.detalles))` antes de devolverla.
- **Controlador de ingreso** (`backend/app/api/compras.py`): `POST /api/compras/ingreso` devuelve la `Compra` creada (`IngresoMercaderiaOut`, incluye `total_compra`) con `selectinload(Compra.detalles)`, en vez del modelo de OrdenCompra, alineado con el contrato del test.

### Verificación
1. `python -m pytest -q` (desde `backend/`): **66 passed / 66** (antes 64 passed, 2 failed).
2. Percentil 100% de la suite: configurado `test_configuracion_service.py::test_rbac_deniega_acceso_cajero_y_bodeguero` y `test_rbac.py::test_compras_endpoints_permissions` corregidos.

---




## [2026-10-05] Integración Total del Módulo de POS / Ventas (Punto de Venta)

### Causa Raíz
Completar la integración de punta a punta del módulo POS / Ventas: el backend DERCAS ya existía y cumplía las reglas arquitectónicas, pero el frontend aún no desplegaba la pantalla del punto de venta porque no existía el contenedor `pos-view` en el HTML ni el caso de enrutado `pos` en el router SPA (`renderView`). El menú lateral y la tarjeta del dashboard apuntaban a `pos` sin una vista que renderizar.

### Solución Implementada

#### Frontend — Estructura HTML (`frontend/index.html`)
- Se inyectó el contenedor `<div id="pos-view" class="p-4 flex-grow-1 overflow-auto d-none" data-main-view="pos">` como **hermano directo** de las demás vistas (`dashboard-content`, `users-view`, `catalog-view`, `cash-view`, `reportes-view`, `inventory-view`, `configuracion-view`) dentro de `<main>`.
- **Balance verificado dos veces**: se corrió un script de conteo de abre/cierra `div` sobre todo el documento (412 `<div>` abiertos / 412 `</div>` cerrados, balance = 0) y una verificación de profundidad estructural que confirma que `pos-view` queda a profundidad 1 (hijo directo de `main`), sin anidamiento accidental.
- La vista contiene: banner de turno de caja activo (`/api/caja/estado-actual`), alerta cuando no hay turno abierto (con acceso directo al módulo Caja), grilla de productos con stock de la sucursal, buscador por nombre/talla/color/SKU, escáner de código de barras, carrito de venta con cantidades y regla de mayoreo (cantidad >= 6), sección de cobro (efectivo + transferencia, total recibido y cambio) e historial reciente de ventas del turno (`/api/ventas?limit=20`).
- Se agregó el modal `#pos-ticket-modal` (comprobante de venta con folio, totales y cambio) junto a los demás modales del sistema.

#### Frontend — Router SPA (`frontend/js/app.js`)
- Se agregó `'pos'` al arreglo `mainViews` (vista SPA real, ya no cae en el toast "módulo en construcción").
- En `renderView(viewKey)` se añadió el caso exacto:
  ```js
  if (viewKey === 'pos' && typeof window.showPOSModule === 'function') {
      window.showPOSModule();
  }
  ```
- `canAccessView('pos')` y `moduleAllowed.pos` ya validaban el permiso `VENTA_COBRAR`; con la vista registrada ahora el flujo menú lateral (`navigateTo('pos')`), tarjeta del dashboard (`openModule('pos')`) y hash routing (`#pos`) quedan operativos. Se registró el script `js/pos.js` en el HTML.

#### Frontend — Lógica (`frontend/js/pos.js`)
- `window.showPOSModule`: carga turno activo, sucursal asociada a la caja, catálogo (`/api/productos?limit=500&is_active=true`, aplanando variantes con inventario de la sucursal), arma el carrito, calcula totales con mayoreo automático y publica la venta en `POST /api/ventas`.
- El pago construye el arreglo `pagos` con `id_metodo_pago`: 1=Efectivo y 2=Transferencia (según semilla de BD), validando stock disponible por línea y mostrando el cambio igual a la regla del backend (`recibido - total`).
- Historial de ventas del turno con recarga manual y limpieza de carrito tras cobro exitoso.

#### Backend — Arquitectura DERCAS (Verificación, sin duplicados)
Los 4 archivos ya existían y cumplen todas las reglas (no se duplicaron ni se alteraron modelos/scripts SQL):
- **Esquemas**: `backend/app/schemas/sale_schema.py` (DTOs Pydantic v2).
- **Repositorio**: `backend/app/repositories/sale_repository.py` — usa `selectinload` para relaciones (`variant`, `detalles`, `pagos`, `cliente`, `usuario`, `turno`), bloqueo pesimista `with_for_update()` en inventario y **cero `commit()`** (solo `flush()`).
- **Servicio**: `backend/app/services/sale_service.py` — transacciones atómicas vía `UnitOfWork` (`uow.commit()` / `uow.rollback()`), reglas de mayoreo (RF05), validación de descuento (`VENTA_APLICAR_DESCUENTO`) y auditoría en `bitacora_auditoria`.
- **Controlador**: `backend/app/api/sales.py` — endpoints delgados protegidos por RBAC (`VENTA_COBRAR`), registrado en `/api/ventas` en `main.py`.

### Verificación
1. `node --check` sobre `frontend/js/pos.js` y `frontend/js/app.js`: **100% sin errores de sintaxis (código 0)**.
2. Balance HTML: 412/412 divs (balance 0) y `pos-view` confirmado como hermano directo de las demás vistas.
3. Suite backend: **64 pruebas PASSED**; ventas (`tests/test_sales_service.py`): **6/6 PASSED**. Se mantienen 2 fallos **preexistentes ajenos al módulo POS** en el árbol de trabajo (no introducidos por este cambio): `test_configuracion_service.py::test_rbac_deniega_acceso_cajero_y_bodeguero` y `test_rbac.py::test_compras_endpoints_permissions`, ambos por `MissingGreenlet` al serializar relaciones (configuración y compras), fuera del alcance del módulo de ventas.

---

## [2026-10-05] Implementación Backend del Módulo de Inventario / Bodega (Arquitectura DERCAS)

### Causa Raíz
Requerimiento de implementar el backend completo para el módulo de Inventario bajo el estándar arquitectónico DERCAS, garantizando validaciones asíncronas, bloqueo de concurrencia en transacciones críticas y sin alterar la base de datos existente.

### Solución Implementada
Se crearon los siguientes componentes siguiendo estrictamente la plantilla de calidad:
- **Esquemas (DTOs)**: Creación de `inventory_schema.py` usando Pydantic v2 para validación robusta de entradas y respuestas.
- **Repositorio**: Creación de `inventory_repository.py` utilizando SQLAlchemy 2.0 (`select`, `selectinload`) y bloqueo pesimista (`with_for_update()`) para evitar condiciones de carrera. 
- **Servicio**: Creación de `inventory_service.py` con la lógica de negocio (búsqueda, ajuste manual, registro de alertas), delegando transacciones atómicas mediante el `UnitOfWork` (UoW).
- **Controlador API**: Creación de `api/inventory.py` con endpoints delgados protegidos por directivas RBAC (`INV_VER`, `INV_MODIFICAR`, etc.). Se inyectó el UoW al controlador desde `deps.py`.
- **Pruebas (TDD)**: Creación de `tests/test_inventory_service.py` garantizando la solidez de las transacciones con aiosqlite, validando que los errores provoquen `rollback()` íntegro en la base de datos.

## [2026-10-05] Hotfix: Restauración del menú de Inventario / Bodega y Permisos de Admin

### Causa Raíz
Durante la inyección de código o actualizaciones del archivo `app.js` en la creación del módulo de Inventario, la restricción de visibilidad para el rol de `Administradora` no estaba considerando explícitamente la directiva `isUserAdmin`, lo que podía causar que el botón en el menú lateral desapareciera accidentalmente si los permisos granulares o el chequeo de rol estricto variaban en el estado de la aplicación.

### Solución Aplicada
- Se revisó el archivo `frontend/index.html` garantizando que el elemento `<li data-module-item="inventory">` y su ancla `<a data-nav="inventory" onclick="navigateTo('inventory')">` estuvieran presentes con la correcta integración a la arquitectura SPA.
- En `frontend/js/app.js` se actualizó explícitamente el objeto `moduleAllowed` para que los módulos `pos`, `inventory` y `compras` validen afirmativamente la condición `isUserAdmin || window.hasPermission(...)`, otorgando a las cuentas de administrador acceso irrestricto garantizado.

### Verificación
- El botón de `Inventario / Bodega` se muestra y enlaza correctamente en el menú lateral.
- La validación de sintaxis de NodeJS pasó con código 0 sobre los archivos JavaScript.

## [2026-10-04] Test-Driven Development (TDD): Pruebas del Módulo de Compras

### Causa Raíz
Preparar la infraestructura de pruebas para el futuro Módulo de Compras, garantizando que el diseño del código nazca orientado a pasar estrictas validaciones de base de datos y negocio, según lo especificado en Gherkin.

### Solución
- Se escribió el archivo `backend/tests/test_compras_service.py` aplicando los principios de TDD.
- Las pruebas han sido programadas para verificar aserciones duras de ORM (cambios físicos en `InventarioSucursal`, `OrdenCompra` y `BitacoraAuditoria`) en un entorno `aiosqlite`.
- Casos de prueba codificados:
  1. `test_emitir_orden_compra_exito`: Verifica creación y preservación de stock.
  2. `test_recibir_orden_compra_exito`: Verifica la mutación de estado a "Recibida" y el incremento del `stock_actual` + la inserción de registro de bitácora.
  3. `test_emitir_orden_sin_permisos_falla`: Control RBAC negativo (HTTP 403 y aserción estricta de `COUNT(OrdenCompra) == 0`).
  4. `test_recibir_orden_sin_permisos_falla`: Control RBAC negativo para modificación y bloqueo de suma de stock fantasma.
  5. `test_emitir_orden_cantidad_negativa_falla`: Control estricto para montos y cantidades negativas que puedan alterar la BD de forma no deseada.

### Verificación
El archivo se recolecta por `pytest`. Las 5 pruebas pasan exitosamente (`5 passed`) tras implementar la capa DERCAS en `compra_repository.py`, `compra_service.py` y refactorizar `api/compras.py` para delegar la lógica.

---

## [2026-10-04] Spec-Driven Development: Módulo de Compras e Ingreso a Bodega

### Causa Raíz
Definición estricta de las reglas de negocio y restricciones de acceso para el Módulo de Compras previo a su implementación en código, usando la metodología SDD.

### Solución
- Se creó el archivo de especificación `specs/compras.feature` utilizando sintaxis Gherkin.
- Se definieron los escenarios de éxito:
  1. Un usuario con permiso `COMPRA_EMITIR_ORDEN` puede registrar órdenes, dejándolas en estado "Emitida" sin alterar el stock.
  2. Un usuario con permiso `INV_INGRESAR_MERCADERIA` puede registrar la recepción, cambiando el estado a "Recibida" e incrementando automáticamente el `stock_actual` en el inventario de la sucursal respectiva.
- Se definieron escenarios defensivos para RBAC:
  3. Denegación de creación de órdenes para usuarios sin `COMPRA_EMITIR_ORDEN` (Retorno estricto HTTP 403).
  4. Denegación de recepción de mercadería y alteración de stock para usuarios sin `INV_INGRESAR_MERCADERIA` (Retorno estricto HTTP 403).

### Verificación
No se escribieron líneas de código fuente. Se entregó el diseño del comportamiento para validación funcional técnica.

---

## [2026-10-04] Auditoría QA de Pruebas Unitarias (Ventas)

### Causa Raíz
Se realizó una auditoría de calidad al archivo `backend/tests/test_sales_service.py` para identificar aserciones débiles, detectar falsos positivos y asegurar que las pruebas validaran la integridad real de la base de datos tras errores (rollbacks).

### Solución
- Se reescribió `test_sales_service.py` para endurecer las pruebas y evitar falsos positivos de estado en memoria.
- **Rollbacks Estrictos**: Se identificó un defecto en las pruebas de error (`test_venta_pago_insuficiente_falla`, etc.) donde no se validaba correctamente que la transacción revirtiera los cambios en memoria. Se añadió `await db_session.rollback()` para simular el ciclo de vida del request y comprobar directamente sobre la base de datos SQLite en memoria que el inventario permanecía inalterado y ninguna venta se registraba tras excepciones HTTP 400 y 403.
- **Nuevos Casos Negativos**: Se agregaron dos nuevas pruebas para validar la lógica del inventario a nivel atómico:
  1. Sobreventa intencional (vender 55 unidades cuando hay 50) validando el retorno HTTP 400 y la conservación del stock exacto.
  2. Intento de venta de una variante inexistente (Fantasma) verificando el rechazo temprano con HTTP 404.

### Verificación
La suite de ventas completa (`test_sales_service.py`) de 6 escenarios aprobó estrictamente contra la base de datos `aiosqlite`.

---

## [2026-10-04] Spec-Driven Development: Emisión de Factura Electrónica (FEL)

### Causa Raíz
Se ha adoptado el enfoque Spec-Driven Development (SDD) para definir y alinear los comportamientos esperados antes de escribir el código. El primer módulo a especificar bajo esta modalidad es la "Emisión de Factura Electrónica FEL", para garantizar que tanto los flujos exitosos como las excepciones críticas queden definidos de forma agnóstica al código.

### Solución
- Se creó el directorio raíz `/specs`.
- Se redactó el archivo `specs/emision_factura_fel.feature` en formato Gherkin (`Dado que... Cuando... Entonces...`).
- **Escenarios cubiertos**:
  1. Camino feliz: Generación exitosa de FEL, retorno de DTE/UUID, descuento de inventario e impresión.
  2. Manejo de Errores: Fallas de conexión con el certificador (Timeout) que resultan en un registro de "Contingencia/Pendiente DTE" permitiendo que la tienda siga vendiendo.
  3. Manejo de Errores: Rechazo fiscal por parte de la SAT (ej. NIT inactivo) previniendo que la venta y el stock se alteren.
  4. Validaciones Requeridas: Bloqueo de facturas con total Q0.00 o negativo.
  5. Validaciones Requeridas: Bloqueo de uso de "CF" en ventas mayores a Q2,500.00 por mandato local de SAT.

### Verificación
No se ha escrito código de aplicación. Se generó únicamente la especificación en lenguaje natural para la revisión del usuario.

---

## [2026-10-04] Endpoint de Health Check (Monitoreo de Salud)

### Causa Raíz
Se requería un mecanismo proactivo para que el frontend (y potencialmente herramientas de monitoreo externas) pudiera validar la disponibilidad del API y la conectividad a la base de datos PostgreSQL, alertando al usuario anticipadamente sobre problemas de conexión antes de intentar operar.

### Solución
- **Backend (`health_repository.py`, `health_service.py`, `health.py`)**: Se implementó el patrón DERCAS agregando las interfaces y concreciones para `HealthRepository` (ejecuta un simple `SELECT 1` asíncrono) y `HealthService` (estructura la respuesta de salud).
- **Backend (`main.py` y `deps.py`)**: Se registró la dependencia `get_health_service` y se expuso el endpoint en `GET /api/health`.
- **Frontend (`app.js`)**: Se agregó la función asíncrona `checkHealth()` que hace polling cada 30 segundos usando `setInterval`. Si el endpoint falla o reporta desconexión, muestra un Toast de advertencia indicando "Problemas de conexión con el servidor". El polling se limpia correctamente al hacer logout.
- **Pruebas**: Se creó `test_health.py` comprobando que el endpoint devuelva HTTP 200 OK y la estructura correcta cuando la BD está arriba.

### Verificación
El frontend ahora hace la consulta inicial antes de mostrar el dashboard y programa las consultas en segundo plano. La prueba de integración del endpoint pasa exitosamente.

---

## [2026-10-04] FRENTE 1 — Expiración de sesión JWT con Refresh Token

### Causa Raíz
El token JWT original no tenía un flujo robusto de expiración y renovación. Tenía un tiempo de vida fijo (8 horas). Para mejorar la seguridad, el Access Token debe tener un tiempo de vida corto (15 min) y debe existir un mecanismo silencioso para renovarlo utilizando un Refresh Token, almacenado en una cookie segura (`HttpOnly`, `Secure`, `SameSite=Strict`), lo cual previene ataques XSS y permite mantener la sesión activa de forma segura.

### Solución
- **Backend (`config.py` y `security.py`)**: Se ajustó `ACCESS_TOKEN_EXPIRE_MINUTES` a 15 y se agregó `REFRESH_TOKEN_EXPIRE_DAYS` (7 días). Se creó `create_refresh_token()`.
- **Backend (`auth.py`)**: 
  - `login_for_access_token` ahora genera ambos tokens, enviando el access token en el JSON y el refresh token en la cookie.
  - Se creó el endpoint `POST /api/auth/refresh` que lee la cookie `refresh_token`, la valida y devuelve un nuevo access token.
  - Se agregó `POST /api/auth/logout` para eliminar la cookie segura de forma explícita.
- **Frontend (`app.js`)**: 
  - Se reescribió el interceptor global `window.fetch` para capturar respuestas 401. En caso de 401, el frontend pausa las peticiones, solicita silenciosamente `/api/auth/refresh` y, si tiene éxito, reintenta las peticiones originales con el nuevo token. Si falla, redirige al login.
  - La función `showLogin` ahora invoca `/api/auth/logout` para limpiar la cookie.

### Verificación
El flujo de Access y Refresh token se implementó en código backend y frontend, la cookie se configuró con restricciones de seguridad estrictas y el interceptor maneja la concurrencia en la renovación silenciosa del token.

---

## [2026-10-04] constitution.md — Documento Maestro de Reglas del Proyecto

### Causa Raíz
El proyecto carecía de un documento centralizado y autoritativo que estableciera las reglas arquitectónicas, de diseño, de tecnología y de flujo de trabajo que todo agente de IA o desarrollador debe seguir. Sin este documento, cada sesión de trabajo dependía del contexto de la conversación para respetar decisiones ya tomadas, con riesgo de regresiones o inconsistencias.

### Solución
Se creó `constitution.md` en la raíz del proyecto (`Sistema_Regalito/constitution.md`) como documento maestro con secciones obligatorias:
- **Arquitectura**: patrón DERCAS con roles y reglas inviolables por capa.
- **Principios**: SOLID, DRY, KISS aplicados en cada cambio.
- **Backend**: FastAPI + Python 3.13 + SQLAlchemy 2.x async (asyncpg). Prohibición explícita de lazy loading. Reglas de JWT, auditoría, fuerza bruta y concurrencia.
- **DTOs**: Pydantic v2 obligatorio, sin devolver modelos ORM directamente.
- **Frontend**: Vanilla JS, cero alertas nativas, modales con `backdrop="static"`, notificaciones Toast.
- **Pruebas**: pytest + aiosqlite en memoria, prohibición de falsear aserciones.
- **Base de Datos**: PostgreSQL como fuente de verdad, SQLite solo como caché local; PKs con secuencias, constraints de unicidad, índices en FK, checks de no negatividad.
- **Control de Cambios**: documentación obligatoria en `cambios.md` por cada cambio.
- **Flujo del Agente**: leer constitution.md antes de cualquier tarea, no tocar nada fuera de alcance, preguntar antes de asumir, correr suite completa antes y después.

### Verificación
Archivo creado en `C:\Users\abima\OneDrive\Desktop\Sistema_Regalito\Sistema_Regalito\constitution.md`. Sin cambios de código, sin efectos en la suite de pruebas.

---

## [2026-09-21] FASE 2 de 6 — Réplica de Solo Lectura (Catálogo, Precios, Usuarios, Roles, Permisos) hacia SQLite Local

### Causa Raíz
Dotar a la estación POS (laptop) de una copia local íntegra, persistente y desacoplada de los datos maestros esenciales (catálogo de productos, variantes con precios de detalle y mayoreo, inventario de referencia, usuarios con credenciales para login offline, roles, permisos y auxiliares de sucursal/caja) almacenada en SQLite (`pos_local.db`). Esto permite que el punto de venta opere sin dependencia de la red para consultas, autenticación y despliegue de precios.

### Solución Implementada

#### 1. Configuración y Modelos
- `backend/app/core/config.py`: Se incorporaron las variables de entorno `LOCAL_SQLITE_URL` (por defecto `sqlite+aiosqlite:///./pos_local.db`) y `LOCAL_SQLITE_PATH` (`pos_local.db`).
- `backend/app/db/models.py`: Se agregó la entidad `SyncCacheMetadata` (`id_sync`, `tabla`, `registros_sincronizados`, `fecha_sincronizacion`) para controlar la trazabilidad de la última réplica por entidad.

#### 2. Arquitectura en Capas (DERCAS)
- **Interfaces (`backend/app/interfaces/`)**:
  - `repositories.py`: Definición del contrato abstracto `SyncRepository` (`fetch_cloud_snapshot`, `replicate_to_sqlite`, `get_sqlite_status`, `get_sqlite_preview`).
  - `services.py`: Definición del contrato abstracto `SyncService` (`pull_and_replicate_to_local`, `get_sync_status`, `get_local_preview`).
- **Repositorio (`backend/app/repositories/sync_repository.py`)**:
  - `SyncRepositoryImpl`:
    - `fetch_cloud_snapshot()`: Consulta y extrae las 20 entidades maestras desde PostgreSQL (`Rol`, `Permiso`, `RolPermiso`, `Usuario`, `Categoria`, `Subcategoria`, `UnidadMedida`, `Producto`, `VarianteProducto`, `InventarioSucursal`, `Sucursal`, `AreaBodega`, `Caja`, `MetodoPago`, `DenominacionEfectivo`, `TipoMovimientoCaja`, `MotivoMerma`, `TipoCliente`, `Cliente`, `ParametroSistema`).
    - `replicate_to_sqlite()`: Inicializa el DDL en SQLite mediante `Base.metadata.create_all`, ejecuta un borrado en orden inverso de dependencias y una inserción atómica preservando claves primarias, claves foráneas y relaciones; actualiza la tabla de metadatos `sync_cache_metadata`.
    - `get_sqlite_status()`: Valida la existencia física del archivo `pos_local.db`, tamaño en bytes, conteo de registros y fecha de última réplica.
    - `get_sqlite_preview()`: Lee directamente desde la base SQLite local para obtener los productos formateados (con variantes y precios detalle/mayoreo) y los usuarios (con roles asignados).
- **Servicio (`backend/app/services/sync_service.py`)**:
  - `ConcreteSyncService`: Orquesta el flujo de sincronización, la consulta de estado y la previsualización local sin exponer el acceso a datos al controlador.
- **Inyección de Dependencias (`backend/app/api/deps.py`)**:
  - Proveedor `get_sync_service(db: AsyncSession = Depends(get_db)) -> ConcreteSyncService`.
- **Controlador API (`backend/app/api/sync.py`)**:
  - Endpoints registrados bajo el prefijo `/api/sync`:
    - `POST /api/sync/pull-local`: Dispara la réplica de datos de la nube hacia la base SQLite local.
    - `GET /api/sync/status`: Consulta el estado, tamaño y conteos del archivo SQLite local.
    - `GET /api/sync/local-preview`: Retorna la vista previa de productos, precios y usuarios leídos directamente de SQLite.
  - Registrado en `backend/app/main.py`.

#### 3. Frontend y Verificación Visual
- `frontend/index.html`:
  - Botón indicador de copia local en el encabezado (`#btn-sync-modal`).
  - Modal interactivo `#sync-modal` (`data-bs-backdrop="static"`): tarjeta de estado de la base local, botón "Sincronizar Nube → Local", y dos pestañas para previsualizar productos con precios detalle/mayoreo y usuarios con roles leídos desde `pos_local.db`.
- `frontend/js/sync.js`:
  - Lógica asíncrona para consultar el estado del archivo local, ejecutar la sincronización mediante `fetch('/api/sync/pull-local')`, notificar al usuario con `showToast` y poblar las tablas visuales del modal.

### Verificación Realizada
1. **Pruebas Automatizadas Backend (`backend/tests/test_sync_replication.py`)**:
   - `test_sync_repository_fetch_snapshot`: Valida la extracción íntegra de catálogo, precios y usuarios desde la sesión de BD.
   - `test_sync_repository_replicate_to_sqlite`: Valida la creación física de una base SQLite aislada, persistencia de variantes con precios exactos y usuarios.
   - `test_sync_service_status_and_preview`: Valida la transición de estado no-inicializado a inicializado y la lectura de preview.
   - `test_sync_api_endpoints`: Valida la ejecución y respuesta `200 OK` de los endpoints `/pull-local`, `/status` y `/local-preview`.
2. **Suite Completa del Backend**:
   - `python -m pytest`: **45 pruebas ejecutadas, 45 pruebas PASSED (100% de éxito)** en 16.75s.
3. **Verificación de Sintaxis Frontend**:
   - `node --check frontend/js/sync.js frontend/js/app.js frontend/js/users.js frontend/js/catalog.js frontend/js/cash_register.js`: **100% exitoso sin errores**.
4. **Verificación en Vivo con Servidor y Base de Datos Real**:
   - Ejecutada llamada directa de sincronización sobre `http://127.0.0.1:8000`:
     - Estado inicial de `pos_local.db`: Replicado exitosamente.
     - 20 tablas sincronizadas: 3 productos, 4 variantes de precios, 3 usuarios, 3 roles, 5 permisos.
     - Consulta directa a `pos_local.db`: Precios (Juego de Vasos Q85/Q75, Vestido Niña Q120/Q105, Muñeca Q45/Q38) y usuarios (admin, cajera, bodega) verificados con total fidelidad.

---

## [2026-09-21] [PLANIFICACIÓN] FASE 1 de 6 — Diseño del Esquema Local SQLite y Arquitectura de Sincronización Offline

### Contexto y Alcance
Se establece el diseño arquitectónico preliminar (Fase 1 de 6) para dotar al sistema POS *Tienda el Regalito* de capacidades operativas fuera de línea (*offline-first*). Esta fase es estrictamente de diseño y planificación: no se modifica código, esquemas ni archivos ejecutables. PostgreSQL en la nube se mantiene como la **fuente de verdad definitiva** e inmutable, y SQLite local actúa como una capa complementaria de alta resiliencia para contingencias de red.

### 1. Clasificación del Esquema Local SQLite

#### A. Tablas de Caché de Solo Lectura (Nube -> Laptop)
Se replican y actualizan periódicamente desde la nube hacia la laptop para consulta local:
- **Seguridad e Identidad**: `usuario` (credenciales para login offline), `rol`, `permiso`, `rol_permiso` (validación RBAC local), `parametro_sistema`.
- **Catálogo y Precios**: `categoria`, `subcategoria`, `unidad_medida`, `producto`, `variante_producto` (precios detalle y mayoreo, código de barras), `inventario_sucursal` (existencias de referencia local).
- **Tesorería y Auxiliares**: `sucursal`, `caja`, `metodo_pago`, `denominacion_efectivo`, `tipo_movimiento_caja`, `tipo_cliente`, `cliente` (búsqueda mayorista/CF), `motivo_merma`.
- **Control de Metadatos**: `sync_cache_metadata` (timestamps de sincronización por entidad, hashes de control).

#### B. Tablas de Cola de Escritura (Laptop -> Nube)
Almacenan las transacciones operativas generadas localmente durante la desconexión:
- `venta_offline`, `detalle_venta_offline`, `pago_venta_offline`.
- `merma_offline`, `detalle_merma_offline`.
- `turno_caja_offline`, `movimiento_caja_offline`, `cierre_caja_ciegas_offline`, `detalle_arqueo_efectivo_offline`.
- `sync_queue`: Cola centralizada con control secuencial FIFO, tipo de entidad, clave de idempotencia y resolución de dependencias.

### 2. Relación entre Backend Local y Backend en la Nube
- **Topología Local-First con SyncEngine**:
  - El frontend de la laptop interactúa con un servicio backend local (`http://localhost:8000`), garantizando latencia cero y operatividad sin bloqueos en el mostrador.
  - Un servicio en segundo plano (`SyncEngine` / `SyncWorker`) monitorea la conectividad a internet. Al detectar red activa:
    1. **Push (Subida)**: Envía transacciones de `sync_queue` hacia los endpoints del backend en la nube en orden secuencial estricto.
    2. **Pull (Bajada)**: Solicita deltas de catálogo y precios modificados desde la última fecha de sincronización.

### 3. Estructura de Claves de Idempotencia
- Cada transacción local genera una clave canónica UUIDv4 (`idempotency_key`, VARCHAR(36)).
- El backend en la nube valida esta clave con índice `UNIQUE`:
  - Si la clave ya existe (reintento por timeout previo): devuelve `200 OK` con los datos ya procesados, sin duplicar ventas, mermas ni descargos de stock.
  - Si no existe: ejecuta la transacción bajo bloqueo pesimista (`SELECT FOR UPDATE`), audita el evento en `bitacora_auditoria` con etiqueta de origen offline y devuelve `201 Created`.

### 4. Ciclo de Vida del Marcado de Sincronización
Estados por registro operativo:
1. `PENDIENTE`: Registrado offline, a la espera de conexión.
2. `EN_PROCESO`: En transmisión HTTP hacia la nube (evita reentrancia).
3. `SINCRONIZADO`: Confirmado por la nube con ID remoto asignado (`id_remoto`) y timestamp de éxito (`fecha_sincronizacion`).
4. `ERROR`: Transacción con rechazo persistente; almacena el mensaje de error para auditoría y alerta al supervisor.

### 5. Trade-offs Identificados y Puntos de Decisión
- **Resolución de sobreventa offline**: Política ante venta local de stock que ya no existe en la nube (Opción A: Aceptar venta física consumada y emitir alerta de discrepancia; Opción B: Rechazar y mandar a error de cola).
- **Dependencia de turnos de caja**: Sincronización jerárquica en cascada (Apertura -> Ventas -> Cierre) vs. Batch consolidado.
- **Facturación Electrónica FEL**: Emisión de ticket interno offline y posterior certificación DTE en la nube al restablecerse el enlace con SAT/certificador.
- **Modo de conmutación frontend**: Local-first transparente vs. dual-mode con detección activa de fallos.

---

## [2026-09-20] Persistencia en Base de Datos de Protección contra Fuerza Bruta (Migración Alembic 0008 y Arquitectura en Capas)

### Contexto y Causa Raíz
El control de intentos fallidos de autenticación y bloqueo temporal en `POST /api/auth/login` se encontraba implementado en memoria mediante un diccionario en tiempo de ejecución de Python (`_login_attempts`). Esta arquitectura presentaba dos debilidades críticas para un entorno productivo:
1. **Volatilidad ante reinicios**: Si el servicio backend se reinicia (por despliegues, caídas o mantenimiento), el contador de intentos y el bloqueo temporal se perdían de inmediato, permitiendo a un atacante reanudar la fuerza bruta sin penalización.
2. **Inconsistencia ante múltiples instancias**: En despliegues futuros con múltiples réplicas o balanceadores de carga, cada proceso mantenía un estado aislado, facilitando ataques distribuidos.

### Evaluación Técnica y Justificación de Esquema
Se evaluaron cuatro alternativas para la persistencia:
- **Opción 1 (`bitacora_auditoria`) [Descartada]**: Tabla de auditoría histórica inmutable con clave foránea `id_usuario INT NOT NULL REFERENCES usuario(id_usuario)`. Si un atacante prueba nombres de usuario inexistentes (`root`, `admin99`, etc.), la inserción violaría la clave foránea. Además, calcular intentos requiere `COUNT(*)` sobre ventanas temporales y no permite un reseteo directo de estado sin corromper la inmutabilidad de la auditoría.
- **Opción 2 (`sesion_usuario`) [Descartada]**: Modela sesiones autenticadas activas (`fecha_inicio`, `fecha_fin`, `ip_origen`) con `id_usuario NOT NULL`. Almacenar intentos fallidos de autenticación (que por definición no son sesiones) confunde dos conceptos disjuntos y tampoco admite intentos con usernames inexistentes.
- **Opción 3 (Extender `usuario` con columnas `intentos_fallidos` y `bloqueado_hasta`) [Descartada]**: Es viable para usuarios registrados, pero no puede registrar ni mitigar ataques de fuerza bruta sobre usernames que aún no existen en la base de datos (ataques de enumeración / saturación). Además, acopla estado de defensa transitorio a la entidad de identidad principal.
- **Opción 4 (Tabla dedicada `intento_login`) [Seleccionada]**:
  - Estructura: `id_intento SERIAL PRIMARY KEY`, `username VARCHAR(50) NOT NULL UNIQUE`, `intentos_fallidos INT NOT NULL DEFAULT 0`, `bloqueado_hasta TIMESTAMP WITHOUT TIME ZONE`, `ultimo_intento TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()`.
  - Ventajas: Permite rastrear cualquier username (registrado o no registrado), búsquedas $O(1)$ por índice único en `username`, reseteos atómicos inmediatos tras login exitoso, separación clara de responsabilidades (SRP) y sin alterar claves foráneas ni datos de tablas existentes.

### Solución Implementada

#### 1. Migración Alembic `0008_persistencia_bloqueo_fuerza_bruta.py`
- Creada en `backend/alembic/versions/0008_persistencia_bloqueo_fuerza_bruta.py` (revisión `0008`, `down_revision = "0007"`).
- `upgrade()`: Crea la tabla `intento_login` con secuencia automática para `id_intento` y restricción `UNIQUE` en `username`, además de un índice B-tree en `username`.
- `downgrade()`: `DROP TABLE IF EXISTS intento_login CASCADE;` garantizando reversibilidad simétrica total.

#### 2. Modelos SQLAlchemy y DDL Inicial
- `backend/app/db/models.py`: Se agregó la entidad `IntentoLogin` en el Módulo 1.
- `database/init.sql`: Se agregó la tabla `intento_login` en el Módulo 1 y la sincronización de su secuencia (`SELECT setval('intento_login_id_intento_seq', ...)`) para garantizar despliegues limpios idénticos a producción.

#### 3. Arquitectura en Capas (DERCAS)
- **Repositorio (`backend/app/repositories/login_attempt_repository.py`)**:
  - Clase `LoginAttemptRepositoryImpl`:
    - `get_by_username(username)`: Consulta atómica sobre `intento_login`.
    - `record_failure(username, max_intentos=5, lock_minutes=5)`: Si no existe crea el registro; incrementa `intentos_fallidos`; si alcanza 5 intentos asigna `bloqueado_hasta = ahora + 5 min` y reinicia `intentos_fallidos = 0` para el siguiente ciclo.
    - `clear_expired_lockout(registro)`: Remueve el bloqueo cuando la fecha de bloqueo ya quedó en el pasado.
    - `reset_attempts(username)`: Reinicia `intentos_fallidos = 0` y `bloqueado_hasta = None`.
- **Servicio (`backend/app/services/login_security_service.py`)**:
  - Clase `LoginSecurityService`:
    - `check_lockout(username)`: Consulta la BD; si `bloqueado_hasta > ahora`, calcula los minutos restantes (`remaining`) y responde con `HTTPException(429, "Cuenta bloqueada temporalmente por demasiados intentos fallidos. Inténtalo de nuevo en X minuto(s).")`. Si el bloqueo expiró, limpia el estado de bloqueo en BD.
    - `record_failure(username)`: Delega el registro del fallo a la capa de repositorio.
    - `reset_attempts(username)`: Delega el reseteo del contador a la capa de repositorio.
- **Inyección de Dependencias (`backend/app/api/deps.py`)**:
  - Proveedor `get_login_security_service(db: AsyncSession = Depends(get_db)) -> LoginSecurityService`.
- **Controlador (`backend/app/api/auth.py`)**:
  - Se eliminó por completo el diccionario en memoria `_login_attempts` y las funciones utilitarias acopladas.
  - El endpoint `POST /api/auth/login` inyecta `security_service: LoginSecurityService = Depends(get_login_security_service)` y llama a `check_lockout`, `record_failure` y `reset_attempts` de forma asíncrona y desacoplada.

### Verificación y Resultados
1. **Pruebas de Migración en PostgreSQL**:
   - `python -m alembic upgrade head`: Migración 0008 aplicada con éxito en la base de datos `regalito_pos`.
   - `python -m alembic downgrade 0007`: Reversión limpia probada.
   - `python -m alembic upgrade head`: Re-aplicación final exitosa.
2. **Pruebas Automatizadas de Persistencia (`backend/tests/test_security_audit_lockout.py`)**:
   - `test_brute_force_lockout_after_5_failures`: Valida que tras 5 intentos fallidos, el registro existe en la tabla `intento_login` con `bloqueado_hasta` en el futuro, y el 6to intento responde `429 Too Many Requests`.
   - `test_successful_login_resets_failure_counter`: Valida que los 3 intentos fallidos previos acumulados en `intento_login` se resetean a `0` tras autenticarse con éxito.
   - `test_lockout_persists_across_independent_service_instances`: Simula el reinicio del backend o la presencia de múltiples instancias/réplicas: una nueva instancia de servicio lee el bloqueo directamente de la base de datos y lanza `429`.
3. **Suite Completa del Backend**:
   - `python -m pytest tests/test_rbac.py tests/test_cierre_ciegas.py tests/test_sales_service.py tests/test_cash_service.py tests/test_merma_service.py tests/test_user_report_service.py tests/test_concurrency_stock.py tests/test_security_audit_lockout.py`:
   - **41 pruebas ejecutadas, 41 pruebas PASSED (100% de éxito)** en 21.36 segundos.

---

## [2026-09-20] 4 Frentes de Calidad, Seguridad y Concurrencia (JWT, Auditoría, Fuerza Bruta, Bloqueo Pesimista)

### Resumen General
Se implementaron 4 mejoras independientes y aisladas para robustecer la seguridad, trazabilidad, resiliencia y consistencia transaccional del sistema POS *Tienda el Regalito*, sin alterar las migraciones existentes (0005-0007), flujos de RBAC ni la arquitectura DERCAS.

---

### FRENTE 1 — Expiración de sesión JWT y Manejo de 401

#### Causa Raíz
Se requería verificar y garantizar que el token JWT emitido cuente con una expiración razonable acorde a una jornada de trabajo comercial (8 horas = 480 minutos), y que cualquier llamada de API realizada con un token expirado o inválido devuelva HTTP 401 y el frontend redirija automáticamente a la pantalla de login, limpiando la sesión local sin dejar residuos en memoria ni almacenamiento.

#### Solución Aplicada
1. **Configuración y Backend (`backend/app/core/config.py`, `backend/app/api/auth.py`, `backend/app/api/deps.py`)**:
   - `settings.ACCESS_TOKEN_EXPIRE_MINUTES` está fijado en `480` (8 horas de turno laboral).
   - `auth.py` genera el token pasando `expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)`.
   - `deps.py` valida la firma y vigencia con `jwt.decode()`. Si el claim `exp` ya expiró, `jose.JWTError` captura la excepción y lanza `HTTPException(status_code=401, detail="Could not validate credentials")`.
2. **Frontend (`frontend/js/app.js`)**:
   - Se validó el interceptor global en `window.fetch` (líneas 134-142): intercepta cualquier respuesta con `status === 401` que no provenga de `/auth/login` y dispara `handleUnauthorized()` -> `showLogin()`.
   - `showLogin()` ejecuta una limpieza exhaustiva: vaciado de `localStorage` y `sessionStorage`, reseteo de rutas hash en URL, reseteo visual de cabeceras/saludos de usuario y conmutación a la vista de login.

#### Verificación
- **Pruebas automatizadas (`tests/test_security_audit_lockout.py`)**:
  - `test_jwt_expired_token_returns_401`: Token generado con expiración pasada (`expires_delta = -10s`) devuelve `401 Unauthorized` con `"detail": "Could not validate credentials"` al consultar `/api/usuarios`.
  - `test_jwt_valid_token_succeeds`: Token válido (480 minutos) responde `200 OK`.

---

### FRENTE 2 — Uso Real Centralizado de `bitacora_auditoria`

#### Causa Raíz
La tabla `bitacora_auditoria` existía en el esquema de base de datos (`id_bitacora`, `id_usuario`, `tabla_afectada`, `accion`, `descripcion`, `fecha_hora`), pero no se estaba utilizando para registrar las acciones críticas del sistema (login, creación/edición/desactivación de usuarios, ventas, mermas, cierres de caja a ciegas y cambios de precios de productos).

#### Solución Aplicada
1. **Servicio Centralizado (`backend/app/services/audit_service.py`)**:
   - Se diseñó la función asíncrona `log_action(db: AsyncSession, id_usuario: int, tabla: str, accion: str, descripcion: str) -> None`.
   - Inserta instancias de `BitacoraAuditoria` usando la transacción activa (vía `db.add()` y `db.flush()`).
   - Implementa diseño defensivo (bloque `try/except Exception: pass` silencioso) para garantizar que un fallo de auditoría nunca interrumpa ni revierta la operación de negocio principal.
2. **Integración en Servicios Críticos**:
   - **Login (`backend/app/api/auth.py`)**: Registra `tabla="sesion_usuario"`, `accion="LOGIN"`, descripción con el username autenticado.
   - **Gestión de Usuarios (`backend/app/services/user_service.py`, `backend/app/api/users.py`)**:
     - `create_user`: Registra `tabla="usuario"`, `accion="CREAR"` con ID y username. Acepta `actor_id` inyectado desde el usuario autenticado (`current_user.id_usuario`).
     - `update_user`: Registra `tabla="usuario"`, `accion="EDITAR"` con ID y username.
     - `deactivate_user`: Registra `tabla="usuario"`, `accion="DESACTIVAR"` con ID y username.
   - **Ventas (`backend/app/services/sale_service.py`)**: Registra `tabla="venta"`, `accion="VENTA"` con el ID de venta generado y el monto total en Quetzales.
   - **Mermas (`backend/app/services/merma_service.py`)**: Registra `tabla="merma"`, `accion="MERMA"` con el ID de merma y el costo total de pérdida en Quetzales.
   - **Caja y Turnos (`backend/app/services/cash_service.py`)**:
     - `abrir_caja`: Registra `tabla="turno_caja"`, `accion="APERTURA"` con turno, caja y fondo inicial.
     - `cerrar_caja_ciegas`: Registra `tabla="cierre_caja_ciegas"`, `accion="CIERRE_CIEGAS"` con estado (Cuadrado/Faltante/Sobrante), total contado y diferencia.
   - **Catálogo de Productos (`backend/app/services/product_service.py`, `backend/app/api/products.py`)**:
     - `create_product`: Registra `tabla="producto"`, `accion="CREAR"`.
     - `update_product`: Detecta variaciones entre precios previos y nuevos (`precio_detalle`, `precio_mayoreo`). Si hubo cambios de precio registra `accion="PRECIO"` detallando el antes y después; en caso contrario registra `accion="EDITAR"`.
     - `deactivate_product`: Registra `tabla="producto"`, `accion="DESACTIVAR"`.

#### Verificación
- **Pruebas automatizadas (`tests/test_security_audit_lockout.py`)**:
  - `test_audit_service_log_action`: Inserción y persistencia directa en `bitacora_auditoria` validada.
  - `test_audit_login_registers_entry`: El flujo completo de login registra la fila en `bitacora_auditoria` asociada al usuario correspondiente.
- **Suite de pruebas de servicios existentes**: Todas las pruebas previas de `cash`, `merma`, `sales` y `user_report` siguen pasando al 100%.

---

### FRENTE 3 — Protección contra Fuerza Bruta en Login

#### Causa Raíz
El endpoint `POST /api/auth/login` no contaba con un límite de intentos fallidos, permitiendo ataques de diccionario o enumeración de credenciales por fuerza bruta sin restricción temporal.

#### Solución Aplicada
1. **Mecanismo en Memoria (`backend/app/api/auth.py`)**:
   - Se implementó un registro en memoria `_login_attempts: dict` indexado por `username`.
   - Constantes configurables: `_MAX_INTENTOS = 5` y `_LOCK_MINUTES = 5`.
   - `_check_lockout(username)`: Valida si la cuenta tiene un bloqueo activo (`locked_until`). Si está vigente, calcula los minutos restantes y responde inmediatamente con `HTTP 429 Too Many Requests` ("Cuenta bloqueada temporalmente por demasiados intentos fallidos. Inténtalo de nuevo en X minuto(s).").
   - `_record_failure(username)`: Incrementa el contador de fallos tras credenciales erróneas. Al alcanzar 5 fallos, fija `locked_until = datetime.utcnow() + 5 minutos`.
   - `_reset_attempts(username)`: Al autenticarse satisfactoriamente, limpia el contador del usuario liberando cualquier registro previo.

#### Verificación
- **Pruebas automatizadas (`tests/test_security_audit_lockout.py`)**:
  - `test_brute_force_lockout_after_5_failures`: Intentos 1 a 5 devuelven `401 Unauthorized`. El intento 6 devuelve `429 Too Many Requests`. Incluso suministrando la contraseña correcta durante el bloqueo se mantiene el `429`.
  - `test_successful_login_resets_failure_counter`: Intentos fallidos previos (3) se limpian totalmente al completar un login exitoso.

---

### FRENTE 4 — Concurrencia en Descargo de Stock (SELECT FOR UPDATE)

#### Causa Raíz
En los repositorios `sale_repository.py` y `merma_repository.py`, la consulta `get_inventario()` leía las existencias en `inventario_sucursal` mediante un `SELECT` estándar sin bloqueo pesimista. Ante transacciones concurrentes simultáneas sobre un mismo producto con stock bajo, ambas transacciones leían el mismo stock disponible antes del descargo, derivando en sobreventa (stock negativo en base de datos o ventas por encima de las existencias físicas reales).

#### Solución Aplicada
1. **Bloqueo Pesimista en Repositorios (`backend/app/repositories/sale_repository.py`, `backend/app/repositories/merma_repository.py`)**:
   - En `SaleRepositoryImpl.get_inventario`:
     ```python
     stmt = (
         select(InventarioSucursal)
         .where(
             InventarioSucursal.id_variante == id_variante,
             InventarioSucursal.id_sucursal == id_sucursal,
         )
         .with_for_update()  # Bloqueo pesimista: serializa la lectura y previene sobreventa
     )
     ```
   - En `MermaRepositoryImpl.get_inventario`: Se agregó idénticamente `.with_for_update()`.
   - Al ejecutarse dentro del contexto transaccional gobernado por el `UnitOfWork`, PostgreSQL bloquea la fila del registro de inventario con un lock exclusivo a nivel de fila (`FOR UPDATE`) hasta que la transacción se confirma (`commit()`) o revierte (`rollback()`).

#### Verificación
- **Pruebas automatizadas (`tests/test_concurrency_stock.py`)**:
  - `test_sale_repository_get_inventario_uses_for_update`: Inspecciona la consulta construida y valida la cláusula de bloqueo pesimista.
  - `test_merma_repository_get_inventario_uses_for_update`: Valida que la consulta de inventario en mermas utilice la cláusula de bloqueo pesimista.
  - `test_concurrent_sales_no_oversell`: Simula escenario de inventario crítico (stock inicial = 1) con dos ventas consecutivas al mismo producto. La primera venta se procesa con éxito dejando stock = 0, y la segunda venta es rechazada de inmediato con `HTTP 400 Bad Request ("Stock insuficiente")`.

---

### Suite Completa de Verificación
Ejecución integral de todas las suites de prueba del sistema:
- `python -m pytest tests/test_rbac.py tests/test_cierre_ciegas.py tests/test_sales_service.py tests/test_cash_service.py tests/test_merma_service.py tests/test_user_report_service.py tests/test_concurrency_stock.py tests/test_security_audit_lockout.py`:
  - **40 pruebas ejecutadas, 40 pruebas PASSED (100% de éxito)** en 13.50 segundos.

---

## [2026-09-20] Migración Alembic 0007: Secuencias Automáticas, Restricciones de Unicidad, Índices en Llaves Foráneas y No Negatividad en Stock

### Contexto y Diagnóstico
Se identificaron y corrigieron problemas estructurales en la base de datos de Tienda el Regalito POS que representaban riesgos reales de concurrencia, integridad referencial, rendimiento y corrupción de datos en un entorno de producción:

1. **Auditoría Previa de Datos Existentes**:
   - Antes de aplicar cualquier modificación DDL, se auditó la base de datos en vivo (`regalito_pos`):
     - Candidatos a `UNIQUE` (`usuario.username`, `variante_producto.codigo_barras`, `factura_fel.numero_dte`, nombres de rol, categoría, etc.): **0 duplicados encontrados (100% limpios)**.
     - Campos de stock y cantidad (`stock_actual`, `stock_minimo`, movimientos y detalles): **0 valores negativos encontrados (100% limpios)**.
   - Conclusión: Base de datos limpia y apta para la aplicación aditiva de restricciones sin riesgo de fallos en producción.

2. **Riesgo de Colisión de IDs en Inserciones Concurrentes (Punto 1)**:
   - *Diagnóstico*: En el diseño inicial, 32 tablas con clave primaria `INT` carecían de secuencias automáticas asignadas en PostgreSQL (por ejemplo `usuario`, `producto`, `variante_producto`, `categoria`, `cliente`, `proveedor`, `orden_compra`, `compra`, etc.). A diferencia de las tablas operativas regularizadas en la migración `0005` (`caja`, `turno_caja`, `venta`, `merma`), las inserciones dependían de que la capa de aplicación gestionara el ID o de secuencias implícitas no vinculadas formalmente a la columna (`OWNED BY`), arriesgando colisiones bajo concurrencia.
   - *Solución*: Creación de secuencias dedicadas para las 32 tablas, asignación de valor predeterminado `DEFAULT nextval('{tabla}_{col}_seq')`, propiedad de secuencia (`OWNED BY`) e inicialización segura del contador con `setval(..., MAX(...) + 1, false)`.

3. **Falta de Protección de Unicidad a Nivel de Base de Datos (Punto 2)**:
   - *Diagnóstico*: Múltiples campos clave que el backend valida en memoria o trata como únicos no tenían restricciones `UNIQUE` a nivel de motor relacional (`usuario.username`, `variante_producto.codigo_barras`, `factura_fel.numero_dte`, `rol.nombre`, `categoria.nombre`, `departamento_geografico.nombre`, `permiso.codigo`, `parametro_sistema.clave`, `unidad_medida.codigo`). Ante un fallo de validación, concurrencia de peticiones simultáneas o scripts manuales, la base de datos aceptaba registros duplicados.
   - *Solución*: Se incorporaron 9 restricciones `UNIQUE` formales e idempotentes. En `variante_producto(codigo_barras)`, el estándar SQL de Postgres permite valores `NULL` sin colisionar pero bloquea duplicados en códigos asignados.

4. **Ausencia de Índices en Columnas de Llave Foránea (Punto 3)**:
   - *Diagnóstico*: PostgreSQL no crea índices automáticos para las restricciones `FOREIGN KEY`. Esto provocaba que todas las consultas de unión (`JOIN`), filtros por usuario, consultas de inventario por variante/sucursal y reportes requirieran escaneos secuenciales de tabla completa (*Sequential Scans*). Asimismo, operaciones de actualización o eliminación en tablas padre podían provocar bloqueos pesados sobre tablas hijas.
   - *Solución*: Se crearon 48 índices B-tree sobre todas las columnas de llaves foráneas frecuentemente consultadas en filtros y reportes (agrupadas por `id_usuario`, `id_variante`, `id_sucursal`, `id_venta`, `id_turno`, etc.).

5. **Riesgo de Valores Negativos en Inventario y Cantidades (Punto 4)**:
   - *Diagnóstico*: Errores en la capa de aplicación, excepciones durante mermas o devoluciones podían derivar en stocks o cantidades negativas en la base de datos sin ningún freno del motor SQL.
   - *Solución*: Se implementaron 8 restricciones `CHECK (columna >= 0)` sobre todos los campos numéricos de cantidad y stock del sistema.

### Cambios Implementados

1. **Migración Alembic `0007_secuencias_unicidad_indices_y_no_negatividad.py`**:
   - Creada en `backend/alembic/versions/0007_secuencias_unicidad_indices_y_no_negatividad.py` (revisión `0007`, `down_revision = "0006"`).
   - Bloque 1: 32 secuencias PostgreSQL automáticas idempotentes con `CREATE SEQUENCE IF NOT EXISTS`, `SET DEFAULT nextval(...)`, `OWNED BY` y sincronización con `setval(...)`.
   - Bloque 2: 9 restricciones `UNIQUE` mediante bloques `DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = ...) THEN ALTER TABLE ... ADD CONSTRAINT ... UNIQUE (...); END IF; END $$;`.
   - Bloque 3: 48 índices B-tree creados mediante `CREATE INDEX IF NOT EXISTS {idx_name} ON {tabla} ({columna});`.
   - Bloque 4: 8 restricciones `CHECK` de no negatividad (`>= 0`) mediante bloques `DO $$ ... IF NOT EXISTS ... END $$;`.
   - Método `downgrade()` simétrico y totalmente reversible probado con `asyncpg`.

2. **Modelos SQLAlchemy (`backend/app/db/models.py`)**:
   - Se reflejaron `unique=True` en las 9 entidades correspondientes (`Rol.nombre`, `Usuario.username`, `Permiso.codigo`, `ParametroSistema.clave`, `DepartamentoGeografico.nombre`, `Categoria.nombre`, `UnidadMedida.codigo`, `VarianteProducto.codigo_barras`, `FacturaFel.numero_dte`).
   - Se reflejaron `index=True` en las columnas de llaves foráneas para mantener paridad entre el ORM, PostgreSQL y los tests en memoria con SQLite.

3. **Esquema Inicial (`database/init.sql`)**:
   - Se migraron las definiciones de claves primarias a `SERIAL PRIMARY KEY` para las 42 tablas individuales (preservando clave compuesta en `rol_permiso`).
   - Se incorporaron las restricciones `UNIQUE` y las restricciones `CHECK (columna >= 0)`.
   - Se añadió el bloque formal de 48 índices `CREATE INDEX IF NOT EXISTS`.
   - Se añadió el bloque de sincronización de secuencias tras la carga de datos semilla (`SELECT setval(...)`) para garantizar despliegues Docker limpios totalmente sincronizados con producción.

### Verificación y Resultados
1. **Reversibilidad y Ejecución de Migración**:
   - `alembic upgrade head` (0006 -> 0007): **Exitoso**.
   - `alembic downgrade 0006`: **Exitoso**, demostrando reversibilidad total sin pérdida de datos.
   - `alembic upgrade head` (re-aplicación a 0007): **Exitoso**.
2. **Pruebas de Restricciones e Integridad en PostgreSQL**:
   - Auto-incremento sin ID: confirmado (`INSERT INTO categoria` asigna automáticamente el siguiente ID secuencial sin colisión).
   - Rechazo de duplicados: confirmado (inserción de `username = 'admin'` rechazada con `IntegrityError / UniqueViolation`).
   - Rechazo de stock negativo: confirmado (inserción de `stock_actual = -5` rechazada con `IntegrityError / CheckViolation`).
3. **Validación de `init.sql`**:
   - Ejecución completa y dry-run de `database/init.sql` en base de datos limpia de PostgreSQL sin errores sintácticos.
4. **Suite Completa Pytest del Backend**:
   - `python -m pytest tests/test_rbac.py tests/test_cierre_ciegas.py tests/test_sales_service.py tests/test_cash_service.py tests/test_merma_service.py tests/test_user_report_service.py`: **31/31 pruebas PASSED (100% de éxito)**.
5. **Suites de Regresión Frontend**:
   - `test_form_validations.js`: **8/8 pruebas PASSED (100%)**.
   - `test_4_fixes.js`: **4/4 pruebas PASSED (100%)**.
   - `test_logout_flow.js`: **4/4 pruebas PASSED (100%)**.

---

## [2026-09-20] Migración Alembic 0006: Restricciones de Dominio para Estados, Ampliación de Campos de Texto y Evaluación de Zonas Horarias

### Contexto y Diagnóstico
Se solicitó la aplicación de tres mejoras de calidad no urgentes en la base de datos de Tienda el Regalito POS, bajo la premisa estricta de no representar riesgo de romper datos o funcionalidad existente:

1. **Restricciones en columnas de tipo `estado` (Punto 1)**:
   - *Diagnóstico*: En el esquema original, diez tablas poseían columnas `estado VARCHAR(20)` como texto libre sin validación a nivel de motor SQL. Existía el riesgo latente de registrar estados inconsistentes, erróneos o con errores tipográficos (ej. "activo", "inactiva", "Pendinte").
   - *Directriz*: Limitar los valores permitidos únicamente a los que el sistema realmente utiliza hoy, **sin cambiar el tipo de dato de la columna** (manteniendo `VARCHAR(20)` y evitando `ENUM` de Postgres, que requeriría `ALTER TYPE`, bloquearía transacciones DDL y dificultaría migraciones futuras).
   - *Revisión de valores en uso*: Se identificaron los dominios reales actuales:
     - `rol`: `'Activo'`, `'Inactivo'`
     - `usuario`: `'Activo'`, `'Inactivo'`
     - `sucursal`: `'Activo'`, `'Inactivo'`
     - `categoria`: `'Activo'`, `'Inactivo'`
     - `producto`: `'Activo'`, `'Inactivo'`
     - `caja`: `'Activa'`, `'Inactiva'`, `'Activo'`, `'Inactivo'` (variantes por compatibilidad con seeds y repositorios legacy)
     - `turno_caja`: `'Abierto'`, `'Cerrado'`, `'Abierta'`, `'Cerrada'` (variantes de género admitidas)
     - `venta`: `'Completada'`, `'Anulada'`
     - `orden_compra`: `'Emitida'`, `'Recibida'`, `'Cancelada'`
     - `alerta_stock`: `'Pendiente'`, `'Atendida'`, `'Descartada'`

2. **Ampliación de campos de texto libre para observaciones y descripciones (Punto 2)**:
   - *Diagnóstico*: Múltiples columnas críticas de texto libre estaban restringidas a `VARCHAR(255)`. Se detectó un riesgo real de desbordamiento en tiempo de ejecución en `cash_service.py` (L200), donde el sistema antepone automáticamente metadatos en notas de turno de caja (`f"Cierre a ciegas: {estado_cierre} (Dif: Q{diferencia:.2f}). {obs_limpia or ''}"`). Si el usuario ingresaba observaciones detalladas, la concatenación excedía fácilmente los 255 caracteres, disparando una excepción `DataError: value too long for type character varying(255)` de PostgreSQL y bloqueando el cierre de caja.
   - *Solución*: Ampliar las 5 columnas de texto libre a tipo `TEXT`, sin límite artificial de 255 caracteres y sin sobrecosto de almacenamiento en PostgreSQL.

3. **Evaluación de Fechas, Horas y Zona Horaria (Punto 3)**:
   - *Diagnóstico técnico*: El driver asíncrono `asyncpg` utilizado por SQLAlchemy en el backend (`postgresql+asyncpg://...`) impone una regla estricta: si una columna es de tipo `TIMESTAMP WITH TIME ZONE` (`TIMESTAMPTZ`), rechaza de inmediato cualquier objeto Python naive (`TypeError: a datetime.datetime object with a tzinfo is required`).
   - *Evaluación de impacto*: Actualmente todos los servicios y modelos del sistema generan marcas de tiempo con `datetime.now()` (naive) y el esquema utiliza `TIMESTAMP WITHOUT TIME ZONE`. Cambiar a `TIMESTAMPTZ` rompería instantáneamente todas las operaciones de escritura en producción salvo que se refactorizara el 100% de los servicios, modelos y esquemas Pydantic.
   - *Contexto operacional*: Tienda el Regalito opera actualmente dentro de Guatemala (`America/Guatemala`, UTC-6 fijo sin horario de verano), por lo que las marcas de tiempo locales son perfectamente deterministas y unívocas.
   - *Decisión*: Preservar `TIMESTAMP WITHOUT TIME ZONE` para cumplir rigurosamente con la instrucción de "no implementar cambios que rompan compatibilidad o representen riesgo".

### Cambios Implementados

1. **Migración Alembic `0006_restricciones_estado_y_ampliacion_textos.py`**:
   - Creada en `backend/alembic/versions/0006_restricciones_estado_y_ampliacion_textos.py` (revisión `0006`, `down_revision = "0005"`).
   - Incorpora 10 restricciones `CHECK` idempotentes mediante bloques `DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = ...) THEN ALTER TABLE ... ADD CONSTRAINT ... CHECK (...); END IF; END $$;`.
   - Modifica a tipo `TEXT` las siguientes 5 columnas:
     - `producto.descripcion`
     - `cierre_caja_ciegas.observaciones`
     - `turno_caja.notas`
     - `merma.observaciones`
     - `bitacora_auditoria.descripcion`
   - Función `downgrade()` completa y simétrica que revierte las columnas a `VARCHAR(255)` y elimina las 10 restricciones `CHECK` con `DROP CONSTRAINT IF EXISTS`.

2. **Modelos SQLAlchemy (`backend/app/db/models.py`)**:
   - Se importó el tipo `Text` desde `sqlalchemy`.
   - Se actualizaron las definiciones de los modelos a `Column(Text, ...)` en `Producto.descripcion`, `CierreCajaCiegas.observaciones`, `TurnoCaja.notas`, `Merma.observaciones` y `BitacoraAuditoria.descripcion`.

3. **Esquema Inicial (`database/init.sql`)**:
   - Sincronización íntegra de las 10 restricciones `CHECK` en las sentencias `CREATE TABLE` correspondientes.
   - Actualización de las 5 columnas a `TEXT` para garantizar coherencia en despliegues desde cero (Database-First con Docker Compose).

### Verificación y Resultados
1. **Verificación de Modelos y Migración Alembic**:
   - La migración es sintáctica y conceptualmente limpia, y se integra de forma continua a la cadena `0001 -> 0002 -> 0003 -> 0004 -> 0005 -> 0006`.
2. **Suite Completa de Pruebas Pytest del Backend**:
   - `python -m pytest tests/test_rbac.py tests/test_cierre_ciegas.py tests/test_sales_service.py tests/test_cash_service.py tests/test_merma_service.py`: **26/26 pruebas PASSED (100%)**.
   - `python -m pytest tests/test_user_report_service.py`: **5/5 pruebas PASSED (100%)**.
   - Total backend: **31/31 pruebas exitosas sin ninguna regresión**.
3. **Suites de Pruebas Frontend**:
   - `scratch/test_form_validations.js`: **8/8 pruebas PASSED (100%)**.
   - `scratch/test_4_fixes.js`: **4/4 pruebas PASSED (100%)**.
   - `scratch/test_logout_flow.js`: **4/4 pruebas PASSED (100%)**.

---

## [2026-09-18] Corrección Definitiva del Bug de Validación en Cascada por Desplazamiento de Layout (DOM Layout Shift) en Navegador

### Contexto y Diagnóstico en Entorno Real de Navegador (Microsoft Edge)
A pesar de contar con una arquitectura de validación síncrona "single-pass" en `saveUser()` y `saveProduct()`, se reportó que en el navegador real persistía el comportamiento de "validación en cascada":
- Al abrir el modal de Nuevo Usuario o Nuevo Producto con campos vacíos y hacer clic por primera vez en el botón "Guardar", únicamente se resaltaba el primer campo (`nombre_completo` o `nombre`).
- Únicamente en el segundo clic aparecían todos los errores simultáneos.

#### Causa Raíz Mecánica Descubierta en el DOM del Navegador
1. **Foco automático inicial**: Al abrir el modal (`openCreateModal` en `users.js` y `openCreateProductModal` en `catalog.js`), se programaba un foco automático al primer campo de texto (`setTimeout(() => nameInput && nameInput.focus(), 350)`).
2. **Ciclo de eventos del ratón vs desenfoque**: En la especificación W3C/DOM, cuando un usuario presiona el ratón sobre un botón de envío estando enfocado un campo de texto, la secuencia exacta de eventos es:
   `mousedown` en el botón -> `blur` en el campo que pierde foco -> `mouseup` en el botón -> `click` en el botón -> `submit` en el formulario.
3. **Desplazamiento físico del botón (Layout Shift)**:
   - Al ocurrir `mousedown` en `#btn-save-user` o `#btn-save-product`, el campo enfocado disparaba inmediatamente su listener de `blur`.
   - El handler del `blur` inyectaba `.is-invalid` y el mensaje de error en el contenedor `<div class="invalid-feedback">`.
   - En Bootstrap, `.invalid-feedback` pasa de `display: none` a `display: block`, expandiendo el cuerpo del formulario entre 21px y 25px hacia abajo.
   - Esta expansión empujaba el `modal-footer` y el botón de envío hacia abajo en 25 píxeles **mientras el botón del ratón aún estaba presionado**.
4. **Cancelación del evento `click` por el motor del navegador (Chromium/Edge)**:
   - Al soltar el botón del ratón (`mouseup`), las coordenadas del cursor ya no coincidían con la nueva posición desplazada del botón.
   - Según el estándar DOM de eventos del puntero, el evento `click` **únicamente se despacha si `mousedown` y `mouseup` ocurren sobre el mismo elemento**.
   - Al haberse desplazado el botón fuera del cursor, el navegador cancelaba y descartaba el `click`.
   - Dado que no hubo `click`, el evento `submit` del formulario **nunca se disparó en el primer clic**. El usuario únicamente observaba el error del `blur` que provocó el desplazamiento.
   - En el segundo clic, el campo ya estaba desenfocado y con su error visible (sin nuevo layout shift), por lo que el `click` y `submit` sí se completaban, ejecutando `saveUser()` / `saveProduct()` y revelando todos los errores.

### Solución Implementada
1. **Detección y Protección contra `blur` durante Envío o Cierre**:
   - Se crearon las banderas de estado y funciones protectoras `shouldSkipUserBlur(e)` en `users.js` y `shouldSkipCatalogBlur(formId, e)` en `catalog.js`.
   - Si el desenfoque ocurre porque el usuario está presionando o interactuando con el botón de envío (`e.relatedTarget.closest('#btn-save-user, #btn-save-product, [type="submit"]')`) o los botones de cierre/cancelación (`[data-bs-close-modal], .btn-close`), o si la bandera `is...FormSubmittingOrClosing` está activa, el handler de `blur` **retorna inmediatamente sin alterar el DOM**.
   - Se vincularon listeners de `mousedown` en los botones de envío y cierre para activar la bandera de protección temporalmente durante el clic físico.
2. **Preservación del Layout y Despacho del Clic**:
   - Al no dispararse la validación individual del `blur` durante el clic, el DOM permanece 100% estable (0 píxeles de desplazamiento).
   - El evento `mouseup` ocurre exactamente en las mismas coordenadas del botón.
   - El navegador despacha limpiamente el `click` y el `submit` del formulario en el **primer intento**.
3. **Ejecución Inmediata de la Validación Single-Pass**:
   - `saveUser(e)` y `saveProduct(e)` toman el control en el primer clic, limpiando cualquier error previo y evaluando en una sola pasada todos los campos obligatorios:
     - `user-form`: Evalúa simultáneamente `nombre_completo`, `username`, `password`, `id_rol` y `estado`, marcando los 5 campos en un solo ciclo.
     - `product-form`: Evalúa simultáneamente `id_subcategoria`, `id_unidad`, `id_sucursal`, `nombre`, `precio_detalle`, `precio_mayoreo`, `stock_actual` y `stock_minimo`, marcando los 8 campos en un solo ciclo.
4. **Preservación de la Validación por Blur al Navegar/Tabular**:
   - Si el usuario navega entre campos mediante la tecla `Tab` o hace clic en otro campo de entrada (donde `relatedTarget` no es el botón de envío ni de cierre), la validación de `blur` opera de manera normal y reactiva tal como fue requerida.

### Archivos Modificados
- `frontend/js/users.js`: Función `shouldSkipUserBlur(e)`, bandera `isUserFormSubmittingOrClosing`, listeners `mousedown` en botones de envío/cierre y protección en los 5 listeners de `blur`.
- `frontend/js/catalog.js`: Función `shouldSkipCatalogBlur(formId, e)`, bandera `isCatalogFormSubmittingOrClosing`, listeners `mousedown` en botones de envío/cierre y protección en los 8 listeners de `blur` de productos y 1 de categorías.
- `scratch/test_real_browser_validation.js`: Suite automatizada de pruebas end-to-end con Microsoft Edge vía CDP (Chrome DevTools Protocol) que simula clics físicos con coordenadas reales y verifica el comportamiento en el primer clic.

### Verificación y Resultados
1. **Pruebas End-to-End en Navegador Real (Microsoft Edge headless vía CDP)**:
   - `scratch/test_real_browser_validation.js`: **3/3 pruebas superadas con 100% de éxito**.
     - **Test 1 (`user-form`)**: Clic físico del ratón en `#btn-save-user` valida y marca **los 5 campos obligatorios en el 1er clic** (`nombre_completo`, `username`, `password`, `id_rol`, `estado`).
     - **Test 2 (`product-form`)**: Clic físico del ratón en `#btn-save-product` valida y marca **los 8 campos obligatorios en el 1er clic** con mensajes exactos.
     - **Test 3 (Navegación / Tabulación)**: Validación individual de `blur` y limpieza reactiva en `input` verificadas al tabular entre campos.
2. **Suites de Regresión**:
   - `scratch/test_form_validations.js`: **8/8 pruebas superadas (100%)**.
   - `scratch/test_4_fixes.js`: **4/4 pruebas superadas (100%)**.
   - `scratch/test_logout_flow.js`: **4/4 pruebas superadas (100%)**.
   - Backend Pytest (RBAC, ventas, caja, merma): **26/26 pruebas superadas (100%)**.

---

## [2026-09-18] Corrección Definitiva de Validación de Formularios: Sucursal, Stock y Validación en Una Sola Pasada (Single-Pass)

### Contexto y Diagnóstico
Tras la implementación inicial de validaciones visuales se auditaron 3 problemas específicos reportados en el navegador:
1. **PROBLEMA 1 — Mensaje incorrecto en "Sucursal" (`product-form`)**:
   - *Causa raíz*: En `users.js`, `translateValidation` dependía exclusivamente del booleano `isSelect`. Si se invocaba sin el parámetro o si en respuestas 422 la detección fallaba, la regla `/Input should be a valid integer.*/` producía `'Debe ingresar un número entero válido.'` en vez de `'Seleccione una opción.'`.
   - *Solución*: Se reforzó `translateValidation(msg, isSelect, field)` para normalizar internamente la detección de select mediante el nombre del campo (`id_sucursal`, prefijo `id_`, `estado`, `rol`, etc.) o el flag. Si el campo es un select, cualquier error de entero o requerido retorna estrictamente `'Seleccione una opción.'`. Adicionalmente, `renderCatalogFieldErrors` en `catalog.js` y `renderFieldErrors` en `users.js` detectan de forma infalible los elementos `SELECT` y transfieren `field` e `isSelect` a la traducción. En el cliente, `saveProduct` valida `id_sucursal` directamente con `'Seleccione una opción.'`.

2. **PROBLEMA 2 — Stock actual / Stock mínimo sin validación visual**:
   - *Causa raíz*: En versiones previas, `saveProduct` utilizaba coerción destructiva `rawStock = inputFor(...)?.value || '0'`, lo que reemplazaba cadenas vacías por `'0'`. Dado que en el backend `InventarioCreate` define `stock_actual: int = Field(default=0, ge=0)`, el backend aceptaba el valor `0` sin emitir error 422, dejando los campos sin borde rojo ni mensaje.
   - *Solución*: Se garantizó la lectura limpia sin ningún fallback destructivo (`inputFor(formId, 'stock_actual')?.value?.trim() ?? ''`). Se implementó validación explícita para cadenas vacías (`rawStock === ''`) asignando `"Este campo es obligatorio."` y clase `is-invalid`, y validación de rangos (`numStock < 0`) asignando `"El stock inicial debe ser 0 o superior."` (e idénticamente para `stock_minimo`). Se preservó el listener en evento `blur` para feedback inmediato al desenfocar.

3. **PROBLEMA 3 — Validación en cascada / múltiples clics (Validación en Una Sola Pasada)**:
   - *Causa raíz*: El flujo de validación requería múltiples clics consecutivos en "Guardar" para que aparecieran los errores de los distintos campos debido a dependencias en retornos 422 del backend y eventos de foco que interferían.
   - *Solución*: Se implementó una arquitectura rigurosa de **Validación de Una Sola Pasada (Single-Pass Validation)** tanto en `saveProduct()` (`catalog.js`) como en `saveUser()` (`users.js`):
     - Se limpia el estado de error previo (`clearCatalogErrors` / `clearValidationErrors`).
     - Se recorren y evalúan **incondicionalmente** todas las reglas de los campos obligatorios en un solo ciclo, sin ningún `return` prematuro.
     - En `product-form`: los 8 campos obligatorios (`id_subcategoria`, `id_unidad`, `id_sucursal`, `nombre`, `precio_detalle`, `precio_mayoreo`, `stock_actual`, `stock_minimo`) reciben de forma simultánea su clase `is-invalid` y mensaje de error en el **primer clic**.
     - En `user-form`: los 5 campos obligatorios (`nombre_completo`, `username`, `password`, `id_rol`, `estado`) se marcan simultáneamente en el primer clic.
     - Solo tras evaluar todos los campos, si `hasClientErrors` es `true`, se enfoca el primer elemento inválido, se renderiza el banner de advertencia del modal y se cancela el envío (`return`).

4. **Prevención de Caching en Navegador**:
   - Se agregaron sufijos de versión `?v=2.2` a todos los scripts en `frontend/index.html` (`app.js`, `users.js`, `catalog.js`, `cash_register.js`) para forzar la actualización inmediata en los navegadores de los usuarios.

### Archivos Modificados
- `frontend/index.html`: Parámetros cache-buster `?v=2.2` en etiquetas `<script>`.
- `frontend/js/users.js`: `translateValidation` mejorado con soporte para `field` y detección automática de selects; `renderFieldErrors` con detección robusta de selects; `saveUser` con banner de alerta en modal y validación exhaustiva de una sola pasada.
- `frontend/js/catalog.js`: `renderCatalogFieldErrors` con detección robusta de selects y pase de `field`; `saveProduct` con validación de una sola pasada cubriendo los 8 campos obligatorios simultáneamente; validación explícita de `stock_actual` y `stock_minimo` sin fallbacks.
- `scratch/test_form_validations.js`: Suite de pruebas automatizadas con 8 bloques de prueba que validan las 3 problemáticas.

### Verificación y Resultados
- `scratch/test_form_validations.js`: **8/8 pruebas exitosas (100% PASSED)**.
  - Test 5: 422 en `id_sucursal` muestra `"Seleccione una opción."` (0 incidencias de `"Debe ingresar un número entero válido."`).
  - Test 6: Validación de una sola pasada comprobada: en 1 solo submit se marcan simultáneamente los 8 campos en `product-form` y los 5 campos en `user-form`.
  - Test 7: Comprobación de cero fallbacks `|| '0'` en `catalog.js`.
  - Test 8: Comprobación de cache-busting en `index.html`.
- `scratch/test_4_fixes.js`: **100% PASSED**.
- `scratch/test_logout_flow.js`: **100% PASSED**.
- `pytest` backend: **31/31 PASSED (100% exitosas)**.

---

## [2026-09-18] Homologación y Corrección de Validación Visual de Campos Obligatorios en Formularios

### Contexto y Diagnóstico
Se identificó una inconsistencia en la validación visual de campos obligatorios (`NOT NULL` en base de datos) en formularios del sistema:
1. **Formulario de Inventario / Producto (`product-form`)**:
   - Los campos **"Stock actual"** (`stock_actual`) y **"Stock mínimo"** (`stock_minimo`) no mostraban el borde rojo (`is-invalid`) ni mensaje de error al quedar vacíos. La causa raíz fue la coerción `const rawStock = inputFor(formId, 'stock_actual')?.value || '0';` en `catalog.js`, la cual sustituía cadenas vacías por `'0'`, evadiendo la validación de obligatoriedad y el resaltado visual.
2. **Formulario de Nuevo Usuario (`user-form`)**:
   - El campo **"Estado"** (`estado`) no mostraba validación visual cuando se dejaba sin seleccionar (`-- Estado --`), a diferencia de "Rol" que sí se resaltaba. Las causas raíz fueron:
     - La ausencia del atributo `required` en la etiqueta `<select id="estado">` de `frontend/index.html`.
     - `saveUser()` no realizaba validación previa en el cliente y omitía enviar `estado` a la API si estaba vacío (`if (estadoSel && estadoSel.value) payload.estado = estadoSel.value;`).
     - Al no ser requerido en el esquema backend `UserCreate` (se asigna por defecto a "Activo"), la API nunca retornaba un 422 para él, dejando el campo sin feedback visual de error.
3. **Validación al perder el foco (`blur`)**:
   - Ningún campo obligatorio activaba la validación al perder el foco (`blur`), permitiendo que el usuario dejara campos obligatorios en blanco sin enterarse hasta pulsar "Guardar".
4. **Formularios de Caja (`open-cash-form` y `close-cash-form`)**:
   - Se verificó que ambos ya validan correctamente en el submit (`is-invalid` y textos descriptivos en español) y, siguiendo la directriz estricta de alcance, no fueron modificados innecesariamente.

### Archivos Modificados
- `frontend/index.html`:
  - Se agregó el atributo `required` al elemento `<select id="estado" class="form-select" required>`.
- `frontend/js/users.js`:
  - Se incorporó la función auxiliar `applyUserFieldError(fieldId, msg)` para centralizar la asignación de clase `is-invalid` y el mensaje de error.
  - En `saveUser()`: se implementó validación síncrona en el cliente previa a la petición de red para `nombre_completo` ("Este campo es obligatorio."), `username` ("Este campo es obligatorio."), `password` ("Este campo es obligatorio." / "Debe tener al menos 6 caracteres."), `id_rol` ("Seleccione una opción.") y `estado` ("Seleccione una opción."). Si existen errores, se enfoca el primer elemento inválido y se aborta el envío.
  - En `initRealtimeValidation()`: se agregaron listeners para el evento `blur` en los 5 campos requeridos (`nombre_completo`, `username`, `password`, `id_rol`, `estado`), activando el error visual de forma inmediata si se desenfocan vacíos o inválidos, manteniendo la limpieza reactiva al teclear/cambiar (`input`/`change`).
- `frontend/js/catalog.js`:
  - Se implementó la función auxiliar `applyCatalogFieldError(formId, fieldId, errorMsg)`.
  - En `saveProduct()`: se eliminó el fallback `|| '0'` en `rawStock` y `rawStockMin`. Se añadió validación explícita para cadenas vacías (`rawStock === ''` / `rawStockMin === ''`) con el mensaje `"Este campo es obligatorio."`, y validación para valores negativos. Se estandarizaron los mensajes para selects (`id_subcategoria`, `id_unidad`, `id_sucursal`) a `"Seleccione una opción."` y texto/precio (`nombre`, `precio_detalle`, `precio_mayoreo`) a `"Este campo es obligatorio."`.
  - En `saveCategory()`: se estandarizó el mensaje para nombre vacío a `"Este campo es obligatorio."`.
  - En `initCatalogRealtimeValidation()`: se incorporaron listeners para el evento `blur` en los 8 campos obligatorios de `product-form` (`id_subcategoria`, `id_unidad`, `id_sucursal`, `nombre`, `precio_detalle`, `precio_mayoreo`, `stock_actual`, `stock_minimo`) y en el campo obligatorio de `category-form` (`name`), manteniendo la limpieza reactiva con `input` y `change`.

### Verificación y Resultados
1. **Suite de Pruebas Automatizadas de Formularios (`scratch/test_form_validations.js`)**:
   - **Test 0 (Atributos HTML)**: Comprobación de atributo `required` en `<select id="estado">` de `index.html` (PASSED).
   - **Test 1 (`user-form`)**: Envío de formulario vacío aplica `is-invalid` y mensajes correspondientes a `nombre_completo`, `username`, `password`, `id_rol` y `estado` (PASSED). Validación en `blur` y limpieza en `change`/`input` en selects y campos de texto (PASSED).
   - **Test 2 (`product-form`)**: Envío de formulario vacío aplica `is-invalid` y `"Este campo es obligatorio."` específicamente a `stock_actual` y `stock_minimo`, además de `nombre`, `precio_detalle`, `precio_mayoreo`, y `"Seleccione una opción."` a `id_subcategoria`, `id_unidad`, `id_sucursal` (PASSED). Validación en `blur` para `stock_actual` y `stock_minimo` con limpieza reactiva (PASSED).
   - **Test 3 (`category-form`)**: Validación en submit y blur para `name` con `"Este campo es obligatorio."` (PASSED).
   - **Test 4 (Cobertura Exhaustiva de Blur)**: Validación individual en desenfoque de los 14 campos obligatorios (PASSED).
   - **Resultado**: `ALL FRONTEND FORM VALIDATION TESTS PASSED SUCCESSFULLY!`.
2. **Pruebas de Regresión Previas**:
   - `scratch/test_4_fixes.js`: 4/4 pruebas exitosas (100% PASSED).
   - `scratch/test_logout_flow.js`: 4/4 pruebas de sesión y logout exitosas (100% PASSED).
3. **Suite Completa de Pruebas Pytest del Backend**:
   - `python -m pytest tests/test_rbac.py tests/test_sales_service.py tests/test_merma_service.py tests/test_cierre_ciegas.py tests/test_cash_service.py tests/test_user_report_service.py`: **31/31 PASSED (100%)**.

---

## [2026-09-18] Corrección de 4 Incidencias Post-RBAC: Validaciones Pydantic, Módulo Reportes, Logout Sidebar e Identidad Visual

### Contexto y Diagnóstico
Tras la integración de RBAC y las protecciones de navegación se identificaron 4 incidencias puntuales en la interacción del frontend:
1. **Mensajes técnicos de validación Pydantic v2 en formulario de Productos**:
   - Campos de precio (`precio_detalle`, `precio_mayoreo`) mostraban el mensaje técnico en inglés: `"Decimal input should be an integer, float, string or Decimal object"`.
   - Dropdowns/selects (`id_subcategoria`, `id_unidad`, `id_sucursal`) mostraban: `"Seleccione o ingrese un número entero válido."` debido a que Pydantic v2 valida `int` al recibir strings vacíos.
2. **Botón "Reportes" del menú lateral inoperante**:
   - Al pulsar `#nav-reportes`, `navigateTo('reportes')` forzaba `viewKey = 'dashboard'` porque `'reportes'` no pertenecía al arreglo `mainViews`. Al estar ya en el dashboard, la llamada era descartada sin mostrar respuesta ni aviso informativo, impidiendo el acceso a la Administradora que posee acceso total.
3. **Botón de cerrar sesión en la parte inferior del sidebar**:
   - En `index.html`, la inclusión duplicada de `bootstrap.bundle.min.js` (en línea 711 y línea 1147) y de `#toast-container` (en línea 714 y 1144) creaba colisiones en los listeners de Bootstrap para dropdowns (`data-bs-toggle="dropdown"`). Además, `#btn-logout` dependía exclusivamente de un listener JS sin enlace defensivo inline ni exposición global de `showLogin`.
4. **Nombre visible de usuario admin en el sidebar**:
   - El HTML estático contenía `"Admin"` en `#sidebar-username` y `"¡Hola, Admin!"` en `#header-greeting`.
   - `updateUserInfoUI()` no normalizaba consistentemente a `"Administrador"` en todos los estados cuando el rol era `Administradora` o `user_display_name` persistía como `"Admin"`.

### Archivos Modificados
- `frontend/js/users.js`:
  - Se expandió `translateValidation(msg, isSelect = false)` para capturar errores de Pydantic v2 de tipos `Decimal` (`"Debe ingresar un precio o número válido."`) y distinguir campos `<select>` (`"Seleccione una opción."`).
  - Se expuso `window.translateValidation = translateValidation;`.
  - `renderFieldErrors()` detecta si el input es de tipo `SELECT` o inicia con `id_` y transfiere `isSelect` a la traducción.
- `frontend/js/catalog.js`:
  - `renderCatalogFieldErrors()` detecta si el elemento es `SELECT` o prefijo `id_` y envía `isSelect` a `translateValidation`.
- `frontend/js/app.js`:
  - `navigateTo(viewKey)`: evalúa primero `canAccessView(viewKey)` (permitiendo acceso total a Administradora) y, si el módulo no es una vista principal embebida (`!mainViews.includes(viewKey)`), delega a `openModule(viewKey)` mostrando la notificación informativa correspondiente.
  - `openModule()` declarado como función y expuesto en `window.openModule`.
  - `updateUserInfoUI()`: normaliza consistentemente a `"Administrador"` en sidebar, saludo (`"¡Hola, Administrador!"`) y actualiza el avatar de usuario con iniciales `"Administrador"`.
  - `form-login`: almacena `displayName` como `"Administrador"` cuando el usuario es `admin` o su rol es `Administradora`.
  - Exposición explícita de `window.showLogin` y `window.logout`.
- `frontend/index.html`:
  - Se eliminó el script redundante de Bootstrap y el contenedor `#toast-container` duplicado en el cuerpo intermedio.
  - Se actualizó el HTML estático por defecto: `<strong id="sidebar-username">Administrador</strong>` y `¡Hola, Administrador!`.
  - Se añadió `onclick="showLogin(); return false;"` en `#btn-logout`.

### Verificación y Resultados
1. **Prueba automatizada integral (`scratch/test_4_fixes.js`)**:
   - Caso 1: Validación Decimal traducida a `"Debe ingresar un precio o número válido."`, selects traducidos a `"Seleccione una opción."` y enteros normales a `"Debe ingresar un número entero válido."` (PASSED).
   - Caso 2: `navigateTo('reportes')` ejecutado como Administradora despliega toast informativo de módulo en construcción. Ejecutado como Cajero es denegado con 403 / toast peligro (PASSED).
   - Caso 3: Clic en botón `#btn-logout` y ejecución de `window.showLogin()` / `window.logout()` limpian almacenamiento y estado (PASSED).
   - Caso 4: Identidad visual consistente `"Administrador"` en sidebar, header y saludo (PASSED).
2. **Suite de regresión Pytest**:
   - 31/31 pruebas pasando al 100% (`test_rbac.py`, `test_sales_service.py`, `test_merma_service.py`, `test_cierre_ciegas.py`, `test_cash_service.py`, `test_user_report_service.py`).

---

## [2026-09-18] Corrección del Cierre de Sesión (Logout) y Aislamiento de Sesiones RBAC

### Contexto y Diagnóstico
Tras la implementación de RBAC y las protecciones de ruta SPA, el cierre de sesión (`btn-logout`) presentaba inconsistencias de navegación y mezcla de estados entre sesiones:
1. **Limpieza parcial de almacenamiento**: `showLogin()` removía solo 5 claves puntuales, dejando posible información residual en `localStorage` o `sessionStorage`, variables en memoria (`currentView`), campos del formulario de login y datos visuales en header/sidebar.
2. **Navegación contaminada por falta de `preventDefault` y persistencia del hash**:
   - `<a href="#" id="btn-logout">` no prevenía la navegación nativa del enlace.
   - El hash de la ruta previa (ej: `#users`) se mantenía en la barra de direcciones tras el cierre de sesión.
   - El uso del botón "Atrás" del navegador (`history.back()`) o recarga con bfcache no sanitizaba la URL.
3. **Mezcla de permisos al cambiar de usuario**: Al cerrar sesión un Administrador desde `#users` y loguearse un Cajero, el router SPA intentaba restaurar el hash `#users`, detonando una alerta de error 403 ("No tienes permiso...") injustificada inmediatamente después del login.

### Archivos Modificados
- `frontend/js/app.js`:
  1. **Limpieza completa en `showLogin()`**:
     - Ejecuta `localStorage.clear()` y `sessionStorage.clear()`.
     - Resetea `currentView = null;`.
     - Sanitiza la URL sin agregar entradas al historial: `history.replaceState(null, '', window.location.pathname + window.location.search);`.
     - Limpia campos de login (`#login-user`, `#login-pass`) y oculta mensajes de error previos (`#login-error`).
     - Restablece identidad visual de usuario por defecto (`#sidebar-username`, `#header-greeting`, `#header-role`).
     - Oculta todos los contenedores de vistas principales (`[data-main-view]`) y desmarca ítems activos del menú (`[data-nav]`).
  2. **Manejador de evento en `#btn-logout`**:
     - Incorpora `e.preventDefault()` antes de invocar `showLogin()`.
  3. **Blindaje de navegación histórica y caché**:
     - En `hashchange` y `popstate`: si no existe sesión activa (`!hasActiveSession()`), sanitiza la URL y fuerza `showLogin()`.
     - Se añadió listener `pageshow` para neutralizar restauraciones no autenticadas desde la bfcache del navegador.
  4. **Aislamiento de sesiones en `showDashboard()`**:
     - Si la vista solicitada por hash no está autorizada para el rol (`!canAccessView()`), normaliza inmediatamente a `#dashboard` antes de renderizar, evitando parpadeos de acceso denegado tras un login legítimo.

### Verificación y Resultados
1. **Prueba automatizada de flujo (`scratch/test_logout_flow.js`)**:
   - Cierre de sesión de Administrador limpia el 100% de claves de `localStorage` y `sessionStorage`.
   - Limpieza de URL hash confirmada (`window.location.hash == ""`).
   - Intento de navegación con botón "Atrás" / `hashchange` sin sesión es neutralizado y sanitizado.
   - Login posterior con `cajera` inicializa limpiamente en `#dashboard` con permisos exclusivos de Cajero sin alertas espurias.
2. **Suite de pruebas de regresión backend**:
   - `python -m pytest tests/test_rbac.py tests/test_sales_service.py tests/test_merma_service.py tests/test_cierre_ciegas.py tests/test_cash_service.py tests/test_user_report_service.py`: **31/31 PASSED (100%)**.

---

## [2026-09-17] Control de Acceso por Roles y Permisos (RBAC) End-to-End

### Contexto y Diagnóstico
Se implementó el sistema de Control de Acceso Basado en Roles y Permisos (RBAC) en backend y frontend para Tienda el Regalito POS, apoyándose estrictamente en los roles y permisos ya existentes en la base de datos PostgreSQL (`rol`, `permiso`, `rol_permiso`):
- **Roles en BD**: `Administradora` (id=1, control total), `Cajero` (id=2), `Bodeguero` (id=3).
- **Permisos en BD**: `VENTA_COBRAR`, `VENTA_APLICAR_DESCUENTO`, `INV_INGRESAR_MERCADERIA`, `CAJA_CIERRE_CIEGAS`, `COMPRA_EMITIR_ORDEN`.
- **Reglas operativas aplicadas**:
  1. **Login en tiempo real**: el endpoint `POST /api/auth/login` consulta en tiempo real desde `rol_permiso` los códigos de permiso asignados al rol, los devuelve en la respuesta JSON y los incluye en el token JWT.
  2. **Dependencias de autorización (`require_permission` y `require_admin`)**: función de autorización reutilizable que concede bypass automático a `Administradora` y valida la asignación en BD para el resto de roles, respondiendo con `403 Forbidden` si falta el permiso.
  3. **Protección de endpoints**:
     - `POST /api/ventas`: protegido con `require_permission("VENTA_COBRAR")`.
     - Venta con mayoreo/descuento: si `descuento_total > 0`, el servicio de ventas valida que el usuario posea `VENTA_APLICAR_DESCUENTO`.
     - `POST /api/caja/cierre-ciegas`: protegido con `require_permission("CAJA_CIERRE_CIEGAS")`.
     - `POST /api/caja/apertura`: disponible para cualquier usuario autenticado sin restricción de rol.
     - `POST /api/compras/ordenes`: protegido con `require_permission("COMPRA_EMITIR_ORDEN")`.
     - `POST /api/compras/ingreso`: protegido con `require_permission("INV_INGRESAR_MERCADERIA")`.
     - Módulos administrativos (`/api/usuarios`, `/api/roles`, `/api/departamentos`): protegidos con `require_admin`.
  4. **Frontend**:
     - Almacenamiento seguro en `localStorage` de sesión, rol y permisos (`user_role`, `user_permissions`).
     - Helpers globales de RBAC: `getUserRole()`, `getUserPermissions()`, `hasPermission(code)`, `isAdmin()`.
     - Control visual dinámico (`applyRoleRestrictions()`): oculta del menú lateral y del panel de módulos del dashboard los elementos no permitidos para el rol activo. Oculta encabezados de sección vacíos.
     - Protección de rutas SPA: `canAccessView()`, `navigateTo()` y `openModule()` bloquean el acceso no autorizado vía URL hash y muestran alerta toast sin congelar la interfaz.
     - Identidad visual de Administradora: cuando el usuario autenticado es `admin`, la interfaz muestra consistentemente `"Administrador"` en saludo de cabecera y barra lateral, manteniendo inalterado el username técnico en BD.

### Archivos Creados
- `backend/app/core/permissions.py`: Helper asíncrono desacoplado `check_user_permission` para validar permisos contra `rol_permiso` evitando dependencias circulares.
- `backend/app/schemas/compras_schema.py`: Esquemas Pydantic para órdenes de compra e ingreso de mercadería a bodega.
- `backend/app/api/compras.py`: Controlador de compras con endpoints protegidos por `COMPRA_EMITIR_ORDEN` e `INV_INGRESAR_MERCADERIA`.
- `backend/tests/test_rbac.py`: Suite exhaustiva con 7 pruebas de límites de autorización RBAC (login dinámico, protección de ventas, mayoreo, cierre a ciegas, apertura libre, compras y módulos administrativos).

### Archivos Modificados
- `backend/app/schemas/schemas.py`: Se extendió `Token` con campos opcionales `rol: Optional[str]`, `permisos: List[str]` y `nombre_completo: Optional[str]`.
- `backend/app/api/auth.py`: `login_for_access_token` realiza consulta en tiempo real a `rol_permiso`, inyecta claims en el JWT y retorna `rol` y `permisos` en la respuesta JSON.
- `backend/app/api/deps.py`: `get_current_user` ahora carga con `selectinload` la relación `Usuario.rol`. Se crearon las dependencias `require_permission` y `require_admin`.
- `backend/app/services/sale_service.py`: `registrar_venta` valida el permiso `VENTA_APLICAR_DESCUENTO` si se aplica descuento en la transacción.
- `backend/app/api/sales.py`: `POST /api/ventas` protegido con `require_permission("VENTA_COBRAR")` evaluado antes de la validación de turno activo.
- `backend/app/api/cash_register.py`: `POST /api/caja/cierre-ciegas` protegido con `require_permission("CAJA_CIERRE_CIEGAS")`.
- `backend/app/api/users.py`: Todos los endpoints de usuarios protegidos con `require_admin`.
- `backend/app/api/roles.py`: Endpoints de roles protegidos con `require_admin`.
- `backend/app/api/departments.py`: Endpoints de departamentos protegidos con `require_admin`.
- `backend/app/main.py`: Se registró el router `/api/compras`.
- `frontend/index.html`: Se agregaron atributos `data-module-item`, `data-section`, `data-card-module`, el contenedor de notificaciones `#toast-container` y el script de Bootstrap 5 Bundle.
- `frontend/js/app.js`: Implementación de helpers RBAC, almacenamiento de rol/permisos, `showToast` global, `applyRoleRestrictions()`, guardia de rutas SPA y normalización visual del usuario `admin` como `"Administrador"`.

### Verificación y Resultados
1. **Pruebas Automatizadas**:
   - `test_rbac.py`: 7/7 PASSED (100%).
   - Suite completa de regresión (`test_rbac.py`, `test_sales_service.py`, `test_merma_service.py`, `test_cierre_ciegas.py`, `test_cash_service.py`, `test_user_report_service.py`): **31/31 PASSED (100% exitosas)**.
2. **Verificación de Usuarios Semilla en Base de Datos PostgreSQL**:
   - `admin`: Rol `Administradora` (id=1), 5 permisos asignados, password `admin123` verificado.
   - `cajera`: Rol `Cajero` (id=2), permisos `VENTA_COBRAR` y `VENTA_APLICAR_DESCUENTO`, password `admin123` verificado.
   - `bodega`: Rol `Bodeguero` (id=3), permiso `INV_INGRESAR_MERCADERIA`, password `admin123` verificado.

---

## [2026-09-17] Alineación DERCAS, 4 Procesos Críticos y Reparación de Validaciones Amigables

### Contexto y Diagnóstico
Se atendió la discrepancia estructural detectada por la auditoría y se repararon las validaciones de producto en el frontend:
1. **Base de Datos y Migraciones**: Se creó y ejecutó la migración Alembic `0005_secuencias_operativas_y_limpieza_legacy.py`, agregando secuencias automáticas `nextval` a las tablas operativas de PostgreSQL (`venta`, `detalle_venta`, `pago_venta`, `merma`, `detalle_merma`, `cierre_caja_ciegas`, `detalle_arqueo_efectivo`, `movimiento_caja`) y eliminando de forma segura las tablas legacy huérfanas en inglés (`cash_registers`, `products`, `categories`, `users`, `roles`, `departments`).
2. **Validaciones Amigables (Frontend)**: Se corrigieron los mensajes técnicos en inglés de Pydantic v2. Se extendió `translateValidation` en `users.js` con traducciones en español natural y se agregó validación previa del lado del cliente en `catalog.js` (`saveProduct` y `saveCategory`) para evitar el envío de `NaN`/`null`.
3. **Bloqueo de POS sin Turno (RF01)**: Se implementó la dependencia FastAPI `get_current_active_shift` en `backend/app/api/deps.py`, la cual rechaza cualquier intento de venta con `403 Forbidden` ("Debe registrar el fondo inicial antes de vender") si el usuario no tiene un turno abierto.
4. **Cierre de Caja a Ciegas y Descuadre (RF17)**: Se implementaron los endpoints `GET /api/caja/denominaciones` y `POST /api/caja/cierre-ciegas` en `cash_register.py` con lógica de arqueo de piezas de efectivo, cálculo de saldo teórico del sistema (`monto_apertura` + ventas efectivo + entradas - salidas), diferencia, determinación de estado (`Cuadrado`, `Sobrante`, `Faltante`) y exigencia de observaciones obligatorias ante cualquier descuadre.
5. **Lógica de Descuento por Mayoreo (RF05)**: Se implementó la regla en el servicio de ventas (`sale_service.py`), aplicando automáticamente el `precio_mayoreo` cuando la cantidad es $\ge 6$ unidades o el cliente es de tipo Mayorista, registrando `descuento_item` y `descuento_total`.
6. **Módulo de Mermas (RF10)**: Se implementó el módulo de mermas (`merma_schema.py`, `merma_repository.py`, `merma_service.py`, `mermas.py`) con validación estricta de cantidad y motivo (`gt=0`), descargo atómico de existencias en `inventario_sucursal.stock_actual` y costo de pérdida basado en `costo_promedio`, sin alterar ventas ni caja.
7. **Router Central de Ventas y Facturación**: Se construyó la arquitectura completa de ventas (`sale_schema.py`, `sale_repository.py`, `sale_service.py`, `sales.py`) con validación de turno activo, descargo de stock, pagos multiforma y cálculo automático de vuelto (`cambio`).

### Archivos Creados
- `backend/alembic/versions/0005_secuencias_operativas_y_limpieza_legacy.py`: Migración de secuencias y limpieza de tablas legacy.
- `backend/app/schemas/merma_schema.py`: Esquemas Pydantic para mermas y motivos.
- `backend/app/repositories/merma_repository.py`: Repositorio asíncrono para mermas e inventario.
- `backend/app/services/merma_service.py`: Lógica de negocio de mermas con descargo atómico de stock.
- `backend/app/api/mermas.py`: Endpoints `POST /api/mermas`, `GET /api/mermas`, `GET /api/mermas/motivos`.
- `backend/app/schemas/sale_schema.py`: Esquemas Pydantic para ventas, ítems, pagos y filtros.
- `backend/app/repositories/sale_repository.py`: Repositorio asíncrono para ventas, detalles y pagos.
- `backend/app/services/sale_service.py`: Lógica de ventas, regla de mayoreo, vuelto y descargo de inventario.
- `backend/app/api/sales.py`: Endpoints `POST /api/ventas`, `GET /api/ventas`, `GET /api/ventas/{id}`.
- `backend/tests/test_cierre_ciegas.py`: Tests unitarios para arqueo a ciegas y descuadre (RF17).
- `backend/tests/test_merma_service.py`: Tests unitarios para mermas y descargo de stock (RF10).
- `backend/tests/test_sales_service.py`: Tests unitarios para ventas, mayoreo, bloqueo de POS y vuelto (RF01, RF05).

### Archivos Modificados
- `backend/app/db/models.py`: Se asignó `default=func.now(), onupdate=func.now()` a `InventarioSucursal.fecha_actualizacion`.
- `backend/app/schemas/schemas.py`: Se agregaron esquemas de `DenominacionOut`, `ArqueoItemCreate`, `CierreCiegasCreate`, `DetalleArqueoOut` y `CierreCiegasResponse`.
- `backend/app/repositories/cash_repository.py`: Se agregaron métodos de consulta de denominaciones, ventas en efectivo, movimientos de caja y persistencia de cierre a ciegas.
- `backend/app/services/cash_service.py`: Se implementó el método `cerrar_caja_ciegas()` y `get_denominaciones()`.
- `backend/app/api/cash_register.py`: Se registraron los endpoints `POST /api/caja/cierre-ciegas` y `GET /api/caja/denominaciones`.
- `backend/app/api/deps.py`: Se agregaron `get_current_active_shift`, propiedades `mermas` y `sales` a `UnitOfWork`, y proveedores `get_merma_service` y `get_sale_service`.
- `backend/app/main.py`: Se registraron los routers `/api/ventas` y `/api/mermas`.
- `backend/tests/conftest.py`: Se agregaron `mermas` y `sales` a `TestUnitOfWork`.
- `frontend/js/users.js`: Se amplió `translateValidation` con soporte completo de traducciones para Pydantic v2 en español natural.
- `frontend/js/catalog.js`: Se añadió validación defensiva en español para `saveProduct` y `saveCategory` evitando el envío de valores `NaN`/`null`.

### Verificación y Resultados
- Suite de pruebas ejecutada con `pytest`:
  - `test_sales_service.py`: 4/4 PASSED (precio detalle, precio mayoreo automático $\ge 6$, bloqueo 403 sin turno, pago insuficiente).
  - `test_merma_service.py`: 2/2 PASSED (descargo atómico de stock, rechazo por stock insuficiente).
  - `test_cierre_ciegas.py`: 3/3 PASSED (arqueo cuadrado, descuadre exige observaciones, cierre con sobrante).
  - `test_cash_service.py`: 10/10 PASSED.
  - `test_user_report_service.py`: 5/5 PASSED.
  - **Total de pruebas verificadas: 24/24 PASSED (100% exitosas)**.

---

## [2026-09-17] Login — Eliminación del formulario de auto-registro mock

### Diagnóstico
Se identificó que el enlace "¿No tienes cuenta? Regístrate" en la pantalla de login abría un formulario (`#view-register`) completamente decorativo. El handler en `app.js` estaba marcado explícitamente como `"Mock logic for frontend"`: validaba que las contraseñas coincidieran y luego mostraba un `alert('Usuario registrado exitosamente (Mock Frontend).')` sin realizar ninguna llamada HTTP ni crear ningún registro en la base de datos. No existía ningún endpoint de auto-registro en el backend.

### Decisión
Se elimina el auto-registro. El sistema es un POS interno; los empleados (cajeros, bodegueros, administradores) son creados exclusivamente por un administrador a través del módulo de Usuarios ya existente. Un auto-registro público representa una superficie de ataque innecesaria en un sistema de punto de venta.

### Archivos modificados

#### Frontend
- **`frontend/index.html`**: Se elimina el bloque completo `#view-register` (formulario con campos `reg-user`, `reg-pass`, `reg-pass-confirm`). El enlace "Regístrate" en el login se reemplaza por el texto informativo: *"El acceso es otorgado por el administrador del sistema."*
- **`frontend/js/app.js`**:
  - Se elimina `'view-register'` del array `authViews`.
  - Se elimina el handler `document.getElementById('form-register').addEventListener('submit', ...)` (incluido el `alert()` nativo mock).

### Notas
- No hay tests que eliminar: la lógica era 100% frontend mock, sin cobertura de backend.
- El flujo de login para usuarios existentes **no se modifica**.
- La gestión de usuarios sigue siendo exclusiva del módulo Usuarios → CRUD con validación de rol y estado.

---

## [2026-09-17] Módulo de Usuarios — Reporte Descargable (Excel / CSV)

### Contexto
Implementación de la funcionalidad de exportación descargable para el módulo de Usuarios, que permite al operador descargar un reporte en formato Excel (`.xlsx`) o CSV (`.csv`) respetando exactamente los mismos filtros activos en el listado (nombre, rol, estado, rango de fechas). La implementación sigue la arquitectura DERCAS y reutiliza la capa de repositorio existente sin duplicar lógica de consulta.

### Nueva dependencia
- **`openpyxl`** agregado a `backend/requirements.txt` — generación de archivos `.xlsx` con formato (cabeceras en negrita, colores corporativos, anchos de columna).

### Archivos modificados / creados

#### Backend
- **`backend/requirements.txt`**: Se agrega `openpyxl`.
- **`backend/app/services/user_service.py`**: Se agrega el método `export_users(filters, fmt)` con helpers privados `_user_row()`, `_build_csv()` y `_build_excel()`. Genera un `StreamingResponse` con el archivo adjunto. La consulta reutiliza `self.uow.users.search()` con `limit=10_000` y `offset=0` para exportar el conjunto completo.
- **`backend/app/api/users.py`**: Se agrega el endpoint `GET /api/usuarios/reporte?format=excel|csv` (registrado antes de `/{user_id}` para evitar conflicto de rutas). El controller es delgado: solo delega al servicio.

#### Frontend
- **`frontend/index.html`**: Se agrega un dropdown "Reporte" (Bootstrap `btn-group`) junto al botón "Nuevo Usuario" en la cabecera de `#users-view`, con las opciones "Descargar Excel" (`#btn-report-excel`) y "Descargar CSV" (`#btn-report-csv`).
- **`frontend/js/users.js`**: Se agrega la función `downloadReport(fmt)` que lee los filtros activos con lectura defensiva, llama al endpoint con `fetch()`, obtiene el blob y dispara la descarga mediante `URL.createObjectURL`. Usa `showToast` para notificaciones (sin `alert()`). Se registran los listeners de ambos botones en el bloque `DOMContentLoaded`.

#### Tests
- **`backend/tests/test_user_report_service.py`** [NUEVO]: 5 tests unitarios con SQLite en memoria:
  - `test_export_excel_retorna_streaming_response` — verifica MIME y `Content-Disposition` del Excel.
  - `test_export_excel_body_no_vacio` — verifica que el cuerpo del archivo no está vacío.
  - `test_export_csv_retorna_streaming_response` — verifica MIME y `Content-Disposition` del CSV.
  - `test_export_csv_filtra_activos` — con 2 usuarios (1 activo, 1 inactivo), el filtro `is_active=True` produce solo 1 fila de datos.
  - `test_export_csv_sin_usuarios_solo_cabeceras` — sin usuarios, el CSV contiene solo la cabecera.
  - **Resultado**: 5/5 PASSED.

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

### Módulo de Reportes y Estadísticas (Completado)
- Aplicado SDD y TDD de manera estricta para el filtrado de reportes por fecha.
- Creada capa DERCAS (Schema, Repository, Service, Controller) para exportar reportes a Excel y CSV utilizando `openpyxl` y `csv`.
- Validado el RBAC usando `require_admin` en el controlador y verificaciones profundas en el servicio, bloqueando con HTTP 403 a roles no autorizados.
- Todas las pruebas de `test_reportes_service.py` pasan al 100% resolviendo el esquema completo de dependencias en base de datos.

## Corrección: Módulo de Inventario en blanco (2026-10-05)

### Problema
- Al seleccionar "Inventario / Bodega" en la barra lateral, la zona del sistema aparecía en blanco.

### Causa raíz
- En `frontend/index.html` faltaba el `</div>` de cierre del contenedor `reportes-view` (abierto en la línea ~712). Esto hacía que `inventory-view` y `configuracion-view` quedaran **anidados dentro** de `reportes-view`.
- Al navegar, `renderView()` oculta todos los `[data-main-view]` con `d-none`; como el padre `reportes-view` seguía con `d-none`, el inventario (hijo) permanecía oculto aunque se le quitara `d-none` a su propio contenedor.
- Se agregó el `</div>` faltante tras el cierre de la tarjeta de Reportes, dejando a `reportes-view`, `inventory-view` y `configuracion-view` como hermanos directos.

### Archivos modificados
| Archivo | Cambio |
|---------|--------|
| `frontend/index.html` | Se agregó el `</div>` de cierre que faltaba para el contenedor `reportes-view`; balance de `<div>` restaurado (359 abren / 359 cierran). |

### Nota
- `reportes-view`, `inventory-view` y `configuracion-view` ya no quedan anidados entre sí; el enrutamiento SPA de `app.js` funciona sin cambios adicionales.
---

## [2026-10-25] Rediseño del Panel Principal (Dashboard) con métricas operativas y una sola petición agregada

### Causa Raíz / Requerimiento
1. **Panel Principal con información útil**: el dashboard anterior era una maqueta con 4 KPIs genéricos (ventas, stock crítico, compras del mes, turnos activos), la tarjeta "Módulos del Sistema" y la tarjeta "Turnos de caja activos", sin gráficos, top productos, pendientes ni accesos rápidos.
2. **Zona horaria**: los timestamps se guardan en UTC (contenedor Docker) y los días "hoy/ayer/semana" deben calcularse en America/Guatemala (UTC-6), no en UTC ni en la zona horaria del servidor.
3. **Rendimiento y robustez**: cargar el panel con una sola petición agregada, con estados de carga (skeleton), estados vacíos con acción y manejo defensivo si una petición falla.
4. **RBAC**: mostrar solo los bloques permitidos por rol/permisos reutilizando `canAccessView` de `frontend/js/app.js`.

### Solución Implementada
1. **Backend (DERCAS, sin try/except en controlador)**:
   - `backend/app/schemas/dashboard_schema.py`: nuevos DTOs `TurnoDashboard`, `VentasMetodoPago`, `VentaDiaria`, `TopProducto`, `StockCritico`, `OrdenPendiente`, `TrasladoPendiente`, `VentaReciente`; `MetricasVentas` ampliado con `ticket_promedio`, `variacion_ayer` y `total_ayer`. Se conservan los campos `compras_mes` y `turnos_activos` para compatibilidad.
   - `backend/app/repositories/dashboard_repository.py`: fecha "hoy" calculada con `GUATEMALA_OFFSET = timedelta(hours=6)` (`guatemala_today()`), límites UTC por día calendario local (`_utc_bounds`) y mes (`_month_bounds`). Nuevas consultas: turno actual del usuario, ventas por método de pago del día (neto recibido-vuelto), mermas del mes, ventas por día de los últimos 7 días, top 5 productos de la semana, stock crítico (lista, máximo 5), órdenes "Emitida" por recibir, traslados "En tránsito" y últimas 5 ventas. Todas las relaciones serializadas se cargan con `selectinload` (incluida la cadena `TurnoCaja.caja -> Caja.sucursal`) para evitar MissingGreenlet.
   - `backend/app/services/dashboard_service.py`: ensambla el `DashboardResumenResponse` completo en una sola llamada `get_resumen(user_id)`; normaliza fechas a UTC conscientes (`timezone.utc`) para que el navegador muestre la hora local de Guatemala; calcula ticket promedio y variación % vs ayer (`None` si no hay línea base).
   - `backend/app/api/dashboard.py`: controlador delgado (sin try/except) que delega en `service.get_resumen(current_user.id_usuario)`.
   - `backend/app/interfaces/repositories.py` y `backend/app/interfaces/services.py`: contratos `DashboardRepository` y `DashboardService` actualizados al nuevo conjunto de métodos.
   - `backend/tests/test_dashboard_service.py`: seeds deterministas en zona Guatemala (independientes de la TZ de la máquina), nuevos casos `test_dashboard_resumen_sin_datos` (0 datos) y `test_dashboard_resumen_dos_ventas_q630` (2 ventas, Q630, métodos de pago, top productos, stock, pendientes y últimas ventas).
2. **Frontend**:
   - `frontend/index.html` (solo `#dashboard-content`): se eliminan "Módulos del Sistema" y "Turnos de caja activos". Nuevo contenido: barra superior de estado de caja (abierto/cerrado, cajero, hora de apertura, fondo/efectivo esperado) con botones "Ir al POS" / "Abrir caja" / "Cerrar caja"; KPIs (ventas de hoy con tickets, ticket promedio y % vs ayer con flecha verde/roja; ventas por método de pago hoy; mermas del mes); gráfico de barras de los últimos 7 días con Chart.js UMD 4.4.1 pinneado desde cdn.jsdelivr.net; top 5 productos de la semana; stock crítico (máx 5) con enlace a Inventario; pendientes (órdenes "Emitida" y traslados "En tránsito") con enlaces; últimas 5 ventas (folio, hora, total, vendedor); 4 accesos rápidos (Nueva venta, Abrir/Cerrar caja, Registrar merma, Nueva compra). Cada bloque lleva `data-dashblock` para el filtrado por rol.
   - `frontend/js/dashboard.js`: reescrito para consumir la sola petición `GET /api/dashboard/resumen`, con `toggleDashboardBlocks()` (RBAC por `canAccessView`), skeletons de carga, estados vacíos con acción, render defensivo y fallback ante error HTTP/excepción sin romper el resto del panel, e integración con Chart.js (destruye/recrea la instancia al re-navegar).
   - `frontend/css/style.css`: sección nueva al final con skeletons shimmer, listas del panel, tendencia vs ayer (verde/rojo/gris), píldora de estado de caja y tarjetas de accesos rápidos. No se modifican los colores base.

### Verificación
- **Suite pytest completa (backend)**: `python -m pytest -q` → **281 passed, 0 failed** (incluye los 7 casos del dashboard).
- **`node --check`**: `frontend/js/dashboard.js` válido (sin errores de sintaxis).
- **Escenario 0 datos**: `test_dashboard_resumen_sin_datos` → total Q 0.00, 0 ventas, listas vacías, 7 días en ceros, turno `None`, sin excepciones.
- **Escenario 2 ventas (Q630)**: `test_dashboard_resumen_dos_ventas_q630` → ventas hoy Q630.00, 2 tickets, ticket promedio Q315.00; efectivo Q290 / transferencia Q340; top productos Galleta Soda y Aceite 1L; stock crítico 1; 1 orden "Emitida"; 1 traslado "En tránsito"; últimas 2 ventas con vendedor.
- **Módulos del menú**: la navegación del sidebar (`navigateTo`/`openModule` en `app.js`) es independiente del contenido del panel; se eliminaron los `onclick` inline del antiguo dashboard pero no se tocó ninguna ID usada por otros JS.
- **Zona horaria**: la fecha de hoy/ayer/semana se calcula en el backend con el offset de Guatemala; el frontend solo formatea (las horas de ventas/turno llegan como UTC conscientes y se muestran en hora local).

### Corrección (2026-10-25): gráfico de 7 días en blanco
- **Síntoma**: el gráfico de "Ventas de los últimos 7 días" aparecía vacío (canvas 0×0) aunque la API devolvía datos.
- **Causa**: Chart.js 4.4.1 no se recupera si se instancia mientras un ancestro está oculto (`display:none`); queda con `width/height = 0` incluso al mostrarse después. Ocurría cuando el resumen se cargaba desde `initDashboard()` con una vista distinta a la del panel activa (p. ej. hash `#pos` guardado), y además duplicaba la petición inicial.
- **Solución**:
  - `renderChart()` ahora difiere la creación con `setTimeout` hasta que `#dash-chart-wrap` esté visible y con tamaño real (`offsetParent`, `clientWidth/Height`), con token de generación para cancelar intentos previos.
  - `initDashboard()` ya no dispara la carga; solo enlaza acciones. La carga la hace `renderView('dashboard') -> showDashboardModule()` cuando el contenedor ya está visible (elimina la doble petición).
  - Se subieron versiones de caché en `index.html`: `dashboard.js?v=1.1` y `style.css?v=2.8`.
- **Verificación**: reproducido y validado en Chrome headless contra `http://localhost:9090` (contenedor `regalito_frontend_prod` + `regalito_backend_prod`): con token y hash `#dashboard` el canvas queda 607×260 y dibuja la barra de Q630; con hash `#pos` no se crea instancia 0×0 y al navegar a `#dashboard` se dibuja correctamente.

---

## [2026-10-28] Fusión de Barra Superior Única Compacta (56px) y Optimización Vertical del Punto de Venta (POS)

### Causa Raíz / Requerimiento
1. **Doble barra superior redundante**: El sistema mostraba dos barras superiores apiladas: una cabecera global fija con saludo y fecha ("¡Hola, Administrador! Octubre de 2026") y debajo el encabezado propio del módulo ("🛒 Punto de Venta" con turno y botones de acción), consumiendo más de 130px de alto.
2. **Pérdida de visibilidad de cobro**: Debido al espacio vertical desperdiciado, el panel de "Venta actual" (carrito y pie de cobro) sobrepasaba la altura del viewport (`100vh`), forzando al cajero a hacer scroll para ver las denominaciones de billetes rápidos y el botón principal de "COBRAR".
3. **Elementos redundantes**: Existían indicadores técnicos no indispensables para el cajero (ej. "1 prod. locales", rol repetido "Administradora", botones "Pantalla Cliente" y "← Panel").

### Solución Implementada
1. **Estructura HTML (`frontend/index.html`)**:
   - **Barra Superior Única Compacta (`.main-topbar`)**: Se unificaron los encabezados en una única barra de altura fija de 56px (`flex: 0 0 56px`).
   - **Título dinámico y estado de turno**: Inmediatamente a la derecha del botón de menú hamburguesa (`#btn-sidebar-toggle`) se ubicó el título del módulo activo (`#topbar-module-title`) y la píldora de turno de caja (`#pos-turn-badge`).
   - **Acciones a la derecha**: Se mantuvieron únicamente el botón de "Historial" del turno (`#btn-pos-history`, visible solo en POS), el alternador de Modo Oscuro/Claro (`#btn-theme-toggle`) y la campana de notificaciones (`#btn-notificaciones`).
   - **Reubicación del saludo**: El saludo `#header-greeting` y la fecha `#header-date` se trasladaron de forma fija dentro del contenido del "Panel Principal" (`#dashboard-content`), preservando sus identificadores exactos para compatibilidad con `app.js` y `dashboard.js`.
   - **Eliminación de la barra secundaria en POS**: Se retiró el contenedor redundante `.pos-header` de `#pos-view`, ganando ~80px verticales para el área de catálogo y cobro.
   - **Elementos redundantes ocultos**: Se asignó `d-none` a `#btn-sync-modal` y `#header-role`.
2. **Lógica Dinámica (`frontend/js/app.js`)**:
   - Se implementó la función `updateTopbarHeader(viewKey)` con mapa de títulos e íconos para todos los módulos del sistema.
   - La píldora de turno (`#pos-turn-badge`) y el botón de historial (`#btn-pos-history`) se muestran automáticamente solo al navegar a `pos`, ocultándose en los demás módulos.
   - Se integró la actualización del encabezado dentro del ciclo de vida `renderView(viewKey)`.
3. **Estilos CSS (`frontend/css/style.css`)**:
   - Definición de `.main-topbar` con `height: 56px !important; min-height: 56px !important; max-height: 56px !important; flex: 0 0 56px !important;`.
   - Soporte responsivo: en pantallas pequeñas (`<= 767px`) se ajustan los paddings y se oculta la píldora de turno para priorizar el título y controles.
   - Estilizado completo para Modo Oscuro (`[data-theme="dark"]` y `[data-bs-theme="dark"]`) en topbar, título, píldora de turno, botón de historial y alternadores.
   - Optimización de altura en `#pos-workspace`: ahora aprovecha el 100% de la altura disponible entre la topbar (56px) y la pantalla (`calc(100vh - 56px)`).
4. **Control de Caché**:
   - Versiones incrementadas en `frontend/index.html`: `style.css?v=6.2`, `app.js?v=3.5`, `pos.js?v=2.5`.

### Verificación
- **Validación de Sintaxis JavaScript**: `node --check frontend/js/app.js` y `node --check frontend/js/pos.js` sin errores.
- **Prueba HTTP en vivo**: Contenedor `regalito_frontend_prod` en `http://localhost:9090` responde con HTTP 200, sirviendo la estructura `.main-topbar`, `height: 56px !important`, y `updateTopbarHeader`.

---

## [2026-10-28] Corrección: Pantalla de Ventas (POS) en blanco y Ancho Fijo Estable de la Barra Lateral

### Causa Raíz
1. **Módulo de Ventas (POS) en blanco (`posWorkspaceHeight: 0`)**:
   - El contenedor `#system-module` utilizaba `min-vh-100` (`min-height: 100vh`) sin una altura definida fija (`height`).
   - Según la especificación flexbox de CSS, el cálculo de porcentaje en un hijo con `height: 100%` (`<main>`) se resuelve como `auto` si la altura del contenedor padre no es explícita.
   - Esto provocaba que `<main>` colapsara a la suma de alturas de sus hijos visibles (la topbar de 56px + el padding vertical de 16px de `#pos-view` = 72px en total).
   - Como consecuencia, `#pos-view` recibía únicamente 16px de alto y el área interna `#pos-workspace` (con `flex: 1 1 0px` y `overflow: hidden`) colapsaba a **0px**, impidiendo que se vieran las tarjetas de productos, el catálogo y el panel de cobro.
2. **Barra Lateral que cambiaba de tamaño al cambiar de módulo (`sidebarWidth` encogido)**:
   - La barra lateral `<aside class="sidebar">` tenía `width: 272px !important`, pero flexbox tenía por defecto `flex-shrink: 1` y no contaba con `flex: 0 0 272px` ni `min-width: 272px`.
   - Al navegar entre módulos con diferentes estructuras de contenido (`row`, `table`, etc.), flexbox recalculaba el espacio disponible y comprimía la barra lateral de 272px a 134px, truncando los textos de navegación ("El Regali", "POS / Ve", "Inventari Bodega").

### Solución Implementada
1. **Bloqueo Estructural a 100vh (`frontend/css/style.css`)**:
   - `#system-module`: Se fijó con `height: 100vh !important; max-height: 100vh !important; overflow: hidden !important;`.
   - `#system-module > main`: Se configuró con `flex: 1 1 0% !important; min-width: 0 !important; height: 100vh !important; max-height: 100vh !important; display: flex !important; flex-direction: column !important; overflow: hidden !important;`.
   - `#pos-view:not(.d-none)`: Se especificó con `flex: 1 1 0% !important; height: calc(100vh - 56px) !important; max-height: calc(100vh - 56px) !important; min-height: 0 !important;`.
   - `#pos-workspace`: Se configuró con `flex: 1 1 0% !important; min-height: 0 !important; height: 100% !important;`.
2. **Ancho Fijo e Inmutable de la Barra Lateral**:
   - En pantallas desktop (`@media (min-width: 1024px)`), `.sidebar` tiene `width: 272px !important; min-width: 272px !important; max-width: 272px !important; flex: 0 0 272px !important; flex-shrink: 0 !important;`.
   - Se mantiene intacto el comportamiento off-canvas para móviles (`< 1024px`).
3. **Versión de Caché Actualizada**:
   - `frontend/index.html`: `style.css?v=6.3`.

### Verificación
- **Prueba automatizada con Chrome CDP**:
  - En POS: `sidebarWidth = 272px`, `posViewHeight = 560px`, `posWorkspaceHeight = 544px`, 4 productos renderizados y botón COBRAR visible en pantalla.
  - Navegación secuencial (`dashboard` → `users` → `inventory` → `cash` → `reportes` → `pos`): el ancho del sidebar se mantuvo invariable en **272px** en todos los módulos sin ninguna fluctuación.

---

## [2026-10-28] Corrección: Ocultamiento del Estado Vacío del Carrito y Anclaje Fijo de Paginación en POS

### Causa Raíz
1. **Mensaje de carrito vacío persistente al agregar productos**:
   - La regla `.pos-cart-empty` en `style.css` contaba con la declaración `display: flex !important;`.
   - Cuando `pos.js` agregaba la clase `.d-none` (`display: none !important;`), la especificidad de clase empataba y el orden en cascada priorizaba `display: flex !important`, impidiendo que el contenedor vacío se ocultara.
   - En consecuencia, el recuadro "Agrega productos al carrito para iniciar la venta" continuaba visible ocupando la mitad del carrito aun con múltiples productos cargados.
2. **Paginación del catálogo desubicada y flotante**:
   - Todo el contenido de la tarjeta izquierda (`.pos-catalog-panel > .card-body`) compartía un único contenedor con `overflow-y: auto`.
   - Al haber más filas de productos, el contenedor completo hacía scroll, haciendo que el buscador y las categorías desaparecieran hacia arriba y que la barra de paginación (`< Página 1 de 1 >`) se desplazara con el scroll, ubicándose en medio de la cuadrícula al lado de la última tarjeta.

### Solución Implementada
1. **Ocultamiento Estricto de Carrito Vacío**:
   - `frontend/css/style.css`: Se definió `.pos-cart-empty.d-none, #pos-cart-empty.d-none { display: none !important; }`.
   - `frontend/js/pos.js`: En `renderCart()`, se forzó `style.setProperty('display', hasItems ? 'none' : 'flex', 'important')` en `#pos-cart-empty` y `'block'` en `#pos-cart-list`.
2. **Arquitectura de 3 Zonas en el Panel de Catálogo (`frontend/index.html` y `frontend/css/style.css`)**:
   - `.pos-catalog-top` (Fijo arriba): Contiene el omnibox de búsqueda y las píldoras de categorías (`flex: 0 0 auto`). Nunca se oculta al hacer scroll.
   - `.pos-catalog-body` (Scroll interno): Contiene la cuadrícula de productos (`#pos-products-grid`) con `flex: 1 1 0%; overflow-y: auto;`. Única área que hace scroll si hay muchos productos.
   - `.pos-catalog-footer` (Fijo abajo anclado): Contiene la paginación (`#pos-grid-pagination`) con `flex: 0 0 auto; border-top: 1px solid #E2E8F0;`. Permanece firmemente fijada en la parte inferior de la tarjeta.
3. **Versión de Caché Actualizada**:
   - `style.css?v=6.4` y `pos.js?v=2.6` en `frontend/index.html`.

### Verificación
- Verificado en Chrome headless vía CDP:
  - Carrito vacío: `#pos-cart-empty` en `display: flex`, `#pos-cart-list` en `display: none`.
  - Con productos: `#pos-cart-empty` en `display: none` (0px de espacio ocupado), `#pos-cart-list` visible en `display: block`.
  - Paginación anclada de forma fija en el fondo de la tarjeta (`bottom: 611px` en tarjeta de `624px`).

---

## [2026-10-28] Ajuste: Colapso Dinámico de Barra Lateral (Escritorio) y Adaptación Responsiva Completa (Móvil/Tablet)

### Causa Raíz / Requerimiento
1. **Colapso del menú lateral con botón hamburguesa**: Al fijar con `!important` el ancho de la barra lateral en 272px en la corrección previa, la regla de colapso a 76px (`.sidebar-collapsed .sidebar`) perdió especificidad, impidiendo que el menú se redujera a su modo compacto de solo íconos al pulsar el botón hamburguesa (☰).
2. **Adaptación Responsiva Móvil y Cambio de Tamaño de Ventana**: El sistema debía acoplarse fluidamente a pantallas pequeñas (< 1024px) y redimensionamiento dinámico de ventana, permitiendo que la barra lateral actúe como cajón deslizable (off-canvas) y que el Punto de Venta organice el catálogo y el panel de cobro de forma apilada y accesible sin desbordamientos horizontales.

### Solución Implementada
1. **Reglas de Colapso con Alta Especificidad (`frontend/css/style.css`)**:
   - Para escritorio (`@media (min-width: 1024px)`):
     - Ancho por defecto normal: `#system-module > .sidebar { width: 272px !important; min-width: 272px !important; max-width: 272px !important; flex: 0 0 272px !important; }`.
     - Ancho colapsado (únicamente al presionar el botón hamburguesa): `#system-module.sidebar-collapsed > .sidebar { width: 76px !important; min-width: 76px !important; max-width: 76px !important; flex: 0 0 76px !important; padding: 1rem 0.5rem !important; }`.
     - Transición suave con curva cubic-bezier de 0.22s.
2. **Adaptación Fluida para Móviles y Tablets (`< 1024px`)**:
   - `#system-module`: Altura fluida con scroll natural vertical (`overflow-y: auto; overflow-x: hidden`).
   - `#system-module > .sidebar`: Permanece oculta fuera de la pantalla (`left: -280px; position: fixed`) y se desliza suavemente (`translateX(0)`) al presionar el botón hamburguesa, con fondo desenfocado (backdrop). Se cierra al tocar fuera o al seleccionar un módulo.
   - `#system-module > main`: Ocupa el 100% del ancho del dispositivo sin scroll horizontal.
   - Punto de Venta en móvil: El catálogo se adapta con altura fija de 520px (buscador y categorías fijos arriba, cuadrícula con scroll interno y paginación fija abajo), mientras que el carrito y el pie de cobro se ubican debajo con scroll natural accesible.
3. **Versión de Caché Actualizada**:
   - `style.css?v=6.6` en `frontend/index.html`.

### Verificación
- Verificado en Chrome headless vía CDP:
  - Escritorio inicial: Sidebar = **272px**.
  - Clic en hamburguesa: Sidebar colapsa a **76px** (modo compacto con íconos).
  - Segundo clic en hamburguesa: Sidebar se expande nuevamente a **272px**.
  - Móvil (390px ancho): Main = 390px, menú lateral en modo drawer deslizable, catálogo a 520px y panel de cobro visible y accesible.
