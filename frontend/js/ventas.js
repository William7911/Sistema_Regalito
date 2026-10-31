// ============================================================================
// Módulo de Ventas - Tienda el Regalito
// Historial de ventas, filtros de fecha, paginación y reimpresión de tickets
// ============================================================================

(function () {
    'use strict';

    let ventasData = [];
    let currentPage = 1;
    const pageSize = 15;

    function token() {
        return localStorage.getItem('jwt_token') || sessionStorage.getItem('jwt_token') || '';
    }

    function fmtQ(val) {
        return `Q ${Number(val || 0).toFixed(2)}`;
    }

    function fmtFecha(iso) {
        if (!iso) return '—';
        const d = new Date(iso);
        if (isNaN(d.getTime())) return iso;
        return d.toLocaleString('es-GT', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    function esc(val) {
        return String(val == null ? '' : val)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;');
    }

    async function cargarVentas() {
        const tbody = document.getElementById('ventas-table-body');
        const empty = document.getElementById('ventas-empty');
        const pagination = document.getElementById('ventas-pagination');
        if (!tbody) return;

        const from = document.getElementById('filter-ventas-from')?.value || '';
        const to = document.getElementById('filter-ventas-to')?.value || '';

        const params = new URLSearchParams({ limit: '300' });
        if (from) params.append('fecha_desde', from);
        if (to) params.append('fecha_hasta', to);

        tbody.innerHTML = typeof window.renderSkeletonTable === 'function'
            ? window.renderSkeletonTable(6, 9)
            : '<tr><td colspan="9" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Cargando ventas...</td></tr>';

        try {
            const res = await fetch(`/api/ventas?${params.toString()}`, {
                headers: { 'Authorization': `Bearer ${token()}` }
            });

            if (res.status === 401) {
                if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
                return;
            }

            if (!res.ok) throw new Error(`Error ${res.status}`);
            const data = await res.json();
            ventasData = Array.isArray(data.items) ? data.items : [];
            renderTabla();
        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="9" class="text-center py-4 text-danger"><i class="bi bi-exclamation-triangle me-1"></i>${esc(err.message)}</td></tr>`;
            if (typeof window.showToast === 'function') {
                window.showToast('Error al cargar ventas: ' + err.message, 'danger');
            }
        }
    }

    function renderTabla() {
        const tbody = document.getElementById('ventas-table-body');
        const empty = document.getElementById('ventas-empty');
        const pagination = document.getElementById('ventas-pagination');
        if (!tbody) return;

        tbody.innerHTML = '';
        if (ventasData.length === 0) {
            if (empty) empty.classList.remove('d-none');
            if (pagination) pagination.classList.add('d-none');
            return;
        }
        if (empty) empty.classList.add('d-none');

        const totalPages = Math.ceil(ventasData.length / pageSize) || 1;
        if (currentPage > totalPages) currentPage = totalPages;
        const start = (currentPage - 1) * pageSize;
        const pageData = ventasData.slice(start, start + pageSize);

        const pageInfo = document.getElementById('ventas-page-info');
        if (pageInfo) pageInfo.textContent = `Página ${currentPage} de ${totalPages} (${ventasData.length} ventas)`;
        const prevBtn = document.getElementById('ventas-prev-page');
        const nextBtn = document.getElementById('ventas-next-page');
        if (prevBtn) prevBtn.disabled = currentPage === 1;
        if (nextBtn) nextBtn.disabled = currentPage === totalPages;
        if (pagination) pagination.classList.toggle('d-none', ventasData.length === 0);

        pageData.forEach(v => {
            const articulos = (v.detalles || []).reduce((s, d) => s + Number(d.cantidad || 0), 0);
            const cajero = v.usuario ? (v.usuario.nombre_completo || v.usuario.username || `#${v.id_usuario}`) : `#${v.id_usuario || '—'}`;
            const estadoBadge = v.estado === 'Completada'
                ? '<span class="badge bg-success-subtle text-success border border-success-subtle">Completada</span>'
                : v.estado === 'Anulada'
                    ? '<span class="badge bg-danger-subtle text-danger border border-danger-subtle">Anulada</span>'
                    : `<span class="badge bg-secondary-subtle text-secondary">${esc(v.estado)}</span>`;

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td class="fw-bold px-3 text-dark">#${v.id_venta}</td>
                <td class="small text-muted">${fmtFecha(v.fecha_venta)}</td>
                <td class="small">${esc(cajero)}</td>
                <td class="text-center small"><span class="badge bg-light text-dark border px-2 py-1">${articulos} uds</span></td>
                <td class="text-end small">${fmtQ(v.subtotal)}</td>
                <td class="text-end small text-danger">${Number(v.descuento_total || 0) > 0 ? `- ${fmtQ(v.descuento_total)}` : 'Q 0.00'}</td>
                <td class="text-end fw-bold px-3 text-teal">${fmtQ(v.total_venta)}</td>
                <td class="text-center">${estadoBadge}</td>
                <td class="text-center">
                    <button type="button" class="btn btn-sm btn-outline-teal" data-venta-id="${v.id_venta}" title="Reimprimir Ticket">
                        <i class="bi bi-printer me-1"></i>Ticket
                    </button>
                </td>
            `;
            tbody.appendChild(tr);
        });
    }

    async function imprimirTicket(idVenta) {
        let venta = ventasData.find(v => Number(v.id_venta) === Number(idVenta));
        // Si no tiene detalles completos, consultamos la API
        if (!venta || !venta.detalles || venta.detalles.length === 0) {
            try {
                const res = await fetch(`/api/ventas/${idVenta}`, {
                    headers: { 'Authorization': `Bearer ${token()}` }
                });
                if (res.ok) {
                    venta = await res.json();
                }
            } catch (_) {}
        }

        if (!venta) {
            if (typeof window.showToast === 'function') window.showToast('No se encontró la información de la venta.', 'warning');
            return;
        }

        const articulos = (venta.detalles || []).reduce((s, d) => s + Number(d.cantidad || 0), 0);
        const cajero = venta.usuario ? (venta.usuario.nombre_completo || venta.usuario.username) : 'Cajero';
        const fecha = fmtFecha(venta.fecha_venta);
        const fechaSimple = venta.fecha_venta ? String(venta.fecha_venta).slice(0, 10) : 'hoy';

        const items = (venta.detalles || []).map(d => {
            const variant = [d.talla, d.color].filter(Boolean).join(' · ');
            return `
                <div style="margin-bottom: 4px;">
                    <div style="font-weight: bold; font-size: 11px;">${esc(d.nombre_producto || 'Producto')}</div>
                    ${variant ? `<div style="font-size: 10px; color: #555;">${esc(variant)}</div>` : ''}
                    <div style="display: flex; justify-content: space-between; font-size: 11px;">
                        <span>${Number(d.cantidad)} x ${fmtQ(d.precio_unitario)}</span>
                        <span>${fmtQ(d.subtotal)}</span>
                    </div>
                </div>
            `;
        }).join('<hr style="margin: 3px 0; border: none; border-top: 1px dashed #ccc;">');

        const pagos = (venta.pagos || []).map(p => {
            const metodo = p.metodo_pago ? p.metodo_pago.nombre : (Number(p.id_metodo_pago) === 1 ? 'Efectivo' : 'Transferencia');
            return `
                <div style="display: flex; justify-content: space-between; font-size: 11px;">
                    <span>Pago ${esc(metodo)}:</span>
                    <span>${fmtQ(p.monto_recibido)}</span>
                </div>
            `;
        }).join('');

        const cambio = venta.cambio ? fmtQ(venta.cambio) : 'Q 0.00';

        const ticketDoc = `<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Ticket-${venta.id_venta}-${fechaSimple}</title>
    <style>
        body {
            font-family: 'Courier New', Courier, monospace;
            width: 78mm;
            margin: 0 auto;
            padding: 8px;
            color: #000;
            font-size: 11px;
        }
        .center { text-align: center; }
        .bold { font-weight: bold; }
        .sep { border: none; border-top: 1px dashed #000; margin: 6px 0; }
        .row { display: flex; justify-content: space-between; font-size: 11px; }
        .total-row { font-size: 13px; font-weight: bold; display: flex; justify-content: space-between; margin: 4px 0; }
        @media print {
            body { width: 100%; margin: 0; padding: 0; }
            @page { size: 80mm auto; margin: 2mm; }
        }
    </style>
</head>
<body>
    <div class="center bold" style="font-size: 14px;">Curiosidades El Regalito</div>
    <div class="center" style="font-size: 11px;">Tienda de regalos · Guatemala</div>
    <div class="center" style="font-size: 10px;">Precios en Quetzales (Q)</div>
    <hr class="sep">
    <div class="row"><span>TICKET:</span><span class="bold">#${venta.id_venta}</span></div>
    <div class="row"><span>FECHA:</span><span>${fecha}</span></div>
    <div class="row"><span>CAJERO:</span><span>${esc(cajero)}</span></div>
    <hr class="sep">
    <div class="row bold"><span>CANT. x PRECIO</span><span>IMPORTE</span></div>
    <hr class="sep">
    ${items}
    <hr class="sep">
    <div class="row"><span>SUBTOTAL:</span><span>${fmtQ(venta.subtotal)}</span></div>
    <div class="row"><span>DESCUENTO:</span><span>- ${fmtQ(venta.descuento_total)}</span></div>
    <div class="row"><span>ARTÍCULOS:</span><span>${articulos}</span></div>
    <div class="total-row"><span>TOTAL:</span><span>${fmtQ(venta.total_venta)}</span></div>
    <hr class="sep">
    ${pagos}
    <div class="row"><span>CAMBIO:</span><span>${cambio}</span></div>
    <hr class="sep">
    <div class="center bold" style="margin-top: 6px;">¡Gracias por su compra!</div>
    <div class="center" style="font-size: 10px; color: #444;">Conserve este ticket · Vuelva pronto</div>
    <script>
        window.addEventListener('load', () => {
            window.focus();
            setTimeout(() => { window.print(); }, 250);
        });
    </script>
</body>
</html>`;

        const printWindow = window.open('', `ticket_${venta.id_venta}`, 'width=420,height=600');
        if (!printWindow) {
            if (typeof window.showToast === 'function') {
                window.showToast('Permite ventanas emergentes para imprimir el ticket.', 'warning');
            }
            return;
        }
        printWindow.document.open();
        printWindow.document.write(ticketDoc);
        printWindow.document.close();
    }

    function setupEventListeners() {
        const btnFilter = document.getElementById('btn-filter-ventas');
        if (btnFilter) {
            btnFilter.addEventListener('click', () => {
                currentPage = 1;
                cargarVentas();
            });
        }

        const btnClear = document.getElementById('btn-clear-ventas-filters');
        if (btnClear) {
            btnClear.addEventListener('click', () => {
                const from = document.getElementById('filter-ventas-from');
                const to = document.getElementById('filter-ventas-to');
                if (from) from.value = '';
                if (to) to.value = '';
                currentPage = 1;
                cargarVentas();
            });
        }

        const prevBtn = document.getElementById('ventas-prev-page');
        if (prevBtn) {
            prevBtn.addEventListener('click', () => {
                if (currentPage > 1) {
                    currentPage--;
                    renderTabla();
                }
            });
        }

        const nextBtn = document.getElementById('ventas-next-page');
        if (nextBtn) {
            nextBtn.addEventListener('click', () => {
                const total = Math.ceil(ventasData.length / pageSize) || 1;
                if (currentPage < total) {
                    currentPage++;
                    renderTabla();
                }
            });
        }

        const tbody = document.getElementById('ventas-table-body');
        if (tbody) {
            tbody.addEventListener('click', e => {
                const btn = e.target.closest('button[data-venta-id]');
                if (!btn) return;
                imprimirTicket(Number(btn.dataset.ventaId));
            });
        }
    }

    window.showVentasModule = function () {
        cargarVentas();
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', setupEventListeners);
    } else {
        setupEventListeners();
    }
})();
