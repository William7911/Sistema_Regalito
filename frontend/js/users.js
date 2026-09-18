// Módulo de Usuarios - Tienda el Regalito
// Migrado al esquema Usuario del DERCAS (id_usuario, id_rol, nombre_completo,
// username, estado). Cero datos quemados: el Rol se carga desde la BD.
// Validación visual inline con Bootstrap + notificaciones Toast (sin alert() nativos).
const USERS_API = '/api/usuarios';
const ROLES_API = '/api/roles';

let baseSaveText = 'Guardar';

// Estado de paginación y ordenamiento del listado.
let usersState = {
    page: 1,
    pageSize: 10,
    total: 0,
    sortBy: 'nombre_completo',
    sortDir: 'asc',
};

function authHeaders() {
    const token = localStorage.getItem('jwt_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    };
}

// Formatea una fecha (ISO/UTC) a DD/MM/YYYY.
function formatDate(value) {
    if (!value) return '-';
    const d = new Date(value);
    if (isNaN(d.getTime())) return '-';
    const dd = String(d.getDate()).padStart(2, '0');
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const yyyy = d.getFullYear();
    return `${dd}/${mm}/${yyyy}`;
}

function getModal(id) {
    const el = document.getElementById(id);
    return el && window.bootstrap ? bootstrap.Modal.getOrCreateInstance(el) : null;
}

// ---------------------------------------------------------------------------
// Notificaciones (Toast) y confirmación — cero alert()/confirm() nativos
// ---------------------------------------------------------------------------

function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container || !window.bootstrap) return;
    const colors = { success: 'text-bg-success', danger: 'text-bg-danger', warning: 'text-bg-warning', info: 'text-bg-info' };
    const el = document.createElement('div');
    el.className = `toast align-items-center text-white border-0 ${colors[type] || 'text-bg-info'}`;
    el.setAttribute('role', 'alert');
    el.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button>
        </div>`;
    container.appendChild(el);
    const toast = new bootstrap.Toast(el, { delay: 3500 });
    toast.show();
    el.addEventListener('hidden.bs.toast', () => el.remove());
}

function confirmModal(message) {
    return new Promise((resolve) => {
        const msgEl = document.getElementById('confirm-message');
        const okBtn = document.getElementById('confirm-ok');
        const modalEl = document.getElementById('confirm-modal');
        if (!msgEl || !okBtn || !modalEl || !window.bootstrap) {
            resolve(true);
            return;
        }
        const modal = new bootstrap.Modal(modalEl);
        msgEl.textContent = message;
        modal.show();
        // El diálogo de confirmación se muestra sobre cualquier modal abierto
        // (p. ej. #user-modal). Subimos su z-index y el de su backdrop para que
        // quede centrado, completamente visible y oscurezca el fondo correctamente.
        modalEl.style.zIndex = '2000';
        const backdrops = document.querySelectorAll('.modal-backdrop');
        if (backdrops.length) backdrops[backdrops.length - 1].style.zIndex = '1990';

        const cleanup = (val) => {
            modal.hide();
            okBtn.removeEventListener('click', onOk);
            modalEl.removeEventListener('hidden.bs.modal', onHide);
            resolve(val);
        };
        const onOk = () => cleanup(true);
        const onHide = () => cleanup(false);
        okBtn.addEventListener('click', onOk);
        modalEl.addEventListener('hidden.bs.modal', onHide);
    });
}

// ---------------------------------------------------------------------------
// Traducción de errores Pydantic
// ---------------------------------------------------------------------------

function translateValidation(msg, isSelect = false, field = null) {
    if (!msg || typeof msg !== 'string') return 'Valor no válido.';

    // Normalización: si field o isSelect indican campo tipo select / dropdown
    const isSelectField = isSelect === true ||
        (typeof isSelect === 'string' && (isSelect.startsWith('id_') || isSelect === 'estado' || isSelect === 'rol' || isSelect.includes('sucursal') || isSelect.includes('subcategoria') || isSelect.includes('unidad'))) ||
        (typeof field === 'string' && (field.startsWith('id_') || field === 'estado' || field === 'rol' || field.includes('sucursal') || field.includes('subcategoria') || field.includes('unidad')));

    // Pydantic v2: Mensajes de números decimales y precios
    if (/^Decimal input should be an integer, float, string or Decimal object/i.test(msg) ||
        /^Input should be a valid decimal/i.test(msg)) {
        return 'Debe ingresar un precio o número válido.';
    }

    // Pydantic v2: Selects / Dropdowns
    if (isSelectField) {
        if (/Input should be a valid integer/i.test(msg) ||
            /Input should be a valid number/i.test(msg) ||
            /valid integer/i.test(msg) ||
            /valid number/i.test(msg) ||
            msg === 'Field required' ||
            msg === 'String should have at least 1 character') {
            return 'Seleccione una opción.';
        }
    }

    // Traducciones directas comunes
    if (msg === 'String should have at least 1 character') return isSelectField ? 'Seleccione una opción.' : 'Este campo es obligatorio.';
    if (msg === 'Field required') return isSelectField ? 'Seleccione una opción.' : 'Este campo es obligatorio.';
    if (msg === 'Input should be greater than 0') return 'Debe ingresar un valor mayor a 0.';
    if (msg === 'Input should be greater than or equal to 0') return 'Debe ingresar un valor mayor o igual a 0.';
    if (msg === 'Input should be a valid decimal') return 'Debe ingresar un precio o número válido.';
    if (msg === 'Extra inputs are not permitted') return 'Campo no permitido.';
    if (msg === 'Input should be a valid boolean') return 'Seleccione una opción válida.';

    const translations = [
        { from: /Decimal input should be an integer, float, string or Decimal object.*/i, to: 'Debe ingresar un precio o número válido.' },
        { from: /Input should be a valid decimal.*/i, to: 'Debe ingresar un precio o número válido.' },
        { from: /String should have at least (\d+) characters?/, to: 'Debe tener al menos $1 caracteres.' },
        { from: /String should have at most (\d+) characters?/, to: 'No debe exceder $1 caracteres.' },
        { from: /Input should be greater than (\d+(?:\.\d+)?)/, to: 'Debe ser mayor a $1.' },
        { from: /Input should be greater than or equal to (\d+(?:\.\d+)?)/, to: 'Debe ser mayor o igual a $1.' },
        { from: /Input should be less than or equal to (\d+(?:\.\d+)?)/, to: 'No debe exceder $1.' },
        { from: /Input should be less than (\d+(?:\.\d+)?)/, to: 'Debe ser menor a $1.' },
        { from: /Decimal input should have no more than (\d+) decimal places?/, to: 'No debe tener más de $1 decimales.' },
        { from: /Decimal input should have no more than (\d+) digits? in total/, to: 'No debe exceder $1 dígitos en total.' },
        { from: /Input should be a valid integer.*/, to: isSelectField ? 'Seleccione una opción.' : 'Debe ingresar un número entero válido.' },
        { from: /Input should be a valid number.*/, to: isSelectField ? 'Seleccione una opción.' : 'Debe ingresar un número válido.' },
        { from: /Input should be a valid date.*/, to: 'Debe ingresar una fecha válida.' },
        { from: /Input should be a valid datetime.*/, to: 'Debe ingresar una fecha y hora válidas.' },
        { from: /String should match pattern/, to: 'El formato no es válido.' },
        { from: /Value error, (.*)/, to: '$1' },
    ];

    for (const t of translations) {
        if (t.from.test(msg)) return msg.replace(t.from, t.to);
    }
    return msg;
}

window.translateValidation = translateValidation;

// ---------------------------------------------------------------------------
// Errores inline
// ---------------------------------------------------------------------------

function showFormBanner(message, type = 'danger') {
    const banner = document.getElementById('user-form-alert');
    if (!banner) return;
    banner.classList.remove('d-none', 'alert-success', 'alert-danger');
    banner.classList.add(type === 'success' ? 'alert-success' : 'alert-danger');
    banner.textContent = message;
}

function hideFormBanner() {
    const banner = document.getElementById('user-form-alert');
    if (banner) {
        banner.classList.add('d-none');
        banner.classList.remove('alert-success', 'alert-danger');
        banner.textContent = '';
    }
}

function clearFieldError(el) {
    el.classList.remove('is-invalid');
    const feedback = el.id ? document.getElementById(`error-${el.id}`) : null;
    if (feedback) feedback.textContent = '';
}

function clearValidationErrors() {
    document.querySelectorAll('#user-form .form-control, #user-form .form-select').forEach(clearFieldError);
    hideFormBanner();
}

function renderFieldErrors(detail) {
    if (!Array.isArray(detail)) return;
    detail.forEach((err) => {
        const field = err.loc && err.loc.length ? err.loc[err.loc.length - 1] : null;
        const input = field ? document.getElementById(field) : null;
        const isSelect = (input && input.tagName && input.tagName.toUpperCase() === 'SELECT') || (field && (field.startsWith('id_') || field === 'estado' || field === 'rol'));
        const msg = translateValidation(err.msg || 'Valor inválido', isSelect, field);
        const feedback = field ? document.getElementById(`error-${field}`) : null;
        if (input && feedback) {
            input.classList.add('is-invalid');
            feedback.textContent = msg;
        } else {
            showFormBanner(msg, 'danger');
        }
    });
}

function applyUserFieldError(fieldId, msg) {
    const input = document.getElementById(fieldId);
    const feedback = document.getElementById(`error-${fieldId}`);
    if (input) input.classList.add('is-invalid');
    if (feedback) feedback.textContent = msg;
}

let isUserFormSubmittingOrClosing = false;

function shouldSkipUserBlur(e) {
    if (isUserFormSubmittingOrClosing) return true;
    const rt = e && e.relatedTarget;
    if (rt && rt.closest && rt.closest('#btn-save-user, [type="submit"], [data-bs-close-modal], .btn-close')) {
        return true;
    }
    return false;
}

// Limpieza de errores en tiempo real al teclear y validación visual al desenfocar (blur).
function initRealtimeValidation() {
    const form = document.getElementById('user-form');
    if (!form) return;
    form.querySelectorAll('.form-control, .form-select').forEach((el) => {
        el.addEventListener('input', () => clearFieldError(el));
        el.addEventListener('change', () => clearFieldError(el));
    });

    const saveBtn = document.getElementById('btn-save-user');
    if (saveBtn) {
        saveBtn.addEventListener('mousedown', () => {
            isUserFormSubmittingOrClosing = true;
            setTimeout(() => { isUserFormSubmittingOrClosing = false; }, 400);
        });
    }

    const modal = document.getElementById('user-modal');
    if (modal) {
        modal.querySelectorAll('[data-bs-close-modal], .btn-close').forEach(btn => {
            btn.addEventListener('mousedown', () => {
                isUserFormSubmittingOrClosing = true;
                setTimeout(() => { isUserFormSubmittingOrClosing = false; }, 400);
            });
        });
    }

    const nombreInput = document.getElementById('nombre_completo');
    if (nombreInput) {
        nombreInput.addEventListener('blur', (e) => {
            if (shouldSkipUserBlur(e)) return;
            if (!nombreInput.value.trim()) {
                applyUserFieldError('nombre_completo', 'Este campo es obligatorio.');
            }
        });
    }

    const userInput = document.getElementById('username');
    if (userInput) {
        userInput.addEventListener('blur', (e) => {
            if (shouldSkipUserBlur(e)) return;
            if (!userInput.value.trim()) {
                applyUserFieldError('username', 'Este campo es obligatorio.');
            }
        });
    }

    const passInput = document.getElementById('password');
    if (passInput) {
        passInput.addEventListener('blur', (e) => {
            if (shouldSkipUserBlur(e)) return;
            const isCreate = !document.getElementById('user-id')?.value;
            const val = passInput.value;
            if (isCreate && !val) {
                applyUserFieldError('password', 'Este campo es obligatorio.');
            } else if (val && val.length < 6) {
                applyUserFieldError('password', 'Debe tener al menos 6 caracteres.');
            }
        });
    }

    const rolSelect = document.getElementById('id_rol');
    if (rolSelect) {
        rolSelect.addEventListener('blur', (e) => {
            if (shouldSkipUserBlur(e)) return;
            if (!rolSelect.value || isNaN(parseInt(rolSelect.value, 10))) {
                applyUserFieldError('id_rol', 'Seleccione una opción.');
            }
        });
    }

    const estadoSelect = document.getElementById('estado');
    if (estadoSelect) {
        estadoSelect.addEventListener('blur', (e) => {
            if (shouldSkipUserBlur(e)) return;
            if (!estadoSelect.value) {
                applyUserFieldError('estado', 'Seleccione una opción.');
            }
        });
    }
}

// ---------------------------------------------------------------------------
// Estados de guardado (bloqueo + spinner)
// ---------------------------------------------------------------------------

function setSaving(saving) {
    const btn = document.getElementById('btn-save-user');
    const spinner = document.getElementById('btn-save-spinner');
    const text = document.getElementById('btn-save-text');
    if (!btn) return;
    btn.disabled = saving;
    if (spinner) spinner.classList.toggle('d-none', !saving);
    if (text) text.textContent = saving ? 'Guardando...' : baseSaveText;
}

// ---------------------------------------------------------------------------
// Carga de catálogos (Roles / Departamentos)
// ---------------------------------------------------------------------------

async function loadRoles(selectedId = null) {
    const select = document.getElementById('id_rol');
    if (!select) return;
    select.innerHTML = '<option value="">Cargando roles...</option>';
    try {
        const res = await fetch(ROLES_API, { headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'No se pudieron cargar los roles', 'danger');
            return;
        }
        const roles = await res.json();
        select.innerHTML = '<option value="">-- Seleccione rol --</option>';
        roles.forEach(r => {
            const opt = document.createElement('option');
            opt.value = r.id_rol;
            opt.textContent = r.nombre;
            if (selectedId && String(r.id_rol) === String(selectedId)) opt.selected = true;
            select.appendChild(opt);
        });
    } catch (err) {
        select.innerHTML = '<option value="">Sin roles disponibles</option>';
        console.error(err);
    }
}

// Select del filtro de la tabla (rol), independiente del del modal.
async function loadRoleFilter() {
    const select = document.getElementById('filter-role');
    if (!select) return;
    try {
        const res = await fetch(ROLES_API, { headers: authHeaders() });
        if (!res.ok) return;
        const roles = await res.json();
        select.innerHTML = '<option value="">Todos los roles</option>';
        roles.forEach(r => {
            const opt = document.createElement('option');
            opt.value = r.id_rol;
            opt.textContent = r.nombre;
            select.appendChild(opt);
        });
    } catch (err) {
        console.error(err);
    }
}

// ---------------------------------------------------------------------------
// Listado de usuarios (con estado vacío)
// ---------------------------------------------------------------------------

async function loadUsers() {
    const tbody = document.getElementById('users-table-body');
    const empty = document.getElementById('users-empty');
    if (!tbody) return;

    const params = new URLSearchParams();
    const name = (document.getElementById('filter-name')?.value || '').trim();
    const role = document.getElementById('filter-role')?.value || '';
    const isActive = document.getElementById('filter-active')?.value ?? '';
    const from = document.getElementById('filter-from')?.value || '';
    const to = document.getElementById('filter-to')?.value || '';

    if (name) params.append('name', name);
    if (role) params.append('role_id', role);
    if (isActive !== '') params.append('is_active', isActive);
    if (from) params.append('created_from', from);
    if (to) params.append('created_to', to);

    const pageSize = parseInt(document.getElementById('users-page-size')?.value || String(usersState.pageSize || 10), 10) || 10;
    usersState.pageSize = pageSize;
    const page = usersState.page || 1;

    params.append('sort_by', usersState.sortBy || 'id_usuario');
    params.append('sort_dir', usersState.sortDir || 'asc');
    params.append('limit', pageSize);
    params.append('offset', (page - 1) * pageSize);

    try {
        const res = await fetch(`${USERS_API}?${params.toString()}`, { headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'No se pudieron cargar los usuarios', 'danger');
            return;
        }
        const data = await res.json();

        if (data.items.length) {
            tbody.innerHTML = data.items.map(u => {
                const rol = u.rol ? u.rol.nombre : '-';
                const activo = u.estado === 'Activo';
                const fecha = u.fecha_creacion ? formatDate(u.fecha_creacion) : '-';
                return `
                <tr>
                    <td>${u.id_usuario}</td>
                    <td>${u.nombre_completo}</td>
                    <td>${u.username}</td>
                    <td>${rol}</td>
                    <td><span class="badge ${activo ? 'bg-success' : 'bg-secondary'}">${activo ? 'Activo' : 'Inactivo'}</span></td>
                    <td>${fecha}</td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-info" onclick="viewUserDetail(${u.id_usuario})" title="Ver detalle"><i class="bi bi-eye"></i></button>
                        <button class="btn btn-sm btn-outline-primary" onclick="editUser(${u.id_usuario})" title="Editar"><i class="bi bi-pencil"></i></button>
                        ${activo ? `<button class="btn btn-sm btn-outline-danger" onclick="deactivateUser(${u.id_usuario})" title="Desactivar"><i class="bi bi-x-circle"></i></button>` : ''}
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
        usersState.total = data.total || 0;
        renderPagination();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// Renderiza la barra de paginación a partir del estado actual.
