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

    function renderTable() {
        if (!DOM.tableBody) return;
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
            
            const isLowStock = item.stock_actual <= item.stock_minimo;
            const stockBadgeClass = isLowStock ? 'bg-danger' : 'bg-success';

            tr.innerHTML = `
                <td>${item.id_inventario}</td>
                <td>${item.producto_nombre || 'N/A'}</td>
                <td class="font-monospace">${item.variante_sku || 'N/A'}</td>
                <td>${item.sucursal_nombre || 'N/A'}</td>
                <td><span class="badge ${stockBadgeClass} fs-6">${item.stock_actual}</span></td>
                <td>${item.stock_minimo}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-teal" onclick="window.openInventoryModal(${item.id_inventario})" title="Ajustar Stock">
                        <i class="bi bi-sliders"></i> Ajustar
                    </button>
                </td>
            `;
            DOM.tableBody.appendChild(tr);
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

})();
