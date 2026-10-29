// ============================================================================
// Módulo de Caja - Tienda el Regalito POS
// Gestión de Apertura, Cierre de Turnos y Arqueo de Efectivo
// Patrón defensivo: modales estáticos, validación 422 inline, dirty check,
// ordenamiento dinámico, paginación reactiva, filtros de fecha y toasts.
// Cero alert() o confirm() nativos.
// ============================================================================

const CASH_API = '/api/caja';

// Denominaciones oficiales de Guatemala para la calculadora de arqueo accesible
const GT_BILL_DENOMINATIONS = [
    { valor: 200, label: 'Billetes de Q200' },
    { valor: 100, label: 'Billetes de Q100' },
    { valor: 50,  label: 'Billetes de Q50' },
    { valor: 20,  label: 'Billetes de Q20' },
    { valor: 10,  label: 'Billetes de Q10' },
    { valor: 5,   label: 'Billetes de Q5' },
    { valor: 1,   label: 'Billetes de Q1' },
];

let activeExpectedCash = 0;

// Estado local reactivo
let currentTurno = null;
let cashHistoryState = {
    page: 1,
    pageSize: 10,
    total: 0,
    sortBy: 'id_turno',
    sortDir: 'desc',
};

// Cálculo centralizado de Efectivo Esperado: Monto Inicial + Ventas Efectivo + Entradas - Salidas
function computeExpectedCash(turno) {
    if (!turno) return 0;
    const inicial = Number(turno.monto_apertura || 0);
    const ventas = Number(turno.ventas_efectivo != null ? turno.ventas_efectivo : (turno.total_ventas_efectivo != null ? turno.total_ventas_efectivo : 0));
    const entradas = Number(turno.entradas_efectivo || 0);
    const salidas = Number(turno.salidas_efectivo || 0);
    if (turno.efectivo_esperado != null) {
        return Number(turno.efectivo_esperado);
    }
    return Math.max(0, inicial + ventas + entradas - salidas);
}

// ---------------------------------------------------------------------------
// Helpers generales y de autenticación
// ---------------------------------------------------------------------------

function authHeaders() {
    const token = localStorage.getItem('jwt_token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
    };
}

function getModal(id) {
    const el = document.getElementById(id);
    return el && window.bootstrap ? bootstrap.Modal.getOrCreateInstance(el) : null;
}

function formatCurrency(value) {
    if (value === null || value === undefined || value === '') return '-';
    const num = Number(value);
    if (isNaN(num)) return '-';
    return `Q ${num.toFixed(2)}`;
}

function formatDateTime(value) {
    if (!value) return '-';
    const d = new Date(value);
    if (isNaN(d.getTime())) return '-';
    const dd = String(d.getDate()).padStart(2, '0');
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const yyyy = d.getFullYear();
    const hh = String(d.getHours()).padStart(2, '0');
    const min = String(d.getMinutes()).padStart(2, '0');
    return `${dd}/${mm}/${yyyy} ${hh}:${min}`;
}

function formatDate(value) {
    if (!value) return '-';
    const d = new Date(value);
    if (isNaN(d.getTime())) return '-';
    const dd = String(d.getDate()).padStart(2, '0');
    const mm = String(d.getMonth() + 1).padStart(2, '0');
    const yyyy = d.getFullYear();
    return `${dd}/${mm}/${yyyy}`;
}

// ---------------------------------------------------------------------------
// Traducción y renderizado de errores de validación (Pydantic 422)
// ---------------------------------------------------------------------------

function translateCashValidation(msg) {
    if (!msg) return 'Campo inválido.';
    if (msg.includes('greater than or equal to 0')) {
        return 'El monto debe ser mayor o igual a 0.';
    }
    if (msg.includes('Input should be a valid number') || msg.includes('valid decimal')) {
        return 'Ingrese un número válido.';
    }
    if (msg.includes('Input should be a valid integer') || msg.includes('valid integer')) {
        return 'Seleccione una opción válida.';
    }
    if (msg.includes('Field required')) {
        return 'Este campo es obligatorio.';
    }
    if (msg.includes('String should have at most')) {
        const match = msg.match(/at most (\d+) characters/);
        return match ? `No debe exceder ${match[1]} caracteres.` : 'Texto demasiado largo.';
    }
    return msg;
}

function renderCashFieldErrors(form, detail) {
    if (!form || !Array.isArray(detail)) return;
    detail.forEach(err => {
        const fieldName = err.loc && err.loc.length > 0 ? err.loc[err.loc.length - 1] : null;
        if (!fieldName) return;
        
        let input = form.querySelector(`[name="${fieldName}"]`);
        if (!input) {
            // Mapeo defensivo de nombres de campo a IDs
            if (fieldName === 'id_caja') input = document.getElementById('open-cash-caja');
            else if (fieldName === 'monto_apertura') input = document.getElementById('open-cash-monto');
            else if (fieldName === 'monto_cierre') input = document.getElementById('close-cash-monto');
            else if (fieldName === 'notas') input = document.getElementById('close-cash-notas');
        }

        if (input) {
            input.classList.add('is-invalid');
            const feedback = form.querySelector(`#error-${fieldName}`) ||
                input.parentElement.querySelector('.invalid-feedback') ||
                input.nextElementSibling;
            if (feedback && feedback.classList.contains('invalid-feedback')) {
                feedback.textContent = translateCashValidation(err.msg);
            }
        }
    });
}

