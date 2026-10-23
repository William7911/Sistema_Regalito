import pytest
from fastapi import HTTPException
from app.services.role_service import ConcreteRoleService
from app.schemas import schemas


def service(uow):
    return ConcreteRoleService(uow)


@pytest.mark.asyncio
async def test_crear_y_obtener_rol(uow):
    creado = await service(uow).create_role(
        schemas.RoleCreate(nombre="Cajero", descripcion="Atención en caja")
    )
    assert creado.id_rol is not None
    assert creado.nombre == "Cajero"
    assert creado.estado == "Activo"

    obtenido = await service(uow).get_role(creado.id_rol)
    assert obtenido.id_rol == creado.id_rol
    assert obtenido.nombre == "Cajero"


@pytest.mark.asyncio
async def test_rol_duplicado_rechazado(uow):
    svc = service(uow)
    await svc.create_role(schemas.RoleCreate(nombre="Supervisor"))
    with pytest.raises(HTTPException) as exc:
        await svc.create_role(schemas.RoleCreate(nombre="Supervisor"))
    assert exc.value.status_code == 400
    assert "Ya existe" in exc.value.detail


@pytest.mark.asyncio
async def test_obtener_rol_inexistente_404(uow):
    with pytest.raises(HTTPException) as exc:
        await service(uow).get_role(9999)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_actualizar_rol(uow):
    svc = service(uow)
    creado = await svc.create_role(schemas.RoleCreate(nombre="Bodeguero"))
    actualizado = await svc.update_role(
        creado.id_rol, schemas.RoleUpdate(nombre="Encargado Bodega", descripcion="Logística")
    )
    assert actualizado.nombre == "Encargado Bodega"
    assert actualizado.descripcion == "Logística"


@pytest.mark.asyncio
async def test_desactivar_rol_soft_delete(uow):
    svc = service(uow)
    rol_a = await svc.create_role(schemas.RoleCreate(nombre="Rol A"))
    rol_b = await svc.create_role(schemas.RoleCreate(nombre="Rol B"))

    await svc.deactivate_role(rol_a.id_rol)

    activos = await svc.list_roles(include_inactive=False)
    nombres_activos = [r.nombre for r in activos]
    assert "Rol A" not in nombres_activos
    assert "Rol B" in nombres_activos

    todos = await svc.list_roles(include_inactive=True)
    nombres_todos = [r.nombre for r in todos]
    assert "Rol A" in nombres_todos
    assert "Rol B" in nombres_todos

