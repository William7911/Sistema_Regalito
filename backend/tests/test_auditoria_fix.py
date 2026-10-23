"""Pruebas de la corrección de auditoría del Bloque 4.

Verifica que los servicios de escritura que NO registraban en la bitácora de
auditoría ahora registren sus acciones (rol, rol_permiso, categoría,
departamento, orden de compra y configuración).
"""
import pytest
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy import select, func

from app.db.models import (
    Rol, Usuario, Categoria, DepartamentoGeografico, Proveedor, Producto,
    Subcategoria, UnidadMedida, VarianteProducto, ParametroSistema,
    Permiso, BitacoraAuditoria, OrdenCompra,
)
from app.repositories.category_repository import CategoryRepositoryImpl
from app.services.category_service import ConcreteCategoryService
from app.services.department_service import ConcreteDepartmentService
from app.services.role_service import ConcreteRoleService
from app.services.configuracion_service import ConfiguracionService
from app.services.compra_service import ConcreteComprasService
from app.schemas import schemas
from app.schemas.compras_schema import (
    OrdenCompraCreate, DetalleOrdenCompraCreate,
)


async def _crear_usuario(db, nombre="Actor", username="actor_aud", id_rol=None):
    rol = None
    if id_rol is None:
        rol = Rol(nombre="Administradora", estado="Activo")
        db.add(rol)
        await db.flush()
        id_rol = rol.id_rol
    user = Usuario(nombre_completo=nombre, username=username, id_rol=id_rol,
                   password_hash="x", estado="Activo")
    db.add(user)
    await db.flush()
    return user


async def _contar_bitacora(db, tabla, accion):
    n = (await db.execute(
        select(func.count()).select_from(BitacoraAuditoria).where(
            BitacoraAuditoria.tabla_afectada == tabla,
            BitacoraAuditoria.accion == accion,
        )
    )).scalar_one()
    return n


# ---------------------------------------------------------------------------
# Categorías
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_categoria_create_registra_bitacora(db_session):
    repo = CategoryRepositoryImpl(db_session)
    svc = ConcreteCategoryService(repo)
    user = await _crear_usuario(db_session, username="cat_aud")

    await svc.create_category(schemas.CategoriaCreate(nombre="Categoria Auditada"), actor_id=user.id_usuario)

    assert await _contar_bitacora(db_session, "categoria", "CREATE") == 1


@pytest.mark.asyncio
async def test_categoria_update_registra_bitacora(db_session):
    repo = CategoryRepositoryImpl(db_session)
    svc = ConcreteCategoryService(repo)
    user = await _crear_usuario(db_session, username="cat_upd")

    cat = await svc.create_category(schemas.CategoriaCreate(nombre="Cat Original"), actor_id=user.id_usuario)
    await svc.update_category(cat.id_categoria, schemas.CategoriaUpdate(nombre="Cat Editada"), actor_id=user.id_usuario)

    assert await _contar_bitacora(db_session, "categoria", "UPDATE") == 1


@pytest.mark.asyncio
async def test_categoria_deactivate_registra_bitacora(db_session):
    repo = CategoryRepositoryImpl(db_session)
    svc = ConcreteCategoryService(repo)
    user = await _crear_usuario(db_session, username="cat_del")

    cat = await svc.create_category(schemas.CategoriaCreate(nombre="Cat Desactivar"), actor_id=user.id_usuario)
    await svc.deactivate_category(cat.id_categoria, actor_id=user.id_usuario)

    assert await _contar_bitacora(db_session, "categoria", "DEACTIVATE") == 1


# ---------------------------------------------------------------------------
# Departamentos
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_departamento_create_registra_bitacora(uow, db_session):
    svc = ConcreteDepartmentService(uow)
    user = await _crear_usuario(db_session, username="dep_aud")

    await svc.create_department(schemas.DepartmentCreate(nombre="Depto Auditado"), actor_id=user.id_usuario)

    assert await _contar_bitacora(db_session, "departamento_geografico", "CREATE") == 1


