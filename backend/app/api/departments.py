from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from app.api.deps import get_department_service, require_admin, get_current_user
from app.db.models import Usuario
from app.services.department_service import ConcreteDepartmentService
from app.schemas import schemas, cliente_schema

router = APIRouter()


@router.get("", response_model=List[schemas.Department])
async def list_departments(
    include_inactive: bool = False,
    service: ConcreteDepartmentService = Depends(get_department_service),
    current_user: Usuario = Depends(require_admin),
):
    return await service.list_departments(include_inactive=include_inactive)


@router.get("/municipios", response_model=List[cliente_schema.MunicipioOut])
async def list_all_municipios(
    id_departamento: Optional[int] = Query(default=None),
    service: ConcreteDepartmentService = Depends(get_department_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista todos los municipios o filtrados por departamento."""
    return await service.list_municipios(department_id=id_departamento)


@router.get("/{department_id}", response_model=schemas.Department)
async def get_department(
    department_id: int,
    service: ConcreteDepartmentService = Depends(get_department_service),
    current_user: Usuario = Depends(require_admin),
):
    return await service.get_department(department_id)


@router.get("/{department_id}/municipios", response_model=List[cliente_schema.MunicipioOut])
async def list_department_municipios(
    department_id: int,
    service: ConcreteDepartmentService = Depends(get_department_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene los municipios correspondientes a un departamento específico."""
    return await service.list_municipios(department_id=department_id)


@router.post(
    "",
    response_model=schemas.Department,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
async def create_department(
    payload: schemas.DepartmentCreate,
    service: ConcreteDepartmentService = Depends(get_department_service),
    current_user: Usuario = Depends(require_admin),
):
    return await service.create_department(payload)


@router.put(
    "/{department_id}",
    response_model=schemas.Department,
    dependencies=[Depends(require_admin)],
)
async def update_department(
    department_id: int,
    payload: schemas.DepartmentUpdate,
    service: ConcreteDepartmentService = Depends(get_department_service),
    current_user: Usuario = Depends(require_admin),
):
    return await service.update_department(department_id, payload)


@router.delete(
    "/{department_id}",
    response_model=schemas.Department,
    dependencies=[Depends(require_admin)],
)
async def deactivate_department(
    department_id: int,
    service: ConcreteDepartmentService = Depends(get_department_service),
    current_user: Usuario = Depends(require_admin),
):
    """Eliminación lógica (soft delete): marca el departamento como inactivo."""
    return await service.deactivate_department(department_id)
