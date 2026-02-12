from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# 项目基础模型
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = "draft"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

# 项目创建模型
class ProjectCreate(ProjectBase):
    pass

# 项目更新模型
class ProjectUpdate(ProjectBase):
    name: Optional[str] = None
    status: Optional[str] = None

# 项目响应模型
class ProjectResponse(ProjectBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 任务基础模型
class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "todo"
    priority: str = "medium"
    assigned_to: Optional[str] = None
    due_date: Optional[datetime] = None

# 任务创建模型（不含project_id，从URL路径获取）
class TaskCreate(TaskBase):
    pass

# 任务更新模型
class TaskUpdate(TaskBase):
    title: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None

# 任务响应模型
class TaskResponse(TaskBase):
    id: int
    project_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 项目详情响应（包含任务）
class ProjectDetailResponse(ProjectResponse):
    tasks: List[TaskResponse] = []

    class Config:
        from_attributes = True
