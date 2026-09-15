from fastapi import APIRouter, Depends, status, Response
from typing import List
from app.api.deps import get_category_service, get_current_user
from app.db.models import User
from app.services.category_service import ConcreteCategoryService
from app.schemas import schemas

router = APIRouter()


@router.get("", response_model=List[schemas.Category])
async def list_categories(
    include_inactive: bool = False,
    service: ConcreteCategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_user),
):
    return await service.list_categories(include_inactive=include_inactive)


@router.get("/{category_id}", response_model=schemas.Category)
async def get_category(
    category_id: int,
    service: ConcreteCategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_user),
):
    return await service.get_category(category_id)


@router.post("", response_model=schemas.Category, status_code=status.HTTP_201_CREATED)
async def create_category(
    payload: schemas.CategoryCreate,
    service: ConcreteCategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_user),
):
    return await service.create_category(payload)


@router.put("/{category_id}", response_model=schemas.Category)
async def update_category(
    category_id: int,
    payload: schemas.CategoryUpdate,
    service: ConcreteCategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_user),
):
    return await service.update_category(category_id, payload)


@router.delete("/{category_id}", response_model=schemas.Category)
async def deactivate_category(
    category_id: int,
    service: ConcreteCategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_user),
):
    """Eliminación lógica (soft delete): marca la categoría como inactiva."""
    return await service.deactivate_category(category_id)