// Curiosidades El Regalito - Auth & Dashboard Logic
const API_URL = '/api';
const authModule = document.getElementById('auth-module');
const systemModule = document.getElementById('system-module');

// Array of all auth views to easily hide them
const authViews = ['view-login', 'view-register', 'view-recover', 'view-verify', 'view-reset'];

// ---------------------------------------------------------------------------
// Auth Guard: control de acceso y redirección
// ---------------------------------------------------------------------------

function hasActiveSession() {
    return !!localStorage.getItem('jwt_token');
}

// Limpia la sesión local y muestra la pantalla de Login (sin recarga innecesaria).
function showLogin() {
    localStorage.removeItem('jwt_token');
    systemModule.classList.add('d-none');
    authModule.classList.remove('d-none');
    authViews.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.classList.add('d-none');
    });
    const login = document.getElementById('view-login');
    if (login) login.classList.remove('d-none');
}

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
}

// ---------------------------------------------------------------------------
// Navegación SPA (Hash Routing): conmutación de contenedores + sincronización
// del menú lateral + persistencia de la vista activa en la URL (sin recarga).
// ---------------------------------------------------------------------------

const mainViews = ['dashboard', 'users', 'catalog'];

let currentView = null;

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

// Renderiza la vista correspondiente (conmutación de contenedores y sidebar).
function renderView(viewKey) {
    if (!mainViews.includes(viewKey)) viewKey = 'dashboard';
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
}

// Navega a un módulo actualizando el hash de la URL sin recargar la página.
// El cambio de hash dispara 'hashchange' -> renderView().
window.navigateTo = function(viewKey) {
    if (!hasActiveSession()) {
        showLogin();
        return;
    }
    if (!mainViews.includes(viewKey)) viewKey = 'dashboard';
    if (location.hash === `#${viewKey}`) {
        renderView(viewKey);
        return;
    }
    location.hash = viewKey;
}

// Soporte de avance/retroceso del navegador: sincroniza la vista con la ruta.
window.addEventListener('hashchange', () => {
    if (!hasActiveSession()) {
        showLogin();
        return;
    }
    renderView(parseHash());
});

// ---------------------------------------------------------------------------
// Accesos directos del Dashboard ("Módulos del Sistema")
// ---------------------------------------------------------------------------

const moduleLabels = {
    pos: 'POS / Ventas',
    inventario: 'Inventario / Bodega',
    compras: 'Compras',
    caja: 'Caja',
    users: 'Usuarios / Personal',
    catalog: 'Catálogos',
    reportes: 'Reportes',
    configuracion: 'Configuración',
};

// Abre un módulo desde el dashboard: navega si ya existe; avisa con un toast si
// está en construcción (evita pantallas en blanco o interfaz congelada).
window.openModule = function(moduleKey) {
    if (mainViews.includes(moduleKey)) {
        navigateTo(moduleKey);
        return;
    }
    const name = moduleLabels[moduleKey] || 'Módulo';
    if (typeof window.showToast === 'function') {
        window.showToast(`El módulo "${name}" se encuentra en construcción.`, 'info');
    }
};

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
            body: formData
        });

        if (!response.ok) {
            if (response.status === 401) handleUnauthorized();
            throw new Error('Credenciales incorrectas o usuario inactivo');
        }

        const data = await response.json();
        localStorage.setItem('jwt_token', data.access_token);
        
        // Setup dashboard data
        const payload = JSON.parse(atob(data.access_token.split('.')[1]));
        document.getElementById('sidebar-username').innerText = payload.sub;
        document.getElementById('header-greeting').innerText = `¡Hola, ${payload.sub}!`;
        
        showDashboard();
    } catch (err) {
        errorDiv.textContent = err.message;
        errorDiv.classList.remove('d-none');
    }
});

// 2. Registration Validation (Mock logic for frontend as requested)
document.getElementById('form-register').addEventListener('submit', (e) => {
    e.preventDefault();
    const pass = document.getElementById('reg-pass').value;
    const confirm = document.getElementById('reg-pass-confirm').value;
    const errorDiv = document.getElementById('reg-error');
    
    if (pass !== confirm) {
        errorDiv.textContent = 'Las contraseñas no coinciden.';
        errorDiv.classList.remove('d-none');
        return;
    }
    
    if (pass.length < 6) {
        errorDiv.textContent = 'La contraseña debe tener al menos 6 caracteres.';
        errorDiv.classList.remove('d-none');
        return;
    }

    errorDiv.classList.add('d-none');
    alert('Usuario registrado exitosamente (Mock Frontend).');
    switchView('view-login');
});

// 3. Recover Password
document.getElementById('form-recover').addEventListener('submit', (e) => {
    e.preventDefault();
    // Simulate sending email
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
    // Simulate verification
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
    document.getElementById('header-date').innerText = formattedDate.charAt(0).toUpperCase() + formattedDate.slice(1);

    // Restaura la vista activa desde la URL (hash) si existe; si no, Panel Principal.
    currentView = null;
    renderView(parseHash());
}

document.getElementById('btn-logout').addEventListener('click', () => {
    showLogin();
});