function clearCashFormErrors(form) {
    if (!form) return;
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
    form.querySelectorAll('.invalid-feedback').forEach(el => {
        // Restaurar mensajes predeterminados si existen
        if (el.id === 'error-id_caja') el.textContent = 'Seleccione una caja para abrir turno.';
        else if (el.id === 'error-monto_apertura') el.textContent = 'Ingrese un monto de apertura válido (mayor o igual a 0).';
        else if (el.id === 'error-monto_cierre') el.textContent = 'Ingrese el monto total contado en caja.';
        else el.textContent = '';
    });
}

// ---------------------------------------------------------------------------
// Dirty check y cierre seguro de modales
// ---------------------------------------------------------------------------

function cashFormHasData(form) {
    if (!form) return false;
    const inputs = form.querySelectorAll('input:not([type="hidden"]), select, textarea');
    for (const input of inputs) {
        if (input.tagName === 'SELECT') {
            if (input.value !== '') return true;
        } else if (input.value && input.value.trim() !== '') {
            return true;
        }
    }
    return false;
}

window.safeCloseOpenCashModal = async function() {
    const form = document.getElementById('open-cash-form');
    if (cashFormHasData(form)) {
        const discard = await (typeof window.confirmModal === 'function'
            ? window.confirmModal('Tienes datos sin guardar en la apertura de caja. ¿Deseas descartar los cambios?')
            : Promise.resolve(true));
        if (!discard) return;
    }
    resetOpenCashForm();
    const modal = getModal('open-cash-modal');
    if (modal) modal.hide();
};

window.safeCloseCloseCashModal = async function() {
    const form = document.getElementById('close-cash-form');
    if (cashFormHasData(form)) {
        const discard = await (typeof window.confirmModal === 'function'
            ? window.confirmModal('Tienes datos sin guardar en el cierre de caja. ¿Deseas descartar los cambios?')
            : Promise.resolve(true));
        if (!discard) return;
    }
    resetCloseCashForm();
    const modal = getModal('close-cash-modal');
    if (modal) modal.hide();
};

function resetOpenCashForm() {
    const form = document.getElementById('open-cash-form');
    if (form) form.reset();
    clearCashFormErrors(form);
    const alertBox = document.getElementById('open-cash-alert');
    if (alertBox) {
        alertBox.textContent = '';
        alertBox.classList.add('d-none');
    }
}

function resetCloseCashForm() {
    const form = document.getElementById('close-cash-form');
    if (form) form.reset();
    clearCashFormErrors(form);
    const alertBox = document.getElementById('close-cash-alert');
    if (alertBox) {
        alertBox.textContent = '';
        alertBox.classList.add('d-none');
    }
}

// Prevención de pérdida accidental de datos al salir del navegador
window.addEventListener('beforeunload', (e) => {
    const openForm = document.getElementById('open-cash-form');
    const closeForm = document.getElementById('close-cash-form');
    const openModalEl = document.getElementById('open-cash-modal');
    const closeModalEl = document.getElementById('close-cash-modal');

    const isOpenModalVisible = openModalEl && openModalEl.classList.contains('show');
    const isCloseModalVisible = closeModalEl && closeModalEl.classList.contains('show');

    if ((isOpenModalVisible && cashFormHasData(openForm)) ||
        (isCloseModalVisible && cashFormHasData(closeForm))) {
        e.preventDefault();
        e.returnValue = '';
    }
});

// ---------------------------------------------------------------------------
// Control de spinners y bloqueo de botones (previene doble clic)
// ---------------------------------------------------------------------------

function setCashSaving(buttonId, spinnerId, isSaving, normalText, savingText = 'Procesando...') {
    const btn = document.getElementById(buttonId);
    const spinner = document.getElementById(spinnerId);
    if (!btn) return;
    btn.disabled = isSaving;
    if (spinner) spinner.classList.toggle('d-none', !isSaving);
    const textEl = btn.querySelector('.btn-text') || btn.querySelector('span:not(.spinner-border)');
    if (textEl) {
        textEl.textContent = isSaving ? savingText : normalText;
    }
}

// ---------------------------------------------------------------------------
// Carga de Estado Actual y Renderizado de Tarjeta
// ---------------------------------------------------------------------------

async function loadCurrentCashStatus() {
    try {
        const res = await fetch(`${CASH_API}/estado-actual`, { headers: authHeaders() });
        if (!res.ok) {
            throw new Error(`Error al consultar estado de caja (${res.status})`);
        }
        const data = await res.json();
        currentTurno = data;
        renderCashStatusCard(data);
    } catch (err) {
        console.error('Error al cargar estado de caja:', err);
        renderCashStatusCard(null);
    }
}

