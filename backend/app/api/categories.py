from fastapi import APIRouter, Depends, status
from typing import List
from app.api.deps import get_category_service, get_current_user
from app.db.models import Usuario
from app.services.category_service import ConcreteCategoryService
from app.schemas import schemas

router = APIRouter()


@router.get("", response_model=List[schemas.CategoriaOut])
async def list_categories(
    include_inactive: bool = False,
    service: ConcreteCategoryService = Depends(get_category_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.list_categories(include_inactive=include_inactive)


@router.get("/{category_id}", response_model=schemas.CategoriaOut)
async def get_category(
    category_id: int,
    service: ConcreteCategoryService = Depends(get_category_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.get_category(category_id)


@router.post("", response_model=schemas.CategoriaOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: schemas.CategoriaCreate,
    service: ConcreteCategoryService = Depends(get_category_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.create_category(payload)


@router.put("/{category_id}", response_model=schemas.CategoriaOut)
async def update_category(
    category_id: int,
    payload: schemas.CategoriaUpdate,
    service: ConcreteCategoryService = Depends(get_category_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.update_category(category_id, payload)


@router.delete("/{category_id}", response_model=schemas.CategoriaOut)
async def deactivate_category(
    category_id: int,
    service: ConcreteCategoryService = Depends(get_category_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Eliminación lógica (soft delete): marca la categoría como inactiva."""
    return await service.deactivate_category(category_id)