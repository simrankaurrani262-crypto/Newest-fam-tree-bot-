"""
Insurance Model
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import BigInteger, String, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


class Insurance(Base):
    """Insurance policy model"""
    
    __tablename__ = "insurances"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    insurer_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    insured_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Policy details
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # close_family, family, friend
    initial_payout: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    current_payout: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Timestamps
    purchased_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Status
    claimed: Mapped[bool] = mapped_column(default=False)
    claimed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    insurer: Mapped["User"] = relationship(
        "User",
        foreign_keys=[insurer_id],
        back_populates="insurances"
    )
    
    def __repr__(self) -> str:
        return (
            f"<Insurance(insurer={self.insurer_id}, "
            f"insured={self.insured_id}, type={self.type})>"
        )
    
    def calculate_current_payout(self) -> Decimal:
        """Calculate current payout with decay"""
        from src.core.constants import INSURANCE_DECAY_RATE
        
        hours_elapsed = (datetime.utcnow() - self.purchased_at).total_seconds() / 3600
        decay = Decimal(1 - INSURANCE_DECAY_RATE) ** hours_elapsed
        return self.initial_payout * decay
