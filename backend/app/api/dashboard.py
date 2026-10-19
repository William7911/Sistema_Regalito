from fastapi import APIRouter, Depends

from app.api.deps import get_current_user, get_dashboard_service
from app.db.models import Usuario
from app.interfaces.services import DashboardService
from app.schemas.dashboard_schema import DashboardResumenResponse

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/resumen", response_model=DashboardResumenResponse)
async def get_dashboard_resumen(
    service: DashboardService = Depends(get_dashboard_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Devuelve las métricas operativas en tiempo real (ventas del día,
    stock crítico, compras del mes y turnos de caja activos)."""
    return await service.get_resumen()