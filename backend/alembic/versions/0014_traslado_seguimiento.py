"""traslado_seguimiento

Revision ID: 0014
Revises: 0013
Create Date: 2026-10-23

Ampliación de la tabla traslado_inventario para trazabilidad operativa de traslados:
- estado (En tránsito, Recibido, Cancelado)
- id_usuario_envia (referencia a usuario)
- id_usuario_recibe (referencia a usuario)
- fecha_recepcion (timestamp de recepción en destino)
- observaciones (texto de justificación)
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0014"
down_revision: Union[str, None] = "0013"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "traslado_inventario",
        sa.Column("estado", sa.String(20), nullable=False, server_default="En tránsito")
    )
    op.add_column(
        "traslado_inventario",
        sa.Column("id_usuario_envia", sa.Integer(), sa.ForeignKey("usuario.id_usuario"), nullable=True)
    )
    op.add_column(
        "traslado_inventario",
        sa.Column("id_usuario_recibe", sa.Integer(), sa.ForeignKey("usuario.id_usuario"), nullable=True)
    )
    op.add_column(
        "traslado_inventario",
        sa.Column("fecha_recepcion", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "traslado_inventario",
        sa.Column("observaciones", sa.Text(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("traslado_inventario", "observaciones")
    op.drop_column("traslado_inventario", "fecha_recepcion")
    op.drop_column("traslado_inventario", "id_usuario_recibe")
    op.drop_column("traslado_inventario", "id_usuario_envia")
    op.drop_column("traslado_inventario", "estado")

