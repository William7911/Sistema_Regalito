// Módulo de Bitácora de Auditoría - Tienda el Regalito (Bloque 4)
// Pantalla de solo consulta con filtros (usuario, tabla, acción, rango de fechas).
// Acceso controlado por el permiso BITACORA_CONSULTAR (backend).
const BITACORA_API_URL = '/api/bitacora';
const USUARIOS_API_URL = '/api/usuarios';

const bitacoraState = {
    page: 1,
    pageSize: 10,
    total: 0,
};

function bitacoraAuthHeaders() {
    const token = localStorage.getItem('jwt_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    };
}

function bitacoraFormatDateTime(value) {
    if (!value) return '-';
    const d = new Date(value);
    if (isNaN(d.getTime())) return value;
    const dd = String(d.getDate()).padStart(2, '0');
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const yyyy = d.getFullYear();
    const hh = String(d.getHours()).padStart(2, '0');
    const min = String(d.getMinutes()).padStart(2, '0');
    return `${dd}/${mm}/${yyyy} ${hh}:${min}`;
}

function bitacoraAccionBadge(accion) {
    const lower = (accion || '').toUpperCase();
    let cls = 'bg-secondary';
    if (['CREATE', 'CREAR'].includes(lower)) cls = 'bg-success';
    else if (['UPDATE', 'ACTUALIZAR', 'PRECIO'].includes(lower)) cls = 'bg-primary';
    else if (['DELETE', 'DESACTIVAR', 'DEACTIVATE'].includes(lower)) cls = 'bg-danger';
    else if (lower === 'LOGIN') cls = 'bg-info';
    else if (lower === 'VENTA') cls = 'bg-dark';
    return `<span class="badge ${cls}">${accion}</span>`;
}

async function loadBitacoraUsuarios() {
    const select = document.getElementById('bitacora-filter-usuario');
    if (!select) return;
    try {
        const res = await fetch(`${USUARIOS_API_URL}?limit=1000`, { headers: bitacoraAuthHeaders() });
        if (!res.ok) return;
        const data = await res.json();
        select.innerHTML = '<option value="">Todos los usuarios</option>';
        (data.items || []).forEach(u => {
            const opt = document.createElement('option');
            opt.value = u.id_usuario;
            opt.textContent = `${u.nombre_completo} (@${u.username})`;
            select.appendChild(opt);
        });
    } catch (err) {
        console.error(err);
    }
}

async function loadBitacora() {
    const tbody = document.getElementById('bitacora-table-body');
    const empty = document.getElementById('bitacora-empty');
    if (!tbody) return;

    const params = new URLSearchParams();
    const usuario = document.getElementById('bitacora-filter-usuario')?.value || '';
    const tabla = (document.getElementById('bitacora-filter-tabla')?.value || '').trim();
    const accion = (document.getElementById('bitacora-filter-accion')?.value || '').trim();
    const desde = document.getElementById('bitacora-filter-desde')?.value || '';
    const hasta = document.getElementById('bitacora-filter-hasta')?.value || '';

    if (usuario) params.append('id_usuario', usuario);
    if (tabla) params.append('tabla', tabla);
    if (accion) params.append('accion', accion);
    if (desde) params.append('fecha_desde', desde);
    if (hasta) params.append('fecha_hasta', hasta);
    params.append('limit', bitacoraState.pageSize);
    params.append('offset', (bitacoraState.page - 1) * bitacoraState.pageSize);

    if (tbody && typeof window.renderSkeletonTable === 'function') {
        tbody.innerHTML = window.renderSkeletonTable(6, Math.min(bitacoraState.pageSize, 6));
    }

    try {
        const res = await fetch(`${BITACORA_API_URL}?${params.toString()}`, { headers: bitacoraAuthHeaders() });
        if (!res.ok) {
            const err = await res.json().catch(() => null);
            showToast((err && err.detail) || 'No se pudieron cargar los registros de bitácora', 'danger');
            return;
        }
        const data = await res.json();
        if (data.items.length) {
            tbody.innerHTML = data.items.map(b => `
            <tr>
                <td>${b.id_bitacora}</td>
                <td>${b.usuario_nombre || `Usuario #${b.id_usuario}`}</td>
                <td>${b.tabla_afectada}</td>
                <td>${bitacoraAccionBadge(b.accion)}</td>
                <td>${b.descripcion || '-'}</td>
                <td>${bitacoraFormatDateTime(b.fecha_hora)}</td>
            </tr>`).join('');
            tbody.closest('.table-responsive').classList.remove('d-none');
            if (empty) empty.classList.add('d-none');
        } else {
            tbody.innerHTML = '';
            tbody.closest('.table-responsive').classList.add('d-none');
            if (empty) empty.classList.remove('d-none');
        }
        bitacoraState.total = data.total || 0;
        renderBitacoraPagination();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

function renderBitacoraPagination() {
    const pagination = document.getElementById('bitacora-pagination');
    if (!pagination) return;
    const totalPages = Math.max(1, Math.ceil(bitacoraState.total / bitacoraState.pageSize));
    if (bitacoraState.page > totalPages) bitacoraState.page = totalPages;
    const info = document.getElementById('bitacora-page-info');
    const prev = document.getElementById('bitacora-prev-page');
    const next = document.getElementById('bitacora-next-page');
    if (info) info.textContent = `Página ${bitacoraState.page} de ${totalPages}`;
    if (prev) prev.disabled = bitacoraState.page <= 1;
    if (next) next.disabled = bitacoraState.page >= totalPages;
    pagination.classList.toggle('d-none', bitacoraState.total === 0);
}

window.showBitacoraModule = async function () {
    bitacoraState.page = 1;
    await loadBitacoraUsuarios();
    await loadBitacora();
};

document.addEventListener('DOMContentLoaded', () => {
    const btnFilter = document.getElementById('btn-filter-bitacora');
    if (btnFilter) btnFilter.addEventListener('click', () => { bitacoraState.page = 1; loadBitacora(); });
    const pageSize = document.getElementById('bitacora-page-size');
    if (pageSize) pageSize.addEventListener('change', () => {
        bitacoraState.pageSize = parseInt(pageSize.value, 10);
        bitacoraState.page = 1;
        loadBitacora();
    });
    const prevBtn = document.getElementById('bitacora-prev-page');
    if (prevBtn) prevBtn.addEventListener('click', () => {
        if (bitacoraState.page > 1) { bitacoraState.page--; loadBitacora(); }
    });
    const nextBtn = document.getElementById('bitacora-next-page');
    if (nextBtn) nextBtn.addEventListener('click', () => {
        const totalPages = Math.max(1, Math.ceil(bitacoraState.total / bitacoraState.pageSize));
        if (bitacoraState.page < totalPages) { bitacoraState.page++; loadBitacora(); }
    });
});
