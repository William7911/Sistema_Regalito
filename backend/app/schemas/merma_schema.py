from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class MotivoMermaOut(BaseModel):
    id_motivo: int
    descripcion: str

    model_config = ConfigDict(from_attributes=True)


class DetalleMermaCreate(BaseModel):
    id_variante: int = Field(..., description="ID de la variante del producto a mermar")
    id_motivo: int = Field(..., gt=0, description="ID del motivo de merma (catálogo motivo_merma)")
    cantidad: int = Field(..., gt=0, description="Cantidad de unidades mermadas (debe ser mayor a 0)")


class MermaCreate(BaseModel):
    id_sucursal: int = Field(..., description="Sucursal donde se produce la merma")
    observaciones: Optional[str] = Field(default=None, max_length=255, description="Observaciones generales de la merma")
    detalles: List[DetalleMermaCreate] = Field(..., min_length=1, description="Lista de productos/variantes a mermar")


class DetalleMermaOut(BaseModel):
    id_detalle_merma: int
    id_merma: int
    id_variante: int
    id_motivo: int
    cantidad: int
    costo_perdida: Decimal
    motivo: Optional[MotivoMermaOut] = None

    model_config = ConfigDict(from_attributes=True)


class MermaOut(BaseModel):
    id_merma: int
    id_sucursal: int
    id_usuario: int
    fecha_merma: datetime
    observaciones: Optional[str] = None
    costo_total_perdida: Optional[Decimal] = None
    detalles: List[DetalleMermaOut] = []

    model_config = ConfigDict(from_attributes=True)


class MermaFilter(BaseModel):
    id_sucursal: Optional[int] = None
    fecha_desde: Optional[datetime] = None
    fecha_hasta: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=500)
    offset: int = Field(default=0, ge=0)


class MermaList(BaseModel):
    total: int
    items: List[MermaOut]

