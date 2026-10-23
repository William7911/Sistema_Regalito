import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import Rol, Usuario, TipoCliente, Cliente, Permiso, RolPermiso, DepartamentoGeografico, Municipio


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def seed_auth(db_session):
    rol = Rol(nombre="Administradora", estado="Activo")
    db_session.add(rol)
    await db_session.flush()

    user = Usuario(
        id_rol=rol.id_rol,
        nombre_completo="Admin Cliente",
        username="admin_cliente",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    db_session.add(user)

    permiso = Permiso(modulo="Clientes", codigo="CLIENTE_ADMIN", descripcion="Administrar clientes")
    db_session.add(permiso)
    await db_session.flush()

    db_session.add(RolPermiso(id_rol=rol.id_rol, id_permiso=permiso.id_permiso))

    tipo = TipoCliente(nombre="General", estado="Activo")
    db_session.add(tipo)
    await db_session.commit()

    token = security.create_access_token(
        data={"sub": user.username, "role": "Administradora", "permissions": ["CLIENTE_ADMIN"]}
    )
    return {"Authorization": f"Bearer {token}"}, tipo.id_tipo_cliente


async def seed_non_admin_auth(db_session):
    rol = Rol(nombre="Cajera", estado="Activo")
    db_session.add(rol)
    await db_session.flush()

    user = Usuario(
        id_rol=rol.id_rol,
        nombre_completo="Cajera Demo",
        username="cajera_demo",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    db_session.add(user)
    await db_session.commit()

    token = security.create_access_token(
        data={"sub": user.username, "role": "Cajera", "permissions": []}
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_api_clientes_crud(client, db_session):
    headers, id_tipo = await seed_auth(db_session)

    # 1. Crear cliente
    crear_payload = {
        "id_tipo_cliente": id_tipo,
        "nit": "887766-5",
        "nombre_comercial": "Distribuidora San Juan",
        "direccion": "Calle Real 1-20",
        "contactos": [
            {"telefono": "2233-4455", "correo": "info@sanjuan.com"}
        ]
    }
    res_crear = await client.post("/api/clientes", json=crear_payload, headers=headers)
    assert res_crear.status_code == 201
    data_crear = res_crear.json()
    assert data_crear["nit"] == "887766-5"
    assert data_crear["nombre_comercial"] == "Distribuidora San Juan"
    id_cliente = data_crear["id_cliente"]

    # 2. Búsqueda por NIT (usada por POS y FEL)
    res_nit = await client.get("/api/clientes/nit/887766-5", headers=headers)
    assert res_nit.status_code == 200
    assert res_nit.json()["id_cliente"] == id_cliente

    # 3. Listar clientes con filtro
    res_lista = await client.get("/api/clientes?nombre=San%20Juan", headers=headers)
    assert res_lista.status_code == 200
    data_lista = res_lista.json()
    assert data_lista["total"] >= 1
    assert data_lista["items"][0]["id_cliente"] == id_cliente

    # 4. Actualizar cliente
    update_payload = {"nombre_comercial": "Distribuidora San Juan S.A."}
    res_update = await client.put(f"/api/clientes/{id_cliente}", json=update_payload, headers=headers)
    assert res_update.status_code == 200
    assert res_update.json()["nombre_comercial"] == "Distribuidora San Juan S.A."

    # 5. Desactivar cliente (soft delete)
    res_delete = await client.delete(f"/api/clientes/{id_cliente}", headers=headers)
    assert res_delete.status_code == 200
    assert res_delete.json()["estado"] == "Inactivo"


@pytest.mark.asyncio
async def test_api_cliente_403_sin_permiso_cliente_admin(client, db_session):
    headers_admin, id_tipo = await seed_auth(db_session)
    headers_cajera = await seed_non_admin_auth(db_session)

    # Intento de crear cliente sin CLIENTE_ADMIN -> 403
    payload = {
        "id_tipo_cliente": id_tipo,
        "nit": "999888-1",
        "nombre_comercial": "Tienda Denegada"
    }
    res_post = await client.post("/api/clientes", json=payload, headers=headers_cajera)
    assert res_post.status_code == 403
    assert "CLIENTE_ADMIN" in res_post.json()["detail"]

    # Intento de editar sin permiso -> 403
    res_put = await client.put("/api/clientes/1", json={"nombre_comercial": "Hack"}, headers=headers_cajera)
    assert res_put.status_code == 403

    # Intento de eliminar sin permiso -> 403
    res_del = await client.delete("/api/clientes/1", headers=headers_cajera)
    assert res_del.status_code == 403


@pytest.mark.asyncio
async def test_api_cliente_cf_protegido_desactivacion_y_cambio_nit(client, db_session):
    headers, id_tipo = await seed_auth(db_session)

    # Crear cliente CF explícito
    res_cf = await client.post(
        "/api/clientes",
        json={"id_tipo_cliente": id_tipo, "nit": "CF", "nombre_comercial": "Consumidor Final"},
        headers=headers,
    )
    assert res_cf.status_code == 201
    cf_id = res_cf.json()["id_cliente"]

    # 1. Intento de desactivar CF -> 400
    res_del = await client.delete(f"/api/clientes/{cf_id}", headers=headers)
    assert res_del.status_code == 400
    assert "Consumidor Final" in res_del.json()["detail"]

    # 2. Intento de modificar su NIT -> 400
    res_put_nit = await client.put(
        f"/api/clientes/{cf_id}",
        json={"nit": "1234567-8"},
        headers=headers,
    )
    assert res_put_nit.status_code == 400
    assert "No se puede modificar el NIT del cliente Consumidor Final (CF)" in res_put_nit.json()["detail"]


@pytest.mark.asyncio
async def test_api_cliente_nit_duplicado_rechazado(client, db_session):
    headers, id_tipo = await seed_auth(db_session)

    # Crear primero
    res1 = await client.post(
        "/api/clientes",
        json={"id_tipo_cliente": id_tipo, "nit": "5566778-9", "nombre_comercial": "Cliente Uno"},
        headers=headers,
    )
    assert res1.status_code == 201

    # Intentar crear con mismo NIT -> 400
    res2 = await client.post(
        "/api/clientes",
        json={"id_tipo_cliente": id_tipo, "nit": "5566778-9", "nombre_comercial": "Cliente Dos"},
        headers=headers,
    )
    assert res2.status_code == 400
    assert "Ya existe un cliente con ese NIT" in res2.json()["detail"]


@pytest.mark.asyncio
async def test_api_cliente_paginacion_ordenamiento_y_filtros(client, db_session):
    headers, id_tipo = await seed_auth(db_session)

    for i in range(1, 6):
        await client.post(
            "/api/clientes",
            json={"id_tipo_cliente": id_tipo, "nit": f"100000{i}-0", "nombre_comercial": f"Cliente Beta {i}"},
            headers=headers,
        )

    # Paginación: limit=2, offset=0
    res_pag = await client.get("/api/clientes?limit=2&offset=0&nombre=Beta", headers=headers)
    assert res_pag.status_code == 200
    data_pag = res_pag.json()
    assert data_pag["total"] == 5
    assert len(data_pag["items"]) == 2

    # Ordenamiento desc
    res_desc = await client.get("/api/clientes?limit=5&sort_by=nombre_comercial&sort_order=desc&nombre=Beta", headers=headers)
    assert res_desc.status_code == 200
    nombres = [c["nombre_comercial"] for c in res_desc.json()["items"]]
    assert nombres == sorted(nombres, reverse=True)


@pytest.mark.asyncio
async def test_api_tipos_cliente_crud_completo(client, db_session):
    headers, _ = await seed_auth(db_session)

    # 1. Crear tipo de cliente
    res_crear = await client.post(
        "/api/tipos-cliente",
        json={"nombre": "Corporativo Especial", "descuento_predeterminado": 12.5},
        headers=headers,
    )
    assert res_crear.status_code == 201
    tipo = res_crear.json()
    assert tipo["nombre"] == "Corporativo Especial"
    assert tipo["estado"] == "Activo"
    id_tipo = tipo["id_tipo_cliente"]

    # 2. Consultar por ID
    res_get = await client.get(f"/api/tipos-cliente/{id_tipo}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["id_tipo_cliente"] == id_tipo

    # 3. Actualizar tipo
    res_put = await client.put(
        f"/api/tipos-cliente/{id_tipo}",
        json={"nombre": "Corporativo Platino", "descuento_predeterminado": 15.0},
        headers=headers,
    )
    assert res_put.status_code == 200
    assert res_put.json()["nombre"] == "Corporativo Platino"

    # 4. Desactivar (soft delete)
    res_del = await client.delete(f"/api/tipos-cliente/{id_tipo}", headers=headers)
    assert res_del.status_code == 200
    assert res_del.json()["estado"] == "Inactivo"

    # 5. Listar con only_active=true no lo debe incluir
    res_activos = await client.get("/api/tipos-cliente?only_active=true", headers=headers)
    assert res_activos.status_code == 200
    ids_activos = [t["id_tipo_cliente"] for t in res_activos.json()]
    assert id_tipo not in ids_activos


@pytest.mark.asyncio
async def test_api_departamentos_municipios_reutilizable(client, db_session):
    headers, _ = await seed_auth(db_session)

    # Insertar departamento y municipios
    dep = DepartamentoGeografico(nombre="Quetzaltenango", estado="Activo")
    db_session.add(dep)
    await db_session.flush()

    muni1 = Municipio(id_departamento=dep.id_departamento, nombre="Quetzaltenango", estado="Activo")
    muni2 = Municipio(id_departamento=dep.id_departamento, nombre="Salcajá", estado="Activo")
    db_session.add_all([muni1, muni2])
    await db_session.commit()

    # Endpoint reutilizable: /api/departamentos/{id}/municipios
    res = await client.get(f"/api/departamentos/{dep.id_departamento}/municipios", headers=headers)
    assert res.status_code == 200
    munis = res.json()
    assert len(munis) == 2
    assert munis[0]["nombre"] == "Quetzaltenango"
    assert munis[1]["nombre"] == "Salcajá"
