from fastapi import APIRouter, Depends
from app.api.deps import get_historial_precio_service, require_permission
from app.schemas import catalogo_schema as schemas

router = APIRouter(dependencies=[Depends(require_permission("REPORTE_VER"))])


@router.get("", response_model=schemas.HistorialPrecioList)
async def list_historial_precios(
    filters: schemas.HistorialPrecioFilter = Depends(),
    service=Depends(get_historial_precio_service),
):
    """Consulta de solo lectura del historial de precios por producto o variante."""
    items = await service.search(filters)
    total = await service.count(filters)
    return schemas.HistorialPrecioList(total=total, items=items)
