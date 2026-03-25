"""
Friendship Model
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.connection import Base


class Friendship(Base):
    """Friendship model (bidirectional)"""
    
    __tablename__ = "friendships"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    friend_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    
    # Interaction stats
    interaction_count: Mapped[int] = mapped_column(Integer, default=0)
    last_interaction: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="friendships"
    )
    friend: Mapped["User"] = relationship(
        "User",
        foreign_keys=[friend_id]
    )
    
    def __repr__(self) -> str:
        return f"<Friendship(user={self.user_id}, friend={self.friend_id})>"
