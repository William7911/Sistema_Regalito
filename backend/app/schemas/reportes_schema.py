from pydantic import BaseModel, ConfigDict
from datetime import date, datetime
from typing import List, Optional
from decimal import Decimal


class TotalesConsolidadoDTO(BaseModel):
    ventas: Decimal = Decimal("0.00")
    mermas: Decimal = Decimal("0.00")
    compras: Decimal = Decimal("0.00")


class VentaReporteDTO(BaseModel):
    id_venta: int
    fecha: datetime
    fecha_venta: datetime
    estado: str = "Completada"
    vendedor: str = ""
    articulos: str = ""
    metodo_pago: str = "Efectivo"
    subtotal: Decimal = Decimal("0.00")
    descuento: Decimal = Decimal("0.00")
    total: Decimal = Decimal("0.00")
    total_venta: Decimal = Decimal("0.00")

    model_config = ConfigDict(from_attributes=True)


class MermaReporteDTO(BaseModel):
    id_merma: int
    fecha: datetime
    fecha_merma: datetime
    observaciones: Optional[str] = None
    total: Decimal = Decimal("0.00")

    model_config = ConfigDict(from_attributes=True)


class CompraReporteDTO(BaseModel):
    id_compra: int
    fecha: date
    fecha_ingreso: date
    total: Decimal = Decimal("0.00")
    total_compra: Decimal = Decimal("0.00")

    model_config = ConfigDict(from_attributes=True)


class ReporteConsolidadoResponse(BaseModel):
    totales: TotalesConsolidadoDTO = TotalesConsolidadoDTO()
    ventas: List[VentaReporteDTO] = []
    mermas: List[MermaReporteDTO] = []
    compras: List[CompraReporteDTO] = []


class ReporteExportadoDTO(BaseModel):
    filename: str
    content: bytes
    media_type: str


# ---------------------------------------------------------------------------
# Estadísticas del Dashboard de Reportes (KPI / Términos del rango de fecha)
# ---------------------------------------------------------------------------

class KPITotalesDTO(BaseModel):
    """Totales agregados (SUM) dentro del rango de fechas seleccionado.

    ventas            -> Ingresos por ventas netas (total_venta) de ventas Completadas.
    ganancia_estimada -> Ventas netas menos costo de los productos vendidos.
    costo_vendido     -> Suma del costo promedio de los artículos vendidos.
    margen_ganancia   -> Porcentaje de ganancia sobre ventas netas (%).
    mermas            -> Suma del costo de los DetalleMerma asociados a las mermas.
    compras           -> Gasto en mercadería (total_compra de las compras ingresadas).
    count_*           -> Número de registros de cada tipo dentro del rango.
    """

    ventas: Decimal = Decimal("0.00")
    count_ventas: int = 0
    ganancia_estimada: Decimal = Decimal("0.00")
    costo_vendido: Decimal = Decimal("0.00")
    margen_ganancia: Decimal = Decimal("0.00")
    mermas: Decimal = Decimal("0.00")
    count_mermas: int = 0
    compras: Decimal = Decimal("0.00")
    count_compras: int = 0


class GraficaResponse(BaseModel):
    """Respuesta unificada para las tres gráficas del panel.

    `tipo`     -> 'tendencia' | 'categoria' | 'hora'
    `etiquetas`-> Eje X (día/mes, categoría o franja horaria).
    `valores`  -> Serie numérica a dibujar (totales en Q o conteos).
    """

    tipo: str
    etiquetas: List[str] = []
    valores: List[Decimal] = []


class RankingItemDTO(BaseModel):
    """Fila de un ranking (Top Productos / Clientes / Estancados).

    nombre      -> Nombre a mostrar (producto, variante o cliente).
    valor       -> Monto en Q (ventas, compras del cliente o valor de inventario
                   estancado según el tipo de ranking).
    cantidad    -> Opcional: unidades vendidas o unidades en stock.
    """

    nombre: str
    valor: Decimal = Decimal("0.00")
    cantidad: Optional[int] = None


class RankingResponse(BaseModel):
    """Respuesta completa del widget de rankings."""

    tipo: str
    items: List[RankingItemDTO] = []


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
    ventas_count: int = 0
    total_vendido: Decimal = Decimal("0.00")
    turnos_cerrados: int = 0
    diferencia_caja: Decimal = Decimal("0.00")
    ingresos_bodega: int = 0

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
