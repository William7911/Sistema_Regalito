from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from app.api.deps import get_cliente_service, get_current_user, require_permission
from app.db.models import Usuario
from app.services.cliente_service import ConcreteClienteService
from app.schemas import cliente_schema as schemas

router = APIRouter()


# ---------------------------------------------------------------------------
# Tipos de Cliente (Catálogo)
# ---------------------------------------------------------------------------

@router.get("/municipios", response_model=List[schemas.MunicipioOut])
async def list_municipios(
    id_departamento: Optional[int] = Query(default=None),
    service: ConcreteClienteService = Depends(get_cliente_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista municipios para autocompletado en el formulario de clientes."""
    return await service.list_municipios(id_departamento=id_departamento)


@router.get("/tipos", response_model=List[schemas.TipoClienteOut])
async def list_tipos_cliente(
    only_active: bool = Query(default=True),
    service: ConcreteClienteService = Depends(get_cliente_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene los tipos de cliente disponibles en el sistema."""
    return await service.list_tipos_cliente(only_active=only_active)


@router.post(
    "/tipos",
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
    "/tipos/{id_tipo}",
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


# ---------------------------------------------------------------------------
# Reportes y Exportación
# ---------------------------------------------------------------------------

@router.get("/reporte", dependencies=[Depends(require_permission("CLIENTE_ADMIN"))])
async def export_clientes_report(
    filters: schemas.ClienteFilter = Depends(),
    fmt: str = Query(default="excel", pattern="^(excel|csv)$", alias="format"),
    service: ConcreteClienteService = Depends(get_cliente_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Descarga el listado de clientes en formato Excel (.xlsx) o CSV (.csv)."""
    return await service.export_clientes(filters, fmt)


# ---------------------------------------------------------------------------
# Búsqueda rápida por NIT (Integración POS y FEL)
# ---------------------------------------------------------------------------

@router.get("/nit/{nit}", response_model=schemas.ClienteOut)
async def get_cliente_by_nit(
    nit: str,
    service: ConcreteClienteService = Depends(get_cliente_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Búsqueda rápida por NIT para completar datos del receptor en POS y emisión FEL."""
    return await service.get_by_nit(nit)


# ---------------------------------------------------------------------------
# CRUD Clientes
# ---------------------------------------------------------------------------

@router.get("", response_model=schemas.ClienteList)
async def list_clientes(
    filters: schemas.ClienteFilter = Depends(),
    service: ConcreteClienteService = Depends(get_cliente_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista clientes paginados con filtros por nombre comercial, NIT y estado."""
    items = await service.list_clientes(filters)
    total = await service.count_clientes(filters)
    return schemas.ClienteList(total=total, items=items)


@router.get("/{id_cliente}", response_model=schemas.ClienteOut)
async def get_cliente(
    id_cliente: int,
    service: ConcreteClienteService = Depends(get_cliente_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Obtiene el detalle completo de un cliente por su identificador."""
    return await service.get_cliente(id_cliente)


@router.post(
    "",
    response_model=schemas.ClienteOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("CLIENTE_ADMIN"))],
)
async def create_cliente(
    payload: schemas.ClienteCreate,
    service: ConcreteClienteService = Depends(get_cliente_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un nuevo cliente con sus contactos (requiere permiso CLIENTE_ADMIN)."""
    return await service.create_cliente(payload, actor_id=current_user.id_usuario)


@router.put(
    "/{id_cliente}",
    response_model=schemas.ClienteOut,
    dependencies=[Depends(require_permission("CLIENTE_ADMIN"))],
)
async def update_cliente(
    id_cliente: int,
    payload: schemas.ClienteUpdate,
    service: ConcreteClienteService = Depends(get_cliente_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza datos y contactos de un cliente (requiere permiso CLIENTE_ADMIN)."""
    return await service.update_cliente(id_cliente, payload, actor_id=current_user.id_usuario)


@router.delete(
    "/{id_cliente}",
    response_model=schemas.ClienteOut,
    dependencies=[Depends(require_permission("CLIENTE_ADMIN"))],
)
async def deactivate_cliente(
    id_cliente: int,
    service: ConcreteClienteService = Depends(get_cliente_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Eliminación lógica (soft delete). Marca el cliente como Inactivo (no aplica a CF)."""
    return await service.deactivate_cliente(id_cliente, actor_id=current_user.id_usuario)
