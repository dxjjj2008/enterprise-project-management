# 任务Schema模块
"""
任务相关的Pydantic Schema定义
用于请求和响应的数据验证
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, validator
from uuid import uuid4


# ============================================================================
# 任务相关Schema
# ============================================================================

class TaskBase(BaseModel):
    """任务基础Schema"""
    name: str = Field(..., min_length=1, max_length=255, description="任务名称")
    description: Optional[str] = Field(None, description="任务描述")
    start_date: Optional[str] = Field(None, description="开始日期 (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="结束日期 (YYYY-MM-DD)")
    status: Optional[str] = Field("todo", description="任务状态")
    progress: Optional[int] = Field(0, ge=0, le=100, description="进度百分比")
    priority: Optional[str] = Field("medium", description="优先级")
    project_id: Optional[int] = Field(None, description="项目ID")
    parent_id: Optional[int] = Field(None, description="父任务ID")
    assignee_id: Optional[int] = Field(None, description="负责人ID")
    task_type: Optional[str] = Field("task", description="任务类型")
    is_milestone: Optional[bool] = Field(False, description="是否为里程碑")
    is_group: Optional[bool] = Field(False, description="是否为任务组")
    dependencies: Optional[List[int]] = Field(default_factory=list, description="依赖的任务ID列表")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="元数据")

    @validator('start_date', 'end_date')
    def validate_date_format(cls, v):
        if v is not None:
            try:
                datetime.fromisoformat(v)
            except ValueError:
                raise ValueError("日期格式必须为 YYYY-MM-DD")
        return v

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ["todo", "in_progress", "done", "blocked"]
        if v not in valid_statuses:
            raise ValueError(f"status必须是以下值之一: {', '.join(valid_statuses)}")
        return v

    @validator('priority')
    def validate_priority(cls, v):
        valid_priorities = ["low", "medium", "high", "urgent"]
        if v not in valid_priorities:
            raise ValueError(f"priority必须是以下值之一: {', '.join(valid_priorities)}")
        return v

    @validator('progress')
    def validate_progress(cls, v):
        if v < 0 or v > 100:
            raise ValueError("progress必须在0到100之间")
        return v


class TaskCreate(TaskBase):
    """创建任务Schema"""
    pass


class TaskUpdate(BaseModel):
    """更新任务Schema"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    priority: Optional[str] = None
    parent_id: Optional[int] = None
    assignee_id: Optional[int] = None
    task_type: Optional[str] = None
    is_milestone: Optional[bool] = None
    is_group: Optional[bool] = None
    dependencies: Optional[List[int]] = None
    metadata: Optional[Dict[str, Any]] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["todo", "in_progress", "done", "blocked"]
            if v not in valid_statuses:
                raise ValueError(f"status必须是以下值之一: {', '.join(valid_statuses)}")
        return v

    @validator('progress')
    def validate_progress(cls, v):
        if v is not None and (v < 0 or v > 100):
            raise ValueError("progress必须在0到100之间")
        return v


class TaskResponse(TaskBase):
    """任务响应Schema"""
    id: int
    is_completed: bool
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    children: Optional[List["TaskResponse"]] = Field(default_factory=list, description="子任务列表")
    assignee: Optional[Dict[str, Any]] = Field(None, description="负责人信息")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "需求分析",
                "description": "分析用户需求",
                "startDate": "2026-02-01",
                "endDate": "2026-02-05",
                "duration": 5,
                "status": "done",
                "progress": 100,
                "priority": "high",
                "project_id": 1,
                "parent_id": None,
                "assignee_id": 1,
                "task_type": "task",
                "is_completed": True,
                "is_milestone": False,
                "is_group": False,
                "dependencies": [],
                "dependents": [],
                "metadata": {},
                "created_at": "2026-02-01T00:00:00",
                "updated_at": "2026-02-05T00:00:00"
            }
        }


class TaskDetailResponse(TaskBase):
    """任务详情响应Schema（包含依赖信息）"""
    id: int
    is_completed: bool
    children: Optional[List["TaskResponse"]] = Field(default_factory=list, description="子任务列表")
    assignee: Optional[Dict[str, Any]] = Field(None, description="负责人信息")
    dependencies: Optional[List["TaskResponse"]] = Field(default_factory=list, description="依赖的任务")
    dependents: Optional[List["TaskResponse"]] = Field(default_factory=list, description="依赖此任务的任务")

    class Config:
        from_attributes = True


# ============================================================================
# 任务依赖关系Schema
# ============================================================================

class TaskDependencyBase(BaseModel):
    """任务依赖关系基础Schema"""
    type: Optional[str] = Field("fs", description="依赖类型：fs, ss, ff, sf")
    parent_id: int = Field(..., description="父任务ID（被依赖的任务）")
    dependent_id: int = Field(..., description="子任务ID（依赖的任务）")
    condition: Optional[str] = Field(None, description="依赖条件描述")

    @validator('type')
    def validate_dependency_type(cls, v):
        valid_types = ["fs", "ss", "ff", "sf"]
        if v and v not in valid_types:
            raise ValueError(f"type必须是以下值之一: {', '.join(valid_types)}")
        return v or "fs"


class TaskDependencyCreate(TaskDependencyBase):
    """创建任务依赖Schema"""
    pass


class TaskDependencyUpdate(BaseModel):
    """更新任务依赖Schema"""
    type: Optional[str] = None
    condition: Optional[str] = None


class TaskDependencyResponse(TaskDependencyBase):
    """任务依赖响应Schema"""
    id: int
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# ============================================================================
# 查询Schema
# ============================================================================

class TaskQuery(BaseModel):
    """任务查询参数"""
    project_id: Optional[int] = Field(None, description="项目ID")
    status: Optional[str] = Field(None, description="任务状态")
    priority: Optional[str] = Field(None, description="优先级")
    task_type: Optional[str] = Field(None, description="任务类型")
    is_milestone: Optional[bool] = Field(None, description="是否为里程碑")
    is_group: Optional[bool] = Field(None, description="是否为任务组")
    parent_id: Optional[int] = Field(None, description="父任务ID")
    assignee_id: Optional[int] = Field(None, description="负责人ID")
    start_date: Optional[str] = Field(None, description="开始日期（起始）")
    end_date: Optional[str] = Field(None, description="结束日期（结束）")

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            valid_statuses = ["todo", "in_progress", "done", "blocked"]
            if v not in valid_statuses:
                raise ValueError(f"status必须是以下值之一: {', '.join(valid_statuses)}")
        return v


class TaskListResponse(BaseModel):
    """任务列表响应"""
    total: int
    items: List[TaskResponse]
    page: int
    page_size: int


class TaskDependenciesResponse(BaseModel):
    """任务依赖响应"""
    task_id: int
    dependencies: List[TaskResponse]
    dependents: List[TaskResponse]


# 递归引用
TaskResponse.model_rebuild()
TaskDetailResponse.model_rebuild()


# 导出
__all__ = [
    "TaskBase",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskDetailResponse",
    "TaskDependencyBase",
    "TaskDependencyCreate",
    "TaskDependencyUpdate",
    "TaskDependencyResponse",
    "TaskQuery",
    "TaskListResponse",
    "TaskDependenciesResponse",
]
