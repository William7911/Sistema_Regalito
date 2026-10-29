// ============================================================================
// Panel Principal (Dashboard) - Centro de Control Diario ("HOY")
// Interfaz minimalista estilo Square / Loyverse para comercio retail en Guatemala.
// Datos cargados desde GET /api/dashboard/resumen.
// ============================================================================

// ---------------------------------------------------------------------------
// Utilidades de formato
// ---------------------------------------------------------------------------

function formatoQuetzal(value) {
    const numero = new Intl.NumberFormat('es-GT', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(Number(value) || 0);
    return `Q ${numero}`;
}

function setTexto(id, texto) {
    const el = document.getElementById(id);
    if (el) el.textContent = texto;
}

function setClase(id, clase) {
    const el = document.getElementById(id);
    if (el) el.className = clase;
}

function setVisible(id, visible, hasClassDNone = true) {
    const el = document.getElementById(id);
    if (!el) return;
    if (hasClassDNone) el.classList.toggle('d-none', !visible);
}

function formatHora(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return '—';
    return d.toLocaleTimeString('es-GT', { hour: '2-digit', minute: '2-digit' });
}

function esc(texto) {
    return String(texto == null ? '' : texto)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// ---------------------------------------------------------------------------
// Control de Acceso RBAC
// ---------------------------------------------------------------------------

function dashCanView(viewKey) {
    return typeof window.canAccessView === 'function' ? window.canAccessView(viewKey) : true;
}

const dashBlockAccess = {
    'turno-bar': () => dashCanView('pos') || dashCanView('cash'),
    'resumen-hoy': () => true,
    'kpi-ventas': () => dashCanView('pos'),
    'kpi-metodos': () => dashCanView('pos'),
    'kpi-efectivo-caja': () => dashCanView('cash') || dashCanView('pos'),
    'ultimas-ventas': () => dashCanView('pos'),
    'stock-critico': () => dashCanView('inventory'),
};

function toggleDashboardBlocks() {
    document.querySelectorAll('[data-dashblock]').forEach((el) => {
        const key = el.getAttribute('data-dashblock');
        const allowedFn = dashBlockAccess[key];
        const allowed = typeof allowedFn === 'function' ? allowedFn() : true;
        el.classList.toggle('d-none', !allowed);
    });
}

// ---------------------------------------------------------------------------
// Renderizado de Componentes
// ---------------------------------------------------------------------------

function renderTurno(turno) {
    const badge = document.getElementById('dash-turno-badge');

    if (turno && turno.estado && (turno.estado === 'Abierto' || turno.estado === 'Abierta')) {
        setClase('dash-turno-badge', 'badge rounded-pill bg-success-subtle text-success');
        if (badge) badge.innerHTML = '<i class="bi bi-circle-fill me-1"></i>Abierta';

        const cajero = turno.cajero || 'Sin cajero asignado';
        const caja = turno.caja ? ` · ${turno.caja}` : '';
        const apertura = turno.fecha_apertura ? ` · Abierta a las ${formatHora(turno.fecha_apertura)}` : '';
        const fondo = turno.monto_apertura != null ? ` · Fondo inicial ${formatoQuetzal(turno.monto_apertura)}` : '';
        setTexto('dash-turno-detalle', `Cajero: ${cajero}${caja}${apertura}${fondo}`);
    } else {
        setClase('dash-turno-badge', 'badge rounded-pill bg-secondary-subtle text-secondary');
        if (badge) badge.innerHTML = '<i class="bi bi-circle me-1"></i>Cerrada';
        setTexto('dash-turno-detalle', 'No hay un turno de caja abierto actualmente. Abre caja para registrar ventas.');
    }

    const abierto = !!(turno && turno.estado && (turno.estado === 'Abierto' || turno.estado === 'Abierta'));
    const puedePos = dashCanView('pos');
    const puedeCaja = dashCanView('cash');

    setVisible('dash-btn-pos', puedePos);
    setVisible('dash-btn-abrir-caja', puedeCaja && !abierto);
    setVisible('dash-btn-cerrar-caja', puedeCaja && abierto);
}

function renderKPIs(data) {
    const v = (data && data.ventas_hoy) || {};
    const total = Number(v.total) || 0;
    const cantidad = Number(v.cantidad) || 0;

    setTexto('dash-ventas-hoy', formatoQuetzal(total));
    // Texto simple sin términos técnicos: solo cantidad de ventas realizadas
    setTexto('dash-ventas-hoy-detalle', `${cantidad} ${cantidad === 1 ? 'venta realizada' : 'ventas realizadas'}`);

    const vsAyer = document.getElementById('dash-ventas-hoy-vs-ayer');
    const variacion = v.variacion_ayer;
    if (vsAyer) {
        if (variacion === null || variacion === undefined) {
            vsAyer.className = 'small fw-medium mt-1 dash-trend-flat text-muted';
            vsAyer.innerHTML = `<i class="bi bi-dash-circle me-1"></i>Sin ventas ayer`;
        } else {
            const pct = Number(variacion) || 0;
            const up = pct >= 0;
            vsAyer.classList.remove('dash-trend-up', 'dash-trend-down', 'dash-trend-flat');
            vsAyer.classList.add('small', 'fw-medium', 'mt-1', up ? 'dash-trend-up' : 'dash-trend-down');
            vsAyer.innerHTML = `${up ? '<i class="bi bi-arrow-up-right"></i>' : '<i class="bi bi-arrow-down-right"></i>'} ${Math.abs(pct).toLocaleString('es-GT', { maximumFractionDigits: 1 })}% ${up ? 'más' : 'menos'} vs ayer`;
        }
    }

    setVisible('dash-ventas-hoy-empty', cantidad === 0 && dashCanView('pos'));
}

function renderMetodos(metodos) {
    const lista = document.getElementById('dash-metodos-list');
    const datos = Array.isArray(metodos) ? metodos : [];
    const totalMetodos = datos.reduce((acc, m) => acc + (Number(m.total) || 0), 0);

    if (lista) {
        if (!datos.length) {
            lista.classList.add('d-none');
            setVisible('dash-metodos-empty', true);
        } else {
            lista.classList.remove('d-none');
            setVisible('dash-metodos-empty', false);

            lista.innerHTML = datos.map((m) => `
                <div class="dash-list-item d-flex justify-content-between align-items-center py-1">
                    <span class="dash-list-title text-muted">${esc(m.nombre)}</span>
                    <span class="dash-list-value fw-bold text-dark">${formatoQuetzal(m.total)}</span>
                </div>`).join('') + `
                <div class="dash-list-item d-flex justify-content-between align-items-center pt-2 mt-1 border-top">
                    <span class="dash-list-title fw-bold text-dark">Total recaudado</span>
                    <span class="dash-list-value fw-bold text-teal">${formatoQuetzal(totalMetodos)}</span>
                </div>`;
        }
    }
}

function renderEfectivoCaja(data) {
    const turno = data && data.turno_actual;
    const estaAbierto = turno && (turno.estado === 'Abierto' || turno.estado === 'Abierta');

    if (estaAbierto) {
        const fondo = Number(turno.monto_apertura) || 0;
        const metodos = Array.isArray(data.ventas_por_metodo) ? data.ventas_por_metodo : [];
        const efectivoMetodo = metodos.find((m) => m.nombre && m.nombre.toLowerCase().includes('efectivo'));
        const ventasEfectivo = efectivoMetodo ? (Number(efectivoMetodo.total) || 0) : 0;

        const totalEsperado = data.efectivo_esperado != null
            ? Number(data.efectivo_esperado)
            : (fondo + ventasEfectivo);

        setTexto('dash-efectivo-caja', formatoQuetzal(totalEsperado));
        setTexto('dash-efectivo-caja-detalle', `Fondo inicial ${formatoQuetzal(fondo)} + Ventas en efectivo ${formatoQuetzal(ventasEfectivo)}`);
    } else {
        setTexto('dash-efectivo-caja', 'Q 0.00');
        setTexto('dash-efectivo-caja-detalle', 'Caja cerrada · Abre turno para iniciar');
    }
}

function renderUltimasVentas(ventas) {
    const datos = Array.isArray(ventas) ? ventas : [];
    const tbody = document.getElementById('dash-ultimas-ventas-body');

    setVisible('dash-ultimas-skeleton', false);
    setVisible('dash-ultimas-container', datos.length > 0);
    setVisible('dash-ultimas-empty', datos.length === 0);

    if (tbody && datos.length) {
        tbody.innerHTML = datos.map((v) => `
            <tr>
                <td class="fw-bold px-3 text-dark">#${v.folio}</td>
                <td class="small text-muted">${formatHora(v.fecha)}</td>
                <td class="small text-center"><span class="badge bg-light text-dark border px-2 py-1">${Number(v.articulos) || 1} uds</span></td>
                <td class="text-end fw-bold text-teal px-3">${formatoQuetzal(v.total)}</td>
            </tr>`).join('');
    }
}

function renderStock(stockLista, total) {
    const lista = document.getElementById('dash-stock-list');
    const datos = Array.isArray(stockLista) ? stockLista : [];

    if (lista) {
        setVisible('dash-stock-empty', datos.length === 0);
        lista.classList.toggle('d-none', datos.length === 0);
        lista.innerHTML = datos.slice(0, 5).map((s) => `
            <div class="dash-list-item d-flex justify-content-between align-items-center py-2 border-bottom">
                <div class="dash-list-title pe-2">
                    <div class="fw-semibold text-dark">${esc(s.producto)}</div>
                    <div class="small text-muted">${Number(s.stock_actual) || 0} disponibles · Mínimo: ${Number(s.stock_minimo) || 3}</div>
                </div>
                <span class="badge bg-danger-subtle text-danger border border-danger-subtle rounded-pill px-3 py-1 fw-bold">Por agotar</span>
            </div>`).join('');
    }

    if (typeof total === 'number' && total > 5) {
        const card = document.querySelector('[data-dashblock="stock-critico"]');
        if (card) {
            let note = card.querySelector('.dash-stock-more');
            if (!note) {
                note = document.createElement('div');
                note.className = 'small text-muted mt-2 dash-stock-more text-center';
                card.querySelector('.card-body')?.appendChild(note);
            }
            note.textContent = `Y ${total - 5} productos más por agotarse.`;
        }
    } else {
        document.querySelector('.dash-stock-more')?.remove();
    }
}

// ---------------------------------------------------------------------------
// Carga de datos desde Backend
// ---------------------------------------------------------------------------

async function cargarResumenDashboard() {
    toggleDashboardBlocks();

    const token = localStorage.getItem('jwt_token');
    if (!token) {
        if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
        return;
    }

    try {
        const response = await fetch('/api/dashboard/resumen', {
            method: 'GET',
            headers: { 'Authorization': `Bearer ${token}` },
        });

        if (response.status === 401) {
            if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
            return;
        }

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const data = await response.json();

        renderTurno(data.turno_actual);
        renderKPIs(data);
        renderMetodos(data.ventas_por_metodo);
        renderEfectivoCaja(data);
        renderUltimasVentas(data.ultimas_ventas);
        renderStock(data.stock_critico_lista, data.stock_critico);

    } catch (error) {
        console.error('Error al cargar el resumen del dashboard:', error);
        if (typeof window.showToast === 'function') {
            window.showToast('No se pudieron cargar las métricas del panel.', 'danger');
        }
        renderFallbackDashboard();
    }
}

function renderFallbackDashboard() {
    renderTurno(null);
    renderKPIs(null);
    renderMetodos([]);
    renderEfectivoCaja(null);
    renderUltimasVentas([]);
    renderStock([], 0);
    setVisible('dash-ultimas-skeleton', false);
}

// ---------------------------------------------------------------------------
// Vinculación de Acciones y Navegación
// ---------------------------------------------------------------------------

function bindDashboardActions() {
    const irA = (viewKey) => (e) => {
        e.preventDefault();
        if (typeof window.openModule === 'function') {
            window.openModule(viewKey);
        } else if (typeof window.navigateTo === 'function') {
            window.navigateTo(viewKey);
        }
    };

    const btnPos = document.getElementById('dash-btn-pos');
    if (btnPos) btnPos.addEventListener('click', () => (window.openModule ? window.openModule('pos') : window.navigateTo('pos')));

    const btnAbrir = document.getElementById('dash-btn-abrir-caja');
    if (btnAbrir) btnAbrir.addEventListener('click', () => (window.openModule ? window.openModule('caja') : window.navigateTo('cash')));

    const btnCerrar = document.getElementById('dash-btn-cerrar-caja');
    if (btnCerrar) btnCerrar.addEventListener('click', () => (window.openModule ? window.openModule('caja') : window.navigateTo('cash')));



    document.querySelectorAll('[data-dash-nav]').forEach((link) => {
        const view = link.getAttribute('data-dash-nav');
        if (view) link.addEventListener('click', irA(view));
    });
}

window.showDashboardModule = async function () {
    await cargarResumenDashboard();
};

function initDashboard() {
    bindDashboardActions();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}
