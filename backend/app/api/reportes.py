import io
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from datetime import date
from app.api.deps import require_admin, get_reporte_service
from app.db.models import Usuario
from app.services.reporte_service import ReportesService
from app.schemas.reportes_schema import ReporteConsolidadoResponse

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])

@router.get("/", response_model=ReporteConsolidadoResponse)
async def get_reportes(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    current_user: Usuario = Depends(require_admin),
    service: ReportesService = Depends(get_reporte_service)
):
    return await service.obtener_consolidado(fecha_inicio, fecha_fin, current_user.id_usuario)

@router.get("/exportar")
async def exportar_reportes(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    formato: str = Query("excel", regex="^(excel|csv)$"),
    current_user: Usuario = Depends(require_admin),
    service: ReportesService = Depends(get_reporte_service)
):
    result = await service.exportar_reporte(fecha_inicio, fecha_fin, formato, current_user.id_usuario)
    
    return StreamingResponse(
        io.BytesIO(result.content),
        media_type=result.media_type,
        headers={"Content-Disposition": f"attachment; filename={result.filename}"}
    )
