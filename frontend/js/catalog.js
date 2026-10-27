// Módulo de Catálogos (Productos y Categorías) - Tienda el Regalito
// Construido sobre la plantilla del módulo de Usuarios (users.js):
//   - Modales defensivos (backdrop estático + dirty check al cerrar).
//   - Validación inline con Bootstrap + traducción de errores 422.
//   - Integración SPA (hash routing) + Auth Guard + Unload Guard.
//   - Cero alert()/confirm() nativos: se reutilizan showToast() y confirmModal().
// Migrado a la arquitectura relacional del DERCAS: la creación/edición envía un
// payload anidado Producto -> VarianteProducto -> InventarioSucursal en una sola
// petición (POST/PUT /api/productos). Los ids de los campos coinciden con el
// schema de Pydantic (nombre, descripcion, id_subcategoria, id_unidad, variante.*,
// inventario.*) para que la traducción 422 se inyecte inline. El acceso a campos
// se hace SIEMPRE con ámbito de formulario (inputFor/feedbackFor) para evitar
// colisiones de ids repetidos entre formularios.
const CATEGORIES_API = '/api/categorias';
const PRODUCTS_API = '/api/productos';
const CATALOGOS_API = '/api/catalogos';

let baseSaveTextProduct = 'Guardar';
let baseSaveTextCategory = 'Guardar';

const PRODUCT_IMAGE_MAX_BYTES = 5 * 1024 * 1024;
const PRODUCT_IMAGE_TYPES = new Set(['image/jpeg', 'image/png', 'image/webp', 'image/gif']);
let isProductImageUploading = false;
let productImageUploadToken = 0;

// Formatea una fecha (ISO/UTC) a DD/MM/YYYY. Definida aquí para que el módulo
// sea autocontenido (siempre se carga users.js antes, pero se evitan dependencias).
function formatDate(value) {
    if (!value) return '-';
    const d = new Date(value);
    if (isNaN(d.getTime())) return '-';
    const dd = String(d.getDate()).padStart(2, '0');
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const yyyy = d.getFullYear();
    return `${dd}/${mm}/${yyyy}`;
}

// REDISEÑO UI/UX: escapa valores interpolados en atributos HTML (por ejemplo
// la URL de la imagen) para no romper el marcado ni permitir inyección.
function escapeCatalogAttribute(value) {
    return String(value)
        .replace(/&/g, '&amp;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');
}

// REDISEÑO UI/UX: Soft Badge reutilizable para todos los estados del catálogo.
// Fondo pastel + texto oscuro + bordes redondeados (mismo lenguaje de Inventario).
function catalogStatusBadge(estado, extraClasses = '') {
    const activo = estado === 'Activo';
    const variant = activo ? 'catalog-status-badge--active' : 'catalog-status-badge--inactive';
    const label = activo ? 'Activo' : 'Inactivo';
    const classes = `catalog-status-badge ${variant}${extraClasses ? ` ${extraClasses}` : ''}`;
    return `<span class="${classes}">${label}</span>`;
}

/* ----------------------------------------------------------------------
   REDISEÑO UI/UX — ZOOM FLOTANTE DE MINIATURAS (CATÁLOGO)
   Muestra una vista previa ampliada en un contenedor fijo fuera de la
   tabla (#catalog-image-zoom). Se posiciona junto a la miniatura en
   pantalla para que el overflow horizontal de la tabla (.table-responsive)
   no la recorte en monitores compactos. No desplaza los elementos de la
   miniatura y no ocupa espacio en la fila, por lo que su altura no cambia.
   Idéntico al comportamiento, accesibilidad y diseño de Inventario.
   ---------------------------------------------------------------------- */
const CATALOG_IMAGE_ZOOM_SIZE = 200;
const CATALOG_IMAGE_ZOOM_GAP = 12;
const CATALOG_IMAGE_ZOOM_MARGIN = 8;

function getCatalogImageZoom() {
    return document.getElementById('catalog-image-zoom');
}

function positionCatalogImageZoom(trigger) {
    const zoom = getCatalogImageZoom();
    if (!zoom || !trigger) return;

    const rect = trigger.getBoundingClientRect();
    const width = zoom.offsetWidth || CATALOG_IMAGE_ZOOM_SIZE;
    const height = zoom.offsetHeight || CATALOG_IMAGE_ZOOM_SIZE;
    const maxLeft = window.innerWidth - width - CATALOG_IMAGE_ZOOM_MARGIN;

    /* Preferencia: a la derecha de la miniatura; si no cabe, a la izquierda. */
    let left = rect.right + CATALOG_IMAGE_ZOOM_GAP;
    if (left > maxLeft) {
        left = rect.left - width - CATALOG_IMAGE_ZOOM_GAP;
    }
    left = Math.max(CATALOG_IMAGE_ZOOM_MARGIN, Math.min(left, maxLeft));

    /* La miniatura queda centrada verticalmente con respecto a la vista previa. */
    const halfHeight = height / 2;
    let top = rect.top + rect.height / 2;
    top = Math.max(halfHeight + CATALOG_IMAGE_ZOOM_MARGIN, Math.min(top, window.innerHeight - halfHeight - CATALOG_IMAGE_ZOOM_MARGIN));

    zoom.style.left = `${left}px`;
    zoom.style.top = `${top}px`;
}

function showCatalogImageZoom(trigger) {
    const zoom = getCatalogImageZoom();
    const image = document.getElementById('catalog-image-zoom-img');
    const src = trigger && trigger.getAttribute('data-zoom-src');
    if (!zoom || !image || !src) return;

    if (image.getAttribute('src') !== src) {
        image.src = src;
    }
    zoom.classList.add('is-visible');
    zoom.setAttribute('aria-hidden', 'false');
    positionCatalogImageZoom(trigger);
}

function hideCatalogImageZoom() {
    const zoom = getCatalogImageZoom();
    if (!zoom) return;
    zoom.classList.remove('is-visible');
    zoom.setAttribute('aria-hidden', 'true');
}

function setupCatalogImageZoom(trigger) {
    if (!trigger) return;
    trigger.addEventListener('mouseenter', () => showCatalogImageZoom(trigger));
    trigger.addEventListener('mouseleave', hideCatalogImageZoom);
    trigger.addEventListener('focus', () => showCatalogImageZoom(trigger));
    trigger.addEventListener('blur', hideCatalogImageZoom);
}

// REDISEÑO UI/UX: miniatura 40x40 con placeholder de caja y zoom flotante ampliado (idéntico a Inventario).
function catalogProductThumb(imagenUrl) {
    const url = String(imagenUrl || '').trim();
    if (!url) {
        return '<span class="catalog-product-thumb catalog-product-thumb--placeholder" aria-hidden="true">📦</span>';
    }
    const safeUrl = escapeCatalogAttribute(url);
    return `
        <span class="catalog-product-thumb-wrap catalog-product-thumb-wrap--zoomable" data-zoom-src="${safeUrl}" tabindex="0" aria-label="Vista previa ampliada de la imagen del producto">
            <img src="${safeUrl}" alt="" class="catalog-product-thumb" loading="lazy" onerror="this.parentElement.classList.add('is-placeholder'); this.parentElement.removeAttribute('data-zoom-src'); this.parentElement.removeAttribute('tabindex'); this.parentElement.removeAttribute('aria-label'); this.remove();">
            <span class="catalog-product-thumb-fallback" aria-hidden="true">📦</span>
        </span>`;
}

// Estado de paginación y ordenamiento del listado de productos.
let productsState = {
    page: 1,
    pageSize: 10,
    total: 0,
    sortBy: 'nombre',
    sortDir: 'asc',
};

// ---------------------------------------------------------------------------
// Acceso a campos con ámbito de formulario (evita colisiones de ids repetidos)
// ---------------------------------------------------------------------------

function inputFor(formId, fieldId) {
    const form = document.getElementById(formId);
    return form ? form.querySelector(`#${fieldId}`) : null;
}

function feedbackFor(formId, fieldId) {
    const form = document.getElementById(formId);
    return form ? form.querySelector(`#error-${fieldId}`) : null;
}

// Reutiliza authHeaders()/getModal()/showToast()/confirmModal()/translateValidation()
// definidos globalmente en users.js (siempre cargado antes).

// ---------------------------------------------------------------------------
// Errores inline (ámbito de formulario) + banners
// ---------------------------------------------------------------------------

function setCatalogBanner(bannerId, message, type = 'danger') {
    const banner = document.getElementById(bannerId);
    if (!banner) return;
    banner.classList.remove('d-none', 'alert-success', 'alert-danger');
    banner.classList.add(type === 'success' ? 'alert-success' : 'alert-danger');
    banner.textContent = message;
}

function clearCatalogErrors(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    form.querySelectorAll('.form-control, .form-select').forEach((el) => {
        el.classList.remove('is-invalid');
        const fb = el.id ? feedbackFor(formId, el.id) : null;
        if (fb) fb.textContent = '';
    });
    setCatalogBanner(`${formId}-alert`, '', 'danger');
    const banner = document.getElementById(`${formId}-alert`);
    if (banner) banner.classList.add('d-none');
}

function clearCatalogFieldError(formId, el) {
    el.classList.remove('is-invalid');
    const fb = el.id ? feedbackFor(formId, el.id) : null;
    if (fb) fb.textContent = '';
}

function renderCatalogFieldErrors(formId, detail) {
    if (!Array.isArray(detail)) return;
    detail.forEach((err) => {
        const field = err.loc && err.loc.length ? err.loc[err.loc.length - 1] : null;
        const input = field ? inputFor(formId, field) : null;
        const isSelect = (input && input.tagName && input.tagName.toUpperCase() === 'SELECT') ||
            (field && (field.startsWith('id_') || field === 'estado' || field.includes('sucursal') || field.includes('subcategoria') || field.includes('unidad') || field.includes('rol')));
        const msg = typeof translateValidation === 'function'
            ? translateValidation(err.msg || 'Valor inválido', isSelect, field)
            : (isSelect ? 'Seleccione una opción.' : (err.msg || 'Valor inválido'));
        const fb = field ? feedbackFor(formId, field) : null;
        if (input && fb) {
            input.classList.add('is-invalid');
            fb.textContent = msg;
        } else {
            setCatalogBanner(`${formId}-alert`, msg);
        }
    });
}

async function handleCatalogApiError(res, formId) {
    const errData = await res.json().catch(() => null);
    const detail = errData && errData.detail;
    if (res.status === 422 && Array.isArray(detail)) {
        renderCatalogFieldErrors(formId, detail);
    } else if (typeof detail === 'string' && detail.trim()) {
        setCatalogBanner(`${formId}-alert`, detail);
    } else {
        setCatalogBanner(`${formId}-alert`, 'No se pudo completar la operación.');
    }
}

function applyCatalogFieldError(formId, fieldId, errorMsg) {
    const input = inputFor(formId, fieldId);
    const fb = feedbackFor(formId, fieldId);
    if (input) input.classList.add('is-invalid');
    if (fb) fb.textContent = errorMsg;
}

let isCatalogFormSubmittingOrClosing = false;

function shouldSkipCatalogBlur(formId, e) {
    if (isCatalogFormSubmittingOrClosing) return true;
    const rt = e && e.relatedTarget;
    if (rt && rt.closest && rt.closest('#btn-save-product, #btn-save-category, [type="submit"], [data-bs-close-modal], .btn-close')) {
        return true;
    }
    return false;
}

// Limpieza en tiempo real al teclear y validación visual al desenfocar (blur).
function initCatalogRealtimeValidation(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    form.querySelectorAll('.form-control, .form-select').forEach((el) => {
        el.addEventListener('input', () => clearCatalogFieldError(formId, el));
        el.addEventListener('change', () => clearCatalogFieldError(formId, el));
    });

    const submitBtn = (form.querySelector && form.querySelector('button[type="submit"]')) || document.getElementById('btn-save-product');
    if (submitBtn && submitBtn.addEventListener) {
        submitBtn.addEventListener('mousedown', () => {
            isCatalogFormSubmittingOrClosing = true;
            setTimeout(() => { isCatalogFormSubmittingOrClosing = false; }, 400);
        });
    }

    const modal = (form.closest && form.closest('.modal')) || document.getElementById(formId.replace('-form', '-modal'));
    if (modal && modal.querySelectorAll) {
        modal.querySelectorAll('[data-bs-close-modal], .btn-close').forEach(btn => {
            if (btn && btn.addEventListener) {
                btn.addEventListener('mousedown', () => {
                    isCatalogFormSubmittingOrClosing = true;
                    setTimeout(() => { isCatalogFormSubmittingOrClosing = false; }, 400);
                });
            }
        });
    }

    if (formId === 'product-form') {
        const subcatInput = inputFor(formId, 'id_subcategoria');
        if (subcatInput) {
            subcatInput.addEventListener('blur', (e) => {
                if (shouldSkipCatalogBlur(formId, e)) return;
                if (!subcatInput.value) {
                    applyCatalogFieldError(formId, 'id_subcategoria', 'Seleccione una opción.');
                }
            });
        }

        const unidadInput = inputFor(formId, 'id_unidad');
        if (unidadInput) {
            unidadInput.addEventListener('blur', (e) => {
                if (shouldSkipCatalogBlur(formId, e)) return;
                if (!unidadInput.value) {
                    applyCatalogFieldError(formId, 'id_unidad', 'Seleccione una opción.');
                }
            });
        }

        const sucursalInput = inputFor(formId, 'id_sucursal');
        if (sucursalInput) {
            sucursalInput.addEventListener('blur', (e) => {
                if (shouldSkipCatalogBlur(formId, e)) return;
                if (!sucursalInput.value) {
                    applyCatalogFieldError(formId, 'id_sucursal', 'Seleccione una opción.');
                }
            });
        }

        const nombreInput = inputFor(formId, 'nombre');
        if (nombreInput) {
            nombreInput.addEventListener('blur', (e) => {
                if (shouldSkipCatalogBlur(formId, e)) return;
                if (!nombreInput.value.trim()) {
                    applyCatalogFieldError(formId, 'nombre', 'Este campo es obligatorio.');
                }
            });
        }

        const precioDetalleInput = inputFor(formId, 'precio_detalle');
        if (precioDetalleInput) {
            precioDetalleInput.addEventListener('blur', (e) => {
                if (shouldSkipCatalogBlur(formId, e)) return;
                const val = precioDetalleInput.value.trim();
                if (!val) {
                    applyCatalogFieldError(formId, 'precio_detalle', 'Este campo es obligatorio.');
                } else {
                    const num = parseFloat(val);
                    if (isNaN(num) || num <= 0) {
                        applyCatalogFieldError(formId, 'precio_detalle', 'Ingrese un precio de venta mayor a 0 (ej. 15.00).');
                    }
                }
            });
        }

        const precioMayoreoInput = inputFor(formId, 'precio_mayoreo');
        if (precioMayoreoInput) {
            precioMayoreoInput.addEventListener('blur', (e) => {
                if (shouldSkipCatalogBlur(formId, e)) return;
                const val = precioMayoreoInput.value.trim();
                if (!val) {
                    applyCatalogFieldError(formId, 'precio_mayoreo', 'Este campo es obligatorio.');
                } else {
                    const num = parseFloat(val);
                    if (isNaN(num) || num <= 0) {
                        applyCatalogFieldError(formId, 'precio_mayoreo', 'Ingrese un precio mayorista mayor a 0 (ej. 12.00).');
                    }
                }
            });
        }

        const stockActualInput = inputFor(formId, 'stock_actual');
        if (stockActualInput) {
            stockActualInput.addEventListener('blur', (e) => {
                if (shouldSkipCatalogBlur(formId, e)) return;
                const val = stockActualInput.value.trim();
                if (val === '') {
                    applyCatalogFieldError(formId, 'stock_actual', 'Este campo es obligatorio.');
                } else {
                    const num = parseInt(val, 10);
                    if (isNaN(num) || num < 0) {
                        applyCatalogFieldError(formId, 'stock_actual', 'El stock inicial debe ser 0 o superior.');
                    }
                }
            });
        }

        const stockMinimoInput = inputFor(formId, 'stock_minimo');
        if (stockMinimoInput) {
            stockMinimoInput.addEventListener('blur', (e) => {
                if (shouldSkipCatalogBlur(formId, e)) return;
                const val = stockMinimoInput.value.trim();
                if (val === '') {
                    applyCatalogFieldError(formId, 'stock_minimo', 'Este campo es obligatorio.');
                } else {
                    const num = parseInt(val, 10);
                    if (isNaN(num) || num < 0) {
                        applyCatalogFieldError(formId, 'stock_minimo', 'El stock mínimo debe ser 0 o superior.');
                    }
                }
            });
        }
    } else if (formId === 'category-form') {
        const nameInput = inputFor(formId, 'name');
        if (nameInput) {
            nameInput.addEventListener('blur', (e) => {
                if (shouldSkipCatalogBlur(formId, e)) return;
                if (!nameInput.value.trim()) {
                    applyCatalogFieldError(formId, 'name', 'Este campo es obligatorio.');
                }
            });
        }
    }
}

// ---------------------------------------------------------------------------
// Protección de datos (dirty check + cierre seguro) por formulario
// ---------------------------------------------------------------------------

function catalogFormHasData(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    let hasData = false;
    form.querySelectorAll('input[type="text"], input[type="number"], textarea, select').forEach((el) => {
        if (el.value && el.value.trim().length > 0) hasData = true;
    });
    return hasData;
}

async function safeCloseCatalogModal(formId, modalId) {
    const modal = getModal(modalId);
    if (!modal) return;
    if (catalogFormHasData(formId)) {
        const ok = await confirmModal('¿Tienes datos sin guardar. ¿Deseas descartar los cambios y salir?');
        if (!ok) return;
    }
    clearCatalogErrors(formId);
    const form = document.getElementById(formId);
    if (form) form.reset();
    form.querySelectorAll('.is-invalid').forEach((el) => el.classList.remove('is-invalid'));
    form.querySelectorAll('.invalid-feedback').forEach((el) => { el.textContent = ''; });
    modal.hide();
}

// Unload Guard: protege contra recargas/cierres de pestaña con un modal sucio abierto.
window.addEventListener('beforeunload', (event) => {
    const dirty = ['product-form', 'category-form'].some((formId) => {
        const modalId = formId === 'product-form' ? 'product-modal' : 'category-modal';
        const modalEl = document.getElementById(modalId);
        return modalEl && modalEl.classList.contains('show') && catalogFormHasData(formId);
    });
    if (dirty) {
        event.preventDefault();
        event.returnValue = '';
    }
});

// ---------------------------------------------------------------------------
// Carga de catálogos de apoyo (dropdowns) desde la BD (cero datos quemados)
// ---------------------------------------------------------------------------

async function populateFromApi(selectId, url, valueKey, textFn, placeholder, selectedId = null) {
    const select = document.getElementById(selectId);
    if (!select) return;
    select.innerHTML = '<option value="">Cargando...</option>';
    try {
        const res = await fetch(url, { headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'No se pudieron cargar los datos', 'danger');
            select.innerHTML = placeholder ? `<option value="">${placeholder}</option>` : '<option value=""></option>';
            return;
        }
        const items = await res.json();
        select.innerHTML = placeholder ? `<option value="">${placeholder}</option>` : '<option value=""></option>';
        items.forEach((it) => {
            const opt = document.createElement('option');
            opt.value = it[valueKey];
            opt.textContent = textFn(it);
            if (selectedId && String(it[valueKey]) === String(selectedId)) opt.selected = true;
            select.appendChild(opt);
        });
    } catch (err) {
        select.innerHTML = '<option value=""></option>';
        console.error(err);
    }
}

async function populateSubcategorias(selectId, selectedId = null, placeholder) {
    await populateFromApi(
        selectId,
        `${CATALOGOS_API}/subcategorias`,
        'id_subcategoria',
        (s) => (s.categoria ? `${s.categoria.nombre} — ${s.nombre}` : s.nombre),
        placeholder,
        selectedId
    );
}

async function populateUnidades(selectId, selectedId = null, placeholder) {
    await populateFromApi(
        selectId,
        `${CATALOGOS_API}/unidades`,
        'id_unidad',
        (u) => `${u.descripcion} (${u.codigo})`,
        placeholder,
        selectedId
    );
}