function renderCashStatusCard(turno) {
    const titleEl = document.getElementById('cash-status-title');
    const subtitleEl = document.getElementById('cash-status-subtitle');
    const badgeEl = document.getElementById('cash-status-badge');
    const iconBox = document.getElementById('cash-status-icon-box');
    const detailsRow = document.getElementById('cash-active-details');
    const closedMsg = document.getElementById('cash-closed-message');
    const btnOpen = document.getElementById('btn-open-cash');
    const btnClose = document.getElementById('btn-close-cash');

    const isOpen = turno && (turno.estado === 'Abierto' || turno.estado === 'Abierta');

    if (isOpen) {
        // Estado ABIERTA
        if (titleEl) titleEl.textContent = 'Caja Abierta';
        if (subtitleEl) subtitleEl.textContent = 'Turno de trabajo en curso y registrando transacciones.';
        if (badgeEl) {
            badgeEl.className = 'badge bg-success px-3 py-2 rounded-pill fs-6';
            badgeEl.innerHTML = '<i class="bi bi-check-circle-fill me-1"></i> ABIERTA';
        }
        if (iconBox) {
            iconBox.className = 'icon-circle bg-success-subtle text-success fs-4 rounded-circle d-flex align-items-center justify-content-center';
        }

        // Llenar datos del turno
        const cajaNombre = turno.caja ? `${turno.caja.descripcion} (ID #${turno.id_caja})` : `Caja #${turno.id_caja}`;
        const cajeroNombre = turno.usuario ? `${turno.usuario.nombre_completo} (@${turno.usuario.username})` : `Usuario #${turno.id_usuario}`;

        const cajaEl = document.getElementById('cash-active-caja');
        const cajeroEl = document.getElementById('cash-active-cajero');
        const montoEl = document.getElementById('cash-active-monto');
        const ventasEl = document.getElementById('cash-active-ventas');
        const esperadoEl = document.getElementById('cash-active-esperado');
        const fechaEl = document.getElementById('cash-active-fecha');
        const btnMovimiento = document.getElementById('btn-cash-movement');

        if (cajaEl) cajaEl.textContent = cajaNombre;
        if (cajeroEl) cajeroEl.textContent = cajeroNombre;
        if (montoEl) montoEl.textContent = formatCurrency(turno.monto_apertura);

        const montoInicial = Number(turno.monto_apertura || 0);
        const ventasEfectivo = Number(turno.ventas_efectivo != null ? turno.ventas_efectivo : (turno.total_ventas_efectivo != null ? turno.total_ventas_efectivo : 0));
        const efectivoEsperado = computeExpectedCash(turno);
        activeExpectedCash = efectivoEsperado;

        if (ventasEl) ventasEl.textContent = formatCurrency(ventasEfectivo);
        if (esperadoEl) esperadoEl.textContent = formatCurrency(efectivoEsperado);
        if (fechaEl) fechaEl.textContent = formatDateTime(turno.fecha_apertura);

        if (detailsRow) detailsRow.classList.remove('d-none');
        if (closedMsg) closedMsg.classList.add('d-none');

        // Botones contextuales
        if (btnOpen) btnOpen.classList.add('d-none');
        if (btnClose) btnClose.classList.remove('d-none');
        if (btnMovimiento) btnMovimiento.classList.remove('d-none');
    } else {
        // Estado CERRADA
        if (titleEl) titleEl.textContent = 'Caja Cerrada';
        if (subtitleEl) subtitleEl.textContent = 'No hay turno activo para tu usuario en este momento.';
        if (badgeEl) {
            badgeEl.className = 'badge bg-secondary px-3 py-2 rounded-pill fs-6';
            badgeEl.innerHTML = '<i class="bi bi-door-closed me-1"></i> CERRADA';
        }
        if (iconBox) {
            iconBox.className = 'icon-circle bg-light text-muted fs-4 rounded-circle d-flex align-items-center justify-content-center border';
        }

        if (detailsRow) detailsRow.classList.add('d-none');
        if (closedMsg) closedMsg.classList.remove('d-none');

        // Botones contextuales
        const btnMovimiento = document.getElementById('btn-cash-movement');
        if (btnMovimiento) btnMovimiento.classList.add('d-none');
        if (btnOpen) btnOpen.classList.remove('d-none');
        if (btnClose) btnClose.classList.add('d-none');
    }
}

// ---------------------------------------------------------------------------
// Carga de catálogo de Cajas para el dropdown
// ---------------------------------------------------------------------------

