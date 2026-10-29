// Curiosidades El Regalito - Compras / Órdenes y Recepción de Mercadería
(function() {
    const MAX_RESULTS = 50;

    const state = {
        proveedores: [],
        catalog: [],
        cart: [],
        ordenes: [],
        currentRecibirOrden: null,
        currentCancelarId: null,
        proveedoresLoaded: false,
        productsLoaded: false,
    };

    let DOM = {};

    function initDOM() {
        DOM = {
            // Tabs
            pillsOrdenesTab: document.getElementById('pills-ordenes-tab'),
            pillsNuevaOrdenTab: document.getElementById('pills-nueva-orden-tab'),
            btnGotoNuevaOrden: document.getElementById('btn-goto-nueva-orden'),

            // Filtros de órdenes
            filtroEstado: document.getElementById('filtro-compras-estado'),
            filtroDesde: document.getElementById('filtro-compras-desde'),
            filtroHasta: document.getElementById('filtro-compras-hasta'),
            btnFiltroCompras: document.getElementById('btn-filtro-compras'),
            btnLimpiarCompras: document.getElementById('btn-limpiar-compras'),

            // Tabla de órdenes
            tablaOrdenes: document.getElementById('tabla-compras-ordenes'),
            tbodyOrdenes: document.getElementById('tbody-compras-ordenes'),
            ordenesEmpty: document.getElementById('compras-ordenes-empty'),

            // Confección de orden
            search: document.getElementById('compras-search'),
            btnFilter: document.getElementById('btn-compras-filter'),
            btnRefresh: document.getElementById('btn-compras-refresh'),
            btnNuevoProdTop: document.getElementById('btn-compras-nuevo-prod-top'),
            btnNuevoProdEmpty: document.getElementById('btn-compras-nuevo-producto'),
            list: document.getElementById('compras-products-list'),
            listEmpty: document.getElementById('compras-products-empty'),
            listInfo: document.getElementById('compras-products-info'),
            proveedor: document.getElementById('compras-proveedor'),
            cartEmpty: document.getElementById('compras-cart-empty'),
            cartTable: document.getElementById('compras-cart-table'),
            cartBody: document.getElementById('compras-cart-body'),
            totalEstimado: document.getElementById('compras-total'),
            btnEmitir: document.getElementById('btn-compras-emitir'),
            btnClear: document.getElementById('btn-compras-clear'),

            // Modal Recibir
            modalRecibirEl: document.getElementById('modal-recibir-compra'),
            recibirOrdenId: document.getElementById('recibir-orden-id'),
            recibirProveedorNombre: document.getElementById('recibir-proveedor-nombre'),
            recibirFechaEmision: document.getElementById('recibir-fecha-emision'),
            recibirFactura: document.getElementById('recibir-factura'),
            recibirFlete: document.getElementById('recibir-flete'),
            recibirCargadores: document.getElementById('recibir-cargadores'),
            tbodyRecibirDetalles: document.getElementById('tbody-recibir-detalles'),
            recibirSubtotalTxt: document.getElementById('recibir-subtotal-txt'),
            recibirGastosTxt: document.getElementById('recibir-gastos-txt'),
            recibirTotalTxt: document.getElementById('recibir-total-txt'),
            btnConfirmarRecibir: document.getElementById('btn-confirmar-recibir'),

            // Modal Cancelar
            modalCancelarEl: document.getElementById('modal-cancelar-compra'),
            cancelarOrdenId: document.getElementById('cancelar-orden-id'),
            cancelarOrdenMotivo: document.getElementById('cancelar-orden-motivo'),
            btnConfirmarCancelar: document.getElementById('btn-confirmar-cancelar'),

            // Modal Ver
            modalVerEl: document.getElementById('modal-ver-orden'),
            verOrdenId: document.getElementById('ver-orden-id'),
            verFecha: document.getElementById('ver-fecha'),
            verProveedor: document.getElementById('ver-proveedor'),
            verEmisor: document.getElementById('ver-emisor'),
            verEstado: document.getElementById('ver-estado'),
            tbodyVerDetalles: document.getElementById('tbody-ver-detalles'),
            verTotalEstimado: document.getElementById('ver-total-estimado'),
        };
    }

    let modalRecibirInst = null;
    let modalCancelarInst = null;
    let modalVerInst = null;

    document.addEventListener('DOMContentLoaded', () => {
        initDOM();
        setupEvents();
    });

    function openProductModalFromCompras() {
        // Callback para cuando se guarda el nuevo producto
        window.onProductCreatedSuccess = async (createdProd) => {
            // 1. Recargar el catálogo local de compras para incorporar el nuevo producto
            await loadProducts();

            // 2. Localizar la variante del producto recién creado
            let varianteId = null;
            if (createdProd && Array.isArray(createdProd.variantes) && createdProd.variantes.length > 0) {
                varianteId = createdProd.variantes[0].id_variante;
            } else if (createdProd && createdProd.id_producto) {
                const found = state.catalog.find(p => p.id_producto === createdProd.id_producto);
                if (found) varianteId = found.id_variante;
            }

            // 3. Añadir automáticamente el nuevo artículo al carrito de compras conservando los existentes
            if (varianteId) {
                addToCart(varianteId);
                if (typeof window.showToast === 'function') {
                    window.showToast('Producto creado y agregado a la lista de compra actual.', 'success');
                }
            }

            // 4. Limpiar filtro de búsqueda y refrescar lista
            if (DOM.search) {
                DOM.search.value = '';
            }
            renderList();
        };

        // Reutilizar el formulario y modal exacto del módulo de Catálogo / Inventario
        if (typeof window.openCreateProductModal === 'function') {
            window.openCreateProductModal();
        } else if (typeof openCreateProductModal === 'function') {
            openCreateProductModal();
        }
    }
    window.openProductModalFromCompras = openProductModalFromCompras;

    function setupEvents() {
        if (!DOM.pillsOrdenesTab) initDOM();

        if (DOM.btnFiltroCompras) DOM.btnFiltroCompras.addEventListener('click', loadOrdenes);
        if (DOM.btnLimpiarCompras) DOM.btnLimpiarCompras.addEventListener('click', () => {
            if (DOM.filtroEstado) DOM.filtroEstado.value = '';
            if (DOM.filtroDesde) DOM.filtroDesde.value = '';
            if (DOM.filtroHasta) DOM.filtroHasta.value = '';
            loadOrdenes();
        });
        if (DOM.btnGotoNuevaOrden) DOM.btnGotoNuevaOrden.addEventListener('click', () => {
            if (DOM.pillsNuevaOrdenTab) {
                const tab = bootstrap.Tab.getOrCreateInstance(DOM.pillsNuevaOrdenTab);
                tab.show();
            }
        });

        if (DOM.btnNuevoProdTop) DOM.btnNuevoProdTop.addEventListener('click', openProductModalFromCompras);
        if (DOM.btnNuevoProdEmpty) DOM.btnNuevoProdEmpty.addEventListener('click', openProductModalFromCompras);

        if (DOM.list) {
            DOM.list.addEventListener('scroll', hideComprasImageZoom, { passive: true });
        }
        window.addEventListener('scroll', hideComprasImageZoom, true);
        window.addEventListener('resize', hideComprasImageZoom);
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') hideComprasImageZoom();
        });

        if (DOM.btnFilter) DOM.btnFilter.addEventListener('click', renderList);
        if (DOM.search) DOM.search.addEventListener('input', renderList);
        if (DOM.btnRefresh) DOM.btnRefresh.addEventListener('click', () => {
            state.proveedoresLoaded = false;
            state.productsLoaded = false;
            loadProveedores();
            loadProducts();
            loadOrdenes();
        });
        if (DOM.btnClear) DOM.btnClear.addEventListener('click', clearCart);
        if (DOM.btnEmitir) DOM.btnEmitir.addEventListener('click', emitirOrden);

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
                    const row = input.closest('tr');
                    const preview = row ? row.querySelector('.stock-nuevo') : null;
                    if (preview) preview.textContent = item.stock + item.cantidad;
                } else if (field === 'costo') {
                    const val = parseFloat(input.value);
                    item.costo_unitario = (isNaN(val) || val < 0) ? 0 : val;
                }
                renderTotals();
            });

            DOM.cartBody.addEventListener('click', (e) => {
                const btnRemove = e.target.closest('[data-remove]');
                if (btnRemove) {
                    removeFromCart(Number(btnRemove.dataset.remove));
                    return;
                }
                const btnMinus = e.target.closest('.btn-cant-minus');
                if (btnMinus) {
                    const id = Number(btnMinus.dataset.id);
                    const item = findCart(id);
                    if (item && item.cantidad > 1) {
                        item.cantidad -= 1;
                        renderCart();
                    }
                    return;
                }
                const btnPlus = e.target.closest('.btn-cant-plus');
                if (btnPlus) {
                    const id = Number(btnPlus.dataset.id);
                    const item = findCart(id);
                    if (item) {
                        item.cantidad += 1;
                        renderCart();
                    }
                    return;
                }
            });
        }

        // Modal Recibir inputs
        if (DOM.recibirFlete) DOM.recibirFlete.addEventListener('input', calcularTotalesRecibir);
        if (DOM.recibirCargadores) DOM.recibirCargadores.addEventListener('input', calcularTotalesRecibir);
        if (DOM.btnConfirmarRecibir) DOM.btnConfirmarRecibir.addEventListener('click', confirmarRecibir);
        if (DOM.btnConfirmarCancelar) DOM.btnConfirmarCancelar.addEventListener('click', confirmarCancelar);
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

    function canEmitir() {
        const isAdmin = window.isAdmin ? window.isAdmin() : false;
        const perms = window.getUserPermissions ? window.getUserPermissions() : [];
        return isAdmin || perms.includes('COMPRA_EMITIR_ORDEN');
    }

    function canRecibir() {
        const isAdmin = window.isAdmin ? window.isAdmin() : false;
        const perms = window.getUserPermissions ? window.getUserPermissions() : [];
        return isAdmin || perms.includes('INV_INGRESAR_MERCADERIA');
    }

    window.showComprasModule = async function() {
        initDOM();
        applyModuleRBAC();
        if (!state.proveedoresLoaded) await loadProveedores();
        if (!state.productsLoaded) await loadProducts();
        await loadOrdenes();
        renderList();
        renderCart();
    };

    function applyModuleRBAC() {
        const userCanEmit = canEmitir();
        if (DOM.btnGotoNuevaOrden) DOM.btnGotoNuevaOrden.classList.toggle('d-none', !userCanEmit);
        if (DOM.pillsNuevaOrdenTab) DOM.pillsNuevaOrdenTab.classList.toggle('d-none', !userCanEmit);
    }

    // ==========================================
    // 1. GESTIÓN Y LISTADO DE ÓRDENES
    // ==========================================

    async function loadOrdenes() {
        if (!DOM.tbodyOrdenes) initDOM();
        const params = new URLSearchParams();
        const estado = DOM.filtroEstado ? DOM.filtroEstado.value : '';
        const desde = DOM.filtroDesde ? DOM.filtroDesde.value : '';
        const hasta = DOM.filtroHasta ? DOM.filtroHasta.value : '';

        if (estado) params.append('estado', estado);
        if (desde) params.append('fecha_desde', desde);
        if (hasta) params.append('fecha_hasta', hasta);

        const url = `/api/compras/ordenes${params.toString() ? `?${params.toString()}` : ''}`;
        try {
            const data = await apiGet(url);
            state.ordenes = Array.isArray(data) ? data : [];
            renderOrdenes();
        } catch (err) {
            if (err.message === 'Sesión expirada') return;
            if (typeof window.showToast === 'function') {
                window.showToast(`Error al cargar órdenes de compra: ${err.message}`, 'danger');
            }
        }
    }

    function renderOrdenes() {
        if (!DOM.tbodyOrdenes) initDOM();
        if (!DOM.tbodyOrdenes) return;
        DOM.tbodyOrdenes.innerHTML = '';

        const hasOrders = state.ordenes.length > 0;
        if (DOM.ordenesEmpty) DOM.ordenesEmpty.classList.toggle('d-none', hasOrders);
        if (DOM.tablaOrdenes) DOM.tablaOrdenes.classList.toggle('d-none', !hasOrders);

        const userCanEmit = canEmitir();
        const userCanReceive = canRecibir();

        state.ordenes.forEach(o => {
            const tr = document.createElement('tr');

            let badgeEstado = '';
            if (o.estado === 'Recibida') {
                badgeEstado = '<span class="badge bg-success px-2 py-1"><i class="bi bi-check-circle me-1"></i>Ingresada</span>';
            } else if (o.estado === 'Emitida') {
                badgeEstado = '<span class="badge bg-warning text-dark px-2 py-1"><i class="bi bi-clock-history me-1"></i>Pendiente</span>';
            } else if (o.estado === 'Cancelada') {
                badgeEstado = '<span class="badge bg-secondary px-2 py-1"><i class="bi bi-x-circle me-1"></i>Cancelada</span>';
            } else {
                badgeEstado = `<span class="badge bg-light text-dark border px-2 py-1">${o.estado}</span>`;
            }

            let actionsHtml = '';
            if (o.estado === 'Emitida') {
                if (userCanReceive) {
                    actionsHtml += `<button type="button" class="btn btn-sm btn-success me-1 btn-recibir-orden" data-id="${o.id_orden}" title="Recibir Mercadería"><i class="bi bi-box-arrow-in-down me-1"></i>Recibir</button>`;
                }
                if (userCanEmit) {
                    actionsHtml += `<button type="button" class="btn btn-sm btn-outline-danger btn-cancelar-orden" data-id="${o.id_orden}" title="Cancelar Orden"><i class="bi bi-x-circle me-1"></i>Cancelar</button>`;
                }
            } else {
                actionsHtml += `<button type="button" class="btn btn-sm btn-outline-teal btn-ver-orden" data-id="${o.id_orden}" title="Ver Detalles"><i class="bi bi-eye me-1"></i>Detalle</button>`;
            }

            tr.innerHTML = `
                <td class="ps-3 fw-bold text-dark font-monospace">#${o.id_orden}</td>
                <td class="small text-muted">${o.fecha_emision || '—'}</td>
                <td class="fw-semibold text-dark small">${o.nombre_proveedor || `Proveedor ${o.id_proveedor}`}</td>
                <td class="small text-muted">${o.nombre_usuario || `Usuario ${o.id_usuario}`}</td>
                <td class="text-end fw-bold text-dark small">${fmtQ(o.total_estimado)}</td>
                <td class="text-center">${badgeEstado}</td>
                <td class="text-end pe-3 text-nowrap">${actionsHtml}</td>
            `;

            DOM.tbodyOrdenes.appendChild(tr);
        });

        // Event delegation for order actions
        DOM.tbodyOrdenes.querySelectorAll('.btn-recibir-orden').forEach(btn => {
            btn.addEventListener('click', () => window.abrirModalRecibirCompra(Number(btn.dataset.id)));
        });
        DOM.tbodyOrdenes.querySelectorAll('.btn-cancelar-orden').forEach(btn => {
            btn.addEventListener('click', () => window.abrirModalCancelarOrden(Number(btn.dataset.id)));
        });
        DOM.tbodyOrdenes.querySelectorAll('.btn-ver-orden').forEach(btn => {
            btn.addEventListener('click', () => window.abrirModalVerOrden(Number(btn.dataset.id)));
        });
    }

    // ==========================================
    // 2. RECEPCIÓN DE MERCADERÍA (MODAL)
    // ==========================================

    window.abrirModalRecibirCompra = async function(idOrden) {
        initDOM();
        if (!DOM.modalRecibirEl) return;
        try {
            const orden = await apiGet(`/api/compras/ordenes/${idOrden}`);
            state.currentRecibirOrden = orden;

            if (DOM.recibirOrdenId) DOM.recibirOrdenId.textContent = orden.id_orden;
            if (DOM.recibirProveedorNombre) DOM.recibirProveedorNombre.textContent = orden.nombre_proveedor || `Proveedor ${orden.id_proveedor}`;
            if (DOM.recibirFechaEmision) DOM.recibirFechaEmision.textContent = orden.fecha_emision || '—';
            if (DOM.recibirFactura) DOM.recibirFactura.value = '';
            if (DOM.recibirFlete) DOM.recibirFlete.value = '0.00';
            if (DOM.recibirCargadores) DOM.recibirCargadores.value = '0.00';

            renderItemsRecibir(orden.detalles || []);
            calcularTotalesRecibir();

            modalRecibirInst = bootstrap.Modal.getOrCreateInstance(DOM.modalRecibirEl);
            modalRecibirInst.show();
        } catch (err) {
            if (typeof window.showToast === 'function') {
                window.showToast(`No se pudo obtener la orden: ${err.message}`, 'danger');
            }
        }
    };

    function renderItemsRecibir(detalles) {
        if (!DOM.tbodyRecibirDetalles) initDOM();
        if (!DOM.tbodyRecibirDetalles) return;
        DOM.tbodyRecibirDetalles.innerHTML = '';

        detalles.forEach(d => {
            const variantTxt = [d.talla, d.color].filter(Boolean).join(' · ');
            const tr = document.createElement('tr');
            tr.dataset.idVariante = d.id_variante;
            tr.innerHTML = `
                <td>
                    <div class="fw-semibold small text-dark">${d.nombre_producto || `Variante ${d.id_variante}`}</div>
                    <div class="text-muted small">${variantTxt ? `${variantTxt} · ` : ''}${d.codigo_barras || ''}</div>
                </td>
                <td class="text-center font-monospace small">${d.cantidad_pedida}</td>
                <td>
                    <input type="number" class="form-control form-control-sm text-center input-recibir-cant" min="1" step="1" value="${d.cantidad_pedida}">
                </td>
                <td>
                    <input type="number" class="form-control form-control-sm text-end input-recibir-costo" min="0" step="0.01" value="${Number(d.costo_pactado || 0).toFixed(2)}">
                </td>
                <td class="text-end pe-3 fw-bold small text-nowrap subtotal-recibir-line">
                    ${fmtQ(d.cantidad_pedida * d.costo_pactado)}
                </td>
            `;

            const inputCant = tr.querySelector('.input-recibir-cant');
            const inputCosto = tr.querySelector('.input-recibir-costo');
            inputCant.addEventListener('input', calcularTotalesRecibir);
            inputCosto.addEventListener('input', calcularTotalesRecibir);

            DOM.tbodyRecibirDetalles.appendChild(tr);
        });
    }

    function calcularTotalesRecibir() {
        if (!DOM.tbodyRecibirDetalles) initDOM();
        if (!DOM.tbodyRecibirDetalles) return;
        let subtotal = 0;

        DOM.tbodyRecibirDetalles.querySelectorAll('tr').forEach(tr => {
            const inputCant = tr.querySelector('.input-recibir-cant');
            const inputCosto = tr.querySelector('.input-recibir-costo');
            const cant = parseInt(inputCant ? inputCant.value : 0, 10) || 0;
            const costo = parseFloat(inputCosto ? inputCosto.value : 0) || 0;
            const line = round2(cant * costo);
            subtotal += line;
            const cell = tr.querySelector('.subtotal-recibir-line');
            if (cell) cell.textContent = fmtQ(line);
        });

        const flete = parseFloat(DOM.recibirFlete ? DOM.recibirFlete.value : 0) || 0;
        const cargadores = parseFloat(DOM.recibirCargadores ? DOM.recibirCargadores.value : 0) || 0;
        const gastos = round2(flete + cargadores);
        const total = round2(subtotal + gastos);

        if (DOM.recibirSubtotalTxt) DOM.recibirSubtotalTxt.textContent = fmtQ(subtotal);
        if (DOM.recibirGastosTxt) DOM.recibirGastosTxt.textContent = fmtQ(gastos);
        if (DOM.recibirTotalTxt) DOM.recibirTotalTxt.textContent = fmtQ(total);
    }

    async function confirmarRecibir() {
        if (!state.currentRecibirOrden) return;
        const factura = (DOM.recibirFactura ? DOM.recibirFactura.value : '').trim();
        if (!factura) {
            if (typeof window.showToast === 'function') window.showToast('Ingresa el número de factura del proveedor.', 'warning');
            return;
        }

        const detalles = [];
        let valid = true;

        DOM.tbodyRecibirDetalles.querySelectorAll('tr').forEach(tr => {
            const idVariante = Number(tr.dataset.idVariante);
            const inputCant = tr.querySelector('.input-recibir-cant');
            const inputCosto = tr.querySelector('.input-recibir-costo');
            const cant = parseInt(inputCant ? inputCant.value : 0, 10);
            const costo = parseFloat(inputCosto ? inputCosto.value : 0);

            if (isNaN(cant) || cant <= 0) valid = false;
            if (isNaN(costo) || costo < 0) valid = false;

            detalles.push({
                id_variante: idVariante,
                cantidad_recibida: cant,
                costo_unitario: round2(costo),
                id_sucursal: 1,
            });
        });

        if (!valid || detalles.length === 0) {
            if (typeof window.showToast === 'function') window.showToast('Revisa las cantidades y costos ingresados.', 'warning');
            return;
        }

        const flete = parseFloat(DOM.recibirFlete ? DOM.recibirFlete.value : 0) || 0;
        const cargadores = parseFloat(DOM.recibirCargadores ? DOM.recibirCargadores.value : 0) || 0;

        const payload = {
            id_orden: state.currentRecibirOrden.id_orden,
            id_proveedor: state.currentRecibirOrden.id_proveedor,
            numero_factura_proveedor: factura,
            gasto_flete: round2(flete),
            gasto_cargadores: round2(cargadores),
            detalles: detalles,
        };

        if (DOM.btnConfirmarRecibir) DOM.btnConfirmarRecibir.disabled = true;

        try {
            await apiPost('/api/compras/ingreso', payload);
            if (typeof window.showToast === 'function') {
                window.showToast(`Mercadería recibida exitosamente en bodega (factura ${factura})`, 'success');
            }
            if (modalRecibirInst) modalRecibirInst.hide();
            await loadOrdenes();
            state.productsLoaded = false;
            await loadProducts();
        } catch (err) {
            if (typeof window.showToast === 'function') {
                window.showToast(`Error al recibir mercadería: ${err.message}`, 'danger');
            }
        } finally {
            if (DOM.btnConfirmarRecibir) DOM.btnConfirmarRecibir.disabled = false;
        }
    }

    // ==========================================
    // 3. CANCELACIÓN DE ÓRDENES (MODAL)
    // ==========================================

    window.abrirModalCancelarOrden = function(idOrden) {
        initDOM();
        state.currentCancelarId = idOrden;
        if (DOM.cancelarOrdenId) DOM.cancelarOrdenId.textContent = idOrden;
        if (DOM.cancelarOrdenMotivo) DOM.cancelarOrdenMotivo.value = '';
        modalCancelarInst = bootstrap.Modal.getOrCreateInstance(DOM.modalCancelarEl);
        modalCancelarInst.show();
    };

    async function confirmarCancelar() {
        if (!state.currentCancelarId) return;
        const motivo = (DOM.cancelarOrdenMotivo ? DOM.cancelarOrdenMotivo.value : '').trim();

        if (DOM.btnConfirmarCancelar) DOM.btnConfirmarCancelar.disabled = true;
        try {
            await apiPost(`/api/compras/ordenes/${state.currentCancelarId}/cancelar`, { motivo: motivo || null });
            if (typeof window.showToast === 'function') {
                window.showToast(`Orden de compra #${state.currentCancelarId} cancelada exitosamente.`, 'success');
            }
            if (modalCancelarInst) modalCancelarInst.hide();
            await loadOrdenes();
        } catch (err) {
            if (typeof window.showToast === 'function') {
                window.showToast(`Error al cancelar orden: ${err.message}`, 'danger');
            }
        } finally {
            if (DOM.btnConfirmarCancelar) DOM.btnConfirmarCancelar.disabled = false;
        }
    }

    // ==========================================
    // 4. VER DETALLES DE ORDEN (MODAL)
    // ==========================================

    window.abrirModalVerOrden = async function(idOrden) {
        initDOM();
        if (!DOM.modalVerEl) return;
        try {
            const orden = await apiGet(`/api/compras/ordenes/${idOrden}`);
            if (DOM.verOrdenId) DOM.verOrdenId.textContent = orden.id_orden;
            if (DOM.verFecha) DOM.verFecha.textContent = orden.fecha_emision || '—';
            if (DOM.verProveedor) DOM.verProveedor.textContent = orden.nombre_proveedor || `Proveedor ${orden.id_proveedor}`;
            if (DOM.verEmisor) DOM.verEmisor.textContent = orden.nombre_usuario || `Usuario ${orden.id_usuario}`;
            if (DOM.verTotalEstimado) DOM.verTotalEstimado.textContent = fmtQ(orden.total_estimado);

            if (DOM.verEstado) {
                let badge = '';
                if (orden.estado === 'Emitida') badge = '<span class="badge bg-warning text-dark">Emitida</span>';
                else if (orden.estado === 'Recibida') badge = '<span class="badge bg-success">Recibida</span>';
                else if (orden.estado === 'Cancelada') badge = '<span class="badge bg-secondary">Cancelada</span>';
                else badge = `<span class="badge bg-light text-dark">${orden.estado}</span>`;
                DOM.verEstado.innerHTML = badge;
            }

            if (DOM.tbodyVerDetalles) {
                DOM.tbodyVerDetalles.innerHTML = '';
                (orden.detalles || []).forEach(d => {
                    const variantTxt = [d.talla, d.color].filter(Boolean).join(' · ');
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>
                            <div class="fw-semibold small text-dark">${d.nombre_producto || `Variante ${d.id_variante}`}</div>
                            <div class="text-muted small">${variantTxt || '—'}</div>
                        </td>
                        <td class="font-monospace small text-muted">${d.codigo_barras || '—'}</td>
                        <td class="text-center font-monospace small">${d.cantidad_pedida}</td>
                        <td class="text-end small">${fmtQ(d.costo_pactado)}</td>
                        <td class="text-end pe-3 fw-bold small">${fmtQ(d.cantidad_pedida * d.costo_pactado)}</td>
                    `;
                    DOM.tbodyVerDetalles.appendChild(tr);
                });
            }

            modalVerInst = bootstrap.Modal.getOrCreateInstance(DOM.modalVerEl);
            modalVerInst.show();
        } catch (err) {
            if (typeof window.showToast === 'function') {
                window.showToast(`No se pudo cargar la orden: ${err.message}`, 'danger');
            }
        }
    };

    // ==========================================
    // 5. EMISIÓN DE ORDEN (CATÁLOGO + CARRITO)
    // ==========================================

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
        if (!DOM.proveedor) initDOM();
        if (!DOM.proveedor) return;
        const current = DOM.proveedor.value;
        DOM.proveedor.innerHTML = '<option value="">Proveedor General / Sin especificar</option>';
        state.proveedores.forEach(p => {
            const dist = p.distribuidora || '';
            const contacto = p.nombre_contacto || '';
            const nombre = dist || contacto || `Proveedor ${p.id_proveedor}`;
            if (dist.toLowerCase().includes('general')) {
                DOM.proveedor.options[0].value = p.id_proveedor;
                return;
            }
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
                        imagen_url: p.imagen_url || '',
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
        if (!DOM.search) initDOM();
        const term = (DOM.search ? DOM.search.value : '').trim().toLowerCase();
        if (!term) return state.catalog;
        return state.catalog.filter(item =>
            (item.nombre || '').toLowerCase().includes(term) ||
            (item.talla || '').toLowerCase().includes(term) ||
            (item.color || '').toLowerCase().includes(term) ||
            (item.codigo_barras || '').toLowerCase().includes(term)
        );
    }

    /* ----------------------------------------------------------------------
       MINIATURA DEL PRODUCTO CON ZOOM FLOTANTE (CLONADO EXACTO DE INVENTARIO)
       ---------------------------------------------------------------------- */
    function escapeAttribute(value) {
        return String(value)
            .replace(/&/g, '&amp;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#39;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');
    }

    function getProductThumbHtml(item) {
        const imageUrl = item && item.imagen_url ? String(item.imagen_url).trim() : '';
        const safeImageUrl = escapeAttribute(imageUrl);

        if (!imageUrl) {
            return '<span class="inventory-product-thumb inventory-product-thumb--placeholder" aria-hidden="true">📦</span>';
        }

        return `
            <span class="inventory-product-thumb-wrap inventory-product-thumb-wrap--zoomable" data-zoom-src="${safeImageUrl}" tabindex="0" aria-label="Vista previa ampliada de la imagen del producto">
                <img src="${safeImageUrl}" alt="" class="inventory-product-thumb" loading="lazy" onerror="this.parentElement.classList.add('is-placeholder'); this.parentElement.removeAttribute('data-zoom-src'); this.parentElement.removeAttribute('tabindex'); this.parentElement.removeAttribute('aria-label'); this.remove();">
                <span class="inventory-product-thumb-fallback" aria-hidden="true">📦</span>
            </span>`;
    }

    const IMAGE_ZOOM_SIZE = 200;
    const IMAGE_ZOOM_GAP = 12;
    const IMAGE_ZOOM_MARGIN = 8;

    function getComprasImageZoom() {
        return document.getElementById('inventory-image-zoom');
    }

    function positionComprasImageZoom(trigger) {
        const zoom = getComprasImageZoom();
        if (!zoom || !trigger) return;

        const rect = trigger.getBoundingClientRect();
        const width = zoom.offsetWidth || IMAGE_ZOOM_SIZE;
        const height = zoom.offsetHeight || IMAGE_ZOOM_SIZE;
        const maxLeft = window.innerWidth - width - IMAGE_ZOOM_MARGIN;

        let left = rect.right + IMAGE_ZOOM_GAP;
        if (left > maxLeft) {
            left = rect.left - width - IMAGE_ZOOM_GAP;
        }
        left = Math.max(IMAGE_ZOOM_MARGIN, Math.min(left, maxLeft));

        const halfHeight = height / 2;
        let top = rect.top + rect.height / 2;
        top = Math.max(halfHeight + IMAGE_ZOOM_MARGIN, Math.min(top, window.innerHeight - halfHeight - IMAGE_ZOOM_MARGIN));

        zoom.style.left = `${left}px`;
        zoom.style.top = `${top}px`;
    }

    function showComprasImageZoom(trigger) {
        const zoom = getComprasImageZoom();
        const image = document.getElementById('inventory-image-zoom-img');
        const src = trigger && trigger.getAttribute('data-zoom-src');
        if (!zoom || !image || !src) return;

        if (image.getAttribute('src') !== src) {
            image.src = src;
        }
        zoom.classList.add('is-visible');
        zoom.setAttribute('aria-hidden', 'false');
        positionComprasImageZoom(trigger);
    }

    function hideComprasImageZoom() {
        const zoom = getComprasImageZoom();
        if (!zoom) return;
        zoom.classList.remove('is-visible');
        zoom.setAttribute('aria-hidden', 'true');
    }

    function setupComprasImageZoom(trigger) {
        if (!trigger) return;
        trigger.addEventListener('mouseenter', () => showComprasImageZoom(trigger));
        trigger.addEventListener('mouseleave', hideComprasImageZoom);
        trigger.addEventListener('focus', () => showComprasImageZoom(trigger));
        trigger.addEventListener('blur', hideComprasImageZoom);
    }

    function renderList() {
        if (!DOM.list) initDOM();
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

            // Miniatura idéntica a Inventario (con fallback 📦 y zoom flotante)
            const thumb = document.createElement('div');
            thumb.className = 'flex-shrink-0 d-flex align-items-center';
            thumb.innerHTML = getProductThumbHtml(item);

            const info = document.createElement('div');
            info.className = 'flex-grow-1 overflow-hidden';
            info.innerHTML = `
                <div class="fw-semibold text-dark small text-truncate" title="${escapeAttribute(item.nombre)}">${escapeAttribute(item.nombre)}</div>
                <div class="text-muted small text-truncate">
                    ${variant ? `${escapeAttribute(variant)} · ` : ''}<span class="font-monospace">${escapeAttribute(item.codigo_barras || '—')}</span>
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
            btn.title = 'Agregar a la orden';
            btn.addEventListener('click', () => addToCart(item.id_variante));

            row.appendChild(thumb);
            row.appendChild(info);
            row.appendChild(cost);
            row.appendChild(btn);
            DOM.list.appendChild(row);

            const zoomTrigger = thumb.querySelector('.inventory-product-thumb-wrap[data-zoom-src]');
            if (zoomTrigger) setupComprasImageZoom(zoomTrigger);
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
                costo_unitario: Number(item.costo_promedio || 0),
                stock: Number(item.stock || 0),
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
        if (!DOM.cartBody) initDOM();
        if (!DOM.cartBody) return;
        const hasItems = state.cart.length > 0;
        if (DOM.cartEmpty) DOM.cartEmpty.classList.toggle('d-none', hasItems);
        if (DOM.cartTable) DOM.cartTable.classList.toggle('d-none', !hasItems);
        if (DOM.btnEmitir) DOM.btnEmitir.disabled = !hasItems;

        DOM.cartBody.innerHTML = '';
        state.cart.forEach(item => {
            const variant = [item.talla, item.color].filter(Boolean).join(' · ');
            const currentStock = Number(item.stock || 0);
            const newStock = currentStock + Number(item.cantidad || 0);
            const tr = document.createElement('tr');
            tr.className = 'align-middle';
            tr.innerHTML = `
                <td style="overflow: hidden; padding: 6px 3px;">
                    <div class="fw-semibold text-dark small text-truncate" title="${escapeAttribute(item.nombre)}">${escapeAttribute(item.nombre)}</div>
                    <div class="text-muted small text-truncate" style="font-size: 0.72rem;">${variant ? escapeAttribute(variant) : 'Estándar'}</div>
                    <div class="text-secondary small text-nowrap" style="font-size: 0.70rem;">
                        Stk: ${currentStock} &rarr; <span class="fw-bold text-success stock-nuevo">${newStock}</span>
                    </div>
                </td>
                <td class="text-center" style="padding: 6px 2px;">
                    <div class="input-group input-group-sm flex-nowrap" style="min-width: 0;">
                        <span class="input-group-text bg-light text-muted px-1 small" style="font-size: 0.72rem;">Q</span>
                        <input type="number" class="form-control form-control-sm text-end compras-costo font-monospace fw-semibold px-1" data-field="costo" data-id="${item.id_variante}" min="0" step="0.01" value="${item.costo_unitario.toFixed(2)}" autocomplete="off" style="min-width: 0; font-size: 0.78rem;">
                    </div>
                </td>
                <td class="text-center" style="padding: 6px 2px;">
                    <div class="input-group input-group-sm flex-nowrap" style="min-width: 0;">
                        <button class="btn btn-outline-secondary px-1 py-0 btn-cant-minus" data-id="${item.id_variante}" type="button" title="Disminuir" style="width: 20px; font-size: 0.75rem;">-</button>
                        <input type="number" class="form-control form-control-sm text-center compras-cant fw-bold font-monospace px-0" data-field="cant" data-id="${item.id_variante}" min="1" step="1" value="${item.cantidad}" autocomplete="off" style="min-width: 0; width: 24px; font-size: 0.78rem;">
                        <button class="btn btn-outline-secondary px-1 py-0 btn-cant-plus" data-id="${item.id_variante}" type="button" title="Aumentar" style="width: 20px; font-size: 0.75rem;">+</button>
                    </div>
                </td>
                <td class="text-end text-nowrap" style="padding: 6px 2px;">
                    <span class="small fw-bold text-dark font-monospace subtotal-line" style="font-size: 0.78rem;">${fmtQ(round2(item.cantidad * item.costo_unitario))}</span>
                </td>
                <td class="text-center" style="padding: 6px 1px;">
                    <button type="button" class="btn btn-sm btn-outline-danger border-0 p-0 text-muted" data-remove="${item.id_variante}" title="Quitar de la lista">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;

            // Prevenir scroll accidental con rueda de mouse en inputs
            tr.querySelectorAll('input[type="number"]').forEach(inp => {
                inp.addEventListener('wheel', (e) => e.preventDefault(), { passive: false });
            });

            DOM.cartBody.appendChild(tr);
        });

        renderTotals();
    }

    function renderTotals() {
        if (!DOM.totalEstimado) initDOM();
        let total = 0;
        state.cart.forEach(item => { total += round2(item.cantidad * item.costo_unitario); });
        if (DOM.totalEstimado) DOM.totalEstimado.textContent = fmtQ(total);

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

    async function emitirOrden() {
        if (!DOM.proveedor) initDOM();
        if (state.cart.length === 0) {
            if (typeof window.showToast === 'function') window.showToast('Selecciona al menos un producto para ingresar.', 'warning');
            return;
        }

        const proveedorVal = DOM.proveedor ? DOM.proveedor.value : '';
        const proveedorId = proveedorVal ? parseInt(proveedorVal, 10) : null;

        if (DOM.btnEmitir) DOM.btnEmitir.disabled = true;
        try {
            const payload = {
                id_proveedor: proveedorId,
                detalles: state.cart.map(c => ({
                    id_variante: c.id_variante,
                    cantidad_recibida: c.cantidad,
                    costo_unitario: round2(c.costo_unitario),
                    id_sucursal: 1,
                })),
            };

            const orden = await apiPost('/api/compras/ingreso-directo', payload);

            if (typeof window.showToast === 'function') {
                window.showToast(`Mercadería ingresada exitosamente al inventario · Total ${fmtQ(orden.total_estimado)}`, 'success');
            }

            clearCart();
            if (DOM.proveedor) DOM.proveedor.value = '';

            // Cambiar a la pestaña de Historial de Compras
            if (DOM.pillsOrdenesTab) {
                const tab = bootstrap.Tab.getOrCreateInstance(DOM.pillsOrdenesTab);
                tab.show();
            }
            await loadOrdenes();
            state.productsLoaded = false;
            await loadProducts();
        } catch (err) {
            if (typeof window.showToast === 'function') {
                window.showToast(`No se pudo ingresar la mercadería: ${err.message}`, 'danger');
            }
        } finally {
            if (DOM.btnEmitir) DOM.btnEmitir.disabled = false;
        }
    }

})();
