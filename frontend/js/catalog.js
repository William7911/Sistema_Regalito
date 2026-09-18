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
            tbody.innerHTML = filtered.map((c) => `
                <tr>
                    <td>${c.nombre}</td>
                    <td>-</td>
                    <td><span class="badge ${c.estado === 'Activo' ? 'bg-success' : 'bg-secondary'}">${c.estado === 'Activo' ? 'Activo' : 'Inactivo'}</span></td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-rosado" onclick="editCategory(${c.id_categoria})" title="Editar"><i class="bi bi-pencil"></i></button>
                        ${c.estado === 'Activo' ? `<button class="btn btn-sm btn-outline-danger" onclick="deactivateCategory(${c.id_categoria})" title="Desactivar"><i class="bi bi-x-circle"></i></button>` : ''}
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
    const from = document.getElementById('filter-product-from')?.value || '';
    const to = document.getElementById('filter-product-to')?.value || '';

    if (name) params.append('name', name);
    if (barcode) params.append('barcode', barcode);
    if (subcat) params.append('subcategoria_id', subcat);
    if (from) params.append('created_from', from);
    if (to) params.append('created_to', to);

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
                return `
                <tr>
                    <td>${p.id_producto}</td>
                    <td>${p.nombre}</td>
                    <td>${sub}</td>
                    <td>Q ${precio}</td>
                    <td><span class="badge ${stock <= minStock ? 'bg-danger' : 'bg-success'}">${stock}</span></td>
                    <td><span class="badge ${activo ? 'bg-success' : 'bg-secondary'}">${activo ? 'Activo' : 'Inactivo'}</span></td>
                    <td>${fecha}</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-info" onclick="viewProductDetail(${p.id_producto})" title="Ver detalle"><i class="bi bi-eye"></i></button>
                        <button class="btn btn-sm btn-outline-rosado" onclick="editProduct(${p.id_producto})" title="Editar"><i class="bi bi-pencil"></i></button>
                        ${activo ? `<button class="btn btn-sm btn-outline-danger" onclick="deactivateProduct(${p.id_producto})" title="Desactivar"><i class="bi bi-x-circle"></i></button>` : ''}
                    </td>
                </tr>
            `;
            }).join('');
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
        document.getElementById('pdetail-talla').textContent = variante ? (variante.talla || '-') : '-';
        document.getElementById('pdetail-color').textContent = variante ? (variante.color || '-') : '-';
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
// Formulario / Modal de Producto
// ---------------------------------------------------------------------------

async function resetProductForm() {
    clearCatalogErrors('product-form');
    const form = document.getElementById('product-form');
    if (form) form.reset();
    inputFor('product-form', 'product-id').value = '';
    inputFor('product-form', 'variante-id').value = '';
    inputFor('product-form', 'inventario-id').value = '';
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
        inputFor('product-form', 'codigo_barras').value = variante ? (variante.codigo_barras || '') : '';
        inputFor('product-form', 'talla').value = variante ? (variante.talla || '') : '';
        inputFor('product-form', 'color').value = variante ? (variante.color || '') : '';
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
    if (rawStock === '' || rawStock === null || rawStock === undefined) {
        applyFieldError('stock_actual', 'Este campo es obligatorio.');
    } else {
        const numStock = parseInt(rawStock, 10);
        if (isNaN(numStock) || numStock < 0) {
            applyFieldError('stock_actual', 'El stock inicial debe ser 0 o superior.');
        }
    }

    // 9. Stock Mínimo (PROBLEMA 2 - Cero fallback destructivo, obligatorio)
    if (rawStockMin === '' || rawStockMin === null || rawStockMin === undefined) {
        applyFieldError('stock_minimo', 'Este campo es obligatorio.');
    } else {
        const numStockMin = parseInt(rawStockMin, 10);
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
        variante: {
            codigo_barras: inputFor(formId, 'codigo_barras')?.value?.trim() || null,
            talla: inputFor(formId, 'talla')?.value?.trim() || null,
            color: inputFor(formId, 'color')?.value?.trim() || null,
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
    ]);
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
});