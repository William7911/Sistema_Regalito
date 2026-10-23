/**
 * Módulo de Clientes y Tipos de Cliente — Tienda el Regalito
 * Arquitectura DERCAS / Vanilla JS + Bootstrap 5
 * Controla:
 *   - Directorio de clientes paginado con filtros de texto, estado y rango de fechas.
 *   - Ordenamiento interactivo asc/desc por columnas.
 *   - Modal de ficha de solo lectura con contactos, ubicación y tipo.
 *   - Formulario de cliente con contactos dinámicos (agregar, editar, quitar).
 *   - Protección estricta de Consumidor Final (CF): NIT inmutable y no desactivable.
 *   - Mantenimiento completo de Tipos de Cliente (CRUD con soft delete).
 *   - Descarga de reportes Excel y CSV respetando filtros activos.
 *   - Consumo de catálogos de ubicación vía /api/departamentos/{id}/municipios.
 */

(function () {
    'use strict';

    // Estado local del módulo
    const state = {
        // Clientes
        page: 1,
        limit: 15,
        total: 0,
        sortBy: 'id_cliente',
        sortOrder: 'asc',
        currentEditId: null,
        deactivateTargetId: null,

        // Tipos de Cliente
        tiposCliente: [],
        currentEditTipoId: null,
        deactivateTargetTipoId: null,

        // Ubicación
        departamentos: [],
        municipiosMap: {}, // id_departamento -> array
    };

    // Referencias a elementos DOM
    let DOM = {};

    function initDOM() {
        DOM = {
            view: document.getElementById('clients-view'),

            // Tabs
            tabBtnClientes: document.getElementById('tab-btn-clientes'),
            tabBtnTipos: document.getElementById('tab-btn-tipos'),
            tabClientesContent: document.getElementById('tab-clientes-content'),
            tabTiposContent: document.getElementById('tab-tipos-content'),

            // Filtros Clientes
            filterName: document.getElementById('filter-client-name'),
            filterNit: document.getElementById('filter-client-nit'),
            filterType: document.getElementById('filter-client-type'),
            filterActive: document.getElementById('filter-client-active'),
            filterDateFrom: document.getElementById('filter-client-date-from'),
            filterDateTo: document.getElementById('filter-client-date-to'),
            btnFilter: document.getElementById('btn-filter-clients'),
            btnResetFilter: document.getElementById('btn-reset-filter-clients'),
            btnNewClient: document.getElementById('btn-new-client'),
            btnExcel: document.getElementById('btn-report-clients-excel'),
            btnCsv: document.getElementById('btn-report-clients-csv'),

            // Tabla Clientes & Paginación
            tableBody: document.getElementById('clients-table-body'),
            paginationInfo: document.getElementById('clients-pagination-info'),
            pageInfo: document.getElementById('clients-page-info'),
            btnPrev: document.getElementById('clients-prev-page'),
            btnNext: document.getElementById('clients-next-page'),

            // Modal Formulario Cliente
            clientModalEl: document.getElementById('client-modal'),
            clientModalTitle: document.getElementById('clientModalTitle'),
            clientForm: document.getElementById('client-form'),
            clientId: document.getElementById('client-id'),
            clientNit: document.getElementById('client-nit'),
            clientNitHint: document.getElementById('client-nit-hint'),
            clientNitFeedback: document.getElementById('client-nit-feedback'),
            clientName: document.getElementById('client-name'),
            clientType: document.getElementById('client-type'),
            clientDept: document.getElementById('client-dept'),
            clientMuni: document.getElementById('client-muni'),
            clientAddress: document.getElementById('client-address'),
            contactsContainer: document.getElementById('client-contacts-container'),
            btnAddContactRow: document.getElementById('btn-add-contact-row'),
            btnSaveClient: document.getElementById('btn-save-client'),

            // Modal Ficha de Cliente (Solo Lectura)
            detailModalEl: document.getElementById('client-detail-modal'),
            detailBody: document.getElementById('client-detail-body'),

            // Modal Confirmar Desactivación Cliente
            deactivateModalEl: document.getElementById('confirm-client-deactivate-modal'),
            deactivateText: document.getElementById('confirm-client-deactivate-text'),
            btnConfirmDeactivate: document.getElementById('btn-confirm-client-deactivate'),

            // Mantenimiento Tipos de Cliente
            tiposTableBody: document.getElementById('tipos-table-body'),
            btnNewTipo: document.getElementById('btn-new-tipo-cliente'),
            tipoModalEl: document.getElementById('tipo-cliente-modal'),
            tipoModalTitle: document.getElementById('tipoClienteModalTitle'),
            tipoForm: document.getElementById('tipo-cliente-form'),
            tipoId: document.getElementById('tipo-cliente-id'),
            tipoNombre: document.getElementById('tipo-cliente-nombre'),
            tipoDescuento: document.getElementById('tipo-cliente-descuento'),
            btnSaveTipo: document.getElementById('btn-save-tipo-cliente'),
            tipoDeactivateModalEl: document.getElementById('confirm-tipo-deactivate-modal'),
            tipoDeactivateText: document.getElementById('confirm-tipo-deactivate-text'),
            btnConfirmTipoDeactivate: document.getElementById('btn-confirm-tipo-deactivate'),
        };
    }

    // Instancias de modales Bootstrap
    let clientBsModal = null;
    let detailBsModal = null;
    let deactivateBsModal = null;
    let tipoBsModal = null;
    let tipoDeactivateBsModal = null;

    function getAuthHeaders() {
        const token = localStorage.getItem('token') || sessionStorage.getItem('token');
        return {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        };
    }

    // -----------------------------------------------------------------------
    // Inicialización del Módulo
    // -----------------------------------------------------------------------
    window.showClientsModule = async function () {
        initDOM();
        if (!DOM.view) return;

        // Inicializar modales de Bootstrap con backdrop="static"
        if (!clientBsModal && DOM.clientModalEl) {
            clientBsModal = new bootstrap.Modal(DOM.clientModalEl, { backdrop: 'static', keyboard: false });
        }
        if (!detailBsModal && DOM.detailModalEl) {
            detailBsModal = new bootstrap.Modal(DOM.detailModalEl, { backdrop: 'static', keyboard: true });
        }
        if (!deactivateBsModal && DOM.deactivateModalEl) {
            deactivateBsModal = new bootstrap.Modal(DOM.deactivateModalEl, { backdrop: 'static', keyboard: false });
        }
        if (!tipoBsModal && DOM.tipoModalEl) {
            tipoBsModal = new bootstrap.Modal(DOM.tipoModalEl, { backdrop: 'static', keyboard: false });
        }
        if (!tipoDeactivateBsModal && DOM.tipoDeactivateModalEl) {
            tipoDeactivateBsModal = new bootstrap.Modal(DOM.tipoDeactivateModalEl, { backdrop: 'static', keyboard: false });
        }

        bindEvents();
        await loadCatalogs();
        await loadClients();
        await loadTiposCliente();
    };

    function bindEvents() {
        // Filtros y Paginación Clientes
        if (DOM.btnFilter && !DOM.btnFilter.dataset.bound) {
            DOM.btnFilter.dataset.bound = 'true';
            DOM.btnFilter.addEventListener('click', () => { state.page = 1; loadClients(); });
        }
        if (DOM.btnResetFilter && !DOM.btnResetFilter.dataset.bound) {
            DOM.btnResetFilter.dataset.bound = 'true';
            DOM.btnResetFilter.addEventListener('click', resetFilters);
        }
        if (DOM.btnNewClient && !DOM.btnNewClient.dataset.bound) {
            DOM.btnNewClient.dataset.bound = 'true';
            DOM.btnNewClient.addEventListener('click', openNewClientModal);
        }
        if (DOM.btnPrev && !DOM.btnPrev.dataset.bound) {
            DOM.btnPrev.dataset.bound = 'true';
            DOM.btnPrev.addEventListener('click', () => {
                if (state.page > 1) { state.page--; loadClients(); }
            });
        }
        if (DOM.btnNext && !DOM.btnNext.dataset.bound) {
            DOM.btnNext.dataset.bound = 'true';
            DOM.btnNext.addEventListener('click', () => {
                const maxPages = Math.ceil(state.total / state.limit) || 1;
                if (state.page < maxPages) { state.page++; loadClients(); }
            });
        }

        // Ordenamiento por encabezados de tabla
        document.querySelectorAll('[data-client-sort]').forEach(th => {
            if (!th.dataset.bound) {
                th.dataset.bound = 'true';
                th.addEventListener('click', () => {
                    const col = th.dataset.clientSort;
                    if (state.sortBy === col) {
                        state.sortOrder = (state.sortOrder === 'asc') ? 'desc' : 'asc';
                    } else {
                        state.sortBy = col;
                        state.sortOrder = 'asc';
                    }
                    updateSortIcons();
                    loadClients();
                });
            }
        });

        // Reportes Excel y CSV
        if (DOM.btnExcel && !DOM.btnExcel.dataset.bound) {
            DOM.btnExcel.dataset.bound = 'true';
            DOM.btnExcel.addEventListener('click', () => exportReport('excel'));
        }
        if (DOM.btnCsv && !DOM.btnCsv.dataset.bound) {
            DOM.btnCsv.dataset.bound = 'true';
            DOM.btnCsv.addEventListener('click', () => exportReport('csv'));
        }

        // Formulario Cliente
        if (DOM.clientDept && !DOM.clientDept.dataset.bound) {
            DOM.clientDept.dataset.bound = 'true';
            DOM.clientDept.addEventListener('change', (e) => loadMunicipiosForDept(e.target.value));
        }
        if (DOM.btnAddContactRow && !DOM.btnAddContactRow.dataset.bound) {
            DOM.btnAddContactRow.dataset.bound = 'true';
            DOM.btnAddContactRow.addEventListener('click', () => addContactRow());
        }
        if (DOM.clientForm && !DOM.clientForm.dataset.bound) {
            DOM.clientForm.dataset.bound = 'true';
            DOM.clientForm.addEventListener('submit', handleSaveClient);
        }
        if (DOM.btnConfirmDeactivate && !DOM.btnConfirmDeactivate.dataset.bound) {
            DOM.btnConfirmDeactivate.dataset.bound = 'true';
            DOM.btnConfirmDeactivate.addEventListener('click', handleDeactivateConfirm);
        }

        // Mantenimiento Tipos de Cliente
        if (DOM.btnNewTipo && !DOM.btnNewTipo.dataset.bound) {
            DOM.btnNewTipo.dataset.bound = 'true';
            DOM.btnNewTipo.addEventListener('click', openNewTipoModal);
        }
        if (DOM.tipoForm && !DOM.tipoForm.dataset.bound) {
            DOM.tipoForm.dataset.bound = 'true';
            DOM.tipoForm.addEventListener('submit', handleSaveTipo);
        }
        if (DOM.btnConfirmTipoDeactivate && !DOM.btnConfirmTipoDeactivate.dataset.bound) {
            DOM.btnConfirmTipoDeactivate.dataset.bound = 'true';
            DOM.btnConfirmTipoDeactivate.addEventListener('click', handleDeactivateTipoConfirm);
        }
    }

    function updateSortIcons() {
        document.querySelectorAll('[data-client-sort]').forEach(th => {
            const icon = th.querySelector('i');
            if (!icon) return;
            if (th.dataset.clientSort === state.sortBy) {
                icon.className = `bi bi-arrow-${state.sortOrder === 'asc' ? 'up' : 'down'} text-teal small ms-1`;
            } else {
                icon.className = 'bi bi-arrow-down-up text-muted small ms-1';
            }
        });
    }

    function resetFilters() {
        if (DOM.filterName) DOM.filterName.value = '';
        if (DOM.filterNit) DOM.filterNit.value = '';
        if (DOM.filterType) DOM.filterType.value = '';
        if (DOM.filterActive) DOM.filterActive.value = 'true';
        if (DOM.filterDateFrom) DOM.filterDateFrom.value = '';
        if (DOM.filterDateTo) DOM.filterDateTo.value = '';
        state.page = 1;
        state.sortBy = 'id_cliente';
        state.sortOrder = 'asc';
        updateSortIcons();
        loadClients();
    }

    // -----------------------------------------------------------------------
    // Carga de Catálogos (Tipos de Cliente y Departamentos)
    // -----------------------------------------------------------------------
    async function loadCatalogs() {
        try {
            // Tipos de Cliente
            const resTipos = await fetch('/api/tipos-cliente?only_active=false', { headers: getAuthHeaders() });
            if (resTipos.ok) {
                state.tiposCliente = await resTipos.json();
                populateTiposDropdown();
            }

            // Departamentos
            const resDept = await fetch('/api/departamentos', { headers: getAuthHeaders() });
            if (resDept.ok) {
                state.departamentos = await resDept.json();
                populateDeptDropdown();
            }
        } catch (err) {
            console.error('Error cargando catálogos de clientes:', err);
        }
    }

    function populateTiposDropdown() {
        if (DOM.filterType) {
            const currentVal = DOM.filterType.value;
            DOM.filterType.innerHTML = '<option value="">Todos los tipos</option>';
            state.tiposCliente.forEach(t => {
                DOM.filterType.innerHTML += `<option value="${t.id_tipo_cliente}">${t.nombre}</option>`;
            });
            DOM.filterType.value = currentVal;
        }
        if (DOM.clientType) {
            const currentVal = DOM.clientType.value;
            DOM.clientType.innerHTML = '<option value="">Seleccione tipo...</option>';
            state.tiposCliente.filter(t => t.estado === 'Activo').forEach(t => {
                DOM.clientType.innerHTML += `<option value="${t.id_tipo_cliente}">${t.nombre} ${t.descuento_predeterminado ? '(' + t.descuento_predeterminado + '% desc)' : ''}</option>`;
            });
            DOM.clientType.value = currentVal;
        }
    }

    function populateDeptDropdown() {
        if (DOM.clientDept) {
            const currentVal = DOM.clientDept.value;
            DOM.clientDept.innerHTML = '<option value="">Seleccione departamento...</option>';
            state.departamentos.forEach(d => {
                DOM.clientDept.innerHTML += `<option value="${d.id_departamento}">${d.nombre}</option>`;
            });
            DOM.clientDept.value = currentVal;
        }
    }

    // Endpoint reutilizable de ubicación: /api/departamentos/{id}/municipios
    async function loadMunicipiosForDept(deptId, preselectedMuniId = null) {
        if (!DOM.clientMuni) return;
        DOM.clientMuni.innerHTML = '<option value="">Cargando municipios...</option>';
        DOM.clientMuni.disabled = true;

        if (!deptId) {
            DOM.clientMuni.innerHTML = '<option value="">Seleccione departamento primero...</option>';
            return;
        }

        try {
            const res = await fetch(`/api/departamentos/${deptId}/municipios`, { headers: getAuthHeaders() });
            if (res.ok) {
                const munis = await res.json();
                state.municipiosMap[deptId] = munis;
                DOM.clientMuni.innerHTML = '<option value="">Seleccione municipio...</option>';
                munis.forEach(m => {
                    const sel = (preselectedMuniId && Number(preselectedMuniId) === m.id_municipio) ? 'selected' : '';
                    DOM.clientMuni.innerHTML += `<option value="${m.id_municipio}" ${sel}>${m.nombre}</option>`;
                });
                DOM.clientMuni.disabled = false;
            }
        } catch (err) {
            DOM.clientMuni.innerHTML = '<option value="">Error al cargar municipios</option>';
        }
    }

    // -----------------------------------------------------------------------
    // Listado Paginado de Clientes con Filtros y Ordenamiento
    // -----------------------------------------------------------------------
    async function loadClients() {
        if (!DOM.tableBody) return;
        DOM.tableBody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Cargando clientes...</td></tr>';

        const params = new URLSearchParams();
        params.append('limit', state.limit);
        params.append('offset', (state.page - 1) * state.limit);
        params.append('sort_by', state.sortBy);
        params.append('sort_order', state.sortOrder);

        if (DOM.filterName && DOM.filterName.value.trim()) params.append('nombre', DOM.filterName.value.trim());
        if (DOM.filterNit && DOM.filterNit.value.trim()) params.append('nit', DOM.filterNit.value.trim());
        if (DOM.filterType && DOM.filterType.value) params.append('id_tipo_cliente', DOM.filterType.value);
        if (DOM.filterActive && DOM.filterActive.value !== '') params.append('is_active', DOM.filterActive.value);
        if (DOM.filterDateFrom && DOM.filterDateFrom.value) params.append('fecha_desde', DOM.filterDateFrom.value);
        if (DOM.filterDateTo && DOM.filterDateTo.value) params.append('fecha_hasta', DOM.filterDateTo.value);

        try {
            const res = await fetch(`/api/clientes?${params.toString()}`, { headers: getAuthHeaders() });
            if (!res.ok) throw new Error('Error al consultar clientes');
            const data = await res.json();

            state.total = data.total;
            renderClientsTable(data.items);
            renderPagination();
        } catch (err) {
            DOM.tableBody.innerHTML = `<tr><td colspan="7" class="text-center py-4 text-danger"><i class="bi bi-exclamation-circle me-1"></i>${err.message}</td></tr>`;
        }
    }

    function renderClientsTable(items) {
        if (!items || items.length === 0) {
            DOM.tableBody.innerHTML = '<tr><td colspan="7" class="text-center py-4 text-muted">No se encontraron clientes con los filtros aplicados.</td></tr>';
            return;
        }

        DOM.tableBody.innerHTML = '';
        items.forEach(c => {
            const isCF = (c.nit && c.nit.toUpperCase() === 'CF');
            const statusBadge = c.estado === 'Activo'
                ? '<span class="badge rounded-pill bg-success-subtle text-success border border-success-subtle">Activo</span>'
                : '<span class="badge rounded-pill bg-danger-subtle text-danger border border-danger-subtle">Inactivo</span>';

            const tipoBadge = c.tipo_cliente
                ? `<span class="badge bg-light text-dark border">${c.tipo_cliente.nombre}</span>`
                : '<span class="text-muted">—</span>';

            const ubicacion = c.municipio_nombre || (c.direccion ? c.direccion : '<span class="text-muted">—</span>');

            const contactosCount = (c.contactos && c.contactos.length > 0)
                ? (c.contactos[0].telefono ? `<i class="bi bi-telephone me-1 text-muted"></i>${c.contactos[0].telefono}` : (c.contactos[0].correo || '—'))
                : '<span class="text-muted">—</span>';

            const extraContactos = (c.contactos && c.contactos.length > 1)
                ? ` <span class="badge bg-secondary-subtle text-secondary small">+${c.contactos.length - 1}</span>`
                : '';

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong class="font-monospace text-teal">${c.nit}</strong></td>
                <td>
                    <div class="fw-semibold">${c.nombre_comercial}</div>
                    ${c.direccion ? `<small class="text-muted text-truncate d-block" style="max-width: 250px;">${c.direccion}</small>` : ''}
                </td>
                <td>${tipoBadge}</td>
                <td><small class="text-muted">${ubicacion}</small></td>
                <td><small>${contactosCount}${extraContactos}</small></td>
                <td>${statusBadge}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-info me-1" data-action="view-card" data-id="${c.id_cliente}" title="Ver ficha del cliente">
                        <i class="bi bi-eye"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary me-1" data-action="edit" data-id="${c.id_cliente}" title="Editar cliente">
                        <i class="bi bi-pencil"></i>
                    </button>
                    ${isCF
                        ? `<button class="btn btn-sm btn-outline-secondary opacity-50" disabled title="Consumidor Final no puede desactivarse"><i class="bi bi-trash"></i></button>`
                        : `<button class="btn btn-sm ${c.estado === 'Activo' ? 'btn-outline-danger' : 'btn-outline-success'}" data-action="toggle-status" data-id="${c.id_cliente}" data-name="${c.nombre_comercial}" data-status="${c.estado}" title="${c.estado === 'Activo' ? 'Desactivar cliente' : 'Activar cliente'}">
                            <i class="bi ${c.estado === 'Activo' ? 'bi-trash' : 'bi-check-circle'}"></i>
                           </button>`
                    }
                </td>
            `;

            tr.querySelectorAll('button[data-action]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const action = btn.dataset.action;
                    const id = Number(btn.dataset.id);
                    if (action === 'view-card') openClientDetailModal(id);
                    if (action === 'edit') openEditClientModal(id);
                    if (action === 'toggle-status') openDeactivateModal(id, btn.dataset.name, btn.dataset.status);
                });
            });

            DOM.tableBody.appendChild(tr);
        });
    }

    function renderPagination() {
        const totalPages = Math.ceil(state.total / state.limit) || 1;
        if (DOM.paginationInfo) {
            const start = state.total === 0 ? 0 : (state.page - 1) * state.limit + 1;
            const end = Math.min(state.page * state.limit, state.total);
            DOM.paginationInfo.textContent = `Mostrando ${start} a ${end} de ${state.total} clientes`;
        }
        if (DOM.pageInfo) DOM.pageInfo.textContent = `Página ${state.page} de ${totalPages}`;
        if (DOM.btnPrev) DOM.btnPrev.disabled = (state.page <= 1);
        if (DOM.btnNext) DOM.btnNext.disabled = (state.page >= totalPages);
    }

    // -----------------------------------------------------------------------
    // Contactos Dinámicos (Agregar, editar, quitar en modal)
    // -----------------------------------------------------------------------
    function addContactRow(phone = '', email = '') {
        if (!DOM.contactsContainer) return;
        const rowId = 'contact-row-' + Date.now() + '-' + Math.floor(Math.random() * 1000);
        const row = document.createElement('div');
        row.className = 'd-flex gap-2 align-items-center contact-item';
        row.id = rowId;
        row.innerHTML = `
            <div class="input-group input-group-sm flex-grow-1">
                <span class="input-group-text"><i class="bi bi-telephone"></i></span>
                <input type="text" class="form-control contact-phone" placeholder="Teléfono (ej. 5555-1234)" value="${phone}" maxlength="20">
            </div>
            <div class="input-group input-group-sm flex-grow-1">
                <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                <input type="email" class="form-control contact-email" placeholder="Correo (ej. cliente@correo.com)" value="${email}" maxlength="100">
            </div>
            <button type="button" class="btn btn-sm btn-outline-danger btn-remove-contact" title="Quitar contacto">
                <i class="bi bi-trash"></i>
            </button>
        `;
        row.querySelector('.btn-remove-contact').addEventListener('click', () => {
            row.remove();
        });
        DOM.contactsContainer.appendChild(row);
    }

    function getContactsFromModal() {
        if (!DOM.contactsContainer) return [];
        const items = [];
        DOM.contactsContainer.querySelectorAll('.contact-item').forEach(row => {
            const phone = row.querySelector('.contact-phone')?.value.trim() || null;
            const email = row.querySelector('.contact-email')?.value.trim() || null;
            if (phone || email) {
                items.push({ telefono: phone, correo: email });
            }
        });
        return items;
    }

    // -----------------------------------------------------------------------
    // Modal Crear / Editar Cliente
    // -----------------------------------------------------------------------
    function resetClientForm() {
        if (!DOM.clientForm) return;
        DOM.clientForm.reset();
        DOM.clientId.value = '';
        DOM.clientNit.readOnly = false;
        DOM.clientNit.classList.remove('bg-light');
        if (DOM.clientNitHint) DOM.clientNitHint.classList.add('d-none');
        DOM.clientForm.classList.remove('was-validated');
        DOM.clientForm.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
        if (DOM.clientMuni) {
            DOM.clientMuni.innerHTML = '<option value="">Seleccione municipio...</option>';
            DOM.clientMuni.disabled = true;
        }
        if (DOM.contactsContainer) {
            DOM.contactsContainer.innerHTML = '';
        }
    }

    function openNewClientModal() {
        resetClientForm();
        state.currentEditId = null;
        if (DOM.clientModalTitle) DOM.clientModalTitle.textContent = 'Nuevo Cliente';
        addContactRow(); // Fila inicial vacía
        if (clientBsModal) clientBsModal.show();
    }

    async function openEditClientModal(id) {
        resetClientForm();
        state.currentEditId = id;
        if (DOM.clientModalTitle) DOM.clientModalTitle.textContent = 'Editar Cliente';

        try {
            const res = await fetch(`/api/clientes/${id}`, { headers: getAuthHeaders() });
            if (!res.ok) throw new Error('No se pudo cargar la información del cliente');
            const c = await res.json();

            DOM.clientId.value = c.id_cliente;
            DOM.clientNit.value = c.nit;
            DOM.clientName.value = c.nombre_comercial;
            DOM.clientType.value = c.id_tipo_cliente;
            DOM.clientAddress.value = c.direccion || '';

            // Protección de Consumidor Final (CF): su NIT no se puede modificar
            const isCF = (c.nit && c.nit.toUpperCase() === 'CF');
            if (isCF) {
                DOM.clientNit.readOnly = true;
                DOM.clientNit.classList.add('bg-light');
                if (DOM.clientNitHint) DOM.clientNitHint.classList.remove('d-none');
            }

            // Contactos dinámicos
            if (c.contactos && c.contactos.length > 0) {
                c.contactos.forEach(ct => addContactRow(ct.telefono || '', ct.correo || ''));
            } else {
                addContactRow();
            }

            // Ubicación Departamento y Municipio
            if (c.id_municipio) {
                try {
                    // Buscar en catálogo de departamentos
                    const deptRes = await fetch(`/api/departamentos/municipios`, { headers: getAuthHeaders() });
                    if (deptRes.ok) {
                        const allMunis = await deptRes.json();
                        const found = allMunis.find(m => m.id_municipio === c.id_municipio);
                        if (found) {
                            DOM.clientDept.value = found.id_departamento;
                            await loadMunicipiosForDept(found.id_departamento, c.id_municipio);
                        }
                    }
                } catch (_) {}
            }

            if (clientBsModal) clientBsModal.show();
        } catch (err) {
            if (typeof window.showToast === 'function') window.showToast(err.message, 'danger');
        }
    }

    async function handleSaveClient(e) {
        e.preventDefault();
        DOM.clientForm.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

        const nit = DOM.clientNit.value.trim().toUpperCase();
        const nombre = DOM.clientName.value.trim();
        const idTipo = DOM.clientType.value ? Number(DOM.clientType.value) : null;
        const idMuni = DOM.clientMuni.value ? Number(DOM.clientMuni.value) : null;
        const direccion = DOM.clientAddress.value.trim();
        const contactos = getContactsFromModal();

        let hasError = false;
        if (!nit) {
            DOM.clientNit.classList.add('is-invalid');
            hasError = true;
        }
        if (!nombre) {
            DOM.clientName.classList.add('is-invalid');
            hasError = true;
        }
        if (!idTipo) {
            DOM.clientType.classList.add('is-invalid');
            hasError = true;
        }
        if (hasError) return;

        const payload = {
            id_tipo_cliente: idTipo,
            id_municipio: idMuni,
            nit: nit,
            nombre_comercial: nombre,
            direccion: direccion || null,
            contactos: contactos,
        };

        const isEdit = Boolean(state.currentEditId);
        const url = isEdit ? `/api/clientes/${state.currentEditId}` : '/api/clientes';
        const method = isEdit ? 'PUT' : 'POST';

        DOM.btnSaveClient.disabled = true;
        DOM.btnSaveClient.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Guardando...';

        try {
            const res = await fetch(url, {
                method: method,
                headers: getAuthHeaders(),
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                const msg = errData.detail || 'Ocurrió un error al procesar el cliente';
                if (res.status === 400 && msg.toLowerCase().includes('nit')) {
                    DOM.clientNit.classList.add('is-invalid');
                    if (DOM.clientNitFeedback) DOM.clientNitFeedback.textContent = msg;
                } else if (typeof window.showToast === 'function') {
                    window.showToast(msg, 'danger');
                }
                return;
            }

            if (clientBsModal) clientBsModal.hide();
            if (typeof window.showToast === 'function') {
                window.showToast(isEdit ? 'Cliente actualizado exitosamente' : 'Cliente registrado exitosamente', 'success');
            }
            await loadClients();
        } catch (err) {
            if (typeof window.showToast === 'function') window.showToast('Error de red al procesar el cliente', 'danger');
        } finally {
            DOM.btnSaveClient.disabled = false;
            DOM.btnSaveClient.innerHTML = '<i class="bi bi-check-lg me-1"></i> Guardar Cliente';
        }
    }

    // -----------------------------------------------------------------------
    // Modal Ficha de Cliente (Solo Lectura - Punto 3)
    // -----------------------------------------------------------------------
    async function openClientDetailModal(id) {
        if (!DOM.detailBody) return;
        DOM.detailBody.innerHTML = '<div class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Cargando ficha...</div>';
        if (detailBsModal) detailBsModal.show();

        try {
            const res = await fetch(`/api/clientes/${id}`, { headers: getAuthHeaders() });
            if (!res.ok) throw new Error('No se pudo cargar la información del cliente');
            const c = await res.json();

            // Ubicación: encontrar nombre de departamento si existe municipio
            let deptoNombre = '—';
            if (c.id_municipio && state.departamentos.length > 0) {
                try {
                    const muniRes = await fetch(`/api/departamentos/municipios`, { headers: getAuthHeaders() });
                    if (muniRes.ok) {
                        const munis = await muniRes.json();
                        const foundM = munis.find(m => m.id_municipio === c.id_municipio);
                        if (foundM) {
                            const foundD = state.departamentos.find(d => d.id_departamento === foundM.id_departamento);
                            if (foundD) deptoNombre = foundD.nombre;
                        }
                    }
                } catch (_) {}
            }

            const tipoDesc = c.tipo_cliente?.descuento_predeterminado
                ? ` (${c.tipo_cliente.descuento_predeterminado}% de descuento)`
                : '';

            const statusClass = c.estado === 'Activo' ? 'bg-success text-white' : 'bg-danger text-white';

            let contactosHtml = '<span class="text-muted">Sin contactos registrados</span>';
            if (c.contactos && c.contactos.length > 0) {
                contactosHtml = `
                    <div class="table-responsive mt-2">
                        <table class="table table-sm table-bordered mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th>#</th>
                                    <th>Teléfono</th>
                                    <th>Correo Electrónico</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${c.contactos.map((ct, idx) => `
                                    <tr>
                                        <td>${idx + 1}</td>
                                        <td>${ct.telefono ? `<i class="bi bi-telephone text-teal me-1"></i>${ct.telefono}` : '<span class="text-muted">—</span>'}</td>
                                        <td>${ct.correo ? `<i class="bi bi-envelope text-teal me-1"></i>${ct.correo}` : '<span class="text-muted">—</span>'}</td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                `;
            }

            const fechaReg = c.fecha_creacion
                ? new Date(c.fecha_creacion).toLocaleString('es-GT', { dateStyle: 'medium', timeStyle: 'short' })
                : '—';

            DOM.detailBody.innerHTML = `
                <div class="d-flex justify-content-between align-items-center pb-3 border-bottom mb-3">
                    <div>
                        <span class="badge ${statusClass} px-3 py-2 rounded-pill fs-6">${c.estado}</span>
                        <h4 class="fw-bold mb-0 mt-2">${c.nombre_comercial}</h4>
                    </div>
                    <div class="text-end">
                        <span class="text-muted small d-block">NIT</span>
                        <span class="fs-4 fw-monospace text-teal fw-bold">${c.nit}</span>
                    </div>
                </div>

                <div class="row g-3 mb-3">
                    <div class="col-md-6">
                        <div class="p-3 bg-light rounded-3">
                            <small class="text-muted d-block fw-semibold mb-1">TIPO DE CLIENTE</small>
                            <span class="fw-bold">${c.tipo_cliente?.nombre || 'General'}</span>${tipoDesc}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="p-3 bg-light rounded-3">
                            <small class="text-muted d-block fw-semibold mb-1">FECHA DE REGISTRO</small>
                            <span class="fw-semibold">${fechaReg}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="p-3 bg-light rounded-3">
                            <small class="text-muted d-block fw-semibold mb-1">DEPARTAMENTO</small>
                            <span class="fw-semibold">${deptoNombre}</span>
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="p-3 bg-light rounded-3">
                            <small class="text-muted d-block fw-semibold mb-1">MUNICIPIO</small>
                            <span class="fw-semibold">${c.municipio_nombre || '—'}</span>
                        </div>
                    </div>
                    <div class="col-12">
                        <div class="p-3 bg-light rounded-3">
                            <small class="text-muted d-block fw-semibold mb-1">DIRECCIÓN FISCAL / ENTREGA</small>
                            <span class="fw-semibold">${c.direccion || '—'}</span>
                        </div>
                    </div>
                </div>

                <div class="card border border-light-subtle rounded-3">
                    <div class="card-header bg-white fw-bold py-2">
                        <i class="bi bi-people me-1 text-teal"></i> Contactos Asociados (${c.contactos ? c.contactos.length : 0})
                    </div>
                    <div class="card-body p-3">
                        ${contactosHtml}
                    </div>
                </div>
            `;
        } catch (err) {
            DOM.detailBody.innerHTML = `<div class="text-danger text-center py-4"><i class="bi bi-exclamation-circle me-1"></i>${err.message}</div>`;
        }
    }

    // -----------------------------------------------------------------------
    // Desactivación / Reactivación Lógica de Clientes
    // -----------------------------------------------------------------------
    function openDeactivateModal(id, name, status) {
        state.deactivateTargetId = id;
        if (DOM.deactivateText) {
            DOM.deactivateText.textContent = `¿Confirmas que deseas desactivar al cliente "${name}"? No aparecerá en ventas activas.`;
        }
        if (deactivateBsModal) deactivateBsModal.show();
    }

    async function handleDeactivateConfirm() {
        if (!state.deactivateTargetId) return;

        if (DOM.btnConfirmDeactivate) {
            DOM.btnConfirmDeactivate.disabled = true;
            DOM.btnConfirmDeactivate.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Procesando...';
        }

        try {
            const res = await fetch(`/api/clientes/${state.deactivateTargetId}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || 'No se pudo desactivar el cliente');
            }

            if (deactivateBsModal) deactivateBsModal.hide();
            if (typeof window.showToast === 'function') {
                window.showToast('Cliente desactivado exitosamente', 'success');
            }
            await loadClients();
        } catch (err) {
            if (typeof window.showToast === 'function') window.showToast(err.message, 'danger');
        } finally {
            if (DOM.btnConfirmDeactivate) {
                DOM.btnConfirmDeactivate.disabled = false;
                DOM.btnConfirmDeactivate.textContent = 'Desactivar';
            }
        }
    }

    // -----------------------------------------------------------------------
    // Exportación de Reportes Excel / CSV con Filtros Activos (Punto 5)
    // -----------------------------------------------------------------------
    async function exportReport(fmt) {
        const params = new URLSearchParams();
        params.append('format', fmt);
        params.append('sort_by', state.sortBy);
        params.append('sort_order', state.sortOrder);

        if (DOM.filterName && DOM.filterName.value.trim()) params.append('nombre', DOM.filterName.value.trim());
        if (DOM.filterNit && DOM.filterNit.value.trim()) params.append('nit', DOM.filterNit.value.trim());
        if (DOM.filterType && DOM.filterType.value) params.append('id_tipo_cliente', DOM.filterType.value);
        if (DOM.filterActive && DOM.filterActive.value !== '') params.append('is_active', DOM.filterActive.value);
        if (DOM.filterDateFrom && DOM.filterDateFrom.value) params.append('fecha_desde', DOM.filterDateFrom.value);
        if (DOM.filterDateTo && DOM.filterDateTo.value) params.append('fecha_hasta', DOM.filterDateTo.value);

        try {
            const res = await fetch(`/api/clientes/reporte?${params.toString()}`, {
                headers: { 'Authorization': `Bearer ${localStorage.getItem('token') || sessionStorage.getItem('token')}` }
            });

            if (!res.ok) throw new Error('No se pudo generar el reporte de clientes');
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `reporte_clientes_${new Date().toISOString().slice(0, 10)}.${fmt === 'csv' ? 'csv' : 'xlsx'}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

            if (typeof window.showToast === 'function') {
                window.showToast(`Reporte ${fmt.toUpperCase()} descargado exitosamente`, 'success');
            }
        } catch (err) {
            if (typeof window.showToast === 'function') window.showToast(err.message, 'danger');
        }
    }

    // -----------------------------------------------------------------------
    // Mantenimiento de Tipos de Cliente (CRUD con Soft Delete - Punto 1)
    // -----------------------------------------------------------------------
    async function loadTiposCliente() {
        if (!DOM.tiposTableBody) return;
        DOM.tiposTableBody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted"><span class="spinner-border spinner-border-sm me-2"></span>Cargando tipos de cliente...</td></tr>';

        try {
            const res = await fetch('/api/tipos-cliente?only_active=false', { headers: getAuthHeaders() });
            if (!res.ok) throw new Error('Error al cargar tipos de cliente');
            state.tiposCliente = await res.json();
            renderTiposTable(state.tiposCliente);
            populateTiposDropdown();
        } catch (err) {
            DOM.tiposTableBody.innerHTML = `<tr><td colspan="5" class="text-center py-4 text-danger"><i class="bi bi-exclamation-circle me-1"></i>${err.message}</td></tr>`;
        }
    }

    function renderTiposTable(items) {
        if (!items || items.length === 0) {
            DOM.tiposTableBody.innerHTML = '<tr><td colspan="5" class="text-center py-4 text-muted">No hay tipos de cliente registrados.</td></tr>';
            return;
        }

        DOM.tiposTableBody.innerHTML = '';
        items.forEach(t => {
            const statusBadge = t.estado === 'Activo'
                ? '<span class="badge rounded-pill bg-success-subtle text-success border border-success-subtle">Activo</span>'
                : '<span class="badge rounded-pill bg-danger-subtle text-danger border border-danger-subtle">Inactivo</span>';

            const descText = t.descuento_predeterminado !== null && t.descuento_predeterminado !== undefined
                ? `<span class="fw-semibold text-teal">${t.descuento_predeterminado}%</span>`
                : '<span class="text-muted">0.00%</span>';

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><span class="font-monospace text-muted">#${t.id_tipo_cliente}</span></td>
                <td><strong class="text-dark">${t.nombre}</strong></td>
                <td>${descText}</td>
                <td>${statusBadge}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-secondary me-1" data-tipo-action="edit" data-id="${t.id_tipo_cliente}" title="Editar tipo">
                        <i class="bi bi-pencil"></i>
                    </button>
                    ${t.estado === 'Activo'
                        ? `<button class="btn btn-sm btn-outline-danger" data-tipo-action="deactivate" data-id="${t.id_tipo_cliente}" data-name="${t.nombre}" title="Desactivar tipo">
                            <i class="bi bi-trash"></i>
                           </button>`
                        : `<button class="btn btn-sm btn-outline-success" data-tipo-action="activate" data-id="${t.id_tipo_cliente}" data-name="${t.nombre}" title="Reactivar tipo">
                            <i class="bi bi-check-circle"></i>
                           </button>`
                    }
                </td>
            `;

            tr.querySelectorAll('button[data-tipo-action]').forEach(btn => {
                btn.addEventListener('click', () => {
                    const action = btn.dataset.tipoAction;
                    const id = Number(btn.dataset.id);
                    if (action === 'edit') openEditTipoModal(id);
                    if (action === 'deactivate') openDeactivateTipoModal(id, btn.dataset.name);
                    if (action === 'activate') handleActivateTipo(id);
                });
            });

            DOM.tiposTableBody.appendChild(tr);
        });
    }

    function openNewTipoModal() {
        if (!DOM.tipoForm) return;
        DOM.tipoForm.reset();
        DOM.tipoId.value = '';
        state.currentEditTipoId = null;
        if (DOM.tipoModalTitle) DOM.tipoModalTitle.textContent = 'Nuevo Tipo de Cliente';
        if (tipoBsModal) tipoBsModal.show();
    }

    async function openEditTipoModal(id) {
        if (!DOM.tipoForm) return;
        DOM.tipoForm.reset();
        state.currentEditTipoId = id;
        if (DOM.tipoModalTitle) DOM.tipoModalTitle.textContent = 'Editar Tipo de Cliente';

        try {
            const res = await fetch(`/api/tipos-cliente/${id}`, { headers: getAuthHeaders() });
            if (!res.ok) throw new Error('No se pudo cargar el tipo de cliente');
            const t = await res.json();

            DOM.tipoId.value = t.id_tipo_cliente;
            DOM.tipoNombre.value = t.nombre;
            DOM.tipoDescuento.value = (t.descuento_predeterminado !== null && t.descuento_predeterminado !== undefined) ? t.descuento_predeterminado : '';

            if (tipoBsModal) tipoBsModal.show();
        } catch (err) {
            if (typeof window.showToast === 'function') window.showToast(err.message, 'danger');
        }
    }

    async function handleSaveTipo(e) {
        e.preventDefault();
        const nombre = DOM.tipoNombre.value.trim();
        const descuentoRaw = DOM.tipoDescuento.value.trim();
        const descuento = descuentoRaw ? parseFloat(descuentoRaw) : null;

        if (!nombre) {
            DOM.tipoNombre.classList.add('is-invalid');
            return;
        }

        const isEdit = Boolean(state.currentEditTipoId);
        const url = isEdit ? `/api/tipos-cliente/${state.currentEditTipoId}` : '/api/tipos-cliente';
        const method = isEdit ? 'PUT' : 'POST';

        const payload = {
            nombre: nombre,
            descuento_predeterminado: descuento,
        };

        DOM.btnSaveTipo.disabled = true;
        DOM.btnSaveTipo.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Guardando...';

        try {
            const res = await fetch(url, {
                method: method,
                headers: getAuthHeaders(),
                body: JSON.stringify(payload)
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || 'Error al guardar el tipo de cliente');
            }

            if (tipoBsModal) tipoBsModal.hide();
            if (typeof window.showToast === 'function') {
                window.showToast(isEdit ? 'Tipo de cliente actualizado exitosamente' : 'Tipo de cliente registrado exitosamente', 'success');
            }
            await loadTiposCliente();
        } catch (err) {
            if (typeof window.showToast === 'function') window.showToast(err.message, 'danger');
        } finally {
            DOM.btnSaveTipo.disabled = false;
            DOM.btnSaveTipo.innerHTML = '<i class="bi bi-check-lg me-1"></i> Guardar';
        }
    }

    function openDeactivateTipoModal(id, name) {
        state.deactivateTargetTipoId = id;
        if (DOM.tipoDeactivateText) {
            DOM.tipoDeactivateText.textContent = `¿Confirmas que deseas desactivar el tipo de cliente "${name}"?`;
        }
        if (tipoDeactivateBsModal) tipoDeactivateBsModal.show();
    }

    async function handleDeactivateTipoConfirm() {
        if (!state.deactivateTargetTipoId) return;

        if (DOM.btnConfirmTipoDeactivate) {
            DOM.btnConfirmTipoDeactivate.disabled = true;
            DOM.btnConfirmTipoDeactivate.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Procesando...';
        }

        try {
            const res = await fetch(`/api/tipos-cliente/${state.deactivateTargetTipoId}`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || 'No se pudo desactivar el tipo de cliente');
            }

            if (tipoDeactivateBsModal) tipoDeactivateBsModal.hide();
            if (typeof window.showToast === 'function') {
                window.showToast('Tipo de cliente desactivado exitosamente', 'success');
            }
            await loadTiposCliente();
        } catch (err) {
            if (typeof window.showToast === 'function') window.showToast(err.message, 'danger');
        } finally {
            if (DOM.btnConfirmTipoDeactivate) {
                DOM.btnConfirmTipoDeactivate.disabled = false;
                DOM.btnConfirmTipoDeactivate.textContent = 'Desactivar';
            }
        }
    }

    async function handleActivateTipo(id) {
        try {
            const res = await fetch(`/api/tipos-cliente/${id}`, {
                method: 'PUT',
                headers: getAuthHeaders(),
                body: JSON.stringify({ estado: 'Activo' })
            });

            if (!res.ok) {
                const errData = await res.json().catch(() => ({}));
                throw new Error(errData.detail || 'No se pudo reactivar el tipo de cliente');
            }

            if (typeof window.showToast === 'function') {
                window.showToast('Tipo de cliente reactivado exitosamente', 'success');
            }
            await loadTiposCliente();
        } catch (err) {
            if (typeof window.showToast === 'function') window.showToast(err.message, 'danger');
        }
    }

})();
