// ============================================================================
// Panel Principal (Dashboard) - Resumen operativo desde una sola petición
// GET /api/dashboard/resumen. Renderiza la barra de caja, KPIs, gráfico de
// barras (Chart.js UMD 4.4.1), top productos, stock crítico, pendientes,
// últimas ventas y accesos rápidos. Las fechas "hoy/ayer/semana" las calcula
// el backend en America/Guatemala (UTC-6); en el navegador solo se formatean.
// ============================================================================

let dashChartInstance = null;
let dashChartToken = 0;

// ---------------------------------------------------------------------------
// Utilidades
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

// Convierte "YYYY-MM-DD" en una fecha local (sin interpretarla como UTC, para
// no desplazarla con la zona horaria del navegador).
function parseLocalDate(str) {
    if (!str) return null;
    const [y, m, d] = String(str).split('-').map(Number);
    if (!y || !m || !d) return null;
    return new Date(y, m - 1, d);
}

function formatHora(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return '—';
    return d.toLocaleTimeString('es-GT', { hour: '2-digit', minute: '2-digit' });
}

function formatFechaHora(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return '—';
    return d.toLocaleString('es-GT', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}

function esc(texto) {
    return String(texto == null ? '' : texto)
        .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

// ---------------------------------------------------------------------------
// RBAC: qué bloques del panel ve cada rol (reutiliza canAccessView de app.js)
// ---------------------------------------------------------------------------

function dashCanView(viewKey) {
    return typeof window.canAccessView === 'function' ? window.canAccessView(viewKey) : true;
}

const dashBlockAccess = {
    'turno-bar': () => dashCanView('pos') || dashCanView('cash'),
    'kpi-ventas': () => dashCanView('pos'),
    'kpi-metodos': () => dashCanView('pos'),
    'kpi-mermas': () => dashCanView('mermas'),
    'grafico-ventas': () => dashCanView('pos') || dashCanView('reportes'),
    'top-productos': () => dashCanView('reportes') || dashCanView('pos'),
    'stock-critico': () => dashCanView('inventory'),
    'pendientes': () => dashCanView('compras') || dashCanView('traslados'),
    'pendientes-compras': () => dashCanView('compras'),
    'pendientes-traslados': () => dashCanView('traslados'),
    'ultimas-ventas': () => dashCanView('pos'),
    'accesos-rapidos': () => true,
    'qa-venta': () => dashCanView('pos'),
    'qa-caja': () => dashCanView('cash'),
    'qa-merma': () => dashCanView('mermas'),
    'qa-compra': () => dashCanView('compras'),
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
// Render de cada sección (defensivo: nunca rompe el resto del panel)
// ---------------------------------------------------------------------------

function renderTurno(turno) {
    const badge = document.getElementById('dash-turno-badge');
    const detalle = document.getElementById('dash-turno-detalle');

    if (turno && turno.estado) {
        setClase('dash-turno-badge', 'badge rounded-pill bg-success-subtle text-success');
        if (badge) badge.innerHTML = '<i class="bi bi-circle-fill me-1"></i>Abierto';

        const cajero = turno.cajero || 'Sin cajero asignado';
        const caja = turno.caja ? ` · ${turno.caja}` : '';
        const sucursal = turno.sucursal ? ` · ${turno.sucursal}` : '';
        const apertura = turno.fecha_apertura ? ` · Abierta a las ${formatHora(turno.fecha_apertura)}` : '';
        const fondo = turno.monto_apertura != null ? ` · Fondo inicial ${formatoQuetzal(turno.monto_apertura)}` : '';
        setTexto('dash-turno-detalle', `Cajero: ${cajero}${caja}${sucursal}${apertura}${fondo}`);
    } else {
        setClase('dash-turno-badge', 'badge rounded-pill bg-secondary-subtle text-secondary');
        if (badge) badge.innerHTML = '<i class="bi bi-circle me-1"></i>Cerrado';
        setTexto('dash-turno-detalle', 'No hay un turno de caja abierto. Abre caja para comenzar a vender.');
    }

    const abierto = !!(turno && turno.estado);
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
    const ticket = Number(v.ticket_promedio) || 0;

    setTexto('dash-ventas-hoy', formatoQuetzal(total));
    setTexto('dash-ventas-hoy-detalle', `${cantidad} ${cantidad === 1 ? 'venta' : 'ventas'} · Ticket promedio ${formatoQuetzal(ticket)}`);

    const vsAyer = document.getElementById('dash-ventas-hoy-vs-ayer');
    const variacion = v.variacion_ayer;
    if (vsAyer) {
        if (variacion === null || variacion === undefined) {
            vsAyer.className = 'small fw-medium mt-1 dash-trend-flat';
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
                <div class="dash-list-item">
                    <span class="dash-list-title">${esc(m.nombre)}</span>
                    <span class="dash-list-value">${formatoQuetzal(m.total)}</span>
                </div>`).join('') + `
                <div class="dash-list-item">
                    <span class="dash-list-title fw-semibold">Total</span>
                    <span class="dash-list-value">${formatoQuetzal(totalMetodos)}</span>
                </div>`;
        }
    }
}

function renderMermas(data) {
    const mermas = data && data.mermas_mes;
    setTexto('dash-mermas-mes', formatoQuetzal(mermas));
    setTexto('dash-mermas-mes-detalle', 'pérdidas registradas en el mes');
}

function renderChart(ventas7dias) {
    const datos = Array.isArray(ventas7dias) ? ventas7dias : [];
    const hayDatos = datos.some((d) => (Number(d.total) || 0) > 0);

    dashChartToken += 1;
    if (dashChartInstance) { dashChartInstance.destroy(); dashChartInstance = null; }

    setVisible('dash-chart-skeleton', false);
    setVisible('dash-chart-empty', !hayDatos, true);
    setVisible('dash-chart-wrap', hayDatos, true);

    if (!hayDatos) return;

    const canvas = document.getElementById('dash-ventas-chart');
    if (!canvas || typeof window.Chart === 'undefined') {
        document.getElementById('dash-chart-wrap')?.classList.add('d-none');
        const vacio = document.getElementById('dash-chart-empty');
        if (vacio) { vacio.innerHTML = '<i class="bi bi-bar-chart fs-1 d-block mb-2 opacity-50"></i><span>No se pudo cargar el gráfico (CDN).</span>'; vacio.classList.remove('d-none'); }
        return;
    }

    const labels = datos.map((d) => {
        const fecha = parseLocalDate(d.fecha);
        if (!fecha) return d.fecha || '';
        return fecha.toLocaleDateString('es-GT', { weekday: 'short', day: '2-digit' });
    });
    const valores = datos.map((d) => Number(d.total) || 0);
    const token = dashChartToken;
    let intentos = 0;

    // Chart.js no se recupera si se instancia con el contenedor oculto (queda 0x0).
    // Se espera a que el panel esté visible y tenga tamaño real antes de dibujar.
    const dibujar = () => {
        if (token !== dashChartToken) return;
        const wrap = document.getElementById('dash-chart-wrap');
        if (!wrap || wrap.classList.contains('d-none')) return;
        if (!wrap.offsetParent) return;
        if (wrap.clientWidth < 40 || wrap.clientHeight < 40) {
            intentos += 1;
            if (intentos <= 40) {
                setTimeout(dibujar, 250);
            } else {
                setVisible('dash-chart-wrap', false);
                setVisible('dash-chart-empty', true);
            }
            return;
        }

        dashChartInstance = new Chart(canvas, {
            type: 'bar',
            data: {
                labels,
                datasets: [{
                    label: 'Ventas (Q)',
                    data: valores,
                    backgroundColor: 'rgba(13, 115, 119, 0.55)',
                    hoverBackgroundColor: 'rgba(13, 115, 119, 0.8)',
                    borderColor: '#0A5C5E',
                    borderWidth: 1,
                    borderRadius: 6,
                    maxBarThickness: 42,
                }],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => `${formatoQuetzal(ctx.parsed.y)}`,
                        },
                    },
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { callback: (v) => `Q${Number(v).toLocaleString('es-GT')}` },
                    },
                },
            },
        });
    };

    dibujar();
}

function renderTopProductos(top) {
    const lista = document.getElementById('dash-top-productos-list');
    const datos = Array.isArray(top) ? top : [];

    if (lista) {
        setVisible('dash-top-productos-empty', datos.length === 0);
        lista.classList.toggle('d-none', datos.length === 0);
        lista.innerHTML = datos.map((p, i) => `
            <div class="dash-list-item">
                <span class="dash-list-title">${i + 1}. ${esc(p.nombre)}</span>
                <span class="dash-list-value">${formatoQuetzal(p.total)}</span>
            </div>
            <div class="px-1 pb-2" style="margin-top:-4px;">
                <span class="small text-muted">${Number(p.cantidad) || 0} unidades</span>
            </div>`).join('');
    }
}

function renderStock(stockLista, total) {
    const lista = document.getElementById('dash-stock-list');
    const datos = Array.isArray(stockLista) ? stockLista : [];

    if (lista) {
        setVisible('dash-stock-empty', datos.length === 0);
        lista.classList.toggle('d-none', datos.length === 0);
        lista.innerHTML = datos.slice(0, 5).map((s) => `
            <div class="dash-list-item">
                <div class="dash-list-title">
                    ${esc(s.producto)}
                    <div class="dash-list-sub">${Number(s.stock_actual) || 0} de ${Number(s.stock_minimo) || 0} · ${esc(s.sucursal || 'Sin sucursal')}</div>
                </div>
                <span class="badge bg-danger rounded-pill px-3 py-1">Bajo</span>
            </div>`).join('');
    }

    // El encabezado conserva el título; el conteo total se agrega en el subtítulo si existe.
    if (typeof total === 'number' && total > 5) {
        const card = document.querySelector('[data-dashblock="stock-critico"]');
        if (card) {
            let note = card.querySelector('.dash-stock-more');
            if (!note) {
                note = document.createElement('div');
                note.className = 'small text-muted mt-2 dash-stock-more';
                card.querySelector('.card-body')?.appendChild(note);
            }
            note.textContent = `Y ${total - 5} ${total - 5 === 1 ? 'producto más' : 'productos más'} en stock crítico.`;
        }
    } else {
        document.querySelector('.dash-stock-more')?.remove();
    }
}

function renderPendientes(ordenes, traslados) {
    const ordDatos = Array.isArray(ordenes) ? ordenes : [];
    const trDatos = Array.isArray(traslados) ? traslados : [];

    const ordLista = document.getElementById('dash-ordenes-list');
    if (ordLista && dashCanView('compras')) {
        setVisible('dash-ordenes-empty', ordDatos.length === 0);
        ordLista.classList.toggle('d-none', ordDatos.length === 0);
        ordLista.innerHTML = ordDatos.map((o) => `
            <div class="dash-list-item">
                <div class="dash-list-title">
                    ${esc(o.proveedor || 'Proveedor')}
                    <div class="dash-list-sub">Orden #${o.id_orden} · ${o.fecha_emision || '—'}</div>
                </div>
                <span class="dash-list-value">${formatoQuetzal(o.total_estimado)}</span>
            </div>`).join('');
    }

    const trLista = document.getElementById('dash-traslados-list');
    if (trLista && dashCanView('traslados')) {
        setVisible('dash-traslados-empty', trDatos.length === 0);
        trLista.classList.toggle('d-none', trDatos.length === 0);
        trLista.innerHTML = trDatos.map((t) => `
            <div class="dash-list-item">
                <div class="dash-list-title">
                    ${esc(t.producto)}
                    <div class="dash-list-sub">${esc(t.origen || '—')} → ${esc(t.destino || '—')} · ${Number(t.cantidad) || 0} uds</div>
                </div>
                <span class="badge bg-warning text-dark rounded-pill px-3 py-1">En tránsito</span>
            </div>`).join('');
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
                <td class="fw-semibold">#${v.folio}</td>
                <td class="small text-muted">${formatHora(v.fecha)}</td>
                <td class="text-end fw-semibold text-teal">${formatoQuetzal(v.total)}</td>
                <td class="small">${esc(v.vendedor) || '—'}</td>
            </tr>`).join('');
    }
}

// ---------------------------------------------------------------------------
// Carga de datos y estados
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
        renderMermas(data);
        renderChart(data.ventas_7dias);
        renderTopProductos(data.top_productos);
        renderStock(data.stock_critico_lista, data.stock_critico);
        renderPendientes(data.ordenes_pendientes, data.traslados_pendientes);
        renderUltimasVentas(data.ultimas_ventas);

    } catch (error) {
        console.error('Error al cargar el resumen del dashboard:', error);
        if (typeof window.showToast === 'function') {
            window.showToast('No se pudieron cargar las métricas del panel.', 'danger');
        }
        renderFallbackDashboard();
    }
}

function renderFallbackDashboard() {
    // Ante fallo de conexión: ceros/cabeceras honestas sin romper el resto.
    renderTurno(null);
    renderKPIs(null);
    renderMetodos([]);
    setTexto('dash-mermas-mes', 'Q 0.00');
    setTexto('dash-mermas-mes-detalle', 'pérdidas registradas en el mes');
    renderChart([]);
    setVisible('dash-chart-skeleton', false);
    renderTopProductos([]);
    renderStock([], 0);
    renderPendientes([], []);
    renderUltimasVentas([]);
    setVisible('dash-ultimas-skeleton', false);
}

// ---------------------------------------------------------------------------
// Enlace de acciones (una sola vez al cargar la página)
// ---------------------------------------------------------------------------

function bindDashboardActions() {
    const irA = (viewKey) => (e) => {
        e.preventDefault();
        if (typeof window.openModule === 'function') window.openModule(viewKey);
    };

    const btnPos = document.getElementById('dash-btn-pos');
    if (btnPos) btnPos.addEventListener('click', () => window.openModule('pos'));

    const btnAbrir = document.getElementById('dash-btn-abrir-caja');
    if (btnAbrir) btnAbrir.addEventListener('click', () => window.openModule('caja'));

    const btnCerrar = document.getElementById('dash-btn-cerrar-caja');
    if (btnCerrar) btnCerrar.addEventListener('click', () => window.openModule('caja'));

    const qaVenta = document.getElementById('dash-qa-venta');
    if (qaVenta) qaVenta.addEventListener('click', () => window.openModule('pos'));

    const qaCaja = document.getElementById('dash-qa-caja');
    if (qaCaja) qaCaja.addEventListener('click', () => window.openModule('caja'));

    const qaMerma = document.getElementById('dash-qa-merma');
    if (qaMerma) qaMerma.addEventListener('click', () => window.openModule('mermas'));

    const qaCompra = document.getElementById('dash-qa-compra');
    if (qaCompra) qaCompra.addEventListener('click', () => window.openModule('compras'));

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
    // La carga de datos la dispara renderView('dashboard') -> showDashboardModule(),
    // cuando el contenedor ya está visible (evita crear el gráfico en 0x0).
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}