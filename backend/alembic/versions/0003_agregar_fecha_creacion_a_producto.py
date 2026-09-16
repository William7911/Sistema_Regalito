"""agregar_fecha_creacion_a_producto

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-15

Aditiva y preserva los datos existentes:
- Agrega la columna `fecha_creacion` a la tabla `producto` para soportar
  filtros de fecha (desde/hasta) en el módulo de Catálogos (Productos).
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "producto",
        sa.Column(
            "fecha_creacion",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("producto", "fecha_creacion")