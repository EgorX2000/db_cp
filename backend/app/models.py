from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from .database import Base


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    phone = Column(String(25))
    role = Column(String(25), nullable=False)

    personal_data = relationship("UsersPersonalData", back_populates="user",
                                 uselist=False, cascade="all, delete-orphan")


class UsersPersonalData(Base):
    __tablename__ = "users_personal_data"
    user_id = Column(Integer, ForeignKey(
        "users.id", ondelete="CASCADE"), primary_key=True)
    country = Column(String(100))
    city = Column(String(100))
    address = Column(Text)
    postal_code = Column(String(20))
    birth_date = Column(Date)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())
    user = relationship("Users", back_populates="personal_data")


class EquipmentCategories(Base):
    __tablename__ = "equipment_categories"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("equipment_categories.id"))
    created_at = Column(DateTime, server_default=func.now())

    parent = relationship("EquipmentCategories", remote_side=[id])
    children = relationship("EquipmentCategories")


class EquipmentModels(Base):
    __tablename__ = "equipment_models"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    brand = Column(String(100))
    rental_price_per_day = Column(Numeric(10, 2), nullable=False)
    deposit_amount = Column(Numeric(10, 2), default=0)


class Equipment(Base):
    __tablename__ = "equipment"
    id = Column(Integer, primary_key=True)
    category_id = Column(Integer, ForeignKey(
        "equipment_categories.id"), nullable=False)
    model_id = Column(Integer, ForeignKey(
        "equipment_models.id"), nullable=False)
    inventory_number = Column(String(50), unique=True, nullable=False)
    status = Column(String(25), nullable=False, default="Доступно")

    category = relationship("EquipmentCategories")
    model = relationship("EquipmentModels")


class Rentals(Base):
    __tablename__ = "rentals"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    employee_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    return_date = Column(Date)
    status = Column(String(25), nullable=False, default="Активен")
    total_cost = Column(Numeric(10, 2))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(),
                        onupdate=func.now())

    client = relationship("Users", foreign_keys=[user_id])
    employee = relationship("Users", foreign_keys=[employee_id])
    items = relationship("RentalItems", back_populates="rental",
                         cascade="all, delete-orphan")


class RentalItems(Base):
    __tablename__ = "rental_items"
    id = Column(Integer, primary_key=True)
    rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=False)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    damage_fee = Column(Numeric(10, 2), default=0)
    created_at = Column(DateTime, server_default=func.now())

    rental = relationship("Rentals", back_populates="items")
    equipment = relationship("Equipment")


class Payments(Base):
    __tablename__ = "payments"
    id = Column(Integer, primary_key=True)
    rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    payment_method = Column(String(25), nullable=False)
    payment_date = Column(DateTime, server_default=func.now())


class Damages(Base):
    __tablename__ = "damages"
    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    rental_id = Column(Integer, ForeignKey("rentals.id"), nullable=False)
    description = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())


class Repairs(Base):
    __tablename__ = "repairs"
    id = Column(Integer, primary_key=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    description = Column(Text, nullable=False)
    cost = Column(Numeric(10, 2))
    status = Column(String(25), default="В процессе")


class AuditLog(Base):
    __tablename__ = "audit_log"
    id = Column(Integer, primary_key=True)
    table_name = Column(String(50), nullable=False)
    record_id = Column(Integer, nullable=False)
    operation = Column(String(10), nullable=False)
    old_data = Column(JSONB)
    new_data = Column(JSONB)
    changed_at = Column(DateTime, server_default=func.now())
