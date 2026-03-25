"""
Trading/Marketplace Models
"""
from datetime import datetime

from sqlalchemy import BigInteger, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


class Stand(Base):
    """Marketplace stand listing"""
    
    __tablename__ = "stands"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    seller_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Item info
    crop_type: Mapped[str] = mapped_column(String(50), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_per_unit: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    seller: Mapped["User"] = relationship("User", back_populates="stands")
    
    def __repr__(self) -> str:
        return (
            f"<Stand(seller={self.seller_id}, "
            f"crop={self.crop_type}, qty={self.quantity})>"
        )
    
    @property
    def total_price(self) -> float:
        """Calculate total price"""
        return float(self.price_per_unit * self.quantity)
    
    @property
    def boxes(self) -> int:
        """Calculate number of boxes (50 per box)"""
        import math
        return math.ceil(self.quantity / 50)
