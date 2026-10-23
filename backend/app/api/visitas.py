from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permission, UnitOfWork
from app.db.database import get_db
from app.db.models import Usuario
from app.schemas.visita_schema import VisitaCreate, VisitaUpdate, VisitaOut
from app.services.visita_service import ConcreteVisitaService

router = APIRouter()


def get_visita_service(db: AsyncSession = Depends(get_db)):
    return ConcreteVisitaService(UnitOfWork(db))


@router.get("", response_model=List[VisitaOut])
async def listar_visitas(
    estado: Optional[str] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    service: ConcreteVisitaService = Depends(get_visita_service),
    current_user: Usuario = Depends(require_permission("VISITA_REGISTRAR")),
):
    """Lista visitas de seguimiento registradas con filtros opcionales."""
    return await service.listar_visitas(
        id_usuario=current_user.id_usuario,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.get("/{id_visita}", response_model=VisitaOut)
async def obtener_visita(
    id_visita: int,
    service: ConcreteVisitaService = Depends(get_visita_service),
    current_user: Usuario = Depends(require_permission("VISITA_REGISTRAR")),
):
    """Obtiene el detalle y la evaluación de módulos de una visita de seguimiento."""
    return await service.obtener_visita(id_visita, current_user.id_usuario)


@router.post("/borrador", response_model=VisitaOut, status_code=status.HTTP_201_CREATED)
async def guardar_borrador(
    data: VisitaCreate,
    service: ConcreteVisitaService = Depends(get_visita_service),
    current_user: Usuario = Depends(require_permission("VISITA_REGISTRAR")),
):
    """Crea una nueva visita de seguimiento en estado Borrador."""
    return await service.guardar_borrador(data, current_user.id_usuario)


@router.put("/{id_visita}/borrador", response_model=VisitaOut)
async def actualizar_borrador(
    id_visita: int,
    data: VisitaUpdate,
    service: ConcreteVisitaService = Depends(get_visita_service),
    current_user: Usuario = Depends(require_permission("VISITA_REGISTRAR")),
):
    """Actualiza los datos o evaluación de un borrador existente."""
    return await service.actualizar_borrador(id_visita, data, current_user.id_usuario)


@router.post("/{id_visita}/completar", response_model=VisitaOut)
async def completar_visita_existente(
    id_visita: int,
    data: Optional[VisitaUpdate] = None,
    service: ConcreteVisitaService = Depends(get_visita_service),
    current_user: Usuario = Depends(require_permission("VISITA_REGISTRAR")),
):
    """Finaliza y completa una visita de seguimiento existente."""
    return await service.completar_visita(id_visita, data, current_user.id_usuario)


@router.post("/completar", response_model=VisitaOut, status_code=status.HTTP_201_CREATED)
async def crear_y_completar_visita(
    data: VisitaCreate,
    service: ConcreteVisitaService = Depends(get_visita_service),
    current_user: Usuario = Depends(require_permission("VISITA_REGISTRAR")),
):
    """Crea y completa inmediatamente una visita de seguimiento."""
    borrador = await service.guardar_borrador(data, current_user.id_usuario)
    return await service.completar_visita(borrador.id_visita, None, current_user.id_usuario)


@router.get("/{id_visita}/pdf")
async def descargar_pdf_visita(
    id_visita: int,
    service: ConcreteVisitaService = Depends(get_visita_service),
    current_user: Usuario = Depends(require_permission("VISITA_REGISTRAR")),
):
    """Genera y descarga el reporte en PDF de la visita de seguimiento y evaluación."""
    pdf_bytes = await service.generar_pdf(id_visita, current_user.id_usuario)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="visita_seguimiento_{id_visita}.pdf"',
        },
    )
