"""visita_seguimiento_formulario

Revision ID: 0015
Revises: 0014
Create Date: 2026-10-23

Ampliación del módulo de visitas de seguimiento y evaluación de módulos:
- Permite que id_cliente en visita_seguimiento sea opcional (nullable), ya que
  la visita la responde directamente el dueño del negocio / representante.
- Columnas nuevas en visita_seguimiento: lugar, nombre_representante,
  cargo_representante, calificacion_general (1 a 5).
- Soporte para estado 'Borrador' en visita_seguimiento.
- Columna nueva en visita_modulo_evaluacion: resultado (Conforme, Modificar, Agregar).
- Restricción de unicidad (id_visita, nombre_modulo) en visita_modulo_evaluacion.
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0015"
down_revision: Union[str, None] = "0014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. visita_seguimiento: id_cliente nullable
    op.alter_column(
        "visita_seguimiento",
        "id_cliente",
        existing_type=sa.Integer(),
        nullable=True
    )

    # 2. Columnas adicionales en visita_seguimiento
    op.add_column("visita_seguimiento", sa.Column("lugar", sa.String(150), nullable=True))
    op.add_column("visita_seguimiento", sa.Column("nombre_representante", sa.String(150), nullable=True))
    op.add_column("visita_seguimiento", sa.Column("cargo_representante", sa.String(100), nullable=True))
    op.add_column("visita_seguimiento", sa.Column("calificacion_general", sa.SmallInteger(), nullable=True))

    # 3. visita_modulo_evaluacion: resultado y unicidad
    op.add_column("visita_modulo_evaluacion", sa.Column("resultado", sa.String(20), nullable=True))
    op.create_unique_constraint(
        "uq_visita_modulo",
        "visita_modulo_evaluacion",
        ["id_visita", "nombre_modulo"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_visita_modulo", "visita_modulo_evaluacion", type_="unique")
    op.drop_column("visita_modulo_evaluacion", "resultado")
    op.drop_column("visita_seguimiento", "calificacion_general")
    op.drop_column("visita_seguimiento", "cargo_representante")
    op.drop_column("visita_seguimiento", "nombre_representante")
    op.drop_column("visita_seguimiento", "lugar")
    op.alter_column(
        "visita_seguimiento",
        "id_cliente",
        existing_type=sa.Integer(),
        nullable=False
    )
