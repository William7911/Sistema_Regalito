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
