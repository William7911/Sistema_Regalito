// Módulo de Historial de Precios - Tienda el Regalito (Bloque 4)
// Consulta de solo lectura por producto o variante (código de barras/SKU).
const HISTORIAL_API_URL = '/api/historial-precios';
const PRODUCTOS_API_URL = '/api/productos';

const historialState = {
    page: 1,
    pageSize: 10,
    total: 0,
};

function historialAuthHeaders() {
    const token = localStorage.getItem('jwt_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    };
}

function historialFormatDateTime(value) {
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

function historialFormatQty(value) {
    if (value === null || value === undefined) return '-';
    return `Q${Number(value).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

async function loadHistorialProductos() {
    const select = document.getElementById('historial-filter-producto');
    if (!select) return;
    try {
        const res = await fetch(`${PRODUCTOS_API_URL}?limit=500&is_active=true`, { headers: historialAuthHeaders() });
        if (!res.ok) return;
        const data = await res.json();
        select.innerHTML = '<option value="">Todos los productos</option>';
        (data.items || []).forEach(p => {
            const opt = document.createElement('option');
            opt.value = p.id_producto;
            opt.textContent = p.nombre;
            select.appendChild(opt);
        });
    } catch (err) {
        console.error(err);
    }
}

async function resolveVarianteId(codigo) {
    if (!codigo) return null;
    try {
        const res = await fetch(`${PRODUCTOS_API_URL}?barcode=${encodeURIComponent(codigo)}&limit=5`, { headers: historialAuthHeaders() });
        if (!res.ok) return null;
        const data = await res.json();
        const producto = (data.items || [])[0];
        if (!producto || !producto.variantes || !producto.variantes.length) return null;
        return producto.variantes[0].id_variante;
    } catch (err) {
        return null;
    }
}

async function loadHistorial() {
    const tbody = document.getElementById('historial-table-body');
    const empty = document.getElementById('historial-empty');
    if (!tbody) return;

    const productoId = document.getElementById('historial-filter-producto')?.value || '';
    const codigo = (document.getElementById('historial-filter-variante')?.value || '').trim();
    const desde = document.getElementById('historial-filter-desde')?.value || '';
    const hasta = document.getElementById('historial-filter-hasta')?.value || '';

    let params = new URLSearchParams();
    if (codigo) {
        const varianteId = await resolveVarianteId(codigo);
        if (!varianteId) {
            showToast('No se encontró un producto con ese código de barras/SKU.', 'warning');
            return;
        }
        params.append('id_variante', varianteId);
    } else if (productoId) {
        params.append('id_producto', productoId);
    }
    if (desde) params.append('fecha_desde', desde);
    if (hasta) params.append('fecha_hasta', hasta);
    params.append('limit', historialState.pageSize);
    params.append('offset', (historialState.page - 1) * historialState.pageSize);

    if (tbody && typeof window.renderSkeletonTable === 'function') {
        tbody.innerHTML = window.renderSkeletonTable(6, Math.min(historialState.pageSize, 6));
    }

    try {
        const res = await fetch(`${HISTORIAL_API_URL}?${params.toString()}`, { headers: historialAuthHeaders() });
        if (!res.ok) {
            const err = await res.json().catch(() => null);
            showToast((err && err.detail) || 'No se pudieron cargar los cambios de precio', 'danger');
            return;
        }
        const data = await res.json();
        if (data.items.length) {
            tbody.innerHTML = data.items.map(h => `
            <tr>
                <td>${h.id_historial}</td>
                <td>${h.producto_nombre || `Producto #${h.producto_id || '-'}`}</td>
                <td>${h.variante_codigo_barras || h.id_variante}</td>
                <td>${historialFormatQty(h.precio_anterior)}</td>
                <td>${historialFormatQty(h.precio_nuevo)}</td>
                <td>${h.usuario_nombre || `Usuario #${h.id_usuario}`}</td>
                <td>${historialFormatDateTime(h.fecha_modificacion)}</td>
            </tr>`).join('');
            tbody.closest('.table-responsive').classList.remove('d-none');
            if (empty) empty.classList.add('d-none');
        } else {
            tbody.innerHTML = '';
            tbody.closest('.table-responsive').classList.add('d-none');
            if (empty) empty.classList.remove('d-none');
        }
        historialState.total = data.total || 0;
        renderHistorialPagination();
    } catch (err) {
        showToast(err.message, 'danger');
    }
}

function renderHistorialPagination() {
    const pagination = document.getElementById('historial-pagination');
    if (!pagination) return;
    const totalPages = Math.max(1, Math.ceil(historialState.total / historialState.pageSize));
    if (historialState.page > totalPages) historialState.page = totalPages;
    const info = document.getElementById('historial-page-info');
    const prev = document.getElementById('historial-prev-page');
    const next = document.getElementById('historial-next-page');
    if (info) info.textContent = `Página ${historialState.page} de ${totalPages}`;
    if (prev) prev.disabled = historialState.page <= 1;
    if (next) next.disabled = historialState.page >= totalPages;
    pagination.classList.toggle('d-none', historialState.total === 0);
}

window.showHistorialModule = async function () {
    historialState.page = 1;
    await loadHistorialProductos();
    await loadHistorial();
};

document.addEventListener('DOMContentLoaded', () => {
    const btnFilter = document.getElementById('btn-filter-historial');
    if (btnFilter) btnFilter.addEventListener('click', () => { historialState.page = 1; loadHistorial(); });
    const pageSize = document.getElementById('historial-page-size');
    if (pageSize) pageSize.addEventListener('change', () => {
        historialState.pageSize = parseInt(pageSize.value, 10);
        historialState.page = 1;
        loadHistorial();
    });
    const prevBtn = document.getElementById('historial-prev-page');
    if (prevBtn) prevBtn.addEventListener('click', () => {
        if (historialState.page > 1) { historialState.page--; loadHistorial(); }
    });
    const nextBtn = document.getElementById('historial-next-page');
    if (nextBtn) nextBtn.addEventListener('click', () => {
        const totalPages = Math.max(1, Math.ceil(historialState.total / historialState.pageSize));
        if (historialState.page < totalPages) { historialState.page++; loadHistorial(); }
    });
});
