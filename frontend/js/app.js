// Curiosidades El Regalito - Auth & Dashboard Logic
const API_URL = '/api';
const authModule = document.getElementById('auth-module');
const systemModule = document.getElementById('system-module');

// Array of all auth views to easily hide them
const authViews = ['view-login', 'view-recover', 'view-verify', 'view-reset'];
const mainViews = ['dashboard', 'pos', 'users', 'roles', 'clients', 'bitacora', 'historial', 'catalog', 'cash', 'reportes', 'configuracion', 'inventory', 'compras', 'mermas', 'traslados', 'visitas', 'ventas'];
let currentView = null;

// ---------------------------------------------------------------------------
// Toast Notification Utility (Toasts minimalistas en esquina superior derecha)
// ---------------------------------------------------------------------------

window.showToast = function(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    // Normalizar tipos
    const normType = (type === 'error' || type === 'danger') ? 'danger' : (type === 'warning' ? 'warning' : (type === 'info' ? 'info' : 'success'));
    
    const icons = {
        success: 'bi-check-circle-fill',
        danger: 'bi-x-circle-fill',
        warning: 'bi-exclamation-triangle-fill',
        info: 'bi-info-circle-fill',
    };

    const el = document.createElement('div');
    el.className = `custom-toast toast-${normType} toast border-0 show`;
    el.setAttribute('role', 'alert');
    el.setAttribute('aria-live', 'assertive');
    el.setAttribute('aria-atomic', 'true');
    el.innerHTML = `
        <div class="d-flex align-items-center gap-2 flex-grow-1">
            <i class="bi ${icons[normType] || 'bi-info-circle-fill'} fs-5 toast-icon flex-shrink-0"></i>
            <div class="toast-msg">${message}</div>
        </div>
        <button type="button" class="btn-close-toast ms-2 flex-shrink-0" aria-label="Cerrar">
            <i class="bi bi-x-lg"></i>
        </button>`;

    container.appendChild(el);

    const closeBtn = el.querySelector('.btn-close-toast');
    let timer = null;

    const removeToast = () => {
        if (timer) clearTimeout(timer);
        el.style.opacity = '0';
        el.style.transform = 'translateX(30px)';
        setTimeout(() => {
            if (el.parentNode) el.remove();
        }, 250);
    };

    if (closeBtn) {
        closeBtn.addEventListener('click', removeToast);
    }

    // Desaparece automáticamente en 3 segundos (3000 ms)
    timer = setTimeout(removeToast, 3000);
};

// Reemplazar alertas nativas bloqueantes por Toasts minimalistas no intrusivos
window.alert = function(message) {
    window.showToast(message, 'warning');
};

// ---------------------------------------------------------------------------
// Skeleton Loaders Globales (Simulación de estructura con pulso visual)
// ---------------------------------------------------------------------------

window.renderSkeletonTable = function(columns = 6, rows = 4) {
    let html = '';
    const widths = ['w-50', 'w-75', 'w-100', 'w-60', 'w-40', 'w-90', 'w-75'];
    for (let r = 0; r < rows; r++) {
        html += '<tr class="skeleton-table-row">';
        for (let c = 0; c < columns; c++) {
            const w = widths[(r + c) % widths.length] || 'w-75';
            html += `<td><span class="skeleton skeleton-line mb-0 ${w}" style="height: 15px;"></span></td>`;
        }
        html += '</tr>';
    }
    return html;
};

window.renderSkeletonCard = function(lines = 3) {
    let html = '<div class="skeleton-card my-2">';
    html += '<div class="d-flex align-items-center gap-3 mb-3">' +
            '<div class="skeleton skeleton-circle"></div>' +
            '<div class="flex-grow-1">' +
            '<div class="skeleton skeleton-line w-50 mb-1" style="height: 14px;"></div>' +
            '<div class="skeleton skeleton-line w-25 mb-0" style="height: 10px;"></div>' +
            '</div></div>';
    for (let i = 0; i < lines; i++) {
        const w = i === lines - 1 ? 'w-50' : (i % 2 === 0 ? 'w-100' : 'w-75');
        html += `<div class="skeleton skeleton-line ${w} mb-2" style="height: 12px;"></div>`;
    }
    html += '</div>';
    return html;
};

// ---------------------------------------------------------------------------
// RBAC Helpers (Control de Acceso Basado en Roles y Permisos)
// ---------------------------------------------------------------------------

window.getUserRole = function() {
    return sessionStorage.getItem('user_role') || localStorage.getItem('user_role') || '';
};

window.getUserPermissions = function() {
    try {
        const raw = sessionStorage.getItem('user_permissions') || localStorage.getItem('user_permissions') || '[]';
        return JSON.parse(raw);
    } catch (e) {
        return [];
    }
};

window.hasPermission = function(code) {
    const role = window.getUserRole();
    if (role === 'Administradora') return true;
    const perms = window.getUserPermissions();
    return perms.includes(code);
};

window.isAdmin = function() {
    return window.getUserRole() === 'Administradora';
};

window.getToken = function() {
    return sessionStorage.getItem('jwt_token') || localStorage.getItem('jwt_token') || '';
};

// ---------------------------------------------------------------------------
// Auth Guard: control de acceso y redirección
// ---------------------------------------------------------------------------

function hasActiveSession() {
    return !!sessionStorage.getItem('jwt_token');
}