async function loadCashRegisters() {
    const select = document.getElementById('open-cash-caja');
    if (!select) return;

    select.innerHTML = '<option value="">Cargando cajas...</option>';
    try {
        const res = await fetch(`${CASH_API}/cajas`, { headers: authHeaders() });
        if (!res.ok) {
            throw new Error('No se pudo cargar la lista de cajas.');
        }
        const cajas = await res.json();
        select.innerHTML = '<option value="">-- Seleccione una caja --</option>';
        cajas.forEach(c => {
            const opt = document.createElement('option');
            opt.value = c.id_caja;
            opt.textContent = `${c.descripcion} (Caja #${c.id_caja})`;
            select.appendChild(opt);
        });
    } catch (err) {
        console.error('Error al cargar cajas:', err);
        select.innerHTML = '<option value="">Error al cargar cajas</option>';
    }
}

// ---------------------------------------------------------------------------
// Apertura y Cierre de Modales
// ---------------------------------------------------------------------------

window.openOpenCashModal = async function() {
    resetOpenCashForm();
    await loadCashRegisters();
    const modal = getModal('open-cash-modal');
    if (modal) {
        modal.show();
        // Autofocus en monto tras abrir
        setTimeout(() => {
            const montoInput = document.getElementById('open-cash-monto');
            if (montoInput) montoInput.focus();
        }, 300);
    }
};

window.openCloseCashModal = function() {
    resetCloseCashForm();
    if (!currentTurno) {
        if (typeof window.showToast === 'function') {
            window.showToast('No hay un turno de caja activo para cerrar.', 'warning');
        }
        return;
    }

    const montoInicial = Number(currentTurno.monto_apertura || 0);
    const ventasEfectivo = Number(currentTurno.ventas_efectivo != null ? currentTurno.ventas_efectivo : (currentTurno.total_ventas_efectivo != null ? currentTurno.total_ventas_efectivo : 0));
    const entradas = Number(currentTurno.entradas_efectivo || 0);
    const salidas = Number(currentTurno.salidas_efectivo || 0);
    const netoMovimientos = entradas - salidas;
    const efectivoEsperado = computeExpectedCash(currentTurno);
    activeExpectedCash = efectivoEsperado;

    // Resumen superior compacto (4 filas limpias sin signos)
    const montoEl = document.getElementById('close-summary-monto');
    const ventasEl = document.getElementById('close-summary-ventas');
    const movsEl = document.getElementById('close-summary-movimientos');
    const esperadoEl = document.getElementById('close-summary-esperado');
    const quickBtnText = document.getElementById('btn-cash-quick-match-text');

    if (montoEl) montoEl.textContent = formatCurrency(montoInicial);
    if (ventasEl) ventasEl.textContent = formatCurrency(ventasEfectivo);
    if (movsEl) {
        if (netoMovimientos === 0) {
            movsEl.textContent = 'Q 0.00';
            movsEl.className = 'fw-semibold text-dark small font-monospace';
        } else if (netoMovimientos > 0) {
            movsEl.textContent = `+ ${formatCurrency(netoMovimientos)}`;
            movsEl.className = 'fw-semibold text-success small font-monospace';
        } else {
            movsEl.textContent = `- ${formatCurrency(Math.abs(netoMovimientos))}`;
            movsEl.className = 'fw-semibold text-danger small font-monospace';
        }
    }
    if (esperadoEl) esperadoEl.textContent = formatCurrency(efectivoEsperado);

    // Botón sobrio: "Usar monto esperado (Q X.XX)" (sin emojis)
    if (quickBtnText) {
        quickBtnText.textContent = `Usar monto esperado (${formatCurrency(efectivoEsperado)})`;
    }

    // Actualizar indicador de diferencia (oculto mientras el campo esté vacío)
    updateCashDifferenceIndicator();

    const modal = getModal('close-cash-modal');
    if (modal) {
        modal.show();
        setTimeout(() => {
            const montoInput = document.getElementById('close-cash-monto');
            if (montoInput) montoInput.focus();
        }, 300);
    }
};

// ---------------------------------------------------------------------------
// Indicador de Diferencia en Tiempo Real (Minimalista)
// ---------------------------------------------------------------------------

function updateCashDifferenceIndicator() {
    const montoInput = document.getElementById('close-cash-monto');
    const alertEl = document.getElementById('close-cash-diff-alert');
    if (!alertEl || !montoInput) return;

    const valStr = montoInput.value.trim();
    if (valStr === '') {
        alertEl.textContent = '';
        alertEl.className = 'small mt-1 mb-1 d-none';
        return;
    }

    const entered = parseFloat(valStr);
    if (isNaN(entered) || entered < 0) {
        alertEl.className = 'small fw-semibold text-danger mt-1 mb-1';
        alertEl.textContent = 'Ingrese un monto numérico válido mayor o igual a 0.';
        alertEl.classList.remove('d-none');
        return;
    }

    const diff = Math.round((entered - activeExpectedCash) * 100) / 100;
    
    if (Math.abs(diff) < 0.005) {
        // Cuadre exacto (verde, sobrio, sin emojis)
        alertEl.className = 'small fw-bold text-success mt-1 mb-1';
        alertEl.textContent = 'Cuadre exacto (Diferencia: Q 0.00)';
    } else if (diff < 0) {
        // Faltante (rojo, sobrio, sin emojis)
        const faltan = Math.abs(diff).toFixed(2);
        alertEl.className = 'small fw-bold text-danger mt-1 mb-1';
        alertEl.textContent = `Faltante en caja: -Q ${faltan}`;
    } else {
        // Sobrante (azul, sobrio, sin emojis)
        const sobran = diff.toFixed(2);
        alertEl.className = 'small fw-bold text-primary mt-1 mb-1';
        alertEl.textContent = `Sobrante en caja: +Q ${sobran}`;
    }
    alertEl.classList.remove('d-none');
}

