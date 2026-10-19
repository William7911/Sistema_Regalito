// ============================================================================
// Campanita de notificaciones - Alertas de stock pendientes
// Consulta GET /api/inventario/alertas (solo estado 'Pendiente') y, cuando hay
// alertas, enciende el punto rojo (#badge-notificaciones) y llena el dropdown
// (#lista-notificaciones) con mensajes tipo "Producto X por debajo del stock
// mínimo". Se ejecuta al iniciar la aplicación y al abrir el dropdown.
// Cero datos de relleno: todo proviene de la base de datos.
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

    lista.forEach(alerta => {
        const item = document.createElement('button');
        item.type = 'button';
        item.className = 'dropdown-item text-wrap small';

        const mensaje = (alerta.producto_nombre)
            ? `${alerta.producto_nombre} por debajo del stock mínimo`
            : (alerta.mensaje || 'Alerta de stock');

        const texto = document.createElement('span');
        texto.textContent = mensaje;
        item.appendChild(texto);

        if (alerta.stock_actual !== null && alerta.stock_minimo !== null) {
            const detalle = document.createElement('small');
            detalle.className = 'text-muted d-block';
            detalle.textContent = `Stock actual: ${alerta.stock_actual} · Mínimo: ${alerta.stock_minimo}`;
            item.appendChild(detalle);
        }

        contenido.appendChild(item);
    });
}

function renderVacio(contenido, mensaje) {
    contenido.textContent = '';
    const item = document.createElement('div');
    item.className = 'dropdown-item-text text-muted small';
    item.textContent = mensaje;
    contenido.appendChild(item);
}

const btnNotificaciones = document.getElementById('btn-notificaciones');
if (btnNotificaciones) {
    btnNotificaciones.addEventListener('click', () => {
        if (typeof window.cargarNotificaciones === 'function') window.cargarNotificaciones();
    });
}