import pytest
from decimal import Decimal
from datetime import datetime, date
from httpx import AsyncClient, ASGITransport
from fastapi import HTTPException
from sqlalchemy import select

from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import (
    Rol, Usuario, Permiso, RolPermiso, Sucursal, Categoria, Subcategoria, UnidadMedida,
    Producto, VarianteProducto, InventarioSucursal, TrasladoInventario, BitacoraAuditoria
)
from app.schemas.traslado_schema import TrasladoCreate
from app.services.traslado_service import ConcreteTrasladoService


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def seed_traslado_data(db_session):
    # Permisos
    p_inv = Permiso(id_permiso=1, modulo="Inventario", codigo="INV_INGRESAR_MERCADERIA", descripcion="Ingreso")
    p_ventas = Permiso(id_permiso=2, modulo="Ventas", codigo="VENTA_COBRAR", descripcion="Cobro")
    db_session.add_all([p_inv, p_ventas])
    await db_session.flush()

    # Roles
    rol_admin = Rol(id_rol=1, nombre="Administradora", estado="Activo")
    rol_bodega = Rol(id_rol=2, nombre="Bodeguero", estado="Activo")
    rol_cajera = Rol(id_rol=3, nombre="Cajera", estado="Activo")
    db_session.add_all([rol_admin, rol_bodega, rol_cajera])
    await db_session.flush()

    # Mapeo permisos
    db_session.add_all([
        RolPermiso(id_rol=1, id_permiso=1),
        RolPermiso(id_rol=1, id_permiso=2),
        RolPermiso(id_rol=2, id_permiso=1),
        RolPermiso(id_rol=3, id_permiso=2),
    ])
    await db_session.flush()

    # Usuarios
    user_admin = Usuario(
        id_usuario=1, id_rol=1, nombre_completo="Admin Traslados",
        username="admin_traslado", password_hash=security.get_password_hash("pass123"), estado="Activo"
    )
    user_bodega = Usuario(
        id_usuario=2, id_rol=2, nombre_completo="Bodeguero Traslados",
        username="bodega_traslado", password_hash=security.get_password_hash("pass123"), estado="Activo"
    )
    user_cajera = Usuario(
        id_usuario=3, id_rol=3, nombre_completo="Cajera Traslados",
        username="cajera_traslado", password_hash=security.get_password_hash("pass123"), estado="Activo"
    )
    db_session.add_all([user_admin, user_bodega, user_cajera])
    await db_session.flush()

    # Sucursales (Origen: 1, Destino: 2)
    suc1 = Sucursal(id_sucursal=1, nombre="Sucursal Central", direccion="Zona 1", estado="Activo")
    suc2 = Sucursal(id_sucursal=2, nombre="Sucursal Norte", direccion="Zona 18", estado="Activo")
    cat = Categoria(id_categoria=1, nombre="Cat General", estado="Activo")
    subcat = Subcategoria(id_subcategoria=1, id_categoria=1, nombre="Subcat Gen", estado="Activo")
    unidad = UnidadMedida(id_unidad=1, codigo="UND", descripcion="Unidad", estado="Activo")
    db_session.add_all([suc1, suc2, cat, subcat, unidad])
    await db_session.flush()

    prod = Producto(id_producto=1, id_subcategoria=1, id_unidad=1, nombre="Caja de Lapiceros", estado="Activo")
    db_session.add(prod)
    await db_session.flush()

    var = VarianteProducto(
        id_variante=1, id_producto=1, codigo_barras="740999001",
        costo_promedio=Decimal("10.00"),
        precio_detalle=Decimal("15.00"), precio_mayoreo=Decimal("12.00")
    )
    db_session.add(var)
    await db_session.flush()

    # Inventario inicial: Sucursal 1 tiene 20, Sucursal 2 tiene 5
    inv1 = InventarioSucursal(id_inventario=1, id_variante=1, id_sucursal=1, stock_actual=20, stock_minimo=5, fecha_actualizacion=datetime.utcnow())
    inv2 = InventarioSucursal(id_inventario=2, id_variante=1, id_sucursal=2, stock_actual=5, stock_minimo=5, fecha_actualizacion=datetime.utcnow())
    db_session.add_all([inv1, inv2])
    await db_session.commit()

    return {
        "admin_id": 1,
        "bodega_id": 2,
        "cajera_id": 3,
        "suc1": 1,
        "suc2": 2,
        "variante": 1,
        "admin_token": security.create_access_token({"sub": "admin_traslado"}),
        "cajera_token": security.create_access_token({"sub": "cajera_traslado"}),
        "bodega_token": security.create_access_token({"sub": "bodega_traslado"}),
    }


