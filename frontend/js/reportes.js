const REPORTES_API_URL = '/api/reportes';

// Utilidades locales para formateo y seguridad (autocontenido)
function formatoQuetzal(value) {
    const numero = new Intl.NumberFormat('es-GT', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2,
    }).format(Number(value) || 0);
    return `Q ${numero}`;
}

function esc(texto) {
    return String(texto == null ? '' : texto)
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function toDateString(d) {
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/* ========================================================
   Estado global del MÃ³dulo de Reportes y EstadÃ­sticas
   ========================================================
   Estas variables controlan los componentes dinÃ¡micos del panel:

   - reportesChartTab: pestaÃ±a/pÃ­ldora activa de la grÃ¡fica
     ('tendencia' | 'categoria' | 'hora').
   - reportesChartInstance: instancia viva de Chart.js. Es la Ãºnica que
     se debe destruir con .destroy() antes de re-dibujar sobre el canvas.
   - reportesChartToken: contador anti-carrera. Cada vez que se solicita
     un grÃ¡fico se incrementa; las respuestas asÃ­ncronas que lleguen con
     un token antiguo se descartan (evita pintar datos obsoletos).
   - reportesRankTipo / reportesRankLimite: valores actuales de los
     selects del widget de rankings (tipo_reporte y lÃ­mite Top X).
   - reportesRangoActual: Ãºltimo rango de fechas consultado. Las grÃ¡ficas
     y rankings lo reutilizan cuando el usuario solo cambia de pestaÃ±a o
     de ranking sin presionar "Consultar".
   ======================================================== */

let reportesChartTab = 'tendencia';
let reportesChartInstance = null;
let reportesChartToken = 0;
let reportesRankTipo = 'productos';
let reportesRankLimite = 5;
let reportesRangoActual = null;

function getAuthToken() {
    return localStorage.getItem('jwt_token') || localStorage.getItem('token') || '';
}

/**
 * fetchReportesAPI (url)
 * ----------------------
 * Wrapper de fetch para los endpoints protegidos del mÃ³dulo. Inyecta el
 * Bearer token, trata 401/403 centralizadamente y lanza error si el
 * servidor responde con algo distinto a 2xx. Devuelve el JSON parseado.
 */
async function fetchReportesAPI(url) {
    const token = getAuthToken();
    const response = await fetch(url, {
        headers: { 'Authorization': `Bearer ${token}` }
    });

    if (response.status === 401 || response.status === 403) {
        window.handleUnauthorized();
        throw new Error(`No autorizado (${response.status})`);
    }

    if (!response.ok) {
        throw new Error(`Error en el servidor: ${response.status}`);
    }

    return response.json();
}

/**
 * obtenerRangoReportes()
 * ----------------------
 * Lee las variables de fecha (Desde/Hasta) del formulario, que alimentan el
 * "Motor central de fechas". Valida que ambas existan y que Desde <= Hasta,
 * y devuelve un objeto `{ fecha_inicio, fecha_fin }` con formato YYYY-MM-DD
 * listo para concatenar en la query string de los endpoints.
 */
function obtenerRangoReportes() {
    const elFrom = document.getElementById('filter-reportes-from');
    const elTo = document.getElementById('filter-reportes-to');
    let dateFrom = elFrom ? elFrom.value : '';
    let dateTo = elTo ? elTo.value : '';

    if (!dateFrom || !dateTo) {
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
        dateFrom = toDateString(firstDay);
        dateTo = toDateString(today);
        if (elFrom) elFrom.value = dateFrom;
        if (elTo) elTo.value = dateTo;
        if (typeof window.updateReportesDateLabel === 'function') {
            window.updateReportesDateLabel();
        }
    }

    if (new Date(dateFrom) > new Date(dateTo)) {
        window.showToast("La fecha de inicio no puede ser mayor a la final.", "warning");
        return null;
    }

    return { fecha_inicio: dateFrom, fecha_fin: dateTo };
}

document.addEventListener('DOMContentLoaded', () => {
    // Escuchar cambios de vista
    window.addEventListener('viewChanged', (e) => {
        if (e.detail.view === 'reportes') {
            initReportesView();
        }
    });

    // Configurar fechas por defecto al cargar (inicio de mes y hoy en hora local)
    const today = new Date();
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);

    const dateFrom = document.getElementById('filter-reportes-from');
    const dateTo = document.getElementById('filter-reportes-to');
    if (dateFrom && dateTo) {
        dateFrom.value = toDateString(firstDay);
        dateTo.value = toDateString(today);
    }
    if (typeof window.updateReportesDateLabel === 'function') {
        window.updateReportesDateLabel();
    }

    // Botones consolidado
    document.getElementById('btn-filter-reportes')?.addEventListener('click', loadReportesPreview);
    document.getElementById('btn-export-pdf')?.addEventListener('click', () => exportReporte('pdf'));
    document.getElementById('btn-export-excel')?.addEventListener('click', () => exportReporte('excel'));
    document.getElementById('btn-export-csv')?.addEventListener('click', () => exportReporte('csv'));

    // Botones de filtro rápido de temporada (Hoy / Semana / Mes / Año)
    document.querySelectorAll('[data-quick-filter]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const filterType = btn.getAttribute('data-quick-filter');
            document.querySelectorAll('[data-quick-filter]').forEach(b => b.classList.toggle('active', b === btn));
            
            const today = new Date();
            let fromDate = new Date();
            let toDate = new Date();

            if (filterType === 'hoy') {
                fromDate = today;
                toDate = today;
            } else if (filterType === 'semana') {
                const day = today.getDay() || 7; // Lunes = 1 ... Domingo = 7
                fromDate.setDate(today.getDate() - day + 1);
                toDate = today;
            } else if (filterType === 'mes') {
                fromDate = new Date(today.getFullYear(), today.getMonth(), 1);
                toDate = today;
            } else if (filterType === 'ano') {
                fromDate = new Date(today.getFullYear(), 0, 1);
                toDate = today;
            }

            const elFrom = document.getElementById('filter-reportes-from');
            const elTo = document.getElementById('filter-reportes-to');
            if (elFrom) elFrom.value = toDateString(fromDate);
            if (elTo) elTo.value = toDateString(toDate);

            if (typeof window.updateReportesDateLabel === 'function') {
                window.updateReportesDateLabel();
            }
            loadReportesPreview();
        });
    });

    // Pestañas de la tarjeta derecha de rankings (Más Vendidos / Baja Rotación)
    document.querySelectorAll('.reportes-rank-pill').forEach(pill => {
        pill.addEventListener('click', (e) => {
            e.preventDefault();
            const rankTab = pill.getAttribute('data-rank-tab') || 'productos';
            reportesRankTipo = rankTab;
            document.querySelectorAll('.reportes-rank-pill').forEach(p => p.classList.toggle('active', p === pill));
            const subTitle = document.getElementById('reportes-rank-subtitle');
            if (subTitle) {
                subTitle.textContent = rankTab === 'productos' 
                    ? 'Top 5 más vendidos en el período seleccionado' 
                    : 'Top 5 productos con menor stock o sin rotación';
            }
            cargarRanking();
        });
    });

    // Botones Reporte Usuarios
    document.getElementById('btn-filter-rep-usuarios')?.addEventListener('click', loadReporteUsuarios);
    document.getElementById('btn-export-usuarios-pdf')?.addEventListener('click', () => exportarReporteUsuarios('pdf'));
    document.getElementById('btn-export-usuarios-excel')?.addEventListener('click', () => exportarReporteUsuarios('excel'));
    document.getElementById('btn-export-usuarios-csv')?.addEventListener('click', () => exportarReporteUsuarios('csv'));
    document.getElementById('btn-ficha-usuario-pdf')?.addEventListener('click', exportarFichaUsuarioPDF);

    // Botones Reporte Clientes
    document.getElementById('btn-filter-rep-clientes')?.addEventListener('click', loadReporteClientes);
    document.getElementById('btn-export-clientes-pdf')?.addEventListener('click', () => exportarReporteClientes('pdf'));
    document.getElementById('btn-export-clientes-excel')?.addEventListener('click', () => exportarReporteClientes('excel'));
    document.getElementById('btn-export-clientes-csv')?.addEventListener('click', () => exportarReporteClientes('csv'));
    document.getElementById('btn-ficha-cliente-pdf')?.addEventListener('click', exportarFichaClientePDF);

    // Eventos de tabs para carga automÃ¡tica inicial
    document.getElementById('tab-reporte-usuarios')?.addEventListener('shown.bs.tab', () => {
        loadReporteUsuarios();
    });
    document.getElementById('tab-reporte-clientes')?.addEventListener('shown.bs.tab', () => {
        loadReporteClientes();
    });

    /* ====================================================
       GRÃFICAS: pÃ­ldoras (tabs) para conmutar grÃ¡fica.
       Al hacer clic se actualiza la pestaÃ±a activa y se
       consulta el endpoint correspondiente SIN recargar la
       pÃ¡gina. `renderGrafica` destruye la instancia previa.
       ==================================================== */
    document.querySelectorAll('.reportes-chart-pill').forEach((pill) => {
        pill.addEventListener('click', () => {
            reportesChartTab = pill.getAttribute('data-chart-tab') || pill.getAttribute('data-chart') || 'tendencia';
            document.querySelectorAll('.reportes-chart-pill').forEach((p) => {
                p.classList.toggle('active', p === pill);
                p.setAttribute('aria-selected', p === pill ? 'true' : 'false');
            });
            cargarGraficaActual();
        });
    });

    /* ====================================================
       RANKINGS: cualquier cambio en los selects (tipo_reporte
       o lÃ­mite Top X) dispara una nueva consulta a la base de
       datos y re-renderiza la lista <ul>.
       ==================================================== */
    const rankSelect = document.getElementById('reportes-rank-select');
    const rankLimit = document.getElementById('reportes-rank-limit');
    if (rankSelect) {
        reportesRankTipo = rankSelect.value;
        rankSelect.addEventListener('change', (e) => {
            reportesRankTipo = e.target.value;
            cargarRanking();
        });
    }
    if (rankLimit) {
        reportesRankLimite = Number(rankLimit.value) || 5;
        rankLimit.addEventListener('change', (e) => {
            reportesRankLimite = Number(e.target.value) || 5;
            cargarRanking();
        });
    }
});

