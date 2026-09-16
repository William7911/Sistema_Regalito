from fastapi import APIRouter, Depends, status
from typing import List
from app.api.deps import get_department_service, get_current_user
from app.db.models import Usuario
from app.services.department_service import ConcreteDepartmentService
from app.schemas import schemas

router = APIRouter()


@router.get("", response_model=List[schemas.Department])
async def list_departments(
    include_inactive: bool = False,
    service: ConcreteDepartmentService = Depends(get_department_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.list_departments(include_inactive=include_inactive)


@router.get("/{department_id}", response_model=schemas.Department)
async def get_department(
    department_id: int,
    service: ConcreteDepartmentService = Depends(get_department_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.get_department(department_id)


@router.post("", response_model=schemas.Department, status_code=status.HTTP_201_CREATED)
async def create_department(
    payload: schemas.DepartmentCreate,
    service: ConcreteDepartmentService = Depends(get_department_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.create_department(payload)


@router.put("/{department_id}", response_model=schemas.Department)
async def update_department(
    department_id: int,
    payload: schemas.DepartmentUpdate,
    service: ConcreteDepartmentService = Depends(get_department_service),
    current_user: Usuario = Depends(get_current_user),
):
    return await service.update_department(department_id, payload)


@router.delete("/{department_id}", response_model=schemas.Department)
async def deactivate_department(
    department_id: int,
    service: ConcreteDepartmentService = Depends(get_department_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Eliminación lógica (soft delete): marca el departamento como inactivo."""
    return await service.deactivate_department(department_id)