from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class SaleItemCreate(BaseModel):
    id_variante: int = Field(..., description="ID de la variante del producto vendido")
    cantidad: int = Field(..., gt=0, description="Cantidad vendida (mayor a 0)")


class PaymentCreate(BaseModel):
    id_metodo_pago: int = Field(default=1, description="1: Efectivo, 2: Transferencia, etc.")
    monto_recibido: Decimal = Field(..., gt=0, decimal_places=2, description="Monto entregado por el cliente")


class SaleCreate(BaseModel):
    id_sucursal: int = Field(..., description="Sucursal donde se realiza la venta")
    id_cliente: Optional[int] = Field(default=None, description="Cliente opcional (consumidor final si es None)")
    items: List[SaleItemCreate] = Field(..., min_length=1, description="Líneas de productos a vender")
    pagos: List[PaymentCreate] = Field(..., min_length=1, description="Métodos y montos de pago")


class SaleItemResponse(BaseModel):
    id_detalle_venta: int
    id_venta: int
    id_variante: int
    cantidad: int
    precio_unitario: Decimal
    descuento_item: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class PaymentResponse(BaseModel):
    id_pago: int
    id_venta: int
    id_metodo_pago: int
    monto_recibido: Decimal
    vuelto_entregado: Decimal

    model_config = ConfigDict(from_attributes=True)


class SaleResponse(BaseModel):
    id_venta: int
    id_turno: int
    id_cliente: Optional[int] = None
    id_usuario: int
    fecha_venta: datetime
    subtotal: Decimal
    descuento_total: Decimal
    total_venta: Decimal
    estado: str
    cambio: Optional[Decimal] = Decimal("0.00")
    detalles: List[SaleItemResponse] = []
    pagos: List[PaymentResponse] = []

    model_config = ConfigDict(from_attributes=True)


class SaleFilter(BaseModel):
    id_turno: Optional[int] = None
    id_cliente: Optional[int] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    estado: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class SaleList(BaseModel):
    total: int
    items: List[SaleResponse]