/**
 * Inicializa la vista de reportes, valida permisos y carga la vista previa.
 */
function initReportesView() {
    if (!window.isAdmin() && !window.hasPermission('REPORTE_VER')) {
        window.showToast("Acceso denegado. Se requiere permiso REPORTE_VER.", "error");
        window.navigateTo('dashboard');
        return;
    }

    const dateFrom = document.getElementById('filter-reportes-from');
    const dateTo = document.getElementById('filter-reportes-to');
    if (dateFrom && dateTo && (!dateFrom.value || !dateTo.value)) {
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
        dateFrom.value = toDateString(firstDay);
        dateTo.value = toDateString(today);
    }
    if (typeof window.updateReportesDateLabel === 'function') {
        window.updateReportesDateLabel();
    }
    loadReportesPreview();
}

/**
 * Helper para descargar archivos desde endpoints protegidos
 */
async function downloadReporteFile(url, defaultFilename) {
    try {
        const token = getAuthToken();
        window.showToast("Generando reporte...", "info");

        const response = await fetch(url, {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.status === 401 || response.status === 403) {
            window.handleUnauthorized();
            return;
        }

        if (!response.ok) {
            throw new Error(`Error en el servidor: ${response.status}`);
        }

        const blob = await response.blob();
        let filename = defaultFilename;
        const disposition = response.headers.get('Content-Disposition');
        if (disposition && disposition.indexOf('filename=') !== -1) {
            const matches = /filename="?([^"]+)"?/.exec(disposition);
            if (matches != null && matches[1]) {
                filename = matches[1];
            }
        }

        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();

        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);

        window.showToast("Archivo descargado exitosamente", "success");
    } catch (error) {
        console.error("Error al descargar reporte:", error);
        window.showToast("OcurriÃ³ un error al descargar el reporte", "error");
    }
}

/* ========================================================
   1. CONSOLIDADO OPERATIVO (VENTAS / MERMAS / COMPRAS)
   ======================================================== */

