import io
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from datetime import date
from typing import Optional, List

from app.api.deps import require_permission, get_reporte_service
from app.db.models import Usuario
from app.services.reporte_service import ReportesService
from app.schemas.reportes_schema import (
    ReporteConsolidadoResponse,
    UsuarioReporteDTO,
    ClienteReporteDTO,
    KPITotalesDTO,
    GraficaResponse,
    RankingResponse,
)

router = APIRouter(prefix="/api/reportes", tags=["Reportes"])


# ---------------------------------------------------------------------------
# Reporte Consolidado Operativo (Existente)
# ---------------------------------------------------------------------------

@router.get("", response_model=ReporteConsolidadoResponse, include_in_schema=False)
@router.get("/", response_model=ReporteConsolidadoResponse)
async def get_reportes(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    return await service.obtener_consolidado(fecha_inicio, fecha_fin, current_user.id_usuario)


@router.get("/exportar")
async def exportar_reportes(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    formato: str = Query("excel", pattern="^(excel|csv)$"),
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    result = await service.exportar_reporte(fecha_inicio, fecha_fin, formato, current_user.id_usuario)
    return StreamingResponse(
        io.BytesIO(result.content),
        media_type=result.media_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )


# ---------------------------------------------------------------------------
# Dashboard de Estadísticas: KPI / Gráficas / Rankings
# (Motor central de fechas -> el frontend dispara estos 3 endpoints en
# paralelo cada vez que el usuario presiona "Consultar")
# ---------------------------------------------------------------------------

@router.get("/kpi", response_model=KPITotalesDTO)
async def get_kpi_reportes(
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    """Totales agregados (ventas netas, mermas, compras) del rango de fechas."""
    return await service.obtener_kpi(fecha_inicio, fecha_fin, current_user.id_usuario)


@router.get("/grafica", response_model=GraficaResponse)
async def get_grafica_reportes(
    tipo: str = Query("tendencia", pattern="^(tendencia|categoria|hora)$"),
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    """Datos de la gráfica activa (pestaña: tendencia, categoría u hora)."""
    return await service.obtener_grafica(tipo, fecha_inicio, fecha_fin, current_user.id_usuario)


@router.get("/ranking", response_model=RankingResponse)
async def get_ranking_reportes(
    tipo_reporte: str = Query("productos", pattern="^(productos|clientes|estancados)$"),
    limite: int = Query(5, ge=1, le=100),
    fecha_inicio: date = Query(...),
    fecha_fin: date = Query(...),
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    """Rankings (Top Productos / Clientes / Estancados) con límite configurable."""
    return await service.obtener_ranking(tipo_reporte, fecha_inicio, fecha_fin, limite, current_user.id_usuario)


# ---------------------------------------------------------------------------
# Reportes Específicos: Usuarios
# ---------------------------------------------------------------------------

@router.get("/usuarios", response_model=List[UsuarioReporteDTO])
async def get_reporte_usuarios(
    estado: Optional[str] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    return await service.obtener_reporte_usuarios(estado, fecha_desde, fecha_hasta, current_user.id_usuario)


@router.get("/usuarios/exportar")
async def exportar_usuarios(
    estado: Optional[str] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    formato: str = Query("excel", pattern="^(excel|csv|pdf)$"),
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    result = await service.exportar_usuarios(estado, fecha_desde, fecha_hasta, formato, current_user.id_usuario)
    return Response(
        content=result.content,
        media_type=result.media_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )


@router.get("/usuarios/pdf")
async def exportar_usuarios_pdf(
    estado: Optional[str] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    result = await service.exportar_usuarios(estado, fecha_desde, fecha_hasta, "pdf", current_user.id_usuario)
    return Response(
        content=result.content,
        media_type=result.media_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )


@router.get("/usuarios/{id_usuario}", response_model=UsuarioReporteDTO)
async def get_ficha_usuario(
    id_usuario: int,
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    return await service.obtener_ficha_usuario(id_usuario, current_user.id_usuario)


@router.get("/usuarios/{id_usuario}/pdf")
async def exportar_ficha_usuario_pdf(
    id_usuario: int,
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    result = await service.exportar_ficha_usuario_pdf(id_usuario, current_user.id_usuario)
    return Response(
        content=result.content,
        media_type=result.media_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )


# ---------------------------------------------------------------------------
# Reportes Específicos: Clientes
# ---------------------------------------------------------------------------

@router.get("/clientes", response_model=List[ClienteReporteDTO])
async def get_reporte_clientes(
    estado: Optional[str] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    return await service.obtener_reporte_clientes(estado, fecha_desde, fecha_hasta, current_user.id_usuario)


@router.get("/clientes/exportar")
async def exportar_clientes(
    estado: Optional[str] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    formato: str = Query("excel", pattern="^(excel|csv|pdf)$"),
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    result = await service.exportar_clientes(estado, fecha_desde, fecha_hasta, formato, current_user.id_usuario)
    return Response(
        content=result.content,
        media_type=result.media_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )


@router.get("/clientes/pdf")
async def exportar_clientes_pdf(
    estado: Optional[str] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    result = await service.exportar_clientes(estado, fecha_desde, fecha_hasta, "pdf", current_user.id_usuario)
    return Response(
        content=result.content,
        media_type=result.media_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )


@router.get("/clientes/{id_cliente}", response_model=ClienteReporteDTO)
async def get_ficha_cliente(
    id_cliente: int,
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    return await service.obtener_ficha_cliente(id_cliente, current_user.id_usuario)


@router.get("/clientes/{id_cliente}/pdf")
async def exportar_ficha_cliente_pdf(
    id_cliente: int,
    current_user: Usuario = Depends(require_permission("REPORTE_VER")),
    service: ReportesService = Depends(get_reporte_service),
):
    result = await service.exportar_ficha_cliente_pdf(id_cliente, current_user.id_usuario)
    return Response(
        content=result.content,
        media_type=result.media_type,
        headers={"Content-Disposition": f'attachment; filename="{result.filename}"'},
    )
