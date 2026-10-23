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


@pytest.mark.asyncio
async def test_administradora_no_puede_perder_permisos_criticos(uow):
    svc = service(uow)
    rol_admin = await svc.create_role(schemas.RoleCreate(nombre="Administradora"))
    p_rol = Permiso(modulo="Seguridad", codigo="ROL_ADMIN", descripcion="Roles")
    p_usr = Permiso(modulo="Seguridad", codigo="USUARIO_ADMIN", descripcion="Usuarios")
    p_vta = Permiso(modulo="Ventas", codigo="VENTA_COBRAR", descripcion="Cobro")
    uow.db.add_all([p_rol, p_usr, p_vta])
    await uow.db.commit()

    # Intento de asignar solo VENTA_COBRAR sin los permisos críticos
    with pytest.raises(HTTPException) as exc:
        await svc.update_rol_permisos(rol_admin.id_rol, ["VENTA_COBRAR"])
    assert exc.value.status_code == 400
    assert "El rol Administradora no puede perder los permisos críticos" in exc.value.detail

    # Con ambos permisos críticos sí procede
    cods = await svc.update_rol_permisos(rol_admin.id_rol, ["ROL_ADMIN", "USUARIO_ADMIN", "VENTA_COBRAR"])
    assert "ROL_ADMIN" in cods
    assert "USUARIO_ADMIN" in cods


@pytest.mark.asyncio
async def test_usuario_no_puede_quitarse_a_si_mismo_acceso_roles(uow):
    from app.db.models import Usuario
    svc = service(uow)
    rol_sup = await svc.create_role(schemas.RoleCreate(nombre="Supervisor"))
    user = Usuario(
        id_rol=rol_sup.id_rol, nombre_completo="Sup User", username="sup_user",
        password_hash="x", estado="Activo",
    )
    uow.db.add(user)
    p_rol = Permiso(modulo="Seguridad", codigo="ROL_ADMIN", descripcion="Roles")
    p_vta = Permiso(modulo="Ventas", codigo="VENTA_COBRAR", descripcion="Cobro")
    uow.db.add_all([p_rol, p_vta])
    await uow.db.commit()

    # Usuario intentando quitar ROL_ADMIN de su propio rol
    with pytest.raises(HTTPException) as exc:
        await svc.update_rol_permisos(rol_sup.id_rol, ["VENTA_COBRAR"], actor_id=user.id_usuario)
    assert exc.value.status_code == 400
    assert "No puedes quitarte a ti mismo el acceso al módulo de Roles" in exc.value.detail


@pytest.mark.asyncio
async def test_no_se_puede_desactivar_rol_administradora_ni_propio_rol(uow):
    from app.db.models import Usuario
    svc = service(uow)
    rol_admin = await svc.create_role(schemas.RoleCreate(nombre="Administradora"))
    rol_cajero = await svc.create_role(schemas.RoleCreate(nombre="Cajero Especial"))
    user_cajero = Usuario(
        id_rol=rol_cajero.id_rol, nombre_completo="Cajero Test", username="cajero_test",
        password_hash="x", estado="Activo",
    )
    uow.db.add(user_cajero)
    await uow.db.commit()

    # No se puede desactivar Administradora
    with pytest.raises(HTTPException) as exc1:
        await svc.deactivate_role(rol_admin.id_rol)
    assert exc1.value.status_code == 400
    assert "No se puede desactivar el rol Administradora" in exc1.value.detail

    # No puede desactivar su propio rol
    with pytest.raises(HTTPException) as exc2:
        await svc.deactivate_role(rol_cajero.id_rol, actor_id=user_cajero.id_usuario)
    assert exc2.value.status_code == 400
    assert "No puedes desactivar tu propio rol" in exc2.value.detail