async function loadReportesPreview() {
    // Motor central de fechas: se obtiene el rango y se valida.
    const rango = obtenerRangoReportes();
    if (!rango) return;
    reportesRangoActual = rango;

    const btnFilter = document.getElementById('btn-filter-reportes');
    const originalText = btnFilter.innerHTML;
    btnFilter.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    btnFilter.disabled = true;

    // Estado "cargando" en la grÃ¡fica y rankings mientras se espera el fetch.
    graficaPlaceholder('<span class="spinner-border spinner-border-sm me-2"></span>Cargando grÃ¡fica...');
    setRankingLoading();

    try {
                const params = new URLSearchParams({
            fecha_inicio: rango.fecha_inicio,
            fecha_fin: rango.fecha_fin
        });
        const dateParams = params.toString();

        const [kpi, consolidado, grafica, ranking] = await Promise.all([
            fetchReportesAPI(`${REPORTES_API_URL}/kpi?${dateParams}`),
            fetchReportesAPI(`${REPORTES_API_URL}/?${dateParams}`),
            fetchReportesAPI(`${REPORTES_API_URL}/grafica?tipo=${encodeURIComponent(reportesChartTab)}&${dateParams}`),
            fetchReportesAPI(`${REPORTES_API_URL}/ranking?tipo_reporte=${encodeURIComponent(reportesRankTipo)}&limite=${encodeURIComponent(reportesRankLimite)}&${dateParams}`),
        ]);

        renderReportesKPIs(kpi);
        renderReportesPreview(consolidado);
        renderGrafica(grafica);
        renderRanking(ranking);

    } catch (error) {
        console.error("Error al cargar reportes:", error);
        // Al fallar se resetean todos los componentes (estado vacÃ­o limpio).
        renderReportesKPIs(null);
        renderReportesPreview(null);
        graficaPlaceholder('<i class="bi bi-exclamation-triangle"></i><span>Error al cargar la grÃ¡fica</span>');
        renderRanking(null);
        window.showToast("Error al cargar las estadÃ­sticas de reportes.", "error");
    } finally {
        btnFilter.innerHTML = originalText;
        btnFilter.disabled = false;
    }
}

/**
 * renderReportesKPIs(kpi)
 * ---------------
 * Inyecta los totales agregados (SUM) en las tarjetas superiores, formateados
 * como moneda local (Q) con el helper global `formatoQuetzal` (Intl es-GT).
 * Si `kpi` es null se restablece el estado vacÃ­o (Q 0.00 / 0 registros).
 */
function renderReportesKPIs(kpi) {
    const datos = kpi || {
        ventas: 0, count_ventas: 0,
        ganancia_estimada: 0, costo_vendido: 0, margen_ganancia: 0,
        mermas: 0, count_mermas: 0,
        compras: 0, count_compras: 0,
    };

    const elTotalVentas = document.getElementById('reportes-total-ventas');
    const elCountVentas = document.getElementById('reportes-count-ventas');
    const elTotalGanancia = document.getElementById('reportes-total-ganancia');
    const elMargenGanancia = document.getElementById('reportes-margen-ganancia');
    const elTotalMermas = document.getElementById('reportes-total-mermas');
    const elCountMermas = document.getElementById('reportes-count-mermas');
    const elTotalCompras = document.getElementById('reportes-total-compras');
    const elCountCompras = document.getElementById('reportes-count-compras');

    if (elTotalVentas) elTotalVentas.textContent = formatoQuetzal(datos.ventas);
    if (elCountVentas) elCountVentas.textContent = `${Number(datos.count_ventas) || 0} ventas cobradas`;

    if (elTotalGanancia) elTotalGanancia.textContent = formatoQuetzal(datos.ganancia_estimada);
    if (elMargenGanancia) {
        const margen = Number(datos.margen_ganancia || 0).toFixed(1);
        elMargenGanancia.textContent = `Margen: ${margen}% · Costo: ${formatoQuetzal(datos.costo_vendido)}`;
    }

    if (elTotalMermas) elTotalMermas.textContent = formatoQuetzal(datos.mermas);
    if (elCountMermas) elCountMermas.textContent = `${Number(datos.count_mermas) || 0} registros`;

    if (elTotalCompras) elTotalCompras.textContent = formatoQuetzal(datos.compras);
    if (elCountCompras) elCountCompras.textContent = `${Number(datos.count_compras) || 0} registros`;
}

function renderReportesPreview(data) {
    const tbody = document.getElementById('reportes-table-body');
    if (!tbody) return;

    if (!data || typeof data !== 'object') {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">No se pudo cargar la vista previa para el período seleccionado.</td></tr>';
        return;
    }

    const ventas = Array.isArray(data.ventas) ? data.ventas : [];
    tbody.innerHTML = '';

    if (ventas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">No se registraron ventas en el período seleccionado</td></tr>';
        return;
    }

    const recientes = ventas.slice(0, 10);
    recientes.forEach(v => {
        const tr = document.createElement('tr');
        const fechaRaw = v.fecha_venta || v.fecha;
        const fechaStr = fechaRaw 
            ? new Date(fechaRaw).toLocaleString('es-GT', { dateStyle: 'short', timeStyle: 'short' })
            : 'N/A';
        const articulosStr = v.articulos || 'Venta de mostrador';
        const vendedor = v.vendedor || 'Mostrador';
        const metodo = v.metodo_pago || 'Efectivo';
        const metodoBadge = metodo.toLowerCase().includes('transf')
            ? '<span class="badge bg-info-subtle text-info border border-info-subtle"><i class="bi bi-arrow-left-right me-1"></i>Transferencia</span>'
            : '<span class="badge bg-success-subtle text-success border border-success-subtle"><i class="bi bi-cash me-1"></i>Efectivo</span>';

        const descuento = Number(v.descuento || 0);
        const total = Number(v.total_venta ?? (v.total ?? 0)) || 0;
        const anuladaTag = (v.estado && v.estado.toLowerCase() === 'anulada')
            ? ' <span class="badge bg-danger-subtle text-danger ms-1">Anulada</span>'
            : '';

        tr.innerHTML = `
            <td class="text-nowrap small text-muted">${fechaStr}</td>
            <td>
                <div class="fw-semibold text-dark small" style="max-width: 320px; white-space: normal; line-height: 1.3;">
                    ${esc(articulosStr)}
                </div>
                ${anuladaTag}
            </td>
            <td class="small text-muted">${esc(vendedor)}</td>
            <td class="text-center">${metodoBadge}</td>
            <td class="text-end small text-muted">Q ${descuento.toFixed(2)}</td>
            <td class="text-end fw-bold text-teal">Q ${total.toFixed(2)}</td>
        `;
        tbody.appendChild(tr);
    });

    if (ventas.length > 10) {
        const extraRow = document.createElement('tr');
        extraRow.innerHTML = `<td colspan="6" class="text-center text-muted small bg-light">Mostrando 10 de ${ventas.length} ventas. Descargue el reporte completo en PDF o Excel.</td>`;
        tbody.appendChild(extraRow);
    }
}

