import io
import csv
import openpyxl
from fastapi import HTTPException
from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal

from app.schemas.reportes_schema import (
    ReporteConsolidadoResponse,
    ReporteExportadoDTO,
    VentaReporteDTO,
    MermaReporteDTO,
    CompraReporteDTO,
    UsuarioReporteDTO,
    ClienteReporteDTO,
)
from app.core.permissions import check_user_permission

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


class ReportesService:
    def __init__(self, uow):
        self.uow = uow

    async def _check_permission(self, user_id: int, permiso: str = "REPORTE_VER"):
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")

        allowed = await check_user_permission(self.uow.db, user, permiso)
        if not allowed:
            raise HTTPException(
                status_code=403,
                detail=f"Acceso denegado. Se requiere el permiso {permiso}.",
            )
        return user

    async def _check_admin(self, user_id: int):
        return await self._check_permission(user_id, "REPORTE_VER")

    # ---------------------------------------------------------------------------
    # Reporte Consolidado Operativo (Existente)
    # ---------------------------------------------------------------------------

    async def obtener_consolidado(self, fecha_inicio: date, fecha_fin: date, user_id: int) -> ReporteConsolidadoResponse:
        await self._check_permission(user_id)

        ventas_db = await self.uow.reportes.get_ventas_by_date(fecha_inicio, fecha_fin)
        mermas_db = await self.uow.reportes.get_mermas_by_date(fecha_inicio, fecha_fin)
        compras_db = await self.uow.reportes.get_compras_by_date(fecha_inicio, fecha_fin)

        ventas = [VentaReporteDTO.model_validate(v) for v in ventas_db]
        mermas = [MermaReporteDTO.model_validate(m) for m in mermas_db]
        compras = [CompraReporteDTO.model_validate(c) for c in compras_db]

        return ReporteConsolidadoResponse(ventas=ventas, mermas=mermas, compras=compras)

    async def exportar_reporte(self, fecha_inicio: date, fecha_fin: date, formato: str, user_id: int) -> ReporteExportadoDTO:
        consolidado = await self.obtener_consolidado(fecha_inicio, fecha_fin, user_id)

        if formato.lower() == "excel":
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Reporte Consolidado"

            ws.append(["--- VENTAS ---"])
            ws.append(["ID", "Fecha Hora", "Total", "Estado"])
            for v in consolidado.ventas:
                dt = v.fecha_venta.replace(tzinfo=None) if v.fecha_venta.tzinfo else v.fecha_venta
                ws.append([v.id_venta, dt, float(v.total_venta), "Completada"])

            ws.append([])

            ws.append(["--- MERMAS ---"])
            ws.append(["ID", "Fecha Hora", "Observaciones"])
            for m in consolidado.mermas:
                dt = m.fecha_merma.replace(tzinfo=None) if m.fecha_merma.tzinfo else m.fecha_merma
                ws.append([m.id_merma, dt, m.observaciones or ""])

            ws.append([])

            ws.append(["--- COMPRAS ---"])
            ws.append(["ID", "Fecha Ingreso", "Total Compra"])
            for c in consolidado.compras:
                ws.append([c.id_compra, c.fecha_ingreso, float(c.total_compra)])

            output = io.BytesIO()
            wb.save(output)
            output.seek(0)

            return ReporteExportadoDTO(
                filename=f"reporte_{fecha_inicio}_{fecha_fin}.xlsx",
                content=output.read(),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        elif formato.lower() == "csv":
            output = io.StringIO()
            writer = csv.writer(output)

            writer.writerow(["--- VENTAS ---"])
            writer.writerow(["ID", "Fecha Hora", "Total", "Estado"])
            for v in consolidado.ventas:
                writer.writerow([v.id_venta, v.fecha_venta, v.total_venta, "Completada"])

            writer.writerow([])
            writer.writerow(["--- MERMAS ---"])
            writer.writerow(["ID", "Fecha Hora", "Observaciones"])
            for m in consolidado.mermas:
                writer.writerow([m.id_merma, m.fecha_merma, m.observaciones or ""])

            writer.writerow([])
            writer.writerow(["--- COMPRAS ---"])
            writer.writerow(["ID", "Fecha Ingreso", "Total Compra"])
            for c in consolidado.compras:
                writer.writerow([c.id_compra, c.fecha_ingreso, c.total_compra])

            return ReporteExportadoDTO(
                filename=f"reporte_{fecha_inicio}_{fecha_fin}.csv",
                content=output.getvalue().encode("utf-8-sig"),
                media_type="text/csv",
            )
        else:
            raise HTTPException(status_code=400, detail="Formato de exportación no soportado")

    # ---------------------------------------------------------------------------
    # Reporte de Usuarios
    # ---------------------------------------------------------------------------

    def _map_usuario(self, u) -> UsuarioReporteDTO:
        rol_nombre = u.rol.nombre if getattr(u, "rol", None) else "Sin rol"
        return UsuarioReporteDTO(
            id_usuario=u.id_usuario,
            nombre_completo=u.nombre_completo,
            username=u.username,
            id_rol=u.id_rol,
            rol_nombre=rol_nombre,
            estado=u.estado,
            fecha_creacion=u.fecha_creacion,
        )

    async def obtener_reporte_usuarios(
        self,
        estado: Optional[str],
        fecha_desde: Optional[date],
        fecha_hasta: Optional[date],
        user_id: int,
    ) -> List[UsuarioReporteDTO]:
        await self._check_permission(user_id)
        usuarios = await self.uow.reportes.get_usuarios_reporte(
            estado=estado, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta
        )
        return [self._map_usuario(u) for u in usuarios]

    async def obtener_ficha_usuario(self, id_usuario: int, user_id: int) -> UsuarioReporteDTO:
        await self._check_permission(user_id)
        u = await self.uow.reportes.get_usuario_by_id(id_usuario)
        if not u:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return self._map_usuario(u)

    async def exportar_usuarios(
        self,
        estado: Optional[str],
        fecha_desde: Optional[date],
        fecha_hasta: Optional[date],
        formato: str,
        user_id: int,
    ) -> ReporteExportadoDTO:
        usuarios = await self.obtener_reporte_usuarios(estado, fecha_desde, fecha_hasta, user_id)
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M")

        if formato.lower() == "excel":
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Reporte de Usuarios"
            ws.append(["ID", "Nombre Completo", "Usuario", "Rol", "Estado", "Fecha Creación"])
            for u in usuarios:
                fc = u.fecha_creacion.strftime("%Y-%m-%d %H:%M") if u.fecha_creacion else "-"
                ws.append([u.id_usuario, u.nombre_completo, u.username, u.rol_nombre, u.estado, fc])

            buf = io.BytesIO()
            wb.save(buf)
            buf.seek(0)
            return ReporteExportadoDTO(
                filename=f"reporte_usuarios_{fecha_str}.xlsx",
                content=buf.read(),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        elif formato.lower() == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "Nombre Completo", "Usuario", "Rol", "Estado", "Fecha Creacion"])
            for u in usuarios:
                fc = u.fecha_creacion.strftime("%Y-%m-%d %H:%M") if u.fecha_creacion else "-"
                writer.writerow([u.id_usuario, u.nombre_completo, u.username, u.rol_nombre, u.estado, fc])

            return ReporteExportadoDTO(
                filename=f"reporte_usuarios_{fecha_str}.csv",
                content=output.getvalue().encode("utf-8-sig"),
                media_type="text/csv",
            )

        elif formato.lower() == "pdf":
            content = self._generar_pdf_usuarios_listado(usuarios, estado, fecha_desde, fecha_hasta)
            return ReporteExportadoDTO(
                filename=f"reporte_usuarios_{fecha_str}.pdf",
                content=content,
                media_type="application/pdf",
            )
        else:
            raise HTTPException(status_code=400, detail="Formato de exportación no soportado")

    async def exportar_ficha_usuario_pdf(self, id_usuario: int, user_id: int) -> ReporteExportadoDTO:
        usuario = await self.obtener_ficha_usuario(id_usuario, user_id)
        content = self._generar_pdf_ficha_usuario(usuario)
        return ReporteExportadoDTO(
            filename=f"ficha_usuario_{usuario.id_usuario}_{usuario.username}.pdf",
            content=content,
            media_type="application/pdf",
        )

    # ---------------------------------------------------------------------------
    # Reporte de Clientes
    # ---------------------------------------------------------------------------

    def _map_cliente(self, c) -> ClienteReporteDTO:
        tipo_nombre = c.tipo_cliente.nombre if getattr(c, "tipo_cliente", None) else "General"
        muni_nombre = c.municipio.nombre if getattr(c, "municipio", None) else None
        depto_nombre = None
        if getattr(c, "municipio", None) and getattr(c.municipio, "departamento", None):
            depto_nombre = c.municipio.departamento.nombre

        telefonos = [ct.telefono for ct in getattr(c, "contactos", []) if ct.telefono]
        correos = [ct.correo for ct in getattr(c, "contactos", []) if ct.correo]

        return ClienteReporteDTO(
            id_cliente=c.id_cliente,
            nit=c.nit,
            nombre_comercial=c.nombre_comercial,
            id_tipo_cliente=c.id_tipo_cliente,
            tipo_cliente_nombre=tipo_nombre,
            id_municipio=c.id_municipio,
            municipio_nombre=muni_nombre,
            departamento_nombre=depto_nombre,
            direccion=c.direccion,
            telefonos=telefonos,
            correos=correos,
            estado=c.estado,
            fecha_creacion=c.fecha_creacion,
        )

    async def obtener_reporte_clientes(
        self,
        estado: Optional[str],
        fecha_desde: Optional[date],
        fecha_hasta: Optional[date],
        user_id: int,
    ) -> List[ClienteReporteDTO]:
        await self._check_permission(user_id)
        clientes = await self.uow.reportes.get_clientes_reporte(
            estado=estado, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta
        )
        return [self._map_cliente(c) for c in clientes]

    async def obtener_ficha_cliente(self, id_cliente: int, user_id: int) -> ClienteReporteDTO:
        await self._check_permission(user_id)
        c = await self.uow.reportes.get_cliente_by_id(id_cliente)
        if not c:
            raise HTTPException(status_code=404, detail="Cliente no encontrado")
        return self._map_cliente(c)

    async def exportar_clientes(
        self,
        estado: Optional[str],
        fecha_desde: Optional[date],
        fecha_hasta: Optional[date],
        formato: str,
        user_id: int,
    ) -> ReporteExportadoDTO:
        clientes = await self.obtener_reporte_clientes(estado, fecha_desde, fecha_hasta, user_id)
        fecha_str = datetime.now().strftime("%Y%m%d_%H%M")

        if formato.lower() == "excel":
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Reporte de Clientes"
            ws.append(["ID", "NIT", "Nombre Comercial", "Tipo", "Municipio", "Departamento", "Teléfonos", "Correos", "Estado", "Fecha Creación"])
            for c in clientes:
                fc = c.fecha_creacion.strftime("%Y-%m-%d %H:%M") if c.fecha_creacion else "-"
                ws.append([
                    c.id_cliente,
                    c.nit,
                    c.nombre_comercial,
                    c.tipo_cliente_nombre,
                    c.municipio_nombre or "-",
                    c.departamento_nombre or "-",
                    ", ".join(c.telefonos) if c.telefonos else "-",
                    ", ".join(c.correos) if c.correos else "-",
                    c.estado,
                    fc,
                ])

            buf = io.BytesIO()
            wb.save(buf)
            buf.seek(0)
            return ReporteExportadoDTO(
                filename=f"reporte_clientes_{fecha_str}.xlsx",
                content=buf.read(),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        elif formato.lower() == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["ID", "NIT", "Nombre Comercial", "Tipo", "Municipio", "Departamento", "Telefonos", "Correos", "Estado", "Fecha Creacion"])
            for c in clientes:
                fc = c.fecha_creacion.strftime("%Y-%m-%d %H:%M") if c.fecha_creacion else "-"
                writer.writerow([
                    c.id_cliente,
                    c.nit,
                    c.nombre_comercial,
                    c.tipo_cliente_nombre,
                    c.municipio_nombre or "-",
                    c.departamento_nombre or "-",
                    "; ".join(c.telefonos) if c.telefonos else "-",
                    "; ".join(c.correos) if c.correos else "-",
                    c.estado,
                    fc,
                ])

            return ReporteExportadoDTO(
                filename=f"reporte_clientes_{fecha_str}.csv",
                content=output.getvalue().encode("utf-8-sig"),
                media_type="text/csv",
            )

        elif formato.lower() == "pdf":
            content = self._generar_pdf_clientes_listado(clientes, estado, fecha_desde, fecha_hasta)
            return ReporteExportadoDTO(
                filename=f"reporte_clientes_{fecha_str}.pdf",
                content=content,
                media_type="application/pdf",
            )
        else:
            raise HTTPException(status_code=400, detail="Formato de exportación no soportado")

    async def exportar_ficha_cliente_pdf(self, id_cliente: int, user_id: int) -> ReporteExportadoDTO:
        cliente = await self.obtener_ficha_cliente(id_cliente, user_id)
        content = self._generar_pdf_ficha_cliente(cliente)
        return ReporteExportadoDTO(
            filename=f"ficha_cliente_{cliente.id_cliente}_{cliente.nit}.pdf",
            content=content,
            media_type="application/pdf",
        )

    # ---------------------------------------------------------------------------
    # Generadores PDF con ReportLab
    # ---------------------------------------------------------------------------

    def _generar_pdf_usuarios_listado(
        self,
        usuarios: List[UsuarioReporteDTO],
        estado: Optional[str],
        fecha_desde: Optional[date],
        fecha_hasta: Optional[date],
    ) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle("RTitle", parent=styles["Heading1"], fontSize=16, leading=20, textColor=colors.HexColor("#0f172a"), alignment=1)
        sub_style = ParagraphStyle("RSub", parent=styles["Normal"], fontSize=10, leading=13, textColor=colors.HexColor("#64748b"), alignment=1, spaceAfter=10)
        cell_bold = ParagraphStyle("CBold", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=colors.HexColor("#0f172a"))
        cell_text = ParagraphStyle("CText", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#334155"))

        elements = []
        elements.append(Paragraph("TIENDA EL REGALITO", title_style))
        elements.append(Paragraph("REPORTE OFICIAL DE USUARIOS Y PERSONAL", sub_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=10))

        # Metadatos
        filtros_info = [
            [
                Paragraph("<b>Estado:</b> " + (estado or "Todos"), cell_text),
                Paragraph("<b>Fecha Desde:</b> " + (str(fecha_desde) if fecha_desde else "Inicio"), cell_text),
                Paragraph("<b>Fecha Hasta:</b> " + (str(fecha_hasta) if fecha_hasta else "Hoy"), cell_text),
                Paragraph("<b>Total Registros:</b> " + str(len(usuarios)), cell_text),
            ]
        ]
        t_meta = Table(filtros_info, colWidths=[135, 135, 135, 135])
        t_meta.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_meta)
        elements.append(Spacer(1, 10))

        # Tabla de usuarios
        table_data = [
            [
                Paragraph("<b>ID</b>", cell_bold),
                Paragraph("<b>Nombre Completo</b>", cell_bold),
                Paragraph("<b>Usuario</b>", cell_bold),
                Paragraph("<b>Rol Asignado</b>", cell_bold),
                Paragraph("<b>Estado</b>", cell_bold),
                Paragraph("<b>Fecha Registro</b>", cell_bold),
            ]
        ]

        for u in usuarios:
            fc = u.fecha_creacion.strftime("%Y-%m-%d %H:%M") if u.fecha_creacion else "-"
            table_data.append([
                Paragraph(str(u.id_usuario), cell_text),
                Paragraph(u.nombre_completo, cell_text),
                Paragraph(u.username, cell_text),
                Paragraph(u.rol_nombre, cell_text),
                Paragraph(u.estado, cell_text),
                Paragraph(fc, cell_text),
            ])

        t_data = Table(table_data, colWidths=[35, 160, 95, 95, 65, 90])
        t_data.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_data)

        doc.build(elements)
        return buf.getvalue()

    def _generar_pdf_ficha_usuario(self, u: UsuarioReporteDTO) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle("UTitle", parent=styles["Heading1"], fontSize=16, leading=20, textColor=colors.HexColor("#0f172a"), alignment=1)
        sub_style = ParagraphStyle("USub", parent=styles["Normal"], fontSize=11, leading=14, textColor=colors.HexColor("#64748b"), alignment=1, spaceAfter=14)
        label_style = ParagraphStyle("ULabel", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, textColor=colors.HexColor("#334155"))
        val_style = ParagraphStyle("UVal", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#0f172a"))

        elements = []
        elements.append(Paragraph("TIENDA EL REGALITO", title_style))
        elements.append(Paragraph(f"FICHA TÉCNICA DE USUARIO #{u.id_usuario}", sub_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=16))

        fc = u.fecha_creacion.strftime("%Y-%m-%d %H:%M") if u.fecha_creacion else "No registrada"
        data_card = [
            [Paragraph("ID Usuario:", label_style), Paragraph(str(u.id_usuario), val_style)],
            [Paragraph("Nombre Completo:", label_style), Paragraph(u.nombre_completo, val_style)],
            [Paragraph("Nombre de Usuario (Login):", label_style), Paragraph(u.username, val_style)],
            [Paragraph("Rol Asignado:", label_style), Paragraph(u.rol_nombre, val_style)],
            [Paragraph("Estado Operativo:", label_style), Paragraph(u.estado, val_style)],
            [Paragraph("Fecha de Registro:", label_style), Paragraph(fc, val_style)],
        ]

        t_card = Table(data_card, colWidths=[180, 350])
        t_card.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(t_card)
        elements.append(Spacer(1, 30))

        # Firmas
        firma_data = [
            [
                Paragraph("___________________________________<br/><b>Firma del Usuario</b>", sub_style),
                Paragraph("___________________________________<br/><b>Firma Administrador(a)</b>", sub_style),
            ]
        ]
        t_firma = Table(firma_data, colWidths=[265, 265])
        t_firma.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        elements.append(t_firma)

        doc.build(elements)
        return buf.getvalue()

    def _generar_pdf_clientes_listado(
        self,
        clientes: List[ClienteReporteDTO],
        estado: Optional[str],
        fecha_desde: Optional[date],
        fecha_hasta: Optional[date],
    ) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle("CTitle", parent=styles["Heading1"], fontSize=16, leading=20, textColor=colors.HexColor("#0f172a"), alignment=1)
        sub_style = ParagraphStyle("CSub", parent=styles["Normal"], fontSize=10, leading=13, textColor=colors.HexColor("#64748b"), alignment=1, spaceAfter=10)
        cell_bold = ParagraphStyle("CBold", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=colors.HexColor("#0f172a"))
        cell_text = ParagraphStyle("CText", parent=styles["Normal"], fontSize=8, leading=10, textColor=colors.HexColor("#334155"))

        elements = []
        elements.append(Paragraph("TIENDA EL REGALITO", title_style))
        elements.append(Paragraph("REPORTE OFICIAL DE CLIENTES", sub_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=10))

        filtros_info = [
            [
                Paragraph("<b>Estado:</b> " + (estado or "Todos"), cell_text),
                Paragraph("<b>Fecha Desde:</b> " + (str(fecha_desde) if fecha_desde else "Inicio"), cell_text),
                Paragraph("<b>Fecha Hasta:</b> " + (str(fecha_hasta) if fecha_hasta else "Hoy"), cell_text),
                Paragraph("<b>Total Clientes:</b> " + str(len(clientes)), cell_text),
            ]
        ]
        t_meta = Table(filtros_info, colWidths=[135, 135, 135, 135])
        t_meta.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_meta)
        elements.append(Spacer(1, 10))

        table_data = [
            [
                Paragraph("<b>ID</b>", cell_bold),
                Paragraph("<b>NIT</b>", cell_bold),
                Paragraph("<b>Nombre Comercial / Razón Social</b>", cell_bold),
                Paragraph("<b>Tipo</b>", cell_bold),
                Paragraph("<b>Ubicación</b>", cell_bold),
                Paragraph("<b>Teléfono(s)</b>", cell_bold),
                Paragraph("<b>Estado</b>", cell_bold),
            ]
        ]

        for c in clientes:
            ubicacion = f"{c.municipio_nombre or ''}, {c.departamento_nombre or ''}".strip(", ") or "-"
            tels = ", ".join(c.telefonos) if c.telefonos else "-"
            table_data.append([
                Paragraph(str(c.id_cliente), cell_text),
                Paragraph(c.nit, cell_text),
                Paragraph(c.nombre_comercial, cell_text),
                Paragraph(c.tipo_cliente_nombre, cell_text),
                Paragraph(ubicacion, cell_text),
                Paragraph(tels, cell_text),
                Paragraph(c.estado, cell_text),
            ])

        t_data = Table(table_data, colWidths=[30, 65, 160, 75, 100, 60, 50])
        t_data.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(t_data)

        doc.build(elements)
        return buf.getvalue()

    def _generar_pdf_ficha_cliente(self, c: ClienteReporteDTO) -> bytes:
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle("FCTitle", parent=styles["Heading1"], fontSize=16, leading=20, textColor=colors.HexColor("#0f172a"), alignment=1)
        sub_style = ParagraphStyle("FCSub", parent=styles["Normal"], fontSize=11, leading=14, textColor=colors.HexColor("#64748b"), alignment=1, spaceAfter=14)
        label_style = ParagraphStyle("FCLabel", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, textColor=colors.HexColor("#334155"))
        val_style = ParagraphStyle("FCVal", parent=styles["Normal"], fontSize=9, textColor=colors.HexColor("#0f172a"))

        elements = []
        elements.append(Paragraph("TIENDA EL REGALITO", title_style))
        elements.append(Paragraph(f"FICHA TÉCNICA DE CLIENTE #{c.id_cliente} - NIT: {c.nit}", sub_style))
        elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=16))

        fc = c.fecha_creacion.strftime("%Y-%m-%d %H:%M") if c.fecha_creacion else "No registrada"
        ubicacion = f"{c.municipio_nombre or ''}, {c.departamento_nombre or ''}".strip(", ") or "No asignada"
        tels = ", ".join(c.telefonos) if c.telefonos else "Ninguno"
        corrs = ", ".join(c.correos) if c.correos else "Ninguno"

        data_card = [
            [Paragraph("ID Cliente:", label_style), Paragraph(str(c.id_cliente), val_style)],
            [Paragraph("NIT:", label_style), Paragraph(c.nit, val_style)],
            [Paragraph("Nombre / Razón Social:", label_style), Paragraph(c.nombre_comercial, val_style)],
            [Paragraph("Tipo de Cliente:", label_style), Paragraph(c.tipo_cliente_nombre, val_style)],
            [Paragraph("Ubicación Geográfica:", label_style), Paragraph(ubicacion, val_style)],
            [Paragraph("Dirección Física:", label_style), Paragraph(c.direccion or "No registrada", val_style)],
            [Paragraph("Teléfono(s):", label_style), Paragraph(tels, val_style)],
            [Paragraph("Correo(s) Electrónico(s):", label_style), Paragraph(corrs, val_style)],
            [Paragraph("Estado:", label_style), Paragraph(c.estado, val_style)],
            [Paragraph("Fecha de Registro:", label_style), Paragraph(fc, val_style)],
        ]

        t_card = Table(data_card, colWidths=[180, 350])
        t_card.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ]))
        elements.append(t_card)

        doc.build(elements)
        return buf.getvalue()
