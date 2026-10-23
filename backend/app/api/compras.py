from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_permission, UnitOfWork
from app.db.database import get_db
from app.db.models import Usuario, Proveedor, Compra
from app.schemas import compras_schema
from app.services.compra_service import ConcreteComprasService

router = APIRouter()

def get_compras_service(db: AsyncSession = Depends(get_db)):
    return ConcreteComprasService(UnitOfWork(db))

@router.get("/proveedores")
async def list_proveedores(
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    result = await db.execute(select(Proveedor))
    return result.scalars().all()


@router.get("/ordenes", response_model=List[compras_schema.OrdenCompraOut])
async def listar_ordenes(
    estado: Optional[str] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    id_proveedor: Optional[int] = Query(None),
    service: ConcreteComprasService = Depends(get_compras_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista las órdenes de compra con filtros opcionales.
    Requiere permiso COMPRA_EMITIR_ORDEN o INV_INGRESAR_MERCADERIA."""
    return await service.listar_ordenes(
        user_id=current_user.id_usuario,
        estado=estado,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        id_proveedor=id_proveedor,
    )


@router.get("/ordenes/{id_orden}", response_model=compras_schema.OrdenCompraOut)
async def obtener_orden_compra(
    id_orden: int,
    service: ConcreteComprasService = Depends(get_compras_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene los detalles de una orden de compra."""
    return await service.obtener_orden(id_orden, current_user.id_usuario)


@router.post("/ordenes", response_model=compras_schema.OrdenCompraOut, status_code=status.HTTP_201_CREATED)
async def emitir_orden_compra(
    data: compras_schema.OrdenCompraCreate,
    service: ConcreteComprasService = Depends(get_compras_service),
    current_user: Usuario = Depends(require_permission("COMPRA_EMITIR_ORDEN")),
):
    """Emite una orden de compra hacia un proveedor.
    Requiere permiso COMPRA_EMITIR_ORDEN."""
    return await service.crear_orden(data, current_user.id_usuario)


@router.post("/ordenes/{id_orden}/cancelar", response_model=compras_schema.OrdenCompraOut)
async def cancelar_orden_compra(
    id_orden: int,
    payload: Optional[compras_schema.OrdenCompraCancelar] = None,
    service: ConcreteComprasService = Depends(get_compras_service),
    current_user: Usuario = Depends(require_permission("COMPRA_EMITIR_ORDEN")),
):
    """Cancela una orden de compra en estado Emitida.
    Requiere permiso COMPRA_EMITIR_ORDEN."""
    motivo = payload.motivo if payload else None
    return await service.cancelar_orden(id_orden, current_user.id_usuario, motivo=motivo)


@router.post("/ingreso", response_model=compras_schema.IngresoMercaderiaOut, status_code=status.HTTP_201_CREATED)
async def ingresar_mercaderia(
    data: compras_schema.IngresoMercaderiaCreate,
    service: ConcreteComprasService = Depends(get_compras_service),
    current_user: Usuario = Depends(require_permission("INV_INGRESAR_MERCADERIA")),
    db: AsyncSession = Depends(get_db),
):
    """Registra el ingreso físico de mercadería a bodega aumentando existencias.
    Requiere permiso INV_INGRESAR_MERCADERIA."""
    orden = await service.ingresar_mercaderia(data, current_user.id_usuario)
    result = await db.execute(
        select(Compra)
        .options(selectinload(Compra.detalles))
        .where(Compra.id_orden == orden.id_orden)
    )
    return result.scalar_one()
