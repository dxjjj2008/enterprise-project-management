# 任务依赖关系模型
"""
任务相关数据模型
包括TaskDependency等（Task模型在__init__.py中定义）
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Numeric
from sqlalchemy.orm import relationship
from typing import Optional, List

from .database import Base


class TaskDependency(Base):
    """任务依赖关系模型"""
    __tablename__ = "task_dependencies"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # 依赖关系类型
    type = Column(String(50), default="fs", comment="依赖类型：fs (finish-to-start), ss (start-to-start), ff (finish-to-finish), sf (start-to-finish)")

    # 任务关系
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, comment="父任务ID（被依赖的任务）")
    dependent_id = Column(Integer, ForeignKey("tasks.id"), nullable=False, comment="子任务ID（依赖的任务）")

    # 依赖条件（可选）
    condition = Column(Text, nullable=True, comment="依赖条件描述")

    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow, comment="创建时间")

    def __repr__(self):
        return f"<TaskDependency(parent_id={self.parent_id}, dependent_id={self.dependent_id})>"

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "type": self.type,
            "parent_id": self.parent_id,
            "dependent_id": self.dependent_id,
            "condition": self.condition,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# 导出
__all__ = ["TaskDependency"]