function renderPagination() {
    const pagination = document.getElementById('users-pagination');
    if (!pagination) return;
    const totalPages = Math.max(1, Math.ceil(usersState.total / usersState.pageSize));
    if (usersState.page > totalPages) usersState.page = totalPages;
    const info = document.getElementById('users-page-info');
    const prev = document.getElementById('users-prev-page');
    const next = document.getElementById('users-next-page');
    if (info) info.textContent = `Página ${usersState.page} de ${totalPages}`;
    if (prev) prev.disabled = usersState.page <= 1;
    if (next) next.disabled = usersState.page >= totalPages;
    if (usersState.total === 0) {
        pagination.classList.add('d-none');
    } else {
        pagination.classList.remove('d-none');
    }
}

// Va a una página concreta y recarga el listado.
function goToPage(page) {
    const totalPages = Math.max(1, Math.ceil(usersState.total / usersState.pageSize));
    if (page < 1) page = 1;
    if (page > totalPages) page = totalPages;
    if (page === usersState.page) return;
    usersState.page = page;
    loadUsers();
}

// Alterna el orden (asc/desc) de una columna y recarga.
function toggleSort(column) {
    if (usersState.sortBy === column) {
        usersState.sortDir = usersState.sortDir === 'asc' ? 'desc' : 'asc';
    } else {
        usersState.sortBy = column;
        usersState.sortDir = 'asc';
    }
    usersState.page = 1;
    updateSortIndicators();
    loadUsers();
}

