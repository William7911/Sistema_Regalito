"""crear_roles_departamentos_y_normalizar_usuarios

Revision ID: 0001
Revises:
Create Date: 2026-09-14

Aditiva y preserva los datos existentes:
- Crea las tablas `roles` y `departments`.
- Agrega columnas a `users` (name, lastname, code, role_id, department_id).
- Rellena (backfill) los usuarios existentes y enlaza rol/departamento por defecto.
- Elimina la columna `role` (texto) ya reemplazada por `role_id`.

Revision ID: 0001
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Tabla de roles
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(50), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_roles_name", "roles", ["name"], unique=True)

    # 2. Tabla de departamentos
    op.create_table(
        "departments",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_departments_name", "departments", ["name"], unique=True)

    # 3. Nuevas columnas en users (nullable inicialmente para backfill)
    op.add_column("users", sa.Column("name", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("lastname", sa.String(100), nullable=True))
    op.add_column("users", sa.Column("code", sa.String(30), nullable=True))
    op.add_column("users", sa.Column("role_id", sa.Integer(), nullable=True))
    op.add_column("users", sa.Column("department_id", sa.Integer(), nullable=True))

    # 4. Roles y departamentos por defecto
    op.execute(
        "INSERT INTO roles (name, description, is_active) VALUES "
        "('Admin', 'Administrador del sistema', TRUE), "
        "('Cajero', 'Operador de caja', TRUE)"
    )
    op.execute(
        "INSERT INTO departments (name, description, is_active) VALUES "
        "('General', 'Departamento general', TRUE)"
    )

    # 5. Backfill de usuarios existentes (preserva datos)
    op.execute(
        """
        UPDATE users
        SET name = username,
            lastname = '',
            code = 'U' || id::text,
            role_id = (SELECT id FROM roles WHERE name = CASE
                           WHEN role = 'Admin' THEN 'Admin'
                           ELSE 'Cajero' END),
            department_id = (SELECT id FROM departments ORDER BY id LIMIT 1)
        WHERE code IS NULL
        """
    )

    # 6. Columnas NOT NULL e índices de unicidad
    op.alter_column("users", "name", existing_type=sa.String(100), nullable=False)
    op.alter_column("users", "lastname", existing_type=sa.String(100), nullable=False)
    op.alter_column("users", "code", existing_type=sa.String(30), nullable=False)
    op.alter_column("users", "role_id", existing_type=sa.Integer(), nullable=False)
    op.alter_column("users", "department_id", existing_type=sa.Integer(), nullable=False)
    op.create_index("ix_users_code", "users", ["code"], unique=True)

    # 7. Llaves foráneas
    op.create_foreign_key("fk_users_role", "users", "roles", ["role_id"], ["id"])
    op.create_foreign_key(
        "fk_users_department", "users", "departments", ["department_id"], ["id"]
    )

    # 8. Eliminar la columna antigua `role` (texto)
    op.drop_column("users", "role")


def downgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(20), nullable=True))
    op.drop_constraint("fk_users_department", "users", type_="foreignkey")
    op.drop_constraint("fk_users_role", "users", type_="foreignkey")
    op.drop_index("ix_users_code", table_name="users")
    op.alter_column("users", "department_id", nullable=True)
    op.alter_column("users", "role_id", nullable=True)
    op.alter_column("users", "code", nullable=True)
    op.alter_column("users", "lastname", nullable=True)
    op.alter_column("users", "name", nullable=True)
    op.drop_column("users", "department_id")
    op.drop_column("users", "role_id")
    op.drop_column("users", "code")
    op.drop_column("users", "lastname")
    op.drop_column("users", "name")
    op.drop_index("ix_departments_name", table_name="departments")
    op.drop_table("departments")
    op.drop_index("ix_roles_name", table_name="roles")
    op.drop_table("roles")