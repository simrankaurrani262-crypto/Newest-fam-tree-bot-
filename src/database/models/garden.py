"""
Garden Models
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import BigInteger, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


class Garden(Base):
    """Garden model"""
    
    __tablename__ = "gardens"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    slots: Mapped[int] = mapped_column(Integer, default=9)
    max_slots: Mapped[int] = mapped_column(Integer, default=12)
    season: Mapped[str] = mapped_column(String(20), default="spring")
    last_season_change: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    
    # Orders completed (for slot expansion)
    orders_completed: Mapped[int] = mapped_column(Integer, default=0)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="garden")
    plots: Mapped[List["GardenPlot"]] = relationship(
        "GardenPlot",
        back_populates="garden",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Garden(user_id={self.user_id}, slots={self.slots})>"
    
    @property
    def empty_plots(self) -> int:
        """Count empty plots"""
        return self.slots - len(self.plots)


class GardenPlot(Base):
    """Individual garden plot"""
    
    __tablename__ = "garden_plots"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    garden_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("gardens.user_id", ondelete="CASCADE"),
        nullable=False
    )
    plot_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Crop info
    crop_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    planted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    ready_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_fertilized: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Relationships
    garden: Mapped["Garden"] = relationship("Garden", back_populates="plots")
    
    def __repr__(self) -> str:
        return (
            f"<GardenPlot(garden={self.garden_id}, "
            f"plot={self.plot_number}, crop={self.crop_type})>"
        )
    
    @property
    def is_empty(self) -> bool:
        """Check if plot is empty"""
        return self.crop_type is None
    
    @property
    def is_ready(self) -> bool:
        """Check if crop is ready to harvest"""
        if not self.ready_at:
            return False
        return datetime.utcnow() >= self.ready_at
    
    @property
    def time_remaining(self) -> Optional[int]:
        """Get time remaining in seconds"""
        if not self.ready_at or self.is_ready:
            return 0
        return int((self.ready_at - datetime.utcnow()).total_seconds())