# =========================================================================
# PRUEBAS UNITARIAS DE SERVICIO
# =========================================================================

@pytest.mark.asyncio
async def test_crear_traslado_exito_descuenta_origen(uow, db_session):
    ctx = await seed_traslado_data(db_session)
    service = ConcreteTrasladoService(uow)

    payload = TrasladoCreate(
        id_sucursal_origen=ctx["suc1"],
        id_sucursal_destino=ctx["suc2"],
        id_variante=ctx["variante"],
        cantidad=8,
        observaciones="Traslado de prueba por alta demanda"
    )

    traslado = await service.crear_envio(payload, user_id=ctx["bodega_id"])

    assert traslado.id_traslado is not None
    assert traslado.estado == "En tránsito"
    assert traslado.cantidad == 8
    assert traslado.id_usuario_envia == ctx["bodega_id"]

    # Verificar descuento estricto en inventario origen (20 - 8 = 12)
    inv_origen = await db_session.get(InventarioSucursal, 1)
    assert inv_origen.stock_actual == 12

    # Verificar que el destino NO ha recibido todavía (sigue en 5)
    inv_destino = await db_session.get(InventarioSucursal, 2)
    assert inv_destino.stock_actual == 5

    # Verificar bitácora de auditoría con acción CREAR
    stmt = select(BitacoraAuditoria).where(BitacoraAuditoria.tabla_afectada == "traslado_inventario", BitacoraAuditoria.accion == "CREAR")
    logs = (await db_session.execute(stmt)).scalars().all()
    assert len(logs) >= 1


