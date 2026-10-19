import io
import csv
import openpyxl
from fastapi import HTTPException
from datetime import date
from decimal import Decimal
from app.schemas.reportes_schema import (
    ReporteConsolidadoResponse, 
    ReporteExportadoDTO,
    VentaReporteDTO,
    MermaReporteDTO,
    CompraReporteDTO
)
from app.core.permissions import check_user_permission

class ReportesService:
    def __init__(self, uow):
        self.uow = uow

    async def _check_admin(self, user_id: int):
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="Usuario no encontrado")
        
        # Validar si es administradora
        if not user.rol or user.rol.nombre != "Administradora":
            raise HTTPException(status_code=403, detail="Acceso denegado. Solo administradoras pueden acceder a los reportes.")

    async def obtener_consolidado(self, fecha_inicio: date, fecha_fin: date, user_id: int) -> ReporteConsolidadoResponse:
        await self._check_admin(user_id)
        
        ventas_db = await self.uow.reportes.get_ventas_by_date(fecha_inicio, fecha_fin)
        mermas_db = await self.uow.reportes.get_mermas_by_date(fecha_inicio, fecha_fin)
        compras_db = await self.uow.reportes.get_compras_by_date(fecha_inicio, fecha_fin)
        
        ventas = [VentaReporteDTO.model_validate(v) for v in ventas_db]
        mermas = [MermaReporteDTO.model_validate(m) for m in mermas_db]
        compras = [CompraReporteDTO.model_validate(c) for c in compras_db]
        
        return ReporteConsolidadoResponse(ventas=ventas, mermas=mermas, compras=compras)

    async def exportar_reporte(self, fecha_inicio: date, fecha_fin: date, formato: str, user_id: int) -> ReporteExportadoDTO:
        # Esto valida también los permisos internamente
        consolidado = await self.obtener_consolidado(fecha_inicio, fecha_fin, user_id)
        
        if formato.lower() == "excel":
            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Reporte Consolidado"
            
            # Escribir Ventas
            ws.append(["--- VENTAS ---"])
            ws.append(["ID", "Fecha Hora", "Total", "Estado"])
            for v in consolidado.ventas:
                # Convertimos datetime sin timezone a naive para Excel si es necesario
                dt = v.fecha_venta.replace(tzinfo=None) if v.fecha_venta.tzinfo else v.fecha_venta
                ws.append([v.id_venta, dt, float(v.total_venta), "Completada"])
                
            ws.append([])
            
            # Escribir Mermas
            ws.append(["--- MERMAS ---"])
            ws.append(["ID", "Fecha Hora", "Observaciones"])
            for m in consolidado.mermas:
                dt = m.fecha_merma.replace(tzinfo=None) if m.fecha_merma.tzinfo else m.fecha_merma
                ws.append([m.id_merma, dt, m.observaciones or ""])
                
            ws.append([])
            
            # Escribir Compras
            ws.append(["--- COMPRAS ---"])
            ws.append(["ID", "Fecha Ingreso", "Total Compra"])
            for c in consolidado.compras:
                ws.append([c.id_compra, c.fecha_ingreso, float(c.total_compra)])
            
            # Save to BytesIO
            output = io.BytesIO()
            wb.save(output)
            output.seek(0)
            
            return ReporteExportadoDTO(
                filename=f"reporte_{fecha_inicio}_{fecha_fin}.xlsx",
                content=output.read(),
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        elif formato.lower() == "csv":
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Ventas
            writer.writerow(["--- VENTAS ---"])
            writer.writerow(["ID", "Fecha Hora", "Total", "Estado"])
            for v in consolidado.ventas:
                writer.writerow([v.id_venta, v.fecha_venta, v.total_venta, "Completada"])
            
            writer.writerow([])
            
            # Mermas
            writer.writerow(["--- MERMAS ---"])
            writer.writerow(["ID", "Fecha Hora", "Observaciones"])
            for m in consolidado.mermas:
                writer.writerow([m.id_merma, m.fecha_merma, m.observaciones or ""])
                
            writer.writerow([])
            
            # Compras
            writer.writerow(["--- COMPRAS ---"])
            writer.writerow(["ID", "Fecha Ingreso", "Total Compra"])
            for c in consolidado.compras:
                writer.writerow([c.id_compra, c.fecha_ingreso, c.total_compra])
                
            # Codificar a bytes
            content_bytes = output.getvalue().encode('utf-8')
            
            return ReporteExportadoDTO(
                filename=f"reporte_{fecha_inicio}_{fecha_fin}.csv",
                content=content_bytes,
                media_type="text/csv"
            )
        else:
            raise HTTPException(status_code=400, detail="Formato de exportación no soportado (debe ser excel o csv)")
