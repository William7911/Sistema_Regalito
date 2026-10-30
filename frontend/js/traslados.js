// Curiosidades El Regalito - Módulo de Traslados entre Sucursales
(function() {
    'use strict';

    let state = {
        traslados: [],
        sucursales: [],
        catalogoVariantes: [],
        selectedForRecibir: null,
        selectedForCancelar: null,
        sucursalesLoaded: false,
        catalogoLoaded: false,
    };

    let modals = {
        nuevo: null,
        recibir: null,
        cancelar: null,
    };

    let domInitialized = false;

    function getAuthHeaders() {
        const token = localStorage.getItem('jwt_token') || '';
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    }

    async function apiFetch(url, options = {}) {
        options.headers = { ...getAuthHeaders(), ...(options.headers || {}) };
        const res = await fetch(url, options);
        if (res.status === 401) {
            if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
            throw new Error('Sesión expirada');
        }
        if (!res.ok) {
            let detail = 'Error en el servidor';
            try {
                const err = await res.json();
                detail = err.detail || detail;
            } catch (_) {}
            throw new Error(detail);
        }
        return res.json();
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function formatDate(dateStr) {
        if (!dateStr) return '—';
        try {
            const d = new Date(dateStr);
            if (isNaN(d.getTime())) return dateStr;
            const pad = (n) => String(n).padStart(2, '0');
            return `${pad(d.getDate())}/${pad(d.getMonth() + 1)}/${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
        } catch (_) {
            return dateStr;
        }
    }

    function initDOM() {
        if (domInitialized) return;

        const elNuevo = document.getElementById('modal-nuevo-traslado');
        if (elNuevo && !modals.nuevo) {
            modals.nuevo = new bootstrap.Modal(elNuevo, { backdrop: 'static', keyboard: false });
        }

        const elRecibir = document.getElementById('modal-recibir-traslado');
        if (elRecibir && !modals.recibir) {
            modals.recibir = new bootstrap.Modal(elRecibir, { backdrop: 'static', keyboard: false });
        }

        const elCancelar = document.getElementById('modal-cancelar-traslado');
        if (elCancelar && !modals.cancelar) {
            modals.cancelar = new bootstrap.Modal(elCancelar, { backdrop: 'static', keyboard: false });
        }

        setupEventListeners();
        domInitialized = true;
    }

    function setupEventListeners() {
        const btnNuevo = document.getElementById('btn-nuevo-traslado');
        if (btnNuevo) {
            btnNuevo.addEventListener('click', () => abrirModalNuevo());
        }

        const btnRefresh = document.getElementById('btn-traslados-refresh');
        if (btnRefresh) {
            btnRefresh.addEventListener('click', () => loadTraslados());
        }

        const btnFiltrar = document.getElementById('btn-traslados-filtrar');
        if (btnFiltrar) {
            btnFiltrar.addEventListener('click', () => loadTraslados());
        }

        const btnLimpiar = document.getElementById('btn-traslados-limpiar');
        if (btnLimpiar) {
            btnLimpiar.addEventListener('click', () => {
                const fDesde = document.getElementById('traslados-filter-desde');
                const fHasta = document.getElementById('traslados-filter-hasta');
                const fEstado = document.getElementById('traslados-filter-estado');
                if (fDesde) fDesde.value = '';
                if (fHasta) fHasta.value = '';
                if (fEstado) fEstado.value = '';
                loadTraslados();
            });
        }

        const selOrigen = document.getElementById('traslado-input-origen');
        if (selOrigen) {
            selOrigen.addEventListener('change', () => {
                actualizarOpcionesProductos();
                actualizarStockDisponible();
            });
        }

        const selProducto = document.getElementById('traslado-input-producto');
        if (selProducto) {
            selProducto.addEventListener('change', () => {
                actualizarStockDisponible();
            });
        }

        const formNuevo = document.getElementById('form-nuevo-traslado');
        if (formNuevo) {
            formNuevo.addEventListener('submit', async (e) => {
                e.preventDefault();
                await guardarTraslado();
            });
        }

        const btnGuardar = document.getElementById('btn-guardar-traslado');
        if (btnGuardar) {
            btnGuardar.addEventListener('click', async () => {
                await guardarTraslado();
            });
        }

        const btnConfirmarRecibir = document.getElementById('btn-confirmar-recibir-traslado');
        if (btnConfirmarRecibir) {
            btnConfirmarRecibir.addEventListener('click', async () => {
                await confirmarRecibir();
            });
        }

        const btnConfirmarCancelar = document.getElementById('btn-confirmar-cancelar-traslado');
        if (btnConfirmarCancelar) {
            btnConfirmarCancelar.addEventListener('click', async () => {
                await confirmarCancelar();
            });
        }
    }

    document.addEventListener('DOMContentLoaded', () => {
        initDOM();
    });

    window.showTrasladosModule = async function() {
        initDOM();
        await loadSucursales();
        await loadCatalogoVariantes();
        await loadTraslados();
    };

    async function loadSucursales() {
        try {
            const data = await apiFetch('/api/catalogos/sucursales');
            const items = Array.isArray(data) ? data : (data && data.items ? data.items : []);
            state.sucursales = items.filter(s => s.is_active !== false && s.estado !== 'Inactivo');
            state.sucursalesLoaded = true;

            poblarSelectsSucursales();
        } catch (err) {
            console.error('Error al cargar sucursales:', err);
        }
    }

    function poblarSelectsSucursales() {
        const selOrigen = document.getElementById('traslado-input-origen');
        const selDestino = document.getElementById('traslado-input-destino');

        if (selOrigen) {
            selOrigen.innerHTML = '<option value="">Seleccionar origen...</option>';
            state.sucursales.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.id_sucursal;
                opt.textContent = s.nombre;
                selOrigen.appendChild(opt);
            });
        }

        if (selDestino) {
            selDestino.innerHTML = '<option value="">Seleccionar destino...</option>';
            state.sucursales.forEach(s => {
                const opt = document.createElement('option');
                opt.value = s.id_sucursal;
                opt.textContent = s.nombre;
                selDestino.appendChild(opt);
            });
        }
    }

    async function loadCatalogoVariantes() {
        try {
            const data = await apiFetch('/api/productos?limit=1000&is_active=true');
            const flat = [];
            (data.items || []).forEach(p => {
                (p.variantes || []).forEach(v => {
                    flat.push({
                        id_variante: v.id_variante,
                        id_producto: p.id_producto,
                        nombre_producto: p.nombre,
                        sku: v.sku || v.codigo_barras || '',
                        talla: v.talla || '',
                        color: v.color || '',
                        inventarios: v.inventarios || [],
                    });
                });
            });
            flat.sort((a, b) => a.nombre_producto.localeCompare(b.nombre_producto));
            state.catalogoVariantes = flat;
            state.catalogoLoaded = true;
        } catch (err) {
            console.error('Error al cargar variantes de productos:', err);
        }
    }

    function actualizarOpcionesProductos() {
        const selOrigen = document.getElementById('traslado-input-origen');
        const selProd = document.getElementById('traslado-input-producto');
        if (!selOrigen || !selProd) return;

        const origenId = Number(selOrigen.value);
        selProd.innerHTML = '<option value="">Seleccionar producto...</option>';
        if (!origenId) return;

        state.catalogoVariantes.forEach(item => {
            const inv = item.inventarios.find(i => Number(i.id_sucursal) === origenId);
            const stock = inv ? Number(inv.stock_actual) : 0;
            const desc = [item.talla, item.color].filter(Boolean).join(' - ');
            const texto = `${item.nombre_producto}${desc ? ` (${desc})` : ''} — Stock disp.: ${stock}`;
            const opt = document.createElement('option');
            opt.value = item.id_variante;
            opt.textContent = texto;
            opt.dataset.stock = stock;
            selProd.appendChild(opt);
        });
    }

    function actualizarStockDisponible() {
        const selOrigen = document.getElementById('traslado-input-origen');
        const selProd = document.getElementById('traslado-input-producto');
        const badge = document.getElementById('traslado-stock-disponible-badge');
        const inputCant = document.getElementById('traslado-input-cantidad');

        if (!badge) return;

        const origenId = Number(selOrigen ? selOrigen.value : 0);
        const varianteId = Number(selProd ? selProd.value : 0);

        if (!origenId || !varianteId) {
            badge.textContent = 'Stock en origen: —';
            badge.className = 'badge bg-light text-muted border';
            if (inputCant) inputCant.removeAttribute('max');
            return;
        }

        const item = state.catalogoVariantes.find(v => v.id_variante === varianteId);
        const inv = item ? item.inventarios.find(i => Number(i.id_sucursal) === origenId) : null;
        const stock = inv ? Number(inv.stock_actual) : 0;

        badge.textContent = `Stock disponible: ${stock} unidades`;
        if (stock > 0) {
            badge.className = 'badge bg-success-subtle text-success border border-success-subtle';
        } else {
            badge.className = 'badge bg-danger-subtle text-danger border border-danger-subtle';
        }

        if (inputCant) {
            inputCant.max = stock > 0 ? stock : 1;
        }
    }

    async function loadTraslados() {
        try {
            const params = new URLSearchParams();
            const fDesde = document.getElementById('traslados-filter-desde');
            const fHasta = document.getElementById('traslados-filter-hasta');
            const fEstado = document.getElementById('traslados-filter-estado');

            if (fDesde && fDesde.value) params.append('fecha_desde', fDesde.value);
            if (fHasta && fHasta.value) params.append('fecha_hasta', fHasta.value);
            if (fEstado && fEstado.value) params.append('estado', fEstado.value);

            const queryString = params.toString() ? `?${params.toString()}` : '';
            const data = await apiFetch(`/api/traslados${queryString}`);
            state.traslados = Array.isArray(data) ? data : [];
            renderTraslados();
        } catch (err) {
            console.error('Error al cargar traslados:', err);
            if (typeof window.showToast === 'function') {
                window.showToast(err.message || 'Error al cargar lista de traslados.', 'danger');
            }
        }
    }

    function renderTraslados() {
        const tbody = document.getElementById('traslados-table-body');
        const emptyEl = document.getElementById('traslados-empty');
        const totalInfo = document.getElementById('traslados-total-info');

        if (!tbody) return;

        tbody.innerHTML = '';

        if (!state.traslados || state.traslados.length === 0) {
            if (emptyEl) emptyEl.classList.remove('d-none');
            if (totalInfo) totalInfo.textContent = 'Total: 0 traslados';
            return;
        }

        if (emptyEl) emptyEl.classList.add('d-none');
        if (totalInfo) totalInfo.textContent = `Total: ${state.traslados.length} traslados`;

        state.traslados.forEach(t => {
            const tr = document.createElement('tr');

            let estadoBadge = '';
            if (t.estado === 'En tránsito') {
                estadoBadge = '<span class="badge bg-warning text-dark"><i class="bi bi-truck me-1"></i>En tránsito</span>';
            } else if (t.estado === 'Recibido') {
                estadoBadge = '<span class="badge bg-success"><i class="bi bi-check-circle me-1"></i>Recibido</span>';
            } else if (t.estado === 'Cancelado') {
                estadoBadge = '<span class="badge bg-secondary"><i class="bi bi-x-circle me-1"></i>Cancelado</span>';
            } else {
                estadoBadge = `<span class="badge bg-light text-dark border">${escapeHtml(t.estado)}</span>`;
            }

            const origen = t.nombre_origen || (state.sucursales.find(s => s.id_sucursal === t.id_sucursal_origen) || {}).nombre || `Sucursal #${t.id_sucursal_origen}`;
            const destino = t.nombre_destino || (state.sucursales.find(s => s.id_sucursal === t.id_sucursal_destino) || {}).nombre || `Sucursal #${t.id_sucursal_destino}`;
            const producto = t.nombre_producto || (state.catalogoVariantes.find(v => v.id_variante === t.id_variante) || {}).nombre_producto || `Producto #${t.id_variante}`;
            const sku = t.codigo_barras || t.variante_info || '';
            const detalleProd = sku ? `${escapeHtml(producto)} <span class="badge bg-light text-muted border">${escapeHtml(sku)}</span>` : escapeHtml(producto);
            const usuarioEnvia = t.nombre_usuario_envia || '—';
            const usuarioRecibe = t.nombre_usuario_recibe || '';

            let accionesHtml = '';
            if (t.estado === 'En tránsito') {
                accionesHtml = `
                    <div class="btn-group btn-group-sm">
                        <button type="button" class="btn btn-outline-success btn-recibir" data-id="${t.id_traslado}" title="Recibir en destino">
                            <i class="bi bi-box-arrow-in-down me-1"></i>Recibir
                        </button>
                        <button type="button" class="btn btn-outline-danger btn-cancelar" data-id="${t.id_traslado}" title="Cancelar y devolver stock">
                            <i class="bi bi-x-circle me-1"></i>Cancelar
                        </button>
                    </div>
                `;
            } else if (t.estado === 'Recibido') {
                accionesHtml = `
                    <span class="small text-success">
                        <i class="bi bi-check2-all me-1"></i>Recibido ${usuarioRecibe ? 'por ' + escapeHtml(usuarioRecibe) : ''}
                    </span>
                `;
            } else if (t.estado === 'Cancelado') {
                accionesHtml = `
                    <span class="small text-muted" title="${escapeHtml(t.observaciones || '')}">
                        <i class="bi bi-slash-circle me-1"></i>Cancelado
                    </span>
                `;
            }

            tr.innerHTML = `
                <td class="fw-semibold">#${t.id_traslado}</td>
                <td class="small text-muted">${formatDate(t.fecha_traslado)}</td>
                <td><span class="badge bg-primary-subtle text-primary border">${escapeHtml(origen)}</span></td>
                <td><span class="badge bg-info-subtle text-info-emphasis border">${escapeHtml(destino)}</span></td>
                <td>${detalleProd}</td>
                <td class="text-center fw-bold fs-6">${t.cantidad}</td>
                <td class="small text-muted">${escapeHtml(usuarioEnvia)}</td>
                <td class="text-center">${estadoBadge}</td>
                <td class="text-end pe-3">${accionesHtml}</td>
            `;

            tbody.appendChild(tr);
        });

        // Conectar botones dinámicos
        tbody.querySelectorAll('.btn-recibir').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = Number(btn.dataset.id);
                abrirModalRecibir(id);
            });
        });

        tbody.querySelectorAll('.btn-cancelar').forEach(btn => {
            btn.addEventListener('click', () => {
                const id = Number(btn.dataset.id);
                abrirModalCancelar(id);
            });
        });
    }

    async function abrirModalNuevo() {
        initDOM();
        const alertError = document.getElementById('traslado-error-alert');
        if (alertError) alertError.classList.add('d-none');

        const form = document.getElementById('form-nuevo-traslado');
        if (form) form.reset();

        poblarSelectsSucursales();
        actualizarOpcionesProductos();
        actualizarStockDisponible();

        // Refrescar inventario del catalogo para stock exacto
        await loadCatalogoVariantes();
        actualizarOpcionesProductos();
        actualizarStockDisponible();

        if (modals.nuevo) modals.nuevo.show();
    }

    async function guardarTraslado() {
        const alertError = document.getElementById('traslado-error-alert');
        if (alertError) alertError.classList.add('d-none');

        const selOrigen = document.getElementById('traslado-input-origen');
        const selDestino = document.getElementById('traslado-input-destino');
        const selProd = document.getElementById('traslado-input-producto');
        const inputCant = document.getElementById('traslado-input-cantidad');
        const txtObs = document.getElementById('traslado-input-observaciones');
        const btnGuardar = document.getElementById('btn-guardar-traslado');

        const origenId = Number(selOrigen ? selOrigen.value : 0);
        const destinoId = Number(selDestino ? selDestino.value : 0);
        const varianteId = Number(selProd ? selProd.value : 0);
        const cantidad = Number(inputCant ? inputCant.value : 0);
        const observaciones = txtObs ? txtObs.value.trim() : null;

        function showError(msg) {
            if (alertError) {
                alertError.textContent = msg;
                alertError.classList.remove('d-none');
            }
            if (typeof window.showToast === 'function') {
                window.showToast(msg, 'warning');
            }
        }

        if (!origenId) return showError('Seleccione la sucursal de origen.');
        if (!destinoId) return showError('Seleccione la sucursal de destino.');
        if (origenId === destinoId) return showError('La sucursal destino debe ser diferente a la sucursal origen.');
        if (!varianteId) return showError('Seleccione el producto o variante a trasladar.');
        if (!cantidad || cantidad <= 0) return showError('La cantidad debe ser un número entero mayor a 0.');

        // Validar stock disponible
        const item = state.catalogoVariantes.find(v => v.id_variante === varianteId);
        const inv = item ? item.inventarios.find(i => Number(i.id_sucursal) === origenId) : null;
        const stockActual = inv ? Number(inv.stock_actual) : 0;

        if (cantidad > stockActual) {
            return showError(`Stock insuficiente en origen. Solo hay ${stockActual} unidades disponibles.`);
        }

        try {
            if (btnGuardar) {
                btnGuardar.disabled = true;
                btnGuardar.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Despachando...';
            }

            const payload = {
                id_sucursal_origen: origenId,
                id_sucursal_destino: destinoId,
                id_variante: varianteId,
                cantidad: cantidad,
                observaciones: observaciones || null
            };

            await apiFetch('/api/traslados', {
                method: 'POST',
                body: JSON.stringify(payload)
            });

            if (modals.nuevo) modals.nuevo.hide();

            if (typeof window.showToast === 'function') {
                window.showToast('Traslado despachado exitosamente. Stock descontado en origen.', 'success');
            }

            await loadCatalogoVariantes();
            await loadTraslados();
        } catch (err) {
            showError(err.message || 'Error al despachar el traslado.');
        } finally {
            if (btnGuardar) {
                btnGuardar.disabled = false;
                btnGuardar.innerHTML = '<i class="bi bi-send me-1"></i> Despachar y Descontar Stock';
            }
        }
    }

    function abrirModalRecibir(id) {
        initDOM();
        const traslado = state.traslados.find(t => t.id_traslado === id);
        if (!traslado) return;

        state.selectedForRecibir = traslado;

        const lblId = document.getElementById('recibir-traslado-id');
        const lblProd = document.getElementById('recibir-traslado-producto');
        const lblCant = document.getElementById('recibir-traslado-cantidad');
        const lblRuta = document.getElementById('recibir-traslado-ruta');

        const origen = traslado.nombre_origen || (state.sucursales.find(s => s.id_sucursal === traslado.id_sucursal_origen) || {}).nombre || `Sucursal #${traslado.id_sucursal_origen}`;
        const destino = traslado.nombre_destino || (state.sucursales.find(s => s.id_sucursal === traslado.id_sucursal_destino) || {}).nombre || `Sucursal #${traslado.id_sucursal_destino}`;
        const prodNombre = traslado.nombre_producto || (state.catalogoVariantes.find(v => v.id_variante === traslado.id_variante) || {}).nombre_producto || `Producto #${traslado.id_variante}`;

        if (lblId) lblId.textContent = traslado.id_traslado;
        if (lblProd) lblProd.textContent = prodNombre + (traslado.codigo_barras ? ` (${traslado.codigo_barras})` : '');
        if (lblCant) lblCant.textContent = `${traslado.cantidad} unidades`;
        if (lblRuta) lblRuta.textContent = `${origen} -> ${destino}`;

        if (modals.recibir) modals.recibir.show();
    }

    async function confirmarRecibir() {
        if (!state.selectedForRecibir) return;

        const btnConfirmar = document.getElementById('btn-confirmar-recibir-traslado');
        const id = state.selectedForRecibir.id_traslado;

        try {
            if (btnConfirmar) {
                btnConfirmar.disabled = true;
                btnConfirmar.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Recibiendo...';
            }

            await apiFetch(`/api/traslados/${id}/recibir`, {
                method: 'POST'
            });

            if (modals.recibir) modals.recibir.hide();

            if (typeof window.showToast === 'function') {
                window.showToast('Traslado recibido exitosamente. Stock ingresado al inventario de destino.', 'success');
            }

            state.selectedForRecibir = null;
            await loadCatalogoVariantes();
            await loadTraslados();
        } catch (err) {
            if (typeof window.showToast === 'function') {
                window.showToast(err.message || 'Error al recibir el traslado.', 'danger');
            }
        } finally {
            if (btnConfirmar) {
                btnConfirmar.disabled = false;
                btnConfirmar.innerHTML = '<i class="bi bi-check-lg me-1"></i> Confirmar Recepción';
            }
        }
    }

    function abrirModalCancelar(id) {
        initDOM();
        const traslado = state.traslados.find(t => t.id_traslado === id);
        if (!traslado) return;

        state.selectedForCancelar = traslado;

        const lblId = document.getElementById('cancelar-traslado-id');
        const txtMotivo = document.getElementById('cancelar-traslado-motivo');

        if (lblId) lblId.textContent = traslado.id_traslado;
        if (txtMotivo) txtMotivo.value = '';

        if (modals.cancelar) modals.cancelar.show();
    }

    async function confirmarCancelar() {
        if (!state.selectedForCancelar) return;

        const btnConfirmar = document.getElementById('btn-confirmar-cancelar-traslado');
        const txtMotivo = document.getElementById('cancelar-traslado-motivo');
        const id = state.selectedForCancelar.id_traslado;
        const motivo = txtMotivo ? txtMotivo.value.trim() : '';

        try {
            if (btnConfirmar) {
                btnConfirmar.disabled = true;
                btnConfirmar.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Cancelando...';
            }

            await apiFetch(`/api/traslados/${id}/cancelar`, {
                method: 'POST',
                body: JSON.stringify({ motivo: motivo || null })
            });

            if (modals.cancelar) modals.cancelar.hide();

            if (typeof window.showToast === 'function') {
                window.showToast('Traslado cancelado. Stock devuelto a la sucursal de origen.', 'info');
            }

            state.selectedForCancelar = null;
            await loadCatalogoVariantes();
            await loadTraslados();
        } catch (err) {
            if (typeof window.showToast === 'function') {
                window.showToast(err.message || 'Error al cancelar el traslado.', 'danger');
            }
        } finally {
            if (btnConfirmar) {
                btnConfirmar.disabled = false;
                btnConfirmar.innerHTML = '<i class="bi bi-x-circle me-1"></i> Sí, Cancelar y Devolver Stock';
            }
        }
    }

})();
