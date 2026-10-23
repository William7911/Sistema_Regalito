import pytest
from fastapi import HTTPException
from app.db.models import Rol
from app.services.user_service import ConcreteUserService
from app.schemas import schemas


def service(uow):
    return ConcreteUserService(uow)


async def seed_role(uow, nombre="Cajero", estado="Activo"):
    rol = Rol(nombre=nombre, estado=estado)
    created = await uow.roles.create(rol)
    await uow.commit()
    return created.id_rol


def make_user(id_rol, username="jperez", nombre="Juan Pérez", password="secreto123"):
    return schemas.UserCreate(
        nombre_completo=nombre,
        username=username,
        password=password,
        id_rol=id_rol,
    )


@pytest.mark.asyncio
async def test_crear_usuario_exitoso(uow):
    id_rol = await seed_role(uow)
    creado = await service(uow).create_user(make_user(id_rol))
    assert creado.id_usuario is not None
    assert creado.username == "jperez"
    assert creado.nombre_completo == "Juan Pérez"
    assert creado.estado == "Activo"
    assert creado.rol is not None
    assert creado.rol.nombre == "Cajero"


@pytest.mark.asyncio
async def test_crear_usuario_requiere_rol_valido(uow):
    svc = service(uow)
    with pytest.raises(HTTPException) as exc:
        await svc.create_user(make_user(id_rol=9999))
    assert exc.value.status_code == 400
    assert "no existe" in exc.value.detail


@pytest.mark.asyncio
async def test_crear_usuario_rechaza_rol_inactivo(uow):
    id_rol = await seed_role(uow, nombre="Rol Inactivo", estado="Inactivo")
    svc = service(uow)
    with pytest.raises(HTTPException) as exc:
        await svc.create_user(make_user(id_rol=id_rol))
    assert exc.value.status_code == 400
    assert "inactivo" in exc.value.detail


@pytest.mark.asyncio
async def test_nombre_usuario_duplicado_rechazado(uow):
    id_rol = await seed_role(uow)
    svc = service(uow)
    await svc.create_user(make_user(id_rol, username="duplicado"))
    with pytest.raises(HTTPException) as exc:
        await svc.create_user(make_user(id_rol, username="duplicado"))
    assert exc.value.status_code == 400
    assert "Ya existe" in exc.value.detail


@pytest.mark.asyncio
async def test_obtener_usuario_inexistente_404(uow):
    with pytest.raises(HTTPException) as exc:
        await service(uow).get_user(9999)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_actualizar_usuario(uow):
    id_rol = await seed_role(uow)
    svc = service(uow)
    creado = await svc.create_user(make_user(id_rol, username="pedro", nombre="Pedro"))
    actualizado = await svc.update_user(
        creado.id_usuario,
        schemas.UserUpdate(nombre_completo="Pedro Modificado")
    )
    assert actualizado.nombre_completo == "Pedro Modificado"


@pytest.mark.asyncio
async def test_desactivar_usuario_soft_delete(uow):
    id_rol = await seed_role(uow)
    svc = service(uow)
    creado = await svc.create_user(make_user(id_rol, username="inactivar"))
    desactivado = await svc.deactivate_user(creado.id_usuario)
    assert desactivado.estado == "Inactivo"

    filtros = schemas.UserFilter(is_active=True)
    activos = await svc.list_users(filtros)
    usernames_activos = [u.username for u in activos]
    assert "inactivar" not in usernames_activos

