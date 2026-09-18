from typing import Optional, List
from fastapi import HTTPException
from app.db.models import Usuario
from app.core import security
from app.interfaces.services import UserService
from app.schemas import schemas


class ConcreteUserService(UserService):
    """Lógica de negocio de Usuarios (modelo Usuario). El rol siempre se valida contra la BD."""

    def __init__(self, uow):
        self.uow = uow

    async def _validate_role(self, role_id: int):
        role = await self.uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=400, detail="El rol especificado no existe")
        if role.estado != "Activo":
            raise HTTPException(status_code=400, detail="El rol especificado está inactivo")

    async def list_users(self, filters: schemas.UserFilter) -> List[schemas.UserResponse]:
        users = await self.uow.users.search(
            name=filters.name,
            is_active=filters.is_active,
            role_id=filters.role_id,
            created_from=filters.created_from,
            created_to=filters.created_to,
            sort_by=filters.sort_by,
            sort_dir=filters.sort_dir or "asc",
            limit=filters.limit,
            offset=filters.offset,
        )
        return [schemas.UserResponse.model_validate(u) for u in users]

    async def count_users(self, filters: schemas.UserFilter) -> int:
        return await self.uow.users.count_search(
            name=filters.name,
            is_active=filters.is_active,
            role_id=filters.role_id,
            created_from=filters.created_from,
            created_to=filters.created_to,
        )

    async def get_user(self, user_id: int) -> schemas.UserResponse:
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return schemas.UserResponse.model_validate(user)

    async def create_user(self, data: schemas.UserCreate) -> schemas.UserResponse:
        await self._validate_role(data.id_rol)
        if await self.uow.users.get_by_username(data.username.strip()):
            raise HTTPException(status_code=400, detail="Ya existe un usuario con ese nombre de usuario")

        user = Usuario(
            id_rol=data.id_rol,
            nombre_completo=data.nombre_completo.strip(),
            username=data.username.strip(),
            password_hash=security.get_password_hash(data.password),
            estado="Activo",
        )
        try:
            created = await self.uow.users.create(user)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise
        fresh = await self.uow.users.get_by_id(created.id_usuario)
        return schemas.UserResponse.model_validate(fresh)

    async def update_user(
        self, user_id: int, data: schemas.UserUpdate
    ) -> schemas.UserResponse:
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")

        if data.id_rol is not None:
            await self._validate_role(data.id_rol)
            user.id_rol = data.id_rol

        if data.username is not None:
            username = data.username.strip()
            duplicate = await self.uow.users.get_by_username(username)
            if duplicate and duplicate.id_usuario != user_id:
                raise HTTPException(
                    status_code=400, detail="Ya existe un usuario con ese nombre de usuario"
                )
            user.username = username
        if data.nombre_completo is not None:
            user.nombre_completo = data.nombre_completo.strip()
        if data.password:
            user.password_hash = security.get_password_hash(data.password)
        if data.estado is not None:
            user.estado = data.estado.strip()

        try:
            updated = await self.uow.users.update(user)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise
        fresh = await self.uow.users.get_by_id(updated.id_usuario)
        return schemas.UserResponse.model_validate(fresh)

    async def deactivate_user(self, user_id: int) -> schemas.UserResponse:
        """Eliminación lógica (soft delete)."""
        user = await self.uow.users.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        user.estado = "Inactivo"
        try:
            updated = await self.uow.users.update(user)
            await self.uow.commit()
        except Exception:
            await self.uow.rollback()
            raise
        fresh = await self.uow.users.get_by_id(updated.id_usuario)
        return schemas.UserResponse.model_validate(fresh)