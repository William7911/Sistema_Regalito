"""usuario_email_y_recuperacion_password

Revision ID: 0017
Revises: 0016
Create Date: 2026-10-30

Agrega columna de correo a usuario y tabla de códigos de recuperación:
- usuario.email: VARCHAR(100) UNIQUE
- codigo_recuperacion: almacenamiento seguro de códigos OTP de 6 dígitos
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "0017"
down_revision: Union[str, None] = "0016"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = insp.get_table_names()

    # 1. Agregar columna email a la tabla usuario si no existe
    if "usuario" in tables:
        columns = [c["name"] for c in insp.get_columns("usuario")]
        if "email" not in columns:
            op.add_column("usuario", sa.Column("email", sa.String(100), nullable=True))
            op.create_unique_constraint("uq_usuario_email", "usuario", ["email"])

        # Poblar correos de usuarios existentes si están vacíos
        bind.execute(
            sa.text(
                "UPDATE usuario SET email = 'abimaely3@gmail.com' WHERE username = 'admin' AND email IS NULL"
            )
        )
        bind.execute(
            sa.text(
                "UPDATE usuario SET email = 'cajera@tiendaelregalito.gt' WHERE username = 'cajera' AND email IS NULL"
            )
        )
        bind.execute(
            sa.text(
                "UPDATE usuario SET email = 'bodega@tiendaelregalito.gt' WHERE username = 'bodega' AND email IS NULL"
            )
        )

    # 2. Crear tabla codigo_recuperacion si no existe
    if "codigo_recuperacion" not in tables:
        op.create_table(
            "codigo_recuperacion",
            sa.Column("id_codigo", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column(
                "id_usuario",
                sa.Integer(),
                sa.ForeignKey("usuario.id_usuario", ondelete="CASCADE"),
                nullable=False,
            ),
            sa.Column("codigo", sa.String(6), nullable=False),
            sa.Column("expira_en", sa.DateTime(), nullable=False),
            sa.Column("usado", sa.Boolean(), nullable=False, server_default=sa.text("false")),
            sa.Column("fecha_creacion", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        )
        op.create_index(
            "idx_codigo_recuperacion_usuario", "codigo_recuperacion", ["id_usuario"]
        )
        op.create_index(
            "idx_codigo_recuperacion_codigo", "codigo_recuperacion", ["codigo"]
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    tables = insp.get_table_names()

    if "codigo_recuperacion" in tables:
        op.drop_table("codigo_recuperacion")

    if "usuario" in tables:
        columns = [c["name"] for c in insp.get_columns("usuario")]
        if "email" in columns:
            op.drop_constraint("uq_usuario_email", "usuario", type_="unique")
            op.drop_column("usuario", "email")

