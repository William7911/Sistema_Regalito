// ============================================================================
// Campanita de notificaciones - Alertas de stock pendientes
// Consulta GET /api/inventario/alertas (solo estado 'Pendiente') y, cuando hay
// alertas, enciende el punto rojo (#badge-notificaciones) y llena el dropdown
// (#lista-notificaciones) con mensajes tipo "Producto X por debajo del stock
// mínimo". Se ejecuta al iniciar la aplicación y al abrir el dropdown.
// Incluye acción para marcar la alerta como "Atendida" con registro en bitácora.
// ============================================================================

window.cargarNotificaciones = async function() {
    const token = localStorage.getItem('jwt_token');
    if (!token) return;

    const badge = document.getElementById('badge-notificaciones');
    const contenido = document.getElementById('notificaciones-contenido');
    if (!badge || !contenido) return;

    try {
        const response = await fetch('/api/inventario/alertas', {
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

        const alertas = await response.json();
        renderNotificaciones(alertas, badge, contenido);
    } catch (error) {
        console.error('Error al cargar las notificaciones de stock:', error);
        badge.classList.add('d-none');
        renderVacio(contenido, 'No se pudieron cargar las notificaciones.');
    }
};

function renderNotificaciones(alertas, badge, contenido) {
    contenido.textContent = '';

    const lista = Array.isArray(alertas) ? alertas : [];
    if (lista.length === 0) {
        badge.classList.add('d-none');
        renderVacio(contenido, 'Sin alertas de stock pendientes.');
        return;
    }

    badge.textContent = String(lista.length);
    badge.classList.remove('d-none');

    const canAttend = (typeof window.isAdmin === 'function' && window.isAdmin()) ||
                      (typeof window.hasPermission === 'function' && window.hasPermission('INV_INGRESAR_MERCADERIA'));

    lista.forEach(alerta => {
        const item = document.createElement('div');
        item.className = 'dropdown-item-text border-bottom py-2 small d-flex justify-content-between align-items-center gap-2';

        const infoDiv = document.createElement('div');
        infoDiv.className = 'flex-grow-1';

        const mensaje = (alerta.producto_nombre)
            ? `${alerta.producto_nombre} por debajo del stock mínimo`
            : (alerta.mensaje || 'Alerta de stock');

        const texto = document.createElement('div');
        texto.className = 'fw-semibold text-danger';
        texto.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-1"></i>${escapeHtml(mensaje)}`;
        infoDiv.appendChild(texto);

        if (alerta.stock_actual !== null && alerta.stock_minimo !== null) {
            const detalle = document.createElement('small');
            detalle.className = 'text-muted d-block';
            detalle.textContent = `Stock actual: ${alerta.stock_actual} · Mínimo: ${alerta.stock_minimo}`;
            infoDiv.appendChild(detalle);
        }
        item.appendChild(infoDiv);

        if (canAttend) {
            const btnAtender = document.createElement('button');
            btnAtender.type = 'button';
            btnAtender.className = 'btn btn-outline-success btn-xs py-1 px-2 btn-atender-alerta flex-shrink-0';
            btnAtender.innerHTML = '<i class="bi bi-check-lg"></i> Atender';
            btnAtender.title = 'Marcar alerta como atendida';
            btnAtender.addEventListener('click', async (e) => {
                e.stopPropagation();
                await window.atenderAlertaStock(alerta.id_alerta, btnAtender);
            });
            item.appendChild(btnAtender);
        }

        contenido.appendChild(item);
    });
}

function renderVacio(contenido, mensaje) {
    contenido.textContent = '';
    const item = document.createElement('div');
    item.className = 'dropdown-item-text text-muted small py-3 text-center';
    item.textContent = mensaje;
    contenido.appendChild(item);
}

window.atenderAlertaStock = async function(idAlerta, btnEl) {
    const token = localStorage.getItem('jwt_token');
    if (!token) return;

    try {
        if (btnEl) {
            btnEl.disabled = true;
            btnEl.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
        }

        const res = await fetch(`/api/inventario/alertas/${idAlerta}/atender`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (res.status === 401) {
            if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
            return;
        }

        if (!res.ok) {
            let detail = 'Error al atender la alerta';
            try { const d = await res.json(); detail = d.detail || detail; } catch (_) {}
            throw new Error(detail);
        }

        if (typeof window.showToast === 'function') {
            window.showToast('Alerta de stock marcada como atendida.', 'success');
        }

        await window.cargarNotificaciones();
        if (typeof window.cargarAlertasInventarioModal === 'function') {
            await window.cargarAlertasInventarioModal();
        }
    } catch (err) {
        if (typeof window.showToast === 'function') {
            window.showToast(err.message || 'Error al atender alerta', 'danger');
        }
    } finally {
        if (btnEl) {
            btnEl.disabled = false;
            btnEl.innerHTML = '<i class="bi bi-check-lg"></i> Atender';
        }
    }
};

function escapeHtml(text) {
    if (!text) return '';
    const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' };
    return String(text).replace(/[&<>"']/g, m => map[m]);
}

const btnNotificaciones = document.getElementById('btn-notificaciones');
if (btnNotificaciones) {
    btnNotificaciones.addEventListener('click', () => {
        if (typeof window.cargarNotificaciones === 'function') window.cargarNotificaciones();
    });
}
