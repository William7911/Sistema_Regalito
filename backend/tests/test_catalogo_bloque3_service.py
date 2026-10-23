import pytest
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException
from app.db.models import (
    Categoria, Subcategoria, UnidadMedida, Producto, VarianteProducto,
    Sucursal, Caja, TurnoCaja, Venta, PagoVenta,
    Merma, DetalleMerma, OrdenCompra,
    TipoCliente, Cliente, Municipio,
)
from app.services.catalogo_general_service import ConcreteCatalogoGeneralService
from app.schemas import catalogo_schema as schemas


def get_service(uow):
    return ConcreteCatalogoGeneralService(uow)


# ---------------------------------------------------------------------------
# Helpers de seed para dependencias (desactivación segura)
# ---------------------------------------------------------------------------

async def _seed_producto_variante(uow):
    cat = Categoria(nombre="Categoria Bloque3", estado="Activo")
    uow.db.add(cat)
    await uow.db.flush()
    sub = Subcategoria(id_categoria=cat.id_categoria, nombre="Sub Bloque3", estado="Activo")
    uow.db.add(sub)
    await uow.db.flush()
    uni = UnidadMedida(codigo="B3", descripcion="Unidad B3", estado="Activo")
    uow.db.add(uni)
    await uow.db.flush()
    prod = Producto(id_subcategoria=sub.id_subcategoria, id_unidad=uni.id_unidad,
                    nombre="Producto B3", estado="Activo")
    uow.db.add(prod)
    await uow.db.flush()
    var = VarianteProducto(id_producto=prod.id_producto, precio_detalle=Decimal("10"),
                           precio_mayoreo=Decimal("8"), costo_promedio=Decimal("5"))
    uow.db.add(var)
    await uow.db.flush()
    return var


async def _seed_venta_pagada(uow, id_metodo_pago):
    suc = Sucursal(nombre="Sucursal Venta B3", direccion="Zona 1", estado="Activo")
    uow.db.add(suc)
    await uow.db.flush()
    caja = Caja(id_sucursal=suc.id_sucursal, descripcion="Caja 1", estado="Activa")
    uow.db.add(caja)
    await uow.db.flush()
    turno = TurnoCaja(id_caja=caja.id_caja, id_usuario=1, monto_apertura=Decimal("100"),
                      fecha_apertura=datetime.utcnow(), estado="Abierto")
    uow.db.add(turno)
    await uow.db.flush()
    venta = Venta(id_turno=turno.id_turno, id_usuario=1, fecha_venta=datetime.utcnow(),
                  subtotal=Decimal("50"), descuento_total=Decimal("0"),
                  total_venta=Decimal("50"), estado="Completada")
    uow.db.add(venta)
    await uow.db.flush()
    pago = PagoVenta(id_venta=venta.id_venta, id_metodo_pago=id_metodo_pago,
                     monto_recibido=Decimal("50"), vuelto_entregado=Decimal("0"))
    uow.db.add(pago)
    await uow.db.commit()


async def _seed_merma_detalle(uow, id_motivo):
    var = await _seed_producto_variante(uow)
    suc = Sucursal(nombre="Sucursal Merma B3", direccion="Zona 2", estado="Activo")
    uow.db.add(suc)
    await uow.db.flush()
    merma = Merma(id_sucursal=suc.id_sucursal, id_usuario=1, fecha_merma=datetime.utcnow(),
                  observaciones="prueba")
    uow.db.add(merma)
    await uow.db.flush()
    detalle = DetalleMerma(id_merma=merma.id_merma, id_variante=var.id_variante,
                           id_motivo=id_motivo, cantidad=2, costo_perdida=Decimal("10"))
    uow.db.add(detalle)
    await uow.db.commit()


# ---------------------------------------------------------------------------
# MOTIVOS DE MERMA
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crear_motivo_merma_exitoso(uow):
    svc = get_service(uow)
    res = await svc.create_motivo_merma(schemas.MotivoMermaCreate(descripcion="Caducidad"), actor_id=1)
    assert res.id_motivo is not None
    assert res.descripcion == "Caducidad"
    assert res.estado == "Activo"


