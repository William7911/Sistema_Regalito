from fastapi import APIRouter, Depends, status
from typing import List
from app.api.deps import get_role_service, get_current_user
from app.db.models import Usuario
from app.services.role_service import ConcreteRoleService
from app.schemas import schemas

router = APIRouter()


@router.get("", response_model=List[schemas.Role])
async def list_roles(
    include_inactive: bool = False,
    service: ConcreteRoleService = Depends(get_role_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.list_roles(include_inactive=include_inactive)


@router.get("/{role_id}", response_model=schemas.Role)
async def get_role(
    role_id: int,
    service: ConcreteRoleService = Depends(get_role_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.get_role(role_id)


@router.post("", response_model=schemas.Role, status_code=status.HTTP_201_CREATED)
async def create_role(
    payload: schemas.RoleCreate,
    service: ConcreteRoleService = Depends(get_role_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.create_role(payload)


@router.put("/{role_id}", response_model=schemas.Role)
async def update_role(
    role_id: int,
    payload: schemas.RoleUpdate,
    service: ConcreteRoleService = Depends(get_role_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.update_role(role_id, payload)


@router.delete("/{role_id}", response_model=schemas.Role)
async def deactivate_role(
    role_id: int,
    service: ConcreteRoleService = Depends(get_role_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Eliminación lógica (soft delete): marca el rol como inactivo."""
    return await service.deactivate_role(role_id)