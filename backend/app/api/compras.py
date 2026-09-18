from datetime import date
from decimal import Decimal
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, require_permission
from app.db.database import get_db
from app.db.models import (
    Usuario, Proveedor, OrdenCompra, DetalleOrdenCompra,
    Compra, DetalleCompra, InventarioSucursal
)
from app.schemas import compras_schema

router = APIRouter()


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
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_permission("COMPRA_EMITIR_ORDEN")),
):
    """Emite una orden de compra hacia un proveedor (RF Proceso 3).
    Requiere permiso COMPRA_EMITIR_ORDEN."""
    proveedor = await db.get(Proveedor, data.id_proveedor)
    if not proveedor:
        raise HTTPException(status_code=404, detail="El proveedor especificado no existe.")

    total_estimado = sum(
        Decimal(str(item.cantidad_pedida)) * Decimal(str(item.costo_pactado))
        for item in data.detalles
    )

    orden = OrdenCompra(
        id_proveedor=data.id_proveedor,
        id_usuario=current_user.id_usuario,
        fecha_emision=date.today(),
        total_estimado=total_estimado,
        estado="Emitida",
    )
    db.add(orden)
    await db.flush()

    for item in data.detalles:
        det = DetalleOrdenCompra(
            id_orden=orden.id_orden,
            id_variante=item.id_variante,
            cantidad_pedida=item.cantidad_pedida,
            costo_pactado=item.costo_pactado,
        )
        db.add(det)

    await db.commit()
    await db.refresh(orden)

    stmt = select(OrdenCompra).options(selectinload(OrdenCompra.detalles)).where(OrdenCompra.id_orden == orden.id_orden)
    res = await db.execute(stmt)
    return res.scalar_one()


@router.post("/ingreso", response_model=compras_schema.IngresoMercaderiaOut, status_code=status.HTTP_201_CREATED)
async def ingresar_mercaderia(
    data: compras_schema.IngresoMercaderiaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Usuario = Depends(require_permission("INV_INGRESAR_MERCADERIA")),
):
    """Registra el ingreso físico de mercadería a bodega aumentando existencias (RF Proceso 3).
    Requiere permiso INV_INGRESAR_MERCADERIA."""
    proveedor = await db.get(Proveedor, data.id_proveedor)
    if not proveedor:
        raise HTTPException(status_code=404, detail="El proveedor especificado no existe.")

    subtotal_mercaderia = sum(
        Decimal(str(item.cantidad_recibida)) * Decimal(str(item.costo_unitario))
        for item in data.detalles
    )
    total_compra = subtotal_mercaderia + data.gasto_flete + data.gasto_cargadores

    compra = Compra(
        id_orden=data.id_orden,
        id_proveedor=data.id_proveedor,
        id_usuario=current_user.id_usuario,
        numero_factura_proveedor=data.numero_factura_proveedor,
        fecha_ingreso=date.today(),
        subtotal_mercaderia=subtotal_mercaderia,
        gasto_flete=data.gasto_flete,
        gasto_cargadores=data.gasto_cargadores,
        total_compra=total_compra,
    )
    db.add(compra)
    await db.flush()

    for item in data.detalles:
        subtotal_item = Decimal(str(item.cantidad_recibida)) * Decimal(str(item.costo_unitario))
        det = DetalleCompra(
            id_compra=compra.id_compra,
            id_variante=item.id_variante,
            cantidad_recibida=item.cantidad_recibida,
            costo_unitario=item.costo_unitario,
            subtotal=subtotal_item,
        )
        db.add(det)

        sucursal_id = item.id_sucursal or 1
        res_inv = await db.execute(
            select(InventarioSucursal).where(
                InventarioSucursal.id_variante == item.id_variante,
                InventarioSucursal.id_sucursal == sucursal_id,
            )
        )
        inventario = res_inv.scalar_one_or_none()
        if inventario:
            inventario.stock_actual += item.cantidad_recibida

    if data.id_orden:
        orden = await db.get(OrdenCompra, data.id_orden)
        if orden:
            orden.estado = "Recibida"

    await db.commit()
    await db.refresh(compra)

    stmt = select(Compra).options(selectinload(Compra.detalles)).where(Compra.id_compra == compra.id_compra)
    res = await db.execute(stmt)
    return res.scalar_one()

