from typing import Optional, List
from fastapi import HTTPException, status
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Categoria, Subcategoria, UnidadMedida, Sucursal, AreaBodega
from app.interfaces.repositories import ProductRepository
from app.interfaces.services import CatalogoService
from app.schemas import schemas


class ConcreteCatalogoService(CatalogoService):
    """Lógica de negocio de los catálogos de apoyo (dropdowns) de Productos."""

    def __init__(self, db: AsyncSession, product_repository: ProductRepository):
        self.db = db
        self.products = product_repository

    async def list_subcategorias(self, include_inactive: bool = False) -> List[schemas.SubcategoriaOut]:
        items = await self.products.list_subcategorias(include_inactive=include_inactive)
        return [schemas.SubcategoriaOut.model_validate(s) for s in items]

    async def list_unidades(self) -> List[schemas.UnidadMedidaOut]:
        items = await self.products.list_unidades()
        return [schemas.UnidadMedidaOut.model_validate(u) for u in items]

    async def list_sucursales(self, include_inactive: bool = False) -> List[schemas.SucursalOut]:
        items = await self.products.list_sucursales(include_inactive=include_inactive)
        return [schemas.SucursalOut.model_validate(s) for s in items]

    async def list_areas(self, sucursal_id: Optional[int] = None) -> List[schemas.AreaBodegaOut]:
        items = await self.products.list_areas(sucursal_id=sucursal_id)
        return [schemas.AreaBodegaOut.model_validate(a) for a in items]