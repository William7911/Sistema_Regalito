from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import User
import sys

engine = create_engine("postgresql://regalito_admin:Regalito_2026@localhost:5433/regalito_pos")
Session = sessionmaker(bind=engine)
db = Session()

user = db.query(User).filter(User.username == "admin").first()
if user:
    user.password_hash = "$2b$12$lPMl/5JWqwjk52e9mOo5e.gKKCXZ4OqO3Hs8nvOByzE8IXOo3BdKu"
    db.commit()
    print("Password updated successfully.")
else:
    print("User not found.")
db.close()
