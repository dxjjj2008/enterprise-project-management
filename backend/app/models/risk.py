from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class RiskLevel(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RiskProbability(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RiskImpact(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


class RiskStatus(str, enum.Enum):
    identified = "identified"
    monitoring = "monitoring"
    mitigated = "mitigated"
    accepted = "accepted"
    closed = "closed"


class Risk(Base):
    __tablename__ = "risks"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    level = Column(String(20), default=RiskLevel.medium.value)
    probability = Column(String(20), default=RiskProbability.medium.value)
    impact = Column(String(20), default=RiskImpact.medium.value)
    status = Column(String(50), default=RiskStatus.identified.value)
    owner = Column(String(100))
    category = Column(String(50))
    mitigation = Column(Text)
    contingency = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    project = relationship("Project", back_populates="risks")
