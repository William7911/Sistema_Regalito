from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class FelItem(BaseModel):
    id_variante: int
    descripcion: str = ""
    cantidad: int = Field(default=1, gt=0)
    precio_unitario: Decimal = Field(default=Decimal("0.00"), ge=0)
    subtotal: Decimal = Field(default=Decimal("0.00"), ge=0)
    impuesto: Decimal = Field(default=Decimal("0.00"), ge=0)


class FelEmisionRequest(BaseModel):
    id_venta: int = Field(..., description="ID de la venta a certificar")
    nit_receptor: str = Field(..., description="NIT del receptor (CF si es consumidor final)")
    nombre_receptor: str = Field(default="", description="Nombre o razón social del receptor")
    total: Decimal = Field(..., ge=0, description="Total de la factura")
    items: List[FelItem] = Field(default_factory=list, description="Líneas del DTE")


class FelCertificacionRespuesta(BaseModel):
    uuid: str = Field(..., description="UUID de autorización SAT")
    serie: str = Field(default="", description="Serie del DTE")
    numero: str = Field(default="", description="Número de DTE")
    fecha: Optional[datetime] = None
    xml: Optional[str] = None


class FelEmisionResponse(BaseModel):
    id_factura: int
    id_venta: int
    numero_autorizacion_sat: Optional[str] = None
    serie: Optional[str] = None
    numero_dte: Optional[str] = None
    fecha_certificacion: Optional[datetime] = None
    nit_receptor: str
    nombre_receptor: str
    total_facturado: Decimal
    estado: str

    model_config = ConfigDict(from_attributes=True)


class FelReintentoRequest(BaseModel):
    nit_receptor: Optional[str] = None
    nombre_receptor: Optional[str] = None
