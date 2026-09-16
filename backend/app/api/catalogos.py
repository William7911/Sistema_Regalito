from fastapi import APIRouter, Depends
from typing import List, Optional
from app.api.deps import get_catalogo_service, get_current_user
from app.db.models import Usuario
from app.services.catalogo_service import ConcreteCatalogoService
from app.schemas import schemas

router = APIRouter()


@router.get("/subcategorias", response_model=List[schemas.SubcategoriaOut])
async def list_subcategorias(
    include_inactive: bool = False,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.list_subcategorias(include_inactive=include_inactive)


@router.get("/unidades", response_model=List[schemas.UnidadMedidaOut])
async def list_unidades(
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.list_unidades()


@router.get("/sucursales", response_model=List[schemas.SucursalOut])
async def list_sucursales(
    include_inactive: bool = False,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.list_sucursales(include_inactive=include_inactive)


@router.get("/areas", response_model=List[schemas.AreaBodegaOut])
async def list_areas(
    sucursal_id: Optional[int] = None,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.list_areas(sucursal_id=sucursal_id)