// Limpia completamente la sesión local y muestra la pantalla de Login sin residuos.
async function showLogin() {
    // Si tenemos un token, intentamos hacer logout en el backend para limpiar la cookie
    const token = sessionStorage.getItem('jwt_token') || localStorage.getItem('jwt_token');
    if (token) {
        try {
            await nativeFetch(`${API_URL}/auth/logout`, { method: 'POST' });
        } catch (e) {
            // Ignorar errores en logout
        }
    }

    if (typeof healthCheckInterval !== 'undefined' && healthCheckInterval) {
        clearInterval(healthCheckInterval);
        healthCheckInterval = null;
    }

    // 1. Limpieza de almacenamiento de sesión (preservando preferencias de UI y usuario recordado)
    const rememberedUser = localStorage.getItem('remember_user');
    const savedTheme = localStorage.getItem('themePreference');
    const savedSidebar = localStorage.getItem('sidebarCollapsed');

    localStorage.clear();
    sessionStorage.clear();

    if (rememberedUser) localStorage.setItem('remember_user', rememberedUser);
    if (savedTheme) localStorage.setItem('themePreference', savedTheme);
    if (savedSidebar) localStorage.setItem('sidebarCollapsed', savedSidebar);

    // 2. Limpieza de estado en memoria y sanitización de URL sin recarga
    currentView = null;
    if (window.location.hash) {
        history.replaceState(null, '', window.location.pathname + window.location.search);
    }

    // 3. Limpieza y preparación de formularios de autenticación
    const loginUser = document.getElementById('login-user');
    const loginPass = document.getElementById('login-pass');
    const loginError = document.getElementById('login-error');
    const rememberMe = document.getElementById('remember-me');

    if (loginPass) loginPass.value = '';
    if (loginError) {
        loginError.textContent = '';
        loginError.classList.add('d-none');
    }

    if (loginUser && rememberedUser) {
        loginUser.value = rememberedUser;
        if (rememberMe) rememberMe.checked = true;
        if (loginPass) setTimeout(() => loginPass.focus(), 150);
    } else {
        if (loginUser) loginUser.value = '';
        if (rememberMe) rememberMe.checked = false;
        if (loginUser) setTimeout(() => loginUser.focus(), 150);
    }

    // 4. Limpieza de datos visuales de usuario
    const sidebarEl = document.getElementById('sidebar-username');
    if (sidebarEl) sidebarEl.innerText = 'Usuario';
    const greetingEl = document.getElementById('header-greeting');
    if (greetingEl) greetingEl.innerText = '¡Hola, Usuario!';
    const roleBadge = document.getElementById('header-role');
    if (roleBadge) roleBadge.innerText = 'Usuario';

    // 5. Ocultar todas las vistas del sistema y resetear navegación activa
    document.querySelectorAll('[data-main-view]').forEach(container => {
        container.classList.add('d-none');
    });
    document.querySelectorAll('[data-nav]').forEach(link => {
        link.classList.remove('active', 'text-white');
        link.classList.add('text-white-50');
        link.removeAttribute('aria-current');
    });

    // 6. Conmutar a módulo de autenticación
    if (systemModule) systemModule.classList.add('d-none');
    if (authModule) authModule.classList.remove('d-none');
    authViews.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add('d-none');
    });
    const login = document.getElementById('view-login');
    if (login) login.classList.remove('d-none');
}

window.showLogin = showLogin;
window.logout = showLogin;

// Manejo central de respuestas 401: sesión inválida/expirada => Login inmediato.
function handleUnauthorized() {
    showLogin();
}

let isRefreshing = false;
let refreshSubscribers = [];

function subscribeTokenRefresh(cb) {
    refreshSubscribers.push(cb);
}

function onRefreshed(token) {
    refreshSubscribers.forEach(cb => cb(token));
    refreshSubscribers = [];
}

// Interceptor global: intenta refrescar silenciosamente ante un 401.
const nativeFetch = window.fetch;
window.fetch = async function (...args) {
    const url = args[0];
    let response = await nativeFetch.apply(this, args);

    if (response.status === 401 && !url.endsWith('/auth/login') && !url.endsWith('/auth/refresh') && !url.endsWith('/auth/logout')) {
        if (!isRefreshing) {
            isRefreshing = true;
            try {
                const refreshRes = await nativeFetch(`${API_URL}/auth/refresh`, { method: 'POST' });
                if (refreshRes.ok) {
                    const data = await refreshRes.json();
                    sessionStorage.setItem('jwt_token', data.access_token);
                    localStorage.setItem('jwt_token', data.access_token);
                    isRefreshing = false;
                    onRefreshed(data.access_token);
                    
                    // Reintentar la petición original con el nuevo token
                    const newOptions = args[1] || {};
                    newOptions.headers = newOptions.headers || {};
                    // Solo actualizamos el header Authorization si ya estaba presente (ya que se envía manualmente en la app)
                    if (newOptions.headers['Authorization'] || newOptions.headers.get?.('Authorization')) {
                        if (newOptions.headers instanceof Headers) {
                            newOptions.headers.set('Authorization', `Bearer ${data.access_token}`);
                        } else {
                            newOptions.headers['Authorization'] = `Bearer ${data.access_token}`;
                        }
                    }
                    return nativeFetch(args[0], newOptions);
                } else {
                    isRefreshing = false;
                    handleUnauthorized();
                    return response;
                }
            } catch (err) {
                isRefreshing = false;
                handleUnauthorized();
                return response;
            }
        } else {
            return new Promise(resolve => {
                subscribeTokenRefresh(token => {
                    const newOptions = args[1] || {};
                    newOptions.headers = newOptions.headers || {};
                    if (newOptions.headers['Authorization'] || newOptions.headers.get?.('Authorization')) {
                        if (newOptions.headers instanceof Headers) {
                            newOptions.headers.set('Authorization', `Bearer ${token}`);
                        } else {
                            newOptions.headers['Authorization'] = `Bearer ${token}`;
                        }
                    }
                    resolve(nativeFetch(args[0], newOptions));
                });
            });
        }
    }
    return response;
};

// Actualiza el nombre visible y badge de rol en el header y sidebar
function updateUserInfoUI() {
    const rawUser = sessionStorage.getItem('user_name') || localStorage.getItem('user_name') || '';
    const role = sessionStorage.getItem('user_role') || localStorage.getItem('user_role') || '';
    let displayName = sessionStorage.getItem('user_display_name') || localStorage.getItem('user_display_name');

    if (rawUser.toLowerCase() === 'admin' || role === 'Administradora' || !displayName || displayName.toLowerCase() === 'admin') {
        displayName = 'Administrador';
    }

    const sidebarEl = document.getElementById('sidebar-username');
    if (sidebarEl) sidebarEl.innerText = displayName;

    const greetingEl = document.getElementById('header-greeting');
    if (greetingEl) greetingEl.innerText = `¡Hola, ${displayName}!`;

    const roleBadge = document.getElementById('header-role');
    if (roleBadge) {
        roleBadge.innerText = role || 'Usuario';
    }

    const avatarImg = document.querySelector('#dropdownUser img');
    if (avatarImg) {
        avatarImg.src = `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=0A5C5E&color=fff`;
    }
}

