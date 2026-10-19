import pytest
from fastapi import HTTPException
from app.repositories.category_repository import CategoryRepositoryImpl
from app.services.category_service import ConcreteCategoryService
from app.schemas import schemas


def build_service(db_session):
    repository = CategoryRepositoryImpl(db_session)
    return ConcreteCategoryService(repository)


async def test_create_and_get_category(db_session):
    service = build_service(db_session)
    created = await service.create_category(schemas.CategoryCreate(name="Bebidas", description="Refrescos"))
    assert created.id is not None
    assert created.name == "Bebidas"
    assert created.is_active is True

    fetched = await service.get_category(created.id)
    assert fetched.id == created.id


async def test_duplicate_category_name_rejected(db_session):
    service = build_service(db_session)
    await service.create_category(schemas.CategoryCreate(name="Dulcería"))
    with pytest.raises(HTTPException) as exc:
        await service.create_category(schemas.CategoryCreate(name="Dulcería"))
    assert exc.value.status_code == 400


async def test_get_nonexistent_category_404(db_session):
    service = build_service(db_session)
    with pytest.raises(HTTPException) as exc:
        await service.get_category(999)
    assert exc.value.status_code == 404


async def test_update_category(db_session):
    service = build_service(db_session)
    created = await service.create_category(schemas.CategoryCreate(name="Snacks"))
    updated = await service.update_category(
        created.id, schemas.CategoryUpdate(name="Botanas", description="Frituras")
    )
    assert updated.name == "Botanas"
    assert updated.description == "Frituras"


async def test_soft_delete_excludes_inactive(db_session):
    service = build_service(db_session)
    a = await service.create_category(schemas.CategoryCreate(name="A"))
    b = await service.create_category(schemas.CategoryCreate(name="B"))

    await service.deactivate_category(a.id)

    active = await service.list_categories(include_inactive=False)
    names = [c.name for c in active]
    assert "A" not in names
    assert "B" in names

    all_categories = await service.list_categories(include_inactive=True)
    assert len(all_categories) == 2