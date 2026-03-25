"""
Economy Model
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import BigInteger, Numeric, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


class Economy(Base):
    """Economy model for user finances"""
    
    __tablename__ = "economy"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    # Balances
    balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    bank_balance: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    
    # Stats
    reputation: Mapped[int] = mapped_column(Integer, default=100)
    health: Mapped[int] = mapped_column(Integer, default=5)
    
    # Daily
    daily_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_daily_claim: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Gemstone
    current_gemstone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Job
    current_job: Mapped[str] = mapped_column(String(50), default="unemployed")
    
    # Combat stats
    equipped_weapon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Daily limits
    robbery_count_today: Mapped[int] = mapped_column(Integer, default=0)
    kill_count_today: Mapped[int] = mapped_column(Integer, default=0)
    last_limit_reset: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Totals
    total_earned: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    total_spent: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0"))
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="economy")
    
    def __repr__(self) -> str:
        return f"<Economy(user_id={self.user_id}, balance={self.balance})>"
    
    @property
    def net_worth(self) -> Decimal:
        """Calculate total net worth"""
        return self.balance + self.bank_balance
    
    @property
    def reputation_level(self) -> str:
        """Get reputation level"""
        if self.reputation < 50:
            return "criminal"
        elif self.reputation < 100:
            return "normal"
        elif self.reputation < 150:
            return "good"
        return "elite"
    
    @property
    def is_alive(self) -> bool:
        """Check if user is alive"""
        return self.health > 0