// Control visual dinámico según rol y permisos
function applyRoleRestrictions() {
    const role = window.getUserRole();
    const isUserAdmin = window.isAdmin();

    const moduleAllowed = {
        pos: isUserAdmin || window.hasPermission('VENTA_COBRAR'),
        inventory: isUserAdmin || window.hasPermission('INV_INGRESAR_MERCADERIA') || window.hasPermission('VENTA_COBRAR'),
        compras: isUserAdmin || window.hasPermission('COMPRA_EMITIR_ORDEN') || window.hasPermission('INV_INGRESAR_MERCADERIA'),
        mermas: isUserAdmin || window.hasPermission('INV_INGRESAR_MERCADERIA'),
        traslados: isUserAdmin || window.hasPermission('INV_INGRESAR_MERCADERIA'),
        visitas: isUserAdmin || window.hasPermission('VISITA_REGISTRAR'),
        cash: isUserAdmin || role === 'Cajero' || window.hasPermission('CAJA_CIERRE_CIEGAS'),
        caja: isUserAdmin || role === 'Cajero' || window.hasPermission('CAJA_CIERRE_CIEGAS'),
        users: isUserAdmin,
        roles: isUserAdmin,
        clients: isUserAdmin || window.hasPermission('CLIENTE_ADMIN'),
        catalog: isUserAdmin || role === 'Bodeguero' || window.hasPermission('CATALOGO_ADMIN'),
        bitacora: isUserAdmin || window.hasPermission('BITACORA_CONSULTAR'),
        historial: isUserAdmin || window.hasPermission('REPORTE_VER'),
        reportes: isUserAdmin || window.hasPermission('REPORTE_VER'),
        configuracion: isUserAdmin,
        ventas: isUserAdmin || window.hasPermission('REPORTE_VER') || window.hasPermission('VENTA_COBRAR'),
    };

    // 1. Sidebar Items
    document.querySelectorAll('[data-module-item]').forEach(el => {
        const modKey = el.getAttribute('data-module-item');
        const allowed = moduleAllowed[modKey] ?? false;
        el.classList.toggle('d-none', !allowed);
    });

    // 2. Sidebar Section Headers
    const opItems = document.querySelectorAll('[data-module-item="pos"], [data-module-item="inventory"], [data-module-item="compras"], [data-module-item="cash"], [data-module-item="mermas"], [data-module-item="traslados"], [data-module-item="visitas"]');
    const opVisible = Array.from(opItems).some(el => !el.classList.contains('d-none'));
    const opSection = document.querySelector('[data-section="operacion"]');
    if (opSection) opSection.classList.toggle('d-none', !opVisible);

    const admItems = document.querySelectorAll('[data-module-item="users"], [data-module-item="roles"], [data-module-item="clients"], [data-module-item="catalog"], [data-module-item="bitacora"], [data-module-item="historial"], [data-module-item="reportes"], [data-module-item="configuracion"]');
    const admVisible = Array.from(admItems).some(el => !el.classList.contains('d-none'));
    const admSection = document.querySelector('[data-section="administracion"]');
    if (admSection) admSection.classList.toggle('d-none', !admVisible);

    // 3. Dashboard Module Cards
    document.querySelectorAll('[data-card-module]').forEach(el => {
        const modKey = el.getAttribute('data-card-module');
        const allowed = moduleAllowed[modKey] ?? false;
        el.classList.toggle('d-none', !allowed);
    });

    // 4. Dashboard KPI Cards
    const kpiSales = document.querySelector('[data-metric="sales_today"]');
    if (kpiSales) kpiSales.classList.toggle('d-none', !(isUserAdmin || window.hasPermission('VENTA_COBRAR')));

    const kpiStock = document.querySelector('[data-metric="critical_stock"]');
    if (kpiStock) kpiStock.classList.toggle('d-none', !(isUserAdmin || role === 'Bodeguero'));

    const kpiPayables = document.querySelector('[data-metric="payables_pending"]');
    if (kpiPayables) kpiPayables.classList.toggle('d-none', !isUserAdmin);

    const kpiCustomers = document.querySelector('[data-metric="new_customers"]');
    if (kpiCustomers) kpiCustomers.classList.toggle('d-none', !(isUserAdmin || role === 'Cajero'));
}

// Comprueba si el rol/permisos del usuario le permiten ver una pantalla
function canAccessView(viewKey) {
    if (viewKey === 'dashboard') return true;
    if (window.isAdmin()) return true;

    const role = window.getUserRole();
    if (viewKey === 'pos') return window.hasPermission('VENTA_COBRAR');
    if (viewKey === 'inventory') return window.hasPermission('INV_INGRESAR_MERCADERIA') || window.hasPermission('VENTA_COBRAR');
    if (viewKey === 'compras') return window.hasPermission('COMPRA_EMITIR_ORDEN') || window.hasPermission('INV_INGRESAR_MERCADERIA');
    if (viewKey === 'mermas') return window.hasPermission('INV_INGRESAR_MERCADERIA');
    if (viewKey === 'traslados') return window.hasPermission('INV_INGRESAR_MERCADERIA');
    if (viewKey === 'visitas') return window.hasPermission('VISITA_REGISTRAR');
    if (viewKey === 'cash' || viewKey === 'caja') return role === 'Cajero' || window.hasPermission('CAJA_CIERRE_CIEGAS');
    if (viewKey === 'catalog') return role === 'Bodeguero' || window.hasPermission('CATALOGO_ADMIN');
    if (viewKey === 'clients') return window.hasPermission('CLIENTE_ADMIN');
    if (viewKey === 'users' || viewKey === 'configuracion') return false;
    if (viewKey === 'roles') return false;
    if (viewKey === 'bitacora') return window.hasPermission('BITACORA_CONSULTAR');
    if (viewKey === 'historial') return window.hasPermission('REPORTE_VER');
    if (viewKey === 'reportes') return window.hasPermission('REPORTE_VER');
    if (viewKey === 'ventas') return window.hasPermission('REPORTE_VER') || window.hasPermission('VENTA_COBRAR');

    return false;
}

