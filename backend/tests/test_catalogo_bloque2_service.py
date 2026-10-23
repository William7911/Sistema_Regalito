import pytest
from decimal import Decimal
from fastapi import HTTPException
from app.db.models import Categoria, Sucursal, AreaBodega, Subcategoria, UnidadMedida, Producto, VarianteProducto, InventarioSucursal
from app.services.catalogo_service import ConcreteCatalogoService
from app.schemas import catalogo_schema as schemas


def get_service(uow):
    return ConcreteCatalogoService(uow)


# ---------------------------------------------------------------------------
# Helper: crea producto + variante + inventario para probar dependencias
# ---------------------------------------------------------------------------

async def _seed_producto_con_inventario(uow, *, id_sucursal, id_area):
    cat = Categoria(nombre="Categoria Dependencia", estado="Activo")
    uow.db.add(cat)
    await uow.db.flush()
    sub = Subcategoria(id_categoria=cat.id_categoria, nombre="Subcategoria Dependencia", estado="Activo")
    uow.db.add(sub)
    await uow.db.flush()
    uni = UnidadMedida(codigo="DEP", descripcion="Unidad Dependencia", estado="Activo")
    uow.db.add(uni)
    await uow.db.flush()
    prod = Producto(
        id_subcategoria=sub.id_subcategoria,
        id_unidad=uni.id_unidad,
        nombre="Producto Dependencia",
        estado="Activo",
    )
    uow.db.add(prod)
    await uow.db.flush()
    var = VarianteProducto(
        id_producto=prod.id_producto,
        precio_detalle=Decimal("10.00"),
        precio_mayoreo=Decimal("8.00"),
        costo_promedio=Decimal("5.00"),
    )
    uow.db.add(var)
    await uow.db.flush()
    inv = InventarioSucursal(
        id_variante=var.id_variante,
        id_sucursal=id_sucursal,
        id_area=id_area,
        stock_actual=5,
        stock_minimo=1,
    )
    uow.db.add(inv)
    await uow.db.commit()
    return {"sub": sub, "uni": uni, "prod": prod, "var": var, "inv": inv}


# ---------------------------------------------------------------------------
# SUCURSAL
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crear_sucursal_exitosa(uow):
    svc = get_service(uow)
    payload = schemas.SucursalCreate(
        nombre="Sucursal Norte",
        direccion="Km 15 Carretera al Atlántico",
        telefono="2233-4455",
    )
    res = await svc.create_sucursal(payload, actor_id=1)
    assert res.id_sucursal is not None
    assert res.nombre == "Sucursal Norte"
    assert res.estado == "Activo"
    assert res.direccion == "Km 15 Carretera al Atlántico"


