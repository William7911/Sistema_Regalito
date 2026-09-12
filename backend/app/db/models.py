from sqlalchemy import Column, Integer, String, Boolean, DECIMAL, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="Cajero", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    
    cash_registers = relationship("CashRegister", back_populates="user")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    barcode = Column(String(100), unique=True, index=True, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    current_stock = Column(Integer, default=0, nullable=False)
    min_stock = Column(Integer, default=5, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class CashRegister(Base):
    __tablename__ = "cash_registers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    opening_time = Column(DateTime, default=func.now())
    opening_amount = Column(DECIMAL(10, 2), nullable=False)
    petty_cash = Column(DECIMAL(10, 2), default=0, nullable=False)
    closing_time = Column(DateTime, nullable=True)
    blind_closing_amount = Column(DECIMAL(10, 2), nullable=True)
    status = Column(String(20), default="Abierta")

    user = relationship("User", back_populates="cash_registers")
