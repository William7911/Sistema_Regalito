import sys
import os

# Forzamos a Python a reconocer la carpeta raíz del proyecto
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from app.db.database import engine, Base, SessionLocal
from app.db.models import User, Product
from passlib.context import CryptContext

# ... (El resto de tu código se queda exactamente igual)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def init_db():
    print("Creando tablas en la base de datos...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas exitosamente.")

    db = SessionLocal()
    try:
        # Verificar si ya existe un usuario admin
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            hashed_password = pwd_context.hash("admin123")
            new_admin = User(
                username="admin", 
                password_hash=hashed_password, 
                role="Administrador", 
                is_active=True
            )
            db.add(new_admin)
            print("Usuario administrador creado (admin / admin123).")

        # Verificar si existe un producto de prueba
        producto = db.query(Product).filter(Product.barcode == "123456789").first()
        if not producto:
            nuevo_producto = Product(
                name="Cuaderno Universitario 100 hojas",
                barcode="123456789",
                price=15.50,
                stock=50,
                min_stock=10
            )
            db.add(nuevo_producto)
            print("Producto de prueba creado en inventario.")

        db.commit()
        print("Datos iniciales insertados correctamente.")
    except Exception as e:
        print(f"Error al inicializar datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()