function renderCashCalculator() {}
function updateCalculatorTotal() {}
function resetCashCalculator() {}

// ---------------------------------------------------------------------------
async function handleOpenCashSubmit(e) {
    e.preventDefault();
    const form = document.getElementById('open-cash-form');
    const alertBox = document.getElementById('open-cash-alert');
    clearCashFormErrors(form);
    if (alertBox) {
        alertBox.textContent = '';
        alertBox.classList.add('d-none');
    }

    const cajaSelect = document.getElementById('open-cash-caja');
    const montoInput = document.getElementById('open-cash-monto');

    const idCaja = parseInt(cajaSelect.value, 10);
    const monto = parseFloat(montoInput.value);

    let hasClientError = false;
    if (isNaN(idCaja) || idCaja <= 0) {
        cajaSelect.classList.add('is-invalid');
        hasClientError = true;
    }
    if (isNaN(monto) || monto < 0) {
        montoInput.classList.add('is-invalid');
        hasClientError = true;
    }
    if (hasClientError) return;

    setCashSaving('btn-submit-open-cash', 'open-cash-spinner', true, 'Abrir Caja', 'Abriendo...');

    try {
        const payload = {
            id_caja: idCaja,
            monto_apertura: monto,
        };
        const res = await fetch(`${CASH_API}/apertura`, {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify(payload),
        });

        if (res.status === 422) {
            const errorData = await res.json();
            renderCashFieldErrors(form, errorData.detail);
            return;
        }

        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            const msg = (errData && errData.detail) || 'Error al abrir el turno de caja';
            if (alertBox) {
                alertBox.textContent = msg;
                alertBox.classList.remove('d-none');
            } else if (typeof window.showToast === 'function') {
                window.showToast(msg, 'danger');
            }
            return;
        }

        const nuevoTurno = await res.json();
        const modal = getModal('open-cash-modal');
        if (modal) modal.hide();
        resetOpenCashForm();

        if (typeof window.showToast === 'function') {
            window.showToast(`Caja abierta exitosamente con saldo inicial de ${formatCurrency(nuevoTurno.monto_apertura)}.`, 'success');
        }

        await loadCurrentCashStatus();
        await loadCashTurnos();
    } catch (err) {
        console.error(err);
        if (alertBox) {
            alertBox.textContent = err.message || 'Error de conexión con el servidor.';
            alertBox.classList.remove('d-none');
        }
    } finally {
        setCashSaving('btn-submit-open-cash', 'open-cash-spinner', false, 'Abrir Caja');
    }
}

async function handleCloseCashSubmit(e) {
    e.preventDefault();
    const form = document.getElementById('close-cash-form');
    const alertBox = document.getElementById('close-cash-alert');
    clearCashFormErrors(form);
    if (alertBox) {
        alertBox.textContent = '';
        alertBox.classList.add('d-none');
    }

    const montoInput = document.getElementById('close-cash-monto');
    const notasInput = document.getElementById('close-cash-notas');

    const monto = parseFloat(montoInput.value);
    const notas = notasInput ? notasInput.value.trim() : '';

    if (isNaN(monto) || monto < 0) {
        montoInput.classList.add('is-invalid');
        return;
    }

    setCashSaving('btn-submit-close-cash', 'close-cash-spinner', true, 'Cerrar Caja', 'Cerrando...');

    try {
        const payload = {
            monto_cierre: monto,
            notas: notas || null,
        };
        const res = await fetch(`${CASH_API}/cierre`, {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify(payload),
        });

        if (res.status === 422) {
            const errorData = await res.json();
            renderCashFieldErrors(form, errorData.detail);
            return;
        }

        if (!res.ok) {
            const errData = await res.json().catch(() => null);
            const msg = (errData && errData.detail) || 'Error al cerrar el turno de caja';
            if (alertBox) {
                alertBox.textContent = msg;
                alertBox.classList.remove('d-none');
            } else if (typeof window.showToast === 'function') {
                window.showToast(msg, 'danger');
            }
            return;
        }

        const turnoCerrado = await res.json();
        const modal = getModal('close-cash-modal');
        if (modal) modal.hide();
        resetCloseCashForm();

        if (typeof window.showToast === 'function') {
            window.showToast(`Caja cerrada exitosamente. Monto final registrado: ${formatCurrency(turnoCerrado.monto_cierre)}.`, 'success');
        }

        await loadCurrentCashStatus();
        await loadCashTurnos();
    } catch (err) {
        console.error(err);
        if (alertBox) {
            alertBox.textContent = err.message || 'Error de conexión con el servidor.';
            alertBox.classList.remove('d-none');
        }
    } finally {
        setCashSaving('btn-submit-close-cash', 'close-cash-spinner', false, 'Cerrar Caja');
    }
}

