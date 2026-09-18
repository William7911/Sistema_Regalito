from fastapi import APIRouter, Depends, status
from app.api.deps import get_user_service, get_current_user
from app.db.models import Usuario
from app.services.user_service import ConcreteUserService
from app.schemas import schemas

router = APIRouter()


@router.get("", response_model=schemas.UserList)
async def list_users(
    filters: schemas.UserFilter = Depends(),
    service: ConcreteUserService = Depends(get_user_service),
    current_user: Usuario = Depends(get_current_user),
):
    items = await service.list_users(filters)
    total = await service.count_users(filters)
    return schemas.UserList(total=total, items=items)


@router.get("/{user_id}", response_model=schemas.UserResponse)
async def get_user(
    user_id: int,
    service: ConcreteUserService = Depends(get_user_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.get_user(user_id)


@router.post("", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: schemas.UserCreate,
    service: ConcreteUserService = Depends(get_user_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.create_user(payload)


@router.put("/{user_id}", response_model=schemas.UserResponse)
async def update_user(
    user_id: int,
    payload: schemas.UserUpdate,
    service: ConcreteUserService = Depends(get_user_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.update_user(user_id, payload)


@router.delete("/{user_id}", response_model=schemas.UserResponse)
async def deactivate_user(
    user_id: int,
    service: ConcreteUserService = Depends(get_user_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Eliminación lógica (soft delete): marca el usuario como inactivo."""
    return await service.deactivate_user(user_id)