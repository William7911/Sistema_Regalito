import pytest
from fastapi import HTTPException
from app.db.models import Role, Department
from app.services.user_service import ConcreteUserService
from app.schemas import schemas


def service(uow):
    return ConcreteUserService(uow)


async def seed_context(uow):
    role = await uow.roles.create(Role(name="Cajero"))
    await uow.commit()
    dept = await uow.departments.create(Department(name="General"))
    await uow.commit()
    return role.id, dept.id


def make_user(role_id, department_id, code="U001", username="jperez", name="Juan", lastname="Perez"):
    return schemas.UserCreate(
        name=name,
        lastname=lastname,
        code=code,
        username=username,
        password="secreto123",
        role_id=role_id,
        department_id=department_id,
    )


async def test_create_user_ok(uow):
    role_id, dept_id = await seed_context(uow)
    created = await service(uow).create_user(make_user(role_id, dept_id))
    assert created.id is not None
    assert created.username == "jperez"
    assert created.role is not None
    assert created.department is not None


async def test_create_user_requires_valid_role_and_department(uow):
    svc = service(uow)
    # Ni rol ni departamento existen en BD
    with pytest.raises(HTTPException) as exc:
        await svc.create_user(make_user(999, 999))
    assert exc.value.status_code == 400


async def test_create_user_rejects_inactive_role(uow):
    role_id, dept_id = await seed_context(uow)
    role = await uow.roles.get_by_id(role_id)
    role.is_active = False
    await uow.roles.update(role)
    await uow.commit()

    with pytest.raises(HTTPException) as exc:
        await service(uow).create_user(make_user(role_id, dept_id))
    assert exc.value.status_code == 400


async def test_duplicate_username_rejected(uow):
    role_id, dept_id = await seed_context(uow)
    svc = service(uow)
    await svc.create_user(make_user(role_id, dept_id))
    with pytest.raises(HTTPException) as exc:
        await svc.create_user(make_user(role_id, dept_id, code="U002"))
    assert exc.value.status_code == 400


async def test_duplicate_code_rejected(uow):
    role_id, dept_id = await seed_context(uow)
    svc = service(uow)
    await svc.create_user(make_user(role_id, dept_id))
    with pytest.raises(HTTPException) as exc:
        await svc.create_user(make_user(role_id, dept_id, username="otro"))
    assert exc.value.status_code == 400


async def test_soft_delete_user(uow):
    role_id, dept_id = await seed_context(uow)
    svc = service(uow)
    created = await svc.create_user(make_user(role_id, dept_id))
    await svc.deactivate_user(created.id)

    deactivated = await svc.get_user(created.id)
    assert deactivated.is_active is False


async def test_list_users_filters(uow):
    role_id, dept_id = await seed_context(uow)
    svc = service(uow)
    u1 = await svc.create_user(make_user(role_id, dept_id, code="U001", username="jperez"))
    await svc.create_user(make_user(role_id, dept_id, code="U002", username="mgarcia", name="Maria"))

    by_name = await svc.list_users(schemas.UserFilter(name="Juan"))
    assert {u.username for u in by_name} == {"jperez"}

    by_lastname = await svc.list_users(schemas.UserFilter(lastname="Perez"))
    assert len(by_lastname) == 2

    await svc.deactivate_user(u1.id)
    active = await svc.list_users(schemas.UserFilter(is_active=True))
    assert all(u.is_active for u in active)
    assert {u.username for u in active} == {"mgarcia"}

    by_code = await svc.list_users(schemas.UserFilter(code="U002"))
    assert [u.username for u in by_code] == ["mgarcia"]

    assert await svc.count_users(schemas.UserFilter(name="Juan")) == 1