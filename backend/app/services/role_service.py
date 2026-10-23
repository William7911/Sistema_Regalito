from typing import Optional, List
from fastapi import HTTPException
from app.db.models import Rol, Permiso, RolPermiso
from app.interfaces.services import RoleService
from app.schemas import schemas, catalogo_schema
from app.services.audit_service import log_action


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

    async def create_role(self, data: schemas.RoleCreate, actor_id: int = 0) -> schemas.Role:
        existing = await self.uow.roles.get_by_name(data.nombre.strip())
        if existing:
            raise HTTPException(status_code=400, detail="Ya existe un rol con ese nombre")
        rol = Rol(
            nombre=data.nombre.strip(),
            descripcion=data.descripcion.strip() if data.descripcion else None,
            estado="Activo",
        )
        created = await self.uow.roles.create(rol)
        if actor_id:
            await log_action(
                self.uow.db, id_usuario=actor_id, accion="CREAR", tabla="rol",
                descripcion=f"Creó rol '{created.nombre}' (ID: {created.id_rol})",
            )
        await self.uow.commit()
        return schemas.Role.model_validate(created)

    async def update_role(self, role_id: int, data: schemas.RoleUpdate, actor_id: int = 0) -> schemas.Role:
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
        if actor_id:
            await log_action(
                self.uow.db, id_usuario=actor_id, accion="EDITAR", tabla="rol",
                descripcion=f"Actualizó rol '{updated.nombre}' (ID: {updated.id_rol})",
            )
        await self.uow.commit()
        return schemas.Role.model_validate(updated)

    async def deactivate_role(self, role_id: int, actor_id: int = 0) -> schemas.Role:
        """Eliminación lógica (soft delete)."""
        role = await self.uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        if role.nombre == "Administradora" or (role.id_rol == 1 and role.nombre.lower().startswith("admin")):
            raise HTTPException(status_code=400, detail="No se puede desactivar el rol Administradora")
        if actor_id:
            actor = await self.uow.users.get_by_id(actor_id)
            if actor and actor.id_rol == role_id:
                raise HTTPException(status_code=400, detail="No puedes desactivar tu propio rol")
        role.estado = "Inactivo"
        updated = await self.uow.roles.update(role)
        if actor_id:
            await log_action(
                self.uow.db, id_usuario=actor_id, accion="DESACTIVAR", tabla="rol",
                descripcion=f"Desactivó rol '{updated.nombre}' (ID: {updated.id_rol})",
            )
        await self.uow.commit()
        return schemas.Role.model_validate(updated)

    # ---------------------------------------------------------------------------
    # Permisos y rol-permiso
    # ---------------------------------------------------------------------------

    async def list_permisos(self) -> List[catalogo_schema.PermisoOut]:
        permisos = await self.uow.permisos.list_all()
        return [catalogo_schema.PermisoOut.model_validate(p) for p in permisos]

    async def get_rol_permisos(self, role_id: int) -> List[str]:
        role = await self.uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Rol no encontrado")
        permisos = await self.uow.permisos.list_by_rol(role_id)
        return sorted(p.codigo for p in permisos)

    async def update_rol_permisos(
        self, role_id: int, codigos: List[str], actor_id: int = 0
    ) -> List[str]:
        """Reemplaza el conjunto de permisos asignados a un rol."""
        role = await self.uow.roles.get_by_id(role_id)
        if not role:
            raise HTTPException(status_code=404, detail="Rol no encontrado")

        disponibles = await self.uow.permisos.list_all()
        mapa = {p.codigo: p for p in disponibles}
        limite = {p.codigo for p in disponibles}
        for cod in codigos:
            if cod not in limite:
                raise HTTPException(status_code=400, detail=f"El permiso '{cod}' no existe")

        actuales = await self.uow.permisos.list_by_rol(role_id)
        actuales_cod = {p.codigo for p in actuales}
        codigos_set = set(codigos)

        # Regla 1: Un usuario no puede quitarse a sí mismo el acceso a Roles
        if actor_id:
            actor = await self.uow.users.get_by_id(actor_id)
            if actor and actor.id_rol == role_id:
                if "ROL_ADMIN" in mapa and "ROL_ADMIN" not in codigos_set:
                    raise HTTPException(
                        status_code=400,
                        detail="No puedes quitarte a ti mismo el acceso al módulo de Roles",
                    )

        # Regla 2: El rol Administradora no puede perder los permisos críticos (Roles y Usuarios)
        if role.nombre == "Administradora" or (role.id_rol == 1 and role.nombre.lower().startswith("admin")):
            permisos_criticos = {"ROL_ADMIN", "USUARIO_ADMIN"}
            faltantes = [p for p in permisos_criticos if p in mapa and p not in codigos_set]
            if faltantes:
                raise HTTPException(
                    status_code=400,
                    detail="El rol Administradora no puede perder los permisos críticos (acceso a Roles y Usuarios)",
                )

        # Quitar permisos que ya no están seleccionados
        for p in actuales:
            if p.codigo not in codigos_set:
                rp = await self.uow.permisos.get_rol_permiso(role_id, p.id_permiso)
                if rp:
                    await self.uow.permisos.remove_from_rol(rp)

        # Agregar los nuevos permisos
        for cod in codigos_set:
            if cod not in actuales_cod:
                p = mapa[cod]
                await self.uow.permisos.assign_to_rol(
                    RolPermiso(id_rol=role_id, id_permiso=p.id_permiso)
                )

        if actor_id:
            detalle = ", ".join(sorted(codigos_set)) or "sin permisos"
            await log_action(
                self.uow.db, id_usuario=actor_id, accion="EDITAR", tabla="rol_permiso",
                descripcion=f"Actualizó permisos del rol '{role.nombre}' (ID: {role_id}): {detalle}",
            )
        await self.uow.commit()
        return sorted(codigos_set)
