"""agregar_fecha_creacion_a_usuario

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-15

Aditiva y preserva los datos existentes:
- Agrega la columna `fecha_creacion` a la tabla `usuario` para soportar
  filtros de fecha (desde/hasta) en el módulo de Usuarios.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuario",
        sa.Column(
            "fecha_creacion",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("usuario", "fecha_creacion")