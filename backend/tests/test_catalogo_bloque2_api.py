import pytest
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import Rol, Usuario, Permiso, RolPermiso, Categoria, Sucursal, AreaBodega, UnidadMedida, Subcategoria, Producto, VarianteProducto, InventarioSucursal


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def seed_catalogo_admin_auth(db_session):
    rol = Rol(nombre="Administradora", estado="Activo")
    db_session.add(rol)
    await db_session.flush()

    user = Usuario(
        id_rol=rol.id_rol,
        nombre_completo="Admin Catalogo",
        username="admin_cat",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    db_session.add(user)

    permiso = Permiso(modulo="Catálogos", codigo="CATALOGO_ADMIN", descripcion="Gestión de catálogos")
    db_session.add(permiso)
    await db_session.flush()

    db_session.add(RolPermiso(id_rol=rol.id_rol, id_permiso=permiso.id_permiso))
    await db_session.commit()

    token = security.create_access_token(
        data={"sub": user.username, "role": "Administradora", "permissions": ["CATALOGO_ADMIN"]}
    )
    return {"Authorization": f"Bearer {token}"}


async def seed_non_admin_auth(db_session, role_name="Cajera", username="cajera_demo"):
    """Crea un usuario con rol NO administrador (sin CATALOGO_ADMIN).
    Permite parametrizar el rol: 'Cajera' o 'Bodega' (bodeguero)."""
    rol = Rol(nombre=role_name, estado="Activo")
    db_session.add(rol)
    await db_session.flush()

    user = Usuario(
        id_rol=rol.id_rol,
        nombre_completo=f"{role_name} Demo",
        username=username,
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    db_session.add(user)
    await db_session.commit()

    token = security.create_access_token(
        data={"sub": user.username, "role": role_name, "permissions": []}
    )
    return {"Authorization": f"Bearer {token}"}


# ---------------------------------------------------------------------------
# SUCURSALES API
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crear_sucursal_sin_permiso_retorna_403(client, db_session):
    headers = await seed_non_admin_auth(db_session)
    res = await client.post(
        "/api/catalogos/sucursales",
        headers=headers,
        json={"nombre": "Sucursal X", "direccion": "Zona 1"},
    )
    assert res.status_code == 403


@pytest.mark.asyncio
async def test_crud_sucursal_con_permiso_y_soft_delete(client, db_session):
    headers = await seed_catalogo_admin_auth(db_session)

    # 1. Crear
    res = await client.post(
        "/api/catalogos/sucursales",
        headers=headers,
        json={"nombre": "Sucursal Metro", "direccion": "Centro Comercial Metro", "telefono": "2345-6789"},
    )
    assert res.status_code == 201
    data = res.json()
    id_suc = data["id_sucursal"]
    assert data["nombre"] == "Sucursal Metro"
    assert data["estado"] == "Activo"

    # 2. Obtener / Ficha
    res_get = await client.get(f"/api/catalogos/sucursales/{id_suc}", headers=headers)
    assert res_get.status_code == 200
    assert res_get.json()["id_sucursal"] == id_suc

    # 3. Actualizar
    res_put = await client.put(
        f"/api/catalogos/sucursales/{id_suc}",
        headers=headers,
        json={"nombre": "Sucursal Metro Actualizada", "direccion": "Nueva Dir"},
    )
    assert res_put.status_code == 200
    assert res_put.json()["nombre"] == "Sucursal Metro Actualizada"

    # 4. Soft Delete (Desactivar)
    res_del = await client.delete(f"/api/catalogos/sucursales/{id_suc}", headers=headers)
    assert res_del.status_code == 200
    assert res_del.json()["estado"] == "Inactivo"

    # Verificar que sigue existiendo en BD con estado Inactivo
    res_check = await client.get(f"/api/catalogos/sucursales/{id_suc}", headers=headers)
    assert res_check.status_code == 200
    assert res_check.json()["estado"] == "Inactivo"


# ---------------------------------------------------------------------------
# AREAS DE BODEGA API
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crud_area_bodega_con_soft_delete(client, db_session):
    headers = await seed_catalogo_admin_auth(db_session)

    # Crear sucursal primero
    res_suc = await client.post(
        "/api/catalogos/sucursales",
        headers=headers,
        json={"nombre": "Sucursal Para Areas", "direccion": "Zona 12"},
    )
    id_suc = res_suc.json()["id_sucursal"]

    # Crear área
    res = await client.post(
        "/api/catalogos/areas",
        headers=headers,
        json={"id_sucursal": id_suc, "nombre_area": "Pasillo 4"},
    )
    assert res.status_code == 201
    id_area = res.json()["id_area"]
    assert res.json()["nombre_area"] == "Pasillo 4"

    # Desactivar
    res_del = await client.delete(f"/api/catalogos/areas/{id_area}", headers=headers)
    assert res_del.status_code == 200
    assert res_del.json()["estado"] == "Inactivo"


# ---------------------------------------------------------------------------
# SUBCATEGORIAS API
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crud_subcategoria_con_soft_delete(client, db_session):
    headers = await seed_catalogo_admin_auth(db_session)

    # Crear categoría primero
    cat = Categoria(nombre="Ropa Test", estado="Activo")
    db_session.add(cat)
    await db_session.commit()

    # Crear subcategoría
    res = await client.post(
        "/api/catalogos/subcategorias",
        headers=headers,
        json={"id_categoria": cat.id_categoria, "nombre": "Camisas"},
    )
    assert res.status_code == 201
    id_sub = res.json()["id_subcategoria"]
    assert res.json()["nombre"] == "Camisas"

    # Duplicada rechazada
    res_dup = await client.post(
        "/api/catalogos/subcategorias",
        headers=headers,
        json={"id_categoria": cat.id_categoria, "nombre": "Camisas"},
    )
    assert res_dup.status_code == 400

    # Desactivar
    res_del = await client.delete(f"/api/catalogos/subcategorias/{id_sub}", headers=headers)
    assert res_del.status_code == 200
    assert res_del.json()["estado"] == "Inactivo"


# ---------------------------------------------------------------------------
# UNIDADES DE MEDIDA API
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_crud_unidad_medida_con_soft_delete_y_export(client, db_session):
    headers = await seed_catalogo_admin_auth(db_session)

    # Crear unidad
    res = await client.post(
        "/api/catalogos/unidades",
        headers=headers,
        json={"codigo": "KG", "descripcion": "Kilogramo"},
    )
    assert res.status_code == 201
    id_uni = res.json()["id_unidad"]

    # Código duplicado rechazado
    res_dup = await client.post(
        "/api/catalogos/unidades",
        headers=headers,
        json={"codigo": "KG", "descripcion": "Kilo Duplicate"},
    )
    assert res_dup.status_code == 400

    # Desactivar
    res_del = await client.delete(f"/api/catalogos/unidades/{id_uni}", headers=headers)
    assert res_del.status_code == 200
    assert res_del.json()["estado"] == "Inactivo"

    # Exportación CSV
    res_csv = await client.get("/api/catalogos/unidades/export?format=csv", headers=headers)
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]

    # Exportación Excel
    res_xlsx = await client.get("/api/catalogos/unidades/export?format=excel", headers=headers)
    assert res_xlsx.status_code == 200
    assert "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in res_xlsx.headers["content-type"]


# ---------------------------------------------------------------------------
# LECTURA DE COMBOS (Pendiente 1): usuarios NO admin pueden cargar los combos
# ---------------------------------------------------------------------------

async def _seed_combo_data(db_session):
    """Crea datos de ejemplo para poder validar que el combo devuelve registros."""
    suc = Sucursal(nombre="Sucursal Combo", direccion="Zona 1", telefono=None, estado="Activo")
    db_session.add(suc)
    await db_session.flush()
    area = AreaBodega(id_sucursal=suc.id_sucursal, nombre_area="Área Combo", estado="Activo")
    db_session.add(area)
    await db_session.flush()
    uni = UnidadMedida(codigo="CJB", descripcion="Caja Combo", estado="Activo")
    db_session.add(uni)
    await db_session.flush()
    cat = Categoria(nombre="Cat Combo", estado="Activo")
    db_session.add(cat)
    await db_session.flush()
    sub = Subcategoria(id_categoria=cat.id_categoria, nombre="Sub Combo", estado="Activo")
    db_session.add(sub)
    await db_session.commit()
    return {
        "id_sucursal": suc.id_sucursal,
        "id_area": area.id_area,
        "id_unidad": uni.id_unidad,
        "id_subcategoria": sub.id_subcategoria,
    }


@pytest.mark.parametrize(
    "role_name,username",
    [("Cajera", "cajera_demo"), ("Bodega", "bodega_demo")],
)
@pytest.mark.asyncio
async def test_combos_catalogos_cargan_para_usuario_no_admin(client, db_session, role_name, username):
    headers = await seed_non_admin_auth(db_session, role_name=role_name, username=username)
    await _seed_combo_data(db_session)

    # Los 4 combos de lectura deben responder 200 para un usuario SIN CATALOGO_ADMIN
    combos = [
        "/api/catalogos/sucursales",
        "/api/catalogos/areas",
        "/api/catalogos/subcategorias",
        "/api/catalogos/unidades",
    ]
    for url in combos:
        res = await client.get(url, headers=headers)
        assert res.status_code == 200, f"{url} debería ser accesible para no-admin ({role_name}) (200), obtuvo {res.status_code}"

    # Y deben contener los datos sembrados en cada uno
    res_sub = await client.get("/api/catalogos/subcategorias", headers=headers)
    items = res_sub.json()
    assert any(s["nombre"] == "Sub Combo" for s in items)

    res_suc = await client.get("/api/catalogos/sucursales", headers=headers)
    suc_items = res_suc.json()
    assert any(s["nombre"] == "Sucursal Combo" for s in suc_items)

    res_uni = await client.get("/api/catalogos/unidades", headers=headers)
    uni_items = res_uni.json()
    assert any(u["codigo"] == "CJB" for u in uni_items)

    res_area = await client.get("/api/catalogos/areas", headers=headers)
    area_items = res_area.json()
    assert any(a["nombre_area"] == "Área Combo" for a in area_items)


@pytest.mark.parametrize(
    "role_name,username",
    [("Cajera", "cajera_demo"), ("Bodega", "bodega_demo")],
)
@pytest.mark.asyncio
async def test_crud_catalogo_rechazado_403_para_usuario_no_admin(client, db_session, role_name, username):
    headers = await seed_non_admin_auth(db_session, role_name=role_name, username=username)

    # POST / PUT / DELETE de cada entidad deben responder 403 sin CATALOGO_ADMIN
    res = await client.post("/api/catalogos/sucursales", headers=headers,
                            json={"nombre": "Suc X", "direccion": "Zona 1"})
    assert res.status_code == 403
    res = await client.post("/api/catalogos/areas", headers=headers,
                            json={"id_sucursal": 1, "nombre_area": "A1"})
    assert res.status_code == 403
    res = await client.post("/api/catalogos/subcategorias", headers=headers,
                            json={"id_categoria": 1, "nombre": "S1"})
    assert res.status_code == 403
    res = await client.post("/api/catalogos/unidades", headers=headers,
                            json={"codigo": "XX", "descripcion": "Unidad X"})
    assert res.status_code == 403
    res = await client.put("/api/catalogos/sucursales/1", headers=headers,
                           json={"nombre": "Suc Y"})
    assert res.status_code == 403
    res = await client.delete("/api/catalogos/sucursales/1", headers=headers)
    assert res.status_code == 403


# ---------------------------------------------------------------------------
# DESACTIVACIÓN SEGURA (Pendiente 2): 400 con mensaje claro en la API
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_desactivar_subcategoria_con_producto_activo_retorna_400(client, db_session):
    headers = await seed_catalogo_admin_auth(db_session)

    cat = Categoria(nombre="Cat Segura", estado="Activo")
    db_session.add(cat)
    await db_session.flush()
    sub = Subcategoria(id_categoria=cat.id_categoria, nombre="Sub Segura", estado="Activo")
    db_session.add(sub)
    await db_session.flush()
    uni = UnidadMedida(codigo="SEG", descripcion="Unidad Segura", estado="Activo")
    db_session.add(uni)
    await db_session.flush()
    prod = Producto(id_subcategoria=sub.id_subcategoria, id_unidad=uni.id_unidad,
                    nombre="Producto Seguro", estado="Activo")
    db_session.add(prod)
    await db_session.commit()

    res = await client.delete(f"/api/catalogos/subcategorias/{sub.id_subcategoria}", headers=headers)
    assert res.status_code == 400
    assert "producto" in res.json()["detail"]
    assert "1" in res.json()["detail"]


@pytest.mark.asyncio
async def test_desactivar_sucursal_con_inventario_activo_retorna_400(client, db_session):
    headers = await seed_catalogo_admin_auth(db_session)

    suc = Sucursal(nombre="Sucursal Segura", direccion="Zona 2", estado="Activo")
    db_session.add(suc)
    await db_session.flush()
    cat = Categoria(nombre="Cat Inv API", estado="Activo")
    db_session.add(cat)
    await db_session.flush()
    sub = Subcategoria(id_categoria=cat.id_categoria, nombre="Sub Inv API", estado="Activo")
    db_session.add(sub)
    await db_session.flush()
    uni = UnidadMedida(codigo="API", descripcion="Unidad API", estado="Activo")
    db_session.add(uni)
    await db_session.flush()
    prod = Producto(id_subcategoria=sub.id_subcategoria, id_unidad=uni.id_unidad,
                    nombre="Producto API", estado="Activo")
    db_session.add(prod)
    await db_session.flush()
    var = VarianteProducto(id_producto=prod.id_producto, codigo_barras="API-001",
                           precio_detalle=Decimal("10"), precio_mayoreo=Decimal("8"),
                           costo_promedio=Decimal("5"))
    db_session.add(var)
    await db_session.flush()
    inv = InventarioSucursal(id_variante=var.id_variante, id_sucursal=suc.id_sucursal,
                             stock_actual=3, stock_minimo=1)
    db_session.add(inv)
    await db_session.commit()

    res = await client.delete(f"/api/catalogos/sucursales/{suc.id_sucursal}", headers=headers)
    assert res.status_code == 400
    assert "inventario activo" in res.json()["detail"]


@pytest.mark.asyncio
async def test_desactivar_area_bodega_con_inventario_activo_retorna_400(client, db_session):
    headers = await seed_catalogo_admin_auth(db_session)

    suc = Sucursal(nombre="Sucursal Area API", direccion="Zona 3", estado="Activo")
    db_session.add(suc)
    await db_session.flush()
    area = AreaBodega(id_sucursal=suc.id_sucursal, nombre_area="Area Con Stock API", estado="Activo")
    db_session.add(area)
    await db_session.flush()
    cat = Categoria(nombre="Cat Area API", estado="Activo")
    db_session.add(cat)
    await db_session.flush()
    sub = Subcategoria(id_categoria=cat.id_categoria, nombre="Sub Area API", estado="Activo")
    db_session.add(sub)
    await db_session.flush()
    uni = UnidadMedida(codigo="AREA", descripcion="Unidad Area API", estado="Activo")
    db_session.add(uni)
    await db_session.flush()
    prod = Producto(id_subcategoria=sub.id_subcategoria, id_unidad=uni.id_unidad,
                    nombre="Producto Area API", estado="Activo")
    db_session.add(prod)
    await db_session.flush()
    var = VarianteProducto(id_producto=prod.id_producto, codigo_barras="AREA-001",
                           precio_detalle=Decimal("10"), precio_mayoreo=Decimal("8"),
                           costo_promedio=Decimal("5"))
    db_session.add(var)
    await db_session.flush()
    inv = InventarioSucursal(id_variante=var.id_variante, id_sucursal=suc.id_sucursal,
                             id_area=area.id_area, stock_actual=2, stock_minimo=1)
    db_session.add(inv)
    await db_session.commit()

    res = await client.delete(f"/api/catalogos/areas/{area.id_area}", headers=headers)
    assert res.status_code == 400
    assert "inventario activo" in res.json()["detail"]
    assert "1" in res.json()["detail"]


@pytest.mark.asyncio
async def test_desactivar_unidad_medida_con_producto_activo_retorna_400(client, db_session):
    headers = await seed_catalogo_admin_auth(db_session)

    cat = Categoria(nombre="Cat Uni API", estado="Activo")
    db_session.add(cat)
    await db_session.flush()
    sub = Subcategoria(id_categoria=cat.id_categoria, nombre="Sub Uni API", estado="Activo")
    db_session.add(sub)
    await db_session.flush()
    uni = UnidadMedida(codigo="UNI", descripcion="Unidad Bloqueada API", estado="Activo")
    db_session.add(uni)
    await db_session.flush()
    prod = Producto(id_subcategoria=sub.id_subcategoria, id_unidad=uni.id_unidad,
                    nombre="Producto Uni API", estado="Activo")
    db_session.add(prod)
    await db_session.commit()

    res = await client.delete(f"/api/catalogos/unidades/{uni.id_unidad}", headers=headers)
    assert res.status_code == 400
    assert "producto" in res.json()["detail"]
    assert "1" in res.json()["detail"]


@pytest.mark.asyncio
async def test_desactivar_sucursal_con_area_activa_retorna_400(client, db_session):
    headers = await seed_catalogo_admin_auth(db_session)

    suc = Sucursal(nombre="Sucursal Con Area API", direccion="Zona 12", estado="Activo")
    db_session.add(suc)
    await db_session.flush()
    db_session.add(AreaBodega(id_sucursal=suc.id_sucursal, nombre_area="Area Activa API", estado="Activo"))
    await db_session.commit()

    res = await client.delete(f"/api/catalogos/sucursales/{suc.id_sucursal}", headers=headers)
    assert res.status_code == 400
    assert "área(s) de bodega activa(s)" in res.json()["detail"]
    assert "1" in res.json()["detail"]

    res_get = await client.get(f"/api/catalogos/sucursales/{suc.id_sucursal}", headers=headers)
    assert res_get.json()["estado"] == "Activo"