@pytest.mark.asyncio
async def test_crear_sucursal_nombre_duplicado_rechazado(uow):
    svc = get_service(uow)
    payload = schemas.SucursalCreate(
        nombre="Sucursal Duplicada",
        direccion="Calle 1",
    )
    await svc.create_sucursal(payload, actor_id=1)

    with pytest.raises(HTTPException) as exc_info:
        await svc.create_sucursal(payload, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "Ya existe una sucursal" in exc_info.value.detail


@pytest.mark.asyncio
async def test_desactivar_y_reactivar_sucursal_soft_delete(uow):
    svc = get_service(uow)
    payload = schemas.SucursalCreate(
        nombre="Sucursal Temporal",
        direccion="Calle 2",
    )
    created = await svc.create_sucursal(payload, actor_id=1)
    assert created.estado == "Activo"

    # Soft delete
    deactivated = await svc.deactivate_sucursal(created.id_sucursal, actor_id=1)
    assert deactivated.estado == "Inactivo"

    # Reactivar
    reactivated = await svc.activate_sucursal(created.id_sucursal, actor_id=1)
    assert reactivated.estado == "Activo"


@pytest.mark.asyncio
async def test_buscar_sucursales_con_filtros_y_paginacion(uow):
    svc = get_service(uow)
    for i in range(3):
        await svc.create_sucursal(
            schemas.SucursalCreate(nombre=f"Filtrable {i}", direccion=f"Dir {i}"),
            actor_id=1,
        )

    filt = schemas.SucursalFilter(search="Filtrable", limit=2, offset=0)
    items = await svc.search_sucursales(filt)
    total = await svc.count_sucursales(filt)
    assert total >= 3
    assert len(items) == 2


# ---------------------------------------------------------------------------
# AREA BODEGA
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crear_area_bodega_exitosa(uow):
    svc = get_service(uow)
    suc = await svc.create_sucursal(
        schemas.SucursalCreate(nombre="Sucursal Area Test", direccion="Zona 10"),
        actor_id=1,
    )

    payload = schemas.AreaBodegaCreate(
        id_sucursal=suc.id_sucursal,
        nombre_area="Bodega Principal A",
    )
    area = await svc.create_area_bodega(payload, actor_id=1)
    assert area.id_area is not None
    assert area.nombre_area == "Bodega Principal A"
    assert area.id_sucursal == suc.id_sucursal
    assert area.estado == "Activo"


@pytest.mark.asyncio
async def test_crear_area_bodega_sucursal_inexistente_rechazada(uow):
    svc = get_service(uow)
    payload = schemas.AreaBodegaCreate(
        id_sucursal=999999,
        nombre_area="Area Fantasma",
    )
    with pytest.raises(HTTPException) as exc_info:
        await svc.create_area_bodega(payload, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "sucursal" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_crear_area_bodega_duplicada_misma_sucursal_rechazada(uow):
    svc = get_service(uow)
    suc = await svc.create_sucursal(
        schemas.SucursalCreate(nombre="Sucursal Area Dup", direccion="Zona 1"),
        actor_id=1,
    )
    payload = schemas.AreaBodegaCreate(
        id_sucursal=suc.id_sucursal,
        nombre_area="Bodega Central",
    )
    await svc.create_area_bodega(payload, actor_id=1)

    with pytest.raises(HTTPException) as exc_info:
        await svc.create_area_bodega(payload, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "Ya existe un área" in exc_info.value.detail


@pytest.mark.asyncio
async def test_desactivar_area_bodega_soft_delete(uow):
    svc = get_service(uow)
    suc = await svc.create_sucursal(
        schemas.SucursalCreate(nombre="Sucursal Soft Area", direccion="Zona 5"),
        actor_id=1,
    )
    area = await svc.create_area_bodega(
        schemas.AreaBodegaCreate(id_sucursal=suc.id_sucursal, nombre_area="Area Delete"),
        actor_id=1,
    )
    assert area.estado == "Activo"

    deactivated = await svc.deactivate_area_bodega(area.id_area, actor_id=1)
    assert deactivated.estado == "Inactivo"


# ---------------------------------------------------------------------------
# SUBCATEGORIA
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crear_subcategoria_exitosa(uow):
    cat = Categoria(nombre="Tecnología Test", estado="Activo")
    uow.db.add(cat)
    await uow.db.flush()
    await uow.commit()

    svc = get_service(uow)
    payload = schemas.SubcategoriaCreate(
        id_categoria=cat.id_categoria,
        nombre="Smartphones",
    )
    sub = await svc.create_subcategoria(payload, actor_id=1)
    assert sub.id_subcategoria is not None
    assert sub.nombre == "Smartphones"
    assert sub.id_categoria == cat.id_categoria
    assert sub.estado == "Activo"


@pytest.mark.asyncio
async def test_crear_subcategoria_categoria_inexistente_rechazada(uow):
    svc = get_service(uow)
    payload = schemas.SubcategoriaCreate(
        id_categoria=888888,
        nombre="Sub Invalida",
    )
    with pytest.raises(HTTPException) as exc_info:
        await svc.create_subcategoria(payload, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "categoría" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_crear_subcategoria_duplicada_misma_categoria_rechazada(uow):
    cat = Categoria(nombre="Juguetes Test", estado="Activo")
    uow.db.add(cat)
    await uow.db.flush()
    await uow.commit()

    svc = get_service(uow)
    payload = schemas.SubcategoriaCreate(
        id_categoria=cat.id_categoria,
        nombre="Muñecas",
    )
    await svc.create_subcategoria(payload, actor_id=1)

    with pytest.raises(HTTPException) as exc_info:
        await svc.create_subcategoria(payload, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "Ya existe una subcategoría" in exc_info.value.detail


@pytest.mark.asyncio
async def test_desactivar_subcategoria_soft_delete(uow):
    cat = Categoria(nombre="Hogar Test", estado="Activo")
    uow.db.add(cat)
    await uow.db.flush()
    await uow.commit()

    svc = get_service(uow)
    sub = await svc.create_subcategoria(
        schemas.SubcategoriaCreate(id_categoria=cat.id_categoria, nombre="Decoración"),
        actor_id=1,
    )
    deactivated = await svc.deactivate_subcategoria(sub.id_subcategoria, actor_id=1)
    assert deactivated.estado == "Inactivo"


# ---------------------------------------------------------------------------
# UNIDAD DE MEDIDA
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crear_unidad_medida_exitosa(uow):
    svc = get_service(uow)
    payload = schemas.UnidadMedidaCreate(
        codigo="DOC",
        descripcion="Docena",
    )
    uni = await svc.create_unidad_medida(payload, actor_id=1)
    assert uni.id_unidad is not None
    assert uni.codigo == "DOC"
    assert uni.descripcion == "Docena"
    assert uni.estado == "Activo"


@pytest.mark.asyncio
async def test_crear_unidad_medida_codigo_duplicado_rechazado(uow):
    svc = get_service(uow)
    payload = schemas.UnidadMedidaCreate(
        codigo="CJ",
        descripcion="Caja",
    )
    await svc.create_unidad_medida(payload, actor_id=1)

    with pytest.raises(HTTPException) as exc_info:
        await svc.create_unidad_medida(payload, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "código" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_desactivar_unidad_medida_soft_delete(uow):
    svc = get_service(uow)
    uni = await svc.create_unidad_medida(
        schemas.UnidadMedidaCreate(codigo="PAR", descripcion="Par"),
        actor_id=1,
    )
    deactivated = await svc.deactivate_unidad_medida(uni.id_unidad, actor_id=1)
    assert deactivated.estado == "Inactivo"


# ---------------------------------------------------------------------------
# DESACTIVACIÓN SEGURA (no desactivar si hay registros activos dependientes)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_desactivar_sucursal_con_inventario_activo_rechazado(uow):
    svc = get_service(uow)
    suc = await svc.create_sucursal(
        schemas.SucursalCreate(nombre="Sucursal Con Stock", direccion="Zona 3"),
        actor_id=1,
    )
    await _seed_producto_con_inventario(uow, id_sucursal=suc.id_sucursal, id_area=None)

    with pytest.raises(HTTPException) as exc_info:
        await svc.deactivate_sucursal(suc.id_sucursal, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "inventario activo" in exc_info.value.detail
    assert "1" in exc_info.value.detail

    # El estado NO cambió
    still = await svc.get_sucursal(suc.id_sucursal)
    assert still.estado == "Activo"


@pytest.mark.asyncio
async def test_update_sucursal_no_puede_desactivar_con_inventario_activo(uow):
    svc = get_service(uow)
    suc = await svc.create_sucursal(
        schemas.SucursalCreate(nombre="Sucursal Update Insegura", direccion="Zona 4"),
        actor_id=1,
    )
    await _seed_producto_con_inventario(uow, id_sucursal=suc.id_sucursal, id_area=None)

    with pytest.raises(HTTPException) as exc_info:
        await svc.update_sucursal(
            suc.id_sucursal,
            schemas.SucursalUpdate(estado="Inactivo"),
            actor_id=1,
        )
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_desactivar_sucursal_con_areas_bodega_activas_rechazado(uow):
    svc = get_service(uow)
    suc = await svc.create_sucursal(
        schemas.SucursalCreate(nombre="Sucursal Con Areas", direccion="Zona 9"),
        actor_id=1,
    )
    await svc.create_area_bodega(
        schemas.AreaBodegaCreate(id_sucursal=suc.id_sucursal, nombre_area="Area Activa 1"),
        actor_id=1,
    )
    await svc.create_area_bodega(
        schemas.AreaBodegaCreate(id_sucursal=suc.id_sucursal, nombre_area="Area Activa 2"),
        actor_id=1,
    )

    with pytest.raises(HTTPException) as exc_info:
        await svc.deactivate_sucursal(suc.id_sucursal, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "área(s) de bodega activa(s)" in exc_info.value.detail
    assert "2" in exc_info.value.detail

    still = await svc.get_sucursal(suc.id_sucursal)
    assert still.estado == "Activo"


@pytest.mark.asyncio
async def test_update_sucursal_no_puede_desactivar_con_areas_activas(uow):
    svc = get_service(uow)
    suc = await svc.create_sucursal(
        schemas.SucursalCreate(nombre="Sucursal Update Areas", direccion="Zona 10"),
        actor_id=1,
    )
    area = await svc.create_area_bodega(
        schemas.AreaBodegaCreate(id_sucursal=suc.id_sucursal, nombre_area="Area Update"),
        actor_id=1,
    )

    with pytest.raises(HTTPException) as exc_info:
        await svc.update_sucursal(
            suc.id_sucursal,
            schemas.SucursalUpdate(estado="Inactivo"),
            actor_id=1,
        )
    assert exc_info.value.status_code == 400
    assert "área(s) de bodega activa(s)" in exc_info.value.detail

    still = await svc.get_sucursal(suc.id_sucursal)
    assert still.estado == "Activo"
    assert (await svc.get_area_bodega(area.id_area)).estado == "Activo"


@pytest.mark.asyncio
async def test_desactivar_sucursal_ok_cuando_areas_estan_inactivas(uow):
    svc = get_service(uow)
    suc = await svc.create_sucursal(
        schemas.SucursalCreate(nombre="Sucursal Areas Inactivas", direccion="Zona 11"),
        actor_id=1,
    )
    area = await svc.create_area_bodega(
        schemas.AreaBodegaCreate(id_sucursal=suc.id_sucursal, nombre_area="Area A Inactivar"),
        actor_id=1,
    )
    await svc.deactivate_area_bodega(area.id_area, actor_id=1)

    deactivated = await svc.deactivate_sucursal(suc.id_sucursal, actor_id=1)
    assert deactivated.estado == "Inactivo"


@pytest.mark.asyncio
async def test_desactivar_area_bodega_con_inventario_activo_rechazado(uow):
    svc = get_service(uow)
    suc = await svc.create_sucursal(
        schemas.SucursalCreate(nombre="Sucursal Area Segura", direccion="Zona 6"),
        actor_id=1,
    )
    area = await svc.create_area_bodega(
        schemas.AreaBodegaCreate(id_sucursal=suc.id_sucursal, nombre_area="Area Con Stock"),
        actor_id=1,
    )
    await _seed_producto_con_inventario(uow, id_sucursal=suc.id_sucursal, id_area=area.id_area)

    with pytest.raises(HTTPException) as exc_info:
        await svc.deactivate_area_bodega(area.id_area, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "inventario activo" in exc_info.value.detail

    still = await svc.get_area_bodega(area.id_area)
    assert still.estado == "Activo"


@pytest.mark.asyncio
async def test_desactivar_subcategoria_con_productos_activos_rechazado(uow):
    svc = get_service(uow)
    suc = await svc.create_sucursal(
        schemas.SucursalCreate(nombre="Sucursal Para Sub", direccion="Zona 7"),
        actor_id=1,
    )
    seeded = await _seed_producto_con_inventario(uow, id_sucursal=suc.id_sucursal, id_area=None)

    with pytest.raises(HTTPException) as exc_info:
        await svc.deactivate_subcategoria(seeded["sub"].id_subcategoria, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "producto" in exc_info.value.detail
    assert "1" in exc_info.value.detail

    still = await svc.get_subcategoria(seeded["sub"].id_subcategoria)
    assert still.estado == "Activo"


@pytest.mark.asyncio
async def test_desactivar_unidad_medida_con_productos_activos_rechazado(uow):
    svc = get_service(uow)
    suc = await svc.create_sucursal(
        schemas.SucursalCreate(nombre="Sucursal Para Uni", direccion="Zona 8"),
        actor_id=1,
    )
    seeded = await _seed_producto_con_inventario(uow, id_sucursal=suc.id_sucursal, id_area=None)

    with pytest.raises(HTTPException) as exc_info:
        await svc.deactivate_unidad_medida(seeded["uni"].id_unidad, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "producto" in exc_info.value.detail

    still = await svc.get_unidad_medida(seeded["uni"].id_unidad)
    assert still.estado == "Activo"
