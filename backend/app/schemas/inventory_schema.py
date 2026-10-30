from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class InventoryBase(BaseModel):
    stock_actual: int = Field(..., ge=0, description="Stock actual de la variante en la sucursal")
    stock_minimo: int = Field(..., ge=0, description="Nivel mínimo de stock para generar alerta")

class InventoryCreate(InventoryBase):
    id_variante: int = Field(..., gt=0)
    id_sucursal: int = Field(..., gt=0)
    id_area: Optional[int] = None

class InventoryUpdate(BaseModel):
    stock_minimo: Optional[int] = Field(None, ge=0)
    id_area: Optional[int] = None

class StockAdjustment(BaseModel):
    cantidad: int = Field(..., description="Cantidad a ajustar (positiva o negativa)")
    motivo: str = Field(..., min_length=3, max_length=150, description="Motivo del ajuste")

class InventoryResponse(InventoryBase):
    id_inventario: int
    id_variante: int
    id_sucursal: int
    id_area: Optional[int]
    fecha_actualizacion: datetime
    
    # Datos adicionales para presentación (opcional)
    id_producto: Optional[int] = None
    producto_nombre: Optional[str] = None
    producto_estado: Optional[str] = None
    variante_sku: Optional[str] = None
    talla: Optional[str] = None
    color: Optional[str] = None
    sucursal_nombre: Optional[str] = None
    # Imagen del producto: el frontend la usa para la miniatura y el zoom.
    imagen_url: Optional[str] = None

    class Config:
        from_attributes = True

class AlertaStockResponse(BaseModel):
    id_alerta: int
    id_inventario: int
    mensaje: str
    fecha_generacion: datetime
    estado: str
    producto_nombre: Optional[str] = None
    variante_sku: Optional[str] = None
    stock_actual: Optional[int] = None
    stock_minimo: Optional[int] = None

    class Config:
        from_attributes = True
