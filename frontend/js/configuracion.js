// ============================================================================
// Módulo de Configuración
// ============================================================================

let isConfiguracionLoaded = false;

window.showConfiguracionModule = async function() {
    if (!window.isAdmin()) {
        if (typeof window.showToast === 'function') {
            window.showToast('No tienes permiso para acceder a este módulo.', 'danger');
        }
        window.navigateTo('dashboard');
        return;
    }

    if (!isConfiguracionLoaded) {
        await cargarConfiguracion();
        isConfiguracionLoaded = true;
    }
};

async function cargarConfiguracion() {
    try {
        const token = localStorage.getItem('jwt_token');
        if (!token) {
            if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
            return;
        }

        const btnSave = document.getElementById('btn-save-config');
        if (btnSave) {
            btnSave.disabled = true;
            btnSave.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Cargando...';
        }

        const response = await fetch('/api/configuracion/', {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (response.status === 401) {
            if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
            return;
        }

        if (!response.ok) {
            throw new Error(`Error HTTP: ${response.status}`);
        }

        const config = await response.json();
        
        const nitInput = document.getElementById('config-nit');
        const razonSocialInput = document.getElementById('config-razon-social');
        const direccionInput = document.getElementById('config-direccion');
        const tokenFelInput = document.getElementById('config-token-fel');

        if (nitInput && config['NIT']) nitInput.value = config['NIT'];
        if (razonSocialInput && config['Razón Social']) razonSocialInput.value = config['Razón Social'];
        if (direccionInput && config['Dirección']) direccionInput.value = config['Dirección'];
        if (tokenFelInput && config['Token FEL']) tokenFelInput.value = config['Token FEL'];

    } catch (error) {
        console.error('Error al cargar configuración:', error);
        window.showToast('Error al cargar los parámetros de configuración.', 'danger');
    } finally {
        const btnSave = document.getElementById('btn-save-config');
        if (btnSave) {
            btnSave.disabled = false;
            btnSave.innerHTML = 'Guardar Cambios';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const configForm = document.getElementById('configuracion-form');
    if (configForm) {
        configForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            if (!window.isAdmin()) {
                window.showToast('Permiso denegado.', 'danger');
                return;
            }

            const token = localStorage.getItem('jwt_token');
            if (!token) {
                if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
                return;
            }

            const nit = document.getElementById('config-nit').value.trim();
            const razonSocial = document.getElementById('config-razon-social').value.trim();
            const direccion = document.getElementById('config-direccion').value.trim();
            const tokenFel = document.getElementById('config-token-fel').value.trim();

            if (!nit || !razonSocial) {
                window.showToast('El NIT y la Razón Social son obligatorios.', 'warning');
                return;
            }

            const btnSave = document.getElementById('btn-save-config');
            btnSave.disabled = true;
            btnSave.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Guardando...';

            try {
                const response = await fetch('/api/configuracion/', {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        "NIT": nit,
                        "Razón Social": razonSocial,
                        "Dirección": direccion,
                        "Token FEL": tokenFel
                    })
                });

                if (response.status === 401) {
                    if (typeof window.handleUnauthorized === 'function') window.handleUnauthorized();
                    return;
                }

                if (!response.ok) {
                    const data = await response.json();
                    throw new Error(data.detail || `Error HTTP: ${response.status}`);
                }

                window.showToast('Configuración actualizada exitosamente', 'success');

            } catch (error) {
                console.error('Error al guardar configuración:', error);
                window.showToast(`Error al guardar: ${error.message}`, 'danger');
            } finally {
                btnSave.disabled = false;
                btnSave.innerHTML = 'Guardar Cambios';
            }
        });
    }

    // Toggle Password Visibility
    const toggleBtn = document.getElementById('toggle-token-visibility');
    const tokenInput = document.getElementById('config-token-fel');
    if (toggleBtn && tokenInput) {
        toggleBtn.addEventListener('click', () => {
            const type = tokenInput.getAttribute('type') === 'password' ? 'text' : 'password';
            tokenInput.setAttribute('type', type);
            const icon = toggleBtn.querySelector('i');
            if (type === 'text') {
                icon.classList.replace('bi-eye', 'bi-eye-slash');
            } else {
                icon.classList.replace('bi-eye-slash', 'bi-eye');
            }
        });
    }
});
