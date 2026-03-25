"""
Factory Worker Model
"""
from datetime import datetime
from typing import Optional

from sqlalchemy import BigInteger, String, Integer, Numeric, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


class FactoryWorker(Base):
    """Factory worker model"""
    
    __tablename__ = "factory_workers"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    
    owner_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    worker_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Worker stats
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, default=0)
    
    # Status
    status: Mapped[str] = mapped_column(String(20), default="idle")  # idle, working, completed
    work_end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Equipment
    shield_expires: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        foreign_keys=[owner_id],
        back_populates="owned_workers"
    )
    worker: Mapped["User"] = relationship(
        "User",
        foreign_keys=[worker_id],
        back_populates="worker_jobs"
    )
    
    def __repr__(self) -> str:
        return (
            f"<FactoryWorker(owner={self.owner_id}, "
            f"worker={self.worker_id}, status={self.status})>"
        )
    
    @property
    def has_shield(self) -> bool:
        """Check if worker has active shield"""
        if not self.shield_expires:
            return False
        return datetime.utcnow() < self.shield_expires
    
    @property
    def is_working(self) -> bool:
        """Check if worker is currently working"""
        return self.status == "working"
    
    @property
    def time_remaining(self) -> Optional[int]:
        """Get work time remaining in seconds"""
        if not self.work_end_time or not self.is_working:
            return None
        remaining = int((self.work_end_time - datetime.utcnow()).total_seconds())
        return max(0, remaining)
