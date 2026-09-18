from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Usuario, RolPermiso, Permiso


async def check_user_permission(db: AsyncSession, user: Usuario, permission_code: str) -> bool:
    """Verifica si el usuario posee un código de permiso asignado a su rol.
    Administradora tiene bypass total (superusuario)."""
    if user.rol and user.rol.nombre == "Administradora":
        return True
    stmt = (
        select(Permiso.codigo)
        .select_from(RolPermiso)
        .join(Permiso, RolPermiso.id_permiso == Permiso.id_permiso)
        .where(
            RolPermiso.id_rol == user.id_rol,
            Permiso.codigo == permission_code,
        )
    )
    res = await db.execute(stmt)
    return res.scalar_one_or_none() is not None

