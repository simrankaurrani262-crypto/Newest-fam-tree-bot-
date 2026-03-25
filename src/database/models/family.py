"""
Family Models
"""
from datetime import datetime
from typing import Optional, List

from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from src.database.connection import Base


class RelationType(str, enum.Enum):
    """Family relation types"""
    SPOUSE = "spouse"
    PARENT = "parent"
    CHILD = "child"
    SIBLING = "sibling"


class Family(Base):
    """Family group model"""
    
    __tablename__ = "families"
    
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    founder_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id"),
        nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    member_count: Mapped[int] = mapped_column(default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Family(id={self.id}, name={self.name})>"


class FamilyRelation(Base):
    """Family relationship model (graph edges)"""
    
    __tablename__ = "family_relations"
    
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    related_user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    relation_type: Mapped[RelationType] = mapped_column(
        SQLEnum(RelationType),
        nullable=False
    )
    family_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("families.id", ondelete="CASCADE"),
        nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[user_id],
        back_populates="family_relations"
    )
    related_user: Mapped["User"] = relationship(
        "User",
        foreign_keys=[related_user_id]
    )
    
    def __repr__(self) -> str:
        return (
            f"<FamilyRelation(user={self.user_id}, "
            f"related={self.related_user_id}, type={self.relation_type})>"
        )
