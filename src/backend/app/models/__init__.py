# 企业项目管理系统 - 数据库模型
"""
SQLAlchemy ORM数据模型定义
包含用户、项目、任务等核心实体
"""

from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum as SQLEnum, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
import enum

from app.models.database import Base


class UserRole(str, enum.Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    MANAGER = "manager"
    MEMBER = "member"
    VIEWER = "viewer"


class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    ARCHIVED = "archived"


class TaskPriority(str, enum.Enum):
    """任务优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class ProjectStatus(str, enum.Enum):
    """项目状态枚举"""
    PLANNING = "planning"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class PlanStatus(str, enum.Enum):
    """计划状态枚举"""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"
    ARCHIVED = "archived"


class ApprovalType(str, enum.Enum):
    """审批类型枚举"""
    LEAVE = "leave"
    EXPENSE = "expense"
    TRIP = "trip"
    PURCHASE = "purchase"
    PROJECT_INIT = "project_init"
    PROJECT_CHANGE = "project_change"


class ApprovalStatus(str, enum.Enum):
    """审批状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class RiskLevel(str, enum.Enum):
    """风险等级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RiskStatus(str, enum.Enum):
    """风险状态枚举"""
    IDENTIFIED = "identified"
    ASSESSED = "assessed"
    MITIGATING = "mitigating"
    MONITORING = "monitoring"
    CLOSED = "closed"


class IssueStatus(str, enum.Enum):
    """问题状态枚举"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IssuePriority(str, enum.Enum):
    """问题优先级枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class User(Base):
    """用户模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    avatar = Column(String(500), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # 关系
    owned_projects = relationship("Project", back_populates="owner", foreign_keys="Project.owner_id")
    project_memberships = relationship("ProjectMember", back_populates="user")
    created_tasks = relationship("Task", back_populates="creator", foreign_keys="Task.created_by_id")
    assigned_tasks = relationship("Task", back_populates="assignee", foreign_keys="Task.assignee_id")
    comments = relationship("Comment", back_populates="author")
    plans = relationship("Plan", back_populates="owner")
    wbs_tasks = relationship("WBSTask", back_populates="assignee")
    
    def __repr__(self):
        return f"<User {self.username}>"


class Project(Base):
    """项目模型"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    key = Column(String(10), unique=True, index=True, nullable=False)  # 项目标识符，如 "EPM"
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.PLANNING)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # 关系
    owner = relationship("User", back_populates="owned_projects", foreign_keys=[owner_id])
    members = relationship("ProjectMember", back_populates="project", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    milestones = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    plans = relationship("Plan", back_populates="project", cascade="all, delete-orphan")
    approvals = relationship("Approval", back_populates="project")
    
    def __repr__(self):
        return f"<Project {self.key}>"


class ProjectMember(Base):
    """项目成员关联模型"""
    __tablename__ = "project_members"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.MEMBER)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    project = relationship("Project", back_populates="members")
    user = relationship("User", back_populates="project_memberships")
    
    # 复合唯一约束
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_member"),
    )
    
    def __repr__(self):
        return f"<ProjectMember project={self.project_id} user={self.user_id}>"


class Milestone(Base):
    """里程碑模型"""
    __tablename__ = "milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="pending")  # pending, completed
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    project = relationship("Project", back_populates="milestones")
    
    def __repr__(self):
        return f"<Milestone {self.name}>"


class Plan(Base):
    """计划模型"""
    __tablename__ = "plans"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(PlanStatus), default=PlanStatus.DRAFT)
    progress = Column(Integer, default=0)  # 0-100
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # 关系
    project = relationship("Project", back_populates="plans")
    owner = relationship("User", back_populates="plans")
    wbs_tasks = relationship("WBSTask", back_populates="plan", cascade="all, delete-orphan")
    milestones = relationship("PlanMilestone", back_populates="plan", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Plan {self.name}>"


class WBSTask(Base):
    """WBS任务模型"""
    __tablename__ = "wbs_tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("wbs_tasks.id"), nullable=True)
    name = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(Integer, default=1)
    sort_order = Column(Integer, default=0)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    duration = Column(Integer, default=1)  # 工期（天）
    progress = Column(Integer, default=0)  # 0-100
    status = Column(String(20), default="pending")  # pending, in_progress, completed, cancelled
    is_milestone = Column(Boolean, default=False)
    dependency = Column(JSON, nullable=True)  # 前置任务ID列表
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # 关系
    plan = relationship("Plan", back_populates="wbs_tasks")
    parent = relationship("WBSTask", remote_side=[id], backref="children")
    assignee = relationship("User", back_populates="wbs_tasks")
    
    def __repr__(self):
        return f"<WBSTask {self.name}>"


class PlanMilestone(Base):
    """计划里程碑模型"""
    __tablename__ = "plan_milestones"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("wbs_tasks.id"), nullable=True)
    name = Column(String(200), nullable=False)
    plan_date = Column(DateTime, nullable=True)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    plan = relationship("Plan", back_populates="milestones")
    
    def __repr__(self):
        return f"<PlanMilestone {self.name}>"


class Approval(Base):
    """审批模型"""
    __tablename__ = "approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    type = Column(SQLEnum(ApprovalType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    applicant_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING)
    current_node = Column(String(100), nullable=True)
    form_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    applicant = relationship("User", foreign_keys=[applicant_id])
    project = relationship("Project", back_populates="approvals")
    flow_nodes = relationship("ApprovalFlowNode", back_populates="approval", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Approval {self.title}>"


class ApprovalFlowNode(Base):
    """审批流程节点模型"""
    __tablename__ = "approval_flow_nodes"
    
    id = Column(Integer, primary_key=True, index=True)
    approval_id = Column(Integer, ForeignKey("approvals.id"), nullable=False)
    name = Column(String(100), nullable=False)
    approver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(20), default="pending")  # pending, approved, rejected
    comment = Column(Text, nullable=True)
    approved_at = Column(DateTime, nullable=True)
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    approval = relationship("Approval", back_populates="flow_nodes")
    
    def __repr__(self):
        return f"<ApprovalFlowNode {self.name}>"


class Task(Base):
    """任务模型"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # 父任务ID，支持子任务
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.TODO)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.MEDIUM)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    start_date = Column(DateTime, nullable=True)
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_hours = Column(Integer, nullable=True)
    actual_hours = Column(Integer, nullable=True)
    progress = Column(Integer, default=0)  # 0-100
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # 关系
    project = relationship("Project", back_populates="tasks")
    parent = relationship("Task", remote_side=[id], backref="subtasks")
    assignee = relationship("User", back_populates="assigned_tasks", foreign_keys=[assignee_id])
    creator = relationship("User", back_populates="created_tasks", foreign_keys=[created_by_id])
    comments = relationship("Comment", back_populates="task", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="task", cascade="all, delete-orphan")
    labels = relationship("TaskLabel", back_populates="task", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Task {self.title}>"


class Comment(Base):
    """评论模型"""
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # 关系
    task = relationship("Task", back_populates="comments")
    author = relationship("User", back_populates="comments")
    
    def __repr__(self):
        return f"<Comment {self.id}>"


class Attachment(Base):
    """附件模型"""
    __tablename__ = "attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=True)
    file_type = Column(String(100), nullable=True)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # 关系
    task = relationship("Task", back_populates="attachments")
    
    def __repr__(self):
        return f"<Attachment {self.filename}>"


class Label(Base):
    """标签模型"""
    __tablename__ = "labels"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    color = Column(String(20), default="#0079bf")  # 标签颜色
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)  # 可选的全局标签
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    tasks = relationship("TaskLabel", back_populates="label")
    
    def __repr__(self):
        return f"<Label {self.name}>"