@pytest.mark.asyncio
async def test_crear_traslado_stock_insuficiente_falla(uow, db_session):
    ctx = await seed_traslado_data(db_session)
    service = ConcreteTrasladoService(uow)

    payload = TrasladoCreate(
        id_sucursal_origen=ctx["suc1"],
        id_sucursal_destino=ctx["suc2"],
        id_variante=ctx["variante"],
        cantidad=25,  # Disponible: 20
        observaciones="Exceso"
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.crear_envio(payload, user_id=ctx["bodega_id"])

    assert exc_info.value.status_code == 400
    assert "Stock insuficiente" in exc_info.value.detail

    # Stock intacto
    inv_origen = await db_session.get(InventarioSucursal, 1)
    assert inv_origen.stock_actual == 20


@pytest.mark.asyncio
async def test_crear_traslado_mismas_sucursales_falla(uow, db_session):
    ctx = await seed_traslado_data(db_session)
    service = ConcreteTrasladoService(uow)

    payload = TrasladoCreate(
        id_sucursal_origen=ctx["suc1"],
        id_sucursal_destino=ctx["suc1"],
        id_variante=ctx["variante"],
        cantidad=2,
    )

    with pytest.raises(HTTPException) as exc_info:
        await service.crear_envio(payload, user_id=ctx["bodega_id"])

    assert exc_info.value.status_code == 400
    assert "distintas" in exc_info.value.detail


@pytest.mark.asyncio
async def test_recibir_traslado_exito_suma_destino(uow, db_session):
    ctx = await seed_traslado_data(db_session)
    service = ConcreteTrasladoService(uow)

    # 1. Enviar 6 unidades
    payload = TrasladoCreate(
        id_sucursal_origen=ctx["suc1"],
        id_sucursal_destino=ctx["suc2"],
        id_variante=ctx["variante"],
        cantidad=6,
    )
    t = await service.crear_envio(payload, user_id=ctx["admin_id"])

    # 2. Recibir en destino
    recibido = await service.recibir_traslado(t.id_traslado, user_id=ctx["bodega_id"])

    assert recibido.estado == "Recibido"
    assert recibido.id_usuario_recibe == ctx["bodega_id"]
    assert recibido.fecha_recepcion is not None

    # Destino incrementado: 5 + 6 = 11
    inv_destino = await db_session.get(InventarioSucursal, 2)
    assert inv_destino.stock_actual == 11

    # Bitácora registrada con acción EDITAR
    stmt = select(BitacoraAuditoria).where(BitacoraAuditoria.tabla_afectada == "traslado_inventario", BitacoraAuditoria.accion == "EDITAR")
    logs = (await db_session.execute(stmt)).scalars().all()
    assert any("Recepción" in l.descripcion for l in logs)


@pytest.mark.asyncio
async def test_cancelar_traslado_exito_devuelve_origen(uow, db_session):
    ctx = await seed_traslado_data(db_session)
    service = ConcreteTrasladoService(uow)

    # 1. Enviar 5 unidades (Origen pasa de 20 a 15)
    payload = TrasladoCreate(
        id_sucursal_origen=ctx["suc1"],
        id_sucursal_destino=ctx["suc2"],
        id_variante=ctx["variante"],
        cantidad=5,
    )
    t = await service.crear_envio(payload, user_id=ctx["bodega_id"])

    inv_origen = await db_session.get(InventarioSucursal, 1)
    assert inv_origen.stock_actual == 15

    # 2. Cancelar el traslado
    cancelado = await service.cancelar_traslado(t.id_traslado, user_id=ctx["admin_id"], motivo="Error en despacho")

    assert cancelado.estado == "Cancelado"
    assert "Error en despacho" in (cancelado.observaciones or "")

    # Stock en origen devuelto a 20!
    inv_origen_rest = await db_session.get(InventarioSucursal, 1)
    assert inv_origen_rest.stock_actual == 20

    # Destino permanece en 5
    inv_destino = await db_session.get(InventarioSucursal, 2)
    assert inv_destino.stock_actual == 5


@pytest.mark.asyncio
async def test_recibir_o_cancelar_traslado_invalido_falla(uow, db_session):
    ctx = await seed_traslado_data(db_session)
    service = ConcreteTrasladoService(uow)

    payload = TrasladoCreate(
        id_sucursal_origen=ctx["suc1"],
        id_sucursal_destino=ctx["suc2"],
        id_variante=ctx["variante"],
        cantidad=3,
    )
    t = await service.crear_envio(payload, user_id=ctx["bodega_id"])
    await service.recibir_traslado(t.id_traslado, user_id=ctx["admin_id"])

    # No se puede recibir de nuevo una orden ya Recibida
    with pytest.raises(HTTPException) as exc1:
        await service.recibir_traslado(t.id_traslado, user_id=ctx["admin_id"])
    assert exc1.value.status_code == 400

    # No se puede cancelar una orden ya Recibida
    with pytest.raises(HTTPException) as exc2:
        await service.cancelar_traslado(t.id_traslado, user_id=ctx["admin_id"])
    assert exc2.value.status_code == 400


# =========================================================================
# PRUEBAS DE INTEGRACIÓN API
# =========================================================================

@pytest.mark.asyncio
async def test_traslados_api_flujo_completo(client, db_session):
    ctx = await seed_traslado_data(db_session)
    admin_headers = {"Authorization": f"Bearer {ctx['admin_token']}"}

    # 1. POST /api/traslados (Despacho)
    payload = {
        "id_sucursal_origen": ctx["suc1"],
        "id_sucursal_destino": ctx["suc2"],
        "id_variante": ctx["variante"],
        "cantidad": 7,
        "observaciones": "Envío regular",
    }
    r_create = await client.post("/api/traslados", json=payload, headers=admin_headers)
    assert r_create.status_code == 201
    t_data = r_create.json()
    assert t_data["estado"] == "En tránsito"
    id_traslado = t_data["id_traslado"]

    # 2. GET /api/traslados?estado=En tránsito
    r_list = await client.get("/api/traslados?estado=En tránsito", headers=admin_headers)
    assert r_list.status_code == 200
    assert any(x["id_traslado"] == id_traslado for x in r_list.json())

    # 3. POST /api/traslados/{id}/recibir
    r_recibir = await client.post(f"/api/traslados/{id_traslado}/recibir", headers=admin_headers)
    assert r_recibir.status_code == 200
    assert r_recibir.json()["estado"] == "Recibido"

    # Verificar stock en destino (5 + 7 = 12)
    inv_dst = await db_session.get(InventarioSucursal, 2)
    assert inv_dst.stock_actual == 12


@pytest.mark.asyncio
async def test_traslados_api_403_cajera(client, db_session):
    ctx = await seed_traslado_data(db_session)
    cajera_headers = {"Authorization": f"Bearer {ctx['cajera_token']}"}

    payload = {
        "id_sucursal_origen": ctx["suc1"],
        "id_sucursal_destino": ctx["suc2"],
        "id_variante": ctx["variante"],
        "cantidad": 2,
    }

    # Despachar
    r_create = await client.post("/api/traslados", json=payload, headers=cajera_headers)
    assert r_create.status_code == 403

    # Listar
    r_list = await client.get("/api/traslados", headers=cajera_headers)
    assert r_list.status_code == 403

    # Recibir
    r_rec = await client.post("/api/traslados/1/recibir", headers=cajera_headers)
    assert r_rec.status_code == 403

    # Cancelar
    r_canc = await client.post("/api/traslados/1/cancelar", json={}, headers=cajera_headers)
    assert r_canc.status_code == 403

