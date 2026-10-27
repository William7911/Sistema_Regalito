from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from decimal import Decimal
from datetime import date, datetime


class MetricasVentas(BaseModel):
    """Total en Quetzales, cantidad y ticket promedio de ventas del día.

    `variacion_ayer` es el cambio porcentual del total de hoy contra ayer
    (None cuando ayer no hubo ventas, es decir, sin línea base).
    """

    total: Decimal = Decimal("0.00")
    cantidad: int = 0
    ticket_promedio: Decimal = Decimal("0.00")
    variacion_ayer: Optional[Decimal] = None
    total_ayer: Decimal = Decimal("0.00")


class MetricasCompras(BaseModel):
    """Total invertido y cantidad de compras del mes."""

    total: Decimal = Decimal("0.00")
    cantidad: int = 0


class TurnoDashboard(BaseModel):
    """Estado del turno de caja del usuario para la barra superior."""

    id_turno: int
    estado: str
    cajero: str = ""
    caja: Optional[str] = None
    id_sucursal: Optional[int] = None
    sucursal: Optional[str] = None
    fecha_apertura: Optional[datetime] = None
    monto_apertura: Optional[Decimal] = None


class VentasMetodoPago(BaseModel):
    """Total cobrado hoy por método de pago (neto: recibido - vuelto)."""

    nombre: str
    total: Decimal = Decimal("0.00")


class VentaDiaria(BaseModel):
    """Total de ventas de un día calendario (zona America/Guatemala)."""

    fecha: date
    total: Decimal = Decimal("0.00")


class TopProducto(BaseModel):
    """Producto más vendido por cantidad en la semana."""

    id_producto: int
    nombre: str
    cantidad: int = 0
    total: Decimal = Decimal("0.00")


class StockCritico(BaseModel):
    """Producto con stock igual o debajo del mínimo en una sucursal."""

    id_inventario: int
    id_variante: int
    producto: str
    stock_actual: int
    stock_minimo: int
    sucursal: str


class OrdenPendiente(BaseModel):
    """Orden de compra emitida que aún falta recibir."""

    id_orden: int
    proveedor: str
    fecha_emision: Optional[date] = None
    total_estimado: Decimal = Decimal("0.00")
    estado: str


class TrasladoPendiente(BaseModel):
    """Traslado de inventario en tránsito entre sucursales."""

    id_traslado: int
    producto: str
    origen: str
    destino: str
    cantidad: int
    estado: str


class VentaReciente(BaseModel):
    """Última venta registrada (folio = id_venta)."""

    folio: int
    fecha: Optional[datetime] = None
    total: Decimal = Decimal("0.00")
    vendedor: str = ""


class DashboardResumenResponse(BaseModel):
    """Resumen operativo completo para el Panel Principal."""

    ventas_hoy: MetricasVentas = MetricasVentas()
    stock_critico: int = 0
    compras_mes: MetricasCompras = MetricasCompras()
    turnos_activos: int = 0

    turno_actual: Optional[TurnoDashboard] = None
    ventas_por_metodo: List[VentasMetodoPago] = []
    mermas_mes: Decimal = Decimal("0.00")
    ventas_7dias: List[VentaDiaria] = []
    top_productos: List[TopProducto] = []
    stock_critico_lista: List[StockCritico] = []
    ordenes_pendientes: List[OrdenPendiente] = []
    traslados_pendientes: List[TrasladoPendiente] = []
    ultimas_ventas: List[VentaReciente] = []

    model_config = ConfigDict(from_attributes=True)