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
    let sortCol = 'id_merma';
    let sortAsc = false;

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

        setupSorting();
        updateSortIcons();

        window.addEventListener('scroll', hideMermasImageZoom, true);
        window.addEventListener('resize', hideMermasImageZoom);
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') hideMermasImageZoom();
        });
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
            const data = await apiFetch('/api/productos?limit=1000');
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
                        imagen_url: p.imagen_url || v.imagen_url || '',
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

        tbody.innerHTML = typeof window.renderSkeletonTable === 'function' ? window.renderSkeletonTable(9, 5) : '<tr><td colspan="9" class="text-center py-4 text-muted">Cargando...</td></tr>';
        if (emptyState) emptyState.classList.add('d-none');

        try {
            const data = await apiFetch(`/api/mermas?${params.toString()}`);
            state.mermas = (data && data.items) ? data.items : [];
            const total = (data && typeof data.total === 'number') ? data.total : state.mermas.length;

            applySortAndRender();
            updateSortIcons();
            if (totalInfo) totalInfo.textContent = `Total: ${total} merma(s) registrada(s)`;
        } catch (err) {
            tbody.innerHTML = `<tr><td colspan="9" class="text-center py-4 text-danger"><i class="bi bi-exclamation-triangle me-1"></i>${err.message || 'Error al consultar mermas'}</td></tr>`;
            if (totalInfo) totalInfo.textContent = 'Error al cargar';
            updateMermasKPIs([]);
        }
    }

    /**
     * updateMermasKPIs(items)
     * ------------------------
     * Calcula métricas agregadas del período:
     * 1. Total Pérdida (Q)
     * 2. Artículos Descartados (total unidades)
     * 3. Motivo más frecuente (con mayor recurrencia e impacto)
     */
    function updateMermasKPIs(items) {
        const kpiTotalPerdida = document.getElementById('merma-kpi-total-perdida');
        const kpiTotalArticulos = document.getElementById('merma-kpi-total-articulos');
        const kpiTotalRegistros = document.getElementById('merma-kpi-total-registros');
        const kpiMotivoFrecuente = document.getElementById('merma-kpi-motivo-frecuente');
        const kpiMotivoDetalle = document.getElementById('merma-kpi-motivo-detalle');

        if (!kpiTotalPerdida || !kpiTotalArticulos || !kpiMotivoFrecuente) return;

        if (!items || items.length === 0) {
            kpiTotalPerdida.textContent = 'Q 0.00';
            kpiTotalArticulos.textContent = '0 unidades';
            if (kpiTotalRegistros) kpiTotalRegistros.textContent = '0 registros de merma';
            kpiMotivoFrecuente.textContent = '—';
            kpiMotivoFrecuente.title = 'Ninguno';
            if (kpiMotivoDetalle) kpiMotivoDetalle.textContent = 'Sin incidencias registradas';
            return;
        }

        let totalPerdida = 0;
        let totalArticulos = 0;
        const motivoContador = {};

        items.forEach(m => {
            const costoMerma = Number(m.costo_total_perdida || 0);
            if (m.detalles && m.detalles.length > 0) {
                m.detalles.forEach(d => {
                    const costo = Number(d.costo_perdida || 0);
                    const cant = Number(d.cantidad || 0);
                    totalPerdida += costo;
                    totalArticulos += cant;

                    const nombreMotivo = (d.motivo && d.motivo.descripcion) ? d.motivo.descripcion.trim() : (d.id_motivo ? `Motivo #${d.id_motivo}` : 'Sin motivo');
                    if (!motivoContador[nombreMotivo]) {
                        motivoContador[nombreMotivo] = { conteo: 0, unidades: 0, costo: 0 };
                    }
                    motivoContador[nombreMotivo].conteo += 1;
                    motivoContador[nombreMotivo].unidades += cant;
                    motivoContador[nombreMotivo].costo += costo;
                });
            } else {
                totalPerdida += costoMerma;
            }
        });

        let topMotivo = '—';
        let topCount = 0;
        let topUnidades = 0;

        for (const [motivo, data] of Object.entries(motivoContador)) {
            if (data.conteo > topCount || (data.conteo === topCount && data.unidades > topUnidades)) {
                topCount = data.conteo;
                topMotivo = motivo;
                topUnidades = data.unidades;
            }
        }

        kpiTotalPerdida.textContent = `Q ${totalPerdida.toLocaleString('es-GT', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        kpiTotalArticulos.textContent = `${totalArticulos.toLocaleString('es-GT')} ${totalArticulos === 1 ? 'unidad' : 'unidades'}`;
        if (kpiTotalRegistros) {
            kpiTotalRegistros.textContent = `${items.length} ${items.length === 1 ? 'registro' : 'registros'} de merma`;
        }
        kpiMotivoFrecuente.textContent = topMotivo;
        kpiMotivoFrecuente.title = topMotivo;
        if (kpiMotivoDetalle) {
            kpiMotivoDetalle.textContent = topCount > 0 ? `${topCount} incidente(s) · ${topUnidades} u.` : 'Sin incidencias';
        }
    }

    /**
     * getMotivoBadge(descripcion)
     * ---------------------------
     * Devuelve Soft Badge con colores semánticos según la gravedad:
     * - Dañado / Roto / Quebrado -> Rojo suave (badge-soft-danger)
     * - Vencimiento / Caducado  -> Ámbar suave (badge-soft-warning)
     * - Manchado / Defecto      -> Morado suave (badge-soft-purple)
     * - Otros                   -> Gris neutro (badge-soft-secondary)
     */
    function getMotivoBadge(descripcion) {
        const desc = descripcion ? escapeHtml(descripcion) : 'Sin motivo';
        const text = (descripcion || '').toLowerCase();

        if (text.includes('dañ') || text.includes('dan') || text.includes('rot') || text.includes('quebr') || text.includes('deterior')) {
            return `<span class="badge-soft-danger" title="Severidad Alta: Daño físico"><i class="bi bi-x-circle me-1"></i>${desc}</span>`;
        }
        if (text.includes('venc') || text.includes('caduc')) {
            return `<span class="badge-soft-warning" title="Vencimiento"><i class="bi bi-clock-history me-1"></i>${desc}</span>`;
        }
        if (text.includes('manch') || text.includes('defecto') || text.includes('fabric') || text.includes('desperf')) {
            return `<span class="badge-soft-purple" title="Defecto o Manchado"><i class="bi bi-shield-exclamation me-1"></i>${desc}</span>`;
        }
        return `<span class="badge-soft-secondary" title="Motivo de salida"><i class="bi bi-tag me-1"></i>${desc}</span>`;
    }

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
            return '<span class="inventory-product-thumb inventory-product-thumb--placeholder" aria-hidden="true"><i class="bi bi-box-seam"></i></span>';
        }

        return `
            <span class="inventory-product-thumb-wrap inventory-product-thumb-wrap--zoomable" data-zoom-src="${safeImageUrl}" tabindex="0" aria-label="Vista previa ampliada de la imagen del producto">
                <img src="${safeImageUrl}" alt="" class="inventory-product-thumb" loading="lazy" onerror="this.parentElement.classList.add('is-placeholder'); this.parentElement.removeAttribute('data-zoom-src'); this.parentElement.removeAttribute('tabindex'); this.parentElement.removeAttribute('aria-label'); this.remove();">
                <span class="inventory-product-thumb-fallback" aria-hidden="true"><i class="bi bi-box-seam"></i></span>
            </span>`;
    }

    /* ----------------------------------------------------------------------
       ZOOM FLOTANTE DE LA MINIATURA DEL PRODUCTO (CLONADO DE INVENTARIO)
       ---------------------------------------------------------------------- */
    const IMAGE_ZOOM_SIZE = 200;
    const IMAGE_ZOOM_GAP = 12;
    const IMAGE_ZOOM_MARGIN = 8;

    function getMermasImageZoom() {
        return document.getElementById('inventory-image-zoom');
    }

    function positionMermasImageZoom(trigger) {
        const zoom = getMermasImageZoom();
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

    function showMermasImageZoom(trigger) {
        const zoom = getMermasImageZoom();
        const image = document.getElementById('inventory-image-zoom-img');
        const src = trigger && trigger.getAttribute('data-zoom-src');
        if (!zoom || !image || !src) return;

        if (image.getAttribute('src') !== src) {
            image.src = src;
        }
        zoom.classList.add('is-visible');
        zoom.setAttribute('aria-hidden', 'false');
        positionMermasImageZoom(trigger);
    }

    function hideMermasImageZoom() {
        const zoom = getMermasImageZoom();
        if (!zoom) return;
        zoom.classList.remove('is-visible');
        zoom.setAttribute('aria-hidden', 'true');
    }

    function setupMermasImageZoom(trigger) {
        if (!trigger) return;
        trigger.addEventListener('mouseenter', () => showMermasImageZoom(trigger));
        trigger.addEventListener('mouseleave', hideMermasImageZoom);
        trigger.addEventListener('focus', () => showMermasImageZoom(trigger));
        trigger.addEventListener('blur', hideMermasImageZoom);
    }

    /**
     * getProductCellHtml(d)
     * ---------------------
     * Renderiza miniatura idéntica a Inventario con zoom flotante
     * y nombre del producto sin badges redundantes de variantes.
     */
    function getProductCellHtml(d) {
        const prodStr = d.nombre_producto ? d.nombre_producto : `Producto #${d.id_producto || d.id_variante}`;
        const catVar = state.catalogoVariantes.find(v => v.id_variante === d.id_variante);
        const imgUrl = (catVar && catVar.imagen_url) || (d.imagen_url || '');

        const itemData = {
            imagen_url: imgUrl,
            producto_nombre: prodStr,
        };

        return `
            <div class="d-flex align-items-center gap-2 inventory-product-cell">
                ${getProductThumbHtml(itemData)}
                <div>
                    <span class="fw-semibold inventory-product-name" title="${escapeAttribute(prodStr)}">${escapeHtml(prodStr)}</span>
                </div>
            </div>
        `;
    }

    function renderTable(items) {
        const tbody = document.getElementById('mermas-table-body');
        const emptyState = document.getElementById('mermas-empty');
        if (!tbody) return;

        hideMermasImageZoom();
        updateMermasKPIs(items);

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
                m.detalles.forEach((d) => {
                    const prodCell = getProductCellHtml(d);
                    const motivoBadge = getMotivoBadge(d.motivo ? d.motivo.descripcion : '');
                    const costoDet = Number(d.costo_perdida || 0);

                    html += `<tr>
                        <td><span class="badge bg-secondary-subtle text-secondary border">#${m.id_merma}</span></td>
                        <td><small class="fw-semibold text-dark">${fechaStr}</small></td>
                        <td>${escapeHtml(sucursalStr)}</td>
                        <td><small class="text-muted"><i class="bi bi-person me-1"></i>${escapeHtml(usuarioStr)}</small></td>
                        <td>${prodCell}</td>
                        <td>${motivoBadge}</td>
                        <td class="text-center fw-bold text-dark">${d.cantidad}</td>
                        <td class="text-end merma-costo-perdida">Q ${costoDet.toFixed(2)}</td>
                        <td><small class="text-muted">${obsStr}</small></td>
                    </tr>`;
                });
            } else {
                html += `<tr>
                    <td><span class="badge bg-secondary-subtle text-secondary border">#${m.id_merma}</span></td>
                    <td><small class="fw-semibold text-dark">${fechaStr}</small></td>
                    <td>${escapeHtml(sucursalStr)}</td>
                    <td><small class="text-muted">${escapeHtml(usuarioStr)}</small></td>
                    <td colspan="3" class="text-muted fst-italic">Sin detalles</td>
                    <td class="text-end merma-costo-perdida">Q ${costoTotal.toFixed(2)}</td>
                    <td><small class="text-muted">${obsStr}</small></td>
                </tr>`;
            }
        });

        tbody.innerHTML = html;
        tbody.querySelectorAll('.inventory-product-thumb-wrap[data-zoom-src]').forEach(wrap => {
            setupMermasImageZoom(wrap);
        });
    }


    /* =======================================================================
       ORDENAMIENTO DE COLUMNAS (SORT) - REPLICADO 1:1 DE INVENTARIO
       ======================================================================= */

    function setupSorting() {
        document.querySelectorAll('#mermas-view th.sortable').forEach(th => {
            th.addEventListener('click', () => {
                const col = th.getAttribute('data-sort');
                if (sortCol === col) {
                    sortAsc = !sortAsc;
                } else {
                    sortCol = col;
                    sortAsc = true;
                }
                updateSortIcons();
                applySortAndRender();
            });
        });
    }

    function updateSortIcons() {
        document.querySelectorAll('#mermas-view th.sortable').forEach(th => {
            const icon = th.querySelector('.sort-icon');
            if (!icon) return;

            const col = th.getAttribute('data-sort');
            if (col === sortCol) {
                // Estado Activo: flecha sólida (↑ o ↓)
                icon.className = `sort-icon bi bi-arrow-${sortAsc ? 'up' : 'down'} text-white ms-1`;
            } else {
                // Íconos inactivos: ⇕ (doble flecha contorno)
                icon.className = 'sort-icon bi bi-arrow-down-up text-white-50 ms-1';
            }
        });
    }

    function getSortValue(item, col) {
        if (!item) return '';

        if (col === 'id_merma') {
            return Number(item.id_merma || 0);
        }
        if (col === 'fecha_merma') {
            return item.fecha_merma ? new Date(item.fecha_merma).getTime() : 0;
        }
        if (col === 'producto_nombre') {
            if (item.detalles && item.detalles.length > 0) {
                return String(item.detalles[0].nombre_producto || '').toLowerCase();
            }
            return '';
        }
        if (col === 'cantidad') {
            if (item.detalles && item.detalles.length > 0) {
                return item.detalles.reduce((acc, d) => acc + (Number(d.cantidad) || 0), 0);
            }
            return 0;
        }
        if (col === 'costo_perdida') {
            if (item.costo_total_perdida != null) {
                return Number(item.costo_total_perdida || 0);
            }
            if (item.detalles && item.detalles.length > 0) {
                return item.detalles.reduce((acc, d) => acc + (Number(d.costo_perdida) || 0), 0);
            }
            return 0;
        }
        return '';
    }

    function applySortAndRender() {
        if (!state.mermas || state.mermas.length === 0) {
            renderTable([]);
            return;
        }

        state.mermas.sort((a, b) => {
            const valA = getSortValue(a, sortCol);
            const valB = getSortValue(b, sortCol);

            if (typeof valA === 'string' && typeof valB === 'string') {
                return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
            }
            return sortAsc ? (valA - valB) : (valB - valA);
        });

        renderTable(state.mermas);
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