// Pinta los indicadores asc/desc en las cabeceras ordenables de usuarios.
function updateSortIndicators() {
    document.querySelectorAll('#users-view th.sortable').forEach((th) => {
        const col = th.getAttribute('data-sort');
        const existing = th.querySelector('.sort-icon');
        if (existing) th.removeChild(existing);
        if (col === usersState.sortBy) {
            const icon = document.createElement('span');
            icon.className = 'sort-icon';
            icon.textContent = usersState.sortDir === 'asc' ? '▲' : '▼';
            th.appendChild(icon);
        }
    });
}

// ---------------------------------------------------------------------------
// Protección contra pérdida de datos (dirty form check + cierre seguro)
// ---------------------------------------------------------------------------

// Indica si el formulario tiene datos ingresados por el usuario (texto no vacío).
function formHasData() {
    const form = document.getElementById('user-form');
    if (!form) return false;
    let hasData = false;
    form.querySelectorAll('input[type="text"], input[type="password"], textarea, select').forEach((el) => {
        if (el.value && el.value.trim().length > 0) hasData = true;
    });
    return hasData;
}

// Cierre seguro: si hay datos sin guardar pide confirmación; si está vacío cierra al instante.
async function safeCloseUserModal() {
    const modal = getModal('user-modal');
    if (!modal) return;
    if (formHasData()) {
        const ok = await confirmModal('¿Tienes datos sin guardar. ¿Deseas descartar los cambios y salir?');
        if (!ok) return;
    }
    clearValidationErrors();
    const form = document.getElementById('user-form');
    if (form) form.reset();
    document.querySelectorAll('#user-form .is-invalid').forEach((el) => el.classList.remove('is-invalid'));
    document.querySelectorAll('#user-form .invalid-feedback').forEach((el) => { el.textContent = ''; });
    modal.hide();
}

