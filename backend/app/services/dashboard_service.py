from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP

from app.interfaces.repositories import DashboardRepository
from app.interfaces.services import DashboardService
from app.schemas.dashboard_schema import (
    DashboardResumenResponse,
    MetricasCompras,
    MetricasVentas,
    OrdenPendiente,
    StockCritico,
    TopProducto,
    TrasladoPendiente,
    TurnoDashboard,
    VentaDiaria,
    VentaReciente,
    VentasMetodoPago,
)

GUATEMALA_OFFSET = timedelta(hours=6)


def _guatemala_today() -> date:
    """Fecha del día actual en America/Guatemala (UTC-6)."""
    return (datetime.utcnow() - GUATEMALA_OFFSET).date()


def _round(value: Decimal, places: int = 2) -> Decimal:
    quantum = Decimal("1").scaleb(-places)
    return Decimal(str(float(value))).quantize(quantum, rounding=ROUND_HALF_UP)


class ConcreteDashboardService(DashboardService):
    """Lógica de negocio del Panel Principal: ensambla las métricas reales."""

    def __init__(self, repository: DashboardRepository):
        self.repository = repository

    async def get_resumen(self, user_id: int) -> DashboardResumenResponse:
        hoy_gt = _guatemala_today()
        ayer_gt = hoy_gt - timedelta(days=1)
        inicio_semana = hoy_gt - timedelta(days=6)

        total_hoy, cantidad_hoy = await self.repository.get_ventas_hoy()
        (_, total_ayer), = await self.repository.get_ventas_por_dia(ayer_gt, ayer_gt)

        ticket_promedio = _round(total_hoy / Decimal(cantidad_hoy)) if cantidad_hoy else Decimal("0.00")

        variacion_ayer = None
        if total_ayer:
            variacion_ayer = _round((total_hoy - total_ayer) / total_ayer * 100)

        mermas_mes = await self.repository.get_mermas_mes()

        ventas_por_metodo = [
            VentasMetodoPago(nombre=nombre, total=total)
            for nombre, total in await self.repository.get_ventas_por_metodo_hoy()
        ]

        ultimas_ventas = [
            VentaReciente(
                folio=v.id_venta,
                fecha=v.fecha_venta.replace(tzinfo=timezone.utc) if v.fecha_venta else None,
                total=v.total_venta,
                vendedor=v.usuario.nombre_completo if v.usuario else "",
                articulos=sum(int(d.cantidad) for d in v.detalles) if getattr(v, "detalles", None) else 1,
            )
            for v in await self.repository.get_ultimas_ventas(5)
        ]

        # Cálculo de efectivo esperado en caja
        efectivo_ventas = Decimal("0.00")
        for m in ventas_por_metodo:
            if "efectivo" in m.nombre.lower():
                efectivo_ventas += m.total

        turno = await self.repository.get_turno_actual(user_id)
        efectivo_esperado = Decimal("0.00")
        if turno and turno.estado in ("Abierto", "Abierta"):
            efectivo_esperado = (turno.monto_apertura or Decimal("0.00")) + efectivo_ventas

        turno_actual = (
            TurnoDashboard(
                id_turno=turno.id_turno,
                estado=turno.estado,
                cajero=turno.usuario.nombre_completo if turno.usuario else "",
                caja=turno.caja.descripcion if turno.caja else None,
                id_sucursal=turno.caja.id_sucursal if turno.caja else None,
                sucursal=turno.caja.sucursal.nombre if turno.caja and turno.caja.sucursal else None,
                fecha_apertura=(
                    turno.fecha_apertura.replace(tzinfo=timezone.utc) if turno.fecha_apertura else None
                ),
                monto_apertura=turno.monto_apertura,
            )
            if turno
            else None
        )

        top_productos = [
            TopProducto(id_producto=pid, nombre=nombre, cantidad=cantidad, total=total)
            for pid, nombre, cantidad, total in await self.repository.get_ventas_top_productos(
                inicio_semana, hoy_gt, 5
            )
        ]

        inventarios_criticos = await self.repository.get_stock_critico(5)
        stock_critico_lista = [
            StockCritico(
                id_inventario=inv.id_inventario,
                id_variante=inv.id_variante,
                producto=(
                    inv.variante.producto.nombre
                    if inv.variante and inv.variante.producto
                    else f"Variante #{inv.id_variante}"
                ),
                stock_actual=inv.stock_actual,
                stock_minimo=inv.stock_minimo,
                sucursal=inv.sucursal.nombre if inv.sucursal else "",
            )
            for inv in inventarios_criticos
        ]

        ordenes_pendientes = [
            OrdenPendiente(
                id_orden=o.id_orden,
                proveedor=o.proveedor.distribuidora if o.proveedor else "",
                fecha_emision=o.fecha_emision,
                total_estimado=o.total_estimado,
                estado=o.estado,
            )
            for o in await self.repository.get_ordenes_pendientes(5)
        ]

        traslados_pendientes = [
            TrasladoPendiente(
                id_traslado=t.id_traslado,
                producto=(
                    t.variante.producto.nombre
                    if t.variante and t.variante.producto
                    else f"Variante #{t.id_variante}"
                ),
                origen=t.sucursal_origen.nombre if t.sucursal_origen else "",
                destino=t.sucursal_destino.nombre if t.sucursal_destino else "",
                cantidad=t.cantidad,
                estado=t.estado,
            )
            for t in await self.repository.get_traslados_pendientes(5)
        ]

        compras_total, compras_cant = await self.repository.get_compras_mes()
        turnos_activos = await self.repository.count_turnos_activos()

        return DashboardResumenResponse(
            ventas_hoy=MetricasVentas(
                total=total_hoy,
                cantidad=cantidad_hoy,
                ticket_promedio=ticket_promedio,
                variacion_ayer=variacion_ayer,
                total_ayer=total_ayer,
            ),
            stock_critico=(await self.repository.count_stock_critico()),
            compras_mes=MetricasCompras(total=compras_total, cantidad=compras_cant),
            turnos_activos=turnos_activos,
            turno_actual=turno_actual,
            ventas_por_metodo=ventas_por_metodo,
            mermas_mes=mermas_mes,
            ventas_7dias=[
                VentaDiaria(fecha=d, total=total)
                for d, total in await self.repository.get_ventas_por_dia(inicio_semana, hoy_gt)
            ],
            top_productos=top_productos,
            stock_critico_lista=stock_critico_lista,
            ordenes_pendientes=ordenes_pendientes,
            traslados_pendientes=traslados_pendientes,
            ultimas_ventas=ultimas_ventas,
            efectivo_esperado=efectivo_esperado,
        )