// Módulo de Roles y Permisos - Tienda el Regalito (Bloque 4)
// Pantalla dentro de Roles para marcar qué permisos tiene cada rol.
// Cero alert()/confirm() nativos; usa toasts y modales con backdrop estático.
const ROLES_API_URL = '/api/roles';

let rolesPermisosEditingId = null;

function rolesAuthHeaders() {
    const token = localStorage.getItem('jwt_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    };
}

function rolesGetModal(id) {
    const el = document.getElementById(id);
    return el && window.bootstrap ? bootstrap.Modal.getOrCreateInstance(el) : null;
}

async function rolesListLoad() {
    const tbody = document.getElementById('roles-table-body');
    const empty = document.getElementById('roles-empty');
    if (!tbody) return;
    try {
        const res = await fetch(`${ROLES_API_URL}?include_inactive=true`, { headers: rolesAuthHeaders() });
        if (!res.ok) {
            const err = await res.json().catch(() => null);
            showToast((err && err.detail) || 'No se pudieron cargar los roles', 'danger');
            return;
        }
        const roles = await res.json();
        if (roles.length) {
            tbody.innerHTML = roles.map(r => {
                const activo = r.estado === 'Activo';
                return `
                <tr>
                    <td>${r.id_rol}</td>
                    <td>${r.nombre}</td>
                    <td>${r.descripcion || '-'}</td>
                    <td><span class="badge ${activo ? 'bg-success' : 'bg-secondary'}">${activo ? 'Activo' : 'Inactivo'}</span></td>
                    <td class="text-end">
                        <button class="btn btn-sm btn-outline-success" onclick="openRolePermisos(${r.id_rol})" title="Permisos"><i class="bi bi-shield-check"></i></button>
                        <button class="btn btn-sm btn-outline-primary" onclick="editRole(${r.id_rol})" title="Editar"><i class="bi bi-pencil"></i></button>
                        ${activo ? `<button class="btn btn-sm btn-outline-danger" onclick="deactivateRole(${r.id_rol})" title="Desactivar"><i class="bi bi-x-circle"></i></button>` : ''}
                    </td>
                </tr>`;
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

function resetRoleForm() {
    document.getElementById('role-id').value = '';
    document.getElementById('role-nombre').value = '';
    document.getElementById('role-nombre').classList.remove('is-invalid');
    document.getElementById('role-nombre').nextElementSibling.textContent = '';
    document.getElementById('role-descripcion').value = '';
    document.getElementById('role-estado-wrap').style.display = 'none';
    document.getElementById('role-estado').value = 'Activo';
    document.getElementById('role-modal-title').textContent = 'Nuevo Rol';
    const text = document.getElementById('btn-save-role-text');
    if (text) text.textContent = 'Guardar';
}

function openCreateRole() {
    resetRoleForm();
    const modal = rolesGetModal('role-modal');
    if (modal) modal.show();
    setTimeout(() => document.getElementById('role-nombre')?.focus(), 350);
}

async function editRole(roleId) {
    try {
        const res = await fetch(`${ROLES_API_URL}/${roleId}`, { headers: rolesAuthHeaders() });
        if (!res.ok) {
            const err = await res.json().catch(() => null);
            showToast((err && err.detail) || 'No se encontró el rol', 'danger');
            return;
        }
        const r = await res.json();
        resetRoleForm();
        document.getElementById('role-id').value = r.id_rol;
        document.getElementById('role-nombre').value = r.nombre;
        document.getElementById('role-descripcion').value = r.descripcion || '';
        document.getElementById('role-estado-wrap').style.display = '';
        document.getElementById('role-estado').value = r.estado === 'Inactivo' ? 'Inactivo' : 'Activo';
        document.getElementById('role-modal-title').textContent = 'Editar Rol';
        document.getElementById('btn-save-role-text').textContent = 'Actualizar';
        const modal = rolesGetModal('role-modal');
        if (modal) modal.show();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

async function saveRole(event) {
    event.preventDefault();
    const id = document.getElementById('role-id').value;
    const nombre = document.getElementById('role-nombre').value.trim();
    const descripcion = document.getElementById('role-descripcion').value.trim();
    const estado = document.getElementById('role-estado').value;

    if (!nombre) {
        const input = document.getElementById('role-nombre');
        input.classList.add('is-invalid');
        input.nextElementSibling.textContent = 'Este campo es obligatorio.';
        input.focus();
        return;
    }

    const btn = document.getElementById('btn-save-role');
    const spinner = document.getElementById('btn-save-role-spinner');
    const text = document.getElementById('btn-save-role-text');
    btn.disabled = true;
    if (spinner) spinner.classList.remove('d-none');
    const base = id ? 'Actualizando...' : 'Guardando...';
    if (text) text.textContent = base;

    const payload = { nombre };
    if (descripcion) payload.descripcion = descripcion;
    if (estado) payload.estado = estado;

    try {
        const url = id ? `${ROLES_API_URL}/${id}` : ROLES_API_URL;
        const res = await fetch(url, { method: id ? 'PUT' : 'POST', headers: rolesAuthHeaders(), body: JSON.stringify(payload) });
        const data = await res.json().catch(() => null);
        if (!res.ok) {
            if (res.status === 422 && Array.isArray(data && data.detail)) {
                const err = data.detail[0];
                const field = err.loc && err.loc.length ? err.loc[err.loc.length - 1] : null;
                if (field === 'nombre') {
                    const input = document.getElementById('role-nombre');
                    input.classList.add('is-invalid');
                    input.nextElementSibling.textContent = 'Este campo es obligatorio.';
                }
            } else {
                showToast((data && data.detail) || 'No se pudo guardar el rol', 'danger');
            }
            return;
        }
        const modal = rolesGetModal('role-modal');
        if (modal) modal.hide();
        showToast(id ? 'Rol actualizado correctamente.' : 'Rol creado correctamente.', 'success');
        await rolesListLoad();
    } catch (err) {
        showToast(err.message, 'danger');
    } finally {
        btn.disabled = false;
        if (spinner) spinner.classList.add('d-none');
        if (text) text.textContent = id ? 'Actualizar' : 'Guardar';
    }
}

async function deactivateRole(roleId) {
    const ok = await confirmModal('¿Desactivar este rol? Los usuarios con este rol se quedarán sin sus accesos.');
    if (!ok) return;
    try {
        const res = await fetch(`${ROLES_API_URL}/${roleId}`, { method: 'DELETE', headers: rolesAuthHeaders() });
        if (!res.ok) {
            const err = await res.json().catch(() => null);
            showToast((err && err.detail) || 'Error al desactivar el rol', 'danger');
            return;
        }
        showToast('Rol desactivado correctamente.', 'success');
        await rolesListLoad();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

// ---------------------------------------------------------------------------
// Permisos del rol
// ---------------------------------------------------------------------------

async function openRolePermisos(roleId) {
    rolesPermisosEditingId = roleId;
    const body = document.getElementById('role-permisos-body');
    const btn = document.getElementById('btn-save-role-permisos');
    if (body) body.innerHTML = typeof window.renderSkeletonCard === 'function' ? window.renderSkeletonCard(5) : '<div class="text-center text-muted py-4">Cargando permisos...</div>';
    if (btn) btn.disabled = true;
    const modal = rolesGetModal('role-permisos-modal');
    if (modal) modal.show();
    document.getElementById('role-permisos-modal-title').textContent = `Permisos del rol #${roleId}`;

    try {
        const [catRes, asigRes] = await Promise.all([
            fetch(`${ROLES_API_URL}/permisos/catalogo`, { headers: rolesAuthHeaders() }),
            fetch(`${ROLES_API_URL}/${roleId}/permisos`, { headers: rolesAuthHeaders() }),
        ]);
        if (!catRes.ok || !asigRes.ok) {
            const err = await catRes.json().catch(() => null);
            showToast((err && err.detail) || 'No se pudieron cargar los permisos', 'danger');
            if (btn) btn.disabled = false;
            return;
        }
        const catalogo = await catRes.json();
        const asignados = new Set(await asigRes.json());

        const grupos = {};
        catalogo.forEach(p => {
            (grupos[p.modulo] = grupos[p.modulo] || []).push(p);
        });

        const myRoleId = parseInt(localStorage.getItem('user_id_rol') || '0', 10);
        const isEditingAdmin = (roleId === 1);
        const isEditingSelf = (myRoleId > 0 && myRoleId === roleId);

        if (body) {
            body.innerHTML = Object.keys(grupos).sort().map(mod => {
                const checks = grupos[mod].map(p => {
                    const isCriticoAdmin = isEditingAdmin && (p.codigo === 'ROL_ADMIN' || p.codigo === 'USUARIO_ADMIN');
                    const isCriticoSelf = isEditingSelf && (p.codigo === 'ROL_ADMIN');
                    const isChecked = asignados.has(p.codigo) || isCriticoAdmin;
                    const isDisabled = isCriticoAdmin || isCriticoSelf;
                    let badge = '';
                    if (isCriticoAdmin) {
                        badge = '<span class="badge bg-warning text-dark ms-1">Crítico (Administradora)</span>';
                    } else if (isCriticoSelf) {
                        badge = '<span class="badge bg-info text-dark ms-1">Tu rol actual (Acceso a Roles)</span>';
                    }
                    return `
                    <div class="form-check mb-1">
                        <input class="form-check-input role-permiso-cb" type="checkbox" value="${p.codigo}" id="perm-${p.codigo}" ${isChecked ? 'checked' : ''} ${isDisabled ? 'disabled' : ''} data-critico="${isDisabled ? '1' : '0'}">
                        <label class="form-check-label small" for="perm-${p.codigo}">
                            <strong>${p.codigo}</strong>
                            ${p.descripcion ? `<span class="text-muted">— ${p.descripcion}</span>` : ''}
                            ${badge}
                        </label>
                    </div>`;
                }).join('');
                return `
                    <div class="card border-0 shadow-sm rounded-3 mb-3 bg-light">
                        <div class="card-header bg-white fw-semibold"><i class="bi bi-grid me-1"></i>${mod}</div>
                        <div class="card-body pt-2 pb-2">${checks}</div>
                    </div>`;
            }).join('') || '<div class="text-center text-muted py-4">No hay permisos disponibles.</div>';
        }
        if (btn) btn.disabled = false;
    } catch (err) {
        showToast(err.message, 'danger');
        if (btn) btn.disabled = false;
    }
}

async function saveRolePermisos() {
    if (rolesPermisosEditingId == null) return;
    const codigos = Array.from(document.querySelectorAll('.role-permiso-cb:checked')).map(el => el.value);
    const btn = document.getElementById('btn-save-role-permisos');
    const spinner = document.getElementById('btn-save-role-permisos-spinner');
    btn.disabled = true;
    if (spinner) spinner.classList.remove('d-none');
    try {
        const res = await fetch(`${ROLES_API_URL}/${rolesPermisosEditingId}/permisos`, {
            method: 'PUT',
            headers: rolesAuthHeaders(),
            body: JSON.stringify({ codigos }),
        });
        const data = await res.json().catch(() => null);
        if (!res.ok) {
            showToast((data && data.detail) || 'No se pudieron guardar los permisos', 'danger');
            return;
        }
        const modal = rolesGetModal('role-permisos-modal');
        if (modal) modal.hide();
        showToast('Permisos actualizados correctamente.', 'success');
        await rolesListLoad();
    } catch (err) {
        showToast(err.message, 'danger');
    } finally {
        btn.disabled = false;
        if (spinner) spinner.classList.add('d-none');
    }
}

// ---------------------------------------------------------------------------
// Navegación / arranque
// ---------------------------------------------------------------------------

window.showRolesModule = async function () {
    resetRoleForm();
    await rolesListLoad();
};

window.openRolePermisos = openRolePermisos;
window.editRole = editRole;

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('role-form');
    if (form) form.addEventListener('submit', saveRole);
    const btnNew = document.getElementById('btn-new-role');
    if (btnNew) btnNew.addEventListener('click', openCreateRole);
    const btnSavePermisos = document.getElementById('btn-save-role-permisos');
    if (btnSavePermisos) btnSavePermisos.addEventListener('click', saveRolePermisos);
    const modalEl = document.getElementById('role-modal');
    if (modalEl) modalEl.addEventListener('hidden.bs.modal', resetRoleForm);
    document.querySelectorAll('#role-modal [data-bs-close-modal]').forEach(btn => {
        btn.addEventListener('click', () => { resetRoleForm(); rolesGetModal('role-modal')?.hide(); });
    });
});