// ---------------------------------------------------------------------------
// Historial de Turnos de Caja (Búsqueda, Filtros, Ordenamiento y Paginación)
// ---------------------------------------------------------------------------

// ---------------------------------------------------------------------------
// Modal y Gestión de Movimientos de Caja (Gastos Menores / Entrada)
// ---------------------------------------------------------------------------

window.openCashMovementModal = function() {
    const form = document.getElementById('cash-movement-form');
    if (form) {
        form.reset();
        form.classList.remove('was-validated');
    }
    const modal = getModal('cash-movement-modal');
    if (modal) modal.show();
};

async function handleCashMovementSubmit(e) {
    e.preventDefault();
    const form = document.getElementById('cash-movement-form');
    if (!form) return;

    const type = document.getElementById('cash-movement-type')?.value;
    const amount = parseFloat(document.getElementById('cash-movement-amount')?.value);
    const concept = document.getElementById('cash-movement-concept')?.value.trim();

    if (!amount || isNaN(amount) || amount <= 0 || !concept) {
        form.classList.add('was-validated');
        return;
    }

    const submitBtn = document.getElementById('btn-submit-cash-movement');
    if (submitBtn) submitBtn.disabled = true;

    try {
        const payload = {
            id_tipo_movimiento: type === 'entrada' ? 1 : 2,
            monto: amount,
            justificacion: concept,
        };
        const res = await fetch(`${CASH_API}/movimiento`, {
            method: 'POST',
            headers: authHeaders(),
            body: JSON.stringify(payload),
        });

        if (!res.ok) {
            const err = await res.json().catch(() => null);
            throw new Error((err && err.detail) || 'Error al registrar movimiento');
        }

        const modal = getModal('cash-movement-modal');
        if (modal) modal.hide();

        const typeLabel = type === 'gasto' ? 'Gasto menor (salida)' : 'Entrada para cambio';
        if (typeof window.showToast === 'function') {
            window.showToast(`${typeLabel} registrado (${formatCurrency(amount)}): "${escapeHtml(concept)}"`, 'success');
        }

        await loadCurrentCashStatus();
        await loadCashTurnos();
    } catch (err) {
        console.error('Error registrando movimiento:', err);
        if (typeof window.showToast === 'function') {
            window.showToast(err.message || 'Error al registrar movimiento en servidor', 'danger');
        }
    } finally {
        if (submitBtn) submitBtn.disabled = false;
    }
}

