from fastapi import APIRouter, Depends, Query, status
from typing import List, Optional
from app.api.deps import get_catalogo_service, get_current_user, require_permission
from app.db.models import Usuario
from app.services.catalogo_service import ConcreteCatalogoService
from app.schemas import catalogo_schema as schemas

router = APIRouter()


# ===========================================================================
# 1. SUCURSALES
# ===========================================================================

@router.get("/sucursales", response_model=List[schemas.SucursalOut])
async def list_sucursales(
    include_inactive: bool = False,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado ligero de sucursales para dropdowns y combos."""
    return await service.list_sucursales(include_inactive=include_inactive)


@router.get("/sucursales/paged", response_model=schemas.SucursalList)
async def search_sucursales(
    filters: schemas.SucursalFilter = Depends(),
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado paginado con filtros para la tabla de administración de sucursales."""
    items = await service.search_sucursales(filters)
    total = await service.count_sucursales(filters)
    return schemas.SucursalList(total=total, items=items)


@router.get("/sucursales/export", dependencies=[Depends(require_permission("CATALOGO_ADMIN"))])
async def export_sucursales(
    filters: schemas.SucursalFilter = Depends(),
    fmt: str = Query(default="excel", pattern="^(excel|csv)$", alias="format"),
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Exporta el reporte de sucursales a formato Excel o CSV."""
    return await service.export_sucursales(filters, fmt)


@router.get("/sucursales/{id_sucursal}", response_model=schemas.SucursalOut)
async def get_sucursal(
    id_sucursal: int,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Ficha de detalle de sucursal por ID."""
    return await service.get_sucursal(id_sucursal)


@router.post(
    "/sucursales",
    response_model=schemas.SucursalOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def create_sucursal(
    payload: schemas.SucursalCreate,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una nueva sucursal (requiere CATALOGO_ADMIN)."""
    return await service.create_sucursal(payload, actor_id=current_user.id_usuario)


@router.put(
    "/sucursales/{id_sucursal}",
    response_model=schemas.SucursalOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def update_sucursal(
    id_sucursal: int,
    payload: schemas.SucursalUpdate,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza una sucursal existente (requiere CATALOGO_ADMIN)."""
    return await service.update_sucursal(id_sucursal, payload, actor_id=current_user.id_usuario)


@router.delete(
    "/sucursales/{id_sucursal}",
    response_model=schemas.SucursalOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def deactivate_sucursal(
    id_sucursal: int,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Desactivación lógica (soft delete) de sucursal (requiere CATALOGO_ADMIN)."""
    return await service.deactivate_sucursal(id_sucursal, actor_id=current_user.id_usuario)


@router.post(
    "/sucursales/{id_sucursal}/activar",
    response_model=schemas.SucursalOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def activate_sucursal(
    id_sucursal: int,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Reactiva una sucursal previamente desactivada (requiere CATALOGO_ADMIN)."""
    return await service.activate_sucursal(id_sucursal, actor_id=current_user.id_usuario)


# ===========================================================================
# 2. AREAS DE BODEGA
# ===========================================================================

@router.get("/areas", response_model=List[schemas.AreaBodegaOut])
async def list_areas(
    sucursal_id: Optional[int] = None,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado ligero de áreas para dropdowns de inventario/bodega."""
    return await service.list_areas(sucursal_id=sucursal_id)


@router.get("/areas/paged", response_model=schemas.AreaBodegaList)
async def search_areas(
    filters: schemas.AreaBodegaFilter = Depends(),
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado paginado con filtros para la administración de áreas de bodega."""
    items = await service.search_areas(filters)
    total = await service.count_areas(filters)
    return schemas.AreaBodegaList(total=total, items=items)


@router.get("/areas/export", dependencies=[Depends(require_permission("CATALOGO_ADMIN"))])
async def export_areas(
    filters: schemas.AreaBodegaFilter = Depends(),
    fmt: str = Query(default="excel", pattern="^(excel|csv)$", alias="format"),
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Exporta el reporte de áreas a Excel o CSV."""
    return await service.export_areas(filters, fmt)


@router.get("/areas/{id_area}", response_model=schemas.AreaBodegaOut)
async def get_area(
    id_area: int,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Ficha de detalle de un área de bodega por ID."""
    return await service.get_area_bodega(id_area)


@router.post(
    "/areas",
    response_model=schemas.AreaBodegaOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def create_area(
    payload: schemas.AreaBodegaCreate,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una nueva área de bodega en una sucursal (requiere CATALOGO_ADMIN)."""
    return await service.create_area_bodega(payload, actor_id=current_user.id_usuario)


@router.put(
    "/areas/{id_area}",
    response_model=schemas.AreaBodegaOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def update_area(
    id_area: int,
    payload: schemas.AreaBodegaUpdate,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza los datos de un área de bodega (requiere CATALOGO_ADMIN)."""
    return await service.update_area_bodega(id_area, payload, actor_id=current_user.id_usuario)


@router.delete(
    "/areas/{id_area}",
    response_model=schemas.AreaBodegaOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def deactivate_area(
    id_area: int,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Desactiva lógicamente un área de bodega (soft delete) (requiere CATALOGO_ADMIN)."""
    return await service.deactivate_area_bodega(id_area, actor_id=current_user.id_usuario)


@router.post(
    "/areas/{id_area}/activar",
    response_model=schemas.AreaBodegaOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def activate_area(
    id_area: int,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Reactiva un área previamente desactivada (requiere CATALOGO_ADMIN)."""
    return await service.activate_area_bodega(id_area, actor_id=current_user.id_usuario)


# ===========================================================================
# 3. SUBCATEGORIAS
# ===========================================================================

@router.get("/subcategorias", response_model=List[schemas.SubcategoriaOut])
async def list_subcategorias(
    include_inactive: bool = False,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado ligero de subcategorías para dropdowns de productos."""
    return await service.list_subcategorias(include_inactive=include_inactive)


@router.get("/subcategorias/paged", response_model=schemas.SubcategoriaList)
async def search_subcategorias(
    filters: schemas.SubcategoriaFilter = Depends(),
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado paginado con filtros para administración de subcategorías."""
    items = await service.search_subcategorias(filters)
    total = await service.count_subcategorias(filters)
    return schemas.SubcategoriaList(total=total, items=items)


@router.get("/subcategorias/export", dependencies=[Depends(require_permission("CATALOGO_ADMIN"))])
async def export_subcategorias(
    filters: schemas.SubcategoriaFilter = Depends(),
    fmt: str = Query(default="excel", pattern="^(excel|csv)$", alias="format"),
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Exporta el catálogo de subcategorías a Excel o CSV."""
    return await service.export_subcategorias(filters, fmt)


@router.get("/subcategorias/{id_subcategoria}", response_model=schemas.SubcategoriaOut)
async def get_subcategoria(
    id_subcategoria: int,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Ficha de detalle de una subcategoría por ID."""
    return await service.get_subcategoria(id_subcategoria)


@router.post(
    "/subcategorias",
    response_model=schemas.SubcategoriaOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def create_subcategoria(
    payload: schemas.SubcategoriaCreate,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una nueva subcategoría dentro de una categoría (requiere CATALOGO_ADMIN)."""
    return await service.create_subcategoria(payload, actor_id=current_user.id_usuario)


@router.put(
    "/subcategorias/{id_subcategoria}",
    response_model=schemas.SubcategoriaOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def update_subcategoria(
    id_subcategoria: int,
    payload: schemas.SubcategoriaUpdate,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza una subcategoría existente (requiere CATALOGO_ADMIN)."""
    return await service.update_subcategoria(id_subcategoria, payload, actor_id=current_user.id_usuario)


@router.delete(
    "/subcategorias/{id_subcategoria}",
    response_model=schemas.SubcategoriaOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def deactivate_subcategoria(
    id_subcategoria: int,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Desactiva lógicamente una subcategoría (soft delete) (requiere CATALOGO_ADMIN)."""
    return await service.deactivate_subcategoria(id_subcategoria, actor_id=current_user.id_usuario)


@router.post(
    "/subcategorias/{id_subcategoria}/activar",
    response_model=schemas.SubcategoriaOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def activate_subcategoria(
    id_subcategoria: int,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Reactiva una subcategoría desactivada (requiere CATALOGO_ADMIN)."""
    return await service.activate_subcategoria(id_subcategoria, actor_id=current_user.id_usuario)


# ===========================================================================
# 4. UNIDADES DE MEDIDA
# ===========================================================================

@router.get("/unidades", response_model=List[schemas.UnidadMedidaOut])
async def list_unidades(
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado ligero de unidades de medida para dropdowns de productos."""
    return await service.list_unidades()


@router.get("/unidades/paged", response_model=schemas.UnidadMedidaList)
async def search_unidades(
    filters: schemas.UnidadMedidaFilter = Depends(),
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Listado paginado con filtros para administración de unidades de medida."""
    items = await service.search_unidades(filters)
    total = await service.count_unidades(filters)
    return schemas.UnidadMedidaList(total=total, items=items)


@router.get("/unidades/export", dependencies=[Depends(require_permission("CATALOGO_ADMIN"))])
async def export_unidades(
    filters: schemas.UnidadMedidaFilter = Depends(),
    fmt: str = Query(default="excel", pattern="^(excel|csv)$", alias="format"),
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Exporta el reporte de unidades de medida a Excel o CSV."""
    return await service.export_unidades(filters, fmt)


@router.get("/unidades/{id_unidad}", response_model=schemas.UnidadMedidaOut)
async def get_unidad(
    id_unidad: int,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Ficha de detalle de una unidad de medida por ID."""
    return await service.get_unidad_medida(id_unidad)


@router.post(
    "/unidades",
    response_model=schemas.UnidadMedidaOut,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def create_unidad(
    payload: schemas.UnidadMedidaCreate,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Crea una nueva unidad de medida (requiere CATALOGO_ADMIN)."""
    return await service.create_unidad_medida(payload, actor_id=current_user.id_usuario)


@router.put(
    "/unidades/{id_unidad}",
    response_model=schemas.UnidadMedidaOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def update_unidad(
    id_unidad: int,
    payload: schemas.UnidadMedidaUpdate,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Actualiza una unidad de medida existente (requiere CATALOGO_ADMIN)."""
    return await service.update_unidad_medida(id_unidad, payload, actor_id=current_user.id_usuario)


@router.delete(
    "/unidades/{id_unidad}",
    response_model=schemas.UnidadMedidaOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def deactivate_unidad(
    id_unidad: int,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Desactiva lógicamente una unidad de medida (soft delete) (requiere CATALOGO_ADMIN)."""
    return await service.deactivate_unidad_medida(id_unidad, actor_id=current_user.id_usuario)


@router.post(
    "/unidades/{id_unidad}/activar",
    response_model=schemas.UnidadMedidaOut,
    dependencies=[Depends(require_permission("CATALOGO_ADMIN"))],
)
async def activate_unidad(
    id_unidad: int,
    service: ConcreteCatalogoService = Depends(get_catalogo_service),
    current_user: Usuario = Depends(get_current_user),
):
    """Reactiva una unidad de medida desactivada (requiere CATALOGO_ADMIN)."""
    return await service.activate_unidad_medida(id_unidad, actor_id=current_user.id_usuario)
