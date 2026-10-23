import os
import pytest
from decimal import Decimal
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import (
    Base, Rol, Usuario, Permiso, RolPermiso,
    Categoria, Subcategoria, UnidadMedida,
    Producto, VarianteProducto, InventarioSucursal,
    Sucursal, Caja, MetodoPago, TipoCliente, Cliente,
    SyncCacheMetadata,
)
from app.repositories.sync_repository import SyncRepositoryImpl
from app.services.sync_service import ConcreteSyncService


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def _seed_sync_test_data(db):
    rol = Rol(nombre="Administradora", estado="Activo")
    db.add(rol)
    await db.flush()

    user = Usuario(
        id_rol=rol.id_rol,
        nombre_completo="Admin Test",
        username="admin_sync",
        password_hash=security.get_password_hash("pass123"),
        estado="Activo",
    )
    db.add(user)

    permiso = Permiso(modulo="Catálogo", codigo="CAT_EDITAR", descripcion="Editar catálogo")
    db.add(permiso)
    await db.flush()

    db.add(RolPermiso(id_rol=rol.id_rol, id_permiso=permiso.id_permiso))

    sucursal = Sucursal(nombre="Sucursal Lago", direccion="Panajachel", estado="Activo")
    db.add(sucursal)
    await db.flush()

    caja = Caja(id_sucursal=sucursal.id_sucursal, descripcion="Caja 1", estado="Activa")
    db.add(caja)

    cat = Categoria(nombre="Ropa Niña", estado="Activo")
    db.add(cat)
    await db.flush()

    subcat = Subcategoria(id_categoria=cat.id_categoria, nombre="Vestidos")
    db.add(subcat)

    unidad = UnidadMedida(codigo="PZA", descripcion="Pieza")
    db.add(unidad)
    await db.flush()

    prod = Producto(
        id_subcategoria=subcat.id_subcategoria,
        id_unidad=unidad.id_unidad,
        nombre="Vestido Floreado 4T",
        descripcion="Vestido de fiesta",
        estado="Activo",
    )
    db.add(prod)
    await db.flush()

    var = VarianteProducto(
        id_producto=prod.id_producto,
        codigo_barras="740100999901",
        talla="4T",
        color="Rosa",
        precio_detalle=Decimal("125.50"),
        precio_mayoreo=Decimal("110.00"),
        costo_promedio=Decimal("75.00"),
    )
    db.add(var)
    await db.flush()

    inv = InventarioSucursal(
        id_variante=var.id_variante,
        id_sucursal=sucursal.id_sucursal,
        stock_actual=15,
        stock_minimo=3,
    )
    db.add(inv)
    await db.commit()
    return user, prod, var


@pytest.mark.asyncio
async def test_sync_repository_fetch_snapshot(db_session):
    """Verifica que el repositorio extraiga correctamente todas las entidades de catálogo, precios y usuarios."""
    await _seed_sync_test_data(db_session)

    repo = SyncRepositoryImpl(db_session)
    snapshot = await repo.fetch_cloud_snapshot()

    assert len(snapshot["rol"]) >= 1
    assert len(snapshot["usuario"]) >= 1
    assert len(snapshot["producto"]) >= 1
    assert len(snapshot["variante_producto"]) >= 1

    var = snapshot["variante_producto"][0]
    assert var["precio_detalle"] == Decimal("125.50")
    assert var["precio_mayoreo"] == Decimal("110.00")
    assert var["codigo_barras"] == "740100999901"


