import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from sqlalchemy import select

from app.db.models import ParametroSistema, Usuario, Rol
from app.services.configuracion_service import ConfiguracionService
from app.api.deps import UnitOfWork

pytestmark = pytest.mark.asyncio

async def _seed_data(db_session: AsyncSession):
    """Inserta datos de prueba necesarios para el Módulo de Configuración."""
    # 1. Roles
    rol_admin = Rol(id_rol=1, nombre="Administradora", descripcion="Acceso total", estado="Activo")
    rol_cajero = Rol(id_rol=2, nombre="Cajero", descripcion="Ventas en POS", estado="Activo")
    rol_bodeguero = Rol(id_rol=3, nombre="Bodeguero", descripcion="Gestión de inventario", estado="Activo")
    db_session.add_all([rol_admin, rol_cajero, rol_bodeguero])
    await db_session.flush()

    # 2. Usuarios
    admin_user = Usuario(id_usuario=1, id_rol=1, nombre_completo="Admin Test", username="admin", password_hash="hash", estado="Activo")
    cajero_user = Usuario(id_usuario=2, id_rol=2, nombre_completo="Cajero Test", username="cajero", password_hash="hash", estado="Activo")
    bodeguero_user = Usuario(id_usuario=3, id_rol=3, nombre_completo="Bodeguero Test", username="bodeguero", password_hash="hash", estado="Activo")
    db_session.add_all([admin_user, cajero_user, bodeguero_user])
    await db_session.flush()

    # 3. Parámetros del sistema por defecto
    param_nit = ParametroSistema(clave="NIT", valor="CF")
    param_razon = ParametroSistema(clave="Razón Social", valor="Mi Empresa")
    param_token = ParametroSistema(clave="Token FEL", valor="TOKEN_INICIAL_123")
    db_session.add_all([param_nit, param_razon, param_token])
    
    await db_session.commit()

async def test_admin_lee_y_actualiza_configuracion_exitosamente(db_session: AsyncSession):
    """Prueba que un usuario Administradora puede leer y modificar la configuración."""
    await _seed_data(db_session)
    uow = UnitOfWork(db_session)
    service = ConfiguracionService(uow)

    admin_user = await db_session.get(Usuario, 1)

    # 1. Validar lectura
    config_actual = await service.obtener_configuracion(usuario_actual=admin_user)
    assert config_actual["NIT"] == "CF"
    assert config_actual["Razón Social"] == "Mi Empresa"

    # 2. Validar actualización
    nuevos_parametros = {
        "NIT": "1234567-8",
        "Razón Social": "Nueva Empresa S.A.",
        "Token FEL": "NUEVO_TOKEN_SECRETO"
    }
    
    await service.actualizar_configuracion(nuevos_parametros, usuario_actual=admin_user)

    # 3. Validar persistencia en base de datos
    result_nit = await db_session.execute(select(ParametroSistema).where(ParametroSistema.clave == "NIT"))
    parametro_nit_db = result_nit.scalar_one()
    assert parametro_nit_db.valor == "1234567-8"

    result_razon = await db_session.execute(select(ParametroSistema).where(ParametroSistema.clave == "Razón Social"))
    parametro_razon_db = result_razon.scalar_one()
    assert parametro_razon_db.valor == "Nueva Empresa S.A."

async def test_validacion_estricta_parametros_criticos_vacios(db_session: AsyncSession):
    """Prueba que el sistema rechace actualizaciones si claves críticas vienen vacías."""
    await _seed_data(db_session)
    uow = UnitOfWork(db_session)
    service = ConfiguracionService(uow)
    
    admin_user = await db_session.get(Usuario, 1)

    # Parámetros inválidos (NIT y Razón Social vacíos)
    parametros_invalidos = {
        "NIT": "   ",
        "Razón Social": "",
        "Token FEL": "TOKEN_VALIDO"
    }

    with pytest.raises(HTTPException) as excinfo:
        await service.actualizar_configuracion(parametros_invalidos, usuario_actual=admin_user)
    
    assert excinfo.value.status_code == 400
    
    # 3. Validar que la BD quedó inalterada tras el rechazo
    result = await db_session.execute(select(ParametroSistema).where(ParametroSistema.clave == "NIT"))
    nit_db = result.scalar_one()
    assert nit_db.valor == "CF"  # Valor original, no fue modificado

async def test_rbac_deniega_acceso_cajero_y_bodeguero(db_session: AsyncSession):
    """Prueba que usuarios no administradores reciban HTTP 403 al intentar acceder."""
    await _seed_data(db_session)
    uow = UnitOfWork(db_session)
    service = ConfiguracionService(uow)

    cajero_user = await db_session.get(Usuario, 2)
    bodeguero_user = await db_session.get(Usuario, 3)

    nuevos_parametros = {"NIT": "12345"}

    # 1. Pruebas para Cajero (Lectura y Escritura)
    with pytest.raises(HTTPException) as excinfo_leer_cajero:
        await service.obtener_configuracion(usuario_actual=cajero_user)
    assert excinfo_leer_cajero.value.status_code == 403

    with pytest.raises(HTTPException) as excinfo_escribir_cajero:
        await service.actualizar_configuracion(nuevos_parametros, usuario_actual=cajero_user)
    assert excinfo_escribir_cajero.value.status_code == 403

    # 2. Pruebas para Bodeguero (Lectura y Escritura)
    with pytest.raises(HTTPException) as excinfo_leer_bodeguero:
        await service.obtener_configuracion(usuario_actual=bodeguero_user)
    assert excinfo_leer_bodeguero.value.status_code == 403

    with pytest.raises(HTTPException) as excinfo_escribir_bodeguero:
        await service.actualizar_configuracion(nuevos_parametros, usuario_actual=bodeguero_user)
    assert excinfo_escribir_bodeguero.value.status_code == 403
