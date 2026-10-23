from app.interfaces.repositories import DashboardRepository
from app.interfaces.services import DashboardService
from app.schemas.dashboard_schema import (
    DashboardResumenResponse,
    MetricasCompras,
    MetricasVentas,
)


class ConcreteDashboardService(DashboardService):
    """Lógica de negocio del Panel Principal: ensambla las métricas reales."""

    def __init__(self, repository: DashboardRepository):
        self.repository = repository

    async def get_resumen(self) -> DashboardResumenResponse:
        ventas_total, ventas_cant = await self.repository.get_ventas_hoy()
        stock_critico = await self.repository.count_stock_critico()
        compras_total, compras_cant = await self.repository.get_compras_mes()
        turnos_activos = await self.repository.count_turnos_activos()

        return DashboardResumenResponse(
            ventas_hoy=MetricasVentas(total=ventas_total, cantidad=ventas_cant),
            stock_critico=stock_critico,
            compras_mes=MetricasCompras(total=compras_total, cantidad=compras_cant),
            turnos_activos=turnos_activos,
        )