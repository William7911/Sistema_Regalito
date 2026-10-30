/**
 * ReportExporter - Sistema de Exportación Universal a Excel y PDF
 * Tienda El Regalito - Panajachel
 * 
 * Permite exportar cualquier tabla HTML a archivos .xlsx y .pdf
 * con formato estandarizado, diseño corporativo teal (#0A5C5E),
 * metadatos de auditoría (usuario, fecha y hora) y cálculo de anchos.
 * Regla UX: Cero emojis en interfaz y documentos.
 */

(function (window) {
    'use strict';

    function getFormattedTimestamp() {
        const now = new Date();
        const pad = (n) => String(n).padStart(2, '0');
        const dia = pad(now.getDate());
        const mes = pad(now.getMonth() + 1);
        const anio = now.getFullYear();
        const horas = pad(now.getHours());
        const mins = pad(now.getMinutes());
        return {
            dateStr: `${dia}/${mes}/${anio}`,
            timeStr: `${horas}:${mins}`,
            fileStamp: `${anio}${mes}${dia}_${horas}${mins}`,
            full: `${dia}/${mes}/${anio} ${horas}:${mins}`
        };
    }

    function getCurrentUserName() {
        try {
            return localStorage.getItem('user_display_name')
                || localStorage.getItem('user_name')
                || 'Administrador';
        } catch (_) {
            return 'Usuario';
        }
    }

    function resolveTable(selectorOrElement) {
        if (!selectorOrElement) return null;
        if (typeof selectorOrElement === 'string') {
            return document.querySelector(selectorOrElement);
        }
        if (selectorOrElement instanceof HTMLElement) {
            return selectorOrElement;
        }
        return null;
    }

    function cleanCellText(cell) {
        if (!cell) return '';

        // Clonar la celda para manipularla sin alterar el DOM real
        const clone = cell.cloneNode(true);

        // Remover botones, dropdowns, inputs de tipo acción, tooltips y zoom
        clone.querySelectorAll('button, .dropdown, select, input[type="button"], input[type="submit"], script, style, .sort-icon, .visually-hidden, .inventory-product-thumb-wrap, .inventory-product-thumb').forEach(el => el.remove());

        // Si hay inputs de texto/checkbox, tomar sus valores
        clone.querySelectorAll('input').forEach(input => {
            if (input.type === 'checkbox') {
                input.replaceWith(input.checked ? 'Si' : 'No');
            } else {
                input.replaceWith(input.value || '');
            }
        });

        // Extraer texto limpio
        let text = clone.innerText || clone.textContent || '';
        return text
            .replace(/[\r\n\t]+/g, ' ')
            .replace(/\s{2,}/g, ' ')
            .trim();
    }

    function parseTableData(tableElement) {
        const table = resolveTable(tableElement);
        if (!table) {
            return { headers: [], rows: [] };
        }

        // 1. Extraer encabezados de thead (o primera fila si no hay thead)
        let headerRow = table.querySelector('thead tr');
        if (!headerRow) {
            headerRow = table.querySelector('tr');
        }

        const headers = [];
        const ignoredIndices = new Set();

        if (headerRow) {
            const headerCells = headerRow.querySelectorAll('th, td');
            headerCells.forEach((th, idx) => {
                const text = cleanCellText(th);
                const textLower = text.toLowerCase();
                // Ignorar columnas de acciones o controles
                if (textLower === 'acciones' || textLower === 'acción' || textLower === 'accion' || textLower === 'opciones' || textLower === '') {
                    if (th.classList.contains('text-end') || headerCells.length - 1 === idx || textLower.includes('accion')) {
                        ignoredIndices.add(idx);
                        return;
                    }
                }
                headers.push({ idx, text });
            });
        }

        // 2. Extraer filas de tbody (o filas siguientes a thead)
        const rowElements = table.querySelectorAll('tbody tr');
        const rows = [];

        rowElements.forEach(tr => {
            // Ignorar filas ocultas, de carga o de estado vacío
            if (tr.classList.contains('d-none') || tr.style.display === 'none') return;
            if (tr.querySelector('.spinner-border') || tr.querySelector('td[colspan]')) {
                const text = tr.textContent.trim().toLowerCase();
                if (text.includes('no hay') || text.includes('no se encontraron') || text.includes('cargando') || text.includes('haga clic')) {
                    return;
                }
            }

            const cells = tr.querySelectorAll('td');
            if (!cells || cells.length === 0) return;

            const rowData = [];
            headers.forEach(h => {
                const cell = cells[h.idx];
                rowData.push(cell ? cleanCellText(cell) : '');
            });

            // Evitar filas totalmente vacías
            if (rowData.some(val => val !== '')) {
                rows.push(rowData);
            }
        });

        return {
            headers: headers.map(h => h.text),
            rows: rows
        };
    }

    /**
     * Exporta los datos de una tabla HTML a un archivo Excel (.xlsx)
     * @param {string|HTMLElement} tableSelectorOrEl - Selector o elemento de la tabla
     * @param {string} filename - Nombre base del archivo descargado
     * @param {string} [sheetName] - Nombre de la hoja de cálculo
     */
    function exportTableToExcel(tableSelectorOrEl, filename, sheetName) {
        if (typeof XLSX === 'undefined') {
            console.error('SheetJS (XLSX) no está cargado');
            if (window.showToast) window.showToast('Error: Librería de Excel no disponible', 'danger');
            return;
        }

        const data = parseTableData(tableSelectorOrEl);
        if (!data.headers.length || !data.rows.length) {
            if (window.showToast) window.showToast('No hay datos en la tabla para exportar', 'warning');
            return;
        }

        const timeInfo = getFormattedTimestamp();
        const baseName = (filename || 'reporte').replace(/\.xlsx$/i, '');
        const finalFileName = `${baseName}_${timeInfo.fileStamp}.xlsx`;
        const validSheetName = (sheetName || 'Datos').replace(/[\\/?*[\]]/g, '').substring(0, 31);

        // Crear libro y hoja
        const wb = XLSX.utils.book_new();
        const wsData = [data.headers, ...data.rows];
        const ws = XLSX.utils.aoa_to_sheet(wsData);

        // Calcular auto-ancho de columnas
        const colWidths = data.headers.map((h, colIdx) => {
            let maxLen = h.length;
            data.rows.forEach(r => {
                const cellVal = r[colIdx] ? String(r[colIdx]) : '';
                if (cellVal.length > maxLen) maxLen = cellVal.length;
            });
            return { wch: Math.min(Math.max(maxLen + 4, 12), 45) };
        });
        ws['!cols'] = colWidths;

        XLSX.utils.book_append_sheet(wb, ws, validSheetName);
        XLSX.writeFile(wb, finalFileName);

        if (window.showToast) {
            window.showToast(`Reporte Excel descargado: ${finalFileName}`, 'success');
        }
    }

    /**
     * Exporta los datos de una tabla HTML a un archivo PDF
     * @param {string|HTMLElement} tableSelectorOrEl - Selector o elemento de la tabla
     * @param {string} title - Título del reporte (ej. "Catálogo de Productos")
     * @param {string} filename - Nombre base del archivo descargado
     * @param {Object} [options] - Opciones adicionales (orientation: 'portrait'|'landscape')
     */
    function exportTableToPdf(tableSelectorOrEl, title, filename, options) {
        const jsPdfLib = window.jspdf && window.jspdf.jsPDF ? window.jspdf.jsPDF : window.jsPDF;
        if (!jsPdfLib) {
            console.error('jsPDF no está cargado');
            if (window.showToast) window.showToast('Error: Librería PDF no disponible', 'danger');
            return;
        }

        const data = parseTableData(tableSelectorOrEl);
        if (!data.headers.length || !data.rows.length) {
            if (window.showToast) window.showToast('No hay datos en la tabla para exportar', 'warning');
            return;
        }

        const timeInfo = getFormattedTimestamp();
        const baseName = (filename || 'reporte').replace(/\.pdf$/i, '');
        const finalFileName = `${baseName}_${timeInfo.fileStamp}.pdf`;
        const colCount = data.headers.length;
        const orientation = (options && options.orientation) || (colCount > 5 ? 'landscape' : 'portrait');

        const doc = new jsPdfLib({
            orientation: orientation,
            unit: 'mm',
            format: 'letter'
        });

        const pageWidth = doc.internal.pageSize.getWidth();
        const pageHeight = doc.internal.pageSize.getHeight();
        const marginX = 14;

        // Franja superior decorativa color teal
        doc.setFillColor(10, 92, 94); // #0A5C5E
        doc.rect(0, 0, pageWidth, 5, 'F');

        // Nombre de la empresa
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(14);
        doc.setTextColor(10, 92, 94);
        doc.text('TIENDA EL REGALITO - PANAJACHEL', marginX, 15);

        // Título del reporte
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(11);
        doc.setTextColor(30, 41, 59);
        doc.text(title || 'REPORTE DEL SISTEMA', marginX, 22);

        // Metadatos (Fecha, Hora, Usuario, Total registros)
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(8);
        doc.setTextColor(100, 116, 139);
        const metaText = `Fecha: ${timeInfo.dateStr} | Hora: ${timeInfo.timeStr} | Generado por: ${getCurrentUserName()} | Total: ${data.rows.length} registros`;
        doc.text(metaText, marginX, 27);

        // Línea divisoria
        doc.setDrawColor(226, 232, 240);
        doc.setLineWidth(0.4);
        doc.line(marginX, 29, pageWidth - marginX, 29);

        // Generación de la tabla con autoTable
        if (typeof doc.autoTable === 'function') {
            doc.autoTable({
                head: [data.headers],
                body: data.rows,
                startY: 33,
                theme: 'striped',
                headStyles: {
                    fillColor: [10, 92, 94], // #0A5C5E
                    textColor: [255, 255, 255],
                    fontStyle: 'bold',
                    fontSize: 8.5,
                    halign: 'left',
                    cellPadding: 2.5
                },
                bodyStyles: {
                    fontSize: 8,
                    textColor: [30, 41, 59],
                    lineColor: [226, 232, 240],
                    lineWidth: 0.1,
                    cellPadding: 2
                },
                alternateRowStyles: {
                    fillColor: [248, 250, 252] // #F8FAFC
                },
                margin: { top: 33, right: marginX, bottom: 15, left: marginX },
                styles: {
                    overflow: 'linebreak'
                },
                didDrawPage: function (pageData) {
                    const totalPages = doc.internal.getNumberOfPages();
                    doc.setFont('helvetica', 'normal');
                    doc.setFontSize(7.5);
                    doc.setTextColor(148, 163, 184);

                    // Línea sobre el footer
                    doc.setDrawColor(226, 232, 240);
                    doc.setLineWidth(0.3);
                    doc.line(marginX, pageHeight - 11, pageWidth - marginX, pageHeight - 11);

                    // Texto del footer
                    doc.text('Sistema de Gestion - Tienda El Regalito', marginX, pageHeight - 6);
                    doc.text(`Pagina ${pageData.pageNumber} de ${totalPages}`, pageWidth - marginX, pageHeight - 6, { align: 'right' });
                }
            });
        } else {
            console.error('jsPDF-AutoTable plugin no disponible');
        }

        doc.save(finalFileName);

        if (window.showToast) {
            window.showToast(`Reporte PDF descargado: ${finalFileName}`, 'success');
        }
    }

    /**
     * Mapeo Declarativo de Botones de Reporte por Módulo
     */
    const EXPORT_REGISTRY = {
        // Catálogo Productos
        'btn-catalog-products-export-excel': { type: 'excel', table: '#products-table', filename: 'catalogo_productos', sheet: 'Productos' },
        'btn-catalog-products-export-pdf':   { type: 'pdf',   table: '#products-table', title: 'Catálogo de Productos', filename: 'catalogo_productos' },

        // Catálogo Categorías
        'btn-catalog-categories-export-excel': { type: 'excel', table: '#categories-table', filename: 'catalogo_categorias', sheet: 'Categorías' },
        'btn-catalog-categories-export-pdf':   { type: 'pdf',   table: '#categories-table', title: 'Catálogo de Categorías', filename: 'catalogo_categorias' },

        // Catálogo Subcategorías PDF
        'btn-export-subcat-pdf': { type: 'pdf', table: '#subcategories-table', title: 'Catálogo de Subcategorías', filename: 'subcategorias' },

        // Catálogo Unidades PDF
        'btn-export-unidades-pdf': { type: 'pdf', table: '#unidades-table', title: 'Unidades de Medida', filename: 'unidades_medida' },

        // Catálogo Sucursales PDF
        'btn-export-sucursales-pdf': { type: 'pdf', table: '#sucursales-table', title: 'Sucursales', filename: 'sucursales' },

        // Catálogo Áreas PDF
        'btn-export-areas-pdf': { type: 'pdf', table: '#areas-table', title: 'Áreas de Bodega', filename: 'areas_bodega' },

        // Catálogo Motivos PDF
        'btn-export-motivos-pdf': { type: 'pdf', table: '#motivos-table', title: 'Motivos de Merma', filename: 'motivos_merma' },

        // Catálogo Métodos Pago PDF
        'btn-export-metodos-pdf': { type: 'pdf', table: '#metodos-table', title: 'Métodos de Pago', filename: 'metodos_pago' },

        // Catálogo Proveedores PDF
        'btn-export-proveedores-pdf': { type: 'pdf', table: '#proveedores-table', title: 'Proveedores', filename: 'proveedores' },

        // Catálogo Departamentos PDF
        'btn-export-departamentos-pdf': { type: 'pdf', table: '#departamentos-table', title: 'Departamentos', filename: 'departamentos' },

        // Catálogo Municipios PDF
        'btn-export-municipios-pdf': { type: 'pdf', table: '#municipios-table', title: 'Municipios', filename: 'municipios' },

        // Inventario
        'btn-inventory-export-excel': { type: 'excel', table: '.inventory-table', filename: 'inventario_existencias', sheet: 'Inventario' },
        'btn-inventory-export-pdf':   { type: 'pdf',   table: '.inventory-table', title: 'Inventario y Existencias', filename: 'inventario_existencias' },

        // Compras
        'btn-compras-export-excel': { type: 'excel', table: '#tabla-compras-ordenes', filename: 'ordenes_compras', sheet: 'Compras' },
        'btn-compras-export-pdf':   { type: 'pdf',   table: '#tabla-compras-ordenes', title: 'Historial de Compras', filename: 'ordenes_compras' },

        // Mermas
        'btn-mermas-export-excel': { type: 'excel', table: '#tabla-mermas', filename: 'mermas_inventario', sheet: 'Mermas' },
        'btn-mermas-export-pdf':   { type: 'pdf',   table: '#tabla-mermas', title: 'Mermas de Inventario', filename: 'mermas_inventario' },

        // Caja
        'btn-cash-export-excel': { type: 'excel', table: '#cash-table', filename: 'turnos_caja', sheet: 'Caja' },
        'btn-cash-export-pdf':   { type: 'pdf',   table: '#cash-table', title: 'Turnos y Movimientos de Caja', filename: 'turnos_caja' },

        // Traslados
        'btn-traslados-export-excel': { type: 'excel', table: '#tabla-traslados', filename: 'traslados_sucursales', sheet: 'Traslados' },
        'btn-traslados-export-pdf':   { type: 'pdf',   table: '#tabla-traslados', title: 'Traslados entre Sucursales', filename: 'traslados_sucursales' },

        // Visitas
        'btn-visitas-export-excel': { type: 'excel', table: '#tabla-visitas', filename: 'visitas_seguimiento', sheet: 'Visitas' },
        'btn-visitas-export-pdf':   { type: 'pdf',   table: '#tabla-visitas', title: 'Historial de Visitas y Evaluaciones', filename: 'visitas_seguimiento' },

        // Roles
        'btn-roles-export-excel': { type: 'excel', table: '#roles-table', filename: 'roles_permisos', sheet: 'Roles' },
        'btn-roles-export-pdf':   { type: 'pdf',   table: '#roles-table', title: 'Roles y Permisos', filename: 'roles_permisos' },

        // Bitácora
        'btn-bitacora-export-excel': { type: 'excel', table: '#bitacora-table', filename: 'bitacora_auditoria', sheet: 'Bitácora' },
        'btn-bitacora-export-pdf':   { type: 'pdf',   table: '#bitacora-table', title: 'Bitácora de Auditoría', filename: 'bitacora_auditoria' },

        // Historial Precios
        'btn-historial-export-excel': { type: 'excel', table: '#historial-table', filename: 'historial_precios', sheet: 'Historial' },
        'btn-historial-export-pdf':   { type: 'pdf',   table: '#historial-table', title: 'Historial de Precios', filename: 'historial_precios' }
    };

    // Escuchador global delegado para todos los botones de reporte
    document.addEventListener('click', function (e) {
        const btn = e.target.closest('button, a');
        if (!btn || !btn.id) return;

        const config = EXPORT_REGISTRY[btn.id];
        if (!config) return;

        e.preventDefault();

        if (config.type === 'excel') {
            exportTableToExcel(config.table, config.filename, config.sheet);
        } else if (config.type === 'pdf') {
            exportTableToPdf(config.table, config.title, config.filename, config.options);
        }
    });

    // Exponer API global
    window.ReportExporter = {
        parseTableData: parseTableData,
        exportTableToExcel: exportTableToExcel,
        exportTableToPdf: exportTableToPdf,
        registry: EXPORT_REGISTRY
    };

})(window);