class TaskLabel(Base):
    """任务-标签关联模型"""
    __tablename__ = "task_labels"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    label_id = Column(Integer, ForeignKey("labels.id"), nullable=False)
    
    # 关系
    task = relationship("Task", back_populates="labels")
    label = relationship("Label", back_populates="tasks")
    
    # 复合唯一约束
    __table_args__ = (
        UniqueConstraint("task_id", "label_id", name="uq_task_label"),
    )
    
    def __repr__(self):
        return f"<TaskLabel task={self.task_id} label={self.label_id}>"


class Risk(Base):
    """风险模型"""
    __tablename__ = "risks"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    level = Column(SQLEnum(RiskLevel), default=RiskLevel.MEDIUM)
    status = Column(SQLEnum(RiskStatus), default=RiskStatus.IDENTIFIED)
    probability = Column(Integer, default=0)  # 发生概率 0-100
    impact = Column(Integer, default=0)  # 影响程度 0-100
    score = Column(Integer, default=0)  # 风险评分
    category = Column(String(100), nullable=True)  # 风险类别
    source = Column(String(200), nullable=True)  # 风险来源
    mitigation = Column(Text, nullable=True)  # 应对措施
    contingency_plan = Column(Text, nullable=True)  # 应急预案
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 风险负责人
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # 关联任务
    due_date = Column(DateTime, nullable=True)
    identified_date = Column(DateTime, default=datetime.utcnow)
    closed_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    project = relationship("Project", back_populates="risks")
    owner = relationship("User", foreign_keys=[owner_id])
    task = relationship("Task")
    
    def __repr__(self):
        return f"<Risk {self.title}>"


