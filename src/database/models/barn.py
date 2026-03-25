"""
Barn (Inventory) Models
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import BigInteger, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


class Barn(Base):
    """Barn (inventory) model"""
    
    __tablename__ = "barns"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    capacity: Mapped[int] = mapped_column(Integer, default=500)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="barn")
    items: Mapped[List["BarnItem"]] = relationship(
        "BarnItem",
        back_populates="barn",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Barn(user_id={self.user_id}, capacity={self.capacity})>"
    
    @property
    def used_space(self) -> int:
        """Calculate used space"""
        return sum(item.quantity for item in self.items)
    
    @property
    def available_space(self) -> int:
        """Calculate available space"""
        return self.capacity - self.used_space
    
    @property
    def is_full(self) -> bool:
        """Check if barn is full"""
        return self.used_space >= self.capacity


class BarnItem(Base):
    """Individual barn item"""
    
    __tablename__ = "barn_items"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    barn_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("barns.user_id", ondelete="CASCADE"),
        nullable=False
    )
    
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)  # crop, recipe
    item_name: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=0)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    barn: Mapped["Barn"] = relationship("Barn", back_populates="items")
    
    def __repr__(self) -> str:
        return f"<BarnItem(barn={self.barn_id}, item={self.item_name}, qty={self.quantity})>"