async function exportReporte(formato) {
    const rango = obtenerRangoReportes();
    if (!rango) return;

    const url = `${REPORTES_API_URL}/exportar?fecha_inicio=${rango.fecha_inicio}&fecha_fin=${rango.fecha_fin}&formato=${formato}`;
    const ext = formato === 'excel' ? 'xlsx' : (formato === 'pdf' ? 'pdf' : 'csv');
    const defaultFilename = `Reporte_${rango.fecha_inicio}_al_${rango.fecha_fin}.${ext}`;
    await downloadReporteFile(url, defaultFilename);
}

/* ========================================================
   2. REPORTE DE USUARIOS (LISTADO, FICHA, EXPORTACIÃ“N)
   ======================================================== */

function getUsuariosFilterParams() {
    const estado = document.getElementById('filter-rep-usuarios-estado')?.value || '';
    const fechaDesde = document.getElementById('filter-rep-usuarios-desde')?.value || '';
    const fechaHasta = document.getElementById('filter-rep-usuarios-hasta')?.value || '';

    const params = new URLSearchParams();
    if (estado) params.append('estado', estado);
    if (fechaDesde) params.append('fecha_desde', fechaDesde);
    if (fechaHasta) params.append('fecha_hasta', fechaHasta);
    return params.toString();
}

async function loadReporteUsuarios() {
    const btn = document.getElementById('btn-filter-rep-usuarios');
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        btn.disabled = true;
    }

    const tbody = document.getElementById('reportes-usuarios-tbody');
    tbody.innerHTML = typeof window.renderSkeletonTable === 'function' ? window.renderSkeletonTable(7, 5) : '<tr><td colspan="7" class="text-center text-muted py-4">Cargando usuarios...</td></tr>';

    try {
        const token = getAuthToken();
        const qs = getUsuariosFilterParams();
        const url = `${REPORTES_API_URL}/usuarios${qs ? '?' + qs : ''}`;

        const res = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.status === 401 || res.status === 403) {
            window.handleUnauthorized();
            return;
        }

        if (!res.ok) {
            throw new Error(`Error en servidor: ${res.status}`);
        }

        const data = await res.json();
        const badge = document.getElementById('badge-total-usuarios');
        if (badge) badge.textContent = `${data.length} usuarios`;

        tbody.innerHTML = '';
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">No se encontraron usuarios con los filtros indicados</td></tr>';
            return;
        }

        data.forEach((u) => {
            const tr = document.createElement('tr');
            const estadoBadge = u.estado === 'Activo'
                ? '<span class="badge bg-success-subtle text-success border border-success-subtle">Activo</span>'
                : '<span class="badge bg-secondary-subtle text-secondary border">Inactivo</span>';

            const cuadreClass = Number(u.diferencia_caja) !== 0 ? 'text-danger fw-bold' : 'text-muted';
            const difStr = Number(u.diferencia_caja) > 0 ? `+${formatoQuetzal(u.diferencia_caja)}` : formatoQuetzal(u.diferencia_caja || 0);

            tr.innerHTML = `
                <td>
                    <div class="fw-bold text-dark">${esc(u.nombre_completo || u.username)}</div>
                    <small class="text-muted">@${esc(u.username)}</small>
                </td>
                <td><span class="badge bg-light text-dark border">${esc(u.rol_nombre || '-')}</span></td>
                <td class="text-center">
                    <span class="badge bg-teal-subtle text-teal fw-semibold">${u.ventas_count || 0} ventas</span>
                </td>
                <td class="text-end fw-bold text-success">${formatoQuetzal(u.total_vendido || 0)}</td>
                <td class="text-center">
                    <div class="fw-medium">${u.turnos_cerrados || 0} turnos</div>
                    <small class="${cuadreClass}">${difStr} dif.</small>
                </td>
                <td class="text-center">
                    <span class="badge bg-light text-dark border">${u.ingresos_bodega || 0} ingresos</span>
                </td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-teal btn-ver-usuario" data-id="${u.id_usuario}">
                        <i class="bi bi-eye me-1"></i>Ver Detalle
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        tbody.querySelectorAll('.btn-ver-usuario').forEach(btnEl => {
            btnEl.addEventListener('click', () => {
                const id = btnEl.getAttribute('data-id');
                window.verFichaUsuario(id);
            });
        });

    } catch (err) {
        console.error("Error al cargar reporte de usuarios:", err);
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger py-4">Error al cargar usuarios</td></tr>';
        window.showToast("No se pudo cargar el reporte de usuarios", "error");
    } finally {
        if (btn) {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }
}

window.verFichaUsuario = async function(id_usuario) {
    try {
        const token = getAuthToken();
        const res = await fetch(`${REPORTES_API_URL}/usuarios/${id_usuario}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.status === 401 || res.status === 403) {
            window.handleUnauthorized();
            return;
        }

        if (!res.ok) {
            throw new Error(`Error al obtener ficha: ${res.status}`);
        }

        const data = await res.json();

        document.getElementById('ficha-usuario-id').value = data.id_usuario;
        document.getElementById('ficha-usuario-username').textContent = `@${data.username}`;
        document.getElementById('ficha-usuario-nombre').textContent = data.nombre_completo || '-';
        document.getElementById('ficha-usuario-rol').textContent = data.rol_nombre || '-';
        
        const estadoEl = document.getElementById('ficha-usuario-estado');
        if (estadoEl) {
            estadoEl.textContent = data.estado;
            estadoEl.className = data.estado === 'Activo' ? 'badge bg-success' : 'badge bg-secondary';
        }

        const fechaStr = data.fecha_creacion ? new Date(data.fecha_creacion).toLocaleString() : '-';
        const fechaEl = document.getElementById('ficha-usuario-fecha');
        if (fechaEl) fechaEl.textContent = fechaStr;

        // Métricas operativas en la ficha
        const ventasEl = document.getElementById('ficha-usuario-ventas');
        if (ventasEl) ventasEl.textContent = `${data.ventas_count || 0} ventas registradas`;

        const totalVendidoEl = document.getElementById('ficha-usuario-total-vendido');
        if (totalVendidoEl) totalVendidoEl.textContent = formatoQuetzal(data.total_vendido || 0);

        const turnosEl = document.getElementById('ficha-usuario-turnos');
        if (turnosEl) turnosEl.textContent = `${data.turnos_cerrados || 0} turnos finalizados`;

        const difEl = document.getElementById('ficha-usuario-diferencia');
        if (difEl) {
            const difVal = Number(data.diferencia_caja || 0);
            difEl.textContent = formatoQuetzal(difVal);
            difEl.className = difVal !== 0 ? 'fw-bold text-danger' : 'fw-bold text-dark';
        }

        const comprasEl = document.getElementById('ficha-usuario-compras');
        if (comprasEl) comprasEl.textContent = `${data.ingresos_bodega || 0} compras/ingresos procesados`;

        const modalEl = document.getElementById('modal-reporte-ficha-usuario');
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();

    } catch (err) {
        console.error("Error al abrir ficha de usuario:", err);
        window.showToast("No se pudo cargar la ficha del usuario", "error");
    }
};

