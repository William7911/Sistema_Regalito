from decimal import Decimal
import pytest
from fastapi import HTTPException
from app.db.models import TipoCliente, Cliente, DepartamentoGeografico, Municipio
from app.services.cliente_service import ConcreteClienteService
from app.schemas import cliente_schema as schemas


def service(uow):
    return ConcreteClienteService(uow)


async def seed_cliente_dependencies(uow):
    tipo = TipoCliente(nombre="Minorista", descuento_predeterminado=Decimal("0.00"), estado="Activo")
    created_tipo = await uow.tipos_cliente.create(tipo)

    dep = DepartamentoGeografico(nombre="Guatemala", estado="Activo")
    uow.db.add(dep)
    await uow.db.flush()

    muni = Municipio(id_departamento=dep.id_departamento, nombre="Mixco", estado="Activo")
    uow.db.add(muni)
    await uow.db.flush()
    await uow.commit()

    return created_tipo.id_tipo_cliente, muni.id_municipio


@pytest.mark.asyncio
async def test_crear_cliente_exitoso_con_contactos(uow):
    id_tipo, id_muni = await seed_cliente_dependencies(uow)
    svc = service(uow)

    payload = schemas.ClienteCreate(
        id_tipo_cliente=id_tipo,
        id_municipio=id_muni,
        nit="1234567-8",
        nombre_comercial="Comercial Las Rosas",
        direccion="Zona 4 de Mixco",
        contactos=[
            schemas.ClienteContactoCreate(telefono="5544-3322", correo="contacto@rosas.com")
        ]
    )

    creado = await svc.create_cliente(payload, actor_id=1)
    assert creado.id_cliente is not None
    assert creado.nit == "1234567-8"
    assert creado.nombre_comercial == "Comercial Las Rosas"
    assert creado.estado == "Activo"
    assert len(creado.contactos) == 1
    assert creado.contactos[0].telefono == "5544-3322"
    assert creado.municipio_nombre == "Mixco"


@pytest.mark.asyncio
async def test_crear_cliente_cf_permitido_multiples_veces(uow):
    id_tipo, id_muni = await seed_cliente_dependencies(uow)
    svc = service(uow)

    payload1 = schemas.ClienteCreate(
        id_tipo_cliente=id_tipo,
        nit="CF",
        nombre_comercial="Consumidor Final 1",
    )
    payload2 = schemas.ClienteCreate(
        id_tipo_cliente=id_tipo,
        nit="cf",  # Minúsculas debe normalizarse a CF
        nombre_comercial="Consumidor Final 2",
    )

    c1 = await svc.create_cliente(payload1, actor_id=1)
    c2 = await svc.create_cliente(payload2, actor_id=1)
    assert c1.id_cliente != c2.id_cliente
    assert c1.nit == "CF"
    assert c2.nit == "CF"


@pytest.mark.asyncio
async def test_nit_duplicado_rechazado_si_no_es_cf(uow):
    id_tipo, _ = await seed_cliente_dependencies(uow)
    svc = service(uow)

    payload = schemas.ClienteCreate(
        id_tipo_cliente=id_tipo,
        nit="9988776-5",
        nombre_comercial="Empresa Alpha",
    )
    await svc.create_cliente(payload, actor_id=1)

    with pytest.raises(HTTPException) as exc:
        await svc.create_cliente(payload, actor_id=1)
    assert exc.value.status_code == 400
    assert "Ya existe un cliente con ese NIT" in exc.value.detail


