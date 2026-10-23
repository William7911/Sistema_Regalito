const REPORTES_API_URL = '/api/reportes';

function getAuthToken() {
    return localStorage.getItem('jwt_token') || localStorage.getItem('token') || '';
}

document.addEventListener('DOMContentLoaded', () => {
    // Escuchar cambios de vista
    window.addEventListener('viewChanged', (e) => {
        if (e.detail.view === 'reportes') {
            initReportesView();
        }
    });

    // Configurar fechas por defecto al cargar (inicio de mes y hoy)
    const today = new Date();
    const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);

    const dateFrom = document.getElementById('filter-reportes-from');
    const dateTo = document.getElementById('filter-reportes-to');
    if (dateFrom && dateTo) {
        dateTo.valueAsDate = today;
        dateFrom.valueAsDate = firstDay;
    }

    // Botones consolidado
    document.getElementById('btn-filter-reportes')?.addEventListener('click', loadReportesPreview);
    document.getElementById('btn-export-excel')?.addEventListener('click', () => exportReporte('excel'));
    document.getElementById('btn-export-csv')?.addEventListener('click', () => exportReporte('csv'));

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

    // Eventos de tabs para carga automática inicial
    document.getElementById('tab-reporte-usuarios')?.addEventListener('shown.bs.tab', () => {
        loadReporteUsuarios();
    });
    document.getElementById('tab-reporte-clientes')?.addEventListener('shown.bs.tab', () => {
        loadReporteClientes();
    });
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
        window.showToast("Ocurrió un error al descargar el reporte", "error");
    }
}

/* ========================================================
   1. CONSOLIDADO OPERATIVO (VENTAS / MERMAS / COMPRAS)
   ======================================================== */

async function loadReportesPreview() {
    const dateFrom = document.getElementById('filter-reportes-from').value;
    const dateTo = document.getElementById('filter-reportes-to').value;

    if (!dateFrom || !dateTo) {
        window.showToast("Debe seleccionar ambas fechas.", "warning");
        return;
    }
    
    if (new Date(dateFrom) > new Date(dateTo)) {
        window.showToast("La fecha de inicio no puede ser mayor a la final.", "warning");
        return;
    }

    const btnFilter = document.getElementById('btn-filter-reportes');
    const originalText = btnFilter.innerHTML;
    btnFilter.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    btnFilter.disabled = true;

    try {
        const token = getAuthToken();
        const url = `${REPORTES_API_URL}/?fecha_inicio=${dateFrom}&fecha_fin=${dateTo}`;
        
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

        const data = await response.json();
        renderReportesPreview(data);

    } catch (error) {
        console.error("Error al cargar reporte:", error);
        window.showToast("Error al cargar la vista previa de reportes.", "error");
    } finally {
        btnFilter.innerHTML = originalText;
        btnFilter.disabled = false;
    }
}

function renderReportesPreview(data) {
    document.getElementById('reportes-total-ventas').textContent = `Q ${data.totales.ventas.toFixed(2)}`;
    document.getElementById('reportes-count-ventas').textContent = `${data.ventas.length} registros`;
    
    document.getElementById('reportes-total-mermas').textContent = `Q ${data.totales.mermas.toFixed(2)}`;
    document.getElementById('reportes-count-mermas').textContent = `${data.mermas.length} registros`;
    
    document.getElementById('reportes-total-compras').textContent = `Q ${data.totales.compras.toFixed(2)}`;
    document.getElementById('reportes-count-compras').textContent = `${data.compras.length} registros`;

    const tbody = document.getElementById('reportes-table-body');
    tbody.innerHTML = '';

    if (data.ventas.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted py-4">No se encontraron ventas en el periodo seleccionado</td></tr>';
        return;
    }

    const recientes = data.ventas.slice(0, 10);
    recientes.forEach(v => {
        const tr = document.createElement('tr');
        const badgeColor = v.estado === 'Completada' ? 'bg-success' : (v.estado === 'Anulada' ? 'bg-danger' : 'bg-warning');

        tr.innerHTML = `
            <td>${new Date(v.fecha).toLocaleString()}</td>
            <td><span class="badge ${badgeColor}">${v.estado}</span></td>
            <td>${v.vendedor}</td>
            <td class="text-end">Q ${v.subtotal.toFixed(2)}</td>
            <td class="text-end">Q ${v.descuento.toFixed(2)}</td>
            <td class="text-end fw-bold text-teal">Q ${v.total.toFixed(2)}</td>
        `;
        tbody.appendChild(tr);
    });
    
    if (data.ventas.length > 10) {
        const extraRow = document.createElement('tr');
        extraRow.innerHTML = `<td colspan="6" class="text-center text-muted small bg-light">Mostrando 10 de ${data.ventas.length} ventas. Descargue el reporte para ver el detalle completo.</td>`;
        tbody.appendChild(extraRow);
    }
}

async function exportReporte(formato) {
    const dateFrom = document.getElementById('filter-reportes-from').value;
    const dateTo = document.getElementById('filter-reportes-to').value;

    if (!dateFrom || !dateTo) {
        window.showToast("Debe seleccionar ambas fechas.", "warning");
        return;
    }

    const url = `${REPORTES_API_URL}/exportar?fecha_inicio=${dateFrom}&fecha_fin=${dateTo}&formato=${formato}`;
    const defaultFilename = `Reporte_${dateFrom}_al_${dateTo}.${formato === 'excel' ? 'xlsx' : 'csv'}`;
    await downloadReporteFile(url, defaultFilename);
}

/* ========================================================
   2. REPORTE DE USUARIOS (LISTADO, FICHA, EXPORTACIÓN)
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
    tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4"><span class="spinner-border spinner-border-sm me-2"></span>Cargando usuarios...</td></tr>';

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

        data.forEach((u, index) => {
            const tr = document.createElement('tr');
            const estadoBadge = u.estado === 'Activo'
                ? '<span class="badge bg-success">Activo</span>'
                : '<span class="badge bg-secondary">Inactivo</span>';

            const fechaStr = u.fecha_creacion ? new Date(u.fecha_creacion).toLocaleDateString() : '-';

            tr.innerHTML = `
                <td>${index + 1}</td>
                <td class="fw-semibold text-dark">${u.username}</td>
                <td>${u.nombre_completo || '-'}</td>
                <td><span class="badge bg-light text-dark border">${u.rol_nombre || '-'}</span></td>
                <td>${estadoBadge}</td>
                <td>${fechaStr}</td>
                <td class="text-center">
                    <button class="btn btn-sm btn-outline-primary btn-ver-usuario" data-id="${u.id_usuario}">
                        <i class="bi bi-eye me-1"></i>Ver
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
        document.getElementById('ficha-usuario-username').textContent = data.username;
        document.getElementById('ficha-usuario-nombre').textContent = data.nombre_completo;
        document.getElementById('ficha-usuario-rol').textContent = data.rol_nombre || '-';
        
        const estadoEl = document.getElementById('ficha-usuario-estado');
        estadoEl.textContent = data.estado;
        estadoEl.className = data.estado === 'Activo' ? 'badge bg-success' : 'badge bg-secondary';

        const fechaStr = data.fecha_creacion ? new Date(data.fecha_creacion).toLocaleString() : '-';
        document.getElementById('ficha-usuario-fecha').textContent = fechaStr;

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
   3. REPORTE DE CLIENTES (LISTADO, FICHA, EXPORTACIÓN)
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
    tbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-4"><span class="spinner-border spinner-border-sm me-2"></span>Cargando clientes...</td></tr>';

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
        if (data.direccion) ubicacionParts.push(`Dirección: ${data.direccion}`);
        document.getElementById('ficha-cliente-ubicacion').textContent = ubicacionParts.join(' | ') || 'Sin ubicación registrada';

        // Contactos
        const telList = (data.telefonos || []).map(t => `<div><i class="bi bi-telephone me-1"></i><strong>Teléfono:</strong> ${t}</div>`);
        const emailList = (data.correos || []).map(e => `<div><i class="bi bi-envelope me-1"></i><strong>Correo:</strong> ${e}</div>`);
        const allContacts = [...telList, ...emailList];
        const contactosEl = document.getElementById('ficha-cliente-contactos');
        if (allContacts.length === 0) {
            contactosEl.textContent = 'Sin teléfonos ni correos registrados';
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
