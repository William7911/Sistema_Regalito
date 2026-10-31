// Curiosidades El Regalito - POS / Ventas Module Logic
(function () {
    'use strict';

    const PAGE_SIZE = 9;
    const WHOLESALE_MIN = 6;
    const CUSTOMER_CHANNEL = 'regalito-pos-cliente';
    const CUSTOMER_STATE_KEY = 'regalito_pos_customer_state';
    const TICKET_FORMAT_KEY = 'regalito_pos_ticket_format';
    const TICKET_CACHE_KEY = 'regalito_pos_ticket_cache_v1';
    const CHARGE_HTML = '<span class="d-flex align-items-center justify-content-center gap-3"><i class="bi bi-cash-coin fs-2"></i> <span class="fs-4 fw-black">COBRAR</span></span>';
    const SCANNER_MAX_GAP = 35;

    const state = {
        turno: null,
        sucursalId: null,
        catalog: [],
        cart: [],
        history: [],
        cliente: null,
        clienteId: 1,
        nitReceptor: 'CF',
        nombreReceptor: 'Consumidor Final',
        category: 'Todos',
        ticketFormat: readStoredTicketFormat(),
        ticket: null,
        lastSale: null,
        charging: false,
    };

    const DOM = {
        view: document.getElementById('pos-view'),
        turnBadge: document.getElementById('pos-turn-badge'),
        turnText: document.getElementById('pos-turn-text'),
        noShift: document.getElementById('pos-no-shift'),
        workspace: document.getElementById('pos-workspace'),
        search: document.getElementById('pos-search'),
        searchClear: document.getElementById('btn-pos-search-clear'),
        grid: document.getElementById('pos-products-grid'),
        gridEmpty: document.getElementById('pos-products-empty'),
        gridInfo: document.getElementById('pos-grid-info'),
        gridPage: document.getElementById('pos-grid-page'),
        gridPrev: document.getElementById('pos-grid-prev'),
        gridNext: document.getElementById('pos-grid-next'),
        gridPagination: document.getElementById('pos-grid-pagination'),
        categoryPills: document.getElementById('pos-category-pills'),
        cartEmpty: document.getElementById('pos-cart-empty'),
        cartList: document.getElementById('pos-cart-list'),
        cartCount: document.getElementById('pos-cart-count'),
        subtotal: document.getElementById('pos-subtotal'),
        discount: document.getElementById('pos-discount'),
        total: document.getElementById('pos-total'),
        cashReceived: document.getElementById('pos-cash-received'),
        transferAmount: document.getElementById('pos-transfer-amount'),
        transferWrap: document.getElementById('pos-transfer-wrap'),
        btnToggleTransfer: document.getElementById('btn-pos-toggle-transfer'),
        btnRemoveTransfer: document.getElementById('btn-pos-remove-transfer'),
        transferToggleText: document.getElementById('pos-transfer-toggle-text'),
        received: document.getElementById('pos-received'),
        change: document.getElementById('pos-change'),
        btnCharge: document.getElementById('btn-pos-charge'),
        btnClear: document.getElementById('btn-pos-clear'),
        clientNit: document.getElementById('pos-client-nit'),
        clientBadge: document.getElementById('pos-client-badge'),
        btnSearchClient: document.getElementById('btn-pos-search-client'),
        btnCustomerScreen: document.getElementById('btn-pos-customer-screen'),
        btnScanner: document.getElementById('btn-pos-scanner'),
        scannerModal: document.getElementById('pos-scanner-modal'),
        scannerVideo: document.getElementById('pos-scanner-video'),
        scannerStatus: document.getElementById('pos-scanner-status'),
        scannerTorch: document.getElementById('btn-pos-scanner-torch'),
        scannerSwitch: document.getElementById('btn-pos-scanner-switch'),
        scannerAlert: document.getElementById('pos-scanner-alert'),
        scannerManualInput: document.getElementById('pos-scanner-manual-input'),
        scannerManualAdd: document.getElementById('btn-pos-scanner-manual-add'),
        btnHistory: document.getElementById('btn-pos-history'),
        historyModal: document.getElementById('pos-history-modal'),
        historyBody: document.getElementById('pos-history-body'),
        historyEmpty: document.getElementById('pos-history-empty'),
        btnReloadHistory: document.getElementById('btn-pos-reload-history'),
        ticketModal: document.getElementById('pos-ticket-modal'),
        ticketSubtitle: document.getElementById('ticket-modal-subtitle'),
        ticketPreview: document.getElementById('pos-ticket-preview'),
        ticketPrintAreaLabel: document.getElementById('ticket-print-area-label'),
        ticketFormat80: document.getElementById('ticket-format-80'),
        ticketFormat58: document.getElementById('ticket-format-58'),
        btnTicketPrint: document.getElementById('btn-ticket-print'),
        btnTicketNewSale: document.getElementById('btn-ticket-new-sale'),
        printArea: document.getElementById('pos-ticket-print-area'),
        pageStyle: document.getElementById('pos-ticket-page-style'),
    };

    let page = 1;
    let ticketModal = null;
    let historyModal = null;
    let scannerModalInstance = null;
    let cameraStream = null;
    let barcodeDetector = null;
    let scanInterval = null;
    let lastScannedCode = null;
    let lastScanTime = 0;
    let currentFacingMode = 'environment';
    let torchActive = false;
    let audioCtx = null;
    let globalScanBuffer = '';
    let lastGlobalKeyTime = 0;
    let customerChannel = null;
    let customerWindow = null;
    let lastSaleTimer = null;
    const scanner = { lastKeyAt: 0, gaps: [] };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    function init() {
        if (typeof bootstrap !== 'undefined') {
            if (DOM.ticketModal) ticketModal = new bootstrap.Modal(DOM.ticketModal);
            if (DOM.historyModal) historyModal = new bootstrap.Modal(DOM.historyModal);
            if (DOM.scannerModal) {
                scannerModalInstance = new bootstrap.Modal(DOM.scannerModal);
                DOM.scannerModal.addEventListener('shown.bs.modal', () => {
                    startCameraScanner();
                    if (DOM.scannerManualInput) setTimeout(() => DOM.scannerManualInput.focus(), 300);
                });
                DOM.scannerModal.addEventListener('hidden.bs.modal', stopCameraScanner);
            }
        }
        setupEvents();
        initCustomerChannel();
        updateTicketFormatUI();
        toggleSearchClear();
        syncCustomerScreen();
    }

    function setupEvents() {
        if (DOM.search) {
            DOM.search.addEventListener('input', () => {
                page = 1;
                toggleSearchClear();
                renderGrid();
            });
            DOM.search.addEventListener('keydown', (event) => {
                trackScannerKey(event);
                if (event.key === 'Escape') {
                    event.preventDefault();
                    clearSearch();
                    return;
                }
                if (event.key !== 'Enter') return;
                event.preventDefault();
                handleSearchEnter();
            });
            DOM.search.addEventListener('blur', () => {
                scanner.lastKeyAt = 0;
                scanner.gaps = [];
            });
        }

        if (DOM.searchClear) {
            DOM.searchClear.addEventListener('click', clearSearch);
        }
        if (DOM.gridPrev) {
            DOM.gridPrev.addEventListener('click', () => {
                if (page > 1) {
                    page -= 1;
                    renderGrid();
                }
            });
        }
        if (DOM.gridNext) {
            DOM.gridNext.addEventListener('click', () => {
                const totalPages = Math.ceil(filteredCatalog().length / PAGE_SIZE) || 1;
                if (page < totalPages) {
                    page += 1;
                    renderGrid();
                }
            });
        }

        if (DOM.categoryPills) {
            DOM.categoryPills.addEventListener('click', (event) => {
                const button = event.target.closest('button[data-category]');
                if (!button) return;
                state.category = button.dataset.category || 'Todos';
                page = 1;
                renderCategoryPills();
                renderGrid();
            });
        }

        if (DOM.grid) {
            DOM.grid.addEventListener('click', (event) => {
                const card = event.target.closest('[data-variante]');
                if (!card) return;
                addToCart(Number(card.dataset.variante));
            });
            DOM.grid.addEventListener('keydown', (event) => {
                if (event.key !== 'Enter' && event.key !== ' ') return;
                const card = event.target.closest('[data-variante]');
                if (!card) return;
                event.preventDefault();
                addToCart(Number(card.dataset.variante));
            });
        }

        if (DOM.cartList) {
            DOM.cartList.addEventListener('click', (event) => {
                const button = event.target.closest('button[data-action]');
                if (!button) return;
                const row = button.closest('[data-variante]');
                if (!row) return;
                const id = Number(row.dataset.variante);
                const action = button.dataset.action;
                const item = findCart(id);
                if (!item) return;
                if (action === 'inc') addToCart(id, 1);
                if (action === 'dec') setQty(id, item.cantidad - 1);
                if (action === 'remove') removeFromCart(id);
            });
            DOM.cartList.addEventListener('change', (event) => {
                const input = event.target.closest('input[data-qty]');
                if (!input) return;
                const row = input.closest('[data-variante]');
                if (!row) return;
                setQty(Number(row.dataset.variante), parseInt(input.value, 10));
            });
        }

        if (DOM.cashReceived) {
            DOM.cashReceived.addEventListener('input', renderTotals);
            DOM.cashReceived.addEventListener('focus', () => DOM.cashReceived.select());
        }
        if (DOM.transferAmount) {
            DOM.transferAmount.addEventListener('input', renderTotals);
        }
        if (DOM.btnToggleTransfer) {
            DOM.btnToggleTransfer.addEventListener('click', () => setTransferVisible(true, true));
        }
        if (DOM.btnRemoveTransfer) {
            DOM.btnRemoveTransfer.addEventListener('click', () => setTransferVisible(false, true));
        }

        document.querySelectorAll('.pos-cash-chip').forEach((button) => {
            button.addEventListener('click', () => applyQuickCash(button.dataset.cash));
        });

        if (DOM.btnClear) {
            DOM.btnClear.addEventListener('click', () => {
                state.cart = [];
                if (DOM.cashReceived) DOM.cashReceived.value = '';
                setTransferVisible(false, false);
                renderCart();
            });
        }
        if (DOM.btnCharge) {
            DOM.btnCharge.addEventListener('click', cobrar);
        }

        if (DOM.btnSearchClient) {
            DOM.btnSearchClient.addEventListener('click', searchClientByNit);
        }
        if (DOM.clientNit) {
            DOM.clientNit.addEventListener('keydown', (event) => {
                if (event.key !== 'Enter') return;
                event.preventDefault();
                searchClientByNit();
            });
            DOM.clientNit.addEventListener('focus', () => DOM.clientNit.select());
            DOM.clientNit.addEventListener('blur', () => {
                if (!DOM.clientNit.value.trim()) setClienteCF();
            });
        }

        if (DOM.btnHistory) {
            DOM.btnHistory.addEventListener('click', openHistoryModal);
        }
        if (DOM.btnReloadHistory) {
            DOM.btnReloadHistory.addEventListener('click', loadHistory);
        }
        if (DOM.historyBody) {
            DOM.historyBody.addEventListener('click', (event) => {
                const button = event.target.closest('button[data-history-action]');
                if (!button) return;
                const id = Number(button.dataset.id);
                const action = button.dataset.historyAction;
                openHistoryTicket(id, action === 'print');
            });
        }

        [DOM.ticketFormat80, DOM.ticketFormat58].forEach((radio) => {
            if (!radio) return;
            radio.addEventListener('change', (event) => {
                if (event.target.checked) applyTicketFormat(event.target.value);
            });
        });
        if (DOM.btnTicketPrint) {
            DOM.btnTicketPrint.addEventListener('click', printTicket);
        }
        if (DOM.btnTicketNewSale) {
            DOM.btnTicketNewSale.addEventListener('click', resetForNewSale);
        }
        if (DOM.btnCustomerScreen) {
            DOM.btnCustomerScreen.addEventListener('click', openCustomerScreen);
        }

        document.addEventListener('keydown', (event) => {
            if (!isPosVisible()) return;
            if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'enter') {
                if (DOM.btnCharge && !DOM.btnCharge.disabled && !document.querySelector('.modal.show')) {
                    event.preventDefault();
                    cobrar();
                }
                return;
            }
            if (event.key === 'F12') {
                if (DOM.btnCharge && !DOM.btnCharge.disabled && !document.querySelector('.modal.show')) {
                    event.preventDefault();
                    cobrar();
                }
                return;
            }
            if (event.key === 'F4') {
                event.preventDefault();
                openHistoryModal();
                return;
            }
            if (event.key === 'F2') {
                event.preventDefault();
                if (DOM.search) {
                    DOM.search.focus();
                    DOM.search.select();
                }
                return;
            }
            if (event.key === '/' && !isTypingTarget(event.target)) {
                event.preventDefault();
                if (DOM.search) DOM.search.focus();
                return;
            }
            if (event.key === 'Escape' && !document.querySelector('.modal.show')) {
                if (DOM.search) DOM.search.focus();
            }
        });

        window.addEventListener('message', (event) => {
            if (event.data && event.data.type === 'request-state') syncCustomerScreen();
        });

        if (DOM.btnScanner) {
            DOM.btnScanner.addEventListener('click', () => {
                if (scannerModalInstance) scannerModalInstance.show();
            });
        }
        if (DOM.scannerManualAdd) {
            DOM.scannerManualAdd.addEventListener('click', handleManualScannerSubmit);
        }
        if (DOM.scannerManualInput) {
            DOM.scannerManualInput.addEventListener('keydown', (e) => {
                if (e.key === 'Enter') {
                    e.preventDefault();
                    handleManualScannerSubmit();
                }
            });
        }
        if (DOM.scannerTorch) {
            DOM.scannerTorch.addEventListener('click', toggleTorch);
        }
        if (DOM.scannerSwitch) {
            DOM.scannerSwitch.addEventListener('click', switchCamera);
        }

        // Listener global para lectores láser de código de barras (USB / Bluetooth)
        window.addEventListener('keydown', (event) => {
            if (!isPosVisible()) return;
            const active = document.activeElement;
            const tag = active ? active.tagName.toLowerCase() : '';
            const id = active ? active.id : '';
            if (tag === 'textarea' || (tag === 'input' && !['pos-search', 'pos-scanner-manual-input'].includes(id))) {
                return;
            }

            const now = performance.now();
            const gap = now - lastGlobalKeyTime;
            lastGlobalKeyTime = now;

            if (event.key === 'Enter') {
                if (globalScanBuffer.length >= 4) {
                    event.preventDefault();
                    const code = globalScanBuffer;
                    globalScanBuffer = '';
                    handleBarcodeDetected(code);
                    if (DOM.search) DOM.search.value = '';
                    return;
                }
                globalScanBuffer = '';
            } else if (event.key.length === 1) {
                if (gap < 60 || globalScanBuffer.length === 0) {
                    globalScanBuffer += event.key;
                } else {
                    globalScanBuffer = event.key;
                }
            }
        });
    }

    function playScanBeep(success) {
        try {
            if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            if (audioCtx.state === 'suspended') audioCtx.resume();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            if (success) {
                osc.frequency.setValueAtTime(1200, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(1800, audioCtx.currentTime + 0.08);
                gain.gain.setValueAtTime(0.2, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.12);
                osc.start(audioCtx.currentTime);
                osc.stop(audioCtx.currentTime + 0.12);
            } else {
                osc.frequency.setValueAtTime(320, audioCtx.currentTime);
                gain.gain.setValueAtTime(0.25, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
                osc.start(audioCtx.currentTime);
                osc.stop(audioCtx.currentTime + 0.2);
            }
        } catch (_) {}
    }

    async function handleBarcodeDetected(code) {
        const clean = String(code || '').trim();
        if (!clean) return;

        const now = Date.now();
        if (clean === lastScannedCode && (now - lastScanTime) < 1300) return;
        lastScannedCode = clean;
        lastScanTime = now;

        const reticle = document.querySelector('.pos-scanner-reticle');
        if (reticle) {
            reticle.classList.add('scan-success');
            setTimeout(() => reticle.classList.remove('scan-success'), 500);
        }

        // Buscar en catálogo local
        let item = state.catalog.find(entry => String(entry.codigo_barras || '').trim() === clean);

        // Si no está en catálogo local, buscar en backend por código de barras
        if (!item) {
            try {
                const token = (typeof getToken === 'function') ? getToken() : (localStorage.getItem('token') || localStorage.getItem('access_token'));
                const res = await fetch(`/api/productos/barcode/${encodeURIComponent(clean)}`, {
                    headers: token ? { 'Authorization': `Bearer ${token}` } : {}
                });
                if (res.ok) {
                    const prod = await res.json();
                    if (prod && prod.variantes && prod.variantes.length > 0) {
                        const matchedVar = prod.variantes.find(v => String(v.codigo_barras || '').trim() === clean) || prod.variantes[0];
                        const inv = (matchedVar.inventarios && matchedVar.inventarios[0]) ? matchedVar.inventarios[0] : null;
                        item = {
                            id_producto: prod.id_producto,
                            id_variante: matchedVar.id_variante,
                            nombre: prod.nombre,
                            precio: Number(matchedVar.precio_detalle),
                            precio_mayoreo: Number(matchedVar.precio_mayoreo),
                            stock: inv ? Number(inv.stock_actual) : 999,
                            codigo_barras: clean,
                            categoria: prod.subcategoria ? (prod.subcategoria.categoria ? prod.subcategoria.categoria.nombre : prod.subcategoria.nombre) : 'General'
                        };
                        state.catalog.push(item);
                    }
                }
            } catch (_) {}
        }

        if (item) {
            playScanBeep(true);
            addToCart(item.id_variante, 1);
            showScannerBanner(`${item.nombre} agregado al carrito`, false);
            toast(`'${item.nombre}' agregado a la venta`, 'success');
        } else {
            playScanBeep(false);
            showScannerBanner(`Código '${clean}' no encontrado`, true);
            toast(`Código '${clean}' no encontrado en el sistema`, 'warning');
        }
    }

    function showScannerBanner(msg, isError) {
        if (!DOM.scannerAlert) return;
        DOM.scannerAlert.textContent = msg;
        DOM.scannerAlert.className = `pos-scanner-alert position-absolute bottom-0 start-0 w-100 p-2 text-center text-white small fw-bold ${isError ? 'error' : ''}`;
        DOM.scannerAlert.classList.remove('d-none');
        setTimeout(() => {
            if (DOM.scannerAlert) DOM.scannerAlert.classList.add('d-none');
        }, 2200);
    }

    async function startCameraScanner() {
        stopCameraScanner();
        if (!DOM.scannerVideo) return;

        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            if (DOM.scannerStatus) DOM.scannerStatus.textContent = 'Cámara no soportada en este navegador';
            return;
        }

        try {
            if (DOM.scannerStatus) DOM.scannerStatus.innerHTML = '<span class="spinner-grow spinner-grow-sm text-teal me-1"></span>Iniciando cámara...';
            const constraints = {
                video: {
                    facingMode: { ideal: currentFacingMode },
                    width: { ideal: 1280 },
                    height: { ideal: 720 }
                }
            };
            cameraStream = await navigator.mediaDevices.getUserMedia(constraints);
            DOM.scannerVideo.srcObject = cameraStream;
            await DOM.scannerVideo.play();

            if (DOM.scannerStatus) DOM.scannerStatus.textContent = 'Apunta al código de barras...';

            const track = cameraStream.getVideoTracks()[0];
            const capabilities = track && track.getCapabilities ? track.getCapabilities() : {};
            if (capabilities.torch && DOM.scannerTorch) {
                DOM.scannerTorch.classList.remove('d-none');
            }
            if (DOM.scannerSwitch) {
                DOM.scannerSwitch.classList.remove('d-none');
            }

            initBarcodeDetectionLoop();
        } catch (err) {
            console.warn('Error al iniciar cámara de escaneo:', err);
            if (DOM.scannerStatus) {
                DOM.scannerStatus.textContent = 'Permiso denegado o cámara no disponible';
            }
        }
    }

    function stopCameraScanner() {
        if (scanInterval) {
            clearInterval(scanInterval);
            scanInterval = null;
        }
        if (cameraStream) {
            cameraStream.getTracks().forEach(t => t.stop());
            cameraStream = null;
        }
        if (DOM.scannerVideo) {
            DOM.scannerVideo.srcObject = null;
        }
        torchActive = false;
        if (DOM.scannerTorch) {
            DOM.scannerTorch.classList.add('d-none');
            DOM.scannerTorch.innerHTML = '<i class="bi bi-lightning-fill"></i>';
        }
    }

    async function toggleTorch() {
        if (!cameraStream) return;
        const track = cameraStream.getVideoTracks()[0];
        if (!track || !track.applyConstraints) return;
        try {
            torchActive = !torchActive;
            await track.applyConstraints({ advanced: [{ torch: torchActive }] });
            if (DOM.scannerTorch) {
                DOM.scannerTorch.innerHTML = torchActive ? '<i class="bi bi-lightning text-warning"></i>' : '<i class="bi bi-lightning-fill"></i>';
            }
        } catch (_) {}
    }

    async function switchCamera() {
        currentFacingMode = currentFacingMode === 'environment' ? 'user' : 'environment';
        await startCameraScanner();
    }

    function handleManualScannerSubmit() {
        if (!DOM.scannerManualInput) return;
        const code = DOM.scannerManualInput.value.trim();
        if (!code) return;
        DOM.scannerManualInput.value = '';
        handleBarcodeDetected(code);
        DOM.scannerManualInput.focus();
    }

    function initBarcodeDetectionLoop() {
        if ('BarcodeDetector' in window) {
            if (!barcodeDetector) {
                try {
                    barcodeDetector = new window.BarcodeDetector({
                        formats: ['ean_13', 'code_128', 'qr_code', 'upc_a', 'ean_8', 'code_39']
                    });
                } catch (_) {}
            }
        }

        if (scanInterval) clearInterval(scanInterval);

        scanInterval = setInterval(async () => {
            if (!DOM.scannerVideo || DOM.scannerVideo.readyState < 2) return;
            if (barcodeDetector) {
                try {
                    const barcodes = await barcodeDetector.detect(DOM.scannerVideo);
                    if (barcodes && barcodes.length > 0) {
                        handleBarcodeDetected(barcodes[0].rawValue);
                    }
                } catch (_) {}
            }
        }, 160);
    }

    function trackScannerKey(event) {
        if (event.key.length !== 1) return;
        const now = performance.now();
        if (scanner.lastKeyAt && now - scanner.lastKeyAt < 120) {
            scanner.gaps.push(now - scanner.lastKeyAt);
            if (scanner.gaps.length > 12) scanner.gaps.shift();
        } else {
            scanner.gaps = [];
        }
        scanner.lastKeyAt = now;
    }

    function looksLikeScanner() {
        if (scanner.gaps.length < 3) return false;
        const average = scanner.gaps.reduce((sum, gap) => sum + gap, 0) / scanner.gaps.length;
        return average <= SCANNER_MAX_GAP;
    }

    function handleSearchEnter() {
        const term = DOM.search.value.trim();
        if (!term) return;
        const scanned = looksLikeScanner();
        scanner.lastKeyAt = 0;
        scanner.gaps = [];

        const exact = state.catalog.find((item) => String(item.codigo_barras) === term);
        if (exact) {
            addToCart(exact.id_variante);
            clearSearch();
            return;
        }

        const matches = filteredCatalog().filter((item) => item.stock > 0);
        if (matches.length === 1) {
            addToCart(matches[0].id_variante);
            clearSearch();
            return;
        }
        if (scanned || /^\d{6,}$/.test(term)) {
            toast(`Código '${term}' no encontrado en esta sucursal.`, 'warning');
            if (DOM.search) DOM.search.select();
            return;
        }
        if (matches.length === 0) {
            toast(`No se encontraron productos para '${term}'.`, 'info');
        }
    }

    function toggleSearchClear() {
        if (!DOM.searchClear) return;
        DOM.searchClear.classList.toggle('d-none', !(DOM.search && DOM.search.value));
    }

    function clearSearch(focus) {
        if (DOM.search) DOM.search.value = '';
        if (DOM.searchClear) DOM.searchClear.classList.add('d-none');
        page = 1;
        renderGrid();
        if (focus !== false && DOM.search) DOM.search.focus();
    }

    function setTransferVisible(visible, focus) {
        if (!DOM.transferWrap) return;
        DOM.transferWrap.classList.toggle('d-none', !visible);
        if (DOM.btnToggleTransfer) DOM.btnToggleTransfer.classList.toggle('d-none', visible);
        if (!visible && DOM.transferAmount) DOM.transferAmount.value = '';
        renderTotals();
        if (visible && focus && DOM.transferAmount) {
            DOM.transferAmount.focus();
            DOM.transferAmount.select();
        }
    }

    function openHistoryModal() {
        if (!isPosVisible()) return;
        if (historyModal) historyModal.show();
        loadHistory();
    }

    function cashierName() {
        return localStorage.getItem('user_display_name')
            || localStorage.getItem('user_name')
            || 'Cajero';
    }

    function token() {
        return localStorage.getItem('jwt_token') || '';
    }

    async function apiGet(url) {
        const response = await fetch(url, { headers: { Authorization: `Bearer ${token()}` } });
        if (response.status === 401) {
            if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
            throw new Error('Sesión expirada');
        }
        if (!response.ok) {
            const detail = await readErrorDetail(response, 'Error en la petición');
            throw new Error(detail);
        }
        return response.json();
    }

    async function apiPost(url, payload) {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token()}`,
            },
            body: JSON.stringify(payload),
        });
        if (response.status === 401) {
            if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
            throw new Error('Sesión expirada');
        }
        if (!response.ok) {
            const fallback = response.status === 403
                ? 'No tienes permisos para esta operación'
                : 'Error al procesar la venta';
            const detail = await readErrorDetail(response, fallback);
            throw new Error(detail);
        }
        return response.json();
    }

    async function readErrorDetail(response, fallback) {
        try {
            const data = await response.json();
            if (typeof data.detail === 'string') return data.detail;
            if (Array.isArray(data.detail)) {
                return data.detail.map((item) => item.msg || 'Dato inválido').join(' · ');
            }
        } catch (_) {
            // Se conserva el mensaje genérico.
        }
        return fallback;
    }

    window.showPOSModule = async function () {
        const hasShift = await loadTurno();
        if (hasShift) {
            await Promise.all([loadProducts(), loadHistory()]);
        } else {
            state.catalog = [];
            state.history = [];
            renderCategoryPills();
            renderGrid();
            renderHistory();
        }
        syncCustomerScreen();
    };

    async function loadTurno() {
        try {
            const turno = await apiGet('/api/caja/estado-actual');
            state.turno = turno || null;
            if (!turno) {
                state.sucursalId = null;
                if (state.cart.length > 0) {
                    state.cart = [];
                    renderCart();
                }
                if (DOM.workspace) DOM.workspace.classList.add('d-none');
                if (DOM.noShift) DOM.noShift.classList.remove('d-none');
                if (DOM.turnText) DOM.turnText.textContent = 'Sin turno abierto';
                if (DOM.turnBadge) {
                    DOM.turnBadge.className = 'badge bg-warning-subtle text-warning px-3 py-2 rounded-pill';
                }
                return false;
            }

            state.sucursalId = turno.caja && turno.caja.id_sucursal
                ? turno.caja.id_sucursal
                : (turno.id_sucursal || null);
            const cajaDesc = turno.caja && turno.caja.descripcion
                ? turno.caja.descripcion
                : `Caja #${turno.id_caja}`;
            if (DOM.turnText) {
                DOM.turnText.textContent = `${cajaDesc} · Turno #${turno.id_turno} · Inicial ${fmtQ(turno.monto_apertura)}`;
            }
            if (DOM.turnBadge) {
                DOM.turnBadge.className = 'badge bg-success-subtle text-success px-3 py-2 rounded-pill';
            }
            if (DOM.noShift) DOM.noShift.classList.add('d-none');
            if (DOM.workspace) DOM.workspace.classList.remove('d-none');
            return true;
        } catch (error) {
            if (error.message === 'Sesión expirada') return false;
            state.turno = null;
            state.sucursalId = null;
            if (DOM.workspace) DOM.workspace.classList.add('d-none');
            if (DOM.turnText) DOM.turnText.textContent = 'Error al consultar turno';
            toast(error.message, 'danger');
            return false;
        }
    }

    async function loadProducts() {
        if (!state.sucursalId) return;
        try {
            const data = await apiGet('/api/productos?limit=500&is_active=true');
            const flat = [];
            (data.items || []).forEach((producto) => {
                const categoria = producto.subcategoria && producto.subcategoria.categoria
                    ? producto.subcategoria.categoria.nombre
                    : (producto.subcategoria ? producto.subcategoria.nombre : 'General');
                const subcategoria = producto.subcategoria ? producto.subcategoria.nombre : '';
                (producto.variantes || []).forEach((variante) => {
                    const inventario = (variante.inventarios || []).find(
                        (item) => Number(item.id_sucursal) === Number(state.sucursalId)
                    );
                    flat.push({
                        id_variante: Number(variante.id_variante),
                        id_producto: Number(producto.id_producto),
                        nombre: producto.nombre,
                        descripcion: producto.descripcion || '',
                        categoria: categoria || 'General',
                        subcategoria: subcategoria || '',
                        imagen_url: safeImageUrl(producto.imagen_url),
                        talla: variante.talla || '',
                        color: variante.color || '',
                        codigo_barras: variante.codigo_barras || '',
                        precio_detalle: Number(variante.precio_detalle || 0),
                        precio_mayoreo: Number(variante.precio_mayoreo || 0),
                        stock: inventario ? Number(inventario.stock_actual || 0) : 0,
                        stock_minimo: inventario ? Number(inventario.stock_minimo || 0) : 0,
                    });
                });
            });
            flat.sort((a, b) => {
                const categoryOrder = String(a.categoria).localeCompare(String(b.categoria), 'es');
                if (categoryOrder !== 0) return categoryOrder;
                const nameOrder = String(a.nombre).localeCompare(String(b.nombre), 'es');
                if (nameOrder !== 0) return nameOrder;
                return String(a.talla || a.color || '').localeCompare(String(b.talla || b.color || ''), 'es');
            });

            const previousCart = state.cart.length;
            const byId = new Map(flat.map((item) => [item.id_variante, item]));
            let removed = 0;
            let clamped = 0;
            state.cart = state.cart.map((item) => {
                const fresh = byId.get(item.id_variante);
                if (!fresh || fresh.stock <= 0) {
                    removed += 1;
                    return null;
                }
                if (item.cantidad > fresh.stock) clamped += 1;
                return { ...item, ...fresh, cantidad: Math.min(item.cantidad, fresh.stock) };
            }).filter(Boolean);

            state.catalog = flat;
            page = 1;
            renderCategoryPills();
            renderGrid();
            renderCart();

            if (previousCart > 0 && (removed > 0 || clamped > 0)) {
                const parts = [];
                if (removed > 0) parts.push(`${removed} producto(s) sin stock`);
                if (clamped > 0) parts.push(`${clamped} cantidad(es) ajustada(s)`);
                toast(`Catálogo actualizado: ${parts.join(' y ')}.`, 'warning');
            }
        } catch (error) {
            if (error.message === 'Sesión expirada') return;
            toast(`Error al cargar catálogo: ${error.message}`, 'danger');
        }
    }

    function categories() {
        const names = new Set(state.catalog.map((item) => item.categoria || 'General'));
        return Array.from(names).sort((a, b) => String(a).localeCompare(String(b), 'es'));
    }

    function renderCategoryPills() {
        if (!DOM.categoryPills) return;
        const list = categories();
        if (state.category !== 'Todos' && !list.includes(state.category)) {
            state.category = 'Todos';
        }
        const counts = new Map();
        state.catalog.forEach((item) => {
            const key = item.categoria || 'General';
            counts.set(key, (counts.get(key) || 0) + 1);
        });

        DOM.categoryPills.innerHTML = '';
        const options = [{ name: 'Todos', count: state.catalog.length }].concat(
            list.map((name) => ({ name, count: counts.get(name) || 0 }))
        );

        options.forEach((option) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = `pos-category-pill${state.category === option.name ? ' active' : ''}`;
            button.dataset.category = option.name;
            button.innerHTML = `${escapeHtml(option.name)}<span class="count">${option.count}</span>`;
            DOM.categoryPills.appendChild(button);
        });
    }

    function filteredCatalog() {
        const term = (DOM.search ? DOM.search.value : '').trim().toLowerCase();
        return state.catalog.filter((item) => {
            const matchesCategory = state.category === 'Todos' || item.categoria === state.category;
            if (!matchesCategory) return false;
            if (!term) return true;
            return String(item.nombre || '').toLowerCase().includes(term)
                || String(item.talla || '').toLowerCase().includes(term)
                || String(item.color || '').toLowerCase().includes(term)
                || String(item.codigo_barras || '').toLowerCase().includes(term)
                || String(item.categoria || '').toLowerCase().includes(term)
                || String(item.subcategoria || '').toLowerCase().includes(term);
        });
    }

    function renderGrid() {
        if (!DOM.grid) return;
        const items = filteredCatalog();
        const totalPages = Math.ceil(items.length / PAGE_SIZE) || 1;
        if (page > totalPages) page = totalPages;
        const start = (page - 1) * PAGE_SIZE;
        const pageItems = items.slice(start, start + PAGE_SIZE);

        DOM.grid.innerHTML = '';
        if (DOM.gridInfo) {
            const units = items.reduce((sum, item) => sum + Math.max(0, item.stock), 0);
            DOM.gridInfo.textContent = `${items.length} variante(s) · ${units} unidad(es)`;
        }
        if (DOM.gridPage) DOM.gridPage.textContent = `Página ${page} de ${totalPages}`;
        if (DOM.gridPrev) DOM.gridPrev.disabled = page === 1;
        if (DOM.gridNext) DOM.gridNext.disabled = page === totalPages;
        if (DOM.gridPagination) DOM.gridPagination.classList.toggle('d-none', items.length === 0);
        if (DOM.gridEmpty) {
            DOM.gridEmpty.classList.toggle('d-none', items.length > 0);
            const label = DOM.gridEmpty.querySelector('span');
            if (label) {
                label.textContent = (DOM.search && DOM.search.value.trim()) || state.category !== 'Todos'
                    ? 'No se encontraron productos con ese filtro'
                    : 'No hay productos disponibles en esta sucursal';
            }
        }

        pageItems.forEach((item) => {
            const column = document.createElement('div');
            column.className = 'col';
            const isOut = item.stock <= 0;
            const variant = [item.talla, item.color].filter(Boolean).join(' · ');
            const stock = stockPresentation(item);
            const image = item.imagen_url
                ? `<img class="pos-product-img" src="${escapeHtml(item.imagen_url)}" alt="${escapeHtml(item.nombre)}" loading="lazy">`
                : '';
            const wholesale = item.precio_mayoreo > 0
                ? `<div class="pos-product-wholesale"><i class="bi bi-tags-fill me-1"></i>Mayoreo ${fmtQ(item.precio_mayoreo)}</div>`
                : '';

            column.innerHTML = `
                <div class="card pos-product-card shadow-sm rounded-4 h-100 ${isOut ? 'is-out' : ''}"
                     data-variante="${item.id_variante}"
                     role="button"
                     tabindex="${isOut ? '-1' : '0'}"
                     aria-disabled="${isOut ? 'true' : 'false'}"
                     aria-label="${escapeHtml(isOut ? `${item.nombre} agotado` : `Agregar ${item.nombre}`)}">
                    <div class="pos-product-media">
                        ${image}
                        <div class="pos-product-placeholder">
                            <i class="bi ${categoryIcon(item.categoria)} pos-product-cat-hero-icon"></i>
                        </div>
                        <span class="pos-stock-badge ${stock.className}">${escapeHtml(stock.label)}</span>
                        <span class="pos-category-tag">${escapeHtml(item.categoria || 'General')}</span>
                    </div>
                    <div class="card-body p-3 d-flex flex-column justify-content-between">
                        <div>
                            <div class="pos-product-name" title="${escapeHtml(item.nombre)}">${escapeHtml(item.nombre)}</div>
                            <div class="pos-product-variant">${escapeHtml(variant || 'Sin variante')}</div>
                        </div>
                        <div class="mt-auto pt-2">
                            <div class="pos-product-price">${fmtQ(item.precio_detalle)}</div>
                            ${wholesale}
                        </div>
                    </div>
                </div>
            `;

            const img = column.querySelector('img');
            if (img) {
                img.addEventListener('error', () => img.remove());
            }
            DOM.grid.appendChild(column);
        });
    }

    function stockPresentation(item) {
        const stock = Number(item.stock || 0);
        if (stock <= 0) {
            return { className: 'pos-stock-out', label: 'Agotado' };
        }
        const minimum = Math.max(3, Number(item.stock_minimo || 0));
        if (stock <= minimum) {
            return { className: 'pos-stock-low', label: `Quedan ${stock}` };
        }
        return { className: 'pos-stock-ok', label: `${stock} disp.` };
    }

    function findCart(varianteId) {
        return state.cart.find((item) => Number(item.id_variante) === Number(varianteId));
    }

    function addToCart(varianteId, qty) {
        const item = state.catalog.find((entry) => Number(entry.id_variante) === Number(varianteId));
        if (!item) return;
        if (item.stock <= 0) {
            toast(`'${item.nombre}' está agotado en esta sucursal.`, 'warning');
            return;
        }
        const cantidad = Number(qty) > 0 ? Number(qty) : 1;
        const existing = findCart(varianteId);
        const current = existing ? Number(existing.cantidad) : 0;
        if (current + cantidad > item.stock) {
            toast(`Stock insuficiente para '${item.nombre}'. Disponible: ${item.stock}.`, 'danger');
            return;
        }
        if (existing) {
            existing.cantidad = current + cantidad;
        } else {
            state.cart.push({
                id_variante: item.id_variante,
                nombre: item.nombre,
                categoria: item.categoria,
                imagen_url: item.imagen_url,
                talla: item.talla,
                color: item.color,
                codigo_barras: item.codigo_barras,
                precio_detalle: item.precio_detalle,
                precio_mayoreo: item.precio_mayoreo,
                stock: item.stock,
                stock_minimo: item.stock_minimo,
                cantidad,
            });
        }
        renderCart();
    }

    function setQty(varianteId, cantidad) {
        const item = findCart(varianteId);
        if (!item) return;
        let next = Number.isFinite(cantidad) ? cantidad : 1;
        if (next <= 0) {
            removeFromCart(varianteId);
            return;
        }
        if (next > item.stock) {
            toast(`Stock insuficiente para '${item.nombre}'. Disponible: ${item.stock}.`, 'danger');
            next = item.stock;
        }
        item.cantidad = next;
        renderCart();
    }

    function removeFromCart(varianteId) {
        state.cart = state.cart.filter((item) => Number(item.id_variante) !== Number(varianteId));
        renderCart();
    }

    function renderCart() {
        if (!DOM.cartList) return;
        const hasItems = state.cart.length > 0;
        const units = state.cart.reduce((sum, item) => sum + Number(item.cantidad || 0), 0);

        if (DOM.cartEmpty) {
            DOM.cartEmpty.classList.toggle('d-none', hasItems);
            DOM.cartEmpty.style.setProperty('display', hasItems ? 'none' : 'flex', 'important');
        }
        if (DOM.cartList) {
            DOM.cartList.classList.toggle('d-none', !hasItems);
            DOM.cartList.style.setProperty('display', hasItems ? 'block' : 'none', 'important');
        }
        if (DOM.btnClear) DOM.btnClear.classList.toggle('d-none', !hasItems);
        if (DOM.cartCount) {
            DOM.cartCount.textContent = `${units} artículo${units === 1 ? '' : 's'}`;
        }

        DOM.cartList.innerHTML = '';
        state.cart.forEach((item) => {
            const unitPrice = effectivePrice(item);
            const lineTotal = round2(unitPrice * Number(item.cantidad));
            const gross = round2(Number(item.precio_detalle) * Number(item.cantidad));
            const saving = round2(gross - lineTotal);
            const variant = [item.talla, item.color].filter(Boolean).join(' · ');
            const mayoreo = saving > 0.009;

            const row = document.createElement('div');
            row.className = 'pos-cart-item';
            row.dataset.variante = item.id_variante;
            row.innerHTML = `
                <div class="pos-cart-col-info">
                    <div class="pos-cart-name text-truncate" title="${escapeHtml(item.nombre)}">${escapeHtml(item.nombre)}</div>
                    ${variant ? `<div class="pos-cart-meta text-truncate">${escapeHtml(variant)}</div>` : ''}
                    ${mayoreo ? '<div class="pos-cart-meta text-success"><i class="bi bi-tags-fill me-1"></i>Mayoreo</div>' : ''}
                </div>
                <div class="pos-cart-col-qty">
                    <div class="pos-qty" role="group" aria-label="Control de cantidad">
                        <button type="button" data-action="dec" title="Disminuir" aria-label="Disminuir"><i class="bi bi-dash-lg"></i></button>
                        <input type="number" data-qty value="${item.cantidad}" min="1" max="${item.stock}" inputmode="numeric" aria-label="Cantidad">
                        <button type="button" data-action="inc" title="Aumentar" aria-label="Aumentar"><i class="bi bi-plus-lg"></i></button>
                    </div>
                </div>
                <div class="pos-cart-col-price text-end">
                    <div class="pos-cart-line-total">${fmtQ(lineTotal)}</div>
                    ${saving > 0.009 ? `<div class="pos-cart-line-savings">Ahorro ${fmtQ(saving)}</div>` : ''}
                </div>
                <div class="pos-cart-col-action">
                    <button type="button" class="btn pos-cart-remove" data-action="remove" title="Eliminar del carrito" aria-label="Eliminar ${escapeHtml(item.nombre)}">
                        <i class="bi bi-trash3-fill"></i>
                    </button>
                </div>
            `;
            DOM.cartList.appendChild(row);
        });

        renderTotals();
    }

    function effectivePrice(item) {
        const detail = Number(item.precio_detalle || 0);
        const wholesale = Number(item.precio_mayoreo || 0) > 0 ? Number(item.precio_mayoreo) : detail;
        return (isWholesaleClient() || Number(item.cantidad) >= WHOLESALE_MIN) ? wholesale : detail;
    }

    function isWholesaleClient() {
        if (!state.cliente) return false;
        const typeName = state.cliente.tipo_cliente
            ? String(state.cliente.tipo_cliente.nombre || '').toUpperCase()
            : '';
        const typeId = Number(state.cliente.id_tipo_cliente || 0);
        return typeName.includes('MAYORISTA') || typeId === 2 || typeId === 3;
    }

    function cartTotals() {
        let subtotalBruto = 0;
        let totalVenta = 0;
        let articulos = 0;
        state.cart.forEach((item) => {
            const quantity = Number(item.cantidad || 0);
            subtotalBruto += Number(item.precio_detalle || 0) * quantity;
            totalVenta += effectivePrice(item) * quantity;
            articulos += quantity;
        });
        return {
            subtotalBruto: round2(subtotalBruto),
            descuento: round2(Math.max(0, subtotalBruto - totalVenta)),
            totalVenta: round2(totalVenta),
            articulos,
        };
    }

    function renderTotals() {
        const totals = cartTotals();
        const cash = round2(DOM.cashReceived ? DOM.cashReceived.value : 0);
        const transferVisible = DOM.transferWrap && !DOM.transferWrap.classList.contains('d-none');
        const transfer = transferVisible ? round2(DOM.transferAmount ? DOM.transferAmount.value : 0) : 0;
        const recibido = round2(cash + transfer);
        const cambio = totals.articulos > 0 ? Math.max(0, round2(recibido - totals.totalVenta)) : 0;

        if (DOM.subtotal) DOM.subtotal.textContent = fmtQ(totals.subtotalBruto);
        if (DOM.discount) DOM.discount.textContent = totals.descuento > 0 ? `- ${fmtQ(totals.descuento)}` : fmtQ(0);
        if (DOM.total) DOM.total.textContent = fmtQ(totals.totalVenta);
        if (DOM.received) DOM.received.textContent = fmtQ(recibido);
        if (DOM.change) DOM.change.textContent = fmtQ(cambio);

        const canCharge = totals.articulos > 0 && totals.totalVenta > 0 && recibido >= totals.totalVenta && !state.charging;
        if (DOM.btnCharge) DOM.btnCharge.disabled = !canCharge;

        syncCustomerScreen();
        return { cash, transfer, recibido, cambio, totalVenta: totals.totalVenta };
    }

    function applyQuickCash(value) {
        const totals = cartTotals();
        if (!DOM.cashReceived) return;
        if (value === 'exact') {
            const transferVisible = DOM.transferWrap && !DOM.transferWrap.classList.contains('d-none');
            const transfer = transferVisible ? round2(DOM.transferAmount ? DOM.transferAmount.value : 0) : 0;
            const cash = Math.max(0, round2(totals.totalVenta - transfer));
            DOM.cashReceived.value = cash > 0 ? cash.toFixed(2) : '';
        } else {
            DOM.cashReceived.value = Number(value || 0).toFixed(2);
        }
        renderTotals();
    }

    async function searchClientByNit() {
        const rawValue = (DOM.clientNit ? DOM.clientNit.value : 'CF').trim();
        const rawNit = rawValue.split('/')[0].trim().toUpperCase();
        if (!rawNit || rawNit === 'CF') {
            setClienteCF();
            renderCart();
            return;
        }

        try {
            const cliente = await apiGet(`/api/clientes/nit/${encodeURIComponent(rawNit)}`);
            if (cliente.estado === 'Inactivo') {
                toast(`El cliente '${cliente.nombre_comercial}' está inactivo y no puede realizar compras.`, 'danger');
                setClienteCF();
                renderCart();
                return;
            }

            state.cliente = cliente;
            state.clienteId = cliente.id_cliente;
            state.nitReceptor = cliente.nit;
            state.nombreReceptor = cliente.nombre_comercial;
            if (DOM.clientNit) {
                DOM.clientNit.value = `${cliente.nit} / ${cliente.nombre_comercial}`;
            }
            setClientUI(
                cliente.tipo_cliente ? cliente.tipo_cliente.nombre : 'Cliente',
                'pos-client-badge is-found'
            );
            toast(`Cliente '${cliente.nombre_comercial}' seleccionado.`, 'info');
            renderCart();
        } catch (error) {
            if (error.message === 'Sesión expirada') return;
            state.cliente = null;
            state.clienteId = null;
            state.nitReceptor = rawNit;
            state.nombreReceptor = `Cliente NIT ${rawNit}`;
            if (DOM.clientNit) DOM.clientNit.value = `${rawNit} / NIT no registrado`;
            setClientUI('NIT', 'pos-client-badge is-warning');
            toast(`NIT ${rawNit} no registrado. Se emitirá a ese NIT.`, 'warning');
            renderCart();
        }
    }

    function setClienteCF() {
        state.cliente = null;
        state.clienteId = 1;
        state.nitReceptor = 'CF';
        state.nombreReceptor = 'Consumidor Final';
        if (DOM.clientNit) DOM.clientNit.value = 'CF / Consumidor Final';
        setClientUI('CF', 'pos-client-badge');
    }

    function setClientUI(badgeText, badgeClass) {
        if (!DOM.clientBadge) return;
        DOM.clientBadge.textContent = badgeText;
        DOM.clientBadge.className = badgeClass;
    }

    async function cobrar() {
        if (state.charging) return;
        if (!state.turno) {
            toast('Debes abrir un turno de caja antes de cobrar.', 'warning');
            return;
        }
        if (state.cart.length === 0) return;

        const totals = cartTotals();
        const payment = renderTotals();
        if (payment.cash + payment.transfer < totals.totalVenta) {
            toast('El total recibido no cubre el monto de la venta.', 'warning');
            return;
        }

        const pagos = [];
        if (payment.cash > 0) pagos.push({ id_metodo_pago: 1, monto_recibido: payment.cash });
        if (payment.transfer > 0) pagos.push({ id_metodo_pago: 2, monto_recibido: payment.transfer });

        const payload = {
            id_sucursal: state.sucursalId,
            id_cliente: state.clienteId,
            nit_receptor: state.nitReceptor,
            nombre_receptor: state.nombreReceptor,
            items: state.cart.map((item) => ({ id_variante: item.id_variante, cantidad: item.cantidad })),
            pagos,
        };
        const clienteSnapshot = state.cliente
            ? { ...state.cliente }
            : {
                nit: state.nitReceptor,
                nombre_comercial: state.nombreReceptor,
                id_tipo_cliente: null,
                tipo_cliente: null,
            };

        setCharging(true);
        try {
            const venta = await apiPost('/api/ventas', payload);
            const ticketPayment = normalizePayment(payment, venta);
            cacheTicket(venta, ticketPayment, clienteSnapshot);
            state.lastSale = {
                id: venta.id_venta,
                total: Number(venta.total_venta || 0),
                at: Date.now(),
            };
            showTicket(venta, ticketPayment, clienteSnapshot);

            state.cart = [];
            if (DOM.cashReceived) DOM.cashReceived.value = '';
            setTransferVisible(false, false);
            setClienteCF();
            renderCart();
            scheduleLastSaleClear();

            await loadProducts();
            await loadHistory();
        } catch (error) {
            if (error.message !== 'Sesión expirada') toast(error.message, 'danger');
        } finally {
            setCharging(false);
        }
    }

    function setCharging(charging) {
        state.charging = charging;
        if (!DOM.btnCharge) return;
        if (charging) {
            DOM.btnCharge.disabled = true;
            DOM.btnCharge.innerHTML = '<span class="spinner-border" aria-hidden="true"></span> <span class="fs-4 fw-black ms-2">Procesando...</span>';
        } else {
            DOM.btnCharge.innerHTML = CHARGE_HTML;
            renderTotals();
        }
    }

    function normalizePayment(payment, venta) {
        const base = paymentFromVenta(venta);
        const cash = payment && Number.isFinite(Number(payment.cash)) ? Number(payment.cash) : base.cash;
        const transfer = payment && Number.isFinite(Number(payment.transfer)) ? Number(payment.transfer) : base.transfer;
        const other = payment && Number.isFinite(Number(payment.other)) ? Number(payment.other) : base.other;
        const cambio = payment && Number.isFinite(Number(payment.cambio)) ? Number(payment.cambio) : base.cambio;
        return {
            cash: round2(cash),
            transfer: round2(transfer),
            other: round2(other),
            cambio: round2(cambio),
        };
    }

    function paymentFromVenta(venta) {
        const pagos = venta.pagos || [];
        let cash = 0;
        let transfer = 0;
        let other = 0;
        pagos.forEach((pago) => {
            const amount = Number(pago.monto_recibido || 0);
            const method = Number(pago.id_metodo_pago);
            if (method === 1) cash += amount;
            else if (method === 2) transfer += amount;
            else other += amount;
        });
        let cambio = Number(venta.cambio || 0);
        if (!cambio) {
            cambio = pagos.reduce((sum, pago) => sum + Number(pago.vuelto_entregado || 0), 0);
        }
        if (!cambio) {
            cambio = Math.max(0, round2(cash + transfer + other - Number(venta.total_venta || 0)));
        }
        return {
            cash: round2(cash),
            transfer: round2(transfer),
            other: round2(other),
            cambio: round2(cambio),
        };
    }

    function showTicket(venta, payment, cliente) {
        state.ticket = {
            venta,
            payment: normalizePayment(payment, venta),
            cliente: cliente || null,
        };
        if (DOM.ticketSubtitle) {
            DOM.ticketSubtitle.textContent = `Venta #${venta.id_venta} · ${formatDate(venta.fecha_venta)}`;
        }
        updateTicketFormatUI();
        renderTicketPreview();
        if (ticketModal) ticketModal.show();
    }

    function buildTicketHtml(venta, payment) {
        const widthClass = state.ticketFormat === '58' ? 'ticket--58' : 'ticket--80';
        const cliente = state.ticket && state.ticket.cliente ? state.ticket.cliente : null;
        const clientId = Number(venta.id_cliente || 0);
        const nit = cliente && cliente.nit ? cliente.nit : (clientId === 1 ? 'CF' : '—');
        const nombre = cliente && cliente.nombre_comercial
            ? cliente.nombre_comercial
            : (clientId === 1 ? 'Consumidor Final' : `Cliente #${clientId || '—'}`);
        const items = (venta.detalles || []).map((detalle) => {
            const quantity = Number(detalle.cantidad || 0);
            const unit = Number(detalle.precio_unitario || 0);
            const subtotal = Number(detalle.subtotal || 0);
            const variant = [detalle.talla, detalle.color].filter(Boolean).join(' · ');
            const mayoreo = Number(detalle.descuento_item || 0) > 0;
            return `
                <div class="ticket-item">
                    <div class="ticket-item-name">${escapeHtml(detalle.nombre_producto || 'Producto')}</div>
                    ${variant ? `<div class="ticket-item-variant">${escapeHtml(variant)}</div>` : ''}
                    <div class="ticket-row"><span>${quantity} x ${fmtQ(unit)}</span><span>${fmtQ(subtotal)}</span></div>
                    ${mayoreo ? '<div class="ticket-item-tag">* MAYOREO</div>' : ''}
                </div>
            `;
        }).join('');

        const paymentRows = [];
        if (payment.cash > 0) paymentRows.push(ticketRow('PAGO EFECTIVO', fmtQ(payment.cash)));
        if (payment.transfer > 0) paymentRows.push(ticketRow('PAGO TRANSF.', fmtQ(payment.transfer)));
        if (payment.other > 0) paymentRows.push(ticketRow('PAGO OTRO', fmtQ(payment.other)));
        const totalRecibido = round2(payment.cash + payment.transfer + payment.other);
        const articulos = (venta.detalles || []).reduce((sum, detalle) => sum + Number(detalle.cantidad || 0), 0);

        return `
            <div class="ticket ${widthClass}">
                <div class="ticket-center">
                    <div class="ticket-business">Curiosidades El Regalito</div>
                    <div class="ticket-sub">Tienda de regalos · Guatemala</div>
                    <div class="ticket-sub">Precios en Quetzales (Q)</div>
                </div>
                <div class="ticket-sep"></div>
                <div class="ticket-row"><span>TICKET</span><span>#${venta.id_venta}</span></div>
                <div class="ticket-row"><span>FECHA</span><span>${escapeHtml(formatDate(venta.fecha_venta))}</span></div>
                <div class="ticket-row"><span>CAJERO</span><span>${escapeHtml(cashierName())}</span></div>
                <div class="ticket-row"><span>CLIENTE</span><span>${escapeHtml(nombre)}</span></div>
                <div class="ticket-row"><span>NIT</span><span>${escapeHtml(nit)}</span></div>
                <div class="ticket-sep"></div>
                <div class="ticket-cols"><span>CANT. x PRECIO</span><span>IMPORTE</span></div>
                ${items}
                <div class="ticket-sep"></div>
                <div class="ticket-row"><span>SUBTOTAL</span><span>${fmtQ(venta.subtotal)}</span></div>
                <div class="ticket-row"><span>DESCUENTO</span><span>- ${fmtQ(venta.descuento_total)}</span></div>
                <div class="ticket-row"><span>ARTÍCULOS</span><span>${articulos}</span></div>
                <div class="ticket-row ticket-total"><span>TOTAL</span><span>${fmtQ(venta.total_venta)}</span></div>
                ${paymentRows.join('')}
                <div class="ticket-row"><span>RECIBIDO</span><span>${fmtQ(totalRecibido)}</span></div>
                <div class="ticket-row ticket-change"><span>CAMBIO</span><span>${fmtQ(payment.cambio)}</span></div>
                <div class="ticket-sep"></div>
                <div class="ticket-center ticket-thanks">¡Gracias por su compra!</div>
                <div class="ticket-center ticket-foot">Conserve este ticket · Vuelva pronto</div>
            </div>
        `;
    }

    function ticketRow(label, value) {
        return `<div class="ticket-row"><span>${escapeHtml(label)}</span><span>${escapeHtml(value)}</span></div>`;
    }

    function renderTicketPreview() {
        if (!state.ticket) return;
        const html = buildTicketHtml(state.ticket.venta, state.ticket.payment);
        if (DOM.ticketPreview) DOM.ticketPreview.innerHTML = html;
        if (DOM.printArea) DOM.printArea.innerHTML = html;
    }

    function updateTicketFormatUI() {
        if (DOM.ticketFormat80) DOM.ticketFormat80.checked = state.ticketFormat === '80';
        if (DOM.ticketFormat58) DOM.ticketFormat58.checked = state.ticketFormat === '58';
        if (DOM.ticketPrintAreaLabel) {
            DOM.ticketPrintAreaLabel.textContent = state.ticketFormat === '58' ? '48 mm' : '72 mm';
        }
        if (DOM.pageStyle) {
            DOM.pageStyle.textContent = `@page { size: ${state.ticketFormat}mm auto; margin: 0; }`;
        }
    }

    function applyTicketFormat(format) {
        state.ticketFormat = format === '58' ? '58' : '80';
        try {
            localStorage.setItem(TICKET_FORMAT_KEY, state.ticketFormat);
        } catch (_) {
            // Sin persistencia si el navegador bloquea localStorage.
        }
        updateTicketFormatUI();
        if (state.ticket) renderTicketPreview();
    }

    function printTicket() {
        if (!state.ticket) {
            toast('No hay un ticket listo para imprimir.', 'warning');
            return;
        }
        renderTicketPreview();
        document.body.classList.add('pos-printing');

        // Nombre de archivo único para guardar como PDF (evita nombres repetidos)
        const idVenta = state.ticket.venta ? state.ticket.venta.id_venta : Date.now();
        const fechaStr = state.ticket.venta && state.ticket.venta.fecha_venta
            ? new Date(state.ticket.venta.fecha_venta).toLocaleDateString('es-GT').replace(/\//g, '-')
            : new Date().toLocaleDateString('es-GT').replace(/\//g, '-');
        const prevTitle = document.title;
        document.title = `Ticket-Venta-${idVenta}-${fechaStr}`;

        const cleanup = () => {
            document.title = prevTitle;
            document.body.classList.remove('pos-printing');
            window.removeEventListener('afterprint', cleanup);
        };
        window.addEventListener('afterprint', cleanup);
        setTimeout(() => {
            try {
                window.print();
            } finally {
                setTimeout(cleanup, 1000);
            }
        }, 80);
    }

    function resetForNewSale() {
        state.cart = [];
        if (DOM.cashReceived) DOM.cashReceived.value = '';
        setTransferVisible(false, false);
        setClienteCF();
        renderCart();
        clearSearch();
    }

    function openHistoryTicket(id, printAfter) {
        const venta = state.history.find((item) => Number(item.id_venta) === Number(id));
        if (!venta) return;
        const cache = readTicketCache();
        const cached = cache[id];
        const ticketSale = cached && cached.venta ? cached.venta : venta;
        const payment = cached && cached.payment ? cached.payment : paymentFromVenta(ticketSale);
        const cliente = cached ? cached.cliente : null;
        const show = () => {
            showTicket(ticketSale, payment, cliente);
            if (printAfter) setTimeout(printTicket, 450);
        };
        if (DOM.historyModal && DOM.historyModal.classList.contains('show') && historyModal) {
            DOM.historyModal.addEventListener('hidden.bs.modal', show, { once: true });
            historyModal.hide();
        } else {
            show();
        }
    }

    async function loadHistory() {
        if (!DOM.historyBody || !state.turno) return;
        try {
            const data = await apiGet(`/api/ventas?id_turno=${state.turno.id_turno}&limit=50`);
            state.history = data.items || [];
            renderHistory();
        } catch (error) {
            if (error.message === 'Sesión expirada') return;
            toast(`Error al cargar historial: ${error.message}`, 'danger');
        }
    }

    function renderHistory() {
        if (!DOM.historyBody) return;
        DOM.historyBody.innerHTML = '';
        const ventas = state.history || [];
        if (DOM.historyEmpty) DOM.historyEmpty.classList.toggle('d-none', ventas.length > 0);

        ventas.forEach((venta) => {
            const articulos = (venta.detalles || []).reduce(
                (sum, detalle) => sum + Number(detalle.cantidad || 0),
                0
            );
            const estadoClass = venta.estado === 'Completada'
                ? 'bg-success-subtle text-success'
                : (venta.estado === 'Anulada' ? 'bg-danger-subtle text-danger' : 'bg-secondary-subtle text-secondary');
            const row = document.createElement('tr');
            row.innerHTML = `
                <td class="fw-semibold small">#${venta.id_venta}</td>
                <td class="small">${escapeHtml(formatDate(venta.fecha_venta))}</td>
                <td class="text-end small">${fmtQ(venta.subtotal)}</td>
                <td class="text-end small text-success">- ${fmtQ(venta.descuento_total)}</td>
                <td class="text-end small fw-bold">${fmtQ(venta.total_venta)}</td>
                <td class="text-center small">${articulos}</td>
                <td><span class="badge ${estadoClass}">${escapeHtml(venta.estado)}</span></td>
                <td class="text-center">
                    <div class="btn-group btn-group-sm" role="group" aria-label="Acciones de venta">
                        <button type="button" class="btn btn-outline-teal" data-history-action="view" data-id="${venta.id_venta}" title="Ver detalle">
                            <i class="bi bi-eye"></i> Detalle
                        </button>
                        <button type="button" class="btn btn-outline-secondary" data-history-action="print" data-id="${venta.id_venta}" title="Reimprimir ticket">
                            <i class="bi bi-printer"></i>
                        </button>
                    </div>
                </td>
            `;
            DOM.historyBody.appendChild(row);
        });
    }

    function syncCustomerScreen() {
        if (!state.lastSale || Date.now() - state.lastSale.at > 20000) {
            if (state.lastSale) state.lastSale = null;
        }
        const totals = cartTotals();
        const payload = {
            type: 'pos-state',
            updatedAt: Date.now(),
            status: state.turno ? 'open' : 'no-shift',
            turno: state.turno
                ? {
                    id: state.turno.id_turno,
                    caja: state.turno.caja ? state.turno.caja.descripcion : `Caja #${state.turno.id_caja}`,
                }
                : null,
            cliente: {
                nit: state.nitReceptor,
                nombre: state.nombreReceptor,
                mayorista: isWholesaleClient(),
            },
            cart: state.cart.map((item) => {
                const unitPrice = effectivePrice(item);
                const lineTotal = round2(unitPrice * Number(item.cantidad));
                const gross = round2(Number(item.precio_detalle) * Number(item.cantidad));
                return {
                    nombre: item.nombre,
                    variante: [item.talla, item.color].filter(Boolean).join(' · '),
                    cantidad: Number(item.cantidad),
                    precio_unitario: round2(unitPrice),
                    subtotal: lineTotal,
                    ahorro: round2(gross - lineTotal),
                };
            }),
            totals: {
                subtotal: totals.subtotalBruto,
                descuento: totals.descuento,
                total: totals.totalVenta,
                articulos: totals.articulos,
            },
            lastSale: state.lastSale,
        };

        try {
            localStorage.setItem(CUSTOMER_STATE_KEY, JSON.stringify(payload));
        } catch (_) {
            // Sin persistencia si el navegador bloquea localStorage.
        }
        if (customerChannel) {
            customerChannel.postMessage({ type: 'pos-state', payload });
        }
        if (customerWindow && !customerWindow.closed) {
            customerWindow.postMessage({ type: 'pos-state', payload }, '*');
        }
    }

    function initCustomerChannel() {
        if (!('BroadcastChannel' in window)) return;
        customerChannel = new BroadcastChannel(CUSTOMER_CHANNEL);
        customerChannel.addEventListener('message', (event) => {
            if (event.data && event.data.type === 'request-state') syncCustomerScreen();
        });
    }

    function openCustomerScreen() {
        customerWindow = window.open(
            'cliente.html',
            'regalito-pantalla-cliente',
            'width=1024,height=720,menubar=no,toolbar=no,location=no,status=no'
        );
        if (!customerWindow) {
            toast('Permite las ventanas emergentes para abrir la pantalla del cliente.', 'warning');
            return;
        }
        customerWindow.focus();
        setTimeout(syncCustomerScreen, 400);
    }

    function scheduleLastSaleClear() {
        if (lastSaleTimer) clearTimeout(lastSaleTimer);
        lastSaleTimer = setTimeout(() => {
            state.lastSale = null;
            syncCustomerScreen();
        }, 20000);
    }

    function readStoredTicketFormat() {
        try {
            return localStorage.getItem(TICKET_FORMAT_KEY) === '58' ? '58' : '80';
        } catch (_) {
            return '80';
        }
    }

    function readTicketCache() {
        try {
            const raw = localStorage.getItem(TICKET_CACHE_KEY);
            const parsed = raw ? JSON.parse(raw) : {};
            return parsed && typeof parsed === 'object' ? parsed : {};
        } catch (_) {
            return {};
        }
    }

    function cacheTicket(venta, payment, cliente) {
        try {
            const cache = readTicketCache();
            cache[venta.id_venta] = {
                venta,
                payment,
                cliente: cliente || null,
                savedAt: Date.now(),
            };
            const entries = Object.entries(cache)
                .sort((a, b) => Number(b[1].savedAt || 0) - Number(a[1].savedAt || 0))
                .slice(0, 40);
            localStorage.setItem(TICKET_CACHE_KEY, JSON.stringify(Object.fromEntries(entries)));
        } catch (_) {
            // El ticket sigue disponible en memoria para imprimir.
        }
    }

    function getInitials(name) {
        const parts = String(name || '')
            .trim()
            .split(/\s+/)
            .filter(Boolean);
        if (parts.length === 0) return 'RG';
        if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
        return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
    }

    function categoryIcon(category) {
        const value = String(category || '').toLowerCase();
        if (value.includes('cristal') || value.includes('vaso') || value.includes('florero') || value.includes('copa') || value.includes('vidrio')) return 'bi-cup-straw';
        if (value.includes('ropa') || value.includes('vestid') || value.includes('pantalon') || value.includes('camis') || value.includes('blusa') || value.includes('bebé') || value.includes('bebe')) return 'bi-bag-heart-fill';
        if (value.includes('juguete') || value.includes('muñeca') || value.includes('muneca') || value.includes('juego') || value.includes('peluche') || value.includes('carro')) return 'bi-controller';
        if (value.includes('hogar') || value.includes('deco') || value.includes('cuadro') || value.includes('adorno')) return 'bi-house-heart-fill';
        if (value.includes('accesorio') || value.includes('joya') || value.includes('reloj')) return 'bi-gem';
        if (value.includes('papeleria') || value.includes('escolar') || value.includes('util')) return 'bi-pencil-square';
        return 'bi-gift-fill';
    }

    function safeImageUrl(value) {
        const url = String(value || '').trim();
        if (!url) return '';
        if (/^(https?:|data:image\/|\/|\.\/|\.\.\/)/i.test(url)) return url;
        if (/^[\w\-./]+\.(png|jpe?g|webp|gif|svg)$/i.test(url)) return url;
        return '';
    }

    function escapeHtml(value) {
        return String(value == null ? '' : value).replace(/[&<>"']/g, (character) => {
            const map = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#39;',
            };
            return map[character];
        });
    }

    function fmtQ(value) {
        const number = Number(value || 0);
        return `Q ${number.toFixed(2)}`;
    }

    function round2(value) {
        return Math.round((Number(value) || 0) * 100) / 100;
    }

    function formatDate(value) {
        if (!value) return '—';
        const date = new Date(value);
        if (Number.isNaN(date.getTime())) return String(value);
        return date.toLocaleString('es-GT', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
        });
    }

    function isPosVisible() {
        return DOM.view && !DOM.view.classList.contains('d-none');
    }

    function isTypingTarget(target) {
        if (!target) return false;
        const tag = String(target.tagName || '').toLowerCase();
        return tag === 'input' || tag === 'textarea' || tag === 'select' || target.isContentEditable;
    }

    function toast(message, type) {
        if (typeof window.showToast === 'function') {
            window.showToast(message, type || 'info');
        }
    }
})();
