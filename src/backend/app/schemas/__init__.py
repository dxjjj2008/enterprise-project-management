# 企业项目管理系统 - Pydantic Schemas
"""
数据验证和序列化模型
用于API请求和响应验证
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from enum import Enum


# ============ 认证 schemas ============

class Token(BaseModel):
    """令牌响应"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """令牌数据"""
    username: Optional[str] = None
    user_id: Optional[int] = None


class UserCreate(BaseModel):
    """用户创建请求"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """用户登录请求"""
    username: str
    password: str


class UserResponse(BaseModel):
    """用户响应"""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    phone: Optional[str]
    avatar: Optional[str]
    role: str
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """用户更新请求"""
    full_name: Optional[str] = None
    phone: Optional[str] = None


class PasswordChange(BaseModel):
    """密码更改请求"""
    old_password: str
    new_password: str = Field(..., min_length=6)


# ============ 项目 schemas ============

class ProjectStatusEnum(str, Enum):
    """项目状态枚举"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectCreate(BaseModel):
    """项目创建请求"""
    name: str = Field(..., min_length=1, max_length=200)
    key: str = Field(..., min_length=2, max_length=10)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    """项目更新请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    status: Optional[ProjectStatusEnum] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class ProjectResponse(BaseModel):
    """项目响应"""
    id: int
    name: str
    key: str
    description: Optional[str]
    status: str
    owner_id: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProjectWithStats(ProjectResponse):
    """带统计的项目响应"""
    stats: dict
    user_role: str


# ============ 项目成员 schemas ============

class UserRoleEnum(str, Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


class ProjectMemberCreate(BaseModel):
    """项目成员创建请求"""
    user_id: int
    role: UserRoleEnum = UserRoleEnum.MEMBER


class ProjectMemberResponse(BaseModel):
    """项目成员响应"""
    id: int
    project_id: int
    user_id: int
    role: str
    joined_at: datetime

    class Config:
        from_attributes = True


class ProjectMemberWithUser(ProjectMemberResponse):
    """带用户信息的项目成员响应"""
    user: UserResponse


# ============ 里程碑 schemas ============

class MilestoneCreate(BaseModel):
    """里程碑创建请求"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    due_date: Optional[datetime] = None


class MilestoneResponse(BaseModel):
    """里程碑响应"""
    id: int
    project_id: int
    name: str
    description: Optional[str]
    due_date: Optional[datetime]
    status: str
    completed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 任务 schemas ============

class TaskStatusEnum(str, Enum):
    """任务状态枚举"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    ARCHIVED = "archived"


class TaskPriorityEnum(str, Enum):
    """任务优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskCreate(BaseModel):
    """任务创建请求"""
    title: str = Field(..., min_length=1, max_length=500)
    description: Optional[str] = None
    parent_id: Optional[int] = None
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM
    assignee_id: Optional[int] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = Field(None, ge=0)
    labels: Optional[List[int]] = None


class TaskUpdate(BaseModel):
    """任务更新请求"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    description: Optional[str] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    assignee_id: Optional[int] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    estimated_hours: Optional[int] = Field(None, ge=0)
    progress: Optional[int] = Field(None, ge=0, le=100)


class TaskResponse(BaseModel):
    """任务响应"""
    id: int
    project_id: int
    parent_id: Optional[int]
    title: str
    description: Optional[str]
    status: str
    priority: str
    assignee_id: Optional[int]
    created_by_id: int
    start_date: Optional[datetime]
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    estimated_hours: Optional[int]
    actual_hours: Optional[int]
    progress: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ============ 评论 schemas ============

class CommentCreate(BaseModel):
    """评论创建请求"""
    content: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    """评论响应"""
    id: int
    task_id: int
    author_id: int
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CommentWithAuthor(CommentResponse):
    """带作者信息的评论响应"""
    author: "UserResponse"


# ============ 标签 schemas ============

class LabelCreate(BaseModel):
    """标签创建请求"""
    name: str = Field(..., min_length=1, max_length=50)
    color: str = "#0079bf"


class LabelResponse(BaseModel):
    """标签响应"""
    id: int
    name: str
    color: str
    project_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 附件 schemas ============

class AttachmentResponse(BaseModel):
    """附件响应"""
    id: int
    task_id: int
    filename: str
    file_path: str
    file_size: Optional[int]
    file_type: Optional[str]
    uploaded_by_id: int
    created_at: datetime

    class Config:
        from_attributes = True


# ============ 通用 schemas ============

class MessageResponse(BaseModel):
    """消息响应"""
    message: str


class PaginatedResponse(BaseModel):
    """分页响应"""
    items: List
    total: int
    skip: int
    limit: int


class ErrorResponse(BaseModel):
    """错误响应"""
    code: int
    message: str
    data: Optional[dict] = None
    error: Optional[str] = None


# 导出所有schemas
__all__ = [
    # 认证
    "Token",
    "TokenData",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "UserUpdate",
    "PasswordChange",
    
    # 项目
    "ProjectStatusEnum",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectWithStats",
    
    # 成员
    "UserRoleEnum",
    "ProjectMemberCreate",
    "ProjectMemberResponse",
    "ProjectMemberWithUser",
    
    # 里程碑
    "MilestoneCreate",
    "MilestoneResponse",
    
    # 任务
    "TaskStatusEnum",
    "TaskPriorityEnum",
    "TaskCreate",
    "TaskUpdate",
    "TaskResponse",
    "TaskWithDetails",
    
    # 评论
    "CommentCreate",
    "CommentResponse",
    "CommentWithAuthor",
    
    # 标签
    "LabelCreate",
    "LabelResponse",
    
    # 附件
    "AttachmentResponse",
    
    # 通用
    "MessageResponse",
    "PaginatedResponse",
    "ErrorResponse"
]
