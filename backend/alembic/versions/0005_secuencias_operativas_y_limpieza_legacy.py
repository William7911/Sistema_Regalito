"""secuencias_operativas_y_limpieza_legacy

Revision ID: 0005
Revises: 0004
Create Date: 2026-09-17

1. Agrega secuencias PostgreSQL automáticas para las tablas operativas:
   - venta (id_venta)
   - detalle_venta (id_detalle_venta)
   - pago_venta (id_pago)
   - merma (id_merma)
   - detalle_merma (id_detalle_merma)
   - cierre_caja_ciegas (id_cierre)
   - detalle_arqueo_efectivo (id_detalle_arqueo)
   - movimiento_caja (id_movimiento)
2. Elimina de forma segura las tablas legacy huérfanas en inglés (cash_registers, products, categories, users, roles, departments)
   reemplazadas por el modelo DERCAS oficial en español (caja, producto, categoria, usuario, rol, departamento_geografico).
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_TABLE_SEQUENCES = [
    ("venta", "id_venta"),
    ("detalle_venta", "id_detalle_venta"),
    ("pago_venta", "id_pago"),
    ("merma", "id_merma"),
    ("detalle_merma", "id_detalle_merma"),
    ("cierre_caja_ciegas", "id_cierre"),
    ("detalle_arqueo_efectivo", "id_detalle_arqueo"),
    ("movimiento_caja", "id_movimiento"),
]


def upgrade() -> None:
    # 1. Crear secuencias seguras para tablas operativas
    for table_name, pk_name in _TABLE_SEQUENCES:
        seq_name = f"{table_name}_{pk_name}_seq"
        op.execute(
            f"""
            DO $$
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_class WHERE relname = '{seq_name}') THEN
                    CREATE SEQUENCE {seq_name};
                    ALTER TABLE {table_name} ALTER COLUMN {pk_name} SET DEFAULT nextval('{seq_name}');
                    ALTER SEQUENCE {seq_name} OWNED BY {table_name}.{pk_name};
                    PERFORM setval('{seq_name}', COALESCE((SELECT MAX({pk_name}) FROM {table_name}), 0) + 1, false);
                END IF;
            END $$;
            """
        )

    # 2. Limpieza segura de tablas huérfanas en inglés (orden respetando FKs internas entre ellas)
    op.execute("DROP TABLE IF EXISTS cash_registers CASCADE;")
    op.execute("DROP TABLE IF EXISTS products CASCADE;")
    op.execute("DROP TABLE IF EXISTS categories CASCADE;")
    op.execute("DROP TABLE IF EXISTS users CASCADE;")
    op.execute("DROP TABLE IF EXISTS roles CASCADE;")
    op.execute("DROP TABLE IF EXISTS departments CASCADE;")


def downgrade() -> None:
    for table_name, pk_name in _TABLE_SEQUENCES:
        seq_name = f"{table_name}_{pk_name}_seq"
        op.execute(
            f"""
            ALTER TABLE {table_name} ALTER COLUMN {pk_name} DROP DEFAULT;
            DROP SEQUENCE IF EXISTS {seq_name} CASCADE;
            """
        )

