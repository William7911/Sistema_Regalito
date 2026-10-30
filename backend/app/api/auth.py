import re
import secrets
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from jose import jwt, JWTError
from app.db.database import get_db
from app.db.models import Usuario, RolPermiso, Permiso, CodigoRecuperacion
from app.core import security
from app.core.config import settings
from app.schemas import schemas
from app.services.audit_service import log_action
from app.services.login_security_service import LoginSecurityService
from app.services.email_service import EmailService
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


# ---------------------------------------------------------------------------
# RECUPERACIÓN DE CONTRASEÑAS (Código OTP de 6 dígitos por Correo Electrónico)
# ---------------------------------------------------------------------------

@router.post("/recuperar-password")
async def solicitar_recuperacion_password(
    payload: schemas.PasswordRecoverRequest,
    db: AsyncSession = Depends(get_db)
):
    identifier = payload.identifier.strip()
    if not identifier:
        raise HTTPException(
            status_code=400,
            detail="Debe ingresar el correo electrónico o nombre de usuario registrado."
        )

    # Validar si es correo electrónico o nombre de usuario
    is_email = "@" in identifier
    if is_email:
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", identifier):
            raise HTTPException(
                status_code=400,
                detail="El formato del correo electrónico ingresado no es válido."
            )
        stmt = select(Usuario).where(func.lower(Usuario.email) == identifier.lower())
    else:
        stmt = select(Usuario).where(Usuario.username == identifier)

    res = await db.execute(stmt)
    user = res.scalar_one_or_none()

    if not user:
        if is_email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El correo '{identifier}' no pertenece a ningún usuario registrado en el sistema. Ingrese el correo asociado a su cuenta."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"El usuario '{identifier}' no existe en el sistema."
            )

    if user.estado != "Activo":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"La cuenta del usuario '{user.username}' se encuentra inactiva. Comuníquese con la administración."
        )

    if not user.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El usuario '{user.username}' no tiene un correo electrónico registrado en el sistema. Solicite a la administración que le asigne uno."
        )

    # Invalidar códigos anteriores no utilizados
    stmt_invalidar = (
        update(CodigoRecuperacion)
        .where(CodigoRecuperacion.id_usuario == user.id_usuario, CodigoRecuperacion.usado == False)
        .values(usado=True)
    )
    await db.execute(stmt_invalidar)

    # Generar código numérico seguro de 6 dígitos (100000 - 999999)
    codigo = f"{secrets.randbelow(900000) + 100000}"
    expira_en = datetime.utcnow() + timedelta(minutes=15)

    nuevo_codigo = CodigoRecuperacion(
        id_usuario=user.id_usuario,
        codigo=codigo,
        expira_en=expira_en,
        usado=False
    )
    db.add(nuevo_codigo)
    await db.commit()

    # Enviar correo electrónico real a la cuenta del usuario
    enviado = await EmailService.enviar_codigo_recuperacion(
        user.email, user.nombre_completo, codigo
    )

    if not enviado:
        if not settings.SMTP_HOST or not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="El servicio de envío de correos (SMTP) no está configurado en el servidor. Debe configurar las credenciales SMTP en el archivo .env para despachar correos reales."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"No se pudo entregar el correo a '{user.email}' mediante el servidor SMTP. Verifique las credenciales de correo o la conexión del servidor."
            )

    # Máscara de correo para privacidad (ej. ab***@gmail.com)
    partes = user.email.split("@")
    if len(partes) == 2:
        user_part, domain = partes
        masked_user = user_part[:2] + "***" if len(user_part) > 2 else user_part + "***"
        masked_email = f"{masked_user}@{domain}"
    else:
        masked_email = user.email

    return {
        "status": "ok",
        "message": f"Código de verificación de 6 dígitos enviado exitosamente a {masked_email}",
        "email": user.email
    }


@router.post("/verificar-codigo")
async def verificar_codigo_recuperacion(
    payload: schemas.CodeVerifyRequest,
    db: AsyncSession = Depends(get_db)
):
    email_or_user = payload.email.strip()
    codigo_ingresado = payload.codigo.strip()

    stmt_user = select(Usuario).where(
        or_(
            func.lower(Usuario.email) == email_or_user.lower(),
            Usuario.username == email_or_user
        )
    )
    res_user = await db.execute(stmt_user)
    user = res_user.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Buscar código activo
    stmt_codigo = select(CodigoRecuperacion).where(
        CodigoRecuperacion.id_usuario == user.id_usuario,
        CodigoRecuperacion.codigo == codigo_ingresado,
        CodigoRecuperacion.usado == False,
        CodigoRecuperacion.expira_en > datetime.utcnow()
    )
    res_codigo = await db.execute(stmt_codigo)
    codigo_obj = res_codigo.scalar_one_or_none()

    if not codigo_obj:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Código de verificación incorrecto o expirado. Solicite uno nuevo."
        )

    # Generar reset_token seguro
    reset_token = security.create_password_reset_token(user.username, user.id_usuario)

    return {
        "status": "ok",
        "message": "Código verificado exitosamente",
        "reset_token": reset_token,
        "email": user.email
    }


@router.post("/reset-password")
async def restablecer_password(
    payload: schemas.PasswordResetRequest,
    db: AsyncSession = Depends(get_db)
):
    user = None

    if payload.reset_token:
        try:
            token_payload = jwt.decode(payload.reset_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = token_payload.get("id_usuario")
            token_type = token_payload.get("type")
            if not user_id or token_type != "password_reset":
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token de restablecimiento inválido")
            res_user = await db.execute(select(Usuario).where(Usuario.id_usuario == user_id))
            user = res_user.scalar_one_or_none()
        except JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El token de restablecimiento ha expirado o es inválido")

    elif payload.email and payload.codigo:
        stmt_user = select(Usuario).where(
            or_(
                func.lower(Usuario.email) == payload.email.strip().lower(),
                Usuario.username == payload.email.strip()
            )
        )
        res_user = await db.execute(stmt_user)
        user = res_user.scalar_one_or_none()
        if user:
            stmt_codigo = select(CodigoRecuperacion).where(
                CodigoRecuperacion.id_usuario == user.id_usuario,
                CodigoRecuperacion.codigo == payload.codigo.strip(),
                CodigoRecuperacion.usado == False,
                CodigoRecuperacion.expira_en > datetime.utcnow()
            )
            res_codigo = await db.execute(stmt_codigo)
            if not res_codigo.scalar_one_or_none():
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Código inválido o expirado")

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No se pudo identificar al usuario para restablecer la contraseña")

    if len(payload.nueva_password) < 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La nueva contraseña debe tener al menos 6 caracteres")

    # Actualizar hash de contraseña
    user.password_hash = security.get_password_hash(payload.nueva_password)

    # Marcar todos los códigos de recuperación del usuario como usados
    await db.execute(
        update(CodigoRecuperacion)
        .where(CodigoRecuperacion.id_usuario == user.id_usuario)
        .values(usado=True)
    )

    await log_action(
        db,
        id_usuario=user.id_usuario,
        tabla="usuario",
        accion="RESET_PASSWORD",
        descripcion=f"Contraseña restablecida exitosamente para '{user.username}'.",
    )

    await db.commit()

    return {
        "status": "ok",
        "message": "Contraseña restablecida exitosamente. Ahora puedes iniciar sesión con tu nueva contraseña."
    }