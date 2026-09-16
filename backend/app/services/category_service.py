from typing import Optional, List
from fastapi import HTTPException, status
from app.db.models import Categoria
from app.interfaces.repositories import CategoryRepository
from app.interfaces.services import CategoryService
from app.schemas import schemas


class ConcreteCategoryService(CategoryService):
    """Lógica de negocio de Categorías (modelo relacional). Cero datos quemados."""

    def __init__(self, repository: CategoryRepository):
        self.repository = repository

    async def list_categories(self, include_inactive: bool = False) -> List[schemas.CategoriaOut]:
        categories = await self.repository.list_all(include_inactive=include_inactive)
        return [schemas.CategoriaOut.model_validate(c) for c in categories]

    async def get_category(self, category_id: int) -> schemas.CategoriaOut:
        categoria = await self.repository.get_by_id(category_id)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        return schemas.CategoriaOut.model_validate(categoria)

    async def create_category(self, data: schemas.CategoriaCreate) -> schemas.CategoriaOut:
        existing = await self.repository.get_by_name(data.nombre.strip())
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")
        categoria = Categoria(nombre=data.nombre.strip(), estado="Activo")
        await self.repository.create(categoria)
        await self.repository.commit()
        return schemas.CategoriaOut.model_validate(categoria)

    async def update_category(
        self, category_id: int, data: schemas.CategoriaUpdate
    ) -> schemas.CategoriaOut:
        categoria = await self.repository.get_by_id(category_id)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")

        if data.nombre is not None:
            nombre = data.nombre.strip()
            duplicate = await self.repository.get_by_name(nombre)
            if duplicate and duplicate.id_categoria != category_id:
                raise HTTPException(status_code=400, detail="Ya existe una categoría con ese nombre")
            categoria.nombre = nombre
        if data.estado is not None:
            categoria.estado = data.estado.strip()

        await self.repository.update(categoria)
        await self.repository.commit()
        return schemas.CategoriaOut.model_validate(categoria)

    async def deactivate_category(self, category_id: int) -> schemas.CategoriaOut:
        """Eliminación lógica (soft delete)."""
        categoria = await self.repository.get_by_id(category_id)
        if not categoria:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
        categoria.estado = "Inactivo"
        await self.repository.update(categoria)
        await self.repository.commit()
        return schemas.CategoriaOut.model_validate(categoria)