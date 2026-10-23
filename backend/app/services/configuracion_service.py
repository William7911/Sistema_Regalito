from typing import Dict, Any
from fastapi import HTTPException
from app.api.deps import UnitOfWork
from app.db.models import Usuario
from app.services.audit_service import log_action

class ConfiguracionService:
    def __init__(self, uow: UnitOfWork):
        self.uow = uow

    async def _validar_acceso_admin(self, usuario: Usuario):
        # Recarga el usuario con la relación `rol` eager-loaded (selectinload)
        # para evitar MissingGreenlet al acceder a la relación fuera del contexto async.
        usuario_cargado = await self.uow.users.get_by_id(usuario.id_usuario) or usuario
        if usuario_cargado.id_rol != 1 and (not usuario_cargado.rol or usuario_cargado.rol.nombre != "Administradora"):
            raise HTTPException(status_code=403, detail="Acceso denegado. Requiere rol de Administradora.")

    async def obtener_configuracion(self, usuario_actual: Usuario) -> Dict[str, str]:
        await self._validar_acceso_admin(usuario_actual)
        return await self.uow.configuracion.obtener_todos()

    async def actualizar_configuracion(self, parametros: Dict[str, str], usuario_actual: Usuario) -> None:
        await self._validar_acceso_admin(usuario_actual)
        
        # Validar claves críticas vacías
        claves_criticas = ["NIT", "Razón Social"]
        for clave in claves_criticas:
            valor = parametros.get(clave)
            if valor is not None and str(valor).strip() == "":
                raise HTTPException(status_code=400, detail=f"La clave crítica '{clave}' no puede estar vacía.")

        for clave, valor in parametros.items():
            await self.uow.configuracion.actualizar_valor(clave, valor)

        await log_action(
            self.uow.db, id_usuario=usuario_actual.id_usuario, accion="UPDATE",
            tabla="parametro_sistema",
            descripcion="Actualizó configuración: " + ", ".join(sorted(parametros.keys())),
        )
        await self.uow.commit()
