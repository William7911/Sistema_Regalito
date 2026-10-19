"""
Servicio centralizado de auditoría.

Registra acciones críticas en la tabla `bitacora_auditoria` de forma
transparente.  No hace commit: la responsabilidad de persistir la transacción
sigue siendo del Unit of Work del servicio que llama a `log_action`.

Uso:
    from app.services.audit_service import log_action
    await log_action(db, id_usuario=..., tabla="usuario", accion="CREAR",
                     descripcion="Creó usuario 'cajera1'")
"""
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import BitacoraAuditoria


async def log_action(
    db: AsyncSession,
    id_usuario: int,
    tabla: str,
    accion: str,
    descripcion: str,
) -> None:
    """
    Inserta un registro en bitacora_auditoria dentro de la sesión activa.

    Parameters
    ----------
    db:          La sesión AsyncSession de SQLAlchemy (dentro de la transacción activa).
    id_usuario:  ID del usuario que realizó la acción.
    tabla:       Nombre de la tabla o módulo afectado (ej. "usuario", "venta").
    accion:      Verbo corto en mayúsculas (ej. "LOGIN", "CREAR", "EDITAR",
                 "DESACTIVAR", "VENTA", "MERMA", "CIERRE_CIEGAS", "PRECIO").
    descripcion: Texto legible con el detalle de la operación.
    """
    try:
        entrada = BitacoraAuditoria(
            id_usuario=id_usuario,
            tabla_afectada=tabla[:50],          # respetar VARCHAR(50) del modelo
            accion=accion[:20],                  # respetar VARCHAR(20)
            descripcion=descripcion,
            fecha_hora=datetime.now(),
        )
        db.add(entrada)
        await db.flush()   # persiste en la transacción sin hacer commit
    except Exception:
        # La auditoría nunca debe interrumpir la operación principal.
        # Si falla (p.ej. falla de constraint) se descarta silenciosamente.
        pass