class RiskResponse(Base):
    """风险应对记录模型"""
    __tablename__ = "risk_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(Integer, ForeignKey("risks.id"), nullable=False)
    action = Column(Text, nullable=False)
    result = Column(Text, nullable=True)  # 应对结果
    performed_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关系
    risk = relationship("Risk", back_populates="responses")
    performed_by = relationship("User", foreign_keys=[performed_by_id])
    
    def __repr__(self):
        return f"<RiskResponse {self.id}>"


class Issue(Base):
    """问题模型"""
    __tablename__ = "issues"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)  # 关联任务
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(IssueStatus), default=IssueStatus.OPEN)
    priority = Column(SQLEnum(IssuePriority), default=IssuePriority.MEDIUM)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # 报告人
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # 责任人
    due_date = Column(DateTime, nullable=True)
    resolved_date = Column(DateTime, nullable=True)
    solution = Column(Text, nullable=True)  # 解决方案
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关系
    project = relationship("Project", back_populates="issues")
    task = relationship("Task")
    reporter = relationship("User", foreign_keys=[reporter_id])
    assignee = relationship("User", foreign_keys=[assignee_id])
    comments = relationship("IssueComment", back_populates="issue", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Issue {self.title}>"


class IssueComment(Base):
    """问题评论模型"""
    __tablename__ = "issue_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    issue_id = Column(Integer, ForeignKey("issues.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)
    
    # 关系
    issue = relationship("Issue", back_populates="comments")
    author = relationship("User", foreign_keys=[author_id])
    
    def __repr__(self):
        return f"<IssueComment {self.id}>"


# 更新项目关系
# 在Project类中添加risks和issues关系
Project.risks = relationship("Risk", back_populates="project", cascade="all, delete-orphan")
Project.issues = relationship("Issue", back_populates="project", cascade="all, delete-orphan")
Risk.responses = relationship("RiskResponse", back_populates="risk", cascade="all, delete-orphan")


# 导出所有模型
__all__ = [
    "User",
    "UserRole",
    "Project",
    "ProjectMember",
    "Milestone",
    "Plan",
    "WBSTask",
    "PlanMilestone",
    "Approval",
    "ApprovalFlowNode",
    "Task",
    "TaskStatus",
    "TaskPriority",
    "Comment",
    "Attachment",
    "Label",
    "TaskLabel",
    "ProjectStatus",
    "PlanStatus",
    "ApprovalType",
    "ApprovalStatus",
    "Risk",
    "RiskResponse",
    "RiskLevel",
    "RiskStatus",
    "Issue",
    "IssueComment",
    "IssueStatus",
    "IssuePriority"
]
