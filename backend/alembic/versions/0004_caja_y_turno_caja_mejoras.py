"""caja_y_turno_caja_mejoras

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-15

Aditiva y preserva los datos existentes:
- Agrega las columnas `monto_cierre` y `notas` a la tabla `turno_caja`.
- Crea secuencias para `id_turno` y `id_caja` para permitir inserciones automáticas.
- Asegura que las cajas activas tengan estado 'Activa'.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Columnas adicionales en turno_caja
    op.add_column(
        "turno_caja",
        sa.Column("monto_cierre", sa.Numeric(10, 2), nullable=True),
    )
    op.add_column(
        "turno_caja",
        sa.Column("notas", sa.String(255), nullable=True),
    )

    # 2. Secuencia para id_turno
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'turno_caja_id_turno_seq') THEN
                CREATE SEQUENCE turno_caja_id_turno_seq;
                ALTER TABLE turno_caja ALTER COLUMN id_turno SET DEFAULT nextval('turno_caja_id_turno_seq');
                ALTER SEQUENCE turno_caja_id_turno_seq OWNED BY turno_caja.id_turno;
                PERFORM setval('turno_caja_id_turno_seq', COALESCE((SELECT MAX(id_turno) FROM turno_caja), 0) + 1, false);
            END IF;
        END $$;
        """
    )

    # 3. Secuencia para id_caja
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = 'caja_id_caja_seq') THEN
                CREATE SEQUENCE caja_id_caja_seq;
                ALTER TABLE caja ALTER COLUMN id_caja SET DEFAULT nextval('caja_id_caja_seq');
                ALTER SEQUENCE caja_id_caja_seq OWNED BY caja.id_caja;
                PERFORM setval('caja_id_caja_seq', COALESCE((SELECT MAX(id_caja) FROM caja), 0) + 1, false);
            END IF;
        END $$;
        """
    )

    # 4. Homologar estado de caja semilla a 'Activa'
    op.execute(
        """
        UPDATE caja
        SET estado = 'Activa'
        WHERE estado IN ('Cerrada', 'Activo');
        """
    )


def downgrade() -> None:
    op.drop_column("turno_caja", "notas")
    op.drop_column("turno_caja", "monto_cierre")

