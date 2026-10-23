from fastapi import APIRouter, Depends, Query, status
from typing import List
from app.api.deps import get_cliente_service, get_current_user, require_permission
from app.db.models import Usuario
from app.services.cliente_service import ConcreteClienteService
from app.schemas import cliente_schema as schemas

router = APIRouter()


@router.get("", response_model=List[schemas.TipoClienteOut])
async def list_tipos_cliente(
    only_active: bool = Query(default=False),
    service: ConcreteClienteService = Depends(get_cliente_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista todos los tipos de cliente (admite filtro only_active)."""
    return await service.list_tipos_cliente(only_active=only_active)


@router.get("/{id_tipo}", response_model=schemas.TipoClienteOut)
async def get_tipo_cliente(
    id_tipo: int,
    service: ConcreteClienteService = Depends(get_cliente_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene un tipo de cliente por ID."""
    return await service.get_tipo_cliente(id_tipo)


@router.post(
    "",
    response_model=schemas.TipoClienteOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("CLIENTE_ADMIN"))],
)
async def create_tipo_cliente(
    payload: schemas.TipoClienteCreate,
    service: ConcreteClienteService = Depends(get_cliente_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un nuevo tipo de cliente (requiere permiso CLIENTE_ADMIN)."""
    return await service.create_tipo_cliente(payload)


@router.put(
    "/{id_tipo}",
    response_model=schemas.TipoClienteOut,
    dependencies=[Depends(require_permission("CLIENTE_ADMIN"))],
)
async def update_tipo_cliente(
    id_tipo: int,
    payload: schemas.TipoClienteUpdate,
    service: ConcreteClienteService = Depends(get_cliente_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza un tipo de cliente existente (requiere permiso CLIENTE_ADMIN)."""
    return await service.update_tipo_cliente(id_tipo, payload)


@router.delete(
    "/{id_tipo}",
    response_model=schemas.TipoClienteOut,
    dependencies=[Depends(require_permission("CLIENTE_ADMIN"))],
)
async def deactivate_tipo_cliente(
    id_tipo: int,
    service: ConcreteClienteService = Depends(get_cliente_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Desactiva lógicamente (soft delete) un tipo de cliente (requiere permiso CLIENTE_ADMIN)."""
    return await service.deactivate_tipo_cliente(id_tipo, actor_id=current_user.id_usuario)