// Guardia de autenticación al inicializar la aplicación.
document.addEventListener('DOMContentLoaded', () => {
    if (hasActiveSession()) {
        showDashboard();
    } else {
        showLogin();
    }
});

// View Switcher for Auth Module
window.switchView = function(viewId) {
    authViews.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add('d-none');
    });
    const target = document.getElementById(viewId);
    if (target) {
        target.classList.remove('d-none');
    }
};

// ---------------------------------------------------------------------------
// Navegación SPA (Hash Routing): conmutación de contenedores + sincronización
// del menú lateral + persistencia de la vista activa en la URL (sin recarga).
// ---------------------------------------------------------------------------


function setActiveNav(viewKey) {
    document.querySelectorAll('[data-nav]').forEach(link => {
        const isActive = link.getAttribute('data-nav') === viewKey;
        link.classList.toggle('active', isActive);
        link.classList.toggle('text-white', isActive);
        link.classList.toggle('text-white-50', !isActive);
        if (isActive) link.setAttribute('aria-current', 'page');
        else link.removeAttribute('aria-current');
    });
}

// Lee el identificador de ruta desde el hash de la URL. Ruta vacía o desconocida
// se normaliza al Panel Principal.
function parseHash() {
    const raw = (location.hash || '').replace(/^#/, '');
    return mainViews.includes(raw) ? raw : 'dashboard';
}

// Renderiza la vista correspondiente con validación de RBAC

function updateTopbarHeader(viewKey) {
    const topbarTitle = document.getElementById('topbar-module-title');
    const topbarTurnBadge = document.getElementById('pos-turn-badge');
    const topbarHistoryBtn = document.getElementById('btn-pos-history');
    if (!topbarTitle) return;

    // Barra superior sobria y estática con el nombre del negocio (evita duplicidad de títulos)
    topbarTitle.innerHTML = '<i class="bi bi-shop text-teal"></i> <span>Regalito - Panajachel</span>';

    if (viewKey === 'pos') {
        if (topbarTurnBadge) topbarTurnBadge.classList.remove('d-none');
        if (topbarHistoryBtn) topbarHistoryBtn.classList.remove('d-none');
    } else {
        if (topbarTurnBadge) topbarTurnBadge.classList.add('d-none');
        if (topbarHistoryBtn) topbarHistoryBtn.classList.add('d-none');
    }
}
window.updateTopbarHeader = updateTopbarHeader;

function renderView(viewKey) {
    if (!mainViews.includes(viewKey)) viewKey = 'dashboard';

    if (!canAccessView(viewKey)) {
        if (typeof window.showToast === 'function') {
            window.showToast('No tienes permiso para acceder a este módulo.', 'danger');
        }
        viewKey = 'dashboard';
        if (location.hash !== '#dashboard') {
            location.hash = '#dashboard';
        }
    }

    if (currentView === viewKey) return;
    currentView = viewKey;

    document.querySelectorAll('[data-main-view]').forEach(container => {
        container.classList.add('d-none');
    });
    const target = document.querySelector(`[data-main-view="${viewKey}"]`);
    if (target) target.classList.remove('d-none');
    setActiveNav(viewKey);
    updateTopbarHeader(viewKey);
    if (typeof window.closeMobileSidebar === 'function') {
        window.closeMobileSidebar();
    }
    window.dispatchEvent(new CustomEvent('viewChanged', { detail: { view: viewKey } }));

    if (viewKey === 'dashboard' && typeof window.showDashboardModule === 'function') {
        window.showDashboardModule();
    }
    if (viewKey === 'users' && typeof window.showUsersModule === 'function') {
        window.showUsersModule();
    }
    if (viewKey === 'roles' && typeof window.showRolesModule === 'function') {
        window.showRolesModule();
    }
    if (viewKey === 'bitacora' && typeof window.showBitacoraModule === 'function') {
        window.showBitacoraModule();
    }
    if (viewKey === 'historial' && typeof window.showHistorialModule === 'function') {
        window.showHistorialModule();
    }
    if (viewKey === 'clients' && typeof window.showClientsModule === 'function') {
        window.showClientsModule();
    }
    if (viewKey === 'catalog' && typeof window.showCatalogModule === 'function') {
        window.showCatalogModule();
    }
    if (viewKey === 'cash' && typeof window.showCashModule === 'function') {
        window.showCashModule();
    }
    if (viewKey === 'reportes' && typeof window.showReportesModule === 'function') {
        window.showReportesModule();
    }
    if (viewKey === 'configuracion' && typeof window.showConfiguracionModule === 'function') {
        window.showConfiguracionModule();
    }
    if (viewKey === 'inventory' && typeof window.showInventoryModule === 'function') {
        window.showInventoryModule();
    }
    if (viewKey === 'compras' && typeof window.showComprasModule === 'function') {
        window.showComprasModule();
    }
    if (viewKey === 'pos' && typeof window.showPOSModule === 'function') {
        window.showPOSModule();
    }
    if (viewKey === 'mermas' && typeof window.showMermasModule === 'function') {
        window.showMermasModule();
    }
    if (viewKey === 'traslados' && typeof window.showTrasladosModule === 'function') {
        window.showTrasladosModule();
    }
    if (viewKey === 'visitas' && typeof window.showVisitasModule === 'function') {
        window.showVisitasModule();
    }
    if (viewKey === 'ventas' && typeof window.showVentasModule === 'function') {
        window.showVentasModule();
    }
}

// Navega a un módulo actualizando el hash de la URL sin recargar la página.
window.navigateTo = function(viewKey) {
    if (!hasActiveSession()) {
        showLogin();
        return;
    }

    if (!canAccessView(viewKey)) {
        if (typeof window.showToast === 'function') {
            window.showToast('No tienes permiso para acceder a este módulo.', 'danger');
        }
        if (location.hash !== '#dashboard') {
            location.hash = '#dashboard';
        }
        return;
    }

    if (!mainViews.includes(viewKey)) {
        openModule(viewKey);
        return;
    }

    if (location.hash === `#${viewKey}`) {
        renderView(viewKey);
        return;
    }
    location.hash = `#${viewKey}`;
};

// Soporte de avance/retroceso del navegador: sincroniza la vista con la ruta.
window.addEventListener('hashchange', () => {
    if (!hasActiveSession()) {
        const currentHash = (window.location.hash || '').replace(/^#/, '');
        if (!currentHash) {
            const isRecoveryActive = ['view-recover', 'view-verify', 'view-reset'].some(id => {
                const el = document.getElementById(id);
                return el && !el.classList.contains('d-none');
            });
            if (isRecoveryActive) return;
        }
        showLogin();
        return;
    }
    renderView(parseHash());
});

window.addEventListener('popstate', () => {
    if (!hasActiveSession()) {
        showLogin();
        return;
    }
    renderView(parseHash());
});

// Soporte para bfcache (Back/Forward Cache): evita mostrar vistas protegidas en caché sin sesión activa
window.addEventListener('pageshow', () => {
    if (!hasActiveSession()) {
        showLogin();
    }
});

// ---------------------------------------------------------------------------
// Accesos directos del Dashboard ("Módulos del Sistema")
// ---------------------------------------------------------------------------

const moduleLabels = {
    pos: 'POS / Ventas',
    inventory: 'Inventario / Bodega',
    compras: 'Compras',
    caja: 'Caja',
    cash: 'Caja',
    users: 'Usuarios / Personal',
    roles: 'Roles y Permisos',
    clients: 'Clientes',
    catalog: 'Catálogos',
    reportes: 'Reportes',
    configuracion: 'Configuración',
    bitacora: 'Bitácora',
    historial: 'Historial de Precios',
    mermas: 'Mermas',
    traslados: 'Traslados',
    visitas: 'Visitas de Seguimiento',
    ventas: 'Ventas',
};

// Abre un módulo desde el dashboard o navegación lateral
function openModule(moduleKey) {
    if (moduleKey === 'caja') moduleKey = 'cash';
    if (!canAccessView(moduleKey)) {
        if (typeof window.showToast === 'function') {
            window.showToast('No tienes permiso para acceder a este módulo.', 'danger');
        }
        return;
    }
    if (mainViews.includes(moduleKey)) {
        navigateTo(moduleKey);
        return;
    }
    const name = moduleLabels[moduleKey] || 'Módulo';
    if (typeof window.showToast === 'function') {
        window.showToast(`El módulo "${name}" se encuentra en construcción.`, 'info');
    }
}
window.openModule = openModule;

// 1. Login Logic

// 1a. Toggle mostrar/ocultar contraseña
window.toggleLoginPassword = function(event) {
    if (event) {
        event.preventDefault();
        event.stopPropagation();
    }
    const loginPassInput = document.getElementById('login-pass');
    const btnTogglePass = document.getElementById('btn-toggle-pass');
    if (!loginPassInput) return;

    const isPassword = loginPassInput.type === 'password' || loginPassInput.getAttribute('type') === 'password';
    const newType = isPassword ? 'text' : 'password';
    loginPassInput.type = newType;
    loginPassInput.setAttribute('type', newType);

    const icon = document.getElementById('btn-toggle-pass-icon') || (btnTogglePass ? btnTogglePass.querySelector('i') : null);
    if (icon) {
        icon.className = isPassword ? 'bi bi-eye text-muted' : 'bi bi-eye-slash text-muted';
    }
    if (btnTogglePass) {
        btnTogglePass.setAttribute('title', isPassword ? 'Ocultar contraseña' : 'Mostrar contraseña');
    }
    
    // Mantener cursor al final
    try {
        const len = loginPassInput.value.length;
        loginPassInput.setSelectionRange(len, len);
    } catch (_) {}
    loginPassInput.focus();
};

const btnTogglePass = document.getElementById('btn-toggle-pass');
if (btnTogglePass) {
    btnTogglePass.onclick = window.toggleLoginPassword;
}

// 1b. Helpers de estado del botón de login
const btnLoginSubmit = document.getElementById('btn-login-submit');
const loginBtnOriginalText = btnLoginSubmit ? btnLoginSubmit.innerHTML : '';

function setLoginLoading(loading) {
    if (!btnLoginSubmit) return;
    if (loading) {
        btnLoginSubmit.disabled = true;
        btnLoginSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Ingresando...';
    } else {
        btnLoginSubmit.disabled = false;
        btnLoginSubmit.innerHTML = loginBtnOriginalText;
    }
}

// 1c. Submit del formulario de login
document.getElementById('form-login').addEventListener('submit', async (e) => {
    e.preventDefault();
    const user = document.getElementById('login-user').value.trim();
    const pass = document.getElementById('login-pass').value.trim();
    const errorDiv = document.getElementById('login-error');
    errorDiv.classList.add('d-none');

    if (!user || !pass) {
        errorDiv.textContent = 'Por favor ingresa usuario y contraseña.';
        errorDiv.classList.remove('d-none');
        return;
    }

    const formData = new URLSearchParams();
    formData.append('username', user);
    formData.append('password', pass);

    setLoginLoading(true);

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: formData,
        });

        if (!response.ok) {
            if (response.status === 401) handleUnauthorized();
            throw new Error('Credenciales incorrectas o usuario inactivo');
        }

        const data = await response.json();

        // Manejo de opción 'Recordarme': guarda el nombre de usuario para prellenarlo, nunca la sesión completa
        const rememberMe = document.getElementById('remember-me');
        if (rememberMe && rememberMe.checked) {
            localStorage.setItem('remember_user', user);
        } else {
            localStorage.removeItem('remember_user');
        }

        const isUserAdmin = user.toLowerCase() === 'admin' || data.rol === 'Administradora';
        const displayName = isUserAdmin ? 'Administrador' : (data.nombre_completo || user);
        const permsJson = JSON.stringify(data.permisos || []);

        // Guardar sesión en sessionStorage (activa estrictamente durante la sesión del navegador)
        sessionStorage.setItem('jwt_token', data.access_token);
        sessionStorage.setItem('user_role', data.rol || '');
        sessionStorage.setItem('user_id_rol', data.id_rol || '');
        sessionStorage.setItem('user_permissions', permsJson);
        sessionStorage.setItem('user_name', user);
        sessionStorage.setItem('user_display_name', displayName);

        // Sincronizar en localStorage para compatibilidad con submódulos en la pestaña activa
        localStorage.setItem('jwt_token', data.access_token);
        localStorage.setItem('user_role', data.rol || '');
        localStorage.setItem('user_id_rol', data.id_rol || '');
        localStorage.setItem('user_permissions', permsJson);
        localStorage.setItem('user_name', user);
        localStorage.setItem('user_display_name', displayName);

        updateUserInfoUI();
        showDashboard();
    } catch (err) {
        errorDiv.textContent = err.message;
        errorDiv.classList.remove('d-none');
    } finally {
        setLoginLoading(false);
    }
});