async function populateSucursales(selectId, selectedId = null, placeholder) {
    await populateFromApi(
        selectId,
        `${CATALOGOS_API}/sucursales`,
        'id_sucursal',
        (s) => s.nombre,
        placeholder,
        selectedId
    );
}

async function populateAreas(selectId, sucursalId, selectedId = null) {
    const select = document.getElementById(selectId);
    if (!select) return;
    select.innerHTML = '<option value="">Sin área</option>';
    if (!sucursalId) return;
    await populateFromApi(
        selectId,
        `${CATALOGOS_API}/areas?sucursal_id=${sucursalId}`,
        'id_area',
        (a) => a.nombre_area,
        'Sin área',
        selectedId
    );
}

// ---------------------------------------------------------------------------
// Listado de Categorías
// ---------------------------------------------------------------------------

async function loadCategoriesTable() {
    const tbody = document.getElementById('categories-table-body');
    const empty = document.getElementById('categories-empty');
    const nameFilter = (document.getElementById('filter-category-name')?.value || '').trim();
    try {
        const params = new URLSearchParams();
        params.append('include_inactive', 'true');
        const res = await fetch(`${CATEGORIES_API}?${params.toString()}`, { headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'No se pudieron cargar las categorías', 'danger');
            return;
        }
        const items = await res.json();
        const filtered = nameFilter
            ? items.filter((c) => (c.nombre || '').toLowerCase().includes(nameFilter.toLowerCase()))
            : items;
        if (filtered.length) {
            // REDISEÑO UI/UX: estado como Soft Badge y papelera en la acción destructiva.
            tbody.innerHTML = filtered.map((c) => `
                <tr>
                    <td>${c.nombre}</td>
                    <td>-</td>
                    <td>${catalogStatusBadge(c.estado)}</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-rosado" onclick="editCategory(${c.id_categoria})" title="Editar"><i class="bi bi-pencil"></i></button>
                        ${c.estado === 'Activo' ? `<button class="btn btn-sm btn-outline-danger" onclick="deactivateCategory(${c.id_categoria})" title="Desactivar"><i class="bi bi-trash"></i></button>` : ''}
                    </td>
                </tr>
            `).join('');
            tbody.closest('.table-responsive').classList.remove('d-none');
            if (empty) empty.classList.add('d-none');
        } else {
            tbody.innerHTML = '';
            tbody.closest('.table-responsive').classList.add('d-none');
            if (empty) empty.classList.remove('d-none');
        }
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ---------------------------------------------------------------------------
// Listado de Productos
// ---------------------------------------------------------------------------

async function loadProducts() {
    const tbody = document.getElementById('products-table-body');
    const empty = document.getElementById('products-empty');
    if (!tbody) return;

    const params = new URLSearchParams();
    const name = (document.getElementById('filter-product-name')?.value || '').trim();
    const barcode = (document.getElementById('filter-product-barcode')?.value || '').trim();
    const subcat = document.getElementById('filter-product-subcategoria')?.value || '';

    if (name) params.append('name', name);
    if (barcode) params.append('barcode', barcode);
    if (subcat) params.append('subcategoria_id', subcat);
    // REDISEÑO UI/UX: se eliminaron los filtros de fecha "Desde/Hasta" del
    // catálogo, por lo que ya no se envían created_from ni created_to.

    const pageSize = parseInt(document.getElementById('products-page-size')?.value || String(productsState.pageSize || 10), 10) || 10;
    productsState.pageSize = pageSize;
    const page = productsState.page || 1;

    params.append('sort_by', productsState.sortBy || 'nombre');
    params.append('sort_dir', productsState.sortDir || 'asc');
    params.append('limit', pageSize);
    params.append('offset', (page - 1) * pageSize);
    try {
        const res = await fetch(`${PRODUCTS_API}?${params.toString()}`, { headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'No se pudieron cargar los productos', 'danger');
            return;
        }
        const data = await res.json();
        const items = data.items || [];
        hideCatalogImageZoom();
        if (items.length) {
            tbody.innerHTML = items.map((p) => {
                const variante = p.variantes && p.variantes[0] ? p.variantes[0] : null;
                const inventario = variante && variante.inventarios && variante.inventarios[0]
                    ? variante.inventarios[0] : null;
                const sub = p.subcategoria
                    ? (p.subcategoria.categoria ? `${p.subcategoria.categoria.nombre} / ${p.subcategoria.nombre}` : p.subcategoria.nombre)
                    : '-';
                const precio = variante ? Number(variante.precio_detalle).toFixed(2) : '0.00';
                const stock = inventario ? Number(inventario.stock_actual) : 0;
                const minStock = inventario ? Number(inventario.stock_minimo) : 0;
                const activo = p.estado === 'Activo';
                const fecha = p.fecha_creacion ? formatDate(p.fecha_creacion) : '-';
                // REDISEÑO UI/UX: miniatura 40x40, soft badges, papelera en la
                // acción destructiva y nombre con tooltip accesible.
                const thumb = catalogProductThumb(p.imagen_url);
                const stockBadge = stock <= minStock
                    ? `<span class="catalog-stock-badge catalog-stock-badge--danger">${stock}</span>`
                    : `<span class="catalog-stock-badge catalog-stock-badge--ok">${stock}</span>`;
                const nombreSeguro = escapeCatalogAttribute(p.nombre || '');
                return `
                <tr>
                    <td>${p.id_producto}</td>
                    <td>
                        <div class="catalog-product-cell d-flex align-items-center gap-2">
                            ${thumb}
                            <span class="catalog-product-name" title="${nombreSeguro}">${p.nombre}</span>
                        </div>
                    </td>
                    <td>${sub}</td>
                    <td>Q ${precio}</td>
                    <td>${stockBadge}</td>
                    <td>${catalogStatusBadge(p.estado)}</td>
                    <td>${fecha}</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-info" onclick="viewProductDetail(${p.id_producto})" title="Ver detalle"><i class="bi bi-eye"></i></button>
                        <button class="btn btn-sm btn-outline-rosado" onclick="editProduct(${p.id_producto})" title="Editar"><i class="bi bi-pencil"></i></button>
                        ${activo ? `<button class="btn btn-sm btn-outline-danger" onclick="deactivateProduct(${p.id_producto})" title="Desactivar"><i class="bi bi-trash"></i></button>` : ''}
                    </td>
                </tr>
            `;
            }).join('');
            tbody.querySelectorAll('.catalog-product-thumb-wrap[data-zoom-src]').forEach((wrap) => {
                setupCatalogImageZoom(wrap);
            });
            tbody.closest('.table-responsive').classList.remove('d-none');
            if (empty) empty.classList.add('d-none');
        } else {
            tbody.innerHTML = '';
            tbody.closest('.table-responsive').classList.add('d-none');
            if (empty) empty.classList.remove('d-none');
        }
        productsState.total = data.total || 0;
        renderProductPagination();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// Renderiza la barra de paginación de productos a partir del estado actual.
function renderProductPagination() {
    const pagination = document.getElementById('products-pagination');
    if (!pagination) return;
    const totalPages = Math.max(1, Math.ceil(productsState.total / productsState.pageSize));
    if (productsState.page > totalPages) productsState.page = totalPages;
    const info = document.getElementById('products-page-info');
    const prev = document.getElementById('products-prev-page');
    const next = document.getElementById('products-next-page');
    if (info) info.textContent = `Página ${productsState.page} de ${totalPages}`;
    if (prev) prev.disabled = productsState.page <= 1;
    if (next) next.disabled = productsState.page >= totalPages;
    pagination.classList.toggle('d-none', productsState.total === 0);
}

// Va a una página concreta y recarga el listado de productos.
function goToProductPage(page) {
    const totalPages = Math.max(1, Math.ceil(productsState.total / productsState.pageSize));
    if (page < 1) page = 1;
    if (page > totalPages) page = totalPages;
    if (page === productsState.page) return;
    productsState.page = page;
    loadProducts();
}

// Alterna el orden (asc/desc) de una columna y recarga.
function toggleProductSort(column) {
    if (productsState.sortBy === column) {
        productsState.sortDir = productsState.sortDir === 'asc' ? 'desc' : 'asc';
    } else {
        productsState.sortBy = column;
        productsState.sortDir = 'asc';
    }
    productsState.page = 1;
    updateProductSortIndicators();
    loadProducts();
}

// Pinta los indicadores asc/desc en las cabeceras ordenables de productos.
function updateProductSortIndicators() {
    document.querySelectorAll('#tab-products th.sortable').forEach((th) => {
        const col = th.getAttribute('data-sort');
        const existing = th.querySelector('.sort-icon');
        if (existing) th.removeChild(existing);
        if (col === productsState.sortBy) {
            const icon = document.createElement('span');
            icon.className = 'sort-icon';
            icon.textContent = productsState.sortDir === 'asc' ? '▲' : '▼';
            th.appendChild(icon);
        }
    });
}

// Modal informativo de detalle de producto (solo lectura).
async function viewProductDetail(productId) {
    try {
        const res = await fetch(`${PRODUCTS_API}/${productId}`, { headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'No se encontró el producto', 'danger');
            return;
        }
        const p = await res.json();
        const variante = p.variantes && p.variantes[0] ? p.variantes[0] : null;
        const inventario = variante && variante.inventarios && variante.inventarios[0]
            ? variante.inventarios[0] : null;
        const sub = p.subcategoria
            ? (p.subcategoria.categoria ? `${p.subcategoria.categoria.nombre} / ${p.subcategoria.nombre}` : p.subcategoria.nombre)
            : '-';
        document.getElementById('pdetail-id').textContent = p.id_producto;
        document.getElementById('pdetail-nombre').textContent = p.nombre || '-';
        document.getElementById('pdetail-descripcion').textContent = p.descripcion || '-';
        document.getElementById('pdetail-subcategoria').textContent = sub;
        document.getElementById('pdetail-unidad').textContent = (p.unidad && p.unidad.descripcion) ? p.unidad.descripcion : '-';
        document.getElementById('pdetail-estado').textContent = p.estado || '-';
        document.getElementById('pdetail-fecha').textContent = p.fecha_creacion
            ? new Date(p.fecha_creacion).toLocaleString()
            : '-';
        document.getElementById('pdetail-barcode').textContent = variante ? (variante.codigo_barras || '-') : '-';
        // REDISEÑO UI/UX: el atributo universal combina Talla y Color en una sola línea.
        const atributoUnificado = [variante?.talla, variante?.color].filter(Boolean).join(' · ');
        document.getElementById('pdetail-atributo').textContent = atributoUnificado || '-';
        document.getElementById('pdetail-precio-detalle').textContent = variante ? `Q ${Number(variante.precio_detalle).toFixed(2)}` : '-';
        document.getElementById('pdetail-precio-mayoreo').textContent = variante ? `Q ${Number(variante.precio_mayoreo).toFixed(2)}` : '-';
        document.getElementById('pdetail-costo').textContent = variante ? `Q ${Number(variante.costo_promedio).toFixed(2)}` : '-';
        document.getElementById('pdetail-sucursal').textContent = inventario ? inventario.id_sucursal : '-';
        document.getElementById('pdetail-stock').textContent = inventario ? inventario.stock_actual : '-';
        document.getElementById('pdetail-stock-min').textContent = inventario ? inventario.stock_minimo : '-';
        const modal = getModal('product-detail-modal');
        if (modal) modal.show();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ---------------------------------------------------------------------------
// Imagen opcional de producto
// ---------------------------------------------------------------------------

function setProductImagePreview(url) {
    const img = document.getElementById('imagen_preview_img');
    const placeholder = document.getElementById('imagen_preview_placeholder');
    const removeBtn = document.getElementById('btn-remove-imagen');
    if (!img || !placeholder) return;

    const value = (url || '').trim();
    if (value) {
        img.src = value;
        img.classList.remove('d-none');
        placeholder.classList.add('d-none');
        if (removeBtn) removeBtn.classList.remove('d-none');
    } else {
        img.removeAttribute('src');
        img.classList.add('d-none');
        placeholder.classList.remove('d-none');
        if (removeBtn) removeBtn.classList.add('d-none');
    }
}

function setProductImageUploading(uploading) {
    isProductImageUploading = uploading;
    // REDISEÑO UI/UX: la dropzone reemplaza al botón "Subir imagen" y muestra
    // un overlay de progreso mientras se carga el archivo.
    const dropzone = document.getElementById('product-image-dropzone');
    const uploadingState = document.getElementById('product-image-uploading');
    const removeBtn = document.getElementById('btn-remove-imagen');
    const fileInput = document.getElementById('imagen_file');
    if (dropzone) {
        dropzone.classList.toggle('is-uploading', uploading);
        dropzone.setAttribute('aria-busy', uploading ? 'true' : 'false');
    }
    if (uploadingState) uploadingState.classList.toggle('d-none', !uploading);
    if (removeBtn) removeBtn.disabled = uploading;
    if (fileInput) fileInput.disabled = uploading;
}

async function uploadProductImage(file) {
    if (!file) return;
    const fileInput = document.getElementById('imagen_file');
    if (!PRODUCT_IMAGE_TYPES.has(file.type)) {
        if (fileInput) fileInput.value = '';
        showToast('Formato no permitido. Usa JPG, PNG, WEBP o GIF.', 'warning');
        return;
    }
    if (file.size > PRODUCT_IMAGE_MAX_BYTES) {
        if (fileInput) fileInput.value = '';
        showToast('La imagen supera el límite de 5 MB.', 'warning');
        return;
    }

    const token = ++productImageUploadToken;
    setProductImageUploading(true);

    try {
        const formData = new FormData();
        formData.append('file', file);
        const res = await fetch(`${PRODUCTS_API}/upload-imagen`, {
            method: 'POST',
            headers: { Authorization: `Bearer ${localStorage.getItem('jwt_token')}` },
            body: formData,
        });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            throw new Error((errData && errData.detail) || 'No se pudo subir la imagen');
        }
        const data = await res.json();
        if (token !== productImageUploadToken) return;

        const input = inputFor('product-form', 'imagen_url');
        if (input) input.value = data.imagen_url || '';
        setProductImagePreview(data.imagen_url);
        showToast('Imagen subida correctamente.', 'success');
    } catch (err) {
        if (token === productImageUploadToken) {
            showToast(err.message, 'danger');
        }
    } finally {
        if (fileInput) fileInput.value = '';
        if (token === productImageUploadToken) setProductImageUploading(false);
    }
}

// ---------------------------------------------------------------------------
// Atributo universal (combobox de captura rápida)
// Campo optimizado para inventarios mixtos: un único input de texto libre que
// sugiere valores ingresados previamente (persistidos en localStorage). Nunca
// bloquea la entrada: se puede escribir cualquier valor nuevo sin elegir de la
// lista. Sustituye a los campos rígidos de Talla y Color.
// ---------------------------------------------------------------------------

const ATRIBUTO_SUGERENCIAS_KEY = 'regalito_atributos_sugeridos';
const ATRIBUTO_SUGERENCIAS_MAX = 20;
let atributoActiveIndex = -1;
let atributoSeededFromBackend = false;

// Rellena el pool de sugerencias con los atributos (Talla/Color) ya existentes
// en el catálogo, para que el combobox muestre opciones útiles desde el primer
// uso. Se ejecuta una sola vez por sesión y falla en silencio.
async function seedAtributoSugerenciasFromBackend() {
    if (atributoSeededFromBackend) return;
    atributoSeededFromBackend = true;
    try {
        const res = await fetch(`${PRODUCTS_API}?limit=500&sort_by=nombre&sort_dir=asc`, { headers: authHeaders() });
        if (!res.ok) return;
        const data = await res.json();
        (data.items || []).forEach((p) => {
            (p.variantes || []).forEach((v) => {
                [v.talla, v.color].forEach((val) => registerAtributoSugerido(val));
            });
        });
        const input = document.getElementById('atributo_variante');
        if (input && input.matches(':focus')) showAtributoSugerencias(input.value);
    } catch {
        // Sin conexión o sin sesión: el combobox sigue útil como input libre.
    }
}

function getAtributoSugerencias() {
    try {
        const raw = JSON.parse(localStorage.getItem(ATRIBUTO_SUGERENCIAS_KEY) || '[]');
        return Array.isArray(raw) ? raw.filter((v) => typeof v === 'string' && v.trim()) : [];
    } catch {
        return [];
    }
}

function registerAtributoSugerido(value) {
    const v = String(value || '').trim();
    if (!v) return;
    const list = getAtributoSugerencias().filter((s) => s.toLowerCase() !== v.toLowerCase());
    list.unshift(v);
    try {
        localStorage.setItem(ATRIBUTO_SUGERENCIAS_KEY, JSON.stringify(list.slice(0, ATRIBUTO_SUGERENCIAS_MAX)));
    } catch {
        // Almacenamiento no disponible (modo privado/incógnito): el campo
        // sigue funcionando como input libre, simplemente sin memoria.
    }
}

function buildAtributoSugerencias(filterText) {
    const term = String(filterText || '').trim().toLowerCase();
    return getAtributoSugerencias()
        .filter((s) => !term || s.toLowerCase().includes(term))
        .slice(0, 8);
}

function hideAtributoSugerencias() {
    const list = document.getElementById('atributo_variante_sugerencias');
    const input = document.getElementById('atributo_variante');
    if (list) list.classList.add('d-none');
    if (input) input.setAttribute('aria-expanded', 'false');
    atributoActiveIndex = -1;
}

function showAtributoSugerencias(filterText) {
    const list = document.getElementById('atributo_variante_sugerencias');
    const input = document.getElementById('atributo_variante');
    if (!list || !input) return;
    const options = buildAtributoSugerencias(filterText);
    if (!options.length) {
        list.innerHTML = '<div class="product-attribute-suggestions-empty">Sin sugerencias, escriba el valor libremente.</div>';
    } else {
        list.innerHTML = options.map((option) =>
            `<div class="product-attribute-option" role="option">${escapeCatalogAttribute(option)}</div>`
        ).join('');
    }
    list.classList.remove('d-none');
    input.setAttribute('aria-expanded', 'true');
    atributoActiveIndex = -1;
}

function selectAtributoOption(optionEl) {
    const input = document.getElementById('atributo_variante');
    if (!input) return;
    input.value = optionEl.textContent;
    input.dispatchEvent(new Event('input', { bubbles: true }));
    hideAtributoSugerencias();
}

function initAtributoCombobox() {
    const input = document.getElementById('atributo_variante');
    const list = document.getElementById('atributo_variante_sugerencias');
    if (!input || !list) return;

    input.addEventListener('focus', () => {
        showAtributoSugerencias(input.value);
        seedAtributoSugerenciasFromBackend();
    });
    input.addEventListener('input', () => showAtributoSugerencias(input.value));
    input.addEventListener('click', () => {
        showAtributoSugerencias(input.value);
        seedAtributoSugerenciasFromBackend();
    });

    input.addEventListener('keydown', (event) => {
        const options = Array.from(list.querySelectorAll('.product-attribute-option'));
        if (event.key === 'Escape') {
            hideAtributoSugerencias();
            return;
        }
        if (!options.length) return;
        if (event.key === 'ArrowDown') {
            event.preventDefault();
            atributoActiveIndex = (atributoActiveIndex + 1) % options.length;
        } else if (event.key === 'ArrowUp') {
            event.preventDefault();
            atributoActiveIndex = (atributoActiveIndex - 1 + options.length) % options.length;
        } else if (event.key === 'Enter' && atributoActiveIndex >= 0) {
            event.preventDefault();
            selectAtributoOption(options[atributoActiveIndex]);
            return;
        } else {
            return;
        }
        options.forEach((option, index) => {
            option.classList.toggle('is-active', index === atributoActiveIndex);
        });
        if (options[atributoActiveIndex]) {
            options[atributoActiveIndex].scrollIntoView({ block: 'nearest' });
        }
    });

    // mousedown (y no click) para seleccionar antes de que el input pierda el foco.
    list.addEventListener('mousedown', (event) => {
        const option = event.target.closest('.product-attribute-option');
        if (option) {
            event.preventDefault();
            selectAtributoOption(option);
        }
    });

    document.addEventListener('click', (event) => {
        if (event.target.closest && !event.target.closest('.product-attribute-combobox')) {
            hideAtributoSugerencias();
        }
    });
}

// ---------------------------------------------------------------------------
// Formulario / Modal de Producto
// ---------------------------------------------------------------------------

async function resetProductForm() {
    productImageUploadToken += 1;
    isProductImageUploading = false;
    hideAtributoSugerencias();
    clearCatalogErrors('product-form');
    const form = document.getElementById('product-form');
    if (form) form.reset();
    inputFor('product-form', 'product-id').value = '';
    inputFor('product-form', 'variante-id').value = '';
    inputFor('product-form', 'inventario-id').value = '';
    const fileInput = document.getElementById('imagen_file');
    if (fileInput) fileInput.value = '';
    setProductImageUploading(false);
    setProductImagePreview('');
    // REDISEÑO UI/UX: el campo de URL vuelve a estar plegado al reabrir el modal.
    const urlWrapper = document.getElementById('imagen-url-wrapper');
    const urlToggle = document.getElementById('toggle-imagen-url');
    if (urlWrapper) urlWrapper.classList.add('d-none');
    if (urlToggle) {
        urlToggle.textContent = 'o ingresar desde URL';
        urlToggle.setAttribute('aria-expanded', 'false');
    }
    const dropzone = document.getElementById('product-image-dropzone');
    if (dropzone) dropzone.classList.remove('is-dragover');
    document.getElementById('product-modal-title').textContent = 'Nuevo Producto';
    baseSaveTextProduct = 'Guardar';
    const text = document.getElementById('btn-save-product-text');
    if (text) text.textContent = baseSaveTextProduct;
    await Promise.all([
        populateSubcategorias('id_subcategoria', null, '-- Seleccione subcategoría --'),
        populateUnidades('id_unidad', null, '-- Seleccione unidad --'),
        populateSucursales('id_sucursal', null, '-- Seleccione sucursal --'),
    ]);
    populateAreas('id_area', null);
}

function openCreateProductModal() {
    resetProductForm().then(() => {
        const modal = getModal('product-modal');
        if (modal) modal.show();
        const nameInput = inputFor('product-form', 'nombre');
        setTimeout(() => nameInput && nameInput.focus(), 350);
    });
}

async function editProduct(productId) {
    clearCatalogErrors('product-form');
    try {
        const res = await fetch(`${PRODUCTS_API}/${productId}`, { headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'No se encontró el producto', 'danger');
            return;
        }
        const p = await res.json();
        const variante = p.variantes && p.variantes[0] ? p.variantes[0] : null;
        const inventario = variante && variante.inventarios && variante.inventarios[0]
            ? variante.inventarios[0] : null;

        inputFor('product-form', 'product-id').value = p.id_producto;
        inputFor('product-form', 'variante-id').value = variante ? variante.id_variante : '';
        inputFor('product-form', 'inventario-id').value = inventario ? inventario.id_inventario : '';
        inputFor('product-form', 'nombre').value = p.nombre;
        inputFor('product-form', 'descripcion').value = p.descripcion || '';
        inputFor('product-form', 'imagen_url').value = p.imagen_url || '';
        productImageUploadToken += 1;
        setProductImageUploading(false);
        const imagenFileInput = document.getElementById('imagen_file');
        if (imagenFileInput) imagenFileInput.value = '';
        setProductImagePreview(p.imagen_url || '');
        inputFor('product-form', 'codigo_barras').value = variante ? (variante.codigo_barras || '') : '';
        // REDISEÑO UI/UX: al editar se precarga el atributo universal combinando
        // Talla + Color (campo de captura rápida para inventarios mixtos).
        const atributoUnificado = [variante?.talla, variante?.color].filter(Boolean).join(' · ');
        inputFor('product-form', 'atributo_variante').value = atributoUnificado;
        inputFor('product-form', 'precio_detalle').value = variante ? variante.precio_detalle : '';
        inputFor('product-form', 'precio_mayoreo').value = variante ? variante.precio_mayoreo : '';
        inputFor('product-form', 'costo_promedio').value = variante ? variante.costo_promedio : '';
        inputFor('product-form', 'stock_actual').value = inventario ? inventario.stock_actual : '';
        inputFor('product-form', 'stock_minimo').value = inventario ? inventario.stock_minimo : '';
        inputFor('product-form', 'product_is_active').checked = p.estado === 'Activo';

        document.getElementById('product-modal-title').textContent = 'Editar Producto';
        baseSaveTextProduct = 'Actualizar';
        const text = document.getElementById('btn-save-product-text');
        if (text) text.textContent = baseSaveTextProduct;

        const sucursalId = inventario ? inventario.id_sucursal : null;
        await Promise.all([
            populateSubcategorias('id_subcategoria', p.id_subcategoria, '-- Seleccione subcategoría --'),
            populateUnidades('id_unidad', p.id_unidad, '-- Seleccione unidad --'),
            populateSucursales('id_sucursal', sucursalId, '-- Seleccione sucursal --'),
        ]);
        await populateAreas('id_area', sucursalId, inventario ? inventario.id_area : null);

        const modal = getModal('product-modal');
        if (modal) modal.show();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

function setProductSaving(saving) {
    const btn = document.getElementById('btn-save-product');
    if (!btn) return;
    btn.disabled = saving;
    const spinner = document.getElementById('btn-save-product-spinner');
    const text = document.getElementById('btn-save-product-text');
    if (spinner) spinner.classList.toggle('d-none', !saving);
    if (text) text.textContent = saving ? 'Guardando...' : baseSaveTextProduct;
}

async function saveProduct(event) {
    event.preventDefault();
    isCatalogFormSubmittingOrClosing = false;
    clearCatalogErrors('product-form');
    if (isProductImageUploading) {
        showToast('Espera a que termine la subida de la imagen.', 'warning');
        return;
    }

    const formId = 'product-form';
    let hasClientErrors = false;

    function applyFieldError(fieldId, errorMsg) {
        const input = inputFor(formId, fieldId);
        const fb = feedbackFor(formId, fieldId);
        if (input) input.classList.add('is-invalid');
        if (fb) fb.textContent = errorMsg;
        hasClientErrors = true;
    }

    const id = inputFor(formId, 'product-id')?.value || '';
    const rawSubcat = inputFor(formId, 'id_subcategoria')?.value || '';
    const rawUnidad = inputFor(formId, 'id_unidad')?.value || '';
    const rawSucursal = inputFor(formId, 'id_sucursal')?.value || '';
    const rawNombre = inputFor(formId, 'nombre')?.value?.trim() || '';
    const rawPrecioDetalle = inputFor(formId, 'precio_detalle')?.value || '';
    const rawPrecioMayoreo = inputFor(formId, 'precio_mayoreo')?.value || '';
    const rawCosto = inputFor(formId, 'costo_promedio')?.value || '0';
    const rawStock = inputFor(formId, 'stock_actual')?.value?.trim() ?? '';
    const rawStockMin = inputFor(formId, 'stock_minimo')?.value?.trim() ?? '';

    // =========================================================================
    // VALIDACIÓN DE UNA SOLA PASADA (Single-pass validation)
    // Se evalúan TODOS los campos obligatorios simultáneamente en el primer clic.
    // =========================================================================

    // 1. Subcategoría (Select obligatorio)
    if (!rawSubcat) {
        applyFieldError('id_subcategoria', 'Seleccione una opción.');
    }

    // 2. Unidad de medida (Select obligatorio)
    if (!rawUnidad) {
        applyFieldError('id_unidad', 'Seleccione una opción.');
    }

    // 3. Sucursal (Select obligatorio - PROBLEMA 1)
    if (!rawSucursal) {
        applyFieldError('id_sucursal', 'Seleccione una opción.');
    }

    // 4. Nombre (Texto obligatorio)
    if (!rawNombre) {
        applyFieldError('nombre', 'Este campo es obligatorio.');
    }

    // 5. Precio Detalle (Numérico > 0 obligatorio)
    const numPrecioDetalle = parseFloat(rawPrecioDetalle);
    if (!rawPrecioDetalle) {
        applyFieldError('precio_detalle', 'Este campo es obligatorio.');
    } else if (isNaN(numPrecioDetalle) || numPrecioDetalle <= 0) {
        applyFieldError('precio_detalle', 'Ingrese un precio de venta mayor a 0 (ej. 15.00).');
    }

    // 6. Precio Mayoreo (Numérico > 0 obligatorio)
    const numPrecioMayoreo = parseFloat(rawPrecioMayoreo);
    if (!rawPrecioMayoreo) {
        applyFieldError('precio_mayoreo', 'Este campo es obligatorio.');
    } else if (isNaN(numPrecioMayoreo) || numPrecioMayoreo <= 0) {
        applyFieldError('precio_mayoreo', 'Ingrese un precio mayorista mayor a 0 (ej. 12.00).');
    }

    // 7. Costo Promedio (Numérico >= 0)
    const numCosto = parseFloat(rawCosto || '0');
    if (isNaN(numCosto) || numCosto < 0) {
        applyFieldError('costo_promedio', 'El costo promedio no puede ser un número negativo.');
    }

    // 8. Stock Actual (PROBLEMA 2 - Cero fallback destructivo, obligatorio)
    let numStock = 0;
    if (rawStock === '' || rawStock === null || rawStock === undefined) {
        applyFieldError('stock_actual', 'Este campo es obligatorio.');
    } else {
        numStock = parseInt(rawStock, 10);
        if (isNaN(numStock) || numStock < 0) {
            applyFieldError('stock_actual', 'El stock inicial debe ser 0 o superior.');
        }
    }

    // 9. Stock Mínimo (PROBLEMA 2 - Cero fallback destructivo, obligatorio)
    let numStockMin = 0;
    if (rawStockMin === '' || rawStockMin === null || rawStockMin === undefined) {
        applyFieldError('stock_minimo', 'Este campo es obligatorio.');
    } else {
        numStockMin = parseInt(rawStockMin, 10);
        if (isNaN(numStockMin) || numStockMin < 0) {
            applyFieldError('stock_minimo', 'El stock mínimo debe ser 0 o superior.');
        }
    }

    // Si cualquier campo falló, enfocar el primer elemento inválido y detener envío
    if (hasClientErrors) {
        const firstInvalid = document.querySelector(`#${formId} .is-invalid`);
        if (firstInvalid) firstInvalid.focus();
        setCatalogBanner(`${formId}-alert`, 'Por favor complete todos los campos obligatorios correctamente.');
        return;
    }

    setProductSaving(true);

    const payload = {
        id_subcategoria: parseInt(rawSubcat, 10),
        id_unidad: parseInt(rawUnidad, 10),
        nombre: rawNombre,
        descripcion: inputFor(formId, 'descripcion')?.value?.trim() || null,
        imagen_url: inputFor(formId, 'imagen_url')?.value?.trim() || '',
        variante: {
            codigo_barras: inputFor(formId, 'codigo_barras')?.value?.trim() || null,
            // REDISEÑO UI/UX: el atributo universal reemplaza a Talla/Color.
            // Se guarda en "color" (String(30)) para admitir valores largos.
            talla: null,
            color: inputFor(formId, 'atributo_variante')?.value?.trim() || null,
            precio_detalle: numPrecioDetalle,
            precio_mayoreo: numPrecioMayoreo,
            costo_promedio: numCosto,
        },
        inventario: {
            id_sucursal: parseInt(rawSucursal, 10),
            id_area: parseInt(inputFor(formId, 'id_area')?.value, 10) || null,
            stock_actual: numStock,
            stock_minimo: numStockMin,
        },
    };
    if (id) payload.estado = inputFor(formId, 'product_is_active')?.checked ? 'Activo' : 'Inactivo';

    const url = id ? `${PRODUCTS_API}/${id}` : PRODUCTS_API;
    const method = id ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, { method, headers: authHeaders(), body: JSON.stringify(payload) });
        if (!res.ok) {
            await handleCatalogApiError(res, formId);
            return;
        }
        const modal = getModal('product-modal');
        if (modal) modal.hide();
        // REDISEÑO UI/UX: cada valor nuevo se suma a las sugerencias del combobox
        // de atributo universal para agilizar la captura en inventarios mixtos.
        registerAtributoSugerido(inputFor(formId, 'atributo_variante')?.value?.trim() || '');
        showToast(id ? 'Producto actualizado correctamente.' : 'Producto creado correctamente.', 'success');
        await loadProducts();
    } catch (err) {
        showToast(err.message, 'danger');
    } finally {
        setProductSaving(false);
    }
}

async function deactivateProduct(productId) {
    const ok = await confirmModal('¿Desactivar este producto?');
    if (!ok) return;
    try {
        const res = await fetch(`${PRODUCTS_API}/${productId}`, { method: 'DELETE', headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'Error al desactivar el producto', 'danger');
            return;
        }
        showToast('Producto desactivado correctamente.', 'success');
        await loadProducts();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ---------------------------------------------------------------------------
// Formulario / Modal de Categoría
// ---------------------------------------------------------------------------

async function resetCategoryForm() {
    clearCatalogErrors('category-form');
    const form = document.getElementById('category-form');
    if (form) form.reset();
    inputFor('category-form', 'category-id').value = '';
    document.getElementById('category-modal-title').textContent = 'Nueva Categoría';
    baseSaveTextCategory = 'Guardar';
    const text = document.getElementById('btn-save-category-text');
    if (text) text.textContent = baseSaveTextCategory;
}

function openCreateCategoryModal() {
    resetCategoryForm().then(() => {
        const modal = getModal('category-modal');
        if (modal) modal.show();
        const nameInput = inputFor('category-form', 'name');
        setTimeout(() => nameInput && nameInput.focus(), 350);
    });
}

async function editCategory(categoryId) {
    clearCatalogErrors('category-form');
    try {
        const res = await fetch(`${CATEGORIES_API}/${categoryId}`, { headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'No se encontró la categoría', 'danger');
            return;
        }
        const c = await res.json();
        inputFor('category-form', 'category-id').value = c.id_categoria;
        inputFor('category-form', 'name').value = c.nombre;
        inputFor('category-form', 'description').value = '';
        inputFor('category-form', 'category_is_active').checked = c.estado === 'Activo';
        document.getElementById('category-modal-title').textContent = 'Editar Categoría';
        baseSaveTextCategory = 'Actualizar';
        const text = document.getElementById('btn-save-category-text');
        if (text) text.textContent = baseSaveTextCategory;
        const modal = getModal('category-modal');
        if (modal) modal.show();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

function setCategorySaving(saving) {
    const btn = document.getElementById('btn-save-category');
    if (!btn) return;
    btn.disabled = saving;
    const spinner = document.getElementById('btn-save-category-spinner');
    const text = document.getElementById('btn-save-category-text');
    if (spinner) spinner.classList.toggle('d-none', !saving);
    if (text) text.textContent = saving ? 'Guardando...' : baseSaveTextCategory;
}

async function saveCategory(event) {
    event.preventDefault();
    isCatalogFormSubmittingOrClosing = false;
    clearCatalogErrors('category-form');

    const nameVal = inputFor('category-form', 'name')?.value?.trim() || '';
    if (!nameVal) {
        const input = inputFor('category-form', 'name');
        const fb = feedbackFor('category-form', 'name');
        if (input) {
            input.classList.add('is-invalid');
            input.focus();
        }
        if (fb) fb.textContent = 'Este campo es obligatorio.';
        setCatalogBanner('category-form-alert', 'Por favor ingrese el nombre de la categoría.');
        return;
    }

    setCategorySaving(true);

    const id = inputFor('category-form', 'category-id').value;
    const payload = {
        nombre: nameVal,
    };
    if (id) payload.estado = inputFor('category-form', 'category_is_active').checked ? 'Activo' : 'Inactivo';

    const url = id ? `${CATEGORIES_API}/${id}` : CATEGORIES_API;
    const method = id ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, { method, headers: authHeaders(), body: JSON.stringify(payload) });
        if (!res.ok) {
            await handleCatalogApiError(res, 'category-form');
            return;
        }
        const modal = getModal('category-modal');
        if (modal) modal.hide();
        showToast(id ? 'Categoría actualizada correctamente.' : 'Categoría creada correctamente.', 'success');
        await Promise.all([loadCategoriesTable(), populateSubcategorias('filter-product-subcategoria', null, 'Todas las subcategorías')]);
    } catch (err) {
        showToast(err.message, 'danger');
    } finally {
        setCategorySaving(false);
    }
}

async function deactivateCategory(categoryId) {
    const ok = await confirmModal('¿Desactivar esta categoría?');
    if (!ok) return;
    try {
        const res = await fetch(`${CATEGORIES_API}/${categoryId}`, { method: 'DELETE', headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'Error al desactivar la categoría', 'danger');
            return;
        }
        showToast('Categoría desactivada correctamente.', 'success');
        await Promise.all([loadCategoriesTable(), populateSubcategorias('filter-product-subcategoria', null, 'Todas las subcategorías')]);
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ---------------------------------------------------------------------------
// Integración SPA (llamado desde renderView en app.js)
// ---------------------------------------------------------------------------

window.showCatalogModule = async function () {
    updateProductSortIndicators();
    await Promise.all([
        loadProducts(),
        loadCategoriesTable(),
        populateSubcategorias('filter-product-subcategoria', null, 'Todas las subcategorías'),
        loadSubcategoriasTable(),
        loadUnidadesTable(),
        loadSucursalesTable(),
        loadAreasTable(),
        populateSubcatCategoriesDropdown(),
        populateAreaSucursalesDropdown(),
    ]);
    initBloque3Tables();
};

window.editProduct = editProduct;
window.editCategory = editCategory;
window.viewProductDetail = viewProductDetail;

document.addEventListener('DOMContentLoaded', () => {
    const productForm = document.getElementById('product-form');
    if (productForm) {
        productForm.addEventListener('submit', saveProduct);
        initCatalogRealtimeValidation('product-form');
    }
    initAtributoCombobox();

    const dropzone = document.getElementById('product-image-dropzone');
    const imageFileInput = document.getElementById('imagen_file');
    const removeImageBtn = document.getElementById('btn-remove-imagen');
    const imageUrlInput = document.getElementById('imagen_url');
    const urlToggle = document.getElementById('toggle-imagen-url');
    const urlWrapper = document.getElementById('imagen-url-wrapper');
    const previewImg = document.getElementById('imagen_preview_img');
    const previewPlaceholder = document.getElementById('imagen_preview_placeholder');

    if (imageFileInput) {
        imageFileInput.addEventListener('change', () => {
            const file = imageFileInput.files && imageFileInput.files[0];
            if (file) uploadProductImage(file);
        });
    }
    // REDISEÑO UI/UX: dropzone con clic, teclado y arrastrar y soltar.
    // Reutiliza la misma función de carga y validación existente.
    if (dropzone && imageFileInput) {
        const openFilePicker = () => {
            if (!isProductImageUploading) imageFileInput.click();
        };
        dropzone.addEventListener('click', (event) => {
            if (event.target === imageFileInput) return;
            openFilePicker();
        });
        dropzone.addEventListener('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                openFilePicker();
            }
        });
        ['dragenter', 'dragover'].forEach((eventName) => {
            dropzone.addEventListener(eventName, (event) => {
                event.preventDefault();
                if (isProductImageUploading) return;
                dropzone.classList.add('is-dragover');
            });
        });
        ['dragleave', 'dragend'].forEach((eventName) => {
            dropzone.addEventListener(eventName, () => dropzone.classList.remove('is-dragover'));
        });
        dropzone.addEventListener('drop', (event) => {
            event.preventDefault();
            dropzone.classList.remove('is-dragover');
            if (isProductImageUploading) return;
            const file = event.dataTransfer && event.dataTransfer.files && event.dataTransfer.files[0];
            if (file) uploadProductImage(file);
        });
    }
    if (removeImageBtn && imageUrlInput) {
        removeImageBtn.addEventListener('click', () => {
            imageUrlInput.value = '';
            if (imageFileInput) imageFileInput.value = '';
            setProductImagePreview('');
            clearCatalogFieldError('product-form', imageUrlInput);
        });
    }
    if (imageUrlInput) {
        imageUrlInput.addEventListener('input', () => {
            setProductImagePreview(imageUrlInput.value);
        });
    }
    // REDISEÑO UI/UX: el campo para pegar una URL queda plegado tras un enlace.
    if (urlToggle && urlWrapper) {
        urlToggle.addEventListener('click', () => {
            const expanded = urlToggle.getAttribute('aria-expanded') === 'true';
            const nextExpanded = !expanded;
            urlWrapper.classList.toggle('d-none', !nextExpanded);
            urlToggle.setAttribute('aria-expanded', String(nextExpanded));
            urlToggle.textContent = nextExpanded ? 'Ocultar campo de URL' : 'o ingresar desde URL';
            if (nextExpanded && imageUrlInput) imageUrlInput.focus();
        });
    }
    if (previewImg && previewPlaceholder) {
        previewImg.addEventListener('error', () => {
            previewImg.classList.add('d-none');
            previewPlaceholder.classList.remove('d-none');
        });
    }
    const categoryForm = document.getElementById('category-form');
    if (categoryForm) {
        categoryForm.addEventListener('submit', saveCategory);
        initCatalogRealtimeValidation('category-form');
    }

    const productModal = document.getElementById('product-modal');
    if (productModal) productModal.addEventListener('hidden.bs.modal', resetProductForm);
    const categoryModal = document.getElementById('category-modal');
    if (categoryModal) categoryModal.addEventListener('hidden.bs.modal', resetCategoryForm);

    document.querySelectorAll('#product-modal [data-bs-close-modal]').forEach((btn) => {
        btn.addEventListener('click', () => safeCloseCatalogModal('product-form', 'product-modal'));
    });
    document.querySelectorAll('#category-modal [data-bs-close-modal]').forEach((btn) => {
        btn.addEventListener('click', () => safeCloseCatalogModal('category-form', 'category-modal'));
    });

    // El área de bodega depende de la sucursal seleccionada.
    const sucursalSelect = document.getElementById('id_sucursal');
    if (sucursalSelect) {
        sucursalSelect.addEventListener('change', () => {
            clearCatalogFieldError('product-form', sucursalSelect);
            populateAreas('id_area', sucursalSelect.value);
        });
    }

    const btnNewProduct = document.getElementById('btn-new-product');
    if (btnNewProduct) btnNewProduct.addEventListener('click', openCreateProductModal);
    const btnNewCategory = document.getElementById('btn-new-category');
    if (btnNewCategory) btnNewCategory.addEventListener('click', openCreateCategoryModal);
    const btnFilterProducts = document.getElementById('btn-filter-products');
    if (btnFilterProducts) btnFilterProducts.addEventListener('click', () => {
        productsState.page = 1;
        loadProducts();
    });
    const btnFilterCategories = document.getElementById('btn-filter-categories');
    if (btnFilterCategories) btnFilterCategories.addEventListener('click', loadCategoriesTable);

    // REDISEÑO UI/UX: pestañas principales + menú "Configuraciones Adicionales".
    // Sincroniza las clases activas y muestra únicamente el panel seleccionado.
    const catalogView = document.getElementById('catalog-view');
    const catalogMainTabs = document.getElementById('catalog-main-tabs');
    const extraMenu = document.getElementById('catalog-extra-menu');
    const extraToggle = document.getElementById('catalog-extra-toggle');

    const syncCatalogTabChrome = (targetSelector) => {
        hideCatalogImageZoom();
        if (!catalogView || !targetSelector) return;

        catalogView.querySelectorAll('.tab-content .tab-pane').forEach((pane) => {
            const isTarget = pane.id && `#${pane.id}` === targetSelector;
            pane.classList.toggle('show', isTarget);
            pane.classList.toggle('active', isTarget);
        });

        catalogMainTabs?.querySelectorAll('.nav-link').forEach((link) => {
            const isActive = link.getAttribute('data-bs-target') === targetSelector;
            link.classList.toggle('active', isActive);
            link.setAttribute('aria-selected', String(isActive));
        });

        let extraActive = false;
        extraMenu?.querySelectorAll('[data-catalog-target]').forEach((item) => {
            const isActive = item.getAttribute('data-catalog-target') === targetSelector;
            item.classList.toggle('active', isActive);
            if (isActive) extraActive = true;
        });
        extraToggle?.classList.toggle('active', extraActive);
    };

    // Los tabs principales siguen usando Bootstrap; solo sincronizamos el chrome.
    document.addEventListener('show.bs.tab', (event) => {
        if (!event.target.closest('#catalog-view')) return;
        syncCatalogTabChrome(event.target.getAttribute('data-bs-target'));
    });

    // Los enlaces del dropdown se controlan manualmente para no romper el menú.
    extraMenu?.querySelectorAll('[data-catalog-target]').forEach((item) => {
        item.addEventListener('click', (event) => {
            event.preventDefault();
            const targetSelector = item.getAttribute('data-catalog-target');
            if (!targetSelector) return;
            syncCatalogTabChrome(targetSelector);
            if (extraToggle && window.bootstrap?.Dropdown) {
                bootstrap.Dropdown.getOrCreateInstance(extraToggle).hide();
            }
        });
    });

    // REDISEÑO UI/UX: botón "X" para limpiar los buscadores de productos.
    catalogView?.querySelectorAll('.catalog-search-field').forEach((field) => {
        const input = field.querySelector('.catalog-search-input');
        const clearBtn = field.querySelector('.catalog-clear-btn');
        if (!input || !clearBtn) return;

        const syncClearVisibility = () => field.classList.toggle('has-value', input.value.trim().length > 0);
        input.addEventListener('input', syncClearVisibility);
        clearBtn.addEventListener('click', () => {
            input.value = '';
            syncClearVisibility();
            input.focus();
            productsState.page = 1;
            loadProducts();
        });
        syncClearVisibility();
    });

    // Paginación de productos
    const pageSize = document.getElementById('products-page-size');
    if (pageSize) pageSize.addEventListener('change', () => {
        productsState.pageSize = parseInt(pageSize.value, 10);
        productsState.page = 1;
        loadProducts();
    });
    const prevBtn = document.getElementById('products-prev-page');
    if (prevBtn) prevBtn.addEventListener('click', () => goToProductPage(productsState.page - 1));
    const nextBtn = document.getElementById('products-next-page');
    if (nextBtn) nextBtn.addEventListener('click', () => goToProductPage(productsState.page + 1));
    // Ordenamiento de columnas de productos
    document.querySelectorAll('#tab-products th.sortable').forEach((th) => {
        th.addEventListener('click', () => toggleProductSort(th.getAttribute('data-sort')));
    });

    /* Ocultar el zoom si la imagen ampliada falla, al desplazarse o al
       redimensionar. Así nunca queda una vista previa flotante huérfana (idéntico a Inventario). */
    const catalogZoomImage = document.getElementById('catalog-image-zoom-img');
    if (catalogZoomImage) {
        catalogZoomImage.addEventListener('error', hideCatalogImageZoom);
    }
    window.addEventListener('scroll', hideCatalogImageZoom, true);
    window.addEventListener('resize', hideCatalogImageZoom);
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') hideCatalogImageZoom();
    });
});

window.hideCatalogImageZoom = hideCatalogImageZoom;

// ===========================================================================
// BLOQUE 2: SUBCATEGORÍAS, UNIDADES, SUCURSALES, ÁREAS DE BODEGA
// ===========================================================================

function getCatalogAuthHeaders() {
    const token = localStorage.getItem('jwt_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

async function readCatalogError(res, fallback) {
    // Extrae el detalle (mensaje claro del backend, p.ej. desactivación segura 400).
    try {
        const errData = await res.json();
        if (errData && typeof errData.detail === 'string' && errData.detail.trim()) return errData.detail;
    } catch (_) { /* cuerpo no JSON */ }
    return fallback;
}

async function downloadCatalogExport(url, defaultFilename) {
    try {
        const token = localStorage.getItem('jwt_token');
        const res = await fetch(url, { headers: { 'Authorization': `Bearer ${token}` } });
        if (!res.ok) throw new Error('Error al descargar el archivo de reporte');
        const blob = await res.blob();
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        link.download = defaultFilename;
        document.body.appendChild(link);
        link.click();
        link.remove();
        showToast('Reporte generado y descargado correctamente.', 'success');
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ---------------------------------------------------------------------------
// 1. SUBCATEGORÍAS CRUD
// ---------------------------------------------------------------------------

let subcatState = {
    page: 1,
    limit: 10,
    total: 0,
    sortBy: 'nombre',
    sortOrder: 'asc',
    search: '',
    id_categoria: '',
    status: '',
    currentEditId: null,
};

async function populateSubcatCategoriesDropdown() {
    const filterSelect = document.getElementById('filter-subcat-cat');
    const formSelect = document.getElementById('subcat-cat-id');
    try {
        const res = await fetch(`${CATEGORIES_API}?limit=500`, { headers: getCatalogAuthHeaders() });
        if (res.ok) {
            const data = await res.json();
            const cats = Array.isArray(data) ? data : (data.items || []);
            if (filterSelect) {
                const current = filterSelect.value;
                filterSelect.innerHTML = '<option value="">Todas las categorías</option>' +
                    cats.map(c => `<option value="${c.id_categoria}">${c.nombre}</option>`).join('');
                filterSelect.value = current;
            }
            if (formSelect) {
                formSelect.innerHTML = '<option value="">Seleccione categoría...</option>' +
                    cats.map(c => `<option value="${c.id_categoria}">${c.nombre}</option>`).join('');
            }
        }
    } catch (e) {
        console.warn('Error al cargar categorías en combos de subcategoría:', e);
    }
}

async function loadSubcategoriasTable() {
    const tbody = document.getElementById('subcategorias-table-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-3 text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Cargando subcategorías...</td></tr>';

    const offset = (subcatState.page - 1) * subcatState.limit;
    const params = new URLSearchParams({
        limit: subcatState.limit,
        offset: offset,
        sort_by: subcatState.sortBy,
        sort_order: subcatState.sortOrder,
    });
    if (subcatState.search) params.append('search', subcatState.search);
    if (subcatState.id_categoria) params.append('id_categoria', subcatState.id_categoria);
    if (subcatState.status === 'Activo') params.append('is_active', 'true');
    if (subcatState.status === 'Inactivo') params.append('is_active', 'false');

    try {
        const res = await fetch(`${CATALOGOS_API}/subcategorias/paged?${params.toString()}`, { headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('Error al cargar subcategorías');
        const data = await res.json();
        subcatState.total = data.total;
        renderSubcategoriasTable(data.items || []);
        renderSubcatPagination();
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-3 text-danger"><i class="bi bi-exclamation-circle me-1"></i> ${err.message}</td></tr>`;
    }
}

function renderSubcategoriasTable(items) {
    const tbody = document.getElementById('subcategorias-table-body');
    if (!tbody) return;
    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted"><i class="bi bi-diagram-2 fs-2 d-block mb-1 opacity-50"></i>No se encontraron subcategorías con los filtros aplicados.</td></tr>';
        return;
    }

    tbody.innerHTML = items.map(s => {
        // REDISEÑO UI/UX: estado unificado como Soft Badge.
        const statusBadge = catalogStatusBadge(s.estado);

        return `
            <tr>
                <td><span class="font-monospace text-muted small">#${s.id_subcategoria}</span></td>
                <td><strong class="text-dark">${s.nombre}</strong></td>
                <td><span class="badge bg-secondary-subtle text-secondary">${s.categoria_nombre || '-'}</span></td>
                <td>${statusBadge}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-info me-1" onclick="openSubcatDetailModal(${s.id_subcategoria})" title="Ver ficha">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary me-1" onclick="openEditSubcatModal(${s.id_subcategoria})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm ${s.estado === 'Activo' ? 'btn-outline-danger' : 'btn-outline-success'}" onclick="toggleSubcatStatus(${s.id_subcategoria}, '${s.nombre}', '${s.estado}')" title="${s.estado === 'Activo' ? 'Desactivar' : 'Activar'}">
                        <i class="bi ${s.estado === 'Activo' ? 'bi-trash' : 'bi-check-circle'}"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderSubcatPagination() {
    const info = document.getElementById('subcat-pagination-info');
    const pageInfo = document.getElementById('subcat-page-info');
    const prevBtn = document.getElementById('subcat-prev-page');
    const nextBtn = document.getElementById('subcat-next-page');
    if (!info) return;

    const start = subcatState.total === 0 ? 0 : (subcatState.page - 1) * subcatState.limit + 1;
    const end = Math.min(subcatState.page * subcatState.limit, subcatState.total);
    const maxPages = Math.ceil(subcatState.total / subcatState.limit) || 1;

    info.textContent = `Mostrando ${start}–${end} de ${subcatState.total}`;
    if (pageInfo) pageInfo.textContent = `Página ${subcatState.page} de ${maxPages}`;
    if (prevBtn) prevBtn.disabled = (subcatState.page <= 1);
    if (nextBtn) nextBtn.disabled = (subcatState.page >= maxPages);
}

function openNewSubcatModal() {
    subcatState.currentEditId = null;
    const title = document.getElementById('subcatModalTitle');
    if (title) title.textContent = 'Nueva Subcategoría';
    const form = document.getElementById('subcat-form');
    if (form) form.reset();
    document.getElementById('subcat-id').value = '';
    const modalEl = document.getElementById('subcat-modal');
    if (modalEl) {
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false });
        modal.show();
    }
}

async function openEditSubcatModal(id) {
    subcatState.currentEditId = id;
    try {
        const res = await fetch(`${CATALOGOS_API}/subcategorias/${id}`, { headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('Error al obtener datos de la subcategoría');
        const s = await res.json();
        document.getElementById('subcat-id').value = s.id_subcategoria;
        document.getElementById('subcat-nombre').value = s.nombre;
        document.getElementById('subcat-cat-id').value = s.id_categoria;
        const title = document.getElementById('subcatModalTitle');
        if (title) title.textContent = `Editar Subcategoría: ${s.nombre}`;
        const modalEl = document.getElementById('subcat-modal');
        if (modalEl) {
            const modal = bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false });
            modal.show();
        }
    } catch (e) {
        showToast(e.message, 'danger');
    }
}

async function openSubcatDetailModal(id) {
    const body = document.getElementById('subcat-detail-body');
    if (!body) return;
    body.innerHTML = '<div class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Cargando ficha...</div>';
    const modalEl = document.getElementById('subcat-detail-modal');
    const modal = bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false });
    modal.show();

    try {
        const res = await fetch(`${CATALOGOS_API}/subcategorias/${id}`, { headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('No se pudo cargar la ficha');
        const s = await res.json();
        body.innerHTML = `
            <div class="row g-3">
                <div class="col-sm-6">
                    <span class="text-muted small d-block">ID de Subcategoría</span>
                    <strong class="font-monospace fs-6">#${s.id_subcategoria}</strong>
                </div>
                <div class="col-sm-6">
                    <span class="text-muted small d-block">Estado</span>
                    ${catalogStatusBadge(s.estado)}
                </div>
                <div class="col-sm-6">
                    <span class="text-muted small d-block">Nombre</span>
                    <strong class="fs-6">${s.nombre}</strong>
                </div>
                <div class="col-sm-6">
                    <span class="text-muted small d-block">Categoría Padre</span>
                    <span class="badge bg-secondary-subtle text-secondary fs-6">${s.categoria_nombre || `ID #${s.id_categoria}`}</span>
                </div>
            </div>
        `;
    } catch (err) {
        body.innerHTML = `<div class="text-center text-danger py-4">${err.message}</div>`;
    }
}

async function handleSaveSubcat(e) {
    e.preventDefault();
    const id = document.getElementById('subcat-id').value;
    const nombre = document.getElementById('subcat-nombre').value.trim();
    const idCat = document.getElementById('subcat-cat-id').value;
    if (!nombre || !idCat) {
        showToast('Complete los campos obligatorios.', 'warning');
        return;
    }

    const payload = { id_categoria: Number(idCat), nombre: nombre };
    const isEdit = Boolean(id);
    const url = isEdit ? `${CATALOGOS_API}/subcategorias/${id}` : `${CATALOGOS_API}/subcategorias`;
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, {
            method: method,
            headers: getCatalogAuthHeaders(),
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Error al guardar la subcategoría');
        }
        showToast(`Subcategoría '${nombre}' ${isEdit ? 'actualizada' : 'creada'} con éxito.`, 'success');
        const modalEl = document.getElementById('subcat-modal');
        if (modalEl) bootstrap.Modal.getInstance(modalEl).hide();
        loadSubcategoriasTable();
        populateSubcategorias('filter-product-subcategoria', null, 'Todas las subcategorías');
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

let pendingSubcatDeactivate = null;

function toggleSubcatStatus(id, name, status) {
    if (status === 'Activo') {
        pendingSubcatDeactivate = { id, name };
        const text = document.getElementById('confirm-subcat-deactivate-text');
        if (text) text.innerHTML = `¿Está seguro de desactivar la subcategoría <strong>${name}</strong>? Los productos asociados permanecerán pero la subcategoría quedará inactiva.`;
        const modalEl = document.getElementById('confirm-subcat-deactivate-modal');
        if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();
    } else {
        // Reactivar directamente
        activateSubcat(id, name);
    }
}

async function confirmSubcatDeactivate() {
    if (!pendingSubcatDeactivate) return;
    const { id, name } = pendingSubcatDeactivate;
    try {
        const res = await fetch(`${CATALOGOS_API}/subcategorias/${id}`, { method: 'DELETE', headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error(await readCatalogError(res, 'Error al desactivar la subcategoría'));
        showToast(`Subcategoría '${name}' desactivada exitosamente.`, 'info');
        const modalEl = document.getElementById('confirm-subcat-deactivate-modal');
        if (modalEl) bootstrap.Modal.getInstance(modalEl).hide();
        loadSubcategoriasTable();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function activateSubcat(id, name) {
    try {
        const res = await fetch(`${CATALOGOS_API}/subcategorias/${id}/activar`, { method: 'POST', headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('Error al reactivar la subcategoría');
        showToast(`Subcategoría '${name}' reactivada exitosamente.`, 'success');
        loadSubcategoriasTable();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ---------------------------------------------------------------------------
// 2. UNIDADES DE MEDIDA CRUD
// ---------------------------------------------------------------------------

let unidadState = {
    page: 1,
    limit: 10,
    total: 0,
    sortBy: 'descripcion',
    sortOrder: 'asc',
    search: '',
    status: '',
    currentEditId: null,
};

async function loadUnidadesTable() {
    const tbody = document.getElementById('unidades-table-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-3 text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Cargando unidades...</td></tr>';

    const offset = (unidadState.page - 1) * unidadState.limit;
    const params = new URLSearchParams({
        limit: unidadState.limit,
        offset: offset,
        sort_by: unidadState.sortBy,
        sort_order: unidadState.sortOrder,
    });
    if (unidadState.search) params.append('search', unidadState.search);
    if (unidadState.status === 'Activo') params.append('is_active', 'true');
    if (unidadState.status === 'Inactivo') params.append('is_active', 'false');

    try {
        const res = await fetch(`${CATALOGOS_API}/unidades/paged?${params.toString()}`, { headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('Error al cargar unidades de medida');
        const data = await res.json();
        unidadState.total = data.total;
        renderUnidadesTable(data.items || []);
        renderUnidadPagination();
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-3 text-danger"><i class="bi bi-exclamation-circle me-1"></i> ${err.message}</td></tr>`;
    }
}

function renderUnidadesTable(items) {
    const tbody = document.getElementById('unidades-table-body');
    if (!tbody) return;
    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted"><i class="bi bi-rulers fs-2 d-block mb-1 opacity-50"></i>No se encontraron unidades de medida.</td></tr>';
        return;
    }

    tbody.innerHTML = items.map(u => {
        // REDISEÑO UI/UX: estado unificado como Soft Badge.
        const statusBadge = catalogStatusBadge(u.estado);

        return `
            <tr>
                <td><span class="font-monospace text-muted small">#${u.id_unidad}</span></td>
                <td><strong class="font-monospace text-teal">${u.codigo}</strong></td>
                <td>${u.descripcion}</td>
                <td>${statusBadge}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-info me-1" onclick="openUnidadDetailModal(${u.id_unidad})" title="Ver ficha">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary me-1" onclick="openEditUnidadModal(${u.id_unidad})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm ${u.estado === 'Activo' ? 'btn-outline-danger' : 'btn-outline-success'}" onclick="toggleUnidadStatus(${u.id_unidad}, '${u.codigo}', '${u.estado}')" title="${u.estado === 'Activo' ? 'Desactivar' : 'Activar'}">
                        <i class="bi ${u.estado === 'Activo' ? 'bi-trash' : 'bi-check-circle'}"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderUnidadPagination() {
    const info = document.getElementById('unidad-pagination-info');
    const pageInfo = document.getElementById('unidad-page-info');
    const prevBtn = document.getElementById('unidad-prev-page');
    const nextBtn = document.getElementById('unidad-next-page');
    if (!info) return;

    const start = unidadState.total === 0 ? 0 : (unidadState.page - 1) * unidadState.limit + 1;
    const end = Math.min(unidadState.page * unidadState.limit, unidadState.total);
    const maxPages = Math.ceil(unidadState.total / unidadState.limit) || 1;

    info.textContent = `Mostrando ${start}–${end} de ${unidadState.total}`;
    if (pageInfo) pageInfo.textContent = `Página ${unidadState.page} de ${maxPages}`;
    if (prevBtn) prevBtn.disabled = (unidadState.page <= 1);
    if (nextBtn) nextBtn.disabled = (unidadState.page >= maxPages);
}

function openNewUnidadModal() {
    unidadState.currentEditId = null;
    const title = document.getElementById('unidadModalTitle');
    if (title) title.textContent = 'Nueva Unidad de Medida';
    const form = document.getElementById('unidad-form');
    if (form) form.reset();
    document.getElementById('unidad-id').value = '';
    const modalEl = document.getElementById('unidad-modal');
    if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();
}

async function openEditUnidadModal(id) {
    unidadState.currentEditId = id;
    try {
        const res = await fetch(`${CATALOGOS_API}/unidades/${id}`, { headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('Error al obtener datos de la unidad');
        const u = await res.json();
        document.getElementById('unidad-id').value = u.id_unidad;
        document.getElementById('unidad-codigo').value = u.codigo;
        document.getElementById('unidad-descripcion').value = u.descripcion;
        const title = document.getElementById('unidadModalTitle');
        if (title) title.textContent = `Editar Unidad: ${u.codigo}`;
        const modalEl = document.getElementById('unidad-modal');
        if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();
    } catch (e) {
        showToast(e.message, 'danger');
    }
}

async function openUnidadDetailModal(id) {
    const body = document.getElementById('unidad-detail-body');
    if (!body) return;
    body.innerHTML = '<div class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Cargando ficha...</div>';
    const modalEl = document.getElementById('unidad-detail-modal');
    bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();

    try {
        const res = await fetch(`${CATALOGOS_API}/unidades/${id}`, { headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('No se pudo cargar la ficha');
        const u = await res.json();
        body.innerHTML = `
            <div class="row g-3">
                <div class="col-sm-6">
                    <span class="text-muted small d-block">ID de Unidad</span>
                    <strong class="font-monospace fs-6">#${u.id_unidad}</strong>
                </div>
                <div class="col-sm-6">
                    <span class="text-muted small d-block">Estado</span>
                    ${catalogStatusBadge(u.estado)}
                </div>
                <div class="col-sm-6">
                    <span class="text-muted small d-block">Código</span>
                    <strong class="font-monospace fs-5 text-teal">${u.codigo}</strong>
                </div>
                <div class="col-sm-6">
                    <span class="text-muted small d-block">Descripción</span>
                    <strong class="fs-6">${u.descripcion}</strong>
                </div>
            </div>
        `;
    } catch (err) {
        body.innerHTML = `<div class="text-center text-danger py-4">${err.message}</div>`;
    }
}

async function handleSaveUnidad(e) {
    e.preventDefault();
    const id = document.getElementById('unidad-id').value;
    const codigo = document.getElementById('unidad-codigo').value.trim().toUpperCase();
    const descripcion = document.getElementById('unidad-descripcion').value.trim();
    if (!codigo || !descripcion) {
        showToast('Complete los campos obligatorios.', 'warning');
        return;
    }

    const payload = { codigo, descripcion };
    const isEdit = Boolean(id);
    const url = isEdit ? `${CATALOGOS_API}/unidades/${id}` : `${CATALOGOS_API}/unidades`;
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, {
            method: method,
            headers: getCatalogAuthHeaders(),
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Error al guardar unidad');
        }
        showToast(`Unidad '${codigo}' ${isEdit ? 'actualizada' : 'creada'} con éxito.`, 'success');
        const modalEl = document.getElementById('unidad-modal');
        if (modalEl) bootstrap.Modal.getInstance(modalEl).hide();
        loadUnidadesTable();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

let pendingUnidadDeactivate = null;

function toggleUnidadStatus(id, code, status) {
    if (status === 'Activo') {
        pendingUnidadDeactivate = { id, code };
        const text = document.getElementById('confirm-unidad-deactivate-text');
        if (text) text.innerHTML = `¿Está seguro de desactivar la unidad de medida <strong>${code}</strong>?`;
        const modalEl = document.getElementById('confirm-unidad-deactivate-modal');
        if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();
    } else {
        activateUnidad(id, code);
    }
}

async function confirmUnidadDeactivate() {
    if (!pendingUnidadDeactivate) return;
    const { id, code } = pendingUnidadDeactivate;
    try {
        const res = await fetch(`${CATALOGOS_API}/unidades/${id}`, { method: 'DELETE', headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error(await readCatalogError(res, 'Error al desactivar la unidad'));
        showToast(`Unidad '${code}' desactivada exitosamente.`, 'info');
        const modalEl = document.getElementById('confirm-unidad-deactivate-modal');
        if (modalEl) bootstrap.Modal.getInstance(modalEl).hide();
        loadUnidadesTable();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function activateUnidad(id, code) {
    try {
        const res = await fetch(`${CATALOGOS_API}/unidades/${id}/activar`, { method: 'POST', headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('Error al reactivar la unidad');
        showToast(`Unidad '${code}' reactivada exitosamente.`, 'success');
        loadUnidadesTable();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ---------------------------------------------------------------------------
// 3. SUCURSALES CRUD
// ---------------------------------------------------------------------------

let sucursalState = {
    page: 1,
    limit: 10,
    total: 0,
    sortBy: 'nombre',
    sortOrder: 'asc',
    search: '',
    status: '',
    fecha_desde: '',
    fecha_hasta: '',
    currentEditId: null,
};

async function loadSucursalesTable() {
    const tbody = document.getElementById('sucursales-table-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="7" class="text-center py-3 text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Cargando sucursales...</td></tr>';

    const offset = (sucursalState.page - 1) * sucursalState.limit;
    const params = new URLSearchParams({
        limit: sucursalState.limit,
        offset: offset,
        sort_by: sucursalState.sortBy,
        sort_order: sucursalState.sortOrder,
    });
    if (sucursalState.search) params.append('search', sucursalState.search);
    if (sucursalState.status === 'Activo') params.append('is_active', 'true');
    if (sucursalState.status === 'Inactivo') params.append('is_active', 'false');
    if (sucursalState.fecha_desde) params.append('fecha_desde', sucursalState.fecha_desde);
    if (sucursalState.fecha_hasta) params.append('fecha_hasta', sucursalState.fecha_hasta);

    try {
        const res = await fetch(`${CATALOGOS_API}/sucursales/paged?${params.toString()}`, { headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('Error al cargar sucursales');
        const data = await res.json();
        sucursalState.total = data.total;
        renderSucursalesTable(data.items || []);
        renderSucursalPagination();
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-3 text-danger"><i class="bi bi-exclamation-circle me-1"></i> ${err.message}</td></tr>`;
    }
}

function renderSucursalesTable(items) {
    const tbody = document.getElementById('sucursales-table-body');
    if (!tbody) return;
    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted"><i class="bi bi-building fs-2 d-block mb-1 opacity-50"></i>No se encontraron sucursales.</td></tr>';
        return;
    }

    tbody.innerHTML = items.map(s => {
        // REDISEÑO UI/UX: estado unificado como Soft Badge.
        const statusBadge = catalogStatusBadge(s.estado);

        return `
            <tr>
                <td><span class="font-monospace text-muted small">#${s.id_sucursal}</span></td>
                <td><strong class="text-dark">${s.nombre}</strong></td>
                <td><small class="text-muted">${s.direccion}</small></td>
                <td><small>${s.telefono || '-'}</small></td>
                <td><span class="badge bg-teal-subtle text-teal">${s.total_areas || 0} áreas</span></td>
                <td>${statusBadge}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-info me-1" onclick="openSucursalDetailModal(${s.id_sucursal})" title="Ver ficha">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary me-1" onclick="openEditSucursalModal(${s.id_sucursal})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm ${s.estado === 'Activo' ? 'btn-outline-danger' : 'btn-outline-success'}" onclick="toggleSucursalStatus(${s.id_sucursal}, '${s.nombre}', '${s.estado}')" title="${s.estado === 'Activo' ? 'Desactivar' : 'Activar'}">
                        <i class="bi ${s.estado === 'Activo' ? 'bi-trash' : 'bi-check-circle'}"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderSucursalPagination() {
    const info = document.getElementById('sucursal-pagination-info');
    const pageInfo = document.getElementById('sucursal-page-info');
    const prevBtn = document.getElementById('sucursal-prev-page');
    const nextBtn = document.getElementById('sucursal-next-page');
    if (!info) return;

    const start = sucursalState.total === 0 ? 0 : (sucursalState.page - 1) * sucursalState.limit + 1;
    const end = Math.min(sucursalState.page * sucursalState.limit, sucursalState.total);
    const maxPages = Math.ceil(sucursalState.total / sucursalState.limit) || 1;

    info.textContent = `Mostrando ${start}–${end} de ${sucursalState.total}`;
    if (pageInfo) pageInfo.textContent = `Página ${sucursalState.page} de ${maxPages}`;
    if (prevBtn) prevBtn.disabled = (sucursalState.page <= 1);
    if (nextBtn) nextBtn.disabled = (sucursalState.page >= maxPages);
}

function openNewSucursalModal() {
    sucursalState.currentEditId = null;
    const title = document.getElementById('sucursalModalTitle');
    if (title) title.textContent = 'Nueva Sucursal';
    const form = document.getElementById('sucursal-form');
    if (form) form.reset();
    document.getElementById('sucursal-id').value = '';
    const modalEl = document.getElementById('sucursal-modal');
    if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();
}

async function openEditSucursalModal(id) {
    sucursalState.currentEditId = id;
    try {
        const res = await fetch(`${CATALOGOS_API}/sucursales/${id}`, { headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('Error al obtener datos de la sucursal');
        const s = await res.json();
        document.getElementById('sucursal-id').value = s.id_sucursal;
        document.getElementById('sucursal-nombre').value = s.nombre;
        document.getElementById('sucursal-direccion').value = s.direccion;
        document.getElementById('sucursal-telefono').value = s.telefono || '';
        const title = document.getElementById('sucursalModalTitle');
        if (title) title.textContent = `Editar Sucursal: ${s.nombre}`;
        const modalEl = document.getElementById('sucursal-modal');
        if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();
    } catch (e) {
        showToast(e.message, 'danger');
    }
}

async function openSucursalDetailModal(id) {
    const body = document.getElementById('sucursal-detail-body');
    if (!body) return;
    body.innerHTML = '<div class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Cargando ficha...</div>';
    const modalEl = document.getElementById('sucursal-detail-modal');
    bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();

    try {
        const res = await fetch(`${CATALOGOS_API}/sucursales/${id}`, { headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('No se pudo cargar la ficha');
        const s = await res.json();
        body.innerHTML = `
            <div class="row g-3">
                <div class="col-sm-6">
                    <span class="text-muted small d-block">ID de Sucursal</span>
                    <strong class="font-monospace fs-6">#${s.id_sucursal}</strong>
                </div>
                <div class="col-sm-6">
                    <span class="text-muted small d-block">Estado</span>
                    ${catalogStatusBadge(s.estado)}
                </div>
                <div class="col-12">
                    <span class="text-muted small d-block">Nombre de la Sucursal</span>
                    <strong class="fs-5 text-teal">${s.nombre}</strong>
                </div>
                <div class="col-sm-8">
                    <span class="text-muted small d-block">Dirección</span>
                    <span>${s.direccion}</span>
                </div>
                <div class="col-sm-4">
                    <span class="text-muted small d-block">Teléfono</span>
                    <span>${s.telefono || 'Sin teléfono'}</span>
                </div>
                <div class="col-sm-6">
                    <span class="text-muted small d-block">Áreas Registradas</span>
                    <span class="badge bg-teal-subtle text-teal fs-6">${s.total_areas || 0} áreas</span>
                </div>
                <div class="col-sm-6">
                    <span class="text-muted small d-block">Fecha de Registro</span>
                    <span class="small">${formatDate(s.fecha_creacion)}</span>
                </div>
            </div>
        `;
    } catch (err) {
        body.innerHTML = `<div class="text-center text-danger py-4">${err.message}</div>`;
    }
}

async function handleSaveSucursal(e) {
    e.preventDefault();
    const id = document.getElementById('sucursal-id').value;
    const nombre = document.getElementById('sucursal-nombre').value.trim();
    const direccion = document.getElementById('sucursal-direccion').value.trim();
    const telefono = document.getElementById('sucursal-telefono').value.trim();
    if (!nombre || !direccion) {
        showToast('Complete los campos obligatorios.', 'warning');
        return;
    }

    const payload = { nombre, direccion, telefono: telefono || null };
    const isEdit = Boolean(id);
    const url = isEdit ? `${CATALOGOS_API}/sucursales/${id}` : `${CATALOGOS_API}/sucursales`;
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, {
            method: method,
            headers: getCatalogAuthHeaders(),
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Error al guardar sucursal');
        }
        showToast(`Sucursal '${nombre}' ${isEdit ? 'actualizada' : 'creada'} con éxito.`, 'success');
        const modalEl = document.getElementById('sucursal-modal');
        if (modalEl) bootstrap.Modal.getInstance(modalEl).hide();
        loadSucursalesTable();
        populateAreaSucursalesDropdown();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

let pendingSucursalDeactivate = null;

function toggleSucursalStatus(id, name, status) {
    if (status === 'Activo') {
        pendingSucursalDeactivate = { id, name };
        const text = document.getElementById('confirm-sucursal-deactivate-text');
        if (text) text.innerHTML = `¿Está seguro de desactivar la sucursal <strong>${name}</strong>?`;
        const modalEl = document.getElementById('confirm-sucursal-deactivate-modal');
        if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();
    } else {
        activateSucursal(id, name);
    }
}

async function confirmSucursalDeactivate() {
    if (!pendingSucursalDeactivate) return;
    const { id, name } = pendingSucursalDeactivate;
    try {
        const res = await fetch(`${CATALOGOS_API}/sucursales/${id}`, { method: 'DELETE', headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error(await readCatalogError(res, 'Error al desactivar la sucursal'));
        showToast(`Sucursal '${name}' desactivada exitosamente.`, 'info');
        const modalEl = document.getElementById('confirm-sucursal-deactivate-modal');
        if (modalEl) bootstrap.Modal.getInstance(modalEl).hide();
        loadSucursalesTable();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function activateSucursal(id, name) {
    try {
        const res = await fetch(`${CATALOGOS_API}/sucursales/${id}/activar`, { method: 'POST', headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('Error al reactivar la sucursal');
        showToast(`Sucursal '${name}' reactivada exitosamente.`, 'success');
        loadSucursalesTable();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ---------------------------------------------------------------------------
// 4. ÁREAS DE BODEGA CRUD
// ---------------------------------------------------------------------------

let areaState = {
    page: 1,
    limit: 10,
    total: 0,
    sortBy: 'nombre_area',
    sortOrder: 'asc',
    search: '',
    id_sucursal: '',
    status: '',
    currentEditId: null,
};

async function populateAreaSucursalesDropdown() {
    const filterSelect = document.getElementById('filter-area-sucursal');
    const formSelect = document.getElementById('area-sucursal-id');
    try {
        const res = await fetch(`${CATALOGOS_API}/sucursales?include_inactive=false`, { headers: getCatalogAuthHeaders() });
        if (res.ok) {
            const sucs = await res.json();
            if (filterSelect) {
                const current = filterSelect.value;
                filterSelect.innerHTML = '<option value="">Todas las sucursales</option>' +
                    sucs.map(s => `<option value="${s.id_sucursal}">${s.nombre}</option>`).join('');
                filterSelect.value = current;
            }
            if (formSelect) {
                formSelect.innerHTML = '<option value="">Seleccione sucursal...</option>' +
                    sucs.map(s => `<option value="${s.id_sucursal}">${s.nombre}</option>`).join('');
            }
        }
    } catch (e) {
        console.warn('Error al cargar sucursales en combo de áreas:', e);
    }
}

async function loadAreasTable() {
    const tbody = document.getElementById('areas-table-body');
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="5" class="text-center py-3 text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Cargando áreas...</td></tr>';

    const offset = (areaState.page - 1) * areaState.limit;
    const params = new URLSearchParams({
        limit: areaState.limit,
        offset: offset,
        sort_by: areaState.sortBy,
        sort_order: areaState.sortOrder,
    });
    if (areaState.search) params.append('search', areaState.search);
    if (areaState.id_sucursal) params.append('id_sucursal', areaState.id_sucursal);
    if (areaState.status === 'Activo') params.append('is_active', 'true');
    if (areaState.status === 'Inactivo') params.append('is_active', 'false');

    try {
        const res = await fetch(`${CATALOGOS_API}/areas/paged?${params.toString()}`, { headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('Error al cargar áreas de bodega');
        const data = await res.json();
        areaState.total = data.total;
        renderAreasTable(data.items || []);
        renderAreaPagination();
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="5" class="text-center py-3 text-danger"><i class="bi bi-exclamation-circle me-1"></i> ${err.message}</td></tr>`;
    }
}

function renderAreasTable(items) {
    const tbody = document.getElementById('areas-table-body');
    if (!tbody) return;
    if (items.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted"><i class="bi bi-geo-alt fs-2 d-block mb-1 opacity-50"></i>No se encontraron áreas de bodega.</td></tr>';
        return;
    }

    tbody.innerHTML = items.map(a => {
        // REDISEÑO UI/UX: estado unificado como Soft Badge.
        const statusBadge = catalogStatusBadge(a.estado);

        return `
            <tr>
                <td><span class="font-monospace text-muted small">#${a.id_area}</span></td>
                <td><strong class="text-dark">${a.nombre_area}</strong></td>
                <td><span class="badge bg-secondary-subtle text-secondary">${a.sucursal_nombre || `Sucursal #${a.id_sucursal}`}</span></td>
                <td>${statusBadge}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-info me-1" onclick="openAreaDetailModal(${a.id_area})" title="Ver ficha">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary me-1" onclick="openEditAreaModal(${a.id_area})" title="Editar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm ${a.estado === 'Activo' ? 'btn-outline-danger' : 'btn-outline-success'}" onclick="toggleAreaStatus(${a.id_area}, '${a.nombre_area}', '${a.estado}')" title="${a.estado === 'Activo' ? 'Desactivar' : 'Activar'}">
                        <i class="bi ${a.estado === 'Activo' ? 'bi-trash' : 'bi-check-circle'}"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderAreaPagination() {
    const info = document.getElementById('area-pagination-info');
    const pageInfo = document.getElementById('area-page-info');
    const prevBtn = document.getElementById('area-prev-page');
    const nextBtn = document.getElementById('area-next-page');
    if (!info) return;

    const start = areaState.total === 0 ? 0 : (areaState.page - 1) * areaState.limit + 1;
    const end = Math.min(areaState.page * areaState.limit, areaState.total);
    const maxPages = Math.ceil(areaState.total / areaState.limit) || 1;

    info.textContent = `Mostrando ${start}–${end} de ${areaState.total}`;
    if (pageInfo) pageInfo.textContent = `Página ${areaState.page} de ${maxPages}`;
    if (prevBtn) prevBtn.disabled = (areaState.page <= 1);
    if (nextBtn) nextBtn.disabled = (areaState.page >= maxPages);
}

function openNewAreaModal() {
    areaState.currentEditId = null;
    const title = document.getElementById('areaModalTitle');
    if (title) title.textContent = 'Nueva Área de Bodega';
    const form = document.getElementById('area-form');
    if (form) form.reset();
    document.getElementById('area-id').value = '';
    const modalEl = document.getElementById('area-modal');
    if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();
}

async function openEditAreaModal(id) {
    areaState.currentEditId = id;
    try {
        const res = await fetch(`${CATALOGOS_API}/areas/${id}`, { headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('Error al obtener datos del área');
        const a = await res.json();
        document.getElementById('area-id').value = a.id_area;
        document.getElementById('area-nombre').value = a.nombre_area;
        document.getElementById('area-sucursal-id').value = a.id_sucursal;
        const title = document.getElementById('areaModalTitle');
        if (title) title.textContent = `Editar Área: ${a.nombre_area}`;
        const modalEl = document.getElementById('area-modal');
        if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();
    } catch (e) {
        showToast(e.message, 'danger');
    }
}

async function openAreaDetailModal(id) {
    const body = document.getElementById('area-detail-body');
    if (!body) return;
    body.innerHTML = '<div class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Cargando ficha...</div>';
    const modalEl = document.getElementById('area-detail-modal');
    bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();

    try {
        const res = await fetch(`${CATALOGOS_API}/areas/${id}`, { headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('No se pudo cargar la ficha');
        const a = await res.json();
        body.innerHTML = `
            <div class="row g-3">
                <div class="col-sm-6">
                    <span class="text-muted small d-block">ID de Área</span>
                    <strong class="font-monospace fs-6">#${a.id_area}</strong>
                </div>
                <div class="col-sm-6">
                    <span class="text-muted small d-block">Estado</span>
                    ${catalogStatusBadge(a.estado)}
                </div>
                <div class="col-sm-6">
                    <span class="text-muted small d-block">Nombre del Área</span>
                    <strong class="fs-6">${a.nombre_area}</strong>
                </div>
                <div class="col-sm-6">
                    <span class="text-muted small d-block">Sucursal Perteneciente</span>
                    <span class="badge bg-teal-subtle text-teal fs-6">${a.sucursal_nombre || `ID #${a.id_sucursal}`}</span>
                </div>
            </div>
        `;
    } catch (err) {
        body.innerHTML = `<div class="text-center text-danger py-4">${err.message}</div>`;
    }
}

async function handleSaveArea(e) {
    e.preventDefault();
    const id = document.getElementById('area-id').value;
    const nombre = document.getElementById('area-nombre').value.trim();
    const idSuc = document.getElementById('area-sucursal-id').value;
    if (!nombre || !idSuc) {
        showToast('Complete los campos obligatorios.', 'warning');
        return;
    }

    const payload = { id_sucursal: Number(idSuc), nombre_area: nombre };
    const isEdit = Boolean(id);
    const url = isEdit ? `${CATALOGOS_API}/areas/${id}` : `${CATALOGOS_API}/areas`;
    const method = isEdit ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, {
            method: method,
            headers: getCatalogAuthHeaders(),
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Error al guardar el área');
        }
        showToast(`Área '${nombre}' ${isEdit ? 'actualizada' : 'creada'} con éxito.`, 'success');
        const modalEl = document.getElementById('area-modal');
        if (modalEl) bootstrap.Modal.getInstance(modalEl).hide();
        loadAreasTable();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

let pendingAreaDeactivate = null;

function toggleAreaStatus(id, name, status) {
    if (status === 'Activo') {
        pendingAreaDeactivate = { id, name };
        const text = document.getElementById('confirm-area-deactivate-text');
        if (text) text.innerHTML = `¿Está seguro de desactivar el área <strong>${name}</strong>?`;
        const modalEl = document.getElementById('confirm-area-deactivate-modal');
        if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();
    } else {
        activateArea(id, name);
    }
}

async function confirmAreaDeactivate() {
    if (!pendingAreaDeactivate) return;
    const { id, name } = pendingAreaDeactivate;
    try {
        const res = await fetch(`${CATALOGOS_API}/areas/${id}`, { method: 'DELETE', headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error(await readCatalogError(res, 'Error al desactivar el área'));
        showToast(`Área '${name}' desactivada exitosamente.`, 'info');
        const modalEl = document.getElementById('confirm-area-deactivate-modal');
        if (modalEl) bootstrap.Modal.getInstance(modalEl).hide();
        loadAreasTable();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function activateArea(id, name) {
    try {
        const res = await fetch(`${CATALOGOS_API}/areas/${id}/activar`, { method: 'POST', headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('Error al reactivar el área');
        showToast(`Área '${name}' reactivada exitosamente.`, 'success');
        loadAreasTable();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ---------------------------------------------------------------------------
// Listeners y Bindings globales del Bloque 2
// ---------------------------------------------------------------------------

function initBloque2Listeners() {
    // 1. Subcategorías
    const btnNewSubcat = document.getElementById('btn-new-subcat');
    if (btnNewSubcat) btnNewSubcat.addEventListener('click', openNewSubcatModal);
    const subcatForm = document.getElementById('subcat-form');
    if (subcatForm) subcatForm.addEventListener('submit', handleSaveSubcat);
    const btnConfirmSubcatDeact = document.getElementById('btn-confirm-subcat-deactivate');
    if (btnConfirmSubcatDeact) btnConfirmSubcatDeact.addEventListener('click', confirmSubcatDeactivate);
    const btnFilterSubcat = document.getElementById('btn-filter-subcat');
    if (btnFilterSubcat) btnFilterSubcat.addEventListener('click', () => {
        subcatState.page = 1;
        subcatState.search = document.getElementById('filter-subcat-search')?.value.trim() || '';
        subcatState.id_categoria = document.getElementById('filter-subcat-cat')?.value || '';
        subcatState.status = document.getElementById('filter-subcat-status')?.value || '';
        loadSubcategoriasTable();
    });
    const btnResetSubcat = document.getElementById('btn-reset-subcat');
    if (btnResetSubcat) btnResetSubcat.addEventListener('click', () => {
        subcatState.page = 1;
        subcatState.search = '';
        subcatState.id_categoria = '';
        subcatState.status = '';
        if (document.getElementById('filter-subcat-search')) document.getElementById('filter-subcat-search').value = '';
        if (document.getElementById('filter-subcat-cat')) document.getElementById('filter-subcat-cat').value = '';
        if (document.getElementById('filter-subcat-status')) document.getElementById('filter-subcat-status').value = '';
        loadSubcategoriasTable();
    });
    const subcatPrev = document.getElementById('subcat-prev-page');
    if (subcatPrev) subcatPrev.addEventListener('click', () => {
        if (subcatState.page > 1) { subcatState.page--; loadSubcategoriasTable(); }
    });
    const subcatNext = document.getElementById('subcat-next-page');
    if (subcatNext) subcatNext.addEventListener('click', () => {
        const maxPages = Math.ceil(subcatState.total / subcatState.limit) || 1;
        if (subcatState.page < maxPages) { subcatState.page++; loadSubcategoriasTable(); }
    });
    document.querySelectorAll('[data-subcat-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-subcat-sort');
            subcatState.sortOrder = (subcatState.sortBy === col && subcatState.sortOrder === 'asc') ? 'desc' : 'asc';
            subcatState.sortBy = col;
            loadSubcategoriasTable();
        });
    });
    document.getElementById('btn-export-subcat-excel')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/subcategorias/export?format=excel`, 'subcategorias.xlsx');
    });
    document.getElementById('btn-export-subcat-csv')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/subcategorias/export?format=csv`, 'subcategorias.csv');
    });

    // 2. Unidades
    const btnNewUnidad = document.getElementById('btn-new-unidad');
    if (btnNewUnidad) btnNewUnidad.addEventListener('click', openNewUnidadModal);
    const unidadForm = document.getElementById('unidad-form');
    if (unidadForm) unidadForm.addEventListener('submit', handleSaveUnidad);
    const btnConfirmUnidadDeact = document.getElementById('btn-confirm-unidad-deactivate');
    if (btnConfirmUnidadDeact) btnConfirmUnidadDeact.addEventListener('click', confirmUnidadDeactivate);
    const btnFilterUnidad = document.getElementById('btn-filter-unidad');
    if (btnFilterUnidad) btnFilterUnidad.addEventListener('click', () => {
        unidadState.page = 1;
        unidadState.search = document.getElementById('filter-unidad-search')?.value.trim() || '';
        unidadState.status = document.getElementById('filter-unidad-status')?.value || '';
        loadUnidadesTable();
    });
    const btnResetUnidad = document.getElementById('btn-reset-unidad');
    if (btnResetUnidad) btnResetUnidad.addEventListener('click', () => {
        unidadState.page = 1;
        unidadState.search = '';
        unidadState.status = '';
        if (document.getElementById('filter-unidad-search')) document.getElementById('filter-unidad-search').value = '';
        if (document.getElementById('filter-unidad-status')) document.getElementById('filter-unidad-status').value = '';
        loadUnidadesTable();
    });
    const unidadPrev = document.getElementById('unidad-prev-page');
    if (unidadPrev) unidadPrev.addEventListener('click', () => {
        if (unidadState.page > 1) { unidadState.page--; loadUnidadesTable(); }
    });
    const unidadNext = document.getElementById('unidad-next-page');
    if (unidadNext) unidadNext.addEventListener('click', () => {
        const maxPages = Math.ceil(unidadState.total / unidadState.limit) || 1;
        if (unidadState.page < maxPages) { unidadState.page++; loadUnidadesTable(); }
    });
    document.querySelectorAll('[data-unidad-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-unidad-sort');
            unidadState.sortOrder = (unidadState.sortBy === col && unidadState.sortOrder === 'asc') ? 'desc' : 'asc';
            unidadState.sortBy = col;
            loadUnidadesTable();
        });
    });
    document.getElementById('btn-export-unidades-excel')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/unidades/export?format=excel`, 'unidades_medida.xlsx');
    });
    document.getElementById('btn-export-unidades-csv')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/unidades/export?format=csv`, 'unidades_medida.csv');
    });

    // 3. Sucursales
    const btnNewSucursal = document.getElementById('btn-new-sucursal');
    if (btnNewSucursal) btnNewSucursal.addEventListener('click', openNewSucursalModal);
    const sucursalForm = document.getElementById('sucursal-form');
    if (sucursalForm) sucursalForm.addEventListener('submit', handleSaveSucursal);
    const btnConfirmSucDeact = document.getElementById('btn-confirm-sucursal-deactivate');
    if (btnConfirmSucDeact) btnConfirmSucDeact.addEventListener('click', confirmSucursalDeactivate);
    const btnFilterSucursal = document.getElementById('btn-filter-sucursal');
    if (btnFilterSucursal) btnFilterSucursal.addEventListener('click', () => {
        sucursalState.page = 1;
        sucursalState.search = document.getElementById('filter-sucursal-search')?.value.trim() || '';
        sucursalState.status = document.getElementById('filter-sucursal-status')?.value || '';
        sucursalState.fecha_desde = document.getElementById('filter-sucursal-from')?.value || '';
        sucursalState.fecha_hasta = document.getElementById('filter-sucursal-to')?.value || '';
        loadSucursalesTable();
    });
    const btnResetSucursal = document.getElementById('btn-reset-sucursal');
    if (btnResetSucursal) btnResetSucursal.addEventListener('click', () => {
        sucursalState.page = 1;
        sucursalState.search = '';
        sucursalState.status = '';
        sucursalState.fecha_desde = '';
        sucursalState.fecha_hasta = '';
        if (document.getElementById('filter-sucursal-search')) document.getElementById('filter-sucursal-search').value = '';
        if (document.getElementById('filter-sucursal-status')) document.getElementById('filter-sucursal-status').value = '';
        if (document.getElementById('filter-sucursal-from')) document.getElementById('filter-sucursal-from').value = '';
        if (document.getElementById('filter-sucursal-to')) document.getElementById('filter-sucursal-to').value = '';
        loadSucursalesTable();
    });
    const sucPrev = document.getElementById('sucursal-prev-page');
    if (sucPrev) sucPrev.addEventListener('click', () => {
        if (sucursalState.page > 1) { sucursalState.page--; loadSucursalesTable(); }
    });
    const sucNext = document.getElementById('sucursal-next-page');
    if (sucNext) sucNext.addEventListener('click', () => {
        const maxPages = Math.ceil(sucursalState.total / sucursalState.limit) || 1;
        if (sucursalState.page < maxPages) { sucursalState.page++; loadSucursalesTable(); }
    });
    document.querySelectorAll('[data-sucursal-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-sucursal-sort');
            sucursalState.sortOrder = (sucursalState.sortBy === col && sucursalState.sortOrder === 'asc') ? 'desc' : 'asc';
            sucursalState.sortBy = col;
            loadSucursalesTable();
        });
    });
    document.getElementById('btn-export-sucursales-excel')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/sucursales/export?format=excel`, 'sucursales.xlsx');
    });
    document.getElementById('btn-export-sucursales-csv')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/sucursales/export?format=csv`, 'sucursales.csv');
    });

    // 4. Áreas
    const btnNewArea = document.getElementById('btn-new-area');
    if (btnNewArea) btnNewArea.addEventListener('click', openNewAreaModal);
    const areaForm = document.getElementById('area-form');
    if (areaForm) areaForm.addEventListener('submit', handleSaveArea);
    const btnConfirmAreaDeact = document.getElementById('btn-confirm-area-deactivate');
    if (btnConfirmAreaDeact) btnConfirmAreaDeact.addEventListener('click', confirmAreaDeactivate);
    const btnFilterArea = document.getElementById('btn-filter-area');
    if (btnFilterArea) btnFilterArea.addEventListener('click', () => {
        areaState.page = 1;
        areaState.search = document.getElementById('filter-area-search')?.value.trim() || '';
        areaState.id_sucursal = document.getElementById('filter-area-sucursal')?.value || '';
        areaState.status = document.getElementById('filter-area-status')?.value || '';
        loadAreasTable();
    });
    const btnResetArea = document.getElementById('btn-reset-area');
    if (btnResetArea) btnResetArea.addEventListener('click', () => {
        areaState.page = 1;
        areaState.search = '';
        areaState.id_sucursal = '';
        areaState.status = '';
        if (document.getElementById('filter-area-search')) document.getElementById('filter-area-search').value = '';
        if (document.getElementById('filter-area-sucursal')) document.getElementById('filter-area-sucursal').value = '';
        if (document.getElementById('filter-area-status')) document.getElementById('filter-area-status').value = '';
        loadAreasTable();
    });
    const areaPrev = document.getElementById('area-prev-page');
    if (areaPrev) areaPrev.addEventListener('click', () => {
        if (areaState.page > 1) { areaState.page--; loadAreasTable(); }
    });
    const areaNext = document.getElementById('area-next-page');
    if (areaNext) areaNext.addEventListener('click', () => {
        const maxPages = Math.ceil(areaState.total / areaState.limit) || 1;
        if (areaState.page < maxPages) { areaState.page++; loadAreasTable(); }
    });
    document.querySelectorAll('[data-area-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-area-sort');
            areaState.sortOrder = (areaState.sortBy === col && areaState.sortOrder === 'asc') ? 'desc' : 'asc';
            areaState.sortBy = col;
            loadAreasTable();
        });
    });
    document.getElementById('btn-export-areas-excel')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/areas/export?format=excel`, 'areas_bodega.xlsx');
    });
    document.getElementById('btn-export-areas-csv')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/areas/export?format=csv`, 'areas_bodega.csv');
    });
}

document.addEventListener('DOMContentLoaded', () => {
    initBloque2Listeners();
});

// ===========================================================================
// BLOQUE 3: MOTIVOS DE MERMA, MÉTODOS DE PAGO, PROVEEDORES, DEPARTAMENTOS
// Y MUNICIPIOS (dropdown dependiente departamento -> municipio)
// ===========================================================================

const B3_STATE = {
    motivos: { page: 1, limit: 10, total: 0, sortBy: 'descripcion', sortOrder: 'asc', search: '', status: '', pending: null },
    metodos: { page: 1, limit: 10, total: 0, sortBy: 'nombre', sortOrder: 'asc', search: '', status: '', pending: null },
    proveedores: { page: 1, limit: 10, total: 0, sortBy: 'distribuidora', sortOrder: 'asc', search: '', status: '', fecha_desde: '', fecha_hasta: '', pending: null },
    departamentos: { page: 1, limit: 10, total: 0, sortBy: 'nombre', sortOrder: 'asc', search: '', status: '', pending: null },
    municipios: { page: 1, limit: 10, total: 0, sortBy: 'nombre', sortOrder: 'asc', search: '', status: '', id_departamento: '', pending: null },
};

const B3_CONFIG = {
    motivos: { plural: 'motivos-merma', label: 'motivo de merma', singular: 'motivo' },
    metodos: { plural: 'metodos-pago', label: 'método de pago', singular: 'metodo' },
    proveedores: { plural: 'proveedores', label: 'proveedor', singular: 'proveedor' },
    departamentos: { plural: 'departamentos', label: 'departamento', singular: 'departamento' },
    municipios: { plural: 'municipios', label: 'municipio', singular: 'municipio' },
};

const B3_EXTRA_PARAMS = {
    proveedores: (s) => ({ fecha_desde: s.fecha_desde, fecha_hasta: s.fecha_hasta }),
    municipios: (s) => ({ id_departamento: s.id_departamento }),
};

function b3StatusBadge(estado) {
    // REDISEÑO UI/UX: reutiliza el mismo Soft Badge del resto del catálogo.
    return catalogStatusBadge(estado);
}

function b3JsStr(value) {
    return String(value || '').replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '');
}

function b3EmptyRow(message, cols) {
    return `<tr><td colspan="${cols}" class="text-center py-4 text-muted"><i class="bi bi-inbox fs-2 d-block mb-1 opacity-50"></i>${message}</td></tr>`;
}

function b3ActionButtons(key, id, name, estado) {
    return `
        <button class="btn btn-sm btn-outline-info me-1" onclick="openB3Detail('${key}', ${id})" title="Ver ficha"><i class="bi bi-eye"></i></button>
        <button class="btn btn-sm btn-outline-secondary me-1" onclick="openB3Edit('${key}', ${id})" title="Editar"><i class="bi bi-pencil"></i></button>
        <button class="btn btn-sm ${estado === 'Activo' ? 'btn-outline-danger' : 'btn-outline-success'}" onclick="toggleB3Status('${key}', ${id}, '${b3JsStr(name)}', '${estado}')" title="${estado === 'Activo' ? 'Desactivar' : 'Activar'}">
            <i class="bi ${estado === 'Activo' ? 'bi-trash' : 'bi-check-circle'}"></i>
        </button>`;
}

function b3QueryString(state, plugin) {
    const params = new URLSearchParams({
        limit: state.limit,
        offset: (state.page - 1) * state.limit,
        sort_by: state.sortBy,
        sort_order: state.sortOrder,
    });
    if (state.search) params.append('search', state.search);
    if (state.status === 'Activo') params.append('is_active', 'true');
    if (state.status === 'Inactivo') params.append('is_active', 'false');
    if (plugin) {
        Object.keys(plugin).forEach((k) => { if (plugin[k]) params.append(k, plugin[k]); });
    }
    return params;
}

async function loadB3Table(key, tbodyId, renderFn) {
    const state = B3_STATE[key];
    const tbody = document.getElementById(tbodyId);
    if (!tbody) return;
    tbody.innerHTML = '<tr><td colspan="8" class="text-center py-3 text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Cargando...</td></tr>';
    const plugin = typeof B3_EXTRA_PARAMS[key] === 'function' ? B3_EXTRA_PARAMS[key](state) : null;
    try {
        const res = await fetch(`${CATALOGOS_API}/${B3_CONFIG[key].plural}/paged?${b3QueryString(state, plugin).toString()}`, { headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error('Error al cargar los registros');
        const data = await res.json();
        state.total = data.total;
        renderFn(data.items || []);
        renderB3Pagination(key);
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="8" class="text-center py-3 text-danger"><i class="bi bi-exclamation-circle me-1"></i> ${err.message}</td></tr>`;
    }
}

function renderB3Pagination(key) {
    const state = B3_STATE[key];
    const info = document.getElementById(`${key}-pagination-info`);
    const pageInfo = document.getElementById(`${key}-page-info`);
    const prevBtn = document.getElementById(`${key}-prev-page`);
    const nextBtn = document.getElementById(`${key}-next-page`);
    if (!info) return;
    const start = state.total === 0 ? 0 : (state.page - 1) * state.limit + 1;
    const end = Math.min(state.page * state.limit, state.total);
    const maxPages = Math.ceil(state.total / state.limit) || 1;
    info.textContent = `Mostrando ${start}–${end} de ${state.total}`;
    if (pageInfo) pageInfo.textContent = `Página ${state.page} de ${maxPages}`;
    if (prevBtn) prevBtn.disabled = (state.page <= 1);
    if (nextBtn) nextBtn.disabled = (state.page >= maxPages);
}

// ---------------------------------------------------------------------------
// Render de tablas
// ---------------------------------------------------------------------------

function renderMotivosTable(items) {
    const tbody = document.getElementById('motivos-table-body');
    if (!tbody) return;
    if (items.length === 0) { tbody.innerHTML = b3EmptyRow('No se encontraron motivos de merma.', 4); return; }
    tbody.innerHTML = items.map(m => `
        <tr>
            <td><span class="font-monospace text-muted small">#${m.id_motivo}</span></td>
            <td><strong class="text-dark">${m.descripcion}</strong></td>
            <td>${b3StatusBadge(m.estado)}</td>
            <td class="text-end">${b3ActionButtons('motivos', m.id_motivo, m.descripcion, m.estado)}</td>
        </tr>`).join('');
}

function renderMetodosTable(items) {
    const tbody = document.getElementById('metodos-table-body');
    if (!tbody) return;
    if (items.length === 0) { tbody.innerHTML = b3EmptyRow('No se encontraron métodos de pago.', 4); return; }
    tbody.innerHTML = items.map(m => `
        <tr>
            <td><span class="font-monospace text-muted small">#${m.id_metodo_pago}</span></td>
            <td><strong class="text-dark">${m.nombre}</strong></td>
            <td>${b3StatusBadge(m.estado)}</td>
            <td class="text-end">${b3ActionButtons('metodos', m.id_metodo_pago, m.nombre, m.estado)}</td>
        </tr>`).join('');
}

function renderProveedoresTable(items) {
    const tbody = document.getElementById('proveedores-table-body');
    if (!tbody) return;
    if (items.length === 0) { tbody.innerHTML = b3EmptyRow('No se encontraron proveedores.', 7); return; }
    tbody.innerHTML = items.map(p => `
        <tr>
            <td><span class="font-monospace text-muted small">#${p.id_proveedor}</span></td>
            <td><strong class="text-dark">${p.distribuidora}</strong></td>
            <td>${p.nombre_contacto}</td>
            <td>${p.telefono || '-'}</td>
            <td>${b3StatusBadge(p.estado)}</td>
            <td>${formatDate(p.fecha_creacion)}</td>
            <td class="text-end">${b3ActionButtons('proveedores', p.id_proveedor, p.distribuidora, p.estado)}</td>
        </tr>`).join('');
}

function renderDepartamentosTable(items) {
    const tbody = document.getElementById('departamentos-table-body');
    if (!tbody) return;
    if (items.length === 0) { tbody.innerHTML = b3EmptyRow('No se encontraron departamentos.', 5); return; }
    tbody.innerHTML = items.map(d => `
        <tr>
            <td><span class="font-monospace text-muted small">#${d.id_departamento}</span></td>
            <td><strong class="text-dark">${d.nombre}</strong></td>
            <td><span class="badge bg-secondary-subtle text-secondary">${d.total_municipios || 0} municipios</span></td>
            <td>${b3StatusBadge(d.estado)}</td>
            <td class="text-end">${b3ActionButtons('departamentos', d.id_departamento, d.nombre, d.estado)}</td>
        </tr>`).join('');
}

function renderMunicipiosTable(items) {
    const tbody = document.getElementById('municipios-table-body');
    if (!tbody) return;
    if (items.length === 0) { tbody.innerHTML = b3EmptyRow('No se encontraron municipios.', 5); return; }
    tbody.innerHTML = items.map(m => `
        <tr>
            <td><span class="font-monospace text-muted small">#${m.id_municipio}</span></td>
            <td><span class="badge bg-secondary-subtle text-secondary">${m.departamento_nombre || m.id_departamento}</span></td>
            <td><strong class="text-dark">${m.nombre}</strong></td>
            <td>${b3StatusBadge(m.estado)}</td>
            <td class="text-end">${b3ActionButtons('municipios', m.id_municipio, m.nombre, m.estado)}</td>
        </tr>`).join('');
}

const RENDER_B3 = {
    motivos: renderMotivosTable,
    metodos: renderMetodosTable,
    proveedores: renderProveedoresTable,
    departamentos: renderDepartamentosTable,
    municipios: renderMunicipiosTable,
};

// ---------------------------------------------------------------------------
// Acciones genéricas: detalle, edición, toggle de estado
// ---------------------------------------------------------------------------

function openB3Detail(key, id) {
    const map = {
        motivos: openMotivoDetailModal,
        metodos: openMetodoDetailModal,
        proveedores: openProveedorDetailModal,
        departamentos: openDepartamentoDetailModal,
        municipios: openMunicipioDetailModal,
    };
    if (map[key]) map[key](id);
}

function openB3Edit(key, id) {
    const map = {
        motivos: openEditMotivoModal,
        metodos: openEditMetodoModal,
        proveedores: openEditProveedorModal,
        departamentos: openEditDepartamentoModal,
        municipios: openEditMunicipioModal,
    };
    if (map[key]) map[key](id);
}

function toggleB3Status(key, id, name, status) {
    if (status === 'Activo') {
        B3_STATE[key].pending = { id, name };
        const sing = B3_CONFIG[key].singular;
        const text = document.getElementById(`confirm-${sing}-deactivate-text`);
        if (text) text.innerHTML = `¿Está seguro de desactivar el ${B3_CONFIG[key].label} <strong>${name}</strong>?`;
        const modalEl = document.getElementById(`confirm-${sing}-deactivate-modal`);
        if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();
    } else {
        activateB3(key, id, name);
    }
}

async function confirmB3Deactivate(key) {
    const pending = B3_STATE[key].pending;
    if (!pending) return;
    const plural = B3_CONFIG[key].plural;
    const sing = B3_CONFIG[key].singular;
    try {
        const res = await fetch(`${CATALOGOS_API}/${plural}/${pending.id}`, { method: 'DELETE', headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error(await readCatalogError(res, `Error al desactivar el ${B3_CONFIG[key].label}`));
        showToast(`${B3_CONFIG[key].label} '${pending.name}' desactivado exitosamente.`, 'info');
        const modalEl = document.getElementById(`confirm-${sing}-deactivate-modal`);
        if (modalEl) bootstrap.Modal.getInstance(modalEl).hide();
        loadB3Table(key, `${key}-table-body`, RENDER_B3[key]);
    } catch (err) {
        showToast(err.message, 'danger');
        const modalEl = document.getElementById(`confirm-${sing}-deactivate-modal`);
        if (modalEl) bootstrap.Modal.getInstance(modalEl).hide();
    }
}

async function activateB3(key, id, name) {
    const plural = B3_CONFIG[key].plural;
    try {
        const res = await fetch(`${CATALOGOS_API}/${plural}/${id}/activar`, { method: 'POST', headers: getCatalogAuthHeaders() });
        if (!res.ok) throw new Error(await readCatalogError(res, `Error al reactivar el ${B3_CONFIG[key].label}`));
        showToast(`${B3_CONFIG[key].label} '${name}' reactivado exitosamente.`, 'success');
        loadB3Table(key, `${key}-table-body`, RENDER_B3[key]);
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ---------------------------------------------------------------------------
// Helpers comunes de modales
// ---------------------------------------------------------------------------

function showB3Modal(id) {
    const modalEl = document.getElementById(id);
    if (modalEl) bootstrap.Modal.getOrCreateInstance(modalEl, { backdrop: 'static', keyboard: false }).show();
}

function hideB3Modal(id) {
    const modalEl = document.getElementById(id);
    if (modalEl && bootstrap.Modal.getInstance(modalEl)) bootstrap.Modal.getInstance(modalEl).hide();
}

function loadB3DetailInto(id, innerHtml) {
    const body = document.getElementById(id);
    if (body) body.innerHTML = innerHtml;
}

function b3DetailRow(label, value) {
    return `<div class="col-sm-6"><span class="text-muted small d-block">${label}</span><strong class="fs-6">${value}</strong></div>`;
}

async function fetchB3One(plural, id) {
    const res = await fetch(`${CATALOGOS_API}/${plural}/${id}`, { headers: getCatalogAuthHeaders() });
    if (!res.ok) throw new Error('No se pudo cargar el registro');
    return res.json();
}

// ---------------------------------------------------------------------------
// MOTIVOS DE MERMA
// ---------------------------------------------------------------------------

function openNewMotivoModal() {
    const title = document.getElementById('motivoModalTitle');
    if (title) title.textContent = 'Nuevo Motivo de Merma';
    const form = document.getElementById('motivo-form');
    if (form) form.reset();
    document.getElementById('motivo-id').value = '';
    showB3Modal('motivo-modal');
}

async function openEditMotivoModal(id) {
    const title = document.getElementById('motivoModalTitle');
    if (title) title.textContent = 'Editar Motivo de Merma';
    try {
        const m = await fetchB3One('motivos-merma', id);
        document.getElementById('motivo-id').value = m.id_motivo;
        document.getElementById('motivo-descripcion').value = m.descripcion;
        showB3Modal('motivo-modal');
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function handleSaveMotivo(e) {
    e.preventDefault();
    const id = document.getElementById('motivo-id').value;
    const descripcion = document.getElementById('motivo-descripcion').value.trim();
    if (!descripcion) { showToast('La descripción es obligatoria.', 'warning'); return; }
    const isEdit = Boolean(id);
    const url = isEdit ? `${CATALOGOS_API}/motivos-merma/${id}` : `${CATALOGOS_API}/motivos-merma`;
    try {
        const res = await fetch(url, { method: isEdit ? 'PUT' : 'POST', headers: getCatalogAuthHeaders(), body: JSON.stringify({ descripcion }) });
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Error al guardar el motivo'); }
        showToast(`Motivo '${descripcion}' ${isEdit ? 'actualizado' : 'creado'} con éxito.`, 'success');
        hideB3Modal('motivo-modal');
        loadB3Table('motivos', 'motivos-table-body', renderMotivosTable);
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function openMotivoDetailModal(id) {
    loadB3DetailInto('motivo-detail-body', '<div class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Cargando ficha...</div>');
    showB3Modal('motivo-detail-modal');
    try {
        const m = await fetchB3One('motivos-merma', id);
        loadB3DetailInto('motivo-detail-body', `
            <div class="row g-3">
                ${b3DetailRow('ID de Motivo', `#${m.id_motivo}`)}
                ${b3DetailRow('Estado', b3StatusBadge(m.estado))}
                ${b3DetailRow('Descripción', m.descripcion)}
            </div>`);
    } catch (err) {
        loadB3DetailInto('motivo-detail-body', `<div class="text-center text-danger py-4">${err.message}</div>`);
    }
}

// ---------------------------------------------------------------------------
// MÉTODOS DE PAGO
// ---------------------------------------------------------------------------

function openNewMetodoModal() {
    const title = document.getElementById('metodoModalTitle');
    if (title) title.textContent = 'Nuevo Método de Pago';
    const form = document.getElementById('metodo-form');
    if (form) form.reset();
    document.getElementById('metodo-id').value = '';
    showB3Modal('metodo-modal');
}

async function openEditMetodoModal(id) {
    const title = document.getElementById('metodoModalTitle');
    if (title) title.textContent = 'Editar Método de Pago';
    try {
        const m = await fetchB3One('metodos-pago', id);
        document.getElementById('metodo-id').value = m.id_metodo_pago;
        document.getElementById('metodo-nombre').value = m.nombre;
        showB3Modal('metodo-modal');
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function handleSaveMetodo(e) {
    e.preventDefault();
    const id = document.getElementById('metodo-id').value;
    const nombre = document.getElementById('metodo-nombre').value.trim();
    if (!nombre) { showToast('El nombre es obligatorio.', 'warning'); return; }
    const isEdit = Boolean(id);
    const url = isEdit ? `${CATALOGOS_API}/metodos-pago/${id}` : `${CATALOGOS_API}/metodos-pago`;
    try {
        const res = await fetch(url, { method: isEdit ? 'PUT' : 'POST', headers: getCatalogAuthHeaders(), body: JSON.stringify({ nombre }) });
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Error al guardar el método'); }
        showToast(`Método '${nombre}' ${isEdit ? 'actualizado' : 'creado'} con éxito.`, 'success');
        hideB3Modal('metodo-modal');
        loadB3Table('metodos', 'metodos-table-body', renderMetodosTable);
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function openMetodoDetailModal(id) {
    loadB3DetailInto('metodo-detail-body', '<div class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Cargando ficha...</div>');
    showB3Modal('metodo-detail-modal');
    try {
        const m = await fetchB3One('metodos-pago', id);
        loadB3DetailInto('metodo-detail-body', `
            <div class="row g-3">
                ${b3DetailRow('ID de Método', `#${m.id_metodo_pago}`)}
                ${b3DetailRow('Estado', b3StatusBadge(m.estado))}
                ${b3DetailRow('Nombre', m.nombre)}
            </div>`);
    } catch (err) {
        loadB3DetailInto('metodo-detail-body', `<div class="text-center text-danger py-4">${err.message}</div>`);
    }
}

// ---------------------------------------------------------------------------
// PROVEEDORES
// ---------------------------------------------------------------------------

function openNewProveedorModal() {
    const title = document.getElementById('proveedorModalTitle');
    if (title) title.textContent = 'Nuevo Proveedor';
    const form = document.getElementById('proveedor-form');
    if (form) form.reset();
    document.getElementById('proveedor-id').value = '';
    showB3Modal('proveedor-modal');
}

async function openEditProveedorModal(id) {
    const title = document.getElementById('proveedorModalTitle');
    if (title) title.textContent = 'Editar Proveedor';
    try {
        const p = await fetchB3One('proveedores', id);
        document.getElementById('proveedor-id').value = p.id_proveedor;
        document.getElementById('proveedor-distribuidora').value = p.distribuidora;
        document.getElementById('proveedor-nombre-contacto').value = p.nombre_contacto;
        document.getElementById('proveedor-telefono').value = p.telefono || '';
        document.getElementById('proveedor-correo').value = p.correo || '';
        document.getElementById('proveedor-cuenta').value = p.cuenta_bancaria || '';
        document.getElementById('proveedor-direccion').value = p.direccion || '';
        showB3Modal('proveedor-modal');
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function handleSaveProveedor(e) {
    e.preventDefault();
    const id = document.getElementById('proveedor-id').value;
    const distribuidora = document.getElementById('proveedor-distribuidora').value.trim();
    const nombre_contacto = document.getElementById('proveedor-nombre-contacto').value.trim();
    if (!distribuidora || !nombre_contacto) { showToast('Complete los campos obligatorios.', 'warning'); return; }
    const payload = {
        distribuidora,
        nombre_contacto,
        telefono: document.getElementById('proveedor-telefono').value.trim() || null,
        correo: document.getElementById('proveedor-correo').value.trim() || null,
        cuenta_bancaria: document.getElementById('proveedor-cuenta').value.trim() || null,
        direccion: document.getElementById('proveedor-direccion').value.trim() || null,
    };
    const isEdit = Boolean(id);
    const url = isEdit ? `${CATALOGOS_API}/proveedores/${id}` : `${CATALOGOS_API}/proveedores`;
    try {
        const res = await fetch(url, { method: isEdit ? 'PUT' : 'POST', headers: getCatalogAuthHeaders(), body: JSON.stringify(payload) });
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Error al guardar el proveedor'); }
        showToast(`Proveedor '${distribuidora}' ${isEdit ? 'actualizado' : 'creado'} con éxito.`, 'success');
        hideB3Modal('proveedor-modal');
        loadB3Table('proveedores', 'proveedores-table-body', renderProveedoresTable);
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function openProveedorDetailModal(id) {
    loadB3DetailInto('proveedor-detail-body', '<div class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Cargando ficha...</div>');
    showB3Modal('proveedor-detail-modal');
    try {
        const p = await fetchB3One('proveedores', id);
        loadB3DetailInto('proveedor-detail-body', `
            <div class="row g-3">
                ${b3DetailRow('ID de Proveedor', `#${p.id_proveedor}`)}
                ${b3DetailRow('Estado', b3StatusBadge(p.estado))}
                ${b3DetailRow('Distribuidora', p.distribuidora)}
                ${b3DetailRow('Contacto', p.nombre_contacto)}
                ${b3DetailRow('Teléfono', p.telefono || '—')}
                ${b3DetailRow('Correo', p.correo || '—')}
                ${b3DetailRow('Cuenta Bancaria', p.cuenta_bancaria || '—')}
                ${b3DetailRow('Dirección', p.direccion || '—')}
                ${b3DetailRow('Fecha de Registro', formatDate(p.fecha_creacion))}
            </div>`);
    } catch (err) {
        loadB3DetailInto('proveedor-detail-body', `<div class="text-center text-danger py-4">${err.message}</div>`);
    }
}

// ---------------------------------------------------------------------------
// DEPARTAMENTOS
// ---------------------------------------------------------------------------

function openNewDepartamentoModal() {
    const title = document.getElementById('departamentoModalTitle');
    if (title) title.textContent = 'Nuevo Departamento';
    const form = document.getElementById('departamento-form');
    if (form) form.reset();
    document.getElementById('departamento-id').value = '';
    showB3Modal('departamento-modal');
}

async function openEditDepartamentoModal(id) {
    const title = document.getElementById('departamentoModalTitle');
    if (title) title.textContent = 'Editar Departamento';
    try {
        const d = await fetchB3One('departamentos', id);
        document.getElementById('departamento-id').value = d.id_departamento;
        document.getElementById('departamento-nombre').value = d.nombre;
        showB3Modal('departamento-modal');
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function handleSaveDepartamento(e) {
    e.preventDefault();
    const id = document.getElementById('departamento-id').value;
    const nombre = document.getElementById('departamento-nombre').value.trim();
    if (!nombre) { showToast('El nombre es obligatorio.', 'warning'); return; }
    const isEdit = Boolean(id);
    const url = isEdit ? `${CATALOGOS_API}/departamentos/${id}` : `${CATALOGOS_API}/departamentos`;
    try {
        const res = await fetch(url, { method: isEdit ? 'PUT' : 'POST', headers: getCatalogAuthHeaders(), body: JSON.stringify({ nombre }) });
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Error al guardar el departamento'); }
        showToast(`Departamento '${nombre}' ${isEdit ? 'actualizado' : 'creado'} con éxito.`, 'success');
        hideB3Modal('departamento-modal');
        loadB3Table('departamentos', 'departamentos-table-body', renderDepartamentosTable);
        populateB3Departamentos();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function openDepartamentoDetailModal(id) {
    loadB3DetailInto('departamento-detail-body', '<div class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Cargando ficha...</div>');
    showB3Modal('departamento-detail-modal');
    try {
        const d = await fetchB3One('departamentos', id);
        loadB3DetailInto('departamento-detail-body', `
            <div class="row g-3">
                ${b3DetailRow('ID de Departamento', `#${d.id_departamento}`)}
                ${b3DetailRow('Estado', b3StatusBadge(d.estado))}
                ${b3DetailRow('Nombre', d.nombre)}
                ${b3DetailRow('N° Municipios', d.total_municipios || 0)}
            </div>`);
    } catch (err) {
        loadB3DetailInto('departamento-detail-body', `<div class="text-center text-danger py-4">${err.message}</div>`);
    }
}

// ---------------------------------------------------------------------------
// MUNICIPIOS (dropdown dependiente departamento -> municipio)
// ---------------------------------------------------------------------------

async function populateB3Departamentos() {
    const filterSelect = document.getElementById('filter-municipio-departamento');
    const formSelect = document.getElementById('municipio-departamento-id');
    try {
        const res = await fetch(`${CATALOGOS_API}/departamentos?include_inactive=false`, { headers: getCatalogAuthHeaders() });
        if (res.ok) {
            const deps = await res.json();
            if (filterSelect) {
                const current = filterSelect.value;
                filterSelect.innerHTML = '<option value="">Todos los departamentos</option>' +
                    deps.map(d => `<option value="${d.id_departamento}">${d.nombre}</option>`).join('');
                filterSelect.value = current;
            }
            if (formSelect) {
                formSelect.innerHTML = '<option value="">Seleccione departamento...</option>' +
                    deps.map(d => `<option value="${d.id_departamento}">${d.nombre}</option>`).join('');
            }
        }
    } catch (err) {
        console.warn('Error al cargar departamentos en combos de municipios:', err);
    }
}

function openNewMunicipioModal() {
    const title = document.getElementById('municipioModalTitle');
    if (title) title.textContent = 'Nuevo Municipio';
    const form = document.getElementById('municipio-form');
    if (form) form.reset();
    document.getElementById('municipio-id').value = '';
    populateB3Departamentos();
    showB3Modal('municipio-modal');
}

async function openEditMunicipioModal(id) {
    const title = document.getElementById('municipioModalTitle');
    if (title) title.textContent = 'Editar Municipio';
    try {
        const m = await fetchB3One('municipios', id);
        await populateB3Departamentos();
        document.getElementById('municipio-id').value = m.id_municipio;
        document.getElementById('municipio-departamento-id').value = String(m.id_departamento);
        document.getElementById('municipio-nombre').value = m.nombre;
        showB3Modal('municipio-modal');
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function handleSaveMunicipio(e) {
    e.preventDefault();
    const id = document.getElementById('municipio-id').value;
    const idDepartamento = document.getElementById('municipio-departamento-id').value;
    const nombre = document.getElementById('municipio-nombre').value.trim();
    if (!idDepartamento || !nombre) { showToast('Complete los campos obligatorios.', 'warning'); return; }
    const payload = { id_departamento: Number(idDepartamento), nombre };
    const isEdit = Boolean(id);
    const url = isEdit ? `${CATALOGOS_API}/municipios/${id}` : `${CATALOGOS_API}/municipios`;
    try {
        const res = await fetch(url, { method: isEdit ? 'PUT' : 'POST', headers: getCatalogAuthHeaders(), body: JSON.stringify(payload) });
        if (!res.ok) { const err = await res.json(); throw new Error(err.detail || 'Error al guardar el municipio'); }
        showToast(`Municipio '${nombre}' ${isEdit ? 'actualizado' : 'creado'} con éxito.`, 'success');
        hideB3Modal('municipio-modal');
        loadB3Table('municipios', 'municipios-table-body', renderMunicipiosTable);
        loadB3Table('departamentos', 'departamentos-table-body', renderDepartamentosTable);
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function openMunicipioDetailModal(id) {
    loadB3DetailInto('municipio-detail-body', '<div class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-1"></span> Cargando ficha...</div>');
    showB3Modal('municipio-detail-modal');
    try {
        const m = await fetchB3One('municipios', id);
        loadB3DetailInto('municipio-detail-body', `
            <div class="row g-3">
                ${b3DetailRow('ID de Municipio', `#${m.id_municipio}`)}
                ${b3DetailRow('Estado', b3StatusBadge(m.estado))}
                ${b3DetailRow('Departamento', m.departamento_nombre || m.id_departamento)}
                ${b3DetailRow('Nombre', m.nombre)}
            </div>`);
    } catch (err) {
        loadB3DetailInto('municipio-detail-body', `<div class="text-center text-danger py-4">${err.message}</div>`);
    }
}

// ---------------------------------------------------------------------------
// Listeners del Bloque 3
// ---------------------------------------------------------------------------

function initBloque3Listeners() {
    // Motivos
    const btnNewMotivo = document.getElementById('btn-new-motivo');
    if (btnNewMotivo) btnNewMotivo.addEventListener('click', openNewMotivoModal);
    const motivoForm = document.getElementById('motivo-form');
    if (motivoForm) motivoForm.addEventListener('submit', handleSaveMotivo);
    const btnConfirmMotivo = document.getElementById('btn-confirm-motivo-deactivate');
    if (btnConfirmMotivo) btnConfirmMotivo.addEventListener('click', () => confirmB3Deactivate('motivos'));
    const btnFilterMotivo = document.getElementById('btn-filter-motivo');
    if (btnFilterMotivo) btnFilterMotivo.addEventListener('click', () => {
        B3_STATE.motivos.page = 1;
        B3_STATE.motivos.search = document.getElementById('filter-motivo-search')?.value.trim() || '';
        B3_STATE.motivos.status = document.getElementById('filter-motivo-status')?.value || '';
        loadB3Table('motivos', 'motivos-table-body', renderMotivosTable);
    });
    const btnResetMotivo = document.getElementById('btn-reset-motivo');
    if (btnResetMotivo) btnResetMotivo.addEventListener('click', () => {
        B3_STATE.motivos.page = 1; B3_STATE.motivos.search = ''; B3_STATE.motivos.status = '';
        if (document.getElementById('filter-motivo-search')) document.getElementById('filter-motivo-search').value = '';
        if (document.getElementById('filter-motivo-status')) document.getElementById('filter-motivo-status').value = '';
        loadB3Table('motivos', 'motivos-table-body', renderMotivosTable);
    });
    const motivoPrev = document.getElementById('motivo-prev-page');
    if (motivoPrev) motivoPrev.addEventListener('click', () => {
        if (B3_STATE.motivos.page > 1) { B3_STATE.motivos.page--; loadB3Table('motivos', 'motivos-table-body', renderMotivosTable); }
    });
    const motivoNext = document.getElementById('motivo-next-page');
    if (motivoNext) motivoNext.addEventListener('click', () => {
        const maxPages = Math.ceil(B3_STATE.motivos.total / B3_STATE.motivos.limit) || 1;
        if (B3_STATE.motivos.page < maxPages) { B3_STATE.motivos.page++; loadB3Table('motivos', 'motivos-table-body', renderMotivosTable); }
    });
    document.querySelectorAll('[data-motivo-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-motivo-sort');
            B3_STATE.motivos.sortOrder = (B3_STATE.motivos.sortBy === col && B3_STATE.motivos.sortOrder === 'asc') ? 'desc' : 'asc';
            B3_STATE.motivos.sortBy = col;
            loadB3Table('motivos', 'motivos-table-body', renderMotivosTable);
        });
    });
    document.getElementById('btn-export-motivos-excel')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/motivos-merma/export?format=excel`, 'motivos_merma.xlsx');
    });
    document.getElementById('btn-export-motivos-csv')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/motivos-merma/export?format=csv`, 'motivos_merma.csv');
    });

    // Métodos de pago
    const btnNewMetodo = document.getElementById('btn-new-metodo');
    if (btnNewMetodo) btnNewMetodo.addEventListener('click', openNewMetodoModal);
    const metodoForm = document.getElementById('metodo-form');
    if (metodoForm) metodoForm.addEventListener('submit', handleSaveMetodo);
    const btnConfirmMetodo = document.getElementById('btn-confirm-metodo-deactivate');
    if (btnConfirmMetodo) btnConfirmMetodo.addEventListener('click', () => confirmB3Deactivate('metodos'));
    const btnFilterMetodo = document.getElementById('btn-filter-metodo');
    if (btnFilterMetodo) btnFilterMetodo.addEventListener('click', () => {
        B3_STATE.metodos.page = 1;
        B3_STATE.metodos.search = document.getElementById('filter-metodo-search')?.value.trim() || '';
        B3_STATE.metodos.status = document.getElementById('filter-metodo-status')?.value || '';
        loadB3Table('metodos', 'metodos-table-body', renderMetodosTable);
    });
    const btnResetMetodo = document.getElementById('btn-reset-metodo');
    if (btnResetMetodo) btnResetMetodo.addEventListener('click', () => {
        B3_STATE.metodos.page = 1; B3_STATE.metodos.search = ''; B3_STATE.metodos.status = '';
        if (document.getElementById('filter-metodo-search')) document.getElementById('filter-metodo-search').value = '';
        if (document.getElementById('filter-metodo-status')) document.getElementById('filter-metodo-status').value = '';
        loadB3Table('metodos', 'metodos-table-body', renderMetodosTable);
    });
    const metodoPrev = document.getElementById('metodo-prev-page');
    if (metodoPrev) metodoPrev.addEventListener('click', () => {
        if (B3_STATE.metodos.page > 1) { B3_STATE.metodos.page--; loadB3Table('metodos', 'metodos-table-body', renderMetodosTable); }
    });
    const metodoNext = document.getElementById('metodo-next-page');
    if (metodoNext) metodoNext.addEventListener('click', () => {
        const maxPages = Math.ceil(B3_STATE.metodos.total / B3_STATE.metodos.limit) || 1;
        if (B3_STATE.metodos.page < maxPages) { B3_STATE.metodos.page++; loadB3Table('metodos', 'metodos-table-body', renderMetodosTable); }
    });
    document.querySelectorAll('[data-metodo-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-metodo-sort');
            B3_STATE.metodos.sortOrder = (B3_STATE.metodos.sortBy === col && B3_STATE.metodos.sortOrder === 'asc') ? 'desc' : 'asc';
            B3_STATE.metodos.sortBy = col;
            loadB3Table('metodos', 'metodos-table-body', renderMetodosTable);
        });
    });
    document.getElementById('btn-export-metodos-excel')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/metodos-pago/export?format=excel`, 'metodos_pago.xlsx');
    });
    document.getElementById('btn-export-metodos-csv')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/metodos-pago/export?format=csv`, 'metodos_pago.csv');
    });

    // Proveedores
    const btnNewProveedor = document.getElementById('btn-new-proveedor');
    if (btnNewProveedor) btnNewProveedor.addEventListener('click', openNewProveedorModal);
    const proveedorForm = document.getElementById('proveedor-form');
    if (proveedorForm) proveedorForm.addEventListener('submit', handleSaveProveedor);
    const btnConfirmProveedor = document.getElementById('btn-confirm-proveedor-deactivate');
    if (btnConfirmProveedor) btnConfirmProveedor.addEventListener('click', () => confirmB3Deactivate('proveedores'));
    const btnFilterProveedor = document.getElementById('btn-filter-proveedor');
    if (btnFilterProveedor) btnFilterProveedor.addEventListener('click', () => {
        B3_STATE.proveedores.page = 1;
        B3_STATE.proveedores.search = document.getElementById('filter-proveedor-search')?.value.trim() || '';
        B3_STATE.proveedores.status = document.getElementById('filter-proveedor-status')?.value || '';
        B3_STATE.proveedores.fecha_desde = document.getElementById('filter-proveedor-from')?.value || '';
        B3_STATE.proveedores.fecha_hasta = document.getElementById('filter-proveedor-to')?.value || '';
        loadB3Table('proveedores', 'proveedores-table-body', renderProveedoresTable);
    });
    const btnResetProveedor = document.getElementById('btn-reset-proveedor');
    if (btnResetProveedor) btnResetProveedor.addEventListener('click', () => {
        B3_STATE.proveedores.page = 1; B3_STATE.proveedores.search = ''; B3_STATE.proveedores.status = '';
        B3_STATE.proveedores.fecha_desde = ''; B3_STATE.proveedores.fecha_hasta = '';
        if (document.getElementById('filter-proveedor-search')) document.getElementById('filter-proveedor-search').value = '';
        if (document.getElementById('filter-proveedor-status')) document.getElementById('filter-proveedor-status').value = '';
        if (document.getElementById('filter-proveedor-from')) document.getElementById('filter-proveedor-from').value = '';
        if (document.getElementById('filter-proveedor-to')) document.getElementById('filter-proveedor-to').value = '';
        loadB3Table('proveedores', 'proveedores-table-body', renderProveedoresTable);
    });
    const provPrev = document.getElementById('proveedor-prev-page');
    if (provPrev) provPrev.addEventListener('click', () => {
        if (B3_STATE.proveedores.page > 1) { B3_STATE.proveedores.page--; loadB3Table('proveedores', 'proveedores-table-body', renderProveedoresTable); }
    });
    const provNext = document.getElementById('proveedor-next-page');
    if (provNext) provNext.addEventListener('click', () => {
        const maxPages = Math.ceil(B3_STATE.proveedores.total / B3_STATE.proveedores.limit) || 1;
        if (B3_STATE.proveedores.page < maxPages) { B3_STATE.proveedores.page++; loadB3Table('proveedores', 'proveedores-table-body', renderProveedoresTable); }
    });
    document.querySelectorAll('[data-proveedor-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-proveedor-sort');
            B3_STATE.proveedores.sortOrder = (B3_STATE.proveedores.sortBy === col && B3_STATE.proveedores.sortOrder === 'asc') ? 'desc' : 'asc';
            B3_STATE.proveedores.sortBy = col;
            loadB3Table('proveedores', 'proveedores-table-body', renderProveedoresTable);
        });
    });
    document.getElementById('btn-export-proveedores-excel')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/proveedores/export?format=excel`, 'proveedores.xlsx');
    });
    document.getElementById('btn-export-proveedores-csv')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/proveedores/export?format=csv`, 'proveedores.csv');
    });

    // Departamentos
    const btnNewDepartamento = document.getElementById('btn-new-departamento');
    if (btnNewDepartamento) btnNewDepartamento.addEventListener('click', openNewDepartamentoModal);
    const departamentoForm = document.getElementById('departamento-form');
    if (departamentoForm) departamentoForm.addEventListener('submit', handleSaveDepartamento);
    const btnConfirmDepartamento = document.getElementById('btn-confirm-departamento-deactivate');
    if (btnConfirmDepartamento) btnConfirmDepartamento.addEventListener('click', () => confirmB3Deactivate('departamentos'));
    const btnFilterDepartamento = document.getElementById('btn-filter-departamento');
    if (btnFilterDepartamento) btnFilterDepartamento.addEventListener('click', () => {
        B3_STATE.departamentos.page = 1;
        B3_STATE.departamentos.search = document.getElementById('filter-departamento-search')?.value.trim() || '';
        B3_STATE.departamentos.status = document.getElementById('filter-departamento-status')?.value || '';
        loadB3Table('departamentos', 'departamentos-table-body', renderDepartamentosTable);
    });
    const btnResetDepartamento = document.getElementById('btn-reset-departamento');
    if (btnResetDepartamento) btnResetDepartamento.addEventListener('click', () => {
        B3_STATE.departamentos.page = 1; B3_STATE.departamentos.search = ''; B3_STATE.departamentos.status = '';
        if (document.getElementById('filter-departamento-search')) document.getElementById('filter-departamento-search').value = '';
        if (document.getElementById('filter-departamento-status')) document.getElementById('filter-departamento-status').value = '';
        loadB3Table('departamentos', 'departamentos-table-body', renderDepartamentosTable);
    });
    const deptPrev = document.getElementById('departamento-prev-page');
    if (deptPrev) deptPrev.addEventListener('click', () => {
        if (B3_STATE.departamentos.page > 1) { B3_STATE.departamentos.page--; loadB3Table('departamentos', 'departamentos-table-body', renderDepartamentosTable); }
    });
    const deptNext = document.getElementById('departamento-next-page');
    if (deptNext) deptNext.addEventListener('click', () => {
        const maxPages = Math.ceil(B3_STATE.departamentos.total / B3_STATE.departamentos.limit) || 1;
        if (B3_STATE.departamentos.page < maxPages) { B3_STATE.departamentos.page++; loadB3Table('departamentos', 'departamentos-table-body', renderDepartamentosTable); }
    });
    document.querySelectorAll('[data-departamento-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-departamento-sort');
            B3_STATE.departamentos.sortOrder = (B3_STATE.departamentos.sortBy === col && B3_STATE.departamentos.sortOrder === 'asc') ? 'desc' : 'asc';
            B3_STATE.departamentos.sortBy = col;
            loadB3Table('departamentos', 'departamentos-table-body', renderDepartamentosTable);
        });
    });
    document.getElementById('btn-export-departamentos-excel')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/departamentos/export?format=excel`, 'departamentos.xlsx');
    });
    document.getElementById('btn-export-departamentos-csv')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/departamentos/export?format=csv`, 'departamentos.csv');
    });

    // Municipios
    const btnNewMunicipio = document.getElementById('btn-new-municipio');
    if (btnNewMunicipio) btnNewMunicipio.addEventListener('click', openNewMunicipioModal);
    const municipioForm = document.getElementById('municipio-form');
    if (municipioForm) municipioForm.addEventListener('submit', handleSaveMunicipio);
    const btnConfirmMunicipio = document.getElementById('btn-confirm-municipio-deactivate');
    if (btnConfirmMunicipio) btnConfirmMunicipio.addEventListener('click', () => confirmB3Deactivate('municipios'));
    const btnFilterMunicipio = document.getElementById('btn-filter-municipio');
    if (btnFilterMunicipio) btnFilterMunicipio.addEventListener('click', () => {
        B3_STATE.municipios.page = 1;
        B3_STATE.municipios.search = document.getElementById('filter-municipio-search')?.value.trim() || '';
        B3_STATE.municipios.id_departamento = document.getElementById('filter-municipio-departamento')?.value || '';
        B3_STATE.municipios.status = document.getElementById('filter-municipio-status')?.value || '';
        loadB3Table('municipios', 'municipios-table-body', renderMunicipiosTable);
    });
    const btnResetMunicipio = document.getElementById('btn-reset-municipio');
    if (btnResetMunicipio) btnResetMunicipio.addEventListener('click', () => {
        B3_STATE.municipios.page = 1; B3_STATE.municipios.search = ''; B3_STATE.municipios.id_departamento = ''; B3_STATE.municipios.status = '';
        if (document.getElementById('filter-municipio-search')) document.getElementById('filter-municipio-search').value = '';
        if (document.getElementById('filter-municipio-departamento')) document.getElementById('filter-municipio-departamento').value = '';
        if (document.getElementById('filter-municipio-status')) document.getElementById('filter-municipio-status').value = '';
        loadB3Table('municipios', 'municipios-table-body', renderMunicipiosTable);
    });
    const muniPrev = document.getElementById('municipio-prev-page');
    if (muniPrev) muniPrev.addEventListener('click', () => {
        if (B3_STATE.municipios.page > 1) { B3_STATE.municipios.page--; loadB3Table('municipios', 'municipios-table-body', renderMunicipiosTable); }
    });
    const muniNext = document.getElementById('municipio-next-page');
    if (muniNext) muniNext.addEventListener('click', () => {
        const maxPages = Math.ceil(B3_STATE.municipios.total / B3_STATE.municipios.limit) || 1;
        if (B3_STATE.municipios.page < maxPages) { B3_STATE.municipios.page++; loadB3Table('municipios', 'municipios-table-body', renderMunicipiosTable); }
    });
    document.querySelectorAll('[data-municipio-sort]').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-municipio-sort');
            B3_STATE.municipios.sortOrder = (B3_STATE.municipios.sortBy === col && B3_STATE.municipios.sortOrder === 'asc') ? 'desc' : 'asc';
            B3_STATE.municipios.sortBy = col;
            loadB3Table('municipios', 'municipios-table-body', renderMunicipiosTable);
        });
    });
    document.getElementById('btn-export-municipios-excel')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/municipios/export?format=excel`, 'municipios.xlsx');
    });
    document.getElementById('btn-export-municipios-csv')?.addEventListener('click', () => {
        downloadCatalogExport(`${CATALOGOS_API}/municipios/export?format=csv`, 'municipios.csv');
    });
}

function initBloque3Tables() {
    loadB3Table('motivos', 'motivos-table-body', renderMotivosTable);
    loadB3Table('metodos', 'metodos-table-body', renderMetodosTable);
    loadB3Table('proveedores', 'proveedores-table-body', renderProveedoresTable);
    loadB3Table('departamentos', 'departamentos-table-body', renderDepartamentosTable);
    loadB3Table('municipios', 'municipios-table-body', renderMunicipiosTable);
    populateB3Departamentos();
}

document.addEventListener('DOMContentLoaded', () => {
    initBloque3Listeners();
});
