import pytest
from fastapi import HTTPException
from app.services.role_service import ConcreteRoleService
from app.schemas import schemas


def service(uow):
    return ConcreteRoleService(uow)


async def test_create_and_get_role(uow):
    created = await service(uow).create_role(schemas.RoleCreate(name="Cajero", description="Caja"))
    assert created.id is not None
    assert created.name == "Cajero"
    assert created.is_active is True

    fetched = await service(uow).get_role(created.id)
    assert fetched.id == created.id


async def test_duplicate_role_name_rejected(uow):
    svc = service(uow)
    await svc.create_role(schemas.RoleCreate(name="Admin"))
    with pytest.raises(HTTPException) as exc:
        await svc.create_role(schemas.RoleCreate(name="Admin"))
    assert exc.value.status_code == 400


async def test_get_nonexistent_role_404(uow):
    with pytest.raises(HTTPException) as exc:
        await service(uow).get_role(999)
    assert exc.value.status_code == 404


async def test_update_role(uow):
    created = await service(uow).create_role(schemas.RoleCreate(name="Gerente"))
    updated = await service(uow).update_role(
        created.id, schemas.RoleUpdate(name="Director", description="Dirección")
    )
    assert updated.name == "Director"
    assert updated.description == "Dirección"


async def test_soft_delete_role(uow):
    svc = service(uow)
    a = await svc.create_role(schemas.RoleCreate(name="A"))
    b = await svc.create_role(schemas.RoleCreate(name="B"))

    await svc.deactivate_role(a.id)

    active = await svc.list_roles()
    assert {r.name for r in active} == {"B"}
    assert len(await svc.list_roles(include_inactive=True)) == 2