async function exportarReporteUsuarios(formato) {
    const qs = getUsuariosFilterParams();
    let url;
    let defFilename;

    if (formato === 'pdf') {
        url = `${REPORTES_API_URL}/usuarios/pdf${qs ? '?' + qs : ''}`;
        defFilename = `reporte_usuarios_${new Date().toISOString().slice(0,10)}.pdf`;
    } else {
        const sep = qs ? '&' : '';
        url = `${REPORTES_API_URL}/usuarios/exportar?${qs}${sep}formato=${formato}`;
        defFilename = `reporte_usuarios_${new Date().toISOString().slice(0,10)}.${formato === 'excel' ? 'xlsx' : 'csv'}`;
    }

    await downloadReporteFile(url, defFilename);
}

async function exportarFichaUsuarioPDF() {
    const id = document.getElementById('ficha-usuario-id')?.value;
    if (!id) return;
    const url = `${REPORTES_API_URL}/usuarios/${id}/pdf`;
    const defFilename = `ficha_usuario_${id}.pdf`;
    await downloadReporteFile(url, defFilename);
}

/* ========================================================
   3. REPORTE DE CLIENTES (LISTADO, FICHA, EXPORTACIÃ“N)
   ======================================================== */

function getClientesFilterParams() {
    const estado = document.getElementById('filter-rep-clientes-estado')?.value || '';
    const fechaDesde = document.getElementById('filter-rep-clientes-desde')?.value || '';
    const fechaHasta = document.getElementById('filter-rep-clientes-hasta')?.value || '';

    const params = new URLSearchParams();
    if (estado) params.append('estado', estado);
    if (fechaDesde) params.append('fecha_desde', fechaDesde);
    if (fechaHasta) params.append('fecha_hasta', fechaHasta);
    return params.toString();
}

async function loadReporteClientes() {
    const btn = document.getElementById('btn-filter-rep-clientes');
    const originalText = btn ? btn.innerHTML : '';
    if (btn) {
        btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
        btn.disabled = true;
    }

    const tbody = document.getElementById('reportes-clientes-tbody');
    tbody.innerHTML = typeof window.renderSkeletonTable === 'function' ? window.renderSkeletonTable(7, 5) : '<tr><td colspan="7" class="text-center text-muted py-4">Cargando clientes...</td></tr>';

    try {
        const token = getAuthToken();
        const qs = getClientesFilterParams();
        const url = `${REPORTES_API_URL}/clientes${qs ? '?' + qs : ''}`;

        const res = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.status === 401 || res.status === 403) {
            window.handleUnauthorized();
            return;
        }

        if (!res.ok) {
            throw new Error(`Error en servidor: ${res.status}`);
        }

        const data = await res.json();
        const badge = document.getElementById('badge-total-clientes');
        if (badge) badge.textContent = `${data.length} clientes`;

        tbody.innerHTML = '';
        if (data.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4">No se encontraron clientes con los filtros indicados</td></tr>';
            return;
        }

        data.forEach((c, index) => {
            const tr = document.createElement('tr');
            const estadoBadge = c.estado === 'Activo'
                ? '<span class="badge bg-success">Activo</span>'
                : '<span class="badge bg-secondary">Inactivo</span>';

            const fechaStr = c.fecha_creacion ? new Date(c.fecha_creacion).toLocaleDateString() : '-';

            tr.innerHTML = `
                <td>${index + 1}</td>
                <td class="fw-bold text-dark">${c.nit}</td>
                <td>${c.nombre_comercial || '-'}</td>
                <td><span class="badge bg-info text-dark">${c.tipo_cliente_nombre || '-'}</span></td>
                <td>${estadoBadge}</td>
                <td>${fechaStr}</td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-primary btn-ver-cliente" data-id="${c.id_cliente}">
                        <i class="bi bi-eye me-1"></i>Ver
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });

        tbody.querySelectorAll('.btn-ver-cliente').forEach(btnEl => {
            btnEl.addEventListener('click', () => {
                const id = btnEl.getAttribute('data-id');
                window.verFichaCliente(id);
            });
        });

    } catch (err) {
        console.error("Error al cargar reporte de clientes:", err);
        tbody.innerHTML = '<tr><td colspan="7" class="text-center text-danger py-4">Error al cargar clientes</td></tr>';
        window.showToast("No se pudo cargar el reporte de clientes", "error");
    } finally {
        if (btn) {
            btn.innerHTML = originalText;
            btn.disabled = false;
        }
    }
}

window.verFichaCliente = async function(id_cliente) {
    try {
        const token = getAuthToken();
        const res = await fetch(`${REPORTES_API_URL}/clientes/${id_cliente}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });

        if (res.status === 401 || res.status === 403) {
            window.handleUnauthorized();
            return;
        }

        if (!res.ok) {
            throw new Error(`Error al obtener ficha: ${res.status}`);
        }

        const data = await res.json();

        document.getElementById('ficha-cliente-id').value = data.id_cliente;
        document.getElementById('ficha-cliente-nit').textContent = data.nit;
        document.getElementById('ficha-cliente-nombre').textContent = data.nombre_comercial;
        document.getElementById('ficha-cliente-tipo').textContent = data.tipo_cliente_nombre || 'General';

        // Ubicacion
        const ubicacionParts = [];
        if (data.departamento_nombre) ubicacionParts.push(`Departamento: ${data.departamento_nombre}`);
        if (data.municipio_nombre) ubicacionParts.push(`Municipio: ${data.municipio_nombre}`);
        if (data.direccion) ubicacionParts.push(`DirecciÃ³n: ${data.direccion}`);
        document.getElementById('ficha-cliente-ubicacion').textContent = ubicacionParts.join(' | ') || 'Sin ubicaciÃ³n registrada';

        // Contactos
        const telList = (data.telefonos || []).map(t => `<div><i class="bi bi-telephone me-1"></i><strong>TelÃ©fono:</strong> ${t}</div>`);
        const emailList = (data.correos || []).map(e => `<div><i class="bi bi-envelope me-1"></i><strong>Correo:</strong> ${e}</div>`);
        const allContacts = [...telList, ...emailList];
        const contactosEl = document.getElementById('ficha-cliente-contactos');
        if (allContacts.length === 0) {
            contactosEl.textContent = 'Sin telÃ©fonos ni correos registrados';
        } else {
            contactosEl.innerHTML = allContacts.join('');
        }

        const estadoEl = document.getElementById('ficha-cliente-estado');
        estadoEl.textContent = data.estado;
        estadoEl.className = data.estado === 'Activo' ? 'badge bg-success' : 'badge bg-secondary';

        const fechaStr = data.fecha_creacion ? new Date(data.fecha_creacion).toLocaleString() : '-';
        document.getElementById('ficha-cliente-fecha').textContent = fechaStr;

        const modalEl = document.getElementById('modal-reporte-ficha-cliente');
        const modal = bootstrap.Modal.getOrCreateInstance(modalEl);
        modal.show();

    } catch (err) {
        console.error("Error al abrir ficha de cliente:", err);
        window.showToast("No se pudo cargar la ficha del cliente", "error");
    }
};

