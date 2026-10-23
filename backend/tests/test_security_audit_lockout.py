"""
Pruebas para los 4 Frentes de Calidad y Seguridad:
- Frente 1: Expiración de JWT (401 en token expirado).
- Frente 2: Bitácora de auditoría en acciones críticas.
- Frente 3: Protección contra fuerza bruta en login (bloqueo tras 5 intentos fallidos -> 429).
"""
import pytest
from datetime import timedelta
from httpx import AsyncClient, ASGITransport
from sqlalchemy import select

from app.main import app
from app.db.database import get_db
from app.core import security
from app.db.models import (
    Rol, Usuario, Permiso, RolPermiso, BitacoraAuditoria,
    Sucursal, Categoria, Subcategoria, UnidadMedida, Producto,
    VarianteProducto, InventarioSucursal, Caja, TurnoCaja, MetodoPago
)
from app.services.audit_service import log_action


@pytest.fixture
async def client(db_session):
    async def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c
    app.dependency_overrides.clear()


async def _seed_test_user(db):
    rol = Rol(nombre="Administradora", estado="Activo")
    db.add(rol)
    await db.flush()

    user = Usuario(
        id_rol=rol.id_rol,
        nombre_completo="Admin Test",
        username="admin_test",
        password_hash=security.get_password_hash("secret123"),
        estado="Activo",
    )
    db.add(user)
    await db.flush()
    return user


# ===========================================================================
# FRENTE 1: Expiración de Token JWT
# ===========================================================================

@pytest.mark.asyncio
async def test_jwt_expired_token_returns_401(client, db_session):
    """Un token JWT expirado debe provocar que las rutas protegidas retornen 401."""
    user = await _seed_test_user(db_session)

    # Token expirado (expiración en el pasado)
    expired_token = security.create_access_token(
        data={"sub": user.username, "role": "Administradora", "permissions": []},
        expires_delta=timedelta(seconds=-10),
    )

    resp = await client.get(
        "/api/usuarios",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Could not validate credentials"


@pytest.mark.asyncio
async def test_jwt_valid_token_succeeds(client, db_session):
    """Un token JWT válido (8 horas) debe permitir el acceso normalmente."""
    user = await _seed_test_user(db_session)

    valid_token = security.create_access_token(
        data={"sub": user.username, "role": "Administradora", "permissions": []},
        expires_delta=timedelta(minutes=480),
    )

    resp = await client.get(
        "/api/usuarios",
        headers={"Authorization": f"Bearer {valid_token}"},
    )
    assert resp.status_code == 200


# ===========================================================================
# FRENTE 2: Bitácora de Auditoría
# ===========================================================================

@pytest.mark.asyncio
async def test_audit_service_log_action(db_session):
    """Verifica que log_action registre en bitacora_auditoria correctamente."""
    user = await _seed_test_user(db_session)

    await log_action(
        db_session,
        id_usuario=user.id_usuario,
        tabla="producto",
        accion="CREAR",
        descripcion="Prueba directa de log_action",
    )
    await db_session.commit()

    res = await db_session.execute(
        select(BitacoraAuditoria).where(BitacoraAuditoria.id_usuario == user.id_usuario)
    )
    logs = res.scalars().all()
    assert len(logs) == 1
    assert logs[0].tabla_afectada == "producto"
    assert logs[0].accion == "CREAR"
    assert logs[0].descripcion == "Prueba directa de log_action"


@pytest.mark.asyncio
async def test_audit_login_registers_entry(client, db_session):
    """El login exitoso debe registrar un evento en bitacora_auditoria."""
    user = await _seed_test_user(db_session)

    resp = await client.post(
        "/api/auth/login",
        data={"username": user.username, "password": "secret123"},
    )
    assert resp.status_code == 200

    res = await db_session.execute(
        select(BitacoraAuditoria).where(
            BitacoraAuditoria.id_usuario == user.id_usuario,
            BitacoraAuditoria.accion == "LOGIN",
        )
    )
    entry = res.scalar_one_or_none()
    assert entry is not None
    assert entry.tabla_afectada == "sesion_usuario"
    assert f"'{user.username}'" in entry.descripcion


# ===========================================================================
# FRENTE 3: Protección contra Fuerza Bruta en Login (Persistida en BD)
# ===========================================================================

@pytest.mark.asyncio
async def test_brute_force_lockout_after_5_failures(client, db_session):
    """Tras 5 intentos fallidos consecutivos, se persiste el bloqueo en BD y el 6to intento responde 429."""
    from app.db.models import IntentoLogin

    await _seed_test_user(db_session)
    username = "admin_test"

    # Intentos 1 al 5 fallidos (credenciales erróneas -> 401)
    for i in range(5):
        resp = await client.post(
            "/api/auth/login",
            data={"username": username, "password": "wrong_password"},
        )
        assert resp.status_code == 401, f"Intento {i+1} debió ser 401"

    # Verificar persistencia real en la tabla `intento_login`
    stmt = select(IntentoLogin).where(IntentoLogin.username == username)
    result = await db_session.execute(stmt)
    db_record = result.scalar_one_or_none()

    assert db_record is not None, "El registro de intento_login debe persistirse en la BD"
    assert db_record.bloqueado_hasta is not None, "Debe tener fecha de bloqueo temporal"
    assert db_record.bloqueado_hasta > __import__("datetime").datetime.now(), "El bloqueo debe estar vigente en el futuro"

    # Intento 6: debe ser bloqueado con 429 Too Many Requests
    resp_locked = await client.post(
        "/api/auth/login",
        data={"username": username, "password": "wrong_password"},
    )
    assert resp_locked.status_code == 429
    assert "Cuenta bloqueada temporalmente" in resp_locked.json()["detail"]

    # Incluso con la contraseña correcta debe permanecer bloqueado por el registro en BD
    resp_correct_but_locked = await client.post(
        "/api/auth/login",
        data={"username": username, "password": "secret123"},
    )
    assert resp_correct_but_locked.status_code == 429


@pytest.mark.asyncio
async def test_successful_login_resets_failure_counter(client, db_session):
    """Un login exitoso reinicia el contador de intentos fallidos en la base de datos."""
    from app.db.models import IntentoLogin

    await _seed_test_user(db_session)
    username = "admin_test"

    # 3 intentos fallidos
    for _ in range(3):
        resp = await client.post(
            "/api/auth/login",
            data={"username": username, "password": "wrong_password"},
        )
        assert resp.status_code == 401

    # Verificar en BD que hay 3 intentos acumulados
    stmt = select(IntentoLogin).where(IntentoLogin.username == username)
    res_pre = await db_session.execute(stmt)
    rec_pre = res_pre.scalar_one_or_none()
    assert rec_pre is not None
    assert rec_pre.intentos_fallidos == 3
    assert rec_pre.bloqueado_hasta is None

    # Login exitoso
    resp_ok = await client.post(
        "/api/auth/login",
        data={"username": username, "password": "secret123"},
    )
    assert resp_ok.status_code == 200

    # Verificar en BD que los intentos se reiniciaron a 0
    await db_session.refresh(rec_pre)
    assert rec_pre.intentos_fallidos == 0
    assert rec_pre.bloqueado_hasta is None


@pytest.mark.asyncio
async def test_lockout_persists_across_independent_service_instances(db_session):
    """Simula reinicio o múltiples réplicas: el bloqueo persiste y es leído por una nueva instancia del servicio."""
    from datetime import datetime, timedelta
    from app.db.models import IntentoLogin
    from app.repositories.login_attempt_repository import LoginAttemptRepositoryImpl
    from app.services.login_security_service import LoginSecurityService
    from fastapi import HTTPException

    username = "persisted_attacker"

    # Instancia 1: Registra 5 fallos y activa bloqueo
    repo1 = LoginAttemptRepositoryImpl(db_session)
    service1 = LoginSecurityService(repo1)

    for _ in range(5):
        await service1.record_failure(username)

    # Simular reinicio creando una instancia totalmente nueva de servicio y repo con el mismo DB
    repo2 = LoginAttemptRepositoryImpl(db_session)
    service2 = LoginSecurityService(repo2)

    # La nueva instancia debe detectar el bloqueo directamente desde la base de datos
    with pytest.raises(HTTPException) as exc_info:
        await service2.check_lockout(username)

    assert exc_info.value.status_code == 429
    assert "Cuenta bloqueada temporalmente" in exc_info.value.detail

