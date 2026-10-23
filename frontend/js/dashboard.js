// ============================================================================
// Panel Principal (Dashboard) - Métricas en tiempo real desde la API
// Consulta GET /api/dashboard/resumen y actualiza las tarjetas KPI del DOM.
// Cero datos de relleno: los números provienen 100% de la base de datos.
// ============================================================================

window.showDashboardModule = async function() {
    await cargarResumenDashboard();
};

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

function setValorNumerico(id, valor, etiqueta) {
    const el = document.getElementById(id);
    if (!el) return;
    el.textContent = String(Number(valor) || 0);
    if (etiqueta) {
        const small = el.nextElementSibling;
        if (small && small.tagName === 'SMALL') small.textContent = etiqueta;
    }
}

async function cargarResumenDashboard() {
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

        // Ventas de hoy
        if (data.ventas_hoy) {
            setTexto('dash-ventas-hoy', formatoQuetzal(data.ventas_hoy.total));
            const ventas = data.ventas_hoy.cantidad || 0;
            setTexto('dash-ventas-hoy-detalle', `${ventas} ${ventas === 1 ? 'venta' : 'ventas'} registrada${ventas === 1 ? '' : 's'} hoy`);
        }

        // Stock crítico (productos con stock <= mínimo)
        const stock = data.stock_critico || 0;
        setValorNumerico('dash-stock-critico', stock, stock === 1 ? 'producto' : 'productos');

        // Compras del mes
        if (data.compras_mes) {
            setTexto('dash-compras-mes', formatoQuetzal(data.compras_mes.total));
            const compras = data.compras_mes.cantidad || 0;
            setTexto('dash-compras-mes-detalle', `${compras} ${compras === 1 ? 'compra' : 'compras'} registrada${compras === 1 ? '' : 's'} este mes`);
        }

        // Turnos de caja activos
        const turnos = data.turnos_activos || 0;
        setValorNumerico('dash-turnos-activos', turnos, turnos === 1 ? 'turno' : 'turnos');

    } catch (error) {
        console.error('Error al cargar el resumen del dashboard:', error);
        if (typeof window.showToast === 'function') {
            window.showToast('No se pudieron cargar las métricas del panel.', 'danger');
        }
        // Valores por defecto honestos (cero) ante fallo de conexión
        setTexto('dash-ventas-hoy', 'Q 0.00');
        setTexto('dash-ventas-hoy-detalle', 'Sin datos disponibles');
        setValorNumerico('dash-stock-critico', 0, 'productos');
        setTexto('dash-compras-mes', 'Q 0.00');
        setTexto('dash-compras-mes-detalle', 'Sin datos disponibles');
        setValorNumerico('dash-turnos-activos', 0, 'turnos');
    }
}