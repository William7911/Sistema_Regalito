from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, require_permission, UnitOfWork
from app.db.database import get_db
from app.db.models import Usuario
from app.schemas.traslado_schema import TrasladoCreate, TrasladoCancelar, TrasladoOut
from app.services.traslado_service import ConcreteTrasladoService

router = APIRouter()


def get_traslado_service(db: AsyncSession = Depends(get_db)):
    return ConcreteTrasladoService(UnitOfWork(db))


@router.get("", response_model=List[TrasladoOut])
async def listar_traslados(
    estado: Optional[str] = Query(None),
    id_sucursal_origen: Optional[int] = Query(None),
    id_sucursal_destino: Optional[int] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    service: ConcreteTrasladoService = Depends(get_traslado_service),
    current_user: Usuario = Depends(require_permission("INV_INGRESAR_MERCADERIA")),
):
    """Lista traslados de inventario entre sucursales con filtros opcionales."""
    return await service.listar_traslados(
        user_id=current_user.id_usuario,
        estado=estado,
        id_sucursal_origen=id_sucursal_origen,
        id_sucursal_destino=id_sucursal_destino,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
    )


@router.get("/{id_traslado}", response_model=TrasladoOut)
async def obtener_traslado(
    id_traslado: int,
    service: ConcreteTrasladoService = Depends(get_traslado_service),
    current_user: Usuario = Depends(require_permission("INV_INGRESAR_MERCADERIA")),
):
    """Obtiene los detalles de un traslado de inventario."""
    return await service.obtener_traslado(id_traslado, current_user.id_usuario)


@router.post("", response_model=TrasladoOut, status_code=status.HTTP_201_CREATED)
async def crear_traslado(
    data: TrasladoCreate,
    service: ConcreteTrasladoService = Depends(get_traslado_service),
    current_user: Usuario = Depends(require_permission("INV_INGRESAR_MERCADERIA")),
):
    """Registra y despacha un traslado de inventario descontando stock del origen."""
    return await service.crear_envio(data, current_user.id_usuario)


@router.post("/{id_traslado}/recibir", response_model=TrasladoOut)
async def recibir_traslado(
    id_traslado: int,
    service: ConcreteTrasladoService = Depends(get_traslado_service),
    current_user: Usuario = Depends(require_permission("INV_INGRESAR_MERCADERIA")),
):
    """Confirma la recepción del traslado en la sucursal destino incrementando existencias."""
    return await service.recibir_traslado(id_traslado, current_user.id_usuario)


@router.post("/{id_traslado}/cancelar", response_model=TrasladoOut)
async def cancelar_traslado(
    id_traslado: int,
    payload: Optional[TrasladoCancelar] = None,
    service: ConcreteTrasladoService = Depends(get_traslado_service),
    current_user: Usuario = Depends(require_permission("INV_INGRESAR_MERCADERIA")),
):
    """Cancela un traslado en tránsito y devuelve las existencias a la sucursal origen."""
    motivo = payload.motivo if payload else None
    return await service.cancelar_traslado(id_traslado, current_user.id_usuario, motivo=motivo)

