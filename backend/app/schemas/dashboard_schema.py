from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class MetricasVentas(BaseModel):
    """Total en Quetzales y cantidad de ventas del día."""

    total: Decimal
    cantidad: int


class MetricasCompras(BaseModel):
    """Total invertido y cantidad de compras del mes."""

    total: Decimal
    cantidad: int


class DashboardResumenResponse(BaseModel):
    """Resumen operativo en tiempo real para el Panel Principal."""

    ventas_hoy: MetricasVentas
    stock_critico: int
    compras_mes: MetricasCompras
    turnos_activos: int

    model_config = ConfigDict(from_attributes=True)