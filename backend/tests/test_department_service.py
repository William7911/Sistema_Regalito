import pytest
from fastapi import HTTPException
from app.services.department_service import ConcreteDepartmentService
from app.schemas import schemas


def service(uow):
    return ConcreteDepartmentService(uow)


@pytest.mark.asyncio
async def test_crear_y_obtener_departamento(uow):
    creado = await service(uow).create_department(schemas.DepartmentCreate(nombre="Guatemala"))
    assert creado.id_departamento is not None
    assert creado.nombre == "Guatemala"

    obtenido = await service(uow).get_department(creado.id_departamento)
    assert obtenido.id_departamento == creado.id_departamento
    assert obtenido.nombre == "Guatemala"


@pytest.mark.asyncio
async def test_departamento_duplicado_rechazado(uow):
    svc = service(uow)
    await svc.create_department(schemas.DepartmentCreate(nombre="Sololá"))
    with pytest.raises(HTTPException) as exc:
        await svc.create_department(schemas.DepartmentCreate(nombre="Sololá"))
    assert exc.value.status_code == 400
    assert "Ya existe" in exc.value.detail


@pytest.mark.asyncio
async def test_obtener_departamento_inexistente_404(uow):
    with pytest.raises(HTTPException) as exc:
        await service(uow).get_department(9999)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_actualizar_departamento(uow):
    svc = service(uow)
    creado = await svc.create_department(schemas.DepartmentCreate(nombre="Peten"))
    actualizado = await svc.update_department(
        creado.id_departamento, schemas.DepartmentUpdate(nombre="Petén")
    )
    assert actualizado.nombre == "Petén"


@pytest.mark.asyncio
async def test_listar_departamentos(uow):
    svc = service(uow)
    await svc.create_department(schemas.DepartmentCreate(nombre="Zacapa"))
    await svc.create_department(schemas.DepartmentCreate(nombre="Izabal"))

    departamentos = await svc.list_departments()
    nombres = [d.nombre for d in departamentos]
    assert "Zacapa" in nombres
    assert "Izabal" in nombres

