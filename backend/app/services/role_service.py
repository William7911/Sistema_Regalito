from typing import Optional, List
from fastapi import HTTPException
from app.db.models import Rol
from app.interfaces.services import RoleService
from app.schemas import schemas


class ConcreteRoleService(RoleService):
    """Lógica de negocio de Roles (modelo Rol). Usa Unit of Work para la transacción."""

    def __init__(self, uow):
        self.uow = uow

    async def list_roles(self, include_inactive: bool = False) -> List[schemas.Role]:
        roles = await self.uow.roles.list_all(include_inactive=include_inactive)
        return [schemas.Role.model_validate(r) for r in roles]

    async def get_role(self, role_id: int) -> schemas.Role:
        role = await self.uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        return schemas.Role.model_validate(role)

    async def create_role(self, data: schemas.RoleCreate) -> schemas.Role:
        existing = await self.uow.roles.get_by_name(data.nombre.strip())
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe un rol con ese nombre")
        rol = Rol(
            nombre=data.nombre.strip(),
            descripcion=data.descripcion.strip() if data.descripcion else None,
            estado="Activo",
        )
        created = await self.uow.roles.create(rol)
        await self.uow.commit()
        return schemas.Role.model_validate(created)

    async def update_role(self, role_id: int, data: schemas.RoleUpdate) -> schemas.Role:
        role = await self.uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Rol no encontrado")

        if data.nombre is not None:
            nombre = data.nombre.strip()
            duplicate = await self.uow.roles.get_by_name(nombre)
            if duplicate and duplicate.id_rol != role_id:
                raise HTTPException(status_code=400, detail="Ya existe un rol con ese nombre")
            role.nombre = nombre
        if data.descripcion is not None:
            role.descripcion = data.descripcion.strip() if data.descripcion else None
        if data.estado is not None:
            role.estado = data.estado.strip()

        updated = await self.uow.roles.update(role)
        await self.uow.commit()
        return schemas.Role.model_validate(updated)

    async def deactivate_role(self, role_id: int) -> schemas.Role:
        """Eliminación lógica (soft delete)."""
        role = await self.uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        role.estado = "Inactivo"
        updated = await self.uow.roles.update(role)
        await self.uow.commit()
        return schemas.Role.model_validate(updated)