// Módulo de Catálogos (Productos y Categorías) - Tienda el Regalito
// Construido sobre la plantilla del módulo de Usuarios (users.js):
//   - Modales defensivos (backdrop estático + dirty check al cerrar).
//   - Validación inline con Bootstrap + traducción de errores 422.
//   - Integración SPA (hash routing) + Auth Guard + Unload Guard.
//   - Cero alert()/confirm() nativos: se reutilizan showToast() y confirmModal().
// Nota: los ids de los campos coinciden con el schema de Pydantic (name, sku,
// barcode, category_id, price, current_stock, min_stock, description). Como
// algunos se repiten entre formularios (p. ej. `name`), el acceso a campos se
// hace SIEMPRE con ámbito de formulario (inputFor/feedbackFor) para evitar
// colisiones de ids.
const CATEGORIES_API = '/api/categorias';
const PRODUCTS_API = '/api/productos';

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
// Carga de catálogos (Categorías para selects)
// ---------------------------------------------------------------------------

async function populateCategorySelect(selectId, selectedId = null, placeholder) {
    const select = document.getElementById(selectId);
    if (!select) return;
    select.innerHTML = '<option value="">Cargando...</option>';
    try {
        const res = await fetch(CATEGORIES_API, { headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'No se pudieron cargar las categorías', 'danger');
            return;
        }
        const categories = await res.json();
        select.innerHTML = placeholder ? `<option value="">${placeholder}</option>` : '<option value=""></option>';
        categories.forEach((c) => {
            if (!c.is_active) return;
            const opt = document.createElement('option');
            opt.value = c.id;
            opt.textContent = c.name;
            if (selectedId && c.id === selectedId) opt.selected = true;
            select.appendChild(opt);
        });
    } catch (err) {
        select.innerHTML = '<option value="">Sin categorías disponibles</option>';
        console.error(err);
    }
}

// ---------------------------------------------------------------------------
// Listado de Categorías
// ---------------------------------------------------------------------------

