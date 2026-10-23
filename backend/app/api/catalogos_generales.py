from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from app.api.deps import get_catalogo_general_service, get_current_user, require_permission
from app.db.models import Usuario
from app.services.catalogo_general_service import ConcreteCatalogoGeneralService
from app.schemas import catalogo_schema as schemas

router = APIRouter()


# ===========================================================================
# 1. MOTIVOS DE MERMA
# ===========================================================================

@router.get("/motivos-merma", response_model=List[schemas.MotivoMermaOut])
async def list_motivos_merma(
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado ligero de motivos de merma activos para combos."""
    return await service.list_motivos_merma()


@router.get("/motivos-merma/paged", response_model=schemas.MotivoMermaList)
async def search_motivos_merma(
    filters: schemas.MotivoMermaFilter = Depends(),
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado paginado con filtros para la administración de motivos de merma."""
    items = await service.search_motivos_merma(filters)
    total = await service.count_motivos_merma(filters)
    return schemas.MotivoMermaList(total=total, items=items)


@router.get("/motivos-merma/export", dependencies=[Depends(require_permission("CATALOGO_ADMIN"))])
async def export_motivos_merma(
    filters: schemas.MotivoMermaFilter = Depends(),
    fmt: str = Query(default="excel", pattern="^(excel|csv)$", alias="format"),
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Exporta los motivos de merma a Excel o CSV respetando filtros."""
    return await service.export_motivos_merma(filters, fmt)


@router.get("/motivos-merma/{id_motivo}", response_model=schemas.MotivoMermaOut)
async def get_motivo_merma(
    id_motivo: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Ficha de detalle de un motivo de merma."""
    return await service.get_motivo_merma(id_motivo)


@router.post(
    "/motivos-merma",
    response_model=schemas.MotivoMermaOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def create_motivo_merma(
    payload: schemas.MotivoMermaCreate,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un motivo de merma (requiere CATALOGO_ADMIN)."""
    return await service.create_motivo_merma(payload, actor_id=current_user.id_usuario)


@router.put(
    "/motivos-merma/{id_motivo}",
    response_model=schemas.MotivoMermaOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def update_motivo_merma(
    id_motivo: int,
    payload: schemas.MotivoMermaUpdate,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza un motivo de merma (requiere CATALOGO_ADMIN)."""
    return await service.update_motivo_merma(id_motivo, payload, actor_id=current_user.id_usuario)


@router.delete(
    "/motivos-merma/{id_motivo}",
    response_model=schemas.MotivoMermaOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def deactivate_motivo_merma(
    id_motivo: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Desactivación lógica de un motivo de merma (requiere CATALOGO_ADMIN)."""
    return await service.deactivate_motivo_merma(id_motivo, actor_id=current_user.id_usuario)


@router.post(
    "/motivos-merma/{id_motivo}/activar",
    response_model=schemas.MotivoMermaOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def activate_motivo_merma(
    id_motivo: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Reactivación de un motivo de merma (requiere CATALOGO_ADMIN)."""
    return await service.activate_motivo_merma(id_motivo, actor_id=current_user.id_usuario)


# ===========================================================================
# 2. MÉTODOS DE PAGO
# ===========================================================================

@router.get("/metodos-pago", response_model=List[schemas.MetodoPagoOut])
async def list_metodos_pago(
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado ligero de métodos de pago activos para combos (POS, cobros)."""
    return await service.list_metodos_pago()


@router.get("/metodos-pago/paged", response_model=schemas.MetodoPagoList)
async def search_metodos_pago(
    filters: schemas.MetodoPagoFilter = Depends(),
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado paginado con filtros para la administración de métodos de pago."""
    items = await service.search_metodos_pago(filters)
    total = await service.count_metodos_pago(filters)
    return schemas.MetodoPagoList(total=total, items=items)


@router.get("/metodos-pago/export", dependencies=[Depends(require_permission("CATALOGO_ADMIN"))])
async def export_metodos_pago(
    filters: schemas.MetodoPagoFilter = Depends(),
    fmt: str = Query(default="excel", pattern="^(excel|csv)$", alias="format"),
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Exporta los métodos de pago a Excel o CSV respetando filtros."""
    return await service.export_metodos_pago(filters, fmt)


@router.get("/metodos-pago/{id_metodo_pago}", response_model=schemas.MetodoPagoOut)
async def get_metodo_pago(
    id_metodo_pago: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Ficha de detalle de un método de pago."""
    return await service.get_metodo_pago(id_metodo_pago)


@router.post(
    "/metodos-pago",
    response_model=schemas.MetodoPagoOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def create_metodo_pago(
    payload: schemas.MetodoPagoCreate,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un método de pago (requiere CATALOGO_ADMIN)."""
    return await service.create_metodo_pago(payload, actor_id=current_user.id_usuario)


@router.put(
    "/metodos-pago/{id_metodo_pago}",
    response_model=schemas.MetodoPagoOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def update_metodo_pago(
    id_metodo_pago: int,
    payload: schemas.MetodoPagoUpdate,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza un método de pago (requiere CATALOGO_ADMIN)."""
    return await service.update_metodo_pago(id_metodo_pago, payload, actor_id=current_user.id_usuario)


@router.delete(
    "/metodos-pago/{id_metodo_pago}",
    response_model=schemas.MetodoPagoOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def deactivate_metodo_pago(
    id_metodo_pago: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Desactivación lógica de un método de pago (requiere CATALOGO_ADMIN)."""
    return await service.deactivate_metodo_pago(id_metodo_pago, actor_id=current_user.id_usuario)


@router.post(
    "/metodos-pago/{id_metodo_pago}/activar",
    response_model=schemas.MetodoPagoOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def activate_metodo_pago(
    id_metodo_pago: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Reactivación de un método de pago (requiere CATALOGO_ADMIN)."""
    return await service.activate_metodo_pago(id_metodo_pago, actor_id=current_user.id_usuario)


# ===========================================================================
# 3. PROVEEDORES
# ===========================================================================

@router.get("/proveedores", response_model=List[schemas.ProveedorOut])
async def list_proveedores(
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado ligero de proveedores activos para combos (compras)."""
    return await service.list_proveedores()


@router.get("/proveedores/paged", response_model=schemas.ProveedorList)
async def search_proveedores(
    filters: schemas.ProveedorFilter = Depends(),
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado paginado con filtros para la administración de proveedores."""
    items = await service.search_proveedores(filters)
    total = await service.count_proveedores(filters)
    return schemas.ProveedorList(total=total, items=items)


@router.get("/proveedores/export", dependencies=[Depends(require_permission("CATALOGO_ADMIN"))])
async def export_proveedores(
    filters: schemas.ProveedorFilter = Depends(),
    fmt: str = Query(default="excel", pattern="^(excel|csv)$", alias="format"),
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Exporta los proveedores a Excel o CSV respetando filtros."""
    return await service.export_proveedores(filters, fmt)


@router.get("/proveedores/{id_proveedor}", response_model=schemas.ProveedorOut)
async def get_proveedor(
    id_proveedor: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Ficha de detalle de un proveedor."""
    return await service.get_proveedor(id_proveedor)


@router.post(
    "/proveedores",
    response_model=schemas.ProveedorOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def create_proveedor(
    payload: schemas.ProveedorCreate,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un proveedor (requiere CATALOGO_ADMIN)."""
    return await service.create_proveedor(payload, actor_id=current_user.id_usuario)


@router.put(
    "/proveedores/{id_proveedor}",
    response_model=schemas.ProveedorOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def update_proveedor(
    id_proveedor: int,
    payload: schemas.ProveedorUpdate,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza un proveedor (requiere CATALOGO_ADMIN)."""
    return await service.update_proveedor(id_proveedor, payload, actor_id=current_user.id_usuario)


@router.delete(
    "/proveedores/{id_proveedor}",
    response_model=schemas.ProveedorOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def deactivate_proveedor(
    id_proveedor: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Desactivación lógica de un proveedor (requiere CATALOGO_ADMIN)."""
    return await service.deactivate_proveedor(id_proveedor, actor_id=current_user.id_usuario)


@router.post(
    "/proveedores/{id_proveedor}/activar",
    response_model=schemas.ProveedorOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def activate_proveedor(
    id_proveedor: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Reactivación de un proveedor (requiere CATALOGO_ADMIN)."""
    return await service.activate_proveedor(id_proveedor, actor_id=current_user.id_usuario)


# ===========================================================================
# 4. DEPARTAMENTOS GEOGRÁFICOS
# ===========================================================================

@router.get("/departamentos", response_model=List[schemas.DepartamentoOut])
async def list_departamentos(
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado ligero de departamentos activos para combos dependientes."""
    return await service.list_departamentos()


@router.get("/departamentos/paged", response_model=schemas.DepartamentoList)
async def search_departamentos(
    filters: schemas.DepartamentoFilter = Depends(),
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado paginado con filtros para la administración de departamentos."""
    items = await service.search_departamentos(filters)
    total = await service.count_departamentos(filters)
    return schemas.DepartamentoList(total=total, items=items)


@router.get("/departamentos/export", dependencies=[Depends(require_permission("CATALOGO_ADMIN"))])
async def export_departamentos(
    filters: schemas.DepartamentoFilter = Depends(),
    fmt: str = Query(default="excel", pattern="^(excel|csv)$", alias="format"),
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Exporta los departamentos a Excel o CSV respetando filtros."""
    return await service.export_departamentos(filters, fmt)


@router.get("/departamentos/{id_departamento}", response_model=schemas.DepartamentoOut)
async def get_departamento(
    id_departamento: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Ficha de detalle de un departamento."""
    return await service.get_departamento(id_departamento)


@router.post(
    "/departamentos",
    response_model=schemas.DepartamentoOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def create_departamento(
    payload: schemas.DepartamentoCreate,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un departamento (requiere CATALOGO_ADMIN)."""
    return await service.create_departamento(payload, actor_id=current_user.id_usuario)


@router.put(
    "/departamentos/{id_departamento}",
    response_model=schemas.DepartamentoOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def update_departamento(
    id_departamento: int,
    payload: schemas.DepartamentoUpdate,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza un departamento (requiere CATALOGO_ADMIN)."""
    return await service.update_departamento(id_departamento, payload, actor_id=current_user.id_usuario)


@router.delete(
    "/departamentos/{id_departamento}",
    response_model=schemas.DepartamentoOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def deactivate_departamento(
    id_departamento: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Desactivación lógica de un departamento (requiere CATALOGO_ADMIN)."""
    return await service.deactivate_departamento(id_departamento, actor_id=current_user.id_usuario)


@router.post(
    "/departamentos/{id_departamento}/activar",
    response_model=schemas.DepartamentoOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def activate_departamento(
    id_departamento: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Reactivación de un departamento (requiere CATALOGO_ADMIN)."""
    return await service.activate_departamento(id_departamento, actor_id=current_user.id_usuario)


# ===========================================================================
# 5. MUNICIPIOS (dropdown dependiente)
# ===========================================================================

@router.get("/municipios", response_model=List[schemas.MunicipioOut])
async def list_municipios(
    id_departamento: Optional[int] = None,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado ligero de municipios activos (todos o por departamento) para combos."""
    return await service.list_municipios(id_departamento=id_departamento)


@router.get("/municipios/paged", response_model=schemas.MunicipioList)
async def search_municipios(
    filters: schemas.MunicipioFilter = Depends(),
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado paginado con filtros para la administración de municipios."""
    items = await service.search_municipios(filters)
    total = await service.count_municipios(filters)
    return schemas.MunicipioList(total=total, items=items)


@router.get("/municipios/export", dependencies=[Depends(require_permission("CATALOGO_ADMIN"))])
async def export_municipios(
    filters: schemas.MunicipioFilter = Depends(),
    fmt: str = Query(default="excel", pattern="^(excel|csv)$", alias="format"),
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Exporta los municipios a Excel o CSV respetando filtros."""
    return await service.export_municipios(filters, fmt)


@router.get("/municipios/{id_municipio}", response_model=schemas.MunicipioOut)
async def get_municipio(
    id_municipio: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Ficha de detalle de un municipio."""
    return await service.get_municipio(id_municipio)


@router.post(
    "/municipios",
    response_model=schemas.MunicipioOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def create_municipio(
    payload: schemas.MunicipioCreate,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea un municipio dentro de un departamento (requiere CATALOGO_ADMIN)."""
    return await service.create_municipio(payload, actor_id=current_user.id_usuario)


@router.put(
    "/municipios/{id_municipio}",
    response_model=schemas.MunicipioOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def update_municipio(
    id_municipio: int,
    payload: schemas.MunicipioUpdate,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza un municipio (requiere CATALOGO_ADMIN)."""
    return await service.update_municipio(id_municipio, payload, actor_id=current_user.id_usuario)


@router.delete(
    "/municipios/{id_municipio}",
    response_model=schemas.MunicipioOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def deactivate_municipio(
    id_municipio: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Desactivación lógica de un municipio (requiere CATALOGO_ADMIN)."""
    return await service.deactivate_municipio(id_municipio, actor_id=current_user.id_usuario)


@router.post(
    "/municipios/{id_municipio}/activar",
    response_model=schemas.MunicipioOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def activate_municipio(
    id_municipio: int,
    service: ConcreteCatalogoGeneralService = Depends(get_catalogo_general_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Reactivación de un municipio (requiere CATALOGO_ADMIN)."""
    return await service.activate_municipio(id_municipio, actor_id=current_user.id_usuario)