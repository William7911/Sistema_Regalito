from typing import Optional, List
from fastapi import HTTPException, status
from app.db.models import Category
from app.interfaces.repositories import CategoryRepository
from app.interfaces.services import CategoryService
from app.schemas import schemas


class ConcreteCategoryService(CategoryService):
    """Lógica de negocio de Categorías. Cero datos quemados: todo se consulta en BD."""

    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    async def list_categories(self, include_inactive: bool = False) -> List[schemas.Category]:
        categories = await self.repository.list_all(include_inactive=include_inactive)
        return [schemas.Category.model_validate(c) for c in categories]

    async def get_category(self, category_id: int) -> schemas.Category:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return schemas.Category.model_validate(category)

    async def create_category(self, data: schemas.CategoryCreate) -> schemas.Category:
        existing = await self.repository.get_by_name(data.name.strip())
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")
        category = Category(name=data.name.strip(), description=data.description)
        created = await self.repository.create(category)
        return schemas.Category.model_validate(created)

    async def update_category(
        self, category_id: int, data: schemas.CategoryUpdate
    ) -> schemas.Category:
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        if data.name is not None:
            name = data.name.strip()
            duplicate = await self.repository.get_by_name(name)
            if duplicate and duplicate.id != category_id:
                raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")
            category.name = name
        if data.description is not None:
            category.description = data.description
        if data.is_active is not None:
            category.is_active = data.is_active

        updated = await self.repository.update(category)
        return schemas.Category.model_validate(updated)

    async def deactivate_category(self, category_id: int) -> schemas.Category:
        """Eliminación lógica (soft delete)."""
        category = await self.repository.get_by_id(category_id)
        if not category:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        category.is_active = False
        updated = await self.repository.update(category)
        return schemas.Category.model_validate(updated)