async function loadCategoriesTable() {
    const tbody = document.getElementById('categories-table-body');
    const empty = document.getElementById('categories-empty');
    try {
        const res = await fetch(`${CATEGORIES_API}?include_inactive=true`, { headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'No se pudieron cargar las categorías', 'danger');
            return;
        }
        const items = await res.json();
        if (items.length) {
            tbody.innerHTML = items.map((c) => `
                <tr>
                    <td>${c.name}</td>
                    <td>${c.description || '-'}</td>
                    <td><span class="badge ${c.is_active ? 'bg-success' : 'bg-secondary'}">${c.is_active ? 'Activo' : 'Inactivo'}</span></td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary" onclick="editCategory(${c.id})" title="Editar"><i class="bi bi-pencil"></i></button>
                        ${c.is_active ? `<button class="btn btn-sm btn-outline-danger" onclick="deactivateCategory(${c.id})" title="Desactivar"><i class="bi bi-x-circle"></i></button>` : ''}
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
    const sku = document.getElementById('filter-product-sku').value.trim();
    const cat = document.getElementById('filter-product-category').value;
    if (name) params.append('name', name);
    if (sku) params.append('sku', sku);
    if (cat) params.append('category_id', cat);
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
            tbody.innerHTML = items.map((p) => `
                <tr>
                    <td>${p.sku || '-'}</td>
                    <td>${p.name}</td>
                    <td>${p.category ? p.category.name : '-'}</td>
                    <td>Q ${Number(p.price).toFixed(2)}</td>
                    <td><span class="badge ${p.current_stock <= p.min_stock ? 'bg-danger' : 'bg-success'}">${p.current_stock}</span></td>
                    <td><span class="badge ${p.is_active ? 'bg-success' : 'bg-secondary'}">${p.is_active ? 'Activo' : 'Inactivo'}</span></td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-primary" onclick="editProduct(${p.id})" title="Editar"><i class="bi bi-pencil"></i></button>
                        ${p.is_active ? `<button class="btn btn-sm btn-outline-danger" onclick="deactivateProduct(${p.id})" title="Desactivar"><i class="bi bi-x-circle"></i></button>` : ''}
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
// Formulario / Modal de Producto
// ---------------------------------------------------------------------------

async function resetProductForm() {
    clearCatalogErrors('product-form');
    const form = document.getElementById('product-form');
    if (form) form.reset();
    inputFor('product-form', 'product-id').value = '';
    document.getElementById('product-modal-title').textContent = 'Nuevo Producto';
    baseSaveTextProduct = 'Guardar';
    const text = document.getElementById('btn-save-product-text');
    if (text) text.textContent = baseSaveTextProduct;
    await populateCategorySelect('category_id', null, '-- Seleccione categoría --');
}

function openCreateProductModal() {
    resetProductForm().then(() => {
        const modal = getModal('product-modal');
        if (modal) modal.show();
        const nameInput = inputFor('product-form', 'name');
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
        inputFor('product-form', 'product-id').value = p.id;
        inputFor('product-form', 'name').value = p.name;
        inputFor('product-form', 'sku').value = p.sku || '';
        inputFor('product-form', 'barcode').value = p.barcode;
        inputFor('product-form', 'price').value = p.price;
        inputFor('product-form', 'current_stock').value = p.current_stock;
        inputFor('product-form', 'min_stock').value = p.min_stock;
        inputFor('product-form', 'product_is_active').checked = p.is_active;
        document.getElementById('product-modal-title').textContent = 'Editar Producto';
        baseSaveTextProduct = 'Actualizar';
        const text = document.getElementById('btn-save-product-text');
        if (text) text.textContent = baseSaveTextProduct;
        await populateCategorySelect('category_id', p.category_id, '-- Seleccione categoría --');
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
        name: inputFor('product-form', 'name').value.trim(),
        sku: inputFor('product-form', 'sku').value.trim() || null,
        barcode: inputFor('product-form', 'barcode').value.trim(),
        category_id: parseInt(inputFor('product-form', 'category_id').value, 10),
        price: parseFloat(inputFor('product-form', 'price').value),
        current_stock: parseInt(inputFor('product-form', 'current_stock').value || '0', 10),
        min_stock: parseInt(inputFor('product-form', 'min_stock').value || '5', 10),
    };
    if (id) payload.is_active = inputFor('product-form', 'product_is_active').checked;

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
        inputFor('category-form', 'category-id').value = c.id;
        inputFor('category-form', 'name').value = c.name;
        inputFor('category-form', 'description').value = c.description || '';
        inputFor('category-form', 'category_is_active').checked = c.is_active;
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
        name: inputFor('category-form', 'name').value.trim(),
        description: inputFor('category-form', 'description').value.trim() || null,
    };
    if (id) payload.is_active = inputFor('category-form', 'category_is_active').checked;

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
        await Promise.all([loadCategoriesTable(), populateCategorySelect('filter-product-category', null, 'Todas las categorías')]);
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
        await Promise.all([loadCategoriesTable(), populateCategorySelect('filter-product-category', null, 'Todas las categorías')]);
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
        populateCategorySelect('filter-product-category', null, 'Todas las categorías'),
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

    const btnNewProduct = document.getElementById('btn-new-product');
    if (btnNewProduct) btnNewProduct.addEventListener('click', openCreateProductModal);
    const btnNewCategory = document.getElementById('btn-new-category');
    if (btnNewCategory) btnNewCategory.addEventListener('click', openCreateCategoryModal);
    const btnFilterProducts = document.getElementById('btn-filter-products');
    if (btnFilterProducts) btnFilterProducts.addEventListener('click', loadProducts);
    const btnFilterCategories = document.getElementById('btn-filter-categories');
    if (btnFilterCategories) btnFilterCategories.addEventListener('click', loadCategoriesTable);
});