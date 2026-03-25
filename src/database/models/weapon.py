"""
Weapon Models
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import BigInteger, String, Integer, Numeric, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


class Weapon(Base):
    """Weapon definition model"""
    
    __tablename__ = "weapons"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Stats
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    rob_power: Mapped[int] = mapped_column(Integer, nullable=False)
    kill_power: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Visual
    emoji: Mapped[str] = mapped_column(String(10), default="🔫")
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # User weapons
    user_weapons: Mapped[List["UserWeapon"]] = relationship("UserWeapon", back_populates="weapon")
    
    def __repr__(self) -> str:
        return f"<Weapon(name={self.name}, price={self.price})>"


class UserWeapon(Base):
    """User's weapon inventory"""
    
    __tablename__ = "user_weapons"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    weapon_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("weapons.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    equipped: Mapped[bool] = mapped_column(Boolean, default=False)
    purchased_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="weapons")
    weapon: Mapped["Weapon"] = relationship("Weapon", back_populates="user_weapons")
    
    def __repr__(self) -> str:
        return f"<UserWeapon(user={self.user_id}, weapon={self.weapon_id}, equipped={self.equipped})>"