@pytest.mark.asyncio
async def test_sync_repository_replicate_to_sqlite(db_session, tmp_path):
    """Verifica que el snapshot se replique y persista íntegramente en un archivo SQLite local."""
    await _seed_sync_test_data(db_session)

    db_file = str(tmp_path / "test_local.db")
    sqlite_url = f"sqlite+aiosqlite:///{db_file}"

    repo = SyncRepositoryImpl(db_session, sqlite_url=sqlite_url, sqlite_path=db_file)
    snapshot = await repo.fetch_cloud_snapshot()
    result = await repo.replicate_to_sqlite(snapshot)

    assert result["status"] == "success"
    assert result["counts"]["producto"] >= 1
    assert result["counts"]["variante_producto"] >= 1
    assert result["counts"]["usuario"] >= 1

    # Verificar directamente en la base SQLite local creada
    local_engine = create_async_engine(sqlite_url)
    session_maker = async_sessionmaker(local_engine)

    async with session_maker() as s:
        res_prod = await s.execute(select(Producto))
        prods = res_prod.scalars().all()
        assert len(prods) >= 1
        assert prods[0].nombre == "Vestido Floreado 4T"

        res_var = await s.execute(select(VarianteProducto))
        vars_local = res_var.scalars().all()
        assert len(vars_local) >= 1
        assert float(vars_local[0].precio_detalle) == 125.50
        assert float(vars_local[0].precio_mayoreo) == 110.00

        res_user = await s.execute(select(Usuario))
        users_local = res_user.scalars().all()
        assert len(users_local) >= 1
        assert users_local[0].username == "admin_sync"

        res_meta = await s.execute(select(SyncCacheMetadata))
        meta = res_meta.scalars().all()
        assert len(meta) > 0


@pytest.mark.asyncio
async def test_sync_service_status_and_preview(db_session, tmp_path):
    """Verifica los métodos de consulta de estado y preview del servicio de sincronización."""
    await _seed_sync_test_data(db_session)

    db_file = str(tmp_path / "test_local_service.db")
    sqlite_url = f"sqlite+aiosqlite:///{db_file}"

    repo = SyncRepositoryImpl(db_session, sqlite_url=sqlite_url, sqlite_path=db_file)
    service = ConcreteSyncService(repo)

    # Estado previo a sincronización
    status_pre = await service.get_sync_status()
    assert status_pre["file_exists"] is False

    # Ejecutar réplica
    sync_res = await service.pull_and_replicate_to_local()
    assert sync_res["status"] == "success"

    # Estado posterior
    status_post = await service.get_sync_status()
    assert status_post["file_exists"] is True
    assert status_post["initialized"] is True
    assert status_post["counts"]["productos"] >= 1
    assert status_post["counts"]["usuarios"] >= 1

    # Previsualización
    preview = await service.get_local_preview()
    assert len(preview["productos"]) >= 1
    assert preview["productos"][0]["nombre"] == "Vestido Floreado 4T"
    assert preview["productos"][0]["precio_detalle"] == 125.50
    assert preview["productos"][0]["precio_mayoreo"] == 110.00

    assert len(preview["usuarios"]) >= 1
    assert preview["usuarios"][0]["username"] == "admin_sync"


@pytest.mark.asyncio
async def test_sync_api_endpoints(client, db_session):
    """Verifica los endpoints REST /api/sync/* consumidos por el frontend."""
    user, _, _ = await _seed_sync_test_data(db_session)

    token = security.create_access_token(
        data={"sub": user.username, "role": "Administradora", "permissions": []}
    )
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Pull / Replicate
    resp_pull = await client.post("/api/sync/pull-local", headers=headers)
    assert resp_pull.status_code == 200
    data_pull = resp_pull.json()
    assert data_pull["status"] == "success"
    assert "counts" in data_pull

    # 2. Status
    resp_status = await client.get("/api/sync/status", headers=headers)
    assert resp_status.status_code == 200
    data_status = resp_status.json()
    assert data_status["file_exists"] is True
    assert data_status["initialized"] is True

    # 3. Preview
    resp_prev = await client.get("/api/sync/local-preview", headers=headers)
    assert resp_prev.status_code == 200
    data_prev = resp_prev.json()
    assert len(data_prev["productos"]) >= 1
    assert len(data_prev["usuarios"]) >= 1

