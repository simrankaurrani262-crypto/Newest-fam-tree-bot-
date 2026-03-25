"""
Transaction Model
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import BigInteger, String, Numeric, DateTime, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column

from src.database.connection import Base


class Transaction(Base):
    """Transaction history model"""
    
    __tablename__ = "transactions"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    from_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True
    )
    to_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=True
    )
    
    amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)  # rob, kill, trade, gift, daily, etc.
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return (
            f"<Transaction(from={self.from_user_id}, "
            f"to={self.to_user_id}, amount={self.amount}, type={self.type})>"
        )
