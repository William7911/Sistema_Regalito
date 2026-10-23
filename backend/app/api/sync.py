from fastapi import APIRouter, Depends, status
from app.api.deps import get_sync_service, get_current_user
from app.db.models import Usuario
from app.services.sync_service import ConcreteSyncService

router = APIRouter()


@router.post("/pull-local")
async def pull_to_local_sqlite(
    service: ConcreteSyncService = Depends(get_sync_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Extrae el catálogo, precios, usuarios, roles y permisos desde PostgreSQL y los replica en SQLite local."""
    return await service.pull_and_replicate_to_local()


@router.get("/status")
async def get_sync_status(
    service: ConcreteSyncService = Depends(get_sync_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna el estado actual de la réplica local en SQLite (existencia del archivo, conteos, última fecha)."""
    return await service.get_sync_status()


@router.get("/local-preview")
async def get_local_preview(
    service: ConcreteSyncService = Depends(get_sync_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna los productos con precios (detalle/mayoreo) y los usuarios leídos directamente desde SQLite local."""
    return await service.get_local_preview()

