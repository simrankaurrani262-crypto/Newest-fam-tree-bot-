"""
User Model
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import BigInteger, String, Boolean, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


class User(Base):
    """User model"""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    language: Mapped[str] = mapped_column(String(5), default="en")
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False)
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)
    banned_until: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ban_reason: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    # Profile
    profile_pic_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    custom_gifs_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    last_active: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    economy: Mapped["Economy"] = relationship("Economy", back_populates="user", uselist=False)
    garden: Mapped["Garden"] = relationship("Garden", back_populates="user", uselist=False)
    barn: Mapped["Barn"] = relationship("Barn", back_populates="user", uselist=False)
    
    # Family relationships
    family_relations: Mapped[List["FamilyRelation"]] = relationship(
        "FamilyRelation",
        foreign_keys="FamilyRelation.user_id",
        back_populates="user"
    )
    
    # Friendships
    friendships: Mapped[List["Friendship"]] = relationship(
        "Friendship",
        foreign_keys="Friendship.user_id",
        back_populates="user"
    )
    
    # Weapons
    weapons: Mapped[List["UserWeapon"]] = relationship("UserWeapon", back_populates="user")
    
    # Factory
    owned_workers: Mapped[List["FactoryWorker"]] = relationship(
        "FactoryWorker",
        foreign_keys="FactoryWorker.owner_id",
        back_populates="owner"
    )
    worker_jobs: Mapped[List["FactoryWorker"]] = relationship(
        "FactoryWorker",
        foreign_keys="FactoryWorker.worker_id",
        back_populates="worker"
    )
    
    # Stands
    stands: Mapped[List["Stand"]] = relationship("Stand", back_populates="seller")
    
    # Insurances
    insurances: Mapped[List["Insurance"]] = relationship(
        "Insurance",
        foreign_keys="Insurance.insurer_id",
        back_populates="insurer"
    )
    
    # Achievements
    achievements: Mapped[List["UserAchievement"]] = relationship("UserAchievement", back_populates="user")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"
    
    @property
    def display_name(self) -> str:
        """Get display name for user"""
        if self.username:
            return f"@{self.username}"
        if self.first_name:
            return self.first_name
        return f"User{self.telegram_id}"
