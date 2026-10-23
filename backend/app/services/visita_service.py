from typing import Optional, List
from datetime import date, datetime
import io
from fastapi import HTTPException

from app.db.models import VisitaSeguimiento, VisitaModuloEvaluacion
from app.schemas.visita_schema import (
    VisitaCreate, VisitaUpdate, VisitaOut, VisitaResumen,
    ModuloEvaluacionOut, MODULOS_DEFAULT, RESULTADOS_PERMITIDOS
)
from app.core.permissions import check_user_permission
from app.services.audit_service import log_action

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch


class ConcreteVisitaService:
    """Servicio para Visitas de Seguimiento y Evaluación de Módulos (DERCAS)."""

    def __init__(self, uow):
        self.uow = uow

    async def _validar_permiso(self, user_id: int, permiso: str = "VISITA_REGISTRAR"):
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        allowed = await check_user_permission(self.uow.db, user, permiso)
        if not allowed:
            raise HTTPException(
                status_code=403,
                detail=f"No tiene permisos para realizar esta acción ({permiso})"
            )

    def _calcular_resumen(self, modulos: List[VisitaModuloEvaluacion]) -> VisitaResumen:
        conformes = sum(1 for m in modulos if m.resultado == "Conforme")
        modificar = sum(1 for m in modulos if m.resultado == "Modificar")
        agregar = sum(1 for m in modulos if m.resultado == "Agregar")
        total = len(MODULOS_DEFAULT)
        sin_evaluar = max(0, total - (conformes + modificar + agregar))
        return VisitaResumen(
            total_modulos=total,
            conformes=conformes,
            modificar=modificar,
            agregar=agregar,
            sin_evaluar=sin_evaluar,
        )

    def _enrich_visita(self, visita: VisitaSeguimiento) -> VisitaOut:
        evaluador_nombre = None
        if getattr(visita, "usuario", None):
            evaluador_nombre = visita.usuario.nombre_completo

        modulos_db = getattr(visita, "modulos", []) or []
        resumen = self._calcular_resumen(modulos_db)

        # Módulos como DTO
        modulos_out = [
            ModuloEvaluacionOut(
                id_modulo_eval=m.id_modulo_eval,
                id_visita=m.id_visita,
                nombre_modulo=m.nombre_modulo,
                resultado=m.resultado,
                calificacion=m.calificacion,
                comentario=m.comentario,
            )
            for m in modulos_db
        ]

        return VisitaOut(
            id_visita=visita.id_visita,
            id_usuario=visita.id_usuario,
            id_cliente=visita.id_cliente,
            fecha_visita=visita.fecha_visita,
            lugar=visita.lugar,
            nombre_representante=visita.nombre_representante,
            cargo_representante=visita.cargo_representante,
            calificacion_general=visita.calificacion_general,
            observaciones=visita.observaciones,
            estado=visita.estado,
            fecha_creacion=visita.fecha_creacion,
            evaluador_nombre=evaluador_nombre,
            modulos=modulos_out,
            resumen=resumen,
        )

    async def guardar_borrador(self, data: VisitaCreate, id_usuario: int) -> VisitaOut:
        await self._validar_permiso(id_usuario)

        visita = VisitaSeguimiento(
            id_usuario=id_usuario,
            fecha_visita=data.fecha_visita or date.today(),
            lugar=data.lugar,
            nombre_representante=data.nombre_representante,
            cargo_representante=data.cargo_representante,
            calificacion_general=data.calificacion_general,
            observaciones=data.observaciones,
            estado="Borrador",
        )
        visita = await self.uow.visitas.create(visita)

        # Si se enviaron evaluaciones de módulos, guardarlas
        if data.modulos:
            await self.uow.visitas.sync_modulos(visita.id_visita, data.modulos)
            visita = await self.uow.visitas.get_by_id(visita.id_visita)

        await log_action(
            self.uow.db,
            id_usuario=id_usuario,
            tabla="visita_seguimiento",
            accion="CREAR",
            descripcion=f"Creó borrador de visita de seguimiento #{visita.id_visita} ({visita.nombre_representante or 'Sin representante'})",
        )
        await self.uow.commit()

        return self._enrich_visita(visita)

    async def actualizar_borrador(self, id_visita: int, data: VisitaUpdate, id_usuario: int) -> VisitaOut:
        await self._validar_permiso(id_usuario)

        visita = await self.uow.visitas.get_by_id(id_visita)
        if not visita:
            raise HTTPException(status_code=404, detail="Visita de seguimiento no encontrada")

        if visita.estado == "Completada":
            raise HTTPException(status_code=400, detail="Una visita completada no puede ser modificada como borrador")

        if data.fecha_visita is not None:
            visita.fecha_visita = data.fecha_visita
        if data.lugar is not None:
            visita.lugar = data.lugar
        if data.nombre_representante is not None:
            visita.nombre_representante = data.nombre_representante
        if data.cargo_representante is not None:
            visita.cargo_representante = data.cargo_representante
        if data.calificacion_general is not None:
            visita.calificacion_general = data.calificacion_general
        if data.observaciones is not None:
            visita.observaciones = data.observaciones

        visita = await self.uow.visitas.update(visita)

        if data.modulos is not None:
            await self.uow.visitas.sync_modulos(visita.id_visita, data.modulos)
            visita = await self.uow.visitas.get_by_id(visita.id_visita)

        await log_action(
            self.uow.db,
            id_usuario=id_usuario,
            tabla="visita_seguimiento",
            accion="EDITAR",
            descripcion=f"Actualizó borrador de visita #{visita.id_visita}",
        )
        await self.uow.commit()

        return self._enrich_visita(visita)

    async def completar_visita(self, id_visita: int, data: Optional[VisitaUpdate], id_usuario: int) -> VisitaOut:
        await self._validar_permiso(id_usuario)

        visita = await self.uow.visitas.get_by_id(id_visita)
        if not visita:
            raise HTTPException(status_code=404, detail="Visita de seguimiento no encontrada")

        if data:
            if data.fecha_visita is not None:
                visita.fecha_visita = data.fecha_visita
            if data.lugar is not None:
                visita.lugar = data.lugar
            if data.nombre_representante is not None:
                visita.nombre_representante = data.nombre_representante
            if data.cargo_representante is not None:
                visita.cargo_representante = data.cargo_representante
            if data.calificacion_general is not None:
                visita.calificacion_general = data.calificacion_general
            if data.observaciones is not None:
                visita.observaciones = data.observaciones

            if data.modulos is not None:
                await self.uow.visitas.sync_modulos(visita.id_visita, data.modulos)

        visita.estado = "Completada"
        visita = await self.uow.visitas.update(visita)
        visita = await self.uow.visitas.get_by_id(visita.id_visita)

        await log_action(
            self.uow.db,
            id_usuario=id_usuario,
            tabla="visita_seguimiento",
            accion="EDITAR",
            descripcion=f"Completó la visita de seguimiento #{visita.id_visita}",
        )
        await self.uow.commit()

        return self._enrich_visita(visita)

    async def obtener_visita(self, id_visita: int, id_usuario: int) -> VisitaOut:
        await self._validar_permiso(id_usuario)

        visita = await self.uow.visitas.get_by_id(id_visita)
        if not visita:
            raise HTTPException(status_code=404, detail="Visita de seguimiento no encontrada")

        return self._enrich_visita(visita)

    async def listar_visitas(
        self,
        id_usuario: int,
        estado: Optional[str] = None,
        fecha_desde: Optional[date] = None,
        fecha_hasta: Optional[date] = None,
    ) -> List[VisitaOut]:
        await self._validar_permiso(id_usuario)

        visitas = await self.uow.visitas.list_all(
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
        )
        return [self._enrich_visita(v) for v in visitas]

    async def generar_pdf(self, id_visita: int, id_usuario: int) -> bytes:
        visita_out = await self.obtener_visita(id_visita, id_usuario)

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1e293b"),
            alignment=1,
            spaceAfter=6,
        )
        subtitle_style = ParagraphStyle(
            "SubTitleStyle",
            parent=styles["Normal"],
            fontSize=11,
            leading=14,
            textColor=colors.HexColor("#64748b"),
            alignment=1,
            spaceAfter=14,
        )
        h2_style = ParagraphStyle(
            "H2Style",
            parent=styles["Heading2"],
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#0f172a"),
            spaceBefore=10,
            spaceAfter=6,
        )
        text_style = ParagraphStyle(
            "TextStyle",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#334155"),
        )
        cell_bold = ParagraphStyle(
            "CellBold",
            parent=text_style,
            fontName="Helvetica-Bold",
        )

        elements = []

        # Título y encabezado
        elements.append(Paragraph("TIENDA EL REGALITO", title_style))
        elements.append(Paragraph("FORMULARIO DE VISITA DE SEGUIMIENTO Y EVALUACIÓN", subtitle_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=12))

        # Información general (Tabla de 4 columnas)
        calif_text = f"{visita_out.calificacion_general} / 5" if visita_out.calificacion_general else "No registrada"
        info_data = [
            [
                Paragraph("<b>No. Visita:</b>", text_style),
                Paragraph(f"#{visita_out.id_visita}", text_style),
                Paragraph("<b>Fecha:</b>", text_style),
                Paragraph(str(visita_out.fecha_visita), text_style),
            ],
            [
                Paragraph("<b>Lugar:</b>", text_style),
                Paragraph(visita_out.lugar or "No especificado", text_style),
                Paragraph("<b>Estado:</b>", text_style),
                Paragraph(visita_out.estado, text_style),
            ],
            [
                Paragraph("<b>Representante:</b>", text_style),
                Paragraph(visita_out.nombre_representante or "No especificado", text_style),
                Paragraph("<b>Cargo:</b>", text_style),
                Paragraph(visita_out.cargo_representante or "No especificado", text_style),
            ],
            [
                Paragraph("<b>Evaluador:</b>", text_style),
                Paragraph(visita_out.evaluador_nombre or "Sistema", text_style),
                Paragraph("<b>Calificación:</b>", text_style),
                Paragraph(calif_text, text_style),
            ],
        ]

        t_info = Table(info_data, colWidths=[90, 180, 90, 180])
        t_info.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        elements.append(t_info)
        elements.append(Spacer(1, 10))

        # Resumen ejecutivo
        r = visita_out.resumen or self._calcular_resumen([])
        elements.append(Paragraph("Resumen de Evaluación", h2_style))
        resumen_data = [
            [
                Paragraph("<b>Módulos Totales</b>", text_style),
                Paragraph("<b>Conformes</b>", text_style),
                Paragraph("<b>A Modificar</b>", text_style),
                Paragraph("<b>Por Agregar</b>", text_style),
                Paragraph("<b>Sin Evaluar</b>", text_style),
            ],
            [
                Paragraph(str(r.total_modulos), text_style),
                Paragraph(f"<font color='#16a34a'><b>{r.conformes}</b></font>", text_style),
                Paragraph(f"<font color='#d97706'><b>{r.modificar}</b></font>", text_style),
                Paragraph(f"<font color='#2563eb'><b>{r.agregar}</b></font>", text_style),
                Paragraph(f"<font color='#64748b'>{r.sin_evaluar}</font>", text_style),
            ]
        ]
        t_resumen = Table(resumen_data, colWidths=[108, 108, 108, 108, 108])
        t_resumen.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f1f5f9")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_resumen)
        elements.append(Spacer(1, 10))

        # Detalle por módulo
        elements.append(Paragraph("Evaluación por Módulo (10 Módulos)", h2_style))
        mod_map = {m.nombre_modulo: m for m in visita_out.modulos}
        
        tabla_mods = [
            [
                Paragraph("<b>#</b>", cell_bold),
                Paragraph("<b>Módulo</b>", cell_bold),
                Paragraph("<b>Resultado</b>", cell_bold),
                Paragraph("<b>Comentario / Observación</b>", cell_bold),
            ]
        ]

        for idx, nom in enumerate(MODULOS_DEFAULT, start=1):
            eval_mod = mod_map.get(nom)
            res = eval_mod.resultado if eval_mod and eval_mod.resultado else "Sin evaluar"
            com = eval_mod.comentario if eval_mod and eval_mod.comentario else "-"
            
            # Color tag
            if res == "Conforme":
                res_html = "<font color='#16a34a'><b>Conforme</b></font>"
            elif res == "Modificar":
                res_html = "<font color='#d97706'><b>Modificar</b></font>"
            elif res == "Agregar":
                res_html = "<font color='#2563eb'><b>Agregar</b></font>"
            else:
                res_html = "<font color='#94a3b8'>Pendiente</font>"

            tabla_mods.append([
                Paragraph(str(idx), text_style),
                Paragraph(f"<b>{nom}</b>", text_style),
                Paragraph(res_html, text_style),
                Paragraph(com, text_style),
            ])

        t_modulos = Table(tabla_mods, colWidths=[24, 116, 90, 310])
        t_modulos.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_modulos)
        elements.append(Spacer(1, 10))

        # Observaciones generales
        if visita_out.observaciones:
            elements.append(Paragraph("Observaciones Generales", h2_style))
            elements.append(Paragraph(visita_out.observaciones, text_style))
            elements.append(Spacer(1, 10))

        # Pie de página / firmas
        elements.append(Spacer(1, 15))
        firma_data = [
            [
                Paragraph("___________________________________<br/><b>Firma del Dueño / Representante</b>", subtitle_style),
                Paragraph("___________________________________<br/><b>Firma del Evaluador / Administrador</b>", subtitle_style),
            ]
        ]
        t_firmas = Table(firma_data, colWidths=[270, 270])
        t_firmas.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ]))
        elements.append(t_firmas)

        doc.build(elements)
        return buffer.getvalue()
