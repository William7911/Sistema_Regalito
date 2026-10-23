from fastapi import APIRouter, Depends
from app.api.deps import get_bitacora_service, require_permission
from app.schemas import catalogo_schema as schemas

router = APIRouter(dependencies=[Depends(require_permission("BITACORA_CONSULTAR"))])


@router.get("", response_model=schemas.BitacoraList)
async def list_bitacora(
    filters: schemas.BitacoraFilter = Depends(),
    service=Depends(get_bitacora_service),
):
    """Consulta de solo lectura de la bitácora de auditoría (permiso BITACORA_CONSULTAR)."""
    items = await service.search(filters)
    total = await service.count(filters)
    return schemas.BitacoraList(total=total, items=items)
