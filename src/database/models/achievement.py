"""
Achievement Models
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import BigInteger, String, Integer, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


class Achievement(Base):
    """Achievement definition model"""
    
    __tablename__ = "achievements"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    
    # Category and rarity
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    rarity: Mapped[str] = mapped_column(String(20), default="bronze")  # bronze, silver, gold, diamond, platinum
    
    # Requirements
    requirement_value: Mapped[int] = mapped_column(Integer, default=1)
    
    # Reward
    reward_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0"))
    
    # Visual
    emoji: Mapped[str] = mapped_column(String(10), default="🏆")
    icon_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # User achievements
    user_achievements: Mapped[list["UserAchievement"]] = relationship(
        "UserAchievement",
        back_populates="achievement"
    )
    
    def __repr__(self) -> str:
        return f"<Achievement(name={self.name}, category={self.category})>"


class UserAchievement(Base):
    """User's unlocked achievements"""
    
    __tablename__ = "user_achievements"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    achievement_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("achievements.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    unlocked_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="achievements")
    achievement: Mapped["Achievement"] = relationship("Achievement", back_populates="user_achievements")
    
    def __repr__(self) -> str:
        return f"<UserAchievement(user={self.user_id}, achievement={self.achievement_id})>"
