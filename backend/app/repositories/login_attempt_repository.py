from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import IntentoLogin


class LoginAttemptRepositoryImpl:
    """Acceso a datos asíncrono para el control de intentos de login y bloqueo por fuerza bruta.
    Gestiona la persistencia en la tabla `intento_login`.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> Optional[IntentoLogin]:
        """Obtiene el registro de intentos para un nombre de usuario."""
        stmt = select(IntentoLogin).where(IntentoLogin.username == username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def record_failure(
        self,
        username: str,
        max_intentos: int = 5,
        lock_minutes: int = 5,
    ) -> IntentoLogin:
        """Registra un intento fallido en base de datos.
        Si alcanza `max_intentos`, activa el bloqueo temporal por `lock_minutes`.
        """
        registro = await self.get_by_username(username)
        ahora = datetime.now()

        if not registro:
            registro = IntentoLogin(
                username=username,
                intentos_fallidos=1,
                bloqueado_hasta=None,
                ultimo_intento=ahora,
            )
            self.db.add(registro)
        else:
            registro.intentos_fallidos += 1
            registro.ultimo_intento = ahora

        if registro.intentos_fallidos >= max_intentos:
            registro.bloqueado_hasta = ahora + timedelta(minutes=lock_minutes)
            registro.intentos_fallidos = 0  # Reinicia contador para el siguiente ciclo

        await self.db.commit()
        await self.db.refresh(registro)
        return registro

    async def clear_expired_lockout(self, registro: IntentoLogin) -> None:
        """Limpia el bloqueo expirado."""
        registro.bloqueado_hasta = None
        registro.intentos_fallidos = 0
        registro.ultimo_intento = datetime.now()
        await self.db.commit()

    async def reset_attempts(self, username: str) -> None:
        """Restablece a 0 los intentos y retira el bloqueo tras login exitoso."""
        registro = await self.get_by_username(username)
        if registro:
            registro.intentos_fallidos = 0
            registro.bloqueado_hasta = None
            registro.ultimo_intento = datetime.now()
            await self.db.commit()

