// Curiosidades El Regalito - Sincronización Offline SQLite (Fase 2 de 6)

document.addEventListener('DOMContentLoaded', () => {
    const syncModal = document.getElementById('sync-modal');
    const btnRunSync = document.getElementById('btn-run-sync');

    if (syncModal) {
        syncModal.addEventListener('show.bs.modal', () => {
            loadSyncStatus();
            loadSyncPreview();
        });
    }

    if (btnRunSync) {
        btnRunSync.addEventListener('click', runLocalSync);
    }

    // Inicializar indicador tras login
    setTimeout(loadSyncStatus, 1000);
});

async function loadSyncStatus() {
    const token = localStorage.getItem('jwt_token');
    if (!token) return;

    try {
        const resp = await fetch('/api/sync/status', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!resp.ok) return;

        const data = await resp.json();
        const statusText = document.getElementById('sync-modal-status-text');
        const lastDateText = document.getElementById('sync-modal-last-date');
        const badgeText = document.getElementById('sync-text-indicator');
        const badgeIcon = document.getElementById('sync-icon-indicator');

        if (data.initialized && data.file_exists) {
            const sizeKb = (data.file_size_bytes / 1024).toFixed(1);
            const prods = data.counts.productos || 0;
            const users = data.counts.usuarios || 0;

            if (statusText) {
                statusText.innerHTML = `<span class="badge bg-success me-1">Inicializada</span> ${sizeKb} KB | ${prods} productos | ${users} usuarios`;
            }
            if (lastDateText) {
                lastDateText.textContent = `Última sincronización: ${data.last_sync ? new Date(data.last_sync).toLocaleString('es-GT') : '-'}`;
            }
            if (badgeText) badgeText.textContent = `${prods} prod. locales`;
            if (badgeIcon) {
                badgeIcon.className = 'bi bi-cloud-check-fill text-success';
            }
        } else {
            if (statusText) {
                statusText.innerHTML = `<span class="badge bg-warning text-dark me-1">Pendiente</span> Base local no inicializada aún.`;
            }
            if (lastDateText) lastDateText.textContent = 'Última sincronización: Nunca';
            if (badgeText) badgeText.textContent = 'Sin sincronizar';
            if (badgeIcon) {
                badgeIcon.className = 'bi bi-cloud-slash-fill text-warning';
            }
        }
    } catch (e) {
        console.warn('No se pudo verificar estado de sincronización:', e);
    }
}

async function runLocalSync() {
    const token = localStorage.getItem('jwt_token');
    if (!token) {
        if (window.showToast) window.showToast('Debes iniciar sesión para sincronizar', 'warning');
        return;
    }

    const btnRunSync = document.getElementById('btn-run-sync');
    const spinner = document.getElementById('sync-spinner-icon');
    const btnText = document.getElementById('sync-btn-text');

    if (btnRunSync) btnRunSync.disabled = true;
    if (spinner) spinner.className = 'spinner-border spinner-border-sm';
    if (btnText) btnText.textContent = 'Sincronizando...';

    try {
        const resp = await fetch('/api/sync/pull-local', {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        const data = await resp.json();
        if (resp.ok && data.status === 'success') {
            if (window.showToast) {
                const pCount = data.counts.producto || 0;
                const uCount = data.counts.usuario || 0;
                window.showToast(`Sincronización exitosa: ${pCount} productos y ${uCount} usuarios replicados a SQLite`, 'success');
            }
            await loadSyncStatus();
            await loadSyncPreview();
        } else {
            const err = data.detail || 'Error al sincronizar con SQLite local';
            if (window.showToast) window.showToast(err, 'danger');
        }
    } catch (e) {
        if (window.showToast) window.showToast('Error de conexión al sincronizar: ' + e.message, 'danger');
    } finally {
        if (btnRunSync) btnRunSync.disabled = false;
        if (spinner) spinner.className = 'bi bi-arrow-repeat';
        if (btnText) btnText.textContent = 'Sincronizar Nube → Local';
    }
}

async function loadSyncPreview() {
    const token = localStorage.getItem('jwt_token');
    if (!token) return;

    const prodsTbody = document.getElementById('sync-products-tbody');
    const usersTbody = document.getElementById('sync-users-tbody');
    const countProds = document.getElementById('count-sync-prods');
    const countUsers = document.getElementById('count-sync-users');

    try {
        const resp = await fetch('/api/sync/local-preview', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (!resp.ok) return;

        const data = await resp.json();
        const prods = data.productos || [];
        const users = data.usuarios || [];

        if (countProds) countProds.textContent = prods.length;
        if (countUsers) countUsers.textContent = users.length;

        // Renderizar productos
        if (prodsTbody) {
            if (prods.length === 0) {
                prodsTbody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-3">No hay productos en la base local</td></tr>';
            } else {
                prodsTbody.innerHTML = prods.map(p => `
                    <tr>
                        <td class="fw-bold text-muted">${p.id_producto}</td>
                        <td class="fw-semibold text-dark">${p.nombre}</td>
                        <td><span class="badge bg-light text-dark border">${p.categoria}</span></td>
                        <td><code>${p.codigo_barras || '-'}</code></td>
                        <td class="text-end fw-bold text-teal">Q${Number(p.precio_detalle).toFixed(2)}</td>
                        <td class="text-end fw-semibold text-muted">Q${Number(p.precio_mayoreo).toFixed(2)}</td>
                        <td><span class="badge ${p.estado === 'Activo' ? 'bg-success' : 'bg-secondary'}">${p.estado}</span></td>
                    </tr>
                `).join('');
            }
        }

        // Renderizar usuarios
        if (usersTbody) {
            if (users.length === 0) {
                usersTbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted py-3">No hay usuarios en la base local</td></tr>';
            } else {
                usersTbody.innerHTML = users.map(u => `
                    <tr>
                        <td class="fw-bold text-muted">${u.id_usuario}</td>
                        <td class="fw-semibold text-dark">${u.nombre_completo}</td>
                        <td><code>${u.username}</code></td>
                        <td><span class="badge bg-info text-dark">${u.rol}</span></td>
                        <td><span class="badge ${u.estado === 'Activo' ? 'bg-success' : 'bg-secondary'}">${u.estado}</span></td>
                    </tr>
                `).join('');
            }
        }
    } catch (e) {
        console.warn('Error cargando preview de SQLite local:', e);
    }
}