// ---------------------------------------------------------------------------
// 3. RECUPERACIÓN DE CONTRASEÑAS (FLUJO COMPLETO CON CÓDIGO OTP)
// ---------------------------------------------------------------------------

let recoveryState = {
    identifier: '',
    email: '',
    reset_token: ''
};

// Formulario 1: Solicitar Código
const formRecover = document.getElementById('form-recover');
if (formRecover) {
    formRecover.addEventListener('submit', async (e) => {
        e.preventDefault();
        const input = document.getElementById('recover-email');
        const errAlert = document.getElementById('recover-error');
        const succAlert = document.getElementById('recover-success');
        const btnSubmit = document.getElementById('btn-recover-submit');

        if (errAlert) errAlert.classList.add('d-none');
        if (succAlert) succAlert.classList.add('d-none');

        const identifier = input ? input.value.trim() : '';
        if (!identifier) {
            if (errAlert) {
                errAlert.textContent = 'Ingresa tu correo electrónico o nombre de usuario.';
                errAlert.classList.remove('d-none');
            }
            return;
        }

        if (btnSubmit) {
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Enviando código...';
        }

        try {
            const res = await fetch(`${API_URL}/auth/recuperar-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ identifier })
            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
                const msg = data.detail || 'No se pudo procesar la solicitud de recuperación.';
                if (errAlert) {
                    errAlert.textContent = msg;
                    errAlert.classList.remove('d-none');
                } else {
                    showToast(msg, 'danger');
                }
                return;
            }

            recoveryState.identifier = identifier;
            recoveryState.email = data.email || identifier;

            // Actualizar vista de verificación
            const targetBadge = document.getElementById('verify-target-email');
            if (targetBadge) {
                targetBadge.textContent = recoveryState.email;
            }

            // Limpiar inputs de código completamente (el usuario debe revisar su correo real)
            const codeInputs = document.querySelectorAll('.code-input');
            codeInputs.forEach(inp => {
                inp.value = '';
            });

            const verifyErr = document.getElementById('verify-error');
            if (verifyErr) verifyErr.classList.add('d-none');

            showToast(data.message || 'Código de verificación enviado a tu correo.', 'success');
            switchView('view-verify');
            if (codeInputs[0]) codeInputs[0].focus();

        } catch (err) {
            if (errAlert) {
                errAlert.textContent = 'Error de conexión con el servidor. Intenta de nuevo.';
                errAlert.classList.remove('d-none');
            }
        } finally {
            if (btnSubmit) {
                btnSubmit.disabled = false;
                btnSubmit.textContent = 'Enviar Código';
            }
        }
    });
}

// Botón de reenvío de código
const btnResend = document.getElementById('btn-resend-code');
if (btnResend) {
    btnResend.addEventListener('click', async (e) => {
        e.preventDefault();
        if (!recoveryState.identifier && !recoveryState.email) {
            switchView('view-recover');
            return;
        }
        btnResend.textContent = 'Reenviando...';
        try {
            const res = await fetch(`${API_URL}/auth/recuperar-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ identifier: recoveryState.identifier || recoveryState.email })
            });
            const data = await res.json().catch(() => ({}));
            if (res.ok) {
                showToast('Nuevo código enviado a tu correo.', 'success');
                const codeInputs = document.querySelectorAll('.code-input');
                codeInputs.forEach(inp => {
                    inp.value = '';
                });
                if (codeInputs[0]) codeInputs[0].focus();
            } else {
                showToast(data.detail || 'Error al reenviar código.', 'danger');
            }
        } catch (err) {
            showToast('Error de conexión.', 'danger');
        } finally {
            btnResend.textContent = 'Reenviar código';
        }
    });
}