async function loadCashTurnos() {
    const tbody = document.getElementById('cash-table-body');
    const empty = document.getElementById('cash-empty');
    if (!tbody) return;

    const from = document.getElementById('filter-cash-from')?.value || '';
    const to = document.getElementById('filter-cash-to')?.value || '';
    const estado = document.getElementById('filter-cash-status')?.value || '';

    const params = new URLSearchParams();
    if (from) params.append('fecha_desde', from);
    if (to) params.append('fecha_hasta', to);
    if (estado) params.append('estado', estado);
    params.append('sort_by', cashHistoryState.sortBy);
    params.append('sort_dir', cashHistoryState.sortDir);
    params.append('limit', cashHistoryState.pageSize);
    params.append('offset', (cashHistoryState.page - 1) * cashHistoryState.pageSize);

    if (tbody && typeof window.renderSkeletonTable === 'function') {
        tbody.innerHTML = window.renderSkeletonTable(8, 5);
    }

    try {
        const res = await fetch(`${CASH_API}/turnos?${params.toString()}`, { headers: authHeaders() });
        if (!res.ok) {
            throw new Error(`Error al consultar historial de turnos (${res.status})`);
        }
        const data = await res.json();
        cashHistoryState.total = data.total || 0;

        if (data.items && data.items.length > 0) {
            tbody.innerHTML = data.items.map(t => {
                const cajaDesc = t.caja ? t.caja.descripcion : `Caja #${t.id_caja}`;
                const cajero = t.usuario ? t.usuario.nombre_completo : `Usuario #${t.id_usuario}`;
                const isOpen = t.estado === 'Abierto' || t.estado === 'Abierta';
                const badgeClass = isOpen ? 'bg-success text-white' : 'bg-secondary text-white';
                const estadoText = isOpen ? 'Abierto' : 'Cerrado';
                const fechaCierre = t.fecha_cierre ? formatDateTime(t.fecha_cierre) : '<span class="text-muted fst-italic">En curso</span>';
                const montoApertura = Number(t.monto_apertura || 0);
                const ventasEfectivo = Number(t.ventas_efectivo != null ? t.ventas_efectivo : 0);
                const entradas = Number(t.entradas_efectivo || 0);
                const salidas = Number(t.salidas_efectivo || 0);
                const efectivoEsperado = t.efectivo_esperado != null
                    ? Number(t.efectivo_esperado)
                    : Math.max(0, montoApertura + ventasEfectivo + entradas - salidas);

                const montoCierre = (t.monto_cierre !== null && t.monto_cierre !== undefined)
                    ? Number(t.monto_cierre)
                    : null;

                // Diferencia: Badge limpio sin iconos (verde Q 0.00, rojo -Q X.XX, azul +Q X.XX, o gris En curso)
                let diffBadge = '<span class="badge bg-light text-muted border px-2 py-1 font-monospace">En curso</span>';
                if (!isOpen && montoCierre !== null) {
                    const diff = t.diferencia != null ? Number(t.diferencia) : (montoCierre - efectivoEsperado);
                    if (Math.abs(diff) < 0.005) {
                        diffBadge = `<span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-1 font-monospace">Q 0.00</span>`;
                    } else if (diff < 0) {
                        diffBadge = `<span class="badge bg-danger-subtle text-danger border border-danger-subtle px-2 py-1 font-monospace">-Q ${Math.abs(diff).toFixed(2)}</span>`;
                    } else {
                        diffBadge = `<span class="badge bg-primary-subtle text-primary border border-primary-subtle px-2 py-1 font-monospace">+Q ${diff.toFixed(2)}</span>`;
                    }
                }

                return `
                    <tr>
                        <td>
                            <strong class="text-dark">#${t.id_turno}</strong>
                            <span class="text-muted small d-block">${escapeHtml(cajaDesc)}</span>
                        </td>
                        <td class="text-dark">${escapeHtml(cajero)}</td>
                        <td>
                            <div class="small fw-medium text-dark">${formatDateTime(t.fecha_apertura)}</div>
                            <div class="small text-muted">${fechaCierre}</div>
                        </td>
                        <td class="font-monospace text-dark">${formatCurrency(t.monto_apertura)}</td>
                        <td class="fw-bold font-monospace text-teal">${formatCurrency(efectivoEsperado)}</td>
                        <td class="fw-bold font-monospace">${montoCierre !== null ? formatCurrency(montoCierre) : '<span class="text-muted">-</span>'}</td>
                        <td>${diffBadge}</td>
                        <td><span class="badge ${badgeClass} rounded-pill px-2 py-1">${estadoText}</span></td>
                    </tr>
                `;
            }).join('');

            tbody.closest('.table-responsive')?.classList.remove('d-none');
            if (empty) empty.classList.add('d-none');
        } else {
            tbody.innerHTML = '';
            tbody.closest('.table-responsive')?.classList.add('d-none');
            if (empty) empty.classList.remove('d-none');
        }

        renderCashPagination();
        updateCashSortIndicators();
    } catch (err) {
        console.error('Error al cargar historial de turnos:', err);
        if (typeof window.showToast === 'function') {
            window.showToast('No se pudieron cargar los turnos de caja.', 'danger');
        }
    }
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

// ---------------------------------------------------------------------------
// Paginación y Ordenamiento Reactivos
// ---------------------------------------------------------------------------

function renderCashPagination() {
    const pagination = document.getElementById('cash-pagination');
    if (!pagination) return;
    const totalPages = Math.max(1, Math.ceil(cashHistoryState.total / cashHistoryState.pageSize));
    if (cashHistoryState.page > totalPages) cashHistoryState.page = totalPages;

    const info = document.getElementById('cash-page-info');
    const prev = document.getElementById('cash-prev-page');
    const next = document.getElementById('cash-next-page');

    if (info) info.textContent = `Página ${cashHistoryState.page} de ${totalPages} (${cashHistoryState.total} turnos)`;
    if (prev) prev.disabled = cashHistoryState.page <= 1;
    if (next) next.disabled = cashHistoryState.page >= totalPages;

    pagination.classList.toggle('d-none', cashHistoryState.total === 0);
}

function goToCashPage(page) {
    const totalPages = Math.max(1, Math.ceil(cashHistoryState.total / cashHistoryState.pageSize));
    if (page < 1) page = 1;
    if (page > totalPages) page = totalPages;
    if (page === cashHistoryState.page) return;
    cashHistoryState.page = page;
    loadCashTurnos();
}

function toggleCashSort(column) {
    if (cashHistoryState.sortBy === column) {
        cashHistoryState.sortDir = cashHistoryState.sortDir === 'asc' ? 'desc' : 'asc';
    } else {
        cashHistoryState.sortBy = column;
        cashHistoryState.sortDir = 'desc'; // Por defecto mostrar más recientes primero
    }
    cashHistoryState.page = 1;
    updateCashSortIndicators();
    loadCashTurnos();
}

function updateCashSortIndicators() {
    document.querySelectorAll('#cash-view th.sortable').forEach(th => {
        const col = th.getAttribute('data-sort');
        let iconSpan = th.querySelector('.sort-icon');
        if (!iconSpan) {
            iconSpan = document.createElement('span');
            iconSpan.className = 'sort-icon';
            th.appendChild(iconSpan);
        }
        if (col === cashHistoryState.sortBy) {
            const arrowClass = cashHistoryState.sortDir === 'asc' ? 'bi-arrow-up' : 'bi-arrow-down';
            iconSpan.innerHTML = `<i class="bi ${arrowClass} text-white ms-1"></i>`;
        } else {
            iconSpan.innerHTML = `<i class="bi bi-arrow-down-up text-white-50 ms-1"></i>`;
        }
    });
}

function clearCashFilters() {
    const fromInput = document.getElementById('filter-cash-from');
    const toInput = document.getElementById('filter-cash-to');
    const statusSelect = document.getElementById('filter-cash-status');

    if (fromInput) fromInput.value = '';
    if (toInput) toInput.value = '';
    if (statusSelect) statusSelect.value = '';

    cashHistoryState.page = 1;
    loadCashTurnos();
}

// ---------------------------------------------------------------------------
// Inicialización del Módulo de Caja (llamado desde el Router SPA de app.js)
// ---------------------------------------------------------------------------

window.showCashModule = async function() {
    updateCashSortIndicators();
    await Promise.all([
        loadCurrentCashStatus(),
        loadCashTurnos(),
    ]);
};

// Wiring de listeners al cargar DOM
document.addEventListener('DOMContentLoaded', () => {
    // Formularios
    const openForm = document.getElementById('open-cash-form');
    if (openForm) openForm.addEventListener('submit', handleOpenCashSubmit);

    const closeForm = document.getElementById('close-cash-form');
    if (closeForm) closeForm.addEventListener('submit', handleCloseCashSubmit);

    // Botón de llenado rápido ("Todo cuadra")
    const btnQuickMatch = document.getElementById('btn-cash-quick-match');
    if (btnQuickMatch) {
        btnQuickMatch.addEventListener('click', () => {
            const montoInput = document.getElementById('close-cash-monto');
            if (montoInput) {
                montoInput.value = activeExpectedCash.toFixed(2);
                montoInput.classList.remove('is-invalid');
                updateCashDifferenceIndicator();
            }
        });
    }

    // Input de monto de cierre: deshabilitar scroll de mouse y actualizar diferencia en vivo
    const closeMontoInput = document.getElementById('close-cash-monto');
    if (closeMontoInput) {
        closeMontoInput.addEventListener('input', updateCashDifferenceIndicator);
        closeMontoInput.addEventListener('wheel', (e) => e.preventDefault(), { passive: false });
    }

    // Botón para reiniciar calculadora de billetes
    const btnResetCalc = document.getElementById('btn-reset-cash-calculator');
    if (btnResetCalc) {
        btnResetCalc.addEventListener('click', resetCashCalculator);
    }

    const movementForm = document.getElementById('cash-movement-form');
    if (movementForm) movementForm.addEventListener('submit', handleCashMovementSubmit);

    // Limpieza de validación en tiempo real al escribir
    [openForm, closeForm].forEach(form => {
        if (!form) return;
        form.querySelectorAll('.form-control, .form-select').forEach(input => {
            input.addEventListener('input', () => input.classList.remove('is-invalid'));
            input.addEventListener('change', () => input.classList.remove('is-invalid'));
        });
    });

    // Filtros de historial
    const btnFilter = document.getElementById('btn-filter-cash');
    if (btnFilter) {
        btnFilter.addEventListener('click', () => {
            cashHistoryState.page = 1;
            loadCashTurnos();
        });
    }

    const btnClear = document.getElementById('btn-clear-cash-filters');
    if (btnClear) btnClear.addEventListener('click', clearCashFilters);

    // Paginación
    const pageSizeSelect = document.getElementById('cash-page-size');
    if (pageSizeSelect) {
        pageSizeSelect.addEventListener('change', () => {
            cashHistoryState.pageSize = parseInt(pageSizeSelect.value, 10) || 10;
            cashHistoryState.page = 1;
            loadCashTurnos();
        });
    }

    const btnPrev = document.getElementById('cash-prev-page');
    if (btnPrev) btnPrev.addEventListener('click', () => goToCashPage(cashHistoryState.page - 1));

    const btnNext = document.getElementById('cash-next-page');
    if (btnNext) btnNext.addEventListener('click', () => goToCashPage(cashHistoryState.page + 1));

    // Ordenamiento por cabeceras
    document.querySelectorAll('#cash-view th.sortable').forEach(th => {
        th.addEventListener('click', () => {
            const col = th.getAttribute('data-sort');
            if (col) toggleCashSort(col);
        });
    });
});