@pytest.mark.asyncio
async def test_departamento_update_registra_bitacora(uow, db_session):
    svc = ConcreteDepartmentService(uow)
    user = await _crear_usuario(db_session, username="dep_upd")

    dep = await svc.create_department(schemas.DepartmentCreate(nombre="Depto A"), actor_id=user.id_usuario)
    await svc.update_department(dep.id_departamento, schemas.DepartmentUpdate(nombre="Depto B"), actor_id=user.id_usuario)

    assert await _contar_bitacora(db_session, "departamento_geografico", "UPDATE") == 1


# ---------------------------------------------------------------------------
# Roles / rol_permiso
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rol_permisos_update_registra_bitacora(uow, db_session):
    svc = ConcreteRoleService(uow)
    user = await _crear_usuario(db_session, username="rp_aud")

    rol = await svc.create_role(schemas.RoleCreate(nombre="Rol Permisos Auditado"))
    permiso = Permiso(modulo="Ventas", codigo="VENTA_COBRAR", descripcion="cobrar")
    db_session.add(permiso)
    await db_session.commit()

    await svc.update_rol_permisos(rol.id_rol, ["VENTA_COBRAR"], actor_id=user.id_usuario)

    assert await _contar_bitacora(db_session, "rol_permiso", "UPDATE") == 1


# ---------------------------------------------------------------------------
# Órdenes de compra
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_compras_crear_orden_registra_bitacora(uow, db_session):
    rol = Rol(nombre="Administradora", estado="Activo")
    db_session.add(rol)
    await db_session.flush()
    usuario = Usuario(nombre_completo="Admin Compras", username="admin_compras_aud",
                      id_rol=rol.id_rol, password_hash="x", estado="Activo")
    db_session.add(usuario)
    await db_session.flush()

    proveedor = Proveedor(nombre_contacto="John", distribuidora="Distribuidora Aud")
    db_session.add(proveedor)
    await db_session.flush()
    cat = Categoria(nombre="Cat Aud", estado="Activo")
    db_session.add(cat)
    await db_session.flush()
    sub = Subcategoria(id_categoria=cat.id_categoria, nombre="Sub Aud", estado="Activo")
    db_session.add(sub)
    await db_session.flush()
    uni = UnidadMedida(codigo="UDA", descripcion="Unidad Aud", estado="Activo")
    db_session.add(uni)
    await db_session.flush()
    prod = Producto(id_subcategoria=sub.id_subcategoria, id_unidad=uni.id_unidad,
                    nombre="Producto Aud", estado="Activo")
    db_session.add(prod)
    await db_session.flush()
    var = VarianteProducto(id_producto=prod.id_producto, precio_detalle=Decimal("10"),
                           precio_mayoreo=Decimal("8"), costo_promedio=Decimal("5"))
    db_session.add(var)
    await db_session.commit()

    svc = ConcreteComprasService(uow)
    await svc.crear_orden(
        OrdenCompraCreate(
            id_proveedor=proveedor.id_proveedor,
            detalles=[DetalleOrdenCompraCreate(id_variante=var.id_variante, cantidad_pedida=5, costo_pactado=Decimal("5.00"))],
        ),
        user_id=usuario.id_usuario,
    )

    assert await _contar_bitacora(db_session, "orden_compra", "CREATE") == 1


# ---------------------------------------------------------------------------
# Configuración (parametros del sistema)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_configuracion_actualizar_registra_bitacora(uow, db_session):
    usuario = await _crear_usuario(db_session, username="cfg_aud")
    param = ParametroSistema(clave="IVA_PORCENTAJE", valor="12")
    db_session.add(param)
    await db_session.commit()

    svc = ConfiguracionService(uow)
    await svc.actualizar_configuracion({"IVA_PORCENTAJE": "12", "NIT_EMPRESA": "12345678-9"}, usuario_actual=usuario)

    assert await _contar_bitacora(db_session, "parametro_sistema", "UPDATE") == 1