async function exportarReporteClientes(formato) {
    const qs = getClientesFilterParams();
    let url;
    let defFilename;

    if (formato === 'pdf') {
        url = `${REPORTES_API_URL}/clientes/pdf${qs ? '?' + qs : ''}`;
        defFilename = `reporte_clientes_${new Date().toISOString().slice(0,10)}.pdf`;
    } else {
        const sep = qs ? '&' : '';
        url = `${REPORTES_API_URL}/clientes/exportar?${qs}${sep}formato=${formato}`;
        defFilename = `reporte_clientes_${new Date().toISOString().slice(0,10)}.${formato === 'excel' ? 'xlsx' : 'csv'}`;
    }

    await downloadReporteFile(url, defFilename);
}

async function exportarFichaClientePDF() {
    const id = document.getElementById('ficha-cliente-id')?.value;
    if (!id) return;
    const url = `${REPORTES_API_URL}/clientes/${id}/pdf`;
    const defFilename = `ficha_cliente_${id}.pdf`;
    await downloadReporteFile(url, defFilename);
}

/* ========================================================
   4. GRÃFICAS INTEGRADAS (Chart.js)
   ========================================================
   El Ã¡rea de grÃ¡ficas reemplaza al placeholder gris: se crea un <canvas>
   dinÃ¡mico dentro de `.reportes-chart-card .card-body` y se instancia
   Chart.js (cargado vÃ­a CDN al final del <head> de index.html).

   CICLO DE VIDA DE LA GRÃFICA (importante):
   1. Antes de pintar una grÃ¡fica NUEVA se llama a `.destroy()` sobre la
      instancia anterior. Chart.js NO permite reutilizar un <canvas>;
      sin el destroy los eventos, animaciones y listeners se acumulan y
      la memoria crece en cada cambio de pestaÃ±a.
   2. El canvas se reemplaza por uno nuevo (un canvas destruido no se puede
      volver a inicializar).
   3. Se usa un "token" numÃ©rico: si el usuario cambia de pestaÃ±a mientras
      una peticiÃ³n estÃ¡ en vuelo, la respuesta obsoleta (con token antiguo)
      se descarta.
   ======================================================== */

/**
 * graficaPlaceholder(innerHTML)
 * ---------------------------
 * Muestra el estado "placeholder" del Ã¡rea de grÃ¡ficas (spinner de carga o
 * mensaje de vacÃ­o/error), DESTRUYENDO la instancia previa de Chart.js y
 * eliminando el canvas dinÃ¡mico que pudiera quedar huÃ©rfano.
 */
function graficaPlaceholder(innerHTML) {
    reportesChartToken += 1;
    if (reportesChartInstance) {
        reportesChartInstance.destroy();
        reportesChartInstance = null;
    }

    const cardBody = document.querySelector('.reportes-chart-card .card-body');
    if (!cardBody) return;
    cardBody.querySelectorAll('.reportes-chart-wrap').forEach((n) => n.remove());

    const placeholder = cardBody.querySelector('.reportes-chart-placeholder');
    if (placeholder) {
        placeholder.classList.remove('d-none');
        const cta = placeholder.querySelector('.reportes-chart-cta');
        if (cta) cta.innerHTML = innerHTML;
    }
}

/**
 * renderGrafica(data)
 * ------------------
 * Recibe la respuesta del endpoint /grafica `{ tipo, etiquetas, valores }`
 * y dibuja la grÃ¡fica correspondiente a `reportesChartTab`.
 *
 * - Si no hay series (rango sin datos) muestra el placeholder "Sin datos".
 * - Si no existe Chart.js (CDN caÃ­do) muestra un mensaje de error.
 * - Antes de instanciar la nueva grÃ¡fica destruye la anterior (ver arriba).
 * - Espera a que el contenedor tenga tamaÃ±o real antes de dibujar (Chart.js
 *   no se recupera si se instancia oculto o con 0x0).
 */
