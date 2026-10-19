from fastapi import APIRouter, Depends, status
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


@router.post("/ordenes", response_model=compras_schema.OrdenCompraOut, status_code=status.HTTP_201_CREATED)
async def emitir_orden_compra(
    data: compras_schema.OrdenCompraCreate,
    service: ConcreteComprasService = Depends(get_compras_service),
    current_user: Usuario = Depends(require_permission("COMPRA_EMITIR_ORDEN")),
):
    """Emite una orden de compra hacia un proveedor.
    Requiere permiso COMPRA_EMITIR_ORDEN."""
    return await service.crear_orden(data, current_user.id_usuario)


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
