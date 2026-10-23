import pytest
from fastapi import HTTPException
from sqlalchemy import select, func
from app.db.models import Permiso, BitacoraAuditoria
from app.services.role_service import ConcreteRoleService
from app.schemas import schemas


def service(uow):
    return ConcreteRoleService(uow)


@pytest.mark.asyncio
async def test_list_permisos(uow):
    uow.db.add_all([
        Permiso(modulo="Ventas", codigo="VENTA_COBRAR", descripcion="Registrar cobros"),
        Permiso(modulo="Seguridad", codigo="BITACORA_CONSULTAR", descripcion="Ver bitácora"),
        Permiso(modulo="Catálogo", codigo="CATALOGO_ADMIN", descripcion="Gestionar catálogos"),
    ])
    await uow.db.commit()

    permisos = await service(uow).list_permisos()
    codigos = [p.codigo for p in permisos]
    assert "VENTA_COBRAR" in codigos
    assert "BITACORA_CONSULTAR" in codigos
    assert "CATALOGO_ADMIN" in codigos
    assert all(p.modulo for p in permisos)


@pytest.mark.asyncio
async def test_get_rol_permisos_regresa_codigos_asignados(uow):
    rol = await service(uow).create_role(schemas.RoleCreate(nombre="Cajero"))
    p1 = Permiso(modulo="Ventas", codigo="VENTA_COBRAR", descripcion="cobrar")
    p2 = Permiso(modulo="Ventas", codigo="VENTA_APLICAR_DESCUENTO", descripcion="descuento")
    uow.db.add_all([p1, p2])
    await uow.db.commit()

    await service(uow).update_rol_permisos(rol.id_rol, ["VENTA_COBRAR", "VENTA_APLICAR_DESCUENTO"])
    codigos = await service(uow).get_rol_permisos(rol.id_rol)
    assert codigos == ["VENTA_APLICAR_DESCUENTO", "VENTA_COBRAR"]


@pytest.mark.asyncio
async def test_update_rol_permisos_reemplaza_conjunto(uow):
    svc = service(uow)
    rol = await svc.create_role(schemas.RoleCreate(nombre="Encargado"))
    perms = [
        Permiso(modulo="Ventas", codigo="VENTA_COBRAR", descripcion="cobrar"),
        Permiso(modulo="Ventas", codigo="VENTA_APLICAR_DESCUENTO", descripcion="descuento"),
        Permiso(modulo="Compras", codigo="COMPRA_EMITIR_ORDEN", descripcion="compras"),
    ]
    uow.db.add_all(perms)
    await uow.db.commit()

    await svc.update_rol_permisos(rol.id_rol, ["VENTA_COBRAR", "COMPRA_EMITIR_ORDEN"])
    codigos = await svc.get_rol_permisos(rol.id_rol)
    assert codigos == ["COMPRA_EMITIR_ORDEN", "VENTA_COBRAR"]

    # Quitar uno y dejar sólo COMPRA_EMITIR_ORDEN
    await svc.update_rol_permisos(rol.id_rol, ["COMPRA_EMITIR_ORDEN"])
    codigos = await svc.get_rol_permisos(rol.id_rol)
    assert codigos == ["COMPRA_EMITIR_ORDEN"]


@pytest.mark.asyncio
async def test_update_rol_permisos_con_codigo_inexistente_lanza_400(uow):
    svc = service(uow)
    rol = await svc.create_role(schemas.RoleCreate(nombre="Rol Sin Permisos"))
    with pytest.raises(HTTPException) as exc:
        await svc.update_rol_permisos(rol.id_rol, ["PERMISO_FANTASMA"])
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_update_rol_permisos_rol_inexistente_404(uow):
    with pytest.raises(HTTPException) as exc:
        await service(uow).update_rol_permisos(9999, [])
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_rol_permisos_limpiar_todo(uow):
    svc = service(uow)
    rol = await svc.create_role(schemas.RoleCreate(nombre="Rol Limpio"))
    perm = Permiso(modulo="Ventas", codigo="VENTA_COBRAR", descripcion="cobrar")
    uow.db.add(perm)
    await uow.db.commit()

    await svc.update_rol_permisos(rol.id_rol, ["VENTA_COBRAR"])
    assert await svc.get_rol_permisos(rol.id_rol) == ["VENTA_COBRAR"]

    await svc.update_rol_permisos(rol.id_rol, [])
    assert await svc.get_rol_permisos(rol.id_rol) == []


@pytest.mark.asyncio
async def test_create_rol_registra_bitacora(uow):
    svc = service(uow)
    usuario = __import__("app.db.models", fromlist=["Usuario"]).Usuario(
        id_rol=1, nombre_completo="Auditor Prueba", username="auditor_prueba",
        password_hash="x", estado="Activo",
    )
    uow.db.add(usuario)
    await uow.db.commit()

    await svc.create_role(schemas.RoleCreate(nombre="Rol Auditado"), actor_id=usuario.id_usuario)

    conteo = (await uow.db.execute(
        select(func.count()).select_from(BitacoraAuditoria)
        .where(BitacoraAuditoria.accion == "CREATE", BitacoraAuditoria.tabla_afectada == "rol")
    )).scalar_one()
    assert conteo == 1