// Formulario 2: Verificar Código (6 dígitos)
const codeInputs = document.querySelectorAll('.code-input');
codeInputs.forEach((input, index) => {
    input.addEventListener('input', (e) => {
        // Solo dígitos
        e.target.value = e.target.value.replace(/\D/g, '');
        if (e.target.value.length >= 1) {
            e.target.value = e.target.value.slice(0, 1);
            if (index < codeInputs.length - 1) {
                codeInputs[index + 1].focus();
            }
        }
    });
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Backspace' && e.target.value === '') {
            if (index > 0) {
                codeInputs[index - 1].focus();
            }
        }
    });
    input.addEventListener('paste', (e) => {
        e.preventDefault();
        const pasted = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '');
        if (pasted.length) {
            codeInputs.forEach((inp, i) => {
                inp.value = pasted[i] || '';
            });
            const lastFilled = Math.min(pasted.length, codeInputs.length) - 1;
            if (lastFilled >= 0 && codeInputs[lastFilled]) codeInputs[lastFilled].focus();
        }
    });
});

const formVerify = document.getElementById('form-verify');
if (formVerify) {
    formVerify.addEventListener('submit', async (e) => {
        e.preventDefault();
        const errAlert = document.getElementById('verify-error');
        const btnSubmit = document.getElementById('btn-verify-submit');
        if (errAlert) errAlert.classList.add('d-none');

        const code = Array.from(codeInputs).map(i => i.value.trim()).join('');
        if (code.length !== 6) {
            if (errAlert) {
                errAlert.textContent = 'Por favor ingresa los 6 dígitos del código.';
                errAlert.classList.remove('d-none');
            }
            return;
        }

        if (btnSubmit) {
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Verificando...';
        }

        try {
            const res = await fetch(`${API_URL}/auth/verificar-codigo`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    email: recoveryState.email || recoveryState.identifier,
                    codigo: code
                })
            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
                const msg = data.detail || 'Código incorrecto o expirado.';
                if (errAlert) {
                    errAlert.textContent = msg;
                    errAlert.classList.remove('d-none');
                } else {
                    showToast(msg, 'danger');
                }
                return;
            }

            recoveryState.reset_token = data.reset_token;
            showToast('Código verificado con éxito.', 'success');

            const resetErr = document.getElementById('reset-error');
            if (resetErr) resetErr.classList.add('d-none');
            const passInput = document.getElementById('reset-pass');
            const confirmInput = document.getElementById('reset-pass-confirm');
            if (passInput) passInput.value = '';
            if (confirmInput) confirmInput.value = '';

            switchView('view-reset');
            if (passInput) passInput.focus();

        } catch (err) {
            if (errAlert) {
                errAlert.textContent = 'Error de conexión con el servidor. Intenta de nuevo.';
                errAlert.classList.remove('d-none');
            }
        } finally {
            if (btnSubmit) {
                btnSubmit.disabled = false;
                btnSubmit.textContent = 'Verificar Código';
            }
        }
    });
}

