from datetime import datetime
from fastapi import HTTPException, status
from app.repositories.login_attempt_repository import LoginAttemptRepositoryImpl


class LoginSecurityService:
    """Servicio de seguridad para mitigación de ataques de fuerza bruta en autenticación.
    Aplica la regla de negocio:
      - 5 intentos fallidos consecutivos bloquean el username durante 5 minutos.
      - Cualquier petición dentro del periodo de bloqueo recibe HTTP 429 con tiempo restante.
      - Al iniciar sesión con éxito, se reinicia el contador de intentos y se levanta cualquier bloqueo.
    """

    MAX_INTENTOS: int = 5
    LOCK_MINUTES: int = 5

    def __init__(self, repository: LoginAttemptRepositoryImpl):
        self.repository = repository

    async def check_lockout(self, username: str) -> None:
        """Verifica si el usuario está actualmente bloqueado. Lanza 429 si el bloqueo está vigente."""
        registro = await self.repository.get_by_username(username)
        if registro and registro.bloqueado_hasta:
            ahora = datetime.now()
            if ahora < registro.bloqueado_hasta:
                remaining = int((registro.bloqueado_hasta - ahora).total_seconds() / 60) + 1
                remaining = max(1, remaining)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        f"Cuenta bloqueada temporalmente por demasiados intentos fallidos. "
                        f"Inténtalo de nuevo en {remaining} minuto(s)."
                    ),
                )
            else:
                # El tiempo de bloqueo ya expiró — limpiar estado
                await self.repository.clear_expired_lockout(registro)

    async def record_failure(self, username: str) -> None:
        """Registra un fallo de autenticación en la base de datos y activa bloqueo si procede."""
        await self.repository.record_failure(
            username=username,
            max_intentos=self.MAX_INTENTOS,
            lock_minutes=self.LOCK_MINUTES,
        )

    async def reset_attempts(self, username: str) -> None:
        """Limpia los intentos fallidos tras una autenticación exitosa."""
        await self.repository.reset_attempts(username)

