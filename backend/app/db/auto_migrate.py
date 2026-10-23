"""Módulo de inicialización automática de esquema y versiones de Alembic al arrancar."""
import os
import sys
import time
import logging
from alembic.config import Config
from alembic import command
from sqlalchemy import create_engine, text, inspect
from app.core.config import settings

logger = logging.getLogger("auto_migrate")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


def run_auto_migrate():
    raw_url = settings.DATABASE_URL
    if raw_url.startswith("postgresql+asyncpg://"):
        sync_url = raw_url.replace("postgresql+asyncpg://", "postgresql://", 1)
    elif raw_url.startswith("sqlite+aiosqlite://"):
        sync_url = raw_url.replace("sqlite+aiosqlite://", "sqlite://", 1)
    else:
        sync_url = raw_url

    ini_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "alembic.ini"))
    alembic_cfg = Config(ini_path)

    # Esperar conexión a la base de datos
    max_retries = 20
    sync_engine = None
    for attempt in range(1, max_retries + 1):
        try:
            sync_engine = create_engine(sync_url, pool_pre_ping=True)
            with sync_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Conexión con base de datos exitosa.")
            break
        except Exception as exc:
            logger.warning(f"Esperando a la base de datos (intento {attempt}/{max_retries}): {exc}")
            time.sleep(2)
    else:
        logger.error("No se pudo conectar a la base de datos tras múltiples intentos.")
        sys.exit(1)

    try:
        with sync_engine.connect() as conn:
            insp = inspect(conn)
            tables = insp.get_table_names()
            has_usuario = "usuario" in tables
            has_alembic = "alembic_version" in tables
            current_version = None
            if has_alembic:
                res = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).fetchone()
                if res and res[0]:
                    current_version = res[0]

        logger.info(
            f"Estado inicial DB: has_usuario={has_usuario}, has_alembic={has_alembic}, "
            f"current_version={current_version}"
        )

        if has_usuario and (not has_alembic or not current_version):
            # La base de datos viene precargada de init.sql pero no tiene alembic_version
            logger.info("Base de datos inicializada desde init.sql sin alembic_version. Ejecutando 'alembic stamp head'...")
            command.stamp(alembic_cfg, "head")
            logger.info("Alembic stamp completado con éxito.")
        else:
            # Base existente con alembic_version o base vacía: upgrade head
            logger.info("Ejecutando 'alembic upgrade head'...")
            command.upgrade(alembic_cfg, "head")
            logger.info("Alembic upgrade completado con éxito.")

        # Verificar versión final
        with sync_engine.connect() as conn:
            final_res = conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1")).fetchone()
            final_ver = final_res[0] if final_res else None
            logger.info(f"Versión final de Alembic en base de datos: {final_ver}")

    except Exception as e:
        logger.error(f"Error durante auto_migrate: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    run_auto_migrate()

