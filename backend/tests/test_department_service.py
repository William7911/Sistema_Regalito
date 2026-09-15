import pytest
from fastapi import HTTPException
from app.services.department_service import ConcreteDepartmentService
from app.schemas import schemas


def service(uow):
    return ConcreteDepartmentService(uow)


async def test_create_and_get_department(uow):
    created = await service(uow).create_department(schemas.DepartmentCreate(name="Ventas"))
    assert created.id is not None
    assert created.is_active is True

    fetched = await service(uow).get_department(created.id)
    assert fetched.id == created.id


async def test_duplicate_department_name_rejected(uow):
    svc = service(uow)
    await svc.create_department(schemas.DepartmentCreate(name="Bodega"))
    with pytest.raises(HTTPException) as exc:
        await svc.create_department(schemas.DepartmentCreate(name="Bodega"))
    assert exc.value.status_code == 400


async def test_get_nonexistent_department_404(uow):
    with pytest.raises(HTTPException) as exc:
        await service(uow).get_department(999)
    assert exc.value.status_code == 404


async def test_update_department(uow):
    created = await service(uow).create_department(schemas.DepartmentCreate(name="Ventas"))
    updated = await service(uow).update_department(
        created.id, schemas.DepartmentUpdate(name="Ventas Norte", description="Sucursal")
    )
    assert updated.name == "Ventas Norte"


async def test_soft_delete_department(uow):
    svc = service(uow)
    a = await svc.create_department(schemas.DepartmentCreate(name="A"))
    await svc.create_department(schemas.DepartmentCreate(name="B"))

    await svc.deactivate_department(a.id)

    active = await svc.list_departments()
    assert {d.name for d in active} == {"B"}
    assert len(await svc.list_departments(include_inactive=True)) == 2