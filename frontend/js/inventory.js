// Curiosidades El Regalito - Inventory Module Logic
(function() {
    let inventoryData = [];
    let filteredData = [];
    let currentPage = 1;
    let pageSize = 10;
    let sortCol = 'id_inventario';
    let sortAsc = true;
    let initialFormData = '';

    const DOM = {
        tableBody: document.getElementById('inventory-table-body'),
        emptyState: document.getElementById('inventory-empty'),
        filterSku: document.getElementById('filter-inv-sku'),
        filterLowStock: document.getElementById('filter-inv-low-stock'),
        btnFilter: document.getElementById('btn-filter-inventory'),
        clearSearch: document.getElementById('btn-clear-inventory-search'),
        pageSize: document.getElementById('inventory-page-size'),
        prevPage: document.getElementById('inventory-prev-page'),
        nextPage: document.getElementById('inventory-next-page'),
        pageInfo: document.getElementById('inventory-page-info'),
        pagination: document.getElementById('inventory-pagination'),
        
        modal: document.getElementById('inventory-modal'),
        form: document.getElementById('inventory-form'),
        inputId: document.getElementById('inv-id'),
        inputProducto: document.getElementById('inv-producto'),
        inputStockActual: document.getElementById('inv-stock-actual'),
        inputMotivo: document.getElementById('inv-motivo'),
        inputCantidad: document.getElementById('inv-cantidad'),
        btnSave: document.getElementById('btn-save-inventory')
    };

    let bsModal = null;
    let confirmBsModal = null;

    document.addEventListener('DOMContentLoaded', () => {
        if (DOM.modal) {
            bsModal = new bootstrap.Modal(DOM.modal);
        }
        const confirmModalEl = document.getElementById('confirm-modal');
        if (confirmModalEl) {
            confirmBsModal = new bootstrap.Modal(confirmModalEl);
        }
        setupEventListeners();
    });

    function setupEventListeners() {
        if (DOM.btnFilter) DOM.btnFilter.addEventListener('click', () => {
            currentPage = 1;
            applyFilters();
        });

        /* ------------------------------------------------------------------
           UX · BOTÓN "X" DEL BUSCADOR DE INVENTARIO
           Dos acciones simultáneas al hacer clic:
             1) Vacía el texto del input.
             2) Re-renderiza la tabla con todos los registros (sin exigir un
                segundo clic en "Filtrar").
           La "X" solo se muestra cuando el input contiene texto.
           ------------------------------------------------------------------ */
        if (DOM.filterSku && DOM.clearSearch) {
            const syncClearButton = () => {
                DOM.clearSearch.classList.toggle('is-visible', DOM.filterSku.value.length > 0);
            };

            DOM.filterSku.addEventListener('input', syncClearButton);

            DOM.clearSearch.addEventListener('click', () => {
                DOM.filterSku.value = '';
                syncClearButton();
                currentPage = 1;
                applyFilters();        // Restaura la tabla al instante.
                DOM.filterSku.focus(); // Mantiene el foco en el buscador.
            });

            syncClearButton();
        }

        /* Ocultar el zoom si la imagen ampliada falla, al desplazarse o al
           redimensionar. Así nunca queda una vista previa flotante huérfana. */
        const zoomImage = document.getElementById('inventory-image-zoom-img');
        if (zoomImage) {
            zoomImage.addEventListener('error', hideInventoryImageZoom);
        }
        window.addEventListener('scroll', hideInventoryImageZoom, true);
        window.addEventListener('resize', hideInventoryImageZoom);
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') hideInventoryImageZoom();
        });

        const btnAlertas = document.getElementById('btn-inventory-alerts');
        if (btnAlertas) {
            btnAlertas.addEventListener('click', async () => {
                const modalEl = document.getElementById('modal-inventario-alertas');
                if (modalEl) {
                    const bsAlertsModal = new bootstrap.Modal(modalEl, { backdrop: 'static' });
                    bsAlertsModal.show();
                    await window.cargarAlertasInventarioModal();
                }
            });
        }
        
        if (DOM.pageSize) DOM.pageSize.addEventListener('change', (e) => {
            pageSize = parseInt(e.target.value);
            currentPage = 1;
            renderTable();
        });
        
        if (DOM.prevPage) DOM.prevPage.addEventListener('click', () => {
            if (currentPage > 1) { currentPage--; renderTable(); }
        });
        
        if (DOM.nextPage) DOM.nextPage.addEventListener('click', () => {
            const maxPage = Math.ceil(filteredData.length / pageSize);
            if (currentPage < maxPage) { currentPage++; renderTable(); }
        });

        // Sorting
        document.querySelectorAll('#inventory-view th.sortable').forEach(th => {
            th.addEventListener('click', () => {
                const col = th.getAttribute('data-sort');
                if (sortCol === col) {
                    sortAsc = !sortAsc;
                } else {
                    sortCol = col;
                    sortAsc = true;
                }
                updateSortIcons();
                applyFilters(); // re-sorts and renders
            });
        });

        // Form Submission
        if (DOM.form) {
            DOM.form.addEventListener('submit', handleFormSubmit);
        }

        // Close Modal Handling (Defensive UX)
        if (DOM.modal) {
            DOM.modal.addEventListener('hide.bs.modal', (e) => {
                if (formHasData() && !window._forceCloseInventoryModal) {
                    e.preventDefault();
                    showConfirmModal('¿Descartar los cambios? Los datos ingresados se perderán.', () => {
                        window._forceCloseInventoryModal = true;
                        bsModal.hide();
                    });
                }
            });

            DOM.modal.addEventListener('hidden.bs.modal', () => {
                window._forceCloseInventoryModal = false;
                DOM.form.reset();
                clearValidation();
            });

            // "data-bs-close-modal" buttons
            DOM.modal.querySelectorAll('[data-bs-close-modal]').forEach(btn => {
                btn.addEventListener('click', () => {
                    if (bsModal) bsModal.hide();
                });
            });
        }

        // Unload Guard
        window.addEventListener('beforeunload', (e) => {
            if (DOM.modal && DOM.modal.classList.contains('show') && formHasData()) {
                e.preventDefault();
                e.returnValue = '';
            }
        });

        // Clear validation on input
        if (DOM.form) {
            DOM.form.querySelectorAll('input, select, textarea').forEach(input => {
                input.addEventListener('input', () => {
                    input.classList.remove('is-invalid');
                });
            });
        }
    }

    function formHasData() {
        if (!DOM.form) return false;
        const currentData = new FormData(DOM.form);
        const currentString = new URLSearchParams(currentData).toString();
        return currentString !== initialFormData;
    }

    function showConfirmModal(message, onConfirm) {
        if (!confirmBsModal) return;
        const msgEl = document.getElementById('confirm-message');
        if (msgEl) msgEl.innerText = message;
        
        const btnOk = document.getElementById('confirm-ok');
        if (btnOk) {
            const newBtnOk = btnOk.cloneNode(true);
            btnOk.parentNode.replaceChild(newBtnOk, btnOk);
            
            newBtnOk.addEventListener('click', () => {
                confirmBsModal.hide();
                onConfirm();
            });
        }
        confirmBsModal.show();
    }

    window.showInventoryModule = async function() {
        await loadInventory();
    };

    async function loadInventory() {
        try {
            const params = new URLSearchParams();
            if (DOM.filterLowStock && DOM.filterLowStock.checked) params.append('low_stock_only', 'true');
            
            if (DOM.tableBody && typeof window.renderSkeletonTable === 'function') {
                DOM.tableBody.innerHTML = window.renderSkeletonTable(8, 6);
            }
            const token = localStorage.getItem('jwt_token');
            const res = await fetch(`/api/inventory/?${params.toString()}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            
            if (!res.ok) {
                if (res.status === 401) {
                    if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
                    return;
                }
                throw new Error('Error al cargar inventario');
            }
            
            inventoryData = await res.json();
            // Rediseño UI/UX: refresca las tarjetas KPI con los datos ya cargados.
            updateInventoryKpis();
            applyFilters();
        } catch (err) {
            if (typeof window.showToast === 'function') {
                window.showToast(err.message, 'danger');
            }
        }
    }

    function applyFilters() {
        let data = [...inventoryData];
        
        // Filter by SKU
        if (DOM.filterSku) {
            const skuTerm = DOM.filterSku.value.trim().toLowerCase();
            if (skuTerm) {
                data = data.filter(item => 
                    (item.producto_nombre && item.producto_nombre.toLowerCase().includes(skuTerm)) ||
                    (item.variante_sku && item.variante_sku.toLowerCase().includes(skuTerm))
                );
            }
        }

        // Sorting
        data.sort((a, b) => {
            let valA = a[sortCol];
            let valB = b[sortCol];
            if (valA == null) valA = '';
            if (valB == null) valB = '';
            
            if (typeof valA === 'string') {
                return sortAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
            }
            return sortAsc ? (valA - valB) : (valB - valA);
        });

        filteredData = data;
        renderTable();
    }

    function updateSortIcons() {
        document.querySelectorAll('#inventory-view th.sortable').forEach(th => {
            const icon = th.querySelector('.sort-icon');
            if (icon) {
                icon.className = 'sort-icon bi bi-arrow-down-up text-muted ms-1';
                if (th.getAttribute('data-sort') === sortCol) {
                    icon.className = `sort-icon bi bi-arrow-${sortAsc ? 'up' : 'down'} ms-1`;
                }
            }
        });
    }

    /* ----------------------------------------------------------------------
       REDISEÑO UI/UX · INSIGNIAS SEMÁNTICAS DE STOCK (SOFT BADGES)
       Solo define la variante visual del stock, sin modificar los datos:
         - danger  : stock igual o por debajo del mínimo (incluye agotados).
         - warning : stock dentro del margen de alerta (hasta 50% sobre el mínimo).
         - ok      : stock holgado, muy por encima del mínimo.
       ---------------------------------------------------------------------- */
    function getStockBadgeMeta(stockActual, stockMinimo) {
        const actual = Number(stockActual) || 0;
        const minimo = Number(stockMinimo) || 0;

        if (actual <= minimo) {
            return {
                className: 'stock-badge--danger',
                label: actual === 0 ? 'Producto agotado' : 'Stock igual o por debajo del mínimo'
            };
        }

        if (actual <= Math.ceil(minimo * 1.5)) {
            return {
                className: 'stock-badge--warning',
                label: 'Stock cerca del mínimo'
            };
        }

        return {
            className: 'stock-badge--ok',
            label: 'Stock holgado'
        };
    }

    /* ----------------------------------------------------------------------
       REDISEÑO UI/UX · MINIATURA DEL PRODUCTO
       Si el registro incluye imagen_url se muestra la foto; en caso contrario
       se usa el placeholder gris con el ícono de caja. No hace peticiones.
       ---------------------------------------------------------------------- */
    /* Escapa valores interpolados en atributos HTML (por ejemplo, la URL de la
       imagen) para no romper el marcado ni permitir inyección de contenido. */
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

    /* ----------------------------------------------------------------------
       ZOOM FLOTANTE DE LA MINIATURA DEL PRODUCTO
       La vista previa se monta fuera de la tabla con position: fixed para que
       el overflow de .table-responsive no la recorte. Se coloca junto a la
       miniatura y no ocupa espacio en la fila, por lo que su altura no cambia.
       ---------------------------------------------------------------------- */
    const IMAGE_ZOOM_SIZE = 200;
    const IMAGE_ZOOM_GAP = 12;
    const IMAGE_ZOOM_MARGIN = 8;

    function getInventoryImageZoom() {
        return document.getElementById('inventory-image-zoom');
    }

    function positionInventoryImageZoom(trigger) {
        const zoom = getInventoryImageZoom();
        if (!zoom || !trigger) return;

        const rect = trigger.getBoundingClientRect();
        const width = zoom.offsetWidth || IMAGE_ZOOM_SIZE;
        const height = zoom.offsetHeight || IMAGE_ZOOM_SIZE;
        const maxLeft = window.innerWidth - width - IMAGE_ZOOM_MARGIN;

        /* Preferencia: a la derecha de la miniatura; si no cabe, a la izquierda. */
        let left = rect.right + IMAGE_ZOOM_GAP;
        if (left > maxLeft) {
            left = rect.left - width - IMAGE_ZOOM_GAP;
        }
        left = Math.max(IMAGE_ZOOM_MARGIN, Math.min(left, maxLeft));

        /* La miniatura queda centrada verticalmente con respecto a la vista previa. */
        const halfHeight = height / 2;
        let top = rect.top + rect.height / 2;
        top = Math.max(halfHeight + IMAGE_ZOOM_MARGIN, Math.min(top, window.innerHeight - halfHeight - IMAGE_ZOOM_MARGIN));

        zoom.style.left = `${left}px`;
        zoom.style.top = `${top}px`;
    }

    function showInventoryImageZoom(trigger) {
        const zoom = getInventoryImageZoom();
        const image = document.getElementById('inventory-image-zoom-img');
        const src = trigger && trigger.getAttribute('data-zoom-src');
        if (!zoom || !image || !src) return;

        if (image.getAttribute('src') !== src) {
            image.src = src;
        }
        zoom.classList.add('is-visible');
        zoom.setAttribute('aria-hidden', 'false');
        positionInventoryImageZoom(trigger);
    }

    function hideInventoryImageZoom() {
        const zoom = getInventoryImageZoom();
        if (!zoom) return;
        zoom.classList.remove('is-visible');
        zoom.setAttribute('aria-hidden', 'true');
    }

    function setupInventoryImageZoom(trigger) {
        if (!trigger) return;
        trigger.addEventListener('mouseenter', () => showInventoryImageZoom(trigger));
        trigger.addEventListener('mouseleave', hideInventoryImageZoom);
        trigger.addEventListener('focus', () => showInventoryImageZoom(trigger));
        trigger.addEventListener('blur', hideInventoryImageZoom);
    }

    /* ----------------------------------------------------------------------
       REDISEÑO UI/UX — TARJETAS DE RESUMEN KPI
       Actualiza el micro-dashboard con los registros ya cargados. No realiza
       consultas nuevas ni altera filtros, ordenamiento o paginación.
       ---------------------------------------------------------------------- */
    function updateInventoryKpis() {
        const uniqueProducts = new Set(
            inventoryData.map(item => item.id_variante || item.variante_sku || item.id_inventario)
        ).size;

        const lowStock = inventoryData.filter(item => {
            const actual = Number(item.stock_actual) || 0;
            const minimo = Number(item.stock_minimo) || 0;
            return actual > 0 && actual <= minimo;
        }).length;

        const outOfStock = inventoryData.filter(item => (Number(item.stock_actual) || 0) <= 0).length;
        const totalUnits = inventoryData.reduce((sum, item) => sum + (Number(item.stock_actual) || 0), 0);

        setKpiValue('kpi-inv-total', uniqueProducts);
        setKpiValue('kpi-inv-low', lowStock);
        setKpiValue('kpi-inv-out', outOfStock);
        setKpiValue('kpi-inv-units', totalUnits);
    }

    function setKpiValue(elementId, value) {
        const el = document.getElementById(elementId);
        if (el) el.textContent = Number(value).toLocaleString('es-GT');
    }

    function renderTable() {
        if (!DOM.tableBody) return;
        hideInventoryImageZoom();
        DOM.tableBody.innerHTML = '';
        
        if (filteredData.length === 0) {
            if (DOM.emptyState) DOM.emptyState.classList.remove('d-none');
            if (DOM.pagination) DOM.pagination.classList.add('d-none');
            return;
        }
        
        if (DOM.emptyState) DOM.emptyState.classList.add('d-none');
        if (DOM.pagination) DOM.pagination.classList.remove('d-none');

        const totalPages = Math.ceil(filteredData.length / pageSize) || 1;
        if (currentPage > totalPages) currentPage = totalPages;
        
        if (DOM.pageInfo) DOM.pageInfo.textContent = `Página ${currentPage} de ${totalPages}`;
        if (DOM.prevPage) DOM.prevPage.disabled = currentPage === 1;
        if (DOM.nextPage) DOM.nextPage.disabled = currentPage === totalPages;

        const start = (currentPage - 1) * pageSize;
        const pageData = filteredData.slice(start, start + pageSize);

        pageData.forEach(item => {
            const tr = document.createElement('tr');

            // Theme global: soft badge unificado con el estado "Activo" de Usuarios.
            const stockMeta = getStockBadgeMeta(item.stock_actual, item.stock_minimo);

            // Rediseño: miniatura del producto, badge semántico y acción fantasma.
            tr.innerHTML = `
                <td>${item.id_inventario}</td>
                <td>
                    <div class="d-flex align-items-center gap-2 inventory-product-cell">
                        ${getProductThumbHtml(item)}
                        <span class="fw-semibold inventory-product-name">${item.producto_nombre || 'N/A'}</span>
                    </div>
                </td>
                <td class="font-monospace">${item.variante_sku || 'N/A'}</td>
                <td>${item.sucursal_nombre || 'N/A'}</td>
                <td>
                    <span class="stock-badge ${stockMeta.className}" title="${stockMeta.label}">${item.stock_actual}</span>
                </td>
                <td>${item.stock_minimo}</td>
                <td class="text-end">
                    <button class="btn btn-sm inventory-action-btn" onclick="window.openInventoryModal(${item.id_inventario})" title="Ajustar stock" aria-label="Ajustar stock">
                        <i class="bi bi-sliders"></i>
                    </button>
                </td>
            `;
            DOM.tableBody.appendChild(tr);
            setupInventoryImageZoom(tr.querySelector('.inventory-product-thumb-wrap[data-zoom-src]'));
        });
    }

    window.openInventoryModal = function(id) {
        const item = inventoryData.find(i => i.id_inventario === id);
        if (!item) return;

        clearValidation();
        if (DOM.inputId) DOM.inputId.value = item.id_inventario;
        if (DOM.inputProducto) DOM.inputProducto.value = `${item.producto_nombre || ''} (${item.variante_sku || ''})`;
        if (DOM.inputStockActual) DOM.inputStockActual.value = item.stock_actual;
        if (DOM.inputMotivo) DOM.inputMotivo.value = '';
        if (DOM.inputCantidad) DOM.inputCantidad.value = '';

        if (DOM.form) {
            initialFormData = new URLSearchParams(new FormData(DOM.form)).toString();
        }
        if (bsModal) bsModal.show();
    };

    function clearValidation() {
        if (!DOM.form) return;
        DOM.form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    }

    async function handleFormSubmit(e) {
        e.preventDefault();
        
        let hasErrors = false;
        clearValidation();

        const motivo = DOM.inputMotivo ? DOM.inputMotivo.value.trim() : '';
        if (motivo.length < 3) {
            if (DOM.inputMotivo) DOM.inputMotivo.classList.add('is-invalid');
            hasErrors = true;
        }

        const cantidad = DOM.inputCantidad ? parseInt(DOM.inputCantidad.value) : 0;
        if (isNaN(cantidad) || cantidad === 0) {
            if (DOM.inputCantidad) DOM.inputCantidad.classList.add('is-invalid');
            hasErrors = true;
        }

        if (hasErrors) return;

        setSaving(true);
        
        const id = DOM.inputId ? DOM.inputId.value : '';
        const payload = {
            cantidad: cantidad,
            motivo: motivo
        };

        try {
            const token = localStorage.getItem('jwt_token');
            const res = await fetch(`/api/inventory/${id}/adjust`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                if (res.status === 401) {
                    if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
                    return;
                }
                const data = await res.json();
                throw new Error(data.detail || 'Error al ajustar stock');
            }

            if (typeof window.showToast === 'function') {
                window.showToast('Stock ajustado correctamente', 'success');
            }
            
            // Force modal close without confirm
            if (DOM.form) {
                initialFormData = new URLSearchParams(new FormData(DOM.form)).toString();
            }
            window._forceCloseInventoryModal = true;
            if (bsModal) bsModal.hide();
            
            await loadInventory();
        } catch (err) {
            if (typeof window.showToast === 'function') {
                window.showToast(err.message, 'danger');
            }
        } finally {
            setSaving(false);
        }
    }

    function setSaving(saving) {
        if (!DOM.btnSave) return;
        if (saving) {
            DOM.btnSave.disabled = true;
            DOM.btnSave.innerHTML = '<span class="spinner-border spinner-border-sm me-1" aria-hidden="true"></span> Guardando...';
        } else {
            DOM.btnSave.disabled = false;
            DOM.btnSave.innerHTML = 'Guardar Ajuste';
        }
    }

    window.cargarAlertasInventarioModal = async function() {
        const container = document.getElementById('inventario-alertas-lista');
        if (!container) return;

        container.innerHTML = typeof window.renderSkeletonCard === 'function' ? window.renderSkeletonCard(3) : '<div class="text-center py-4 text-muted">Cargando alertas...</div>';

        const token = localStorage.getItem('jwt_token');
        try {
            const res = await fetch('/api/inventario/alertas', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (!res.ok) throw new Error('Error al consultar alertas');
            const alertas = await res.json();

            if (!alertas || alertas.length === 0) {
                container.innerHTML = '<div class="text-center py-4 text-success"><i class="bi bi-check-circle fs-3 d-block mb-2"></i>No hay alertas de stock pendientes.</div>';
                return;
            }

            let html = '';
            alertas.forEach(a => {
                const nombre = a.producto_nombre || a.mensaje;
                const sku = a.variante_sku ? `<span class="badge bg-light text-dark border ms-1">SKU: ${a.variante_sku}</span>` : '';
                html += `
                <div class="list-group-item d-flex justify-content-between align-items-center py-3">
                    <div>
                        <h6 class="mb-1 text-danger fw-bold"><i class="bi bi-exclamation-triangle-fill me-1"></i>${nombre}${sku}</h6>
                        <small class="text-muted">Stock actual: <strong class="text-danger">${a.stock_actual}</strong> | Mínimo requerido: <strong>${a.stock_minimo}</strong></small>
                    </div>
                    <button type="button" class="btn btn-sm btn-outline-success btn-atender-alerta" onclick="window.atenderAlertaStock(${a.id_alerta}, this)">
                        <i class="bi bi-check-lg me-1"></i>Marcar Atendida
                    </button>
                </div>`;
            });
            container.innerHTML = html;
        } catch (err) {
            container.innerHTML = `<div class="text-center py-4 text-danger"><i class="bi bi-exclamation-triangle me-1"></i>${err.message || 'Error al cargar alertas'}</div>`;
        }
    };

})();