@pytest.mark.asyncio
async def test_rechazar_desactivar_cliente_cf(uow):
    id_tipo, _ = await seed_cliente_dependencies(uow)
    cf = Cliente(id_cliente=1, id_tipo_cliente=id_tipo, nit="CF", nombre_comercial="Consumidor Final", estado="Activo")
    uow.db.add(cf)
    await uow.commit()

    svc = service(uow)
    with pytest.raises(HTTPException) as exc:
        await svc.deactivate_cliente(1, actor_id=1)
    assert exc.value.status_code == 400
    assert "Consumidor Final" in exc.value.detail

    # Intento de modificar su NIT -> 400
    with pytest.raises(HTTPException) as exc_nit:
        await svc.update_cliente(1, schemas.ClienteUpdate(nit="9999999-9"), actor_id=1)
    assert exc_nit.value.status_code == 400
    assert "No se puede modificar el NIT" in exc_nit.value.detail



@pytest.mark.asyncio
async def test_desactivar_cliente_normal_soft_delete(uow):
    id_tipo, _ = await seed_cliente_dependencies(uow)
    svc = service(uow)

    payload = schemas.ClienteCreate(
        id_tipo_cliente=id_tipo,
        nit="5544332-1",
        nombre_comercial="Cliente Temporal",
    )
    creado = await svc.create_cliente(payload, actor_id=1)
    desactivado = await svc.deactivate_cliente(creado.id_cliente, actor_id=1)
    assert desactivado.estado == "Inactivo"

    # Verificar que el filtro activo no lo incluye
    activos = await svc.list_clientes(schemas.ClienteFilter(is_active=True))
    assert creado.id_cliente not in [c.id_cliente for c in activos]


@pytest.mark.asyncio
async def test_busqueda_y_filtros_cliente(uow):
    id_tipo, _ = await seed_cliente_dependencies(uow)
    svc = service(uow)

    await svc.create_cliente(schemas.ClienteCreate(id_tipo_cliente=id_tipo, nit="11111-1", nombre_comercial="Distribuidora El Éxito"), actor_id=1)
    await svc.create_cliente(schemas.ClienteCreate(id_tipo_cliente=id_tipo, nit="22222-2", nombre_comercial="Farmacia La Paz"), actor_id=1)

    res_nombre = await svc.list_clientes(schemas.ClienteFilter(nombre="Éxito"))
    assert len(res_nombre) == 1
    assert res_nombre[0].nit == "11111-1"

    res_nit = await svc.list_clientes(schemas.ClienteFilter(nit="22222"))
    assert len(res_nit) == 1
    assert res_nit[0].nombre_comercial == "Farmacia La Paz"


@pytest.mark.asyncio
async def test_tipo_cliente_crud(uow):
    svc = service(uow)
    tipo = await svc.create_tipo_cliente(schemas.TipoClienteCreate(nombre="Mayorista VIP", descuento_predeterminado=Decimal("5.00")))
    assert tipo.id_tipo_cliente is not None
    assert tipo.nombre == "Mayorista VIP"

    actualizado = await svc.update_tipo_cliente(tipo.id_tipo_cliente, schemas.TipoClienteUpdate(nombre="Mayorista Preferencial"))
    assert actualizado.nombre == "Mayorista Preferencial"

    lista = await svc.list_tipos_cliente()
    assert any(t.nombre == "Mayorista Preferencial" for t in lista)


@pytest.mark.asyncio
async def test_crear_cliente_requiere_tipo_cliente_valido(uow):
    svc = service(uow)
    with pytest.raises(HTTPException) as exc:
        await svc.create_cliente(schemas.ClienteCreate(id_tipo_cliente=9999, nit="12345", nombre_comercial="Prueba"))
    assert exc.value.status_code == 400
    assert "tipo de cliente" in exc.value.detail.lower()


@pytest.mark.asyncio
async def test_obtener_cliente_por_nit(uow):
    id_tipo, _ = await seed_cliente_dependencies(uow)
    svc = service(uow)
    await svc.create_cliente(schemas.ClienteCreate(id_tipo_cliente=id_tipo, nit="7766554-9", nombre_comercial="Tienda El Sol"), actor_id=1)

    cliente = await svc.get_by_nit("7766554-9")
    assert cliente.nombre_comercial == "Tienda El Sol"

