from typing import List
from fastapi import APIRouter, Depends, status
from app.api.deps import get_current_user, get_merma_service
from app.db.models import Usuario
from app.services.merma_service import ConcreteMermaService
from app.schemas import merma_schema

router = APIRouter()


@router.get("/motivos", response_model=List[merma_schema.MotivoMermaOut])
async def list_motivos_merma(
    service: ConcreteMermaService = Depends(get_merma_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna el catálogo oficial de motivos de merma de inventario."""
    return await service.get_motivos()


@router.post("", response_model=merma_schema.MermaOut, status_code=status.HTTP_201_CREATED)
async def create_merma(
    data: merma_schema.MermaCreate,
    service: ConcreteMermaService = Depends(get_merma_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Registra una merma de inventario aplicando el descargo atómico de existencias (RF10)."""
    return await service.registrar_merma(data, current_user.id_usuario)


@router.get("", response_model=merma_schema.MermaList)
async def list_mermas(
    filters: merma_schema.MermaFilter = Depends(),
    service: ConcreteMermaService = Depends(get_merma_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista las mermas registradas con filtros de sucursal y rango de fechas."""
    items = await service.list_mermas(filters)
    total = await service.count_mermas(filters)
    return merma_schema.MermaList(total=total, items=items)

