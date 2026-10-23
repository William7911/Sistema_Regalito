"""sync_tables_queue_and_metadata

Revision ID: 0016
Revises: 0015
Create Date: 2026-10-23

Tablas de contingencia y sincronización offline:
- sync_cache_metadata: metadata de sincronización de caché local por tabla
- sync_queue: cola de transacciones offline pendientes de sincronización
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0016"
down_revision: Union[str, None] = "0015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = insp.get_table_names()

    if "sync_cache_metadata" not in tables:
        op.create_table(
            "sync_cache_metadata",
            sa.Column("id_sync", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("tabla", sa.String(50), nullable=False, unique=True),
            sa.Column("registros_sincronizados", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("fecha_sincronizacion", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index("idx_sync_cache_metadata_tabla", "sync_cache_metadata", ["tabla"])

    if "sync_queue" not in tables:
        op.create_table(
            "sync_queue",
            sa.Column("id_sync", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("idempotency_key", sa.String(36), nullable=False, unique=True),
            sa.Column("entidad", sa.String(50), nullable=False),
            sa.Column("entidad_id", sa.Integer(), nullable=False),
            sa.Column("operacion", sa.String(20), nullable=False),
            sa.Column("payload", sa.Text(), nullable=False),
            sa.Column("estado", sa.String(20), nullable=False, server_default="PENDIENTE"),
            sa.Column("intentos", sa.Integer(), server_default="0"),
            sa.Column("ultimo_error", sa.Text(), nullable=True),
            sa.Column("creado_en", sa.DateTime(), server_default=sa.func.now()),
            sa.Column("actualizado_en", sa.DateTime(), server_default=sa.func.now()),
        )
        op.create_index("idx_sync_queue_idempotency", "sync_queue", ["idempotency_key"])
        op.create_index("idx_sync_queue_estado", "sync_queue", ["estado"])


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = insp.get_table_names()

    if "sync_queue" in tables:
        op.drop_table("sync_queue")
    if "sync_cache_metadata" in tables:
        op.drop_table("sync_cache_metadata")