// ---------------------------------------------------------------------------
// Formulario / Modal
// ---------------------------------------------------------------------------

// Reseteo absoluto del formulario y sus errores (sin dejar rastro).
async function resetUserForm() {
    clearValidationErrors();
    const form = document.getElementById('user-form');
    if (form) form.reset();
    document.getElementById('user-id').value = '';
    document.getElementById('password').required = true;
    document.getElementById('user-modal-title').textContent = 'Nuevo Usuario';
    baseSaveText = 'Guardar';
    const text = document.getElementById('btn-save-text');
    if (text) text.textContent = baseSaveText;
    await Promise.all([loadRoles(), loadRoleFilter()]);
}

function openCreateModal() {
    resetUserForm().then(() => {
        const modal = getModal('user-modal');
        if (modal) modal.show();
        const nameInput = document.getElementById('nombre_completo');
        setTimeout(() => nameInput && nameInput.focus(), 350);
    });
}

async function editUser(userId) {
    clearValidationErrors();
    try {
        const res = await fetch(`${USERS_API}/${userId}`, { headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'No se encontró el usuario', 'danger');
            return;
        }
        const u = await res.json();
        document.getElementById('user-id').value = u.id_usuario;
        document.getElementById('nombre_completo').value = u.nombre_completo;
        document.getElementById('username').value = u.username;
        document.getElementById('password').value = '';
        document.getElementById('password').required = false;
        const estadoSel = document.getElementById('estado');
        if (estadoSel) estadoSel.value = u.estado === 'Activo' ? 'Activo' : 'Inactivo';
        document.getElementById('user-modal-title').textContent = 'Editar Usuario';
        baseSaveText = 'Actualizar';
        const text = document.getElementById('btn-save-text');
        if (text) text.textContent = baseSaveText;
        await Promise.all([loadRoles(u.id_rol), loadRoleFilter()]);
        const modal = getModal('user-modal');
        if (modal) modal.show();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// Modal informativo de detalle (solo lectura, backdrop estático).
async function viewUserDetail(userId) {
    try {
        const res = await fetch(`${USERS_API}/${userId}`, { headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'No se encontró el usuario', 'danger');
            return;
        }
        const u = await res.json();
        document.getElementById('detail-id').textContent = u.id_usuario;
        document.getElementById('detail-nombre').textContent = u.nombre_completo || '-';
        document.getElementById('detail-username').textContent = u.username || '-';
        document.getElementById('detail-rol').textContent = (u.rol && u.rol.nombre) ? u.rol.nombre : '-';
        document.getElementById('detail-estado').textContent = u.estado || '-';
        document.getElementById('detail-fecha').textContent = u.fecha_creacion
            ? new Date(u.fecha_creacion).toLocaleString()
            : '-';
        const modal = getModal('user-detail-modal');
        if (modal) modal.show();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// Guardar (crear o actualizar)
async function saveUser(event) {
    event.preventDefault();
    isUserFormSubmittingOrClosing = false;
    clearValidationErrors();

    const id = document.getElementById('user-id').value;
    const nombreCompleto = document.getElementById('nombre_completo')?.value?.trim() || '';
    const username = document.getElementById('username')?.value?.trim() || '';
    const password = document.getElementById('password')?.value || '';
    const rolVal = document.getElementById('id_rol')?.value || '';
    const estadoSel = document.getElementById('estado');
    const estadoVal = estadoSel ? estadoSel.value : '';

    let hasClientErrors = false;
    let firstInvalidEl = null;

    function markInvalid(fieldId, errorMsg) {
        applyUserFieldError(fieldId, errorMsg);
        hasClientErrors = true;
        if (!firstInvalidEl) {
            firstInvalidEl = document.getElementById(fieldId);
        }
    }

    if (!nombreCompleto) {
        markInvalid('nombre_completo', 'Este campo es obligatorio.');
    }

    if (!username) {
        markInvalid('username', 'Este campo es obligatorio.');
    }

    if (!id) {
        if (!password) {
            markInvalid('password', 'Este campo es obligatorio.');
        } else if (password.length < 6) {
            markInvalid('password', 'Debe tener al menos 6 caracteres.');
        }
    } else {
        if (password && password.length < 6) {
            markInvalid('password', 'Debe tener al menos 6 caracteres.');
        }
    }

    const idRol = parseInt(rolVal, 10);
    if (!rolVal || isNaN(idRol) || idRol <= 0) {
        markInvalid('id_rol', 'Seleccione una opción.');
    }

    if (!estadoVal) {
        markInvalid('estado', 'Seleccione una opción.');
    }

    if (hasClientErrors) {
        if (firstInvalidEl) firstInvalidEl.focus();
        showFormBanner('Por favor complete todos los campos obligatorios correctamente.', 'danger');
        return;
    }

    setSaving(true);

    // Payload con las claves exactas de Pydantic (UsuarioCreate / UsuarioUpdate).
    const payload = {
        nombre_completo: nombreCompleto,
        username: username,
        id_rol: idRol,
    };
    if (estadoVal) payload.estado = estadoVal;

    if (id) {
        // En edición se omite la contraseña si va en blanco (no se sobrescribe).
        if (password) payload.password = password;
    } else {
        payload.password = password;
    }

    const url = id ? `${USERS_API}/${id}` : USERS_API;
    const method = id ? 'PUT' : 'POST';

    try {
        const res = await fetch(url, {
            method,
            headers: authHeaders(),
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            const detail = errData && errData.detail;
            if (res.status === 422 && Array.isArray(detail)) {
                renderFieldErrors(detail);
            } else if (typeof detail === 'string' && detail.trim()) {
                showToast(detail, 'danger');
            } else {
                showToast('No se pudo completar la operación.', 'danger');
            }
            return;
        }

        const modal = getModal('user-modal');
        if (modal) modal.hide(); // el reseteo ocurre en 'hidden.bs.modal'
        showToast(id ? 'Usuario actualizado correctamente.' : 'Usuario creado correctamente.', 'success');
        await loadUsers();
    } catch (err) {
        showToast(err.message, 'danger');
    } finally {
        setSaving(false);
    }
}

// Eliminación lógica (soft delete) con confirmación no nativa
async function deactivateUser(userId) {
    const ok = await confirmModal('¿Desactivar este usuario?');
    if (!ok) return;
    try {
        const res = await fetch(`${USERS_API}/${userId}`, { method: 'DELETE', headers: authHeaders() });
        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            showToast((errData && errData.detail) || 'Error al desactivar el usuario', 'danger');
            return;
        }
        showToast('Usuario desactivado correctamente.', 'success');
        await loadUsers();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ---------------------------------------------------------------------------
// Resiliencia de datos: guardia contra navegación/recarga involuntaria
// ---------------------------------------------------------------------------

window.addEventListener('beforeunload', (event) => {
    const userModal = document.getElementById('user-modal');
    const isModalVisible = userModal && userModal.classList.contains('show');

    if (isModalVisible && typeof formHasData === 'function' && formHasData()) {
        event.preventDefault();
        event.returnValue = '';
    }
});

// ---------------------------------------------------------------------------
// Navegación
// ---------------------------------------------------------------------------

window.showUsersModule = async function () {
    updateSortIndicators();
    await Promise.all([loadUsers(), loadRoleFilter()]);
};

window.goToDashboard = function () {
    if (typeof window.navigateTo === 'function') window.navigateTo('dashboard');
};

window.editUser = editUser;
window.viewUserDetail = viewUserDetail;

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('user-form');
    if (form) {
        form.addEventListener('submit', saveUser); // Enter en cualquier campo dispara el submit
        initRealtimeValidation();
    }
    const modalEl = document.getElementById('user-modal');
    if (modalEl) modalEl.addEventListener('hidden.bs.modal', resetUserForm); // reseteo impecable al cerrar
    document.querySelectorAll('#user-modal [data-bs-close-modal]').forEach((btn) => {
        btn.addEventListener('click', safeCloseUserModal);
    });
    const btnNew = document.getElementById('btn-new-user');
    if (btnNew) btnNew.addEventListener('click', openCreateModal);
    const btnFilter = document.getElementById('btn-filter-users');
    if (btnFilter) btnFilter.addEventListener('click', () => {
        usersState.page = 1;
        loadUsers();
    });
    // Paginación
    const pageSize = document.getElementById('users-page-size');
    if (pageSize) pageSize.addEventListener('change', () => {
        usersState.pageSize = parseInt(pageSize.value, 10);
        usersState.page = 1;
        loadUsers();
    });
    const prevBtn = document.getElementById('users-prev-page');
    if (prevBtn) prevBtn.addEventListener('click', () => goToPage(usersState.page - 1));
    const nextBtn = document.getElementById('users-next-page');
    if (nextBtn) nextBtn.addEventListener('click', () => goToPage(usersState.page + 1));
    // Ordenamiento de columnas
    document.querySelectorAll('#users-view th.sortable').forEach((th) => {
        th.addEventListener('click', () => toggleSort(th.getAttribute('data-sort')));
    });
    // Reporte descargable
    const btnExcel = document.getElementById('btn-report-excel');
    if (btnExcel) btnExcel.addEventListener('click', (e) => { e.preventDefault(); downloadReport('excel'); });
    const btnCsv = document.getElementById('btn-report-csv');
    if (btnCsv) btnCsv.addEventListener('click', (e) => { e.preventDefault(); downloadReport('csv'); });
});

// ---------------------------------------------------------------------------
// Reporte descargable (Excel / CSV)
// ---------------------------------------------------------------------------

/**
 * Genera y descarga un reporte de usuarios respetando los filtros activos.
 * Usa XMLHttpRequest (no fetch) para evitar el interceptor global de app.js.
 * @param {'excel'|'csv'} fmt
 */
function downloadReport(fmt) {
    const token = localStorage.getItem('jwt_token');
    if (!token) {
        showToast('Sesión no iniciada', 'danger');
        return;
    }

    // Lee los mismos filtros que loadUsers() con lectura defensiva
    const name     = document.getElementById('filter-name')?.value?.trim() || '';
    const roleId   = document.getElementById('filter-role')?.value || '';
    const isActive = document.getElementById('filter-active')?.value || '';
    const dateFrom = document.getElementById('filter-from')?.value || '';
    const dateTo   = document.getElementById('filter-to')?.value || '';

    const params = new URLSearchParams({ format: fmt });
    if (name)          params.set('name', name);
    if (roleId)        params.set('role_id', roleId);
    if (isActive !== '') params.set('is_active', isActive);
    if (dateFrom)      params.set('created_from', dateFrom);
    if (dateTo)        params.set('created_to', dateTo);

    const btnLabel = fmt === 'excel' ? 'Excel' : 'CSV';
    const ext      = fmt === 'excel' ? 'xlsx' : 'csv';
    const fecha    = new Date().toISOString().slice(0, 10);
    const filename = `reporte_usuarios_${fecha}.${ext}`;

    showToast(`Generando reporte ${btnLabel}…`, 'info');

    const xhr = new XMLHttpRequest();
    xhr.open('GET', `${USERS_API}/reporte?${params.toString()}`, true);
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    xhr.responseType = 'blob';

    xhr.onload = function () {
        if (xhr.status === 200) {
            const blob = new Blob([xhr.response]);
            const url  = URL.createObjectURL(blob);
            const a    = document.createElement('a');
            a.href     = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            showToast(`Reporte ${btnLabel} descargado correctamente`, 'success');
        } else if (xhr.status === 401) {
            showToast('Sesión expirada, vuelve a iniciar sesión', 'danger');
        } else {
            showToast(`Error al generar el reporte ${btnLabel} (${xhr.status})`, 'danger');
        }
    };

    xhr.onerror = function () {
        showToast('Error de red al descargar el reporte', 'danger');
    };

    xhr.send();
}