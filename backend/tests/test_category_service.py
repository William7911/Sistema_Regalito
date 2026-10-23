import pytest
from fastapi import HTTPException
from app.repositories.category_repository import CategoryRepositoryImpl
from app.services.category_service import ConcreteCategoryService
from app.schemas import schemas


def build_service(db_session):
    repository = CategoryRepositoryImpl(db_session)
    return ConcreteCategoryService(repository)


@pytest.mark.asyncio
async def test_crear_y_obtener_categoria(db_session):
    service = build_service(db_session)
    creada = await service.create_category(schemas.CategoriaCreate(nombre="Bebidas"))
    assert creada.id_categoria is not None
    assert creada.nombre == "Bebidas"
    assert creada.estado == "Activo"

    obtenida = await service.get_category(creada.id_categoria)
    assert obtenida.id_categoria == creada.id_categoria
    assert obtenida.nombre == "Bebidas"


@pytest.mark.asyncio
async def test_categoria_duplicada_rechazada(db_session):
    service = build_service(db_session)
    await service.create_category(schemas.CategoriaCreate(nombre="Dulcería"))
    with pytest.raises(HTTPException) as exc:
        await service.create_category(schemas.CategoriaCreate(nombre="Dulcería"))
    assert exc.value.status_code == 400
    assert "Ya existe" in exc.value.detail


@pytest.mark.asyncio
async def test_obtener_categoria_inexistente_404(db_session):
    service = build_service(db_session)
    with pytest.raises(HTTPException) as exc:
        await service.get_category(9999)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_actualizar_categoria(db_session):
    service = build_service(db_session)
    creada = await service.create_category(schemas.CategoriaCreate(nombre="Snacks"))
    actualizada = await service.update_category(
        creada.id_categoria, schemas.CategoriaUpdate(nombre="Botanas")
    )
    assert actualizada.nombre == "Botanas"


@pytest.mark.asyncio
async def test_desactivar_categoria_soft_delete(db_session):
    service = build_service(db_session)
    cat_a = await service.create_category(schemas.CategoriaCreate(nombre="Cat A"))
    cat_b = await service.create_category(schemas.CategoriaCreate(nombre="Cat B"))

    await service.deactivate_category(cat_a.id_categoria)

    activas = await service.list_categories(include_inactive=False)
    nombres_activas = [c.nombre for c in activas]
    assert "Cat A" not in nombres_activas
    assert "Cat B" in nombres_activas

    todas = await service.list_categories(include_inactive=True)
    nombres_todas = [c.nombre for c in todas]
    assert "Cat A" in nombres_todas
    assert "Cat B" in nombres_todas

