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
        const msg = translateValidation(err.msg || 'Valor inválido');
        const input = field ? inputFor(formId, field) : null;
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

// Limpieza en tiempo real (micro-interacción).
function initCatalogRealtimeValidation(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    form.querySelectorAll('.form-control, .form-select').forEach((el) => {
        el.addEventListener('input', () => clearCatalogFieldError(formId, el));
        el.addEventListener('change', () => clearCatalogFieldError(formId, el));
    });
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
    const nameFilter = document.getElementById('filter-category-name').value.trim();
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
    const params = new URLSearchParams();
    const name = document.getElementById('filter-product-name').value.trim();
    const barcode = document.getElementById('filter-product-barcode').value.trim();
    const subcat = document.getElementById('filter-product-subcategoria').value;
    if (name) params.append('name', name);
    if (barcode) params.append('barcode', barcode);
    if (subcat) params.append('subcategoria_id', subcat);
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
                return `
                <tr>
                    <td>${p.nombre}</td>
                    <td>${sub}</td>
                    <td>Q ${precio}</td>
                    <td><span class="badge ${stock <= minStock ? 'bg-danger' : 'bg-success'}">${stock}</span></td>
                    <td><span class="badge ${activo ? 'bg-success' : 'bg-secondary'}">${activo ? 'Activo' : 'Inactivo'}</span></td>
                    <td class="text-end">
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
    clearCatalogErrors('product-form');
    setProductSaving(true);

    const id = inputFor('product-form', 'product-id').value;
    const payload = {
        id_subcategoria: parseInt(inputFor('product-form', 'id_subcategoria').value, 10),
        id_unidad: parseInt(inputFor('product-form', 'id_unidad').value, 10),
        nombre: inputFor('product-form', 'nombre').value.trim(),
        descripcion: inputFor('product-form', 'descripcion').value.trim() || null,
        variante: {
            codigo_barras: inputFor('product-form', 'codigo_barras').value.trim() || null,
            talla: inputFor('product-form', 'talla').value.trim() || null,
            color: inputFor('product-form', 'color').value.trim() || null,
            precio_detalle: parseFloat(inputFor('product-form', 'precio_detalle').value),
            precio_mayoreo: parseFloat(inputFor('product-form', 'precio_mayoreo').value),
            costo_promedio: parseFloat(inputFor('product-form', 'costo_promedio').value || '0'),
        },
        inventario: {
            id_sucursal: parseInt(inputFor('product-form', 'id_sucursal').value, 10),
            id_area: parseInt(inputFor('product-form', 'id_area').value, 10) || null,
            stock_actual: parseInt(inputFor('product-form', 'stock_actual').value || '0', 10),
            stock_minimo: parseInt(inputFor('product-form', 'stock_minimo').value || '0', 10),
        },
    };
    if (id) payload.estado = inputFor('product-form', 'product_is_active').checked ? 'Activo' : 'Inactivo';

    const url = id ? `${PRODUCTS_API}/${id}` : PRODUCTS_API;
    const method = id ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, { method, headers: authHeaders(), body: JSON.stringify(payload) });
        if (!res.ok) {
            await handleCatalogApiError(res, 'product-form');
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
    clearCatalogErrors('category-form');
    setCategorySaving(true);

    const id = inputFor('category-form', 'category-id').value;
    const payload = {
        nombre: inputFor('category-form', 'name').value.trim(),
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
    await Promise.all([
        loadProducts(),
        loadCategoriesTable(),
        populateSubcategorias('filter-product-subcategoria', null, 'Todas las subcategorías'),
    ]);
};

window.editProduct = editProduct;
window.editCategory = editCategory;

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
    if (btnFilterProducts) btnFilterProducts.addEventListener('click', loadProducts);
    const btnFilterCategories = document.getElementById('btn-filter-categories');
    if (btnFilterCategories) btnFilterCategories.addEventListener('click', loadCategoriesTable);
});