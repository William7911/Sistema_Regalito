from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from jose import jwt, JWTError
from app.db.database import get_db
from app.db.models import Usuario, RolPermiso, Permiso
from app.core import security
from app.core.config import settings
from app.schemas import schemas
from app.services.audit_service import log_action
from app.services.login_security_service import LoginSecurityService
from app.api.deps import get_login_security_service

router = APIRouter()


@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    response: Response,
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
    security_service: LoginSecurityService = Depends(get_login_security_service),
):
    username = form_data.username

    # 1. Verificar si el username está bloqueado (persistido en BD)
    await security_service.check_lockout(username)

    result = await db.execute(
        select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.username == username)
    )
    user = result.scalar_one_or_none()
    if not user or not await security.verify_password_async(form_data.password, user.password_hash):
        await security_service.record_failure(username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.estado != "Activo":
        raise HTTPException(status_code=400, detail="Inactive user")

    # Inicio de sesión exitoso — limpiar contador de intentos en BD
    await security_service.reset_attempts(username)

    # Registrar en bitácora de auditoría
    await log_action(
        db,
        id_usuario=user.id_usuario,
        tabla="sesion_usuario",
        accion="LOGIN",
        descripcion=f"Inicio de sesión exitoso para '{username}'.",
    )

    # Consultar permisos asignados al rol en tiempo real desde rol_permiso
    stmt_permisos = (
        select(Permiso.codigo)
        .select_from(RolPermiso)
        .join(Permiso, RolPermiso.id_permiso == Permiso.id_permiso)
        .where(RolPermiso.id_rol == user.id_rol)
        .order_by(Permiso.codigo.asc())
    )
    res_permisos = await db.execute(stmt_permisos)
    permisos = list(res_permisos.scalars().all())

    rol_nombre = user.rol.nombre if user.rol else None

    # Access Token (Corto - e.g. 15 mins)
    access_token = security.create_access_token(
        data={"sub": user.username, "role": rol_nombre, "permissions": permisos}
    )

    # Refresh Token (Largo - e.g. 7 días)
    refresh_token = security.create_refresh_token(
        data={"sub": user.username}
    )

    # Establecer la cookie segura para el refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,  # Requiere HTTPS (o localhost en algunos browsers)
        samesite="strict",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "rol": rol_nombre,
        "id_rol": user.id_rol,
        "permisos": permisos,
        "nombre_completo": user.nombre_completo,
    }


@router.post("/refresh")
async def refresh_token(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing")

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")
        if username is None or token_type != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    # Verificar usuario en DB
    result = await db.execute(
        select(Usuario).options(selectinload(Usuario.rol)).where(Usuario.username == username)
    )
    user = result.scalar_one_or_none()
    if not user or user.estado != "Activo":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or not found")

    # Consultar permisos para el nuevo access token
    stmt_permisos = (
        select(Permiso.codigo)
        .select_from(RolPermiso)
        .join(Permiso, RolPermiso.id_permiso == Permiso.id_permiso)
        .where(RolPermiso.id_rol == user.id_rol)
        .order_by(Permiso.codigo.asc())
    )
    res_permisos = await db.execute(stmt_permisos)
    permisos = list(res_permisos.scalars().all())

    rol_nombre = user.rol.nombre if user.rol else None

    # Generar un nuevo Access Token
    new_access_token = security.create_access_token(
        data={"sub": user.username, "role": rol_nombre, "permissions": permisos}
    )

    return {"access_token": new_access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token", httponly=True, secure=True, samesite="strict")
    return {"detail": "Successfully logged out"}