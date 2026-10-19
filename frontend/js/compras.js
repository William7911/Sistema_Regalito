// Curiosidades El Regalito - Compras / Ingreso de Mercadería Module Logic
(function() {
    const MAX_RESULTS = 50;

    const state = {
        proveedores: [],
        catalog: [],
        cart: [],
        proveedoresLoaded: false,
        productsLoaded: false,
    };

    const DOM = {
        search: document.getElementById('compras-search'),
        btnFilter: document.getElementById('btn-compras-filter'),
        btnRefresh: document.getElementById('btn-compras-refresh'),
        list: document.getElementById('compras-products-list'),
        listEmpty: document.getElementById('compras-products-empty'),
        listInfo: document.getElementById('compras-products-info'),
        proveedor: document.getElementById('compras-proveedor'),
        cartEmpty: document.getElementById('compras-cart-empty'),
        cartTable: document.getElementById('compras-cart-table'),
        cartBody: document.getElementById('compras-cart-body'),
        factura: document.getElementById('compras-factura'),
        flete: document.getElementById('compras-flete'),
        cargadores: document.getElementById('compras-cargadores'),
        subtotal: document.getElementById('compras-subtotal'),
        gastos: document.getElementById('compras-gastos'),
        total: document.getElementById('compras-total'),
        btnProcess: document.getElementById('btn-compras-process'),
        btnClear: document.getElementById('btn-compras-clear'),
    };

    document.addEventListener('DOMContentLoaded', () => {
        setupEvents();
    });

    function setupEvents() {
        if (DOM.btnFilter) DOM.btnFilter.addEventListener('click', renderList);
        if (DOM.search) DOM.search.addEventListener('input', renderList);
        if (DOM.btnRefresh) DOM.btnRefresh.addEventListener('click', () => {
            state.proveedoresLoaded = false;
            state.productsLoaded = false;
            loadProveedores();
            loadProducts();
        });
        if (DOM.btnClear) DOM.btnClear.addEventListener('click', clearCart);
        if (DOM.btnProcess) DOM.btnProcess.addEventListener('click', processPurchase);
        if (DOM.flete) DOM.flete.addEventListener('input', renderTotals);
        if (DOM.cargadores) DOM.cargadores.addEventListener('input', renderTotals);
        if (DOM.proveedor) DOM.proveedor.addEventListener('change', renderTotals);

        if (DOM.cartBody) {
            DOM.cartBody.addEventListener('input', (e) => {
                const input = e.target;
                const id = Number(input.dataset.id);
                const field = input.dataset.field;
                const item = findCart(id);
                if (!item) return;
                if (field === 'cant') {
                    const val = parseInt(input.value, 10);
                    item.cantidad = (isNaN(val) || val < 1) ? 1 : val;
                } else if (field === 'costo') {
                    const val = parseFloat(input.value);
                    item.costo_unitario = (isNaN(val) || val < 0) ? 0 : val;
                }
                renderTotals();
            });

            DOM.cartBody.addEventListener('click', (e) => {
                const btn = e.target.closest('[data-remove]');
                if (!btn) return;
                removeFromCart(Number(btn.dataset.remove));
            });
        }
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
            try { const d = await res.json(); detail = d.detail || detail; } catch (_) {}
            throw new Error(detail);
        }
        return res.json();
    }

    async function apiPost(url, payload) {
        const res = await fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token()}` },
            body: JSON.stringify(payload),
        });
        if (res.status === 401) {
            if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
            throw new Error('Sesión expirada');
        }
        if (!res.ok) {
            let detail = 'Error en la petición';
            try { const d = await res.json(); detail = d.detail || detail; } catch (_) {}
            throw new Error(detail);
        }
        return res.json();
    }

    function fmtQ(value) {
        return `Q ${(Number(value) || 0).toFixed(2)}`;
    }

    function round2(value) {
        return Math.round((Number(value) || 0) * 100) / 100;
    }

    window.showComprasModule = async function() {
        if (!state.proveedoresLoaded) await loadProveedores();
        if (!state.productsLoaded) await loadProducts();
        renderList();
        renderCart();
    };

    async function loadProveedores() {
        try {
            const data = await apiGet('/api/compras/proveedores');
            state.proveedores = Array.isArray(data) ? data : [];
            state.proveedoresLoaded = true;
            renderProveedores();
        } catch (err) {
            if (err.message === 'Sesión expirada') return;
            if (typeof window.showToast === 'function') window.showToast(`Error al cargar proveedores: ${err.message}`, 'danger');
        }
    }

    function renderProveedores() {
        if (!DOM.proveedor) return;
        const current = DOM.proveedor.value;
        DOM.proveedor.innerHTML = '<option value="">---- Seleccionar proveedor ----</option>';
        state.proveedores.forEach(p => {
            const dist = p.distribuidora || '';
            const contacto = p.nombre_contacto || '';
            const nombre = dist || contacto || `Proveedor ${p.id_proveedor}`;
            const opt = document.createElement('option');
            opt.value = p.id_proveedor;
            opt.textContent = contacto && dist && contacto !== dist ? `${dist} (${contacto})` : nombre;
            DOM.proveedor.appendChild(opt);
        });
        if (current) DOM.proveedor.value = current;
    }

    async function loadProducts() {
        try {
            const data = await apiGet('/api/productos?limit=1000&is_active=true');
            const flat = [];
            (data.items || []).forEach(p => {
                (p.variantes || []).forEach(v => {
                    const inv = (v.inventarios && v.inventarios.length) ? v.inventarios[0] : null;
                    flat.push({
                        id_variante: v.id_variante,
                        id_producto: p.id_producto,
                        nombre: p.nombre,
                        talla: v.talla || '',
                        color: v.color || '',
                        codigo_barras: v.codigo_barras || '',
                        costo_promedio: Number(v.costo_promedio || 0),
                        stock: inv ? Number(inv.stock_actual) : 0,
                    });
                });
            });
            flat.sort((a, b) => (a.nombre || '').localeCompare(b.nombre || ''));
            state.catalog = flat;
            state.productsLoaded = true;
            renderList();
        } catch (err) {
            if (err.message === 'Sesión expirada') return;
            if (typeof window.showToast === 'function') window.showToast(`Error al cargar catálogo: ${err.message}`, 'danger');
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

    function renderList() {
        if (!DOM.list) return;
        const items = filteredCatalog();
        if (DOM.listInfo) {
            DOM.listInfo.textContent = `${items.length} productos${items.length > MAX_RESULTS ? ` · mostrando ${MAX_RESULTS}` : ''}`;
        }
        if (DOM.listEmpty) DOM.listEmpty.classList.toggle('d-none', items.length > 0);
        DOM.list.classList.toggle('d-none', items.length === 0);
        DOM.list.innerHTML = '';

        items.slice(0, MAX_RESULTS).forEach(item => {
            const variant = [item.talla, item.color].filter(Boolean).join(' · ');
            const row = document.createElement('div');
            row.className = 'border rounded-3 p-2 d-flex align-items-center gap-2 bg-white';

            const info = document.createElement('div');
            info.className = 'flex-grow-1 overflow-hidden';
            info.innerHTML = `
                <div class="fw-semibold text-dark small text-truncate" title="${item.nombre}">${item.nombre}</div>
                <div class="text-muted small text-truncate">
                    ${variant ? `${variant} · ` : ''}<span class="font-monospace">${item.codigo_barras || '—'}</span>
                    <span class="badge bg-light text-dark ms-1">Stock: ${item.stock}</span>
                </div>
            `;

            const cost = document.createElement('span');
            cost.className = 'text-muted small text-nowrap me-1';
            cost.title = 'Costo promedio';
            cost.textContent = `Costo ${fmtQ(item.costo_promedio)}`;

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn btn-sm btn-outline-teal text-nowrap';
            btn.innerHTML = '<i class="bi bi-plus-lg"></i>';
            btn.title = 'Agregar a la compra';
            btn.addEventListener('click', () => addToCart(item.id_variante));

            row.appendChild(info);
            row.appendChild(cost);
            row.appendChild(btn);
            DOM.list.appendChild(row);
        });
    }

    function findCart(varianteId) {
        return state.cart.find(c => c.id_variante === varianteId);
    }

    function addToCart(varianteId) {
        const item = state.catalog.find(i => i.id_variante === varianteId);
        if (!item) return;
        const existing = findCart(varianteId);
        if (existing) {
            existing.cantidad += 1;
        } else {
            state.cart.push({
                id_variante: item.id_variante,
                nombre: item.nombre,
                talla: item.talla,
                color: item.color,
                codigo_barras: item.codigo_barras,
                costo_unitario: item.costo_promedio,
                cantidad: 1,
            });
        }
        renderCart();
    }

    function removeFromCart(varianteId) {
        state.cart = state.cart.filter(c => c.id_variante !== varianteId);
        renderCart();
    }

    function clearCart() {
        if (state.cart.length === 0) return;
        state.cart = [];
        renderCart();
    }

    function renderCart() {
        if (!DOM.cartBody) return;
        const hasItems = state.cart.length > 0;
        if (DOM.cartEmpty) DOM.cartEmpty.classList.toggle('d-none', hasItems);
        if (DOM.cartTable) DOM.cartTable.classList.toggle('d-none', !hasItems);
        if (DOM.btnProcess) DOM.btnProcess.disabled = !hasItems;

        DOM.cartBody.innerHTML = '';
        state.cart.forEach(item => {
            const variant = [item.talla, item.color].filter(Boolean).join(' · ');
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>
                    <div class="fw-semibold text-dark small">${item.nombre}</div>
                    <div class="text-muted small">${variant || '—'}</div>
                </td>
                <td>
                    <input type="number" class="form-control form-control-sm text-end compras-costo" data-field="costo" data-id="${item.id_variante}" min="0" step="0.01" value="${item.costo_unitario.toFixed(2)}">
                </td>
                <td class="text-center">
                    <input type="number" class="form-control form-control-sm text-center compras-cant" data-field="cant" data-id="${item.id_variante}" min="1" step="1" value="${item.cantidad}">
                </td>
                <td class="text-end text-nowrap small fw-semibold text-dark subtotal-line">${fmtQ(round2(item.cantidad * item.costo_unitario))}</td>
                <td class="text-end">
                    <button type="button" class="btn btn-sm btn-outline-danger border-0" data-remove="${item.id_variante}" title="Quitar"><i class="bi bi-trash"></i></button>
                </td>
            `;
            DOM.cartBody.appendChild(tr);
        });

        renderTotals();
    }

    function cartTotals() {
        let subtotal = 0;
        state.cart.forEach(item => { subtotal += round2(item.cantidad * item.costo_unitario); });
        const gastos = round2((Number(DOM.flete ? DOM.flete.value : 0) || 0) + (Number(DOM.cargadores ? DOM.cargadores.value : 0) || 0));
        return {
            subtotal: round2(subtotal),
            gastos: gastos,
            total: round2(subtotal + gastos),
        };
    }

    function renderTotals() {
        const totals = cartTotals();
        if (DOM.subtotal) DOM.subtotal.textContent = fmtQ(totals.subtotal);
        if (DOM.gastos) DOM.gastos.textContent = fmtQ(totals.gastos);
        if (DOM.total) DOM.total.textContent = fmtQ(totals.total);

        if (DOM.cartBody) {
            DOM.cartBody.querySelectorAll('.subtotal-line').forEach(cell => {
                const tr = cell.closest('tr');
                const cantInput = tr.querySelector('.compras-cant');
                const costInput = tr.querySelector('.compras-costo');
                const cant = cantInput ? parseInt(cantInput.value, 10) : 0;
                const cost = costInput ? parseFloat(costInput.value) : 0;
                cell.textContent = fmtQ(round2((isNaN(cant) ? 0 : cant) * (isNaN(cost) ? 0 : cost)));
            });
        }
    }

    async function processPurchase() {
        const proveedorId = parseInt(DOM.proveedor ? DOM.proveedor.value : '', 10);
        const factura = (DOM.factura ? DOM.factura.value : '').trim();

        if (!proveedorId) {
            if (typeof window.showToast === 'function') window.showToast('Selecciona un proveedor para la compra.', 'warning');
            return;
        }
        if (!factura) {
            if (typeof window.showToast === 'function') window.showToast('Ingresa el número de factura del proveedor.', 'warning');
            return;
        }
        if (state.cart.length === 0) {
            if (typeof window.showToast === 'function') window.showToast('Agrega al menos un producto a la compra.', 'warning');
            return;
        }

        const perms = window.getUserPermissions ? window.getUserPermissions() : [];
        const isAdminUser = window.isAdmin ? window.isAdmin() : false;
        if (!isAdminUser && !perms.includes('COMPRA_EMITIR_ORDEN')) {
            if (typeof window.showToast === 'function') window.showToast('No tienes el permiso COMPRA_EMITIR_ORDEN para registrar la compra.', 'danger');
            return;
        }
        if (!isAdminUser && !perms.includes('INV_INGRESAR_MERCADERIA')) {
            if (typeof window.showToast === 'function') window.showToast('No tienes el permiso INV_INGRESAR_MERCADERIA para ingresar mercadería.', 'danger');
            return;
        }

        setProcessing(true);
        try {
            const orden = await apiPost('/api/compras/ordenes', {
                id_proveedor: proveedorId,
                detalles: state.cart.map(c => ({
                    id_variante: c.id_variante,
                    cantidad_pedida: c.cantidad,
                    costo_pactado: round2(c.costo_unitario),
                })),
            });

            const ingreso = await apiPost('/api/compras/ingreso', {
                id_proveedor: proveedorId,
                numero_factura_proveedor: factura,
                id_orden: orden.id_orden,
                gasto_flete: round2(Number(DOM.flete ? DOM.flete.value : 0) || 0),
                gasto_cargadores: round2(Number(DOM.cargadores ? DOM.cargadores.value : 0) || 0),
                detalles: state.cart.map(c => ({
                    id_variante: c.id_variante,
                    cantidad_recibida: c.cantidad,
                    costo_unitario: round2(c.costo_unitario),
                })),
            });

            const total = ingreso.total_compra != null ? ingreso.total_compra : cartTotals().total;
            if (typeof window.showToast === 'function') {
                window.showToast(`Ingreso de mercadería registrado (factura ${factura}) · Total ${fmtQ(total)}`, 'success');
            }
            resetPurchase();
        } catch (err) {
            if (typeof window.showToast === 'function') window.showToast(`No se pudo registrar la compra: ${err.message}`, 'danger');
        } finally {
            setProcessing(false);
        }
    }

    function resetPurchase() {
        state.cart = [];
        if (DOM.proveedor) DOM.proveedor.value = '';
        if (DOM.factura) DOM.factura.value = '';
        if (DOM.flete) DOM.flete.value = '0.00';
        if (DOM.cargadores) DOM.cargadores.value = '0.00';
        renderCart();
        renderList();
    }

    function setProcessing(processing) {
        if (!DOM.btnProcess) return;
        DOM.btnProcess.disabled = processing;
        if (processing) {
            DOM.btnProcess.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span> Procesando...';
        } else {
            DOM.btnProcess.innerHTML = '<i class="bi bi-box-arrow-in-down me-1"></i> Procesar Ingreso';
            if (state.cart.length === 0) DOM.btnProcess.disabled = true;
        }
    }

})();