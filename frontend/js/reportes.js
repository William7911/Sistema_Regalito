document.addEventListener('DOMContentLoaded', () => {
    // Escuchar cambios de vista
    window.addEventListener('viewChanged', (e) => {
        if (e.detail.view === 'reportes') {
            initReportesView();
        }
    });

    // Configurar fechas por defecto al cargar (inicio de mes y hoy)
    const dateFrom = document.getElementById('filter-reportes-from');
    const dateTo = document.getElementById('filter-reportes-to');
    
    if (dateFrom && dateTo) {
        const today = new Date();
        const firstDay = new Date(today.getFullYear(), today.getMonth(), 1);
        
        dateTo.valueAsDate = today;
        dateFrom.valueAsDate = firstDay;
    }

    // Botones
    document.getElementById('btn-filter-reportes')?.addEventListener('click', loadReportesPreview);
    document.getElementById('btn-export-excel')?.addEventListener('click', () => exportReporte('excel'));
    document.getElementById('btn-export-csv')?.addEventListener('click', () => exportReporte('csv'));
});

/**
 * Inicializa la vista de reportes, valida permisos y carga la vista previa.
 */
function initReportesView() {
    if (!window.isAdmin()) {
        window.showToast("Acceso denegado. Se requiere rol de Administradora.", "error");
        window.navigateTo('dashboard');
        return;
    }
    loadReportesPreview();
}

/**
 * Carga el resumen de reportes desde el backend y actualiza las tarjetas y la tabla
 */
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
        const token = window.getAuthToken();
        const url = `${API_URL}/api/reportes/?fecha_inicio=${dateFrom}&fecha_fin=${dateTo}`;
        
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

/**
 * Renderiza los datos en pantalla
 */
function renderReportesPreview(data) {
    // Actualizar KPIs
    document.getElementById('reportes-total-ventas').textContent = `Q ${data.totales.ventas.toFixed(2)}`;
    document.getElementById('reportes-count-ventas').textContent = `${data.ventas.length} registros`;
    
    document.getElementById('reportes-total-mermas').textContent = `Q ${data.totales.mermas.toFixed(2)}`;
    document.getElementById('reportes-count-mermas').textContent = `${data.mermas.length} registros`;
    
    document.getElementById('reportes-total-compras').textContent = `Q ${data.totales.compras.toFixed(2)}`;
    document.getElementById('reportes-count-compras').textContent = `${data.compras.length} registros`;

    // Actualizar tabla (Mostramos máximo las últimas 10 ventas)
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

/**
 * Descarga el reporte consolidado en formato Excel o CSV
 */
async function exportReporte(formato) {
    const dateFrom = document.getElementById('filter-reportes-from').value;
    const dateTo = document.getElementById('filter-reportes-to').value;

    if (!dateFrom || !dateTo) {
        window.showToast("Debe seleccionar ambas fechas.", "warning");
        return;
    }

    try {
        const token = window.getAuthToken();
        const url = `${API_URL}/api/reportes/exportar?fecha_inicio=${dateFrom}&fecha_fin=${dateTo}&formato=${formato}`;
        
        window.showToast(`Generando archivo ${formato.toUpperCase()}...`, "info");
        
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
        
        // Obtener el nombre del archivo del header o usar uno por defecto
        let filename = `Reporte_${dateFrom}_al_${dateTo}.${formato === 'excel' ? 'xlsx' : 'csv'}`;
        const disposition = response.headers.get('Content-Disposition');
        if (disposition && disposition.indexOf('filename=') !== -1) {
            const matches = /filename="?([^"]+)"?/.exec(disposition);
            if (matches != null && matches[1]) {
                filename = matches[1];
            }
        }

        // Crear un enlace temporal para descargar
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        
        // Limpieza
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
        
        window.showToast(`Reporte ${formato.toUpperCase()} descargado exitosamente`, "success");

    } catch (error) {
        console.error("Error al exportar reporte:", error);
        window.showToast("Ocurrió un error al intentar exportar el reporte", "error");
    }
}
