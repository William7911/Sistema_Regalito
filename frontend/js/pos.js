// Curiosidades El Regalito - POS / Ventas Module Logic
(function() {
    let state = {
        turno: null,
        sucursalId: null,
        catalog: [],
        cart: [],
    };
    let page = 1;
    const PAGE_SIZE = 8;

    const DOM = {
        view: document.getElementById('pos-view'),
        turnBadge: document.getElementById('pos-turn-badge'),
        turnText: document.getElementById('pos-turn-text'),
        noShift: document.getElementById('pos-no-shift'),
        workspace: document.getElementById('pos-workspace'),
        search: document.getElementById('pos-search'),
        barcode: document.getElementById('pos-barcode'),
        btnFilter: document.getElementById('btn-pos-filter'),
        btnRefresh: document.getElementById('btn-pos-refresh'),
        grid: document.getElementById('pos-products-grid'),
        gridEmpty: document.getElementById('pos-products-empty'),
        gridInfo: document.getElementById('pos-grid-info'),
        gridPage: document.getElementById('pos-grid-page'),
        gridPrev: document.getElementById('pos-grid-prev'),
        gridNext: document.getElementById('pos-grid-next'),
        cartEmpty: document.getElementById('pos-cart-empty'),
        cartTable: document.getElementById('pos-cart-table'),
        cartBody: document.getElementById('pos-cart-body'),
        subtotal: document.getElementById('pos-subtotal'),
        discount: document.getElementById('pos-discount'),
        total: document.getElementById('pos-total'),
        cashReceived: document.getElementById('pos-cash-received'),
        transferAmount: document.getElementById('pos-transfer-amount'),
        received: document.getElementById('pos-received'),
        change: document.getElementById('pos-change'),
        btnCharge: document.getElementById('btn-pos-charge'),
        btnClear: document.getElementById('btn-pos-clear'),
        historyBody: document.getElementById('pos-history-body'),
        historyEmpty: document.getElementById('pos-history-empty'),
        btnReloadHistory: document.getElementById('btn-pos-reload-history'),
        ticketModal: document.getElementById('pos-ticket-modal'),
        ticketId: document.getElementById('ticket-id'),
        ticketFecha: document.getElementById('ticket-fecha'),
        ticketItems: document.getElementById('ticket-items'),
        ticketSubtotal: document.getElementById('ticket-subtotal'),
        ticketDiscount: document.getElementById('ticket-discount'),
        ticketTotal: document.getElementById('ticket-total'),
        ticketCash: document.getElementById('ticket-cash'),
        ticketTransfer: document.getElementById('ticket-transfer'),
        ticketChange: document.getElementById('ticket-change'),
    };

    let ticketBsModal = null;

    document.addEventListener('DOMContentLoaded', () => {
        if (DOM.ticketModal) {
            ticketBsModal = new bootstrap.Modal(DOM.ticketModal);
        }
        setupEvents();
    });

    function setupEvents() {
        if (DOM.btnFilter) DOM.btnFilter.addEventListener('click', () => {
            page = 1;
            renderGrid();
        });
        if (DOM.search) DOM.search.addEventListener('input', () => {
            page = 1;
            renderGrid();
        });
        if (DOM.barcode) DOM.barcode.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                addByBarcode(DOM.barcode.value.trim());
            }
        });
        if (DOM.btnRefresh) DOM.btnRefresh.addEventListener('click', () => {
            loadProducts();
        });
        if (DOM.gridPrev) DOM.gridPrev.addEventListener('click', () => {
            if (page > 1) { page--; renderGrid(); }
        });
        if (DOM.gridNext) DOM.gridNext.addEventListener('click', () => {
            const totalPages = Math.ceil(filteredCatalog().length / PAGE_SIZE) || 1;
            if (page < totalPages) { page++; renderGrid(); }
        });
        if (DOM.btnClear) DOM.btnClear.addEventListener('click', clearCart);
        if (DOM.btnCharge) DOM.btnCharge.addEventListener('click', cobrar);
        if (DOM.cashReceived) DOM.cashReceived.addEventListener('input', renderTotals);
        if (DOM.transferAmount) DOM.transferAmount.addEventListener('input', renderTotals);
        if (DOM.btnReloadHistory) DOM.btnReloadHistory.addEventListener('click', loadHistory);
        if (DOM.barcode) DOM.barcode.addEventListener('focus', () => DOM.barcode.select());
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'enter') {
                if (DOM.btnCharge && !DOM.btnCharge.disabled) {
                    e.preventDefault();
                    cobrar();
                }
            }
            if (e.key === 'Escape' && DOM.view && !DOM.view.classList.contains('d-none')) {
                if (DOM.search) DOM.search.focus();
            }
        });
    }

    function token() {
        return localStorage.getItem('jwt_token') || '';
    }

    async function apiGet(url) {
        const res = await fetch(url, { headers: { 'Authorization': `Bearer ${token()}` } });
        if (res.status === 401) {
            if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
            throw new Error('Sesión expirada');
        }
        if (!res.ok) {
            let detail = 'Error en la petición';
            try {
                const data = await res.json();
                detail = data.detail || detail;
            } catch (_) { }
            throw new Error(detail);
        }
        return res.json();
    }

    async function apiPost(url, payload) {
        const res = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token()}`,
            },
            body: JSON.stringify(payload),
        });
        if (res.status === 401) {
            if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
            throw new Error('Sesión expirada');
        }
        if (res.status === 403) {
            let detail = 'No tienes permisos para esta operación';
            try {
                const data = await res.json();
                detail = data.detail || detail;
            } catch (_) { }
            throw new Error(detail);
        }
        if (!res.ok) {
            let detail = 'Error al procesar la venta';
            try {
                const data = await res.json();
                detail = data.detail || detail;
            } catch (_) { }
            throw new Error(detail);
        }
        return res.json();
    }

    function fmtQ(value) {
        const num = Number(value || 0);
        return `Q ${num.toFixed(2)}`;
    }

    window.showPOSModule = async function() {
        await loadTurno();
        if (state.turno) {
            await loadProducts();
            await loadHistory();
        }
    };

    async function loadTurno() {
        try {
            const turno = await apiGet('/api/caja/estado-actual');
            state.turno = turno;
            if (!turno) {
                if (DOM.workspace) DOM.workspace.classList.add('d-none');
                if (DOM.noShift) DOM.noShift.classList.remove('d-none');
                if (DOM.turnText) DOM.turnText.textContent = 'Sin turno abierto';
                if (DOM.turnBadge) DOM.turnBadge.classList.replace('bg-light', 'bg-warning');
                return;
            }
            state.sucursalId = (turno.caja && turno.caja.id_sucursal) ? turno.caja.id_sucursal : null;
            const cajaDesc = (turno.caja && turno.caja.descripcion) ? turno.caja.descripcion : `Caja #${turno.id_caja}`;
            if (DOM.turnText) DOM.turnText.textContent = `${cajaDesc} · Inicial Q ${Number(turno.monto_apertura || 0).toFixed(2)}`;
            if (DOM.noShift) DOM.noShift.classList.add('d-none');
            if (DOM.workspace) DOM.workspace.classList.remove('d-none');
        } catch (err) {
            if (err.message === 'Sesión expirada') return;
            if (DOM.workspace) DOM.workspace.classList.add('d-none');
            if (DOM.turnText) DOM.turnText.textContent = 'Error al consultar turno';
            if (typeof window.showToast === 'function') {
                window.showToast(err.message, 'danger');
            }
        }
    }

    async function loadProducts() {
        if (!state.sucursalId) return;
        try {
            const data = await apiGet('/api/productos?limit=500&is_active=true');
            const flat = [];
            (data.items || []).forEach(p => {
                (p.variantes || []).forEach(v => {
                    const inv = (v.inventarios || []).find(i => i.id_sucursal === state.sucursalId);
                    if (!inv || Number(inv.stock_actual) <= 0) return;
                    flat.push({
                        id_variante: v.id_variante,
                        id_producto: p.id_producto,
                        nombre: p.nombre,
                        talla: v.talla || '',
                        color: v.color || '',
                        codigo_barras: v.codigo_barras || '',
                        precio_detalle: Number(v.precio_detalle || 0),
                        precio_mayoreo: Number(v.precio_mayoreo || 0),
                        stock: Number(inv.stock_actual),
                    });
                });
            });
            flat.sort((a, b) => (a.nombre || '').localeCompare(b.nombre || ''));
            state.catalog = flat;
            page = 1;
            renderGrid();
        } catch (err) {
            if (err.message === 'Sesión expirada') return;
            if (typeof window.showToast === 'function') {
                window.showToast(`Error al cargar catálogo: ${err.message}`, 'danger');
            }
        }
    }

    function filteredCatalog() {
        const term = (DOM.search ? DOM.search.value : '').trim().toLowerCase();
        if (!term) return state.catalog;
        return state.catalog.filter(item =>
            (item.nombre || '').toLowerCase().includes(term) ||
            (item.talla || '').toLowerCase().includes(term) ||
            (item.color || '').toLowerCase().includes(term) ||
            (item.codigo_barras || '').toLowerCase().includes(term)
        );
    }

    function renderGrid() {
        if (!DOM.grid) return;
        DOM.grid.innerHTML = '';
        const items = filteredCatalog();
        const totalPages = Math.ceil(items.length / PAGE_SIZE) || 1;
        if (page > totalPages) page = totalPages;
        const start = (page - 1) * PAGE_SIZE;
        const pageItems = items.slice(start, start + PAGE_SIZE);

        if (DOM.gridInfo) DOM.gridInfo.textContent = `${items.length} productos`;
        if (DOM.gridPage) DOM.gridPage.textContent = `Página ${page} de ${totalPages}`;
        if (DOM.gridPrev) DOM.gridPrev.disabled = page === 1;
        if (DOM.gridNext) DOM.gridNext.disabled = page === totalPages;

        if (DOM.gridEmpty) DOM.gridEmpty.classList.toggle('d-none', items.length > 0);
        if (DOM.gridInfo && DOM.gridInfo.parentElement) {
            DOM.gridInfo.parentElement.classList.toggle('d-none', items.length === 0);
        }

        pageItems.forEach(item => {
            const col = document.createElement('div');
            col.className = 'col';
            const low = item.stock <= 3;
            const variant = [item.talla, item.color].filter(Boolean).join(' · ');
            col.innerHTML = `
                <div class="card border-0 shadow-sm rounded-3 h-100 pos-product-card" data-variante="${item.id_variante}" role="button" tabindex="0" title="Clic para agregar">
                    <div class="card-body p-2">
                        <div class="d-flex justify-content-between align-items-start mb-1">
                            <h6 class="fw-bold text-dark mb-0 small text-truncate" title="${item.nombre}">${item.nombre}</h6>
                            <span class="badge ${low ? 'bg-danger' : 'bg-light text-dark'} rounded-pill small">${item.stock}</span>
                        </div>
                        <div class="text-muted small mb-1">${variant || '—'}</div>
                        <div class="text-muted small font-monospace mb-1">${item.codigo_barras || '—'}</div>
                        <div class="fw-semibold text-teal small">${fmtQ(item.precio_detalle)}</div>
                        <div class="text-muted small">Mayoreo: ${fmtQ(item.precio_mayoreo)}</div>
                    </div>
                </div>
            `;
            const card = col.querySelector('.pos-product-card');
            card.addEventListener('click', () => addToCart(item.id_variante));
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    addToCart(item.id_variante);
                }
            });
            DOM.grid.appendChild(col);
        });
    }

    function findCart(varianteId) {
        return state.cart.find(c => c.id_variante === varianteId);
    }

    function addToCart(varianteId, qty) {
        const item = state.catalog.find(i => i.id_variante === varianteId);
        if (!item) return;
        const cantidad = (qty && qty > 0) ? qty : 1;
        const existing = findCart(varianteId);
        const current = existing ? existing.cantidad : 0;
        if (current + cantidad > item.stock) {
            if (typeof window.showToast === 'function') {
                window.showToast(`Stock insuficiente para '${item.nombre}'. Disponible: ${item.stock}.`, 'danger');
            }
            return;
        }
        if (existing) {
            existing.cantidad += cantidad;
        } else {
            state.cart.push({
                id_variante: item.id_variante,
                nombre: item.nombre,
                talla: item.talla,
                color: item.color,
                precio_detalle: item.precio_detalle,
                precio_mayoreo: item.precio_mayoreo,
                stock: item.stock,
                cantidad: cantidad,
            });
        }
        renderCart();
    }

    function addByBarcode(code) {
        if (!code) return;
        const item = state.catalog.find(i => i.codigo_barras === code);
        if (!item) {
            if (typeof window.showToast === 'function') {
                window.showToast(`Código de barras '${code}' no encontrado o sin stock en esta sucursal.`, 'warning');
            }
            return;
        }
        addToCart(item.id_variante);
        if (DOM.barcode) DOM.barcode.value = '';
    }

    function setQty(varianteId, cantidad) {
        const item = findCart(varianteId);
        if (!item) return;
        if (cantidad <= 0) {
            removeFromCart(varianteId);
            return;
        }
        if (cantidad > item.stock) {
            if (typeof window.showToast === 'function') {
                window.showToast(`Stock insuficiente para '${item.nombre}'. Disponible: ${item.stock}.`, 'danger');
            }
            cantidad = item.stock;
        }
        item.cantidad = cantidad;
        renderCart();
    }

    function removeFromCart(varianteId) {
        state.cart = state.cart.filter(c => c.id_variante !== varianteId);
        renderCart();
    }

    function clearCart() {
        state.cart = [];
        renderCart();
    }

    function cartTotals() {
        let subtotalBruto = 0;
        let descuento = 0;
        state.cart.forEach(item => {
            subtotalBruto += item.precio_detalle * item.cantidad;
            if (item.cantidad >= 6) {
                descuento += (item.precio_detalle - item.precio_mayoreo) * item.cantidad;
            }
        });
        const totalVenta = Math.max(0, subtotalBruto - descuento);
        return {
            subtotalBruto: round2(subtotalBruto),
            descuento: round2(descuento),
            totalVenta: round2(totalVenta),
        };
    }

    function round2(value) {
        return Math.round((Number(value) || 0) * 100) / 100;
    }

    function renderTotals() {
        const totals = cartTotals();
        const cash = round2(DOM.cashReceived ? DOM.cashReceived.value : 0);
        const transfer = round2(DOM.transferAmount ? DOM.transferAmount.value : 0);
        const recibido = round2(cash + transfer);
        const cambio = Math.max(0, round2(recibido - totals.totalVenta));

        if (DOM.subtotal) DOM.subtotal.textContent = fmtQ(totals.subtotalBruto);
        if (DOM.discount) DOM.discount.textContent = `- ${fmtQ(totals.descuento)}`;
        if (DOM.total) DOM.total.textContent = fmtQ(totals.totalVenta);
        if (DOM.received) DOM.received.textContent = fmtQ(recibido);
        if (DOM.change) DOM.change.textContent = fmtQ(cambio);

        const canCharge = state.cart.length > 0 && recibido >= totals.totalVenta && totals.totalVenta > 0;
        if (DOM.btnCharge) DOM.btnCharge.disabled = !canCharge;
        return { cash, transfer, cambio, totalVenta: totals.totalVenta };
    }

    function renderCart() {
        if (!DOM.cartBody) return;
        DOM.cartBody.innerHTML = '';
        const hasItems = state.cart.length > 0;

        if (DOM.cartEmpty) DOM.cartEmpty.classList.toggle('d-none', hasItems);
        if (DOM.cartTable) DOM.cartTable.classList.toggle('d-none', !hasItems);

        state.cart.forEach(item => {
            const subtotalItem = round2(item.precio_detalle * item.cantidad);
            const variant = [item.talla, item.color].filter(Boolean).join(' · ');
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>
                    <div class="fw-semibold small">${item.nombre}</div>
                    <div class="text-muted small">${variant || '—'} ${item.cantidad >= 6 ? '<span class="badge bg-success">mayoreo</span>' : ''}</div>
                </td>
                <td class="text-center">
                    <div class="btn-group btn-group-sm" role="group" aria-label="Cantidad">
                        <button type="button" class="btn btn-outline-secondary" data-action="dec" title="Disminuir"><i class="bi bi-dash-lg"></i></button>
                        <span class="btn btn-light border disabled px-1" style="min-width: 34px;">${item.cantidad}</span>
                        <button type="button" class="btn btn-outline-secondary" data-action="inc" title="Aumentar"><i class="bi bi-plus-lg"></i></button>
                    </div>
                </td>
                <td class="text-end small fw-semibold">${fmtQ(subtotalItem)}</td>
                <td class="text-center">
                    <button type="button" class="btn btn-sm btn-outline-danger" data-action="remove" title="Quitar"><i class="bi bi-x-lg"></i></button>
                </td>
            `;
            tr.querySelectorAll('button[data-action]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const action = btn.getAttribute('data-action');
                    if (action === 'inc') addToCart(item.id_variante, 1);
                    if (action === 'dec') setQty(item.id_variante, item.cantidad - 1);
                    if (action === 'remove') removeFromCart(item.id_variante);
                });
            });
            DOM.cartBody.appendChild(tr);
        });

        renderTotals();
    }

    async function cobrar() {
        if (state.cart.length === 0) return;
        const payment = renderTotals();
        if (DOM.btnCharge && DOM.btnCharge.disabled) {
            if (typeof window.showToast === 'function') {
                window.showToast('El total recibido no cubre el monto de la venta.', 'warning');
            }
            return;
        }

        const pagos = [];
        if (payment.cash > 0) {
            pagos.push({ id_metodo_pago: 1, monto_recibido: payment.cash });
        }
        if (payment.transfer > 0) {
            pagos.push({ id_metodo_pago: 2, monto_recibido: payment.transfer });
        }

        const payload = {
            id_sucursal: state.sucursalId,
            id_cliente: null,
            items: state.cart.map(i => ({ id_variante: i.id_variante, cantidad: i.cantidad })),
            pagos: pagos,
        };

        setCharging(true);
        try {
            const venta = await apiPost('/api/ventas', payload);
            showTicket(venta, payment);
            clearCart();
            if (DOM.cashReceived) DOM.cashReceived.value = '';
            if (DOM.transferAmount) DOM.transferAmount.value = '';
            await loadProducts();
            await loadHistory();
        } catch (err) {
            if (typeof window.showToast === 'function') {
                window.showToast(err.message, 'danger');
            }
        } finally {
            setCharging(false);
        }
    }

    function setCharging(charging) {
        if (!DOM.btnCharge) return;
        if (charging) {
            DOM.btnCharge.disabled = true;
            DOM.btnCharge.innerHTML = '<span class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span> Procesando...';
        } else {
            DOM.btnCharge.innerHTML = '<i class="bi bi-cash-coin me-1"></i> Cobrar';
            renderTotals();
        }
    }

    function showTicket(venta, payment) {
        if (!ticketBsModal) return;
        const items = (venta.detalles || []).reduce((acc, d) => acc + Number(d.cantidad || 0), 0);
        if (DOM.ticketId) DOM.ticketId.textContent = `#${venta.id_venta}`;
        if (DOM.ticketFecha) DOM.ticketFecha.textContent = formatDate(venta.fecha_venta);
        if (DOM.ticketItems) DOM.ticketItems.textContent = String(items);
        if (DOM.ticketSubtotal) DOM.ticketSubtotal.textContent = fmtQ(venta.subtotal);
        if (DOM.ticketDiscount) DOM.ticketDiscount.textContent = `- ${fmtQ(venta.descuento_total)}`;
        if (DOM.ticketTotal) DOM.ticketTotal.textContent = fmtQ(venta.total_venta);
        if (DOM.ticketCash) DOM.ticketCash.textContent = fmtQ(payment.cash);
        if (DOM.ticketTransfer) DOM.ticketTransfer.textContent = fmtQ(payment.transfer);
        if (DOM.ticketChange) DOM.ticketChange.textContent = fmtQ(payment.cambio);
        ticketBsModal.show();
    }

    function formatDate(value) {
        if (!value) return '—';
        const d = new Date(value);
        if (isNaN(d.getTime())) return String(value);
        const opts = { year: 'numeric', month: '2-digit', day: '2-digit', hour: '2-digit', minute: '2-digit' };
        return d.toLocaleString('es-GT', opts);
    }

    async function loadHistory() {
        if (!DOM.historyBody) return;
        try {
            const data = await apiGet('/api/ventas?limit=20');
            DOM.historyBody.innerHTML = '';
            const ventas = data.items || [];
            if (DOM.historyEmpty) DOM.historyEmpty.classList.toggle('d-none', ventas.length > 0);
            ventas.forEach(v => {
                const articulos = (v.detalles || []).reduce((acc, d) => acc + Number(d.cantidad || 0), 0);
                const estadoClass = v.estado === 'Completada' ? 'bg-success' : 'bg-secondary';
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td class="fw-semibold small">#${v.id_venta}</td>
                    <td class="small">${formatDate(v.fecha_venta)}</td>
                    <td class="text-end small">${fmtQ(v.subtotal)}</td>
                    <td class="text-end small text-success">- ${fmtQ(v.descuento_total)}</td>
                    <td class="text-end small fw-semibold">${fmtQ(v.total_venta)}</td>
                    <td class="text-center small">${articulos}</td>
                    <td><span class="badge ${estadoClass}">${v.estado}</span></td>
                `;
                DOM.historyBody.appendChild(tr);
            });
        } catch (err) {
            if (err.message === 'Sesión expirada') return;
            if (typeof window.showToast === 'function') {
                window.showToast(`Error al cargar historial: ${err.message}`, 'danger');
            }
        }
    }
})();