// ============================================================================
// MODULO DE VISITAS DE SEGUIMIENTO Y EVALUACION (Dueño del Negocio)
// ============================================================================

(function () {
    const MODULOS_SISTEMA = [
        "POS/Ventas",
        "Inventario",
        "Compras",
        "Caja",
        "Usuarios",
        "Catálogos",
        "Reportes",
        "Configuración",
        "Clientes",
        "Facturación",
    ];

    let currentVisitaId = null;
    let editingVisita = null;

    // Inicialización del módulo
    window.showVisitasModule = function () {
        initVisitasView();
        loadVisitasList();
    };

    function initVisitasView() {
        renderModulosForm();
        setupEventListeners();
        setDefaultFecha();
    }

    function setDefaultFecha() {
        const fechaInput = document.getElementById("visita-fecha");
        if (fechaInput && !fechaInput.value) {
            fechaInput.value = new Date().toISOString().split("T")[0];
        }
    }

    function renderModulosForm(modulosData = []) {
        const container = document.getElementById("visitas-modulos-container");
        if (!container) return;

        const modMap = {};
        if (Array.isArray(modulosData)) {
            modulosData.forEach(m => {
                modMap[m.nombre_modulo] = m;
            });
        }

        let html = "";
        MODULOS_SISTEMA.forEach((nombre, idx) => {
            const current = modMap[nombre] || {};
            const res = current.resultado || "";
            const com = current.comentario || "";

            html += `
            <div class="card mb-3 border shadow-sm rounded-3 modulo-eval-row" data-modulo-name="${nombre}">
                <div class="card-body p-3">
                    <div class="row align-items-center g-2">
                        <div class="col-12 col-md-3">
                            <span class="badge bg-secondary me-2">#${idx + 1}</span>
                            <span class="fw-bold text-dark fs-6">${nombre}</span>
                        </div>
                        <div class="col-12 col-md-4">
                            <div class="btn-group w-100" role="group" aria-label="Resultado para ${nombre}">
                                <input type="radio" class="btn-check" name="radio-res-${idx}" id="res-${idx}-conforme" value="Conforme" ${res === "Conforme" ? "checked" : ""}>
                                <label class="btn btn-outline-success btn-sm fw-semibold" for="res-${idx}-conforme">
                                    <i class="bi bi-check-lg me-1"></i>Conforme
                                </label>

                                <input type="radio" class="btn-check" name="radio-res-${idx}" id="res-${idx}-modificar" value="Modificar" ${res === "Modificar" ? "checked" : ""}>
                                <label class="btn btn-outline-warning btn-sm fw-semibold text-dark" for="res-${idx}-modificar">
                                    <i class="bi bi-pencil-square me-1"></i>Modificar
                                </label>

                                <input type="radio" class="btn-check" name="radio-res-${idx}" id="res-${idx}-agregar" value="Agregar" ${res === "Agregar" ? "checked" : ""}>
                                <label class="btn btn-outline-primary btn-sm fw-semibold" for="res-${idx}-agregar">
                                    <i class="bi bi-plus-circle me-1"></i>Agregar
                                </label>
                            </div>
                        </div>
                        <div class="col-12 col-md-5">
                            <input type="text" class="form-control form-control-sm modulo-comentario" 
                                placeholder="Observación o detalle (opcional)" 
                                value="${com ? com.replace(/"/g, '&quot;') : ''}">
                        </div>
                    </div>
                </div>
            </div>`;
        });

        container.innerHTML = html;
    }

    function setupEventListeners() {
        const btnSaveDraft = document.getElementById("btn-visita-save-draft");
        if (btnSaveDraft && !btnSaveDraft.dataset.bound) {
            btnSaveDraft.addEventListener("click", handleSaveDraft);
            btnSaveDraft.dataset.bound = "true";
        }

        const btnComplete = document.getElementById("btn-visita-complete");
        if (btnComplete && !btnComplete.dataset.bound) {
            btnComplete.addEventListener("click", handleComplete);
            btnComplete.dataset.bound = "true";
        }

        const btnReset = document.getElementById("btn-visita-reset");
        if (btnReset && !btnReset.dataset.bound) {
            btnReset.addEventListener("click", resetForm);
            btnReset.dataset.bound = "true";
        }

        const btnNueva = document.getElementById("btn-visitas-nueva");
        if (btnNueva && !btnNueva.dataset.bound) {
            btnNueva.addEventListener("click", () => {
                resetForm();
                showSection("form");
            });
            btnNueva.dataset.bound = "true";
        }

        const btnHistorial = document.getElementById("btn-visitas-historial");
        if (btnHistorial && !btnHistorial.dataset.bound) {
            btnHistorial.addEventListener("click", () => {
                showSection("history");
                loadVisitasList();
            });
            btnHistorial.dataset.bound = "true";
        }

        const btnFiltrar = document.getElementById("btn-visitas-filtrar");
        if (btnFiltrar && !btnFiltrar.dataset.bound) {
            btnFiltrar.addEventListener("click", loadVisitasList);
            btnFiltrar.dataset.bound = "true";
        }

        const btnLimpiar = document.getElementById("btn-visitas-limpiar");
        if (btnLimpiar && !btnLimpiar.dataset.bound) {
            btnLimpiar.addEventListener("click", () => {
                document.getElementById("visitas-filter-estado").value = "";
                document.getElementById("visitas-filter-desde").value = "";
                document.getElementById("visitas-filter-hasta").value = "";
                loadVisitasList();
            });
            btnLimpiar.dataset.bound = "true";
        }

        const btnPdfSummary = document.getElementById("btn-summary-download-pdf");
        if (btnPdfSummary && !btnPdfSummary.dataset.bound) {
            btnPdfSummary.addEventListener("click", () => {
                if (currentVisitaId) {
                    downloadVisitaPdf(currentVisitaId);
                }
            });
            btnPdfSummary.dataset.bound = "true";
        }
    }

    function showSection(section) {
        const formSec = document.getElementById("visitas-form-section");
        const summarySec = document.getElementById("visitas-summary-section");
        const histSec = document.getElementById("visitas-history-section");

        if (formSec) formSec.classList.toggle("d-none", section !== "form");
        if (summarySec) summarySec.classList.toggle("d-none", section !== "summary");
        if (histSec) histSec.classList.toggle("d-none", section !== "history");
    }

    function collectFormData() {
        const fecha = document.getElementById("visita-fecha")?.value || null;
        const lugar = document.getElementById("visita-lugar")?.value?.trim() || null;
        const nombre_representante = document.getElementById("visita-nombre-rep")?.value?.trim() || null;
        const cargo_representante = document.getElementById("visita-cargo-rep")?.value?.trim() || null;
        const califStr = document.getElementById("visita-calificacion-general")?.value;
        const calificacion_general = califStr ? parseInt(califStr, 10) : null;
        const observaciones = document.getElementById("visita-observaciones")?.value?.trim() || null;

        const modulos = [];
        document.querySelectorAll(".modulo-eval-row").forEach(row => {
            const nombre = row.getAttribute("data-modulo-name");
            const checkedRadio = row.querySelector("input[type=radio]:checked");
            const resultado = checkedRadio ? checkedRadio.value : null;
            const comentario = row.querySelector(".modulo-comentario")?.value?.trim() || null;

            if (resultado || comentario) {
                modulos.push({
                    nombre_modulo: nombre,
                    resultado: resultado,
                    comentario: comentario,
                });
            }
        });

        return {
            fecha_visita: fecha,
            lugar,
            nombre_representante,
            cargo_representante,
            calificacion_general,
            observaciones,
            modulos,
        };
    }

    async function handleSaveDraft() {
        const payload = collectFormData();
        const token = localStorage.getItem("jwt_token");

        try {
            let res;
            if (currentVisitaId) {
                res = await fetch(`${API_URL}/visitas/${currentVisitaId}/borrador`, {
                    method: "PUT",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify(payload),
                });
            } else {
                res = await fetch(`${API_URL}/visitas/borrador`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify(payload),
                });
            }

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Error al guardar el borrador");
            }

            const data = await res.json();
            currentVisitaId = data.id_visita;
            document.getElementById("visita-current-id-badge").textContent = `Borrador #${data.id_visita}`;
            document.getElementById("visita-current-id-badge").classList.remove("d-none");

            if (typeof window.showToast === "function") {
                window.showToast(`Borrador #${data.id_visita} guardado con éxito`, "success");
            }
        } catch (e) {
            console.error(e);
            if (typeof window.showToast === "function") {
                window.showToast(e.message, "danger");
            }
        }
    }

    async function handleComplete() {
        const payload = collectFormData();
        const token = localStorage.getItem("jwt_token");

        if (!payload.nombre_representante) {
            if (typeof window.showToast === "function") {
                window.showToast("Por favor ingrese el nombre del representante o dueño del negocio", "warning");
            }
            document.getElementById("visita-nombre-rep")?.focus();
            return;
        }

        try {
            let res;
            if (currentVisitaId) {
                res = await fetch(`${API_URL}/visitas/${currentVisitaId}/completar`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify(payload),
                });
            } else {
                res = await fetch(`${API_URL}/visitas/completar`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Authorization: `Bearer ${token}`,
                    },
                    body: JSON.stringify(payload),
                });
            }

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Error al finalizar la visita");
            }

            const data = await res.json();
            currentVisitaId = data.id_visita;

            if (typeof window.showToast === "function") {
                window.showToast(`Visita #${data.id_visita} completada exitosamente`, "success");
            }

            renderSummary(data);
            showSection("summary");
        } catch (e) {
            console.error(e);
            if (typeof window.showToast === "function") {
                window.showToast(e.message, "danger");
            }
        }
    }

    function renderSummary(visita) {
        currentVisitaId = visita.id_visita;

        document.getElementById("summary-visita-id").textContent = `#${visita.id_visita}`;
        document.getElementById("summary-fecha").textContent = visita.fecha_visita || "-";
        document.getElementById("summary-lugar").textContent = visita.lugar || "No indicado";
        document.getElementById("summary-representante").textContent = visita.nombre_representante || "-";
        document.getElementById("summary-cargo").textContent = visita.cargo_representante || "-";
        document.getElementById("summary-calificacion").textContent = visita.calificacion_general ? `${visita.calificacion_general} / 5` : "Sin calificar";
        document.getElementById("summary-evaluador").textContent = visita.evaluador_nombre || "Sistema";
        document.getElementById("summary-estado").textContent = visita.estado;
        document.getElementById("summary-observaciones").textContent = visita.observaciones || "Sin observaciones generales.";

        const r = visita.resumen || { total_modulos: 10, conformes: 0, modificar: 0, agregar: 0, sin_evaluar: 10 };
        document.getElementById("summary-kpi-total").textContent = r.total_modulos;
        document.getElementById("summary-kpi-conformes").textContent = r.conformes;
        document.getElementById("summary-kpi-modificar").textContent = r.modificar;
        document.getElementById("summary-kpi-agregar").textContent = r.agregar;
        document.getElementById("summary-kpi-pendientes").textContent = r.sin_evaluar;

        const tableBody = document.getElementById("summary-modulos-table-body");
        if (tableBody) {
            const modMap = {};
            (visita.modulos || []).forEach(m => {
                modMap[m.nombre_modulo] = m;
            });

            let rows = "";
            MODULOS_SISTEMA.forEach((nombre, idx) => {
                const item = modMap[nombre];
                const res = item?.resultado || "Sin evaluar";
                const com = item?.comentario || "-";

                let badge = '<span class="badge bg-secondary">Sin evaluar</span>';
                if (res === "Conforme") badge = '<span class="badge bg-success"><i class="bi bi-check-lg me-1"></i>Conforme</span>';
                else if (res === "Modificar") badge = '<span class="badge bg-warning text-dark"><i class="bi bi-pencil-square me-1"></i>Modificar</span>';
                else if (res === "Agregar") badge = '<span class="badge bg-primary"><i class="bi bi-plus-circle me-1"></i>Agregar</span>';

                rows += `
                <tr>
                    <td class="text-muted small">${idx + 1}</td>
                    <td class="fw-semibold">${nombre}</td>
                    <td>${badge}</td>
                    <td class="text-muted small">${com}</td>
                </tr>`;
            });
            tableBody.innerHTML = rows;
        }
    }

    async function loadVisitasList() {
        const token = localStorage.getItem("jwt_token");
        const estado = document.getElementById("visitas-filter-estado")?.value || "";
        const desde = document.getElementById("visitas-filter-desde")?.value || "";
        const hasta = document.getElementById("visitas-filter-hasta")?.value || "";

        let url = `${API_URL}/visitas?`;
        if (estado) url += `estado=${encodeURIComponent(estado)}&`;
        if (desde) url += `fecha_desde=${encodeURIComponent(desde)}&`;
        if (hasta) url += `fecha_hasta=${encodeURIComponent(hasta)}&`;

        try {
            const res = await fetch(url, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) {
                if (res.status === 403) {
                    console.warn("Usuario no autorizado para listar visitas");
                    return;
                }
                throw new Error("Error al obtener listado de visitas");
            }
            const data = await res.json();
            renderVisitasTable(data);
        } catch (e) {
            console.error(e);
        }
    }

    function renderVisitasTable(visitas) {
        const tbody = document.getElementById("visitas-table-body");
        const emptyDiv = document.getElementById("visitas-empty");
        const countSpan = document.getElementById("visitas-total-info");

        if (!tbody) return;

        if (!visitas || visitas.length === 0) {
            tbody.innerHTML = "";
            if (emptyDiv) emptyDiv.classList.remove("d-none");
            if (countSpan) countSpan.textContent = "Total: 0 visitas";
            return;
        }

        if (emptyDiv) emptyDiv.classList.add("d-none");
        if (countSpan) countSpan.textContent = `Total: ${visitas.length} visita(s)`;

        let rows = "";
        visitas.forEach(v => {
            const estadoBadge = v.estado === "Completada"
                ? '<span class="badge bg-success">Completada</span>'
                : '<span class="badge bg-secondary">Borrador</span>';

            const calif = v.calificacion_general ? `${v.calificacion_general} ★` : "-";

            rows += `
            <tr>
                <td class="fw-bold">#${v.id_visita}</td>
                <td>${v.fecha_visita}</td>
                <td class="fw-semibold">${v.nombre_representante || "Sin asignar"}</td>
                <td class="text-muted small">${v.cargo_representante || "-"}</td>
                <td class="text-center">${calif}</td>
                <td class="text-center">${estadoBadge}</td>
                <td class="text-end">
                    <button class="btn btn-sm btn-outline-info me-1" onclick="window.viewVisitaDetail(${v.id_visita})" title="Ver Resumen">
                        <i class="bi bi-eye"></i>
                    </button>
                    ${v.estado === "Borrador" ? `
                    <button class="btn btn-sm btn-outline-warning me-1" onclick="window.editVisitaDraft(${v.id_visita})" title="Editar Borrador">
                        <i class="bi bi-pencil"></i>
                    </button>` : ""}
                    <button class="btn btn-sm btn-outline-danger" onclick="window.downloadVisitaPdf(${v.id_visita})" title="Descargar PDF">
                        <i class="bi bi-file-earmark-pdf"></i>
                    </button>
                </td>
            </tr>`;
        });

        tbody.innerHTML = rows;
    }

    window.viewVisitaDetail = async function (id) {
        const token = localStorage.getItem("jwt_token");
        try {
            const res = await fetch(`${API_URL}/visitas/${id}`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) throw new Error("No se pudo cargar la visita");
            const data = await res.json();
            renderSummary(data);
            showSection("summary");
        } catch (e) {
            console.error(e);
            if (typeof window.showToast === "function") {
                window.showToast(e.message, "danger");
            }
        }
    };

    window.editVisitaDraft = async function (id) {
        const token = localStorage.getItem("jwt_token");
        try {
            const res = await fetch(`${API_URL}/visitas/${id}`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) throw new Error("No se pudo cargar el borrador");
            const data = await res.json();

            currentVisitaId = data.id_visita;
            document.getElementById("visita-current-id-badge").textContent = `Borrador #${data.id_visita}`;
            document.getElementById("visita-current-id-badge").classList.remove("d-none");

            document.getElementById("visita-fecha").value = data.fecha_visita || "";
            document.getElementById("visita-lugar").value = data.lugar || "";
            document.getElementById("visita-nombre-rep").value = data.nombre_representante || "";
            document.getElementById("visita-cargo-rep").value = data.cargo_representante || "";
            document.getElementById("visita-calificacion-general").value = data.calificacion_general || "";
            document.getElementById("visita-observaciones").value = data.observaciones || "";

            renderModulosForm(data.modulos || []);
            showSection("form");
        } catch (e) {
            console.error(e);
            if (typeof window.showToast === "function") {
                window.showToast(e.message, "danger");
            }
        }
    };

    window.downloadVisitaPdf = async function (id) {
        const token = localStorage.getItem("jwt_token");
        try {
            const res = await fetch(`${API_URL}/visitas/${id}/pdf`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            if (!res.ok) throw new Error("Error al descargar el PDF de la visita");

            const blob = await res.blob();
            const blobUrl = window.URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = blobUrl;
            a.download = `visita_seguimiento_${id}.pdf`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(blobUrl);

            if (typeof window.showToast === "function") {
                window.showToast(`PDF de visita #${id} descargado con éxito`, "success");
            }
        } catch (e) {
            console.error(e);
            if (typeof window.showToast === "function") {
                window.showToast(e.message, "danger");
            }
        }
    };

    function resetForm() {
        currentVisitaId = null;
        const badge = document.getElementById("visita-current-id-badge");
        if (badge) badge.classList.add("d-none");

        document.getElementById("visita-lugar").value = "";
        document.getElementById("visita-nombre-rep").value = "";
        document.getElementById("visita-cargo-rep").value = "";
        document.getElementById("visita-calificacion-general").value = "";
        document.getElementById("visita-observaciones").value = "";
        setDefaultFecha();
        renderModulosForm([]);
    }
})();
