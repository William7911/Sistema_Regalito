// Curiosidades El Regalito - Auth & Dashboard Logic
const API_URL = '/api';
const authModule = document.getElementById('auth-module');
const systemModule = document.getElementById('system-module');

// Array of all auth views to easily hide them
const authViews = ['view-login', 'view-recover', 'view-verify', 'view-reset'];
const mainViews = ['dashboard', 'users', 'catalog', 'cash'];
let currentView = null;

// ---------------------------------------------------------------------------
// Toast Notification Utility (Defensivo, sin alert())
// ---------------------------------------------------------------------------

window.showToast = function(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container || !window.bootstrap) return;
    const colors = {
        success: 'text-bg-success',
        danger: 'text-bg-danger',
        warning: 'text-bg-warning',
        info: 'text-bg-info',
    };
    const el = document.createElement('div');
    el.className = `toast align-items-center text-white border-0 ${colors[type] || 'text-bg-info'}`;
    el.setAttribute('role', 'alert');
    el.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Cerrar"></button>
        </div>`;
    container.appendChild(el);
    const toast = new bootstrap.Toast(el, { delay: 3500 });
    toast.show();
    el.addEventListener('hidden.bs.toast', () => el.remove());
};

// ---------------------------------------------------------------------------
// RBAC Helpers (Control de Acceso Basado en Roles y Permisos)
// ---------------------------------------------------------------------------

window.getUserRole = function() {
    return localStorage.getItem('user_role') || '';
};

window.getUserPermissions = function() {
    try {
        return JSON.parse(localStorage.getItem('user_permissions') || '[]');
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

// ---------------------------------------------------------------------------
// Auth Guard: control de acceso y redirección
// ---------------------------------------------------------------------------

function hasActiveSession() {
    return !!localStorage.getItem('jwt_token');
}

// Limpia completamente la sesión local y muestra la pantalla de Login sin residuos.
function showLogin() {
    // 1. Limpieza total de almacenamiento
    localStorage.clear();
    sessionStorage.clear();

    // 2. Limpieza de estado en memoria y sanitización de URL sin recarga
    currentView = null;
    if (window.location.hash) {
        history.replaceState(null, '', window.location.pathname + window.location.search);
    }

    // 3. Limpieza de formularios de autenticación
    const loginUser = document.getElementById('login-user');
    const loginPass = document.getElementById('login-pass');
    const loginError = document.getElementById('login-error');
    if (loginUser) loginUser.value = '';
    if (loginPass) loginPass.value = '';
    if (loginError) {
        loginError.textContent = '';
        loginError.classList.add('d-none');
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

// Interceptor global: cualquier petición con 401 limpia la sesión y redirige a Login.
const nativeFetch = window.fetch;
window.fetch = function (...args) {
    return nativeFetch.apply(this, args).then((response) => {
        if (response.status === 401 && !response.url.endsWith('/auth/login')) {
            handleUnauthorized();
        }
        return response;
    });
};

// Actualiza el nombre visible y badge de rol en el header y sidebar
function updateUserInfoUI() {
    const rawUser = localStorage.getItem('user_name') || '';
    const role = localStorage.getItem('user_role') || '';
    let displayName = localStorage.getItem('user_display_name');

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
        pos: window.hasPermission('VENTA_COBRAR'),
        inventario: window.hasPermission('INV_INGRESAR_MERCADERIA'),
        compras: window.hasPermission('COMPRA_EMITIR_ORDEN'),
        cash: isUserAdmin || role === 'Cajero',
        caja: isUserAdmin || role === 'Cajero',
        users: isUserAdmin,
        catalog: isUserAdmin || role === 'Bodeguero',
        reportes: isUserAdmin,
        configuracion: isUserAdmin,
    };

    // 1. Sidebar Items
    document.querySelectorAll('[data-module-item]').forEach(el => {
        const modKey = el.getAttribute('data-module-item');
        const allowed = moduleAllowed[modKey] ?? false;
        el.classList.toggle('d-none', !allowed);
    });

    // 2. Sidebar Section Headers
    const opItems = document.querySelectorAll('[data-module-item="pos"], [data-module-item="inventario"], [data-module-item="compras"], [data-module-item="cash"]');
    const opVisible = Array.from(opItems).some(el => !el.classList.contains('d-none'));
    const opSection = document.querySelector('[data-section="operacion"]');
    if (opSection) opSection.classList.toggle('d-none', !opVisible);

    const admItems = document.querySelectorAll('[data-module-item="users"], [data-module-item="catalog"], [data-module-item="reportes"], [data-module-item="configuracion"]');
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
    if (viewKey === 'inventario') return window.hasPermission('INV_INGRESAR_MERCADERIA');
    if (viewKey === 'compras') return window.hasPermission('COMPRA_EMITIR_ORDEN');
    if (viewKey === 'cash' || viewKey === 'caja') return role === 'Cajero';
    if (viewKey === 'catalog') return role === 'Bodeguero';
    if (viewKey === 'users' || viewKey === 'reportes' || viewKey === 'configuracion') return false;

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
        document.getElementById(id).classList.add('d-none');
    });
    document.getElementById(viewId).classList.remove('d-none');
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

    if (viewKey === 'users' && typeof window.showUsersModule === 'function') {
        window.showUsersModule();
    }
    if (viewKey === 'catalog' && typeof window.showCatalogModule === 'function') {
        window.showCatalogModule();
    }
    if (viewKey === 'cash' && typeof window.showCashModule === 'function') {
        window.showCashModule();
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
    inventario: 'Inventario / Bodega',
    compras: 'Compras',
    caja: 'Caja',
    cash: 'Caja',
    users: 'Usuarios / Personal',
    catalog: 'Catálogos',
    reportes: 'Reportes',
    configuracion: 'Configuración',
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
        localStorage.setItem('jwt_token', data.access_token);
        localStorage.setItem('user_role', data.rol || '');
        localStorage.setItem('user_permissions', JSON.stringify(data.permisos || []));
        localStorage.setItem('user_name', user);

        const isUserAdmin = user.toLowerCase() === 'admin' || data.rol === 'Administradora';
        const displayName = isUserAdmin ? 'Administrador' : (data.nombre_completo || user);
        localStorage.setItem('user_display_name', displayName);

        updateUserInfoUI();
        showDashboard();
    } catch (err) {
        errorDiv.textContent = err.message;
        errorDiv.classList.remove('d-none');
    }
});

// 3. Recover Password
document.getElementById('form-recover').addEventListener('submit', (e) => {
    e.preventDefault();
    alert('Código de verificación enviado a tu correo.');
    switchView('view-verify');
});

// 4. Verify Code Auto-advance
const codeInputs = document.querySelectorAll('.code-input');
codeInputs.forEach((input, index) => {
    input.addEventListener('input', (e) => {
        if (e.target.value.length === 1) {
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
});

document.getElementById('form-verify').addEventListener('submit', (e) => {
    e.preventDefault();
    switchView('view-reset');
});

// 5. Reset Password
document.getElementById('form-reset').addEventListener('submit', (e) => {
    e.preventDefault();
    const pass = document.getElementById('reset-pass').value;
    const confirm = document.getElementById('reset-pass-confirm').value;
    const errorDiv = document.getElementById('reset-error');
    
    if (pass !== confirm) {
        errorDiv.textContent = 'Las contraseñas no coinciden.';
        errorDiv.classList.remove('d-none');
        return;
    }

    errorDiv.classList.add('d-none');
    alert('Contraseña actualizada correctamente.');
    switchView('view-login');
});

// 6. Dashboard Switch & Logout
function showDashboard() {
    authModule.classList.add('d-none');
    systemModule.classList.remove('d-none');
    
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