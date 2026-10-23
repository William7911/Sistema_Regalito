// Curiosidades El Regalito - Módulo de Mermas de Inventario
(function() {
    let state = {
        mermas: [],
        motivos: [],
        sucursales: [],
        catalogoVariantes: [],
        motivosLoaded: false,
        sucursalesLoaded: false,
        catalogoLoaded: false,
    };

    let bsModal = null;

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

    document.addEventListener('DOMContentLoaded', () => {
        const modalEl = document.getElementById('mermaModal');
        if (modalEl) {
            bsModal = new bootstrap.Modal(modalEl, { backdrop: 'static', keyboard: false });
        }
        setupEventListeners();
    });

    function setupEventListeners() {
        const btnNueva = document.getElementById('btn-nueva-merma');
        if (btnNueva) {
            btnNueva.addEventListener('click', () => abrirModalNuevaMerma());
        }

        const btnFiltrar = document.getElementById('btn-mermas-filtrar');
        if (btnFiltrar) {
            btnFiltrar.addEventListener('click', () => loadMermas());
        }

        const btnLimpiar = document.getElementById('btn-mermas-limpiar');
        if (btnLimpiar) {
            btnLimpiar.addEventListener('click', () => {
                const fDesde = document.getElementById('mermas-filter-desde');
                const fHasta = document.getElementById('mermas-filter-hasta');
                const fMotivo = document.getElementById('mermas-filter-motivo');
                if (fDesde) fDesde.value = '';
                if (fHasta) fHasta.value = '';
                if (fMotivo) fMotivo.value = '';
                loadMermas();
            });
        }

        const formMerma = document.getElementById('form-merma');
        if (formMerma) {
            formMerma.addEventListener('submit', async (e) => {
                e.preventDefault();
                await guardarMerma();
            });
        }

        const selectSucursal = document.getElementById('merma-input-sucursal');
        if (selectSucursal) {
            selectSucursal.addEventListener('change', () => {
                actualizarOpcionesProductos();
                actualizarCostoEstimado();
            });
        }

        const selectProducto = document.getElementById('merma-input-producto');
        if (selectProducto) {
            selectProducto.addEventListener('change', () => {
                actualizarStockInfo();
                actualizarCostoEstimado();
            });
        }

        const inputCantidad = document.getElementById('merma-input-cantidad');
        if (inputCantidad) {
            inputCantidad.addEventListener('input', () => {
                actualizarCostoEstimado();
            });
        }
    }

    window.showMermasModule = async function() {
        if (!state.motivosLoaded) await loadMotivos();
        if (!state.sucursalesLoaded) await loadSucursales();
        if (!state.catalogoLoaded) await loadCatalogoVariantes();
        await loadMermas();
    };

    async function loadMotivos() {
        try {
            const data = await apiFetch('/api/mermas/motivos');
            state.motivos = Array.isArray(data) ? data : [];
            state.motivosLoaded = true;

            // Llenar select filtro
            const selFilter = document.getElementById('mermas-filter-motivo');
            if (selFilter) {
                selFilter.innerHTML = '<option value="">Todos los motivos</option>';
                state.motivos.forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m.id_motivo;
                    opt.textContent = m.descripcion;
                    selFilter.appendChild(opt);
                });
            }

            // Llenar select modal
            const selModal = document.getElementById('merma-input-motivo');
            if (selModal) {
                selModal.innerHTML = '<option value="">Seleccione un motivo...</option>';
                state.motivos.forEach(m => {
                    const opt = document.createElement('option');
                    opt.value = m.id_motivo;
                    opt.textContent = m.descripcion;
                    selModal.appendChild(opt);
                });
            }
        } catch (err) {
            console.error('Error al cargar motivos de merma:', err);
        }
    }

    async function loadSucursales() {
        try {
            const data = await apiFetch('/api/catalogos/sucursales');
            const items = Array.isArray(data) ? data : (data && data.items ? data.items : []);
            state.sucursales = items.filter(s => s.is_active !== false && s.estado !== 'Inactivo');
            state.sucursalesLoaded = true;

            const selModal = document.getElementById('merma-input-sucursal');
            if (selModal) {
                selModal.innerHTML = '<option value="">Seleccione una sucursal...</option>';
                state.sucursales.forEach(s => {
                    const opt = document.createElement('option');
                    opt.value = s.id_sucursal;
                    opt.textContent = s.nombre;
                    selModal.appendChild(opt);
                });
            }
        } catch (err) {
            console.error('Error al cargar sucursales:', err);
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
                        talla: v.talla || '',
                        color: v.color || '',
                        codigo_barras: v.codigo_barras || '',
                        costo_promedio: Number(v.costo_promedio || 0),
                        inventarios: v.inventarios || [],
                    });
                });
            });
            flat.sort((a, b) => a.nombre_producto.localeCompare(b.nombre_producto));
            state.catalogoVariantes = flat;
            state.catalogoLoaded = true;
        } catch (err) {
            console.error('Error al cargar catálogo de productos:', err);
        }
    }

    function actualizarOpcionesProductos() {
        const selSuc = document.getElementById('merma-input-sucursal');
        const selProd = document.getElementById('merma-input-producto');
        if (!selSuc || !selProd) return;

        const sucId = Number(selSuc.value);
        selProd.innerHTML = '<option value="">Seleccione un producto...</option>';
        if (!sucId) return;

        state.catalogoVariantes.forEach(item => {
            const inv = item.inventarios.find(i => Number(i.id_sucursal) === sucId);
            const stock = inv ? Number(inv.stock_actual) : 0;
            const desc = [item.talla, item.color].filter(Boolean).join(' - ');
            const texto = `${item.nombre_producto}${desc ? ` (${desc})` : ''} — Stock: ${stock}`;
            const opt = document.createElement('option');
            opt.value = item.id_variante;
            opt.textContent = texto;
            opt.dataset.stock = stock;
            opt.dataset.costo = item.costo_promedio;
            selProd.appendChild(opt);
        });
        actualizarStockInfo();
    }

    function actualizarStockInfo() {
        const selProd = document.getElementById('merma-input-producto');
        const infoEl = document.getElementById('merma-stock-info');
        if (!selProd || !infoEl) return;

        const opt = selProd.options[selProd.selectedIndex];
        if (!opt || !opt.value) {
            infoEl.textContent = '';
            return;
        }

        const stock = Number(opt.dataset.stock || 0);
        const costo = Number(opt.dataset.costo || 0);
        if (stock <= 0) {
            infoEl.innerHTML = `<span class="text-danger fw-semibold"><i class="bi bi-exclamation-circle me-1"></i>Sin existencias en esta sucursal (Stock: 0). No se puede registrar merma.</span>`;
        } else {
            infoEl.innerHTML = `<span class="text-success fw-semibold"><i class="bi bi-check-circle me-1"></i>Stock disponible: ${stock} unidades</span> | Costo prom: Q ${costo.toFixed(2)}`;
        }
    }

    function actualizarCostoEstimado() {
        const selProd = document.getElementById('merma-input-producto');
        const inputCant = document.getElementById('merma-input-cantidad');
        const costoEl = document.getElementById('merma-costo-estimado');
        if (!selProd || !inputCant || !costoEl) return;

        const opt = selProd.options[selProd.selectedIndex];
        const costo = opt ? Number(opt.dataset.costo || 0) : 0;
        const cant = Number(inputCant.value || 0);
        const total = (cant > 0 && costo > 0) ? (cant * costo) : 0;
        costoEl.value = `Q ${total.toFixed(2)}`;
    }

    function abrirModalNuevaMerma() {
        const form = document.getElementById('form-merma');
        if (form) form.reset();

        const infoEl = document.getElementById('merma-stock-info');
        if (infoEl) infoEl.textContent = '';

        const costoEl = document.getElementById('merma-costo-estimado');
        if (costoEl) costoEl.value = 'Q 0.00';

        const selSuc = document.getElementById('merma-input-sucursal');
        if (selSuc && state.sucursales.length === 1) {
            selSuc.value = state.sucursales[0].id_sucursal;
            actualizarOpcionesProductos();
        } else if (selSuc && state.sucursales.length > 0) {
            actualizarOpcionesProductos();
        }

        if (bsModal) bsModal.show();
    }

    async function guardarMerma() {
        const selSuc = document.getElementById('merma-input-sucursal');
        const selMotivo = document.getElementById('merma-input-motivo');
        const selProd = document.getElementById('merma-input-producto');
        const inputCant = document.getElementById('merma-input-cantidad');
        const inputObs = document.getElementById('merma-input-observaciones');
        const btnSave = document.getElementById('btn-guardar-merma');

        if (!selSuc.value) {
            if (typeof window.showToast === 'function') window.showToast('Seleccione una sucursal.', 'warning');
            return;
        }
        if (!selMotivo.value) {
            if (typeof window.showToast === 'function') window.showToast('Seleccione el motivo de la merma.', 'warning');
            return;
        }
        if (!selProd.value) {
            if (typeof window.showToast === 'function') window.showToast('Seleccione el producto o variante a mermar.', 'warning');
            return;
        }

        const opt = selProd.options[selProd.selectedIndex];
        const stockActual = Number(opt.dataset.stock || 0);
        const cant = parseInt(inputCant.value, 10);

        if (isNaN(cant) || cant <= 0) {
            if (typeof window.showToast === 'function') window.showToast('Ingrese una cantidad válida mayor a 0.', 'warning');
            return;
        }

        if (cant > stockActual) {
            if (typeof window.showToast === 'function') {
                window.showToast(`Stock insuficiente. Solo hay ${stockActual} unidades disponibles en la sucursal.`, 'danger');
            }
            return;
        }

        const payload = {
            id_sucursal: Number(selSuc.value),
            observaciones: inputObs.value.trim() || null,
            detalles: [
                {
                    id_variante: Number(selProd.value),
                    id_motivo: Number(selMotivo.value),
                    cantidad: cant
                }
            ]
        };

        try {
            if (btnSave) {
                btnSave.disabled = true;
                btnSave.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Registrando...';
            }

            await apiFetch('/api/mermas', {
                method: 'POST',
                body: JSON.stringify(payload)
            });

            if (typeof window.showToast === 'function') {
                window.showToast('Merma registrada exitosamente con descargo de existencias.', 'success');
            }

            if (bsModal) bsModal.hide();

            // Refrescar catálogo local para reflejar nuevo stock
            state.catalogoLoaded = false;
            await loadCatalogoVariantes();

            await loadMermas();
        } catch (err) {
            if (typeof window.showToast === 'function') {
                window.showToast(err.message || 'Error al registrar la merma.', 'danger');
            }
        } finally {
            if (btnSave) {
                btnSave.disabled = false;
                btnSave.innerHTML = '<i class="bi bi-check-lg me-1"></i> Registrar Descargo';
            }
        }
    }

    async function loadMermas() {
        const tbody = document.getElementById('mermas-table-body');
        const emptyState = document.getElementById('mermas-empty');
        const totalInfo = document.getElementById('mermas-total-info');
        if (!tbody) return;

        const fDesde = document.getElementById('mermas-filter-desde');
        const fHasta = document.getElementById('mermas-filter-hasta');
        const fMotivo = document.getElementById('mermas-filter-motivo');

        const params = new URLSearchParams();
        if (fDesde && fDesde.value) params.set('fecha_desde', fDesde.value);
        if (fHasta && fHasta.value) params.set('fecha_hasta', fHasta.value);
        if (fMotivo && fMotivo.value) params.set('id_motivo', fMotivo.value);
        params.set('limit', '100');

        tbody.innerHTML = '<tr><td colspan="9" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Cargando mermas...</td></tr>';
        if (emptyState) emptyState.classList.add('d-none');

        try {
            const data = await apiFetch(`/api/mermas?${params.toString()}`);
            state.mermas = (data && data.items) ? data.items : [];
            const total = (data && typeof data.total === 'number') ? data.total : state.mermas.length;

            renderTable(state.mermas);
            if (totalInfo) totalInfo.textContent = `Total: ${total} merma(s) registrada(s)`;
        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="9" class="text-center py-4 text-danger"><i class="bi bi-exclamation-triangle me-1"></i>${err.message || 'Error al consultar mermas'}</td></tr>`;
            if (totalInfo) totalInfo.textContent = 'Error al cargar';
        }
    }

    function renderTable(items) {
        const tbody = document.getElementById('mermas-table-body');
        const emptyState = document.getElementById('mermas-empty');
        if (!tbody) return;

        if (!items || items.length === 0) {
            tbody.innerHTML = '';
            if (emptyState) emptyState.classList.remove('d-none');
            return;
        }

        if (emptyState) emptyState.classList.add('d-none');

        let html = '';
        items.forEach(m => {
            const fechaStr = m.fecha_merma ? new Date(m.fecha_merma).toLocaleString('es-GT', { dateStyle: 'short', timeStyle: 'short' }) : '—';
            const sucursalStr = m.nombre_sucursal || `Sucursal #${m.id_sucursal}`;
            const usuarioStr = m.nombre_usuario || `Usuario #${m.id_usuario}`;
            const obsStr = m.observaciones ? escapeHtml(m.observaciones) : '<span class="text-muted fst-italic">Sin observaciones</span>';
            const costoTotal = Number(m.costo_total_perdida || 0);

            if (m.detalles && m.detalles.length > 0) {
                m.detalles.forEach((d, idx) => {
                    const motivoStr = d.motivo ? escapeHtml(d.motivo.descripcion) : `Motivo #${d.id_motivo}`;
                    const prodStr = d.nombre_producto ? escapeHtml(d.nombre_producto) : `Variante #${d.id_variante}`;
                    const varInfo = d.variante_info ? `<span class="badge bg-light text-dark border ms-1">${escapeHtml(d.variante_info)}</span>` : '';
                    const costoDet = Number(d.costo_perdida || 0);

                    html += `<tr>
                        <td><span class="badge bg-secondary">#${m.id_merma}</span></td>
                        <td><small class="fw-semibold text-dark">${fechaStr}</small></td>
                        <td>${escapeHtml(sucursalStr)}</td>
                        <td><small class="text-muted"><i class="bi bi-person me-1"></i>${escapeHtml(usuarioStr)}</small></td>
                        <td><strong>${prodStr}</strong>${varInfo}</td>
                        <td><span class="badge bg-danger-subtle text-danger border border-danger-subtle">${motivoStr}</span></td>
                        <td class="text-center fw-bold">${d.cantidad}</td>
                        <td class="text-end fw-semibold text-danger">Q ${costoDet.toFixed(2)}</td>
                        <td><small>${obsStr}</small></td>
                    </tr>`;
                });
            } else {
                html += `<tr>
                    <td><span class="badge bg-secondary">#${m.id_merma}</span></td>
                    <td><small class="fw-semibold text-dark">${fechaStr}</small></td>
                    <td>${escapeHtml(sucursalStr)}</td>
                    <td><small class="text-muted">${escapeHtml(usuarioStr)}</small></td>
                    <td colspan="3" class="text-muted fst-italic">Sin detalles</td>
                    <td class="text-end fw-semibold text-danger">Q ${costoTotal.toFixed(2)}</td>
                    <td><small>${obsStr}</small></td>
                </tr>`;
            }
        });

        tbody.innerHTML = html;
    }

    function escapeHtml(text) {
        if (!text) return '';
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return String(text).replace(/[&<>"']/g, m => map[m]);
    }
})();