@pytest.mark.asyncio
async def test_crear_motivo_merma_duplicado_rechazado(uow):
    svc = get_service(uow)
    await svc.create_motivo_merma(schemas.MotivoMermaCreate(descripcion="Robo"), actor_id=1)
    with pytest.raises(HTTPException) as exc_info:
        await svc.create_motivo_merma(schemas.MotivoMermaCreate(descripcion="ROBO"), actor_id=1)
    assert exc_info.value.status_code == 400
    assert "Ya existe" in exc_info.value.detail


@pytest.mark.asyncio
async def test_buscar_motivos_merma_filtros_paginacion(uow):
    svc = get_service(uow)
    for i in range(3):
        await svc.create_motivo_merma(schemas.MotivoMermaCreate(descripcion=f"Motivo {i}"), actor_id=1)
    filt = schemas.MotivoMermaFilter(search="Motivo", limit=2, offset=0)
    items = await svc.search_motivos_merma(filt)
    total = await svc.count_motivos_merma(filt)
    assert total >= 3
    assert len(items) == 2


@pytest.mark.asyncio
async def test_desactivar_motivo_merma_con_detalles_asociados_rechazado(uow):
    svc = get_service(uow)
    motivo = await svc.create_motivo_merma(schemas.MotivoMermaCreate(descripcion="Rotura"), actor_id=1)
    await _seed_merma_detalle(uow, motivo.id_motivo)

    with pytest.raises(HTTPException) as exc_info:
        await svc.deactivate_motivo_merma(motivo.id_motivo, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "merma asociado" in exc_info.value.detail


@pytest.mark.asyncio
async def test_desactivar_y_reactivar_motivo_merma(uow):
    svc = get_service(uow)
    motivo = await svc.create_motivo_merma(schemas.MotivoMermaCreate(descripcion="Vencimiento"), actor_id=1)
    deactivated = await svc.deactivate_motivo_merma(motivo.id_motivo, actor_id=1)
    assert deactivated.estado == "Inactivo"
    reactivated = await svc.activate_motivo_merma(motivo.id_motivo, actor_id=1)
    assert reactivated.estado == "Activo"


# ---------------------------------------------------------------------------
# MÉTODOS DE PAGO
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crear_metodo_pago_exitoso(uow):
    svc = get_service(uow)
    res = await svc.create_metodo_pago(schemas.MetodoPagoCreate(nombre="Transferencia"), actor_id=1)
    assert res.id_metodo_pago is not None
    assert res.nombre == "Transferencia"
    assert res.estado == "Activo"


@pytest.mark.asyncio
async def test_crear_metodo_pago_duplicado_rechazado(uow):
    svc = get_service(uow)
    await svc.create_metodo_pago(schemas.MetodoPagoCreate(nombre="Efectivo"), actor_id=1)
    with pytest.raises(HTTPException) as exc_info:
        await svc.create_metodo_pago(schemas.MetodoPagoCreate(nombre="efectivo"), actor_id=1)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_desactivar_metodo_pago_con_ventas_completadas_rechazado(uow):
    svc = get_service(uow)
    metodo = await svc.create_metodo_pago(schemas.MetodoPagoCreate(nombre="Cheque"), actor_id=1)
    await _seed_venta_pagada(uow, metodo.id_metodo_pago)

    with pytest.raises(HTTPException) as exc_info:
        await svc.deactivate_metodo_pago(metodo.id_metodo_pago, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "ventas completadas" in exc_info.value.detail
    assert "hay 1 pago(s)" in exc_info.value.detail


@pytest.mark.asyncio
async def test_desactivar_y_reactivar_metodo_pago(uow):
    svc = get_service(uow)
    metodo = await svc.create_metodo_pago(schemas.MetodoPagoCreate(nombre="Tarjeta"), actor_id=1)
    deactivated = await svc.deactivate_metodo_pago(metodo.id_metodo_pago, actor_id=1)
    assert deactivated.estado == "Inactivo"
    reactivated = await svc.activate_metodo_pago(metodo.id_metodo_pago, actor_id=1)
    assert reactivated.estado == "Activo"


# ---------------------------------------------------------------------------
# PROVEEDORES
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crear_proveedor_exitoso(uow):
    svc = get_service(uow)
    res = await svc.create_proveedor(
        schemas.ProveedorCreate(nombre_contacto="Juan", distribuidora="Distribuidora GT",
                                telefono="1234", correo="j@x.com"),
        actor_id=1,
    )
    assert res.id_proveedor is not None
    assert res.distribuidora == "Distribuidora GT"
    assert res.estado == "Activo"


@pytest.mark.asyncio
async def test_crear_proveedor_distribuidora_duplicada_rechazada(uow):
    svc = get_service(uow)
    await svc.create_proveedor(
        schemas.ProveedorCreate(nombre_contacto="Maria", distribuidora="Mayoreo Central"),
        actor_id=1,
    )
    with pytest.raises(HTTPException) as exc_info:
        await svc.create_proveedor(
            schemas.ProveedorCreate(nombre_contacto="Otro", distribuidora="mayoreo central"),
            actor_id=1,
        )
    assert exc_info.value.status_code == 400
    assert "distribuidora" in exc_info.value.detail.lower()


@pytest.mark.asyncio
async def test_buscar_proveedores_por_texto_y_estado(uow):
    svc = get_service(uow)
    await svc.create_proveedor(
        schemas.ProveedorCreate(nombre_contacto="Ana", distribuidora="Dulcería La Bendición"),
        actor_id=1,
    )
    filt = schemas.ProveedorFilter(search="bendición", is_active=True)
    items = await svc.search_proveedores(filt)
    total = await svc.count_proveedores(filt)
    assert total == 1
    assert items[0].distribuidora == "Dulcería La Bendición"


@pytest.mark.asyncio
async def test_desactivar_proveedor_con_orden_emitida_rechazado(uow):
    svc = get_service(uow)
    prov = await svc.create_proveedor(
        schemas.ProveedorCreate(nombre_contacto="Pedro", distribuidora="Industrial Q"),
        actor_id=1,
    )
    orden = OrdenCompra(id_proveedor=prov.id_proveedor, id_usuario=1,
                        fecha_emision=datetime.utcnow().date(), total_estimado=Decimal("100"),
                        estado="Emitida")
    uow.db.add(orden)
    await uow.db.commit()

    with pytest.raises(HTTPException) as exc_info:
        await svc.deactivate_proveedor(prov.id_proveedor, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "orden" in exc_info.value.detail.lower()
    assert "hay 1 orden(es)" in exc_info.value.detail

    # Cubre estado no finalizado 'Recibida Parcialmente'
    orden.estado = "Recibida Parcialmente"
    await uow.db.commit()
    with pytest.raises(HTTPException) as exc_info2:
        await svc.deactivate_proveedor(prov.id_proveedor, actor_id=1)
    assert exc_info2.value.status_code == 400
    assert "hay 1 orden(es)" in exc_info2.value.detail

    # Estado finalizado 'Recibida' permite desactivar
    orden.estado = "Recibida"
    await uow.db.commit()
    deact = await svc.deactivate_proveedor(prov.id_proveedor, actor_id=1)
    assert deact.estado == "Inactivo"


@pytest.mark.asyncio
async def test_desactivar_y_reactivar_proveedor(uow):
    svc = get_service(uow)
    prov = await svc.create_proveedor(
        schemas.ProveedorCreate(nombre_contacto="Luis", distribuidora="Comercial L"),
        actor_id=1,
    )
    deactivated = await svc.deactivate_proveedor(prov.id_proveedor, actor_id=1)
    assert deactivated.estado == "Inactivo"
    reactivated = await svc.activate_proveedor(prov.id_proveedor, actor_id=1)
    assert reactivated.estado == "Activo"


# ---------------------------------------------------------------------------
# DEPARTAMENTOS
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crear_departamento_exitoso(uow):
    svc = get_service(uow)
    res = await svc.create_departamento(schemas.DepartamentoCreate(nombre="Test Departamento"), actor_id=1)
    assert res.id_departamento is not None
    assert res.nombre == "Test Departamento"
    assert res.estado == "Activo"


@pytest.mark.asyncio
async def test_crear_departamento_duplicado_rechazado(uow):
    svc = get_service(uow)
    await svc.create_departamento(schemas.DepartamentoCreate(nombre="Zacapa"), actor_id=1)
    with pytest.raises(HTTPException) as exc_info:
        await svc.create_departamento(schemas.DepartamentoCreate(nombre="ZACAPA"), actor_id=1)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_desactivar_departamento_con_municipios_activos_rechazado(uow):
    svc = get_service(uow)
    dep = await svc.create_departamento(schemas.DepartamentoCreate(nombre="Alta Verapaz"), actor_id=1)
    muni = Municipio(id_departamento=dep.id_departamento, nombre="Cobán", estado="Activo")
    uow.db.add(muni)
    await uow.db.commit()

    with pytest.raises(HTTPException) as exc_info:
        await svc.deactivate_departamento(dep.id_departamento, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "municipio" in exc_info.value.detail.lower()
    assert "hay 1 municipio(s)" in exc_info.value.detail

    still = await svc.get_departamento(dep.id_departamento)
    assert still.total_municipios == 1
    assert still.estado == "Activo"


@pytest.mark.asyncio
async def test_desactivar_departamento_sin_municipios_ok(uow):
    svc = get_service(uow)
    dep = await svc.create_departamento(schemas.DepartamentoCreate(nombre="Petén Test"), actor_id=1)
    deactivated = await svc.deactivate_departamento(dep.id_departamento, actor_id=1)
    assert deactivated.estado == "Inactivo"


# ---------------------------------------------------------------------------
# MUNICIPIOS
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crear_municipio_exitoso_y_dropdown_dependiente(uow):
    svc = get_service(uow)
    dep = await svc.create_departamento(schemas.DepartamentoCreate(nombre="Sololá Test"), actor_id=1)
    muni = await svc.create_municipio(
        schemas.MunicipioCreate(id_departamento=dep.id_departamento, nombre="Panajachel"),
        actor_id=1,
    )
    assert muni.id_municipio is not None
    assert muni.id_departamento == dep.id_departamento

    # Dropdown dependiente: solo municipios del departamento
    lista = await svc.list_municipios(id_departamento=dep.id_departamento)
    assert len(lista) == 1
    assert lista[0].nombre == "Panajachel"


@pytest.mark.asyncio
async def test_crear_municipio_departamento_inexistente_rechazado(uow):
    svc = get_service(uow)
    with pytest.raises(HTTPException) as exc_info:
        await svc.create_municipio(schemas.MunicipioCreate(id_departamento=999999, nombre="X"), actor_id=1)
    assert exc_info.value.status_code == 400


@pytest.mark.asyncio
async def test_desactivar_municipio_con_clientes_activos_rechazado(uow):
    svc = get_service(uow)
    dep = await svc.create_departamento(schemas.DepartamentoCreate(nombre="Chimaltenango Test"), actor_id=1)
    muni = await svc.create_municipio(
        schemas.MunicipioCreate(id_departamento=dep.id_departamento, nombre="Tecpán"),
        actor_id=1,
    )
    tipo = TipoCliente(nombre="Consumidor", estado="Activo")
    uow.db.add(tipo)
    await uow.db.flush()
    cliente = Cliente(id_tipo_cliente=tipo.id_tipo_cliente, id_municipio=muni.id_municipio,
                      nit="1234567-8", nombre_comercial="Tienda Test", estado="Activo")
    uow.db.add(cliente)
    await uow.db.commit()

    with pytest.raises(HTTPException) as exc_info:
        await svc.deactivate_municipio(muni.id_municipio, actor_id=1)
    assert exc_info.value.status_code == 400
    assert "cliente" in exc_info.value.detail.lower()
    assert "1" in exc_info.value.detail


@pytest.mark.asyncio
async def test_desactivar_y_reactivar_municipio(uow):
    svc = get_service(uow)
    dep = await svc.create_departamento(schemas.DepartamentoCreate(nombre="Izabal Test"), actor_id=1)
    muni = await svc.create_municipio(
        schemas.MunicipioCreate(id_departamento=dep.id_departamento, nombre="Livingston"),
        actor_id=1,
    )
    deactivated = await svc.deactivate_municipio(muni.id_municipio, actor_id=1)
    assert deactivated.estado == "Inactivo"
    reactivated = await svc.activate_municipio(muni.id_municipio, actor_id=1)
    assert reactivated.estado == "Activo"