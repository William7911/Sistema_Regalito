// Módulo de Usuarios - Tienda el Regalito
// Cero datos quemados: Roles y Departamentos se cargan desde la BD.
const USERS_API = '/api/usuarios';
const ROLES_API = '/api/roles';
const DEPARTMENTS_API = '/api/departamentos';

function authHeaders() {
    const token = localStorage.getItem('jwt_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    };
}

// Cargar roles desde la BD y llenar el <select>
async function loadRoles(selectedId = null) {
    const select = document.getElementById('user-role');
    select.innerHTML = '<option value="">Cargando roles...</option>';
    try {
        const res = await fetch(ROLES_API, { headers: authHeaders() });
        if (!res.ok) throw new Error('No se pudieron cargar los roles');
        const roles = await res.json();
        select.innerHTML = '<option value="">-- Seleccione rol --</option>';
        roles.forEach(r => {
            const opt = document.createElement('option');
            opt.value = r.id;
            opt.textContent = r.name;
            if (selectedId && r.id === selectedId) opt.selected = true;
            select.appendChild(opt);
        });
    } catch (err) {
        select.innerHTML = '<option value="">Sin roles disponibles</option>';
        console.error(err);
    }
}

// Cargar departamentos desde la BD y llenar el <select>
async function loadDepartments(selectedId = null) {
    const select = document.getElementById('user-department');
    select.innerHTML = '<option value="">Cargando departamentos...</option>';
    try {
        const res = await fetch(DEPARTMENTS_API, { headers: authHeaders() });
        if (!res.ok) throw new Error('No se pudieron cargar los departamentos');
        const departments = await res.json();
        select.innerHTML = '<option value="">-- Seleccione departamento --</option>';
        departments.forEach(d => {
            const opt = document.createElement('option');
            opt.value = d.id;
            opt.textContent = d.name;
            if (selectedId && d.id === selectedId) opt.selected = true;
            select.appendChild(opt);
        });
    } catch (err) {
        select.innerHTML = '<option value="">Sin departamentos disponibles</option>';
        console.error(err);
    }
}

// Listar usuarios con filtros
async function loadUsers() {
    const tbody = document.getElementById('users-table-body');
    const params = new URLSearchParams();
    const name = document.getElementById('filter-name').value.trim();
    const code = document.getElementById('filter-code').value.trim();
    const isActive = document.getElementById('filter-active').value;
    if (name) params.append('name', name);
    if (code) params.append('code', code);
    if (isActive !== '') params.append('is_active', isActive);

    try {
        const res = await fetch(`${USERS_API}?${params.toString()}`, { headers: authHeaders() });
        if (!res.ok) throw new Error('No se pudieron cargar los usuarios');
        const data = await res.json();

        tbody.innerHTML = data.items.map(u => `
            <tr>
                <td>${u.code}</td>
                <td>${u.name} ${u.lastname}</td>
                <td>${u.username}</td>
                <td>${u.role ? u.role.name : '-'}</td>
                <td>${u.department ? u.department.name : '-'}</td>
                <td><span class="badge ${u.is_active ? 'bg-success' : 'bg-secondary'}">${u.is_active ? 'Activo' : 'Inactivo'}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editUser(${u.id})"><i class="bi bi-pencil"></i></button>
                    ${u.is_active ? `<button class="btn btn-sm btn-outline-danger" onclick="deactivateUser(${u.id})"><i class="bi bi-x-circle"></i></button>` : ''}
                </td>
            </tr>
        `).join('') || '<tr><td colspan="7" class="text-center text-muted">Sin usuarios</td></tr>';
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-danger">${err.message}</td></tr>`;
    }
}

// Limpiar formulario y cargar dropdowns (crear)
async function resetUserForm() {
    document.getElementById('user-form').reset();
    document.getElementById('user-id').value = '';
    document.getElementById('user-password').required = true;
    await Promise.all([loadRoles(), loadDepartments()]);
}

// Cargar un usuario al formulario para editar
async function editUser(userId) {
    try {
        const res = await fetch(`${USERS_API}/${userId}`, { headers: authHeaders() });
        if (!res.ok) throw new Error('No se encontró el usuario');
        const u = await res.json();
        document.getElementById('user-id').value = u.id;
        document.getElementById('user-name').value = u.name;
        document.getElementById('user-lastname').value = u.lastname;
        document.getElementById('user-code').value = u.code;
        document.getElementById('user-username').value = u.username;
        document.getElementById('user-password').value = '';
        document.getElementById('user-password').required = false;
        document.getElementById('user-active').checked = u.is_active;
        await Promise.all([loadRoles(u.role_id), loadDepartments(u.department_id)]);
        document.getElementById('users-view').scrollIntoView({ behavior: 'smooth' });
    } catch (err) {
        alert(err.message);
    }
}

// Guardar (crear o actualizar)
async function saveUser(event) {
    event.preventDefault();
    const id = document.getElementById('user-id').value;
    const payload = {
        name: document.getElementById('user-name').value.trim(),
        lastname: document.getElementById('user-lastname').value.trim(),
        code: document.getElementById('user-code').value.trim(),
        username: document.getElementById('user-username').value.trim(),
        role_id: parseInt(document.getElementById('user-role').value, 10),
        department_id: parseInt(document.getElementById('user-department').value, 10),
    };
    const password = document.getElementById('user-password').value;
    if (password) payload.password = password;

    const url = id ? `${USERS_API}/${id}` : USERS_API;
    const method = id ? 'PUT' : 'POST';
    if (!id) payload.is_active = true;

    try {
        const res = await fetch(url, {
            method,
            headers: authHeaders(),
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Error al guardar el usuario');
        }
        alert(id ? 'Usuario actualizado' : 'Usuario creado');
        await resetUserForm();
        await loadUsers();
    } catch (err) {
        alert(err.message);
    }
}

// Eliminación lógica (soft delete)
async function deactivateUser(userId) {
    if (!confirm('¿Desactivar este usuario?')) return;
    try {
        const res = await fetch(`${USERS_API}/${userId}`, { method: 'DELETE', headers: authHeaders() });
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || 'Error al desactivar el usuario');
        }
        await loadUsers();
    } catch (err) {
        alert(err.message);
    }
}

// Mostrar el módulo de usuarios y precargar todo
window.showUsersModule = async function () {
    document.getElementById('dashboard-content').classList.add('d-none');
    document.getElementById('users-view').classList.remove('d-none');
    await resetUserForm();
    await loadUsers();
};

window.goToDashboard = function () {
    document.getElementById('users-view').classList.add('d-none');
    document.getElementById('dashboard-content').classList.remove('d-none');
};

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('user-form');
    if (form) {
        form.addEventListener('submit', saveUser);
    }
    const btnNew = document.getElementById('btn-new-user');
    if (btnNew) btnNew.addEventListener('click', resetUserForm);
    const btnFilter = document.getElementById('btn-filter-users');
    if (btnFilter) btnFilter.addEventListener('click', loadUsers);
});