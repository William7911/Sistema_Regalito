from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from decimal import Decimal
from datetime import date


class DetalleOrdenCompraCreate(BaseModel):
    id_variante: int
    cantidad_pedida: int = Field(..., gt=0)
    costo_pactado: Decimal = Field(..., ge=0)


class OrdenCompraCreate(BaseModel):
    id_proveedor: int
    detalles: List[DetalleOrdenCompraCreate] = Field(..., min_length=1)


class DetalleOrdenCompraOut(BaseModel):
    id_detalle_orden: int
    id_orden: int
    id_variante: int
    cantidad_pedida: int
    costo_pactado: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrdenCompraOut(BaseModel):
    id_orden: int
    id_proveedor: int
    id_usuario: int
    fecha_emision: date
    total_estimado: Decimal
    estado: str
    detalles: List[DetalleOrdenCompraOut] = []

    model_config = ConfigDict(from_attributes=True)


class DetalleIngresoCreate(BaseModel):
    id_variante: int
    cantidad_recibida: int = Field(..., gt=0)
    costo_unitario: Decimal = Field(..., ge=0)
    id_sucursal: Optional[int] = 1


class IngresoMercaderiaCreate(BaseModel):
    id_proveedor: int
    numero_factura_proveedor: str = Field(..., min_length=1, max_length=50)
    id_orden: Optional[int] = None
    gasto_flete: Decimal = Field(default=Decimal("0.00"), ge=0)
    gasto_cargadores: Decimal = Field(default=Decimal("0.00"), ge=0)
    detalles: List[DetalleIngresoCreate] = Field(..., min_length=1)


class DetalleIngresoOut(BaseModel):
    id_detalle_compra: int
    id_compra: int
    id_variante: int
    cantidad_recibida: int
    costo_unitario: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class IngresoMercaderiaOut(BaseModel):
    id_compra: int
    id_orden: Optional[int] = None
    id_proveedor: int
    id_usuario: int
    numero_factura_proveedor: str
    fecha_ingreso: date
    subtotal_mercaderia: Decimal
    gasto_flete: Decimal
    gasto_cargadores: Decimal
    total_compra: Decimal
    detalles: List[DetalleIngresoOut] = []

    model_config = ConfigDict(from_attributes=True)

