from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class TrasladoCreate(BaseModel):
    id_sucursal_origen: int
    id_sucursal_destino: int
    id_variante: int
    cantidad: int = Field(..., gt=0)
    observaciones: Optional[str] = None


class TrasladoCancelar(BaseModel):
    motivo: Optional[str] = None


class TrasladoOut(BaseModel):
    id_traslado: int
    id_variante: int
    id_sucursal_origen: int
    id_sucursal_destino: int
    cantidad: int
    fecha_traslado: datetime
    estado: str
    id_usuario_envia: Optional[int] = None
    id_usuario_recibe: Optional[int] = None
    fecha_recepcion: Optional[datetime] = None
    observaciones: Optional[str] = None

    # Enriched fields
    nombre_origen: Optional[str] = None
    nombre_destino: Optional[str] = None
    nombre_producto: Optional[str] = None
    variante_info: Optional[str] = None
    codigo_barras: Optional[str] = None
    nombre_usuario_envia: Optional[str] = None
    nombre_usuario_recibe: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

