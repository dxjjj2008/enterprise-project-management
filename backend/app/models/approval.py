from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ApprovalType(str, enum.Enum):
    project = "project"
    budget = "budget"
    resource = "resource"
    procurement = "procurement"
    leave = "leave"
    other = "other"


class ApprovalStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    cancelled = "cancelled"


class ApprovalPriority(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Approval(Base):
    __tablename__ = "approvals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    approval_type = Column(String(50), default=ApprovalType.other.value)
    status = Column(String(50), default=ApprovalStatus.pending.value)
    priority = Column(String(20), default=ApprovalPriority.medium.value)
    applicant = Column(String(100), nullable=False)
    approver = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    history = relationship("ApprovalHistory", back_populates="approval", cascade="all, delete")


class ApprovalHistory(Base):
    __tablename__ = "approval_history"

    id = Column(Integer, primary_key=True, index=True)
    approval_id = Column(Integer, ForeignKey("approvals.id"), nullable=False)
    action = Column(String(50), nullable=False)
    user = Column(String(100), nullable=False)
    comment = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    approval = relationship("Approval", back_populates="history")
