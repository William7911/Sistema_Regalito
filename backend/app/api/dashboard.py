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
    """Devuelve las métricas operativas del Panel Principal: estado de caja,
    ventas del día (por método de pago, últimos 7 días, top productos),
    mermas, stock crítico, pendientes y últimas ventas."""
    return await service.get_resumen(current_user.id_usuario)