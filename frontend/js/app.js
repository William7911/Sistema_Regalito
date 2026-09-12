// Curiosidades El Regalito - Auth & Dashboard Logic
const API_URL = '/api';
const authModule = document.getElementById('auth-module');
const systemModule = document.getElementById('system-module');

// Array of all auth views to easily hide them
const authViews = ['view-login', 'view-register', 'view-recover', 'view-verify', 'view-reset'];

// Check token on load
document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('jwt_token');
    if (token) {
        showDashboard();
    }
});

// View Switcher for Auth Module
window.switchView = function(viewId) {
    authViews.forEach(id => {
        document.getElementById(id).classList.add('d-none');
    });
    document.getElementById(viewId).classList.remove('d-none');
}

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
}

document.getElementById('btn-logout').addEventListener('click', () => {
    localStorage.removeItem('jwt_token');
    location.reload();
});
