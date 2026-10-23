"""persistencia_bloqueo_fuerza_bruta

Revision ID: 0008
Revises: 0007
Create Date: 2026-09-20

Persistencia de intentos fallidos y bloqueo temporal de fuerza bruta en base de datos.
Crea la tabla `intento_login` con clave primaria serial y restricción UNIQUE en username.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Crear tabla intento_login con secuencia automática y restricción UNIQUE en username
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS intento_login (
            id_intento SERIAL PRIMARY KEY,
            username VARCHAR(50) NOT NULL UNIQUE,
            intentos_fallidos INT NOT NULL DEFAULT 0,
            bloqueado_hasta TIMESTAMP WITHOUT TIME ZONE,
            ultimo_intento TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW()
        );
        """
    )
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_intento_login_username ON intento_login (username);
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS intento_login CASCADE;")

