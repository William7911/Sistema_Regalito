"""permisos_roles_usuarios

Revision ID: 0013
Revises: 0012
Create Date: 2026-10-23

Agrega permisos críticos de Seguridad y Administración:
- ROL_ADMIN: Gestión completa de roles y permisos.
- USUARIO_ADMIN: Gestión completa de usuarios.
Asigna ambos permisos al rol Administradora (id_rol = 1).
"""
from typing import Sequence, Union
from alembic import op

revision: str = "0013"
down_revision: Union[str, None] = "0012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO permiso (modulo, codigo, descripcion) VALUES
            ('Seguridad', 'ROL_ADMIN',     'Gestión completa de roles y permisos'),
            ('Seguridad', 'USUARIO_ADMIN', 'Gestión completa de usuarios')
        ON CONFLICT (codigo) DO NOTHING;
    """)
    op.execute("""
        INSERT INTO rol_permiso (id_rol, id_permiso)
        SELECT 1, id_permiso FROM permiso
        WHERE codigo IN ('ROL_ADMIN', 'USUARIO_ADMIN')
        ON CONFLICT DO NOTHING;
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM rol_permiso
        WHERE id_permiso IN (SELECT id_permiso FROM permiso WHERE codigo IN ('ROL_ADMIN', 'USUARIO_ADMIN'));
    """)
    op.execute("""
        DELETE FROM permiso
        WHERE codigo IN ('ROL_ADMIN', 'USUARIO_ADMIN');
    """)