function renderGrafica(data) {
    const cardBody = document.querySelector('.reportes-chart-card .card-body');
    if (!cardBody) return;

    const etiquetas = Array.isArray(data && data.etiquetas) ? data.etiquetas : [];
    const valores = Array.isArray(data && data.valores) ? data.valores : [];
    const hayDatos = etiquetas.length > 0 && valores.some((v) => (Number(v) || 0) > 0);

    if (!hayDatos) {
        graficaPlaceholder('<i class="bi bi-bar-chart-fill"></i><span>Sin datos para el rango seleccionado</span>');
        return;
    }

    // Token anti-carrera: nueva operaciÃ³n de pintado.
    reportesChartToken += 1;
    const token = reportesChartToken;

    // DESTRUYE la instancia anterior antes de crear la nueva (requisito clave).
    if (reportesChartInstance) {
        reportesChartInstance.destroy();
        reportesChartInstance = null;
    }

    // Oculta el placeholder gris y crea el contenedor/canvas dinÃ¡micos.
    const placeholder = cardBody.querySelector('.reportes-chart-placeholder');
    if (placeholder) placeholder.classList.add('d-none');

    cardBody.querySelectorAll('.reportes-chart-wrap').forEach((n) => n.remove());
    const wrap = document.createElement('div');
    wrap.className = 'reportes-chart-wrap';
    wrap.style.position = 'relative';
    wrap.style.height = '300px';
    const canvas = document.createElement('canvas');
    wrap.appendChild(canvas);
    cardBody.appendChild(wrap);

    if (typeof window.Chart === 'undefined') {
        graficaPlaceholder('<i class="bi bi-exclamation-triangle"></i><span>No se pudo cargar Chart.js (CDN)</span>');
        return;
    }

        let intentos = 0;
    const dibujar = () => {
        if (token !== reportesChartToken) return;
        if (!wrap.offsetParent || wrap.clientWidth < 40 || wrap.clientHeight < 40) {
            if (intentos++ < 25) {
                setTimeout(dibujar, 100);
            }
            return;
        }
        reportesChartInstance = new Chart(canvas, construirConfiguracionGrafica(reportesChartTab, { etiquetas, valores }));
    };
    dibujar();
}

/**
 * construirConfiguracionGrafica(tipo, data)
 * ----------------------------------------
 * Devuelve la configuraciÃ³n que consume `new Chart(canvas, config)` segÃºn la
 * pestaÃ±a activa:
 *   - 'tendencia' -> GrÃ¡fica de LÃNEAS con los totales por dÃ­a (o mes).
 *   - 'categoria' -> GrÃ¡fica de DONA con los ingresos por categorÃ­a.
 *   - 'hora'      -> GrÃ¡fica de BARRAS con el conteo por hora pico.
 */
// Plugin de etiquetas numéricas directas sobre las barras (accesibilidad senior)
const barValueLabelsPlugin = {
    id: 'barValueLabels',
    afterDatasetsDraw(chart) {
        const { ctx, data } = chart;
        const isHorizontal = chart.config.options.indexAxis === 'y';
        if (!data.datasets || !data.datasets[0] || !data.datasets[0].data) return;
        
        const totalSum = data.datasets[0].data.reduce((a, b) => a + (Number(b) || 0), 0);
        
        chart.data.datasets.forEach((dataset, i) => {
            const meta = chart.getDatasetMeta(i);
            if (!meta || !meta.data) return;
            meta.data.forEach((bar, index) => {
                const val = Number(dataset.data[index]) || 0;
                if (val <= 0) return;
                ctx.save();
                ctx.font = 'bold 11px system-ui, -apple-system, sans-serif';
                ctx.fillStyle = '#0f172a';
                
                if (isHorizontal) {
                    const pct = totalSum > 0 ? ((val / totalSum) * 100).toFixed(1) : '0';
                    const text = `${formatoQuetzal(val)} (${pct}%)`;
                    ctx.textAlign = 'left';
                    ctx.textBaseline = 'middle';
                    ctx.fillText(text, bar.x + 8, bar.y);
                } else {
                    const text = formatoQuetzal(val);
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'bottom';
                    ctx.fillText(text, bar.x, bar.y - 4);
                }
                ctx.restore();
            });
        });
    }
};

/**
 * construirConfiguracionGrafica(tipo, data)
 * ----------------------------------------
 * Simplificada para adultos mayores (cero emojis, barras claras con números visibles):
 *   - 'tendencia' (Ventas por Día): Barras verticales en teal institucional (#0d7377) con montos Q arriba.
 *   - 'categoria' (Ventas por Categoría): Barras horizontales por categoría con monto Q y porcentaje visible.
 */
function construirConfiguracionGrafica(tipo, data) {
    const etiquetas = data.etiquetas || [];
    const valores = (data.valores || []).map((v) => Number(v) || 0);
    const paleta = ['#0A5C5E', '#0d7377', '#14b8a6', '#059669', '#10b981', '#f59e0b', '#2563eb', '#7c3aed', '#dc2626', '#64748b'];

    if (tipo === 'categoria') {
        return {
            type: 'bar',
            plugins: [barValueLabelsPlugin],
            data: {
                labels: etiquetas,
                datasets: [{
                    label: 'Ventas por Categoría (Q)',
                    data: valores,
                    backgroundColor: paleta.slice(0, etiquetas.length),
                    borderRadius: 6,
                    maxBarThickness: 28,
                }],
            },
            options: {
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: { top: 10, right: 110, left: 10, bottom: 5 }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: (ctx) => ` Total: ${formatoQuetzal(ctx.parsed.x)}`
                        }
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        grace: '20%',
                        ticks: { callback: (v) => `Q${Number(v).toLocaleString('es-GT')}` },
                        grid: { color: '#f1f5f9' }
                    },
                    y: {
                        grid: { display: false },
                        ticks: {
                            font: { weight: '600', size: 12 },
                            color: '#1e293b'
                        }
                    }
                }
            }
        };
    }

    // Default 'tendencia' -> Barras verticales en teal institucional (#0d7377) con valor visible en la parte superior
    return {
        type: 'bar',
        plugins: [barValueLabelsPlugin],
        data: {
            labels: etiquetas,
            datasets: [{
                label: 'Ventas por Día (Q)',
                data: valores,
                backgroundColor: '#0d7377',
                hoverBackgroundColor: '#0A5C5E',
                borderRadius: 6,
                maxBarThickness: 45,
            }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            layout: {
                padding: { top: 25, right: 15, left: 10, bottom: 5 }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: (ctx) => ` Ventas: ${formatoQuetzal(ctx.parsed.y)}`
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    grace: '15%',
                    ticks: { callback: (v) => `Q${Number(v).toLocaleString('es-GT')}` },
                    grid: { color: '#f1f5f9' }
                },
                x: {
                    grid: { display: false },
                    ticks: {
                        font: { weight: '600', size: 11 },
                        color: '#334155'
                    }
                }
            }
        }
    };
}

function baseOptionsGrafica(esDinero) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                callbacks: {
                    label: (ctx) => {
                        const raw = ctx.parsed && ctx.parsed.y !== undefined ? ctx.parsed.y : ctx.parsed;
                        return esDinero ? ` Ventas: ${formatoQuetzal(raw)}` : ` ${raw} transacciones`;
                    },
                },
            },
        },
        scales: esDinero
            ? { y: { beginAtZero: true, ticks: { callback: (v) => `Q${Number(v).toLocaleString('es-GT')}` } } }
            : { y: { beginAtZero: true, ticks: { precision: 0, stepSize: 1 } } },
    };
}

/**
 * cargarGraficaActual()
 * ---------------------
 * Dispara la peticiÃ³n de la grÃ¡fica de la pestaÃ±a activa usando el ÃšLTIMO
 * rango consultado (no obliga a volver a presionar "Consultar"). Muestra un
 * spinner mientras llega la respuesta.
 */
function cargarGraficaActual() {
    if (!reportesRangoActual) {
        reportesRangoActual = obtenerRangoReportes();
    }
    if (!reportesRangoActual) {
        graficaPlaceholder('<i class="bi bi-bar-chart-fill"></i><span>Presione "Consultar" para cargar la gráfica seleccionada</span>');
        return;
    }

    graficaPlaceholder('<span class="spinner-border spinner-border-sm me-2"></span>Cargando gráfica...');

    const { fecha_inicio, fecha_fin } = reportesRangoActual;
    const params = new URLSearchParams({
        tipo: reportesChartTab,
        fecha_inicio: fecha_inicio,
        fecha_fin: fecha_fin
    });
    fetchReportesAPI(`${REPORTES_API_URL}/grafica?${params.toString()}`)
        .then(renderGrafica)
        .catch((err) => {
            console.error("Error al cargar la gráfica:", err);
            graficaPlaceholder('<i class="bi bi-exclamation-triangle"></i><span>Error al cargar la gráfica</span>');
        });
}

/* ========================================================
   5. WIDGET DE RANKINGS (Top Productos / Clientes / Estancados)
   ======================================================== */

/**
 * setRankingLoading()
 * -------------------
 * Marca el estado "cargando" de la lista de rankings mientras se espera la
 * respuesta del servidor.
 */
function setRankingLoading() {
    const ul = document.querySelector('.reportes-rank-list');
    if (ul) {
        ul.innerHTML = typeof window.renderSkeletonCard === 'function' ? window.renderSkeletonCard(3) : '<li class="reportes-rank-item text-muted">Cargando...</li>';
    }
}

/**
 * renderRanking(data)
 * -------------------
 * Inyecta en el <ul> los elementos <li> con el ranking consultado.
 * Cada fila muestra posiciÃ³n, nombre (escapado para evitar XSS) y el monto
 * en moneda local (Q). Con `data` null/[] se muestra un estado vacÃ­o.
 */
function renderRanking(data) {
    const ul = document.querySelector('.reportes-rank-list');
    if (!ul) return;

    const items = (data && Array.isArray(data.items)) ? data.items : [];

    if (items.length === 0) {
        ul.innerHTML = '<li class="reportes-rank-item py-3 text-center"><span class="reportes-rank-name text-muted"><i class="bi bi-inbox me-1"></i>Sin datos para el período seleccionado</span></li>';
        return;
    }

    ul.innerHTML = items.map((item, i) => {
        let detalleBadge = '';
        if (reportesRankTipo === 'productos') {
            const uds = item.cantidad || 0;
            detalleBadge = `<span class="badge bg-teal-subtle text-teal fw-semibold">${uds} ${uds === 1 ? 'ud vendida' : 'uds vendidas'}</span>`;
        } else if (reportesRankTipo === 'estancados') {
            const stock = item.cantidad || 0;
            const badgeClass = stock <= 8 ? 'bg-danger-subtle text-danger border border-danger-subtle' : 'bg-warning-subtle text-warning-emphasis border border-warning-subtle';
            detalleBadge = `<span class="badge ${badgeClass} fw-semibold">Stock actual: ${stock} uds</span>`;
        }

        return `
            <li class="reportes-rank-item py-2 border-bottom d-flex align-items-center justify-content-between">
                <div class="d-flex align-items-center me-2 text-truncate" style="min-width: 0;">
                    <span class="reportes-rank-num me-2 flex-shrink-0">${i + 1}</span>
                    <div class="text-truncate">
                        <div class="reportes-rank-name fw-semibold text-dark text-truncate" title="${esc(item.nombre)}">${esc(item.nombre)}</div>
                        <div class="mt-1">${detalleBadge}</div>
                    </div>
                </div>
                <div class="text-end flex-shrink-0 ms-2">
                    <span class="reportes-rank-amount fw-bold text-dark">${formatoQuetzal(item.valor)}</span>
                </div>
            </li>
        `;
    }).join('');
}

function cargarRanking() {
    if (!reportesRangoActual) {
        reportesRangoActual = obtenerRangoReportes();
    }
    if (!reportesRangoActual) {
        renderRanking(null);
        return;
    }

    setRankingLoading();

    const { fecha_inicio, fecha_fin } = reportesRangoActual;
    const params = new URLSearchParams({
        tipo_reporte: reportesRankTipo,
        limite: reportesRankLimite,
        fecha_inicio: fecha_inicio,
        fecha_fin: fecha_fin
    });
    fetchReportesAPI(`${REPORTES_API_URL}/ranking?${params.toString()}`)
        .then(renderRanking)
        .catch((err) => {
            console.error("Error al cargar el ranking:", err);
            renderRanking(null);
        });
}


// Exportaciones globales para integración con app.js y atajos del DOM
window.initReportesView = initReportesView;
window.showReportesModule = initReportesView;
window.loadReportesPreview = loadReportesPreview;
window.cargarGraficaActual = cargarGraficaActual;
window.cargarRanking = cargarRanking;
