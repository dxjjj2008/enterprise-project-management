from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.core.database import Base


class ResourceRole(str, enum.Enum):
    developer = "developer"
    designer = "designer"
    pm = "pm"
    tester = "tester"
    devops = "devops"
    analyst = "analyst"
    other = "other"


class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200))
    role = Column(String(50), default=ResourceRole.other.value)
    department = Column(String(100))
    skills = Column(Text)
    workload = Column(Integer, default=0)
    utilization = Column(Integer, default=0)
    avatar = Column(String(10))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Label(Base):
    __tablename__ = "labels"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(50), nullable=False)
    color = Column(String(7), default="#409EFF")
    created_at = Column(DateTime, default=datetime.utcnow)

    # 关系
    project = relationship("Project", back_populates="labels")