// Formulario 3: Restablecer Contraseña
const formReset = document.getElementById('form-reset');
if (formReset) {
    formReset.addEventListener('submit', async (e) => {
        e.preventDefault();
        const pass = document.getElementById('reset-pass')?.value || '';
        const confirm = document.getElementById('reset-pass-confirm')?.value || '';
        const errorDiv = document.getElementById('reset-error');
        const btnSubmit = document.getElementById('btn-reset-submit');

        if (errorDiv) errorDiv.classList.add('d-none');

        if (pass.length < 6) {
            if (errorDiv) {
                errorDiv.textContent = 'La contraseña debe tener al menos 6 caracteres.';
                errorDiv.classList.remove('d-none');
            }
            return;
        }

        if (pass !== confirm) {
            if (errorDiv) {
                errorDiv.textContent = 'Las contraseñas no coinciden.';
                errorDiv.classList.remove('d-none');
            }
            return;
        }

        if (btnSubmit) {
            btnSubmit.disabled = true;
            btnSubmit.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Guardando contraseña...';
        }

        try {
            const res = await fetch(`${API_URL}/auth/reset-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    reset_token: recoveryState.reset_token,
                    email: recoveryState.email,
                    nueva_password: pass
                })
            });

            const data = await res.json().catch(() => ({}));

            if (!res.ok) {
                const msg = data.detail || 'No se pudo restablecer la contraseña.';
                if (errorDiv) {
                    errorDiv.textContent = msg;
                    errorDiv.classList.remove('d-none');
                } else {
                    showToast(msg, 'danger');
                }
                return;
            }

            showToast('Contraseña restablecida exitosamente. Ahora puedes ingresar.', 'success');
            
            // Limpiar estado y redirigir a Login con usuario precargado
            const loginUser = document.getElementById('login-user');
            if (loginUser) loginUser.value = recoveryState.identifier || recoveryState.email;
            const loginPass = document.getElementById('login-pass');
            if (loginPass) {
                loginPass.value = '';
                loginPass.focus();
            }

            recoveryState = { identifier: '', email: '', reset_token: '' };
            switchView('view-login');

        } catch (err) {
            if (errorDiv) {
                errorDiv.textContent = 'Error de conexión con el servidor. Intenta de nuevo.';
                errorDiv.classList.remove('d-none');
            }
        } finally {
            if (btnSubmit) {
                btnSubmit.disabled = false;
                btnSubmit.textContent = 'Guardar Contraseña';
            }
        }
    });
}

let healthCheckInterval = null;

async function checkHealth() {
    try {
        const response = await fetch(`${API_URL}/health`);
        if (!response.ok) {
            throw new Error('Health check failed');
        }
        const data = await response.json();
        if (data.status !== 'ok') {
            throw new Error('Database disconnected');
        }
    } catch (error) {
        if (typeof window.showToast === 'function') {
            window.showToast('Problemas de conexión con el servidor', 'danger');
        }
    }
}

// 6. Dashboard Switch & Logout
async function showDashboard() {
    authModule.classList.add('d-none');
    systemModule.classList.remove('d-none');
    
    // Check health once before showing dashboard fully, and set interval
    await checkHealth();
    if (healthCheckInterval) clearInterval(healthCheckInterval);
    healthCheckInterval = setInterval(checkHealth, 30000); // 30 seconds

    // Set dynamic date
    const now = new Date();
    const options = { month: 'long', year: 'numeric' };
    const formattedDate = now.toLocaleDateString('es-GT', options);
    const headerDate = document.getElementById('header-date');
    if (headerDate) {
        headerDate.innerText = formattedDate.charAt(0).toUpperCase() + formattedDate.slice(1);
    }

    updateUserInfoUI();
    applyRoleRestrictions();

    // Campanita de notificaciones: alertas de stock pendientes (al iniciar y tras login)
    if (typeof window.cargarNotificaciones === 'function') {
        window.cargarNotificaciones();
    }

    // Restaura la vista activa desde la URL (hash) si existe y tiene permisos; si no, Panel Principal.
    let initialView = parseHash();
    if (!canAccessView(initialView)) {
        initialView = 'dashboard';
    }
    if (location.hash !== `#${initialView}`) {
        location.hash = `#${initialView}`;
    }
    currentView = null;
    renderView(initialView);
}

const btnLogout = document.getElementById('btn-logout');
if (btnLogout) {
    btnLogout.addEventListener('click', (e) => {
        e.preventDefault();
        showLogin();
    });
}

/* ===== Control de Navegación: Sidebar Colapsable y Adaptabilidad Móvil (< 768px) ===== */
(function () {
    var KEY = 'sidebarCollapsed';
    var MOBILE_BREAKPOINT = 768; // Breakpoint estándar (Bootstrap md)

    function isMobile() {
        return window.innerWidth < MOBILE_BREAKPOINT;
    }

    function applySidebarDesktop(collapsed) {
        var m = document.getElementById('system-module');
        if (!m) return;
        if (isMobile()) {
            m.classList.remove('sidebar-collapsed');
            return;
        }
        m.classList.toggle('sidebar-collapsed', collapsed);
        document.querySelectorAll('.sidebar .sidebar-link').forEach(function (a) {
            if (collapsed) {
                var span = a.querySelector('span');
                var text = span ? span.textContent.trim() : a.textContent.trim();
                a.setAttribute('title', text);
            } else {
                a.removeAttribute('title');
            }
        });
    }

    function openMobileSidebar() {
        var m = document.getElementById('system-module');
        if (!m) return;
        // Garantizar que en móvil el texto SIEMPRE esté visible y no colapsado
        m.classList.remove('sidebar-collapsed');
        m.classList.add('mobile-sidebar-open');
    }

    function closeMobileSidebar() {
        var m = document.getElementById('system-module');
        if (!m) return;
        m.classList.remove('mobile-sidebar-open');
    }

    function toggleMobileSidebar() {
        var m = document.getElementById('system-module');
        if (!m) return;
        if (m.classList.contains('mobile-sidebar-open')) {
            closeMobileSidebar();
        } else {
            openMobileSidebar();
        }
    }

    // Exponer globalmente para cierre al navegar
    window.openMobileSidebar = openMobileSidebar;
    window.closeMobileSidebar = closeMobileSidebar;
    window.toggleMobileSidebar = toggleMobileSidebar;

    document.addEventListener('DOMContentLoaded', function () {
        var collapsed = false;
        try { collapsed = localStorage.getItem(KEY) === '1'; } catch (e) {}
        if (!isMobile()) {
            applySidebarDesktop(collapsed);
        }

        // Botón hamburguesa (☰) en la cabecera: hace el menú "menos ancho" / alterna colapso
        var btnToggle = document.getElementById('btn-sidebar-toggle');
        if (btnToggle) {
            btnToggle.addEventListener('click', function (e) {
                e.stopPropagation();
                if (isMobile()) {
                    toggleMobileSidebar();
                } else {
                    var m = document.getElementById('system-module');
                    var now = !m.classList.contains('sidebar-collapsed');
                    applySidebarDesktop(now);
                    try { localStorage.setItem(KEY, now ? '1' : '0'); } catch (err) {}
                }
            });
        }

        // Botón cerrar (X) dentro del menú off-canvas móvil
        var btnClose = document.getElementById('btn-sidebar-close');
        if (btnClose) {
            btnClose.addEventListener('click', function (e) {
                e.preventDefault();
                closeMobileSidebar();
            });
        }

        // Clic en el backdrop exterior semi-transparente
        var backdrop = document.getElementById('sidebar-mobile-backdrop');
        if (backdrop) {
            backdrop.addEventListener('click', function () {
                closeMobileSidebar();
            });
        }

        // Clic en cualquier enlace del menú lateral cierra el menú en móviles
        document.querySelectorAll('.sidebar .sidebar-link').forEach(function (link) {
            link.addEventListener('click', function () {
                if (isMobile()) {
                    closeMobileSidebar();
                }
            });
        });

        // Tecla Escape para accesibilidad
        document.addEventListener('keydown', function (e) {
            if (e.key === 'Escape') {
                closeMobileSidebar();
            }
        });

        // Sincronización al redimensionar pantalla (únicamente adapta cuando cruza el breakpoint)
        window.addEventListener('resize', function () {
            if (!isMobile()) {
                closeMobileSidebar();
                var saved = false;
                try { saved = localStorage.getItem(KEY) === '1'; } catch (e) {}
                applySidebarDesktop(saved);
            } else {
                var m = document.getElementById('system-module');
                if (m) m.classList.remove('sidebar-collapsed');
            }
        });
    });
})();

/* ==========================================================================
   MODO OSCURO / CLARO (THEME SWITCHER)
   ==========================================================================
   Permite al usuario alternar entre Modo Claro (Light) y Modo Oscuro (Carbón).
   - Persiste la preferencia en localStorage ('themePreference').
   - Modifica los atributos 'data-theme' y 'data-bs-theme' en <html>.
   - Actualiza de forma interactiva el ícono del botón (Sol / Luna).
   - Respeta el esquema preferido por el sistema si no hay elección manual.
   ========================================================================== */
(function () {
    var THEME_KEY = 'themePreference';

    function getActiveTheme() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    }

    function updateThemeIcon(theme) {
        var icon = document.getElementById('theme-icon');
        var btn = document.getElementById('btn-theme-toggle');
        if (!icon) return;

        if (theme === 'dark') {
            icon.className = 'bi bi-sun-fill text-warning fs-6';
            if (btn) btn.setAttribute('title', 'Cambiar a Modo Claro');
        } else {
            icon.className = 'bi bi-moon-stars-fill text-secondary fs-6';
            if (btn) btn.setAttribute('title', 'Cambiar a Modo Oscuro');
        }
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        document.documentElement.setAttribute('data-bs-theme', theme);
        try {
            localStorage.setItem(THEME_KEY, theme);
        } catch (e) {
            console.warn('No se pudo guardar la preferencia de tema en localStorage:', e);
        }
        updateThemeIcon(theme);
        window.dispatchEvent(new CustomEvent('themeChanged', { detail: { theme: theme } }));
    }

    function toggleTheme() {
        var current = getActiveTheme();
        var next = current === 'dark' ? 'light' : 'dark';
        applyTheme(next);
    }

    // Exponer funciones globales para facilitar llamadas o depuración
    window.toggleTheme = toggleTheme;
    window.setTheme = applyTheme;

    // Inicializar evento al cargar el DOM
    document.addEventListener('DOMContentLoaded', function () {
        var current = getActiveTheme();
        updateThemeIcon(current);

        var btnToggle = document.getElementById('btn-theme-toggle');
        if (btnToggle) {
            btnToggle.addEventListener('click', function (e) {
                e.preventDefault();
                toggleTheme();
            });
        }
    });

    // Detectar cambios en las preferencias de color del sistema operativo
    if (window.matchMedia) {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
            try {
                if (!localStorage.getItem(THEME_KEY)) {
                    applyTheme(e.matches ? 'dark' : 'light');
                }
            } catch (err) {}
        });
    }
})();
