from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal


class VentaReporteDTO(BaseModel):
    id_venta: int
    fecha_venta: datetime
    total_venta: Decimal

    model_config = ConfigDict(from_attributes=True)


class MermaReporteDTO(BaseModel):
    id_merma: int
    fecha_merma: datetime
    observaciones: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CompraReporteDTO(BaseModel):
    id_compra: int
    fecha_ingreso: date
    total_compra: Decimal

    model_config = ConfigDict(from_attributes=True)


class ReporteConsolidadoResponse(BaseModel):
    ventas: List[VentaReporteDTO]
    mermas: List[MermaReporteDTO]
    compras: List[CompraReporteDTO]


class ReporteExportadoDTO(BaseModel):
    filename: str
    content: bytes
    media_type: str


# ---------------------------------------------------------------------------
# Reportes Específicos: Usuarios y Clientes
# ---------------------------------------------------------------------------

class UsuarioReporteDTO(BaseModel):
    id_usuario: int
    nombre_completo: str
    username: str
    id_rol: int
    rol_nombre: str
    estado: str
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ClienteReporteDTO(BaseModel):
    id_cliente: int
    nit: str
    nombre_comercial: str
    id_tipo_cliente: int
    tipo_cliente_nombre: str
    id_municipio: Optional[int] = None
    municipio_nombre: Optional[str] = None
    departamento_nombre: Optional[str] = None
    direccion: Optional[str] = None
    telefonos: List[str] = []
    correos: List[str] = []
    estado: str
    fecha_creacion: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
