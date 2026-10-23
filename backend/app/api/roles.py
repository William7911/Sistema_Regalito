from fastapi import APIRouter, Depends, status
from typing import List
from app.api.deps import get_role_service, require_admin
from app.db.models import Usuario
from app.services.role_service import ConcreteRoleService
from app.schemas import schemas, catalogo_schema

router = APIRouter(dependencies=[Depends(require_admin)])


@router.get("", response_model=List[schemas.Role])
async def list_roles(
    include_inactive: bool = False,
    service: ConcreteRoleService = Depends(get_role_service),
    current_user: Usuario = Depends(require_admin),
):
    return await service.list_roles(include_inactive=include_inactive)


@router.get("/{role_id}", response_model=schemas.Role)
async def get_role(
    role_id: int,
    service: ConcreteRoleService = Depends(get_role_service),
    current_user: Usuario = Depends(require_admin),
):
    return await service.get_role(role_id)


@router.post("", response_model=schemas.Role, status_code=status.HTTP_201_CREATED)
async def create_role(
    payload: schemas.RoleCreate,
    service: ConcreteRoleService = Depends(get_role_service),
    current_user: Usuario = Depends(require_admin),
):
    return await service.create_role(payload, actor_id=current_user.id_usuario)


@router.put("/{role_id}", response_model=schemas.Role)
async def update_role(
    role_id: int,
    payload: schemas.RoleUpdate,
    service: ConcreteRoleService = Depends(get_role_service),
    current_user: Usuario = Depends(require_admin),
):
    return await service.update_role(role_id, payload, actor_id=current_user.id_usuario)


@router.delete("/{role_id}", response_model=schemas.Role)
async def deactivate_role(
    role_id: int,
    service: ConcreteRoleService = Depends(get_role_service),
    current_user: Usuario = Depends(require_admin),
):
    """Eliminación lógica (soft delete): marca el rol como inactivo."""
    return await service.deactivate_role(role_id, actor_id=current_user.id_usuario)


# ---------------------------------------------------------------------------
# Permisos y rol-permiso (pantalla dentro de Roles)
# ---------------------------------------------------------------------------

@router.get("/permisos/catalogo", response_model=List[catalogo_schema.PermisoOut])
async def list_permisos(
    service: ConcreteRoleService = Depends(get_role_service),
    current_user: Usuario = Depends(require_admin),
):
    """Lista todos los permisos disponibles, agrupables en el frontend por 'modulo'."""
    return await service.list_permisos()


@router.get("/{role_id}/permisos", response_model=List[str])
async def get_rol_permisos(
    role_id: int,
    service: ConcreteRoleService = Depends(get_role_service),
    current_user: Usuario = Depends(require_admin),
):
    """Lista los códigos de permisos asignados a un rol."""
    return await service.get_rol_permisos(role_id)


@router.put("/{role_id}/permisos", response_model=List[str])
async def update_rol_permisos(
    role_id: int,
    payload: catalogo_schema.RolePermisosUpdate,
    service: ConcreteRoleService = Depends(get_role_service),
    current_user: Usuario = Depends(require_admin),
):
    """Reemplaza el conjunto de permisos asignados a un rol."""
    return await service.update_rol_permisos(
        role_id, payload.codigos, actor_id=current_user.id_usuario
    )
