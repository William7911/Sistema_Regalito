import asyncio
import os
import sys

# Asegurar que el directorio raíz de la app esté en el sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from app.db.database import AsyncSessionLocal
from app.db.models import Usuario, Rol
from app.core.security import get_password_hash

async def seed_admin():
    async with AsyncSessionLocal() as session:
        # 1. Asegurar que exista el rol "Administradora"
        result_rol = await session.execute(select(Rol).where(Rol.nombre == "Administradora"))
        rol_admin = result_rol.scalar_one_or_none()
        
        if not rol_admin:
            print("El rol 'Administradora' no existe. Creándolo...")
            rol_admin = Rol(
                nombre="Administradora", 
                descripcion="Acceso total al sistema", 
                estado="Activo"
            )
            session.add(rol_admin)
            await session.flush()  # Para obtener el ID autogenerado si no lo tiene explícito
            print(f"Rol creado exitosamente (ID: {rol_admin.id_rol}).")
            
        # 2. Buscar si existe el usuario "admin"
        result_user = await session.execute(select(Usuario).where(Usuario.username == "admin"))
        user_admin = result_user.scalar_one_or_none()
        
        if not user_admin:
            print("El usuario 'admin' no existe. Creándolo...")
            user_admin = Usuario(
                id_rol=rol_admin.id_rol,
                nombre_completo="Super Administrador",
                username="admin",
                password_hash=get_password_hash("Admin123!"),
                estado="Activo"
            )
            session.add(user_admin)
            print("Usuario 'admin' creado exitosamente.")
        else:
            print("El usuario 'admin' ya existe. Actualizando la contraseña a 'Admin123!'...")
            user_admin.password_hash = get_password_hash("Admin123!")
            # Asegurar que esté activo y con el rol correcto
            user_admin.estado = "Activo"
            user_admin.id_rol = rol_admin.id_rol
            
        # 3. Guardar cambios en la base de datos
        await session.commit()
        print("¡Proceso de seeding finalizado con éxito!")

if __name__ == "__main__":
    asyncio.run(seed_admin())
