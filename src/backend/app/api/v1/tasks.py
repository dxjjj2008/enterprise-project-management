# 企业项目管理系统 - 任务API
"""
任务管理和协作API
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.models import (
    User, Project, Task, Comment, Label, TaskLabel,
    UserRole, TaskStatus, TaskPriority
)
from app.models.database import get_db
from app.core.security import get_current_user

router = APIRouter()


@router.get("/{project_id}/tasks")
async def get_tasks(
    project_id: int,
    skip: int = 0,
    limit: int = 100,
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    assignee_id: Optional[int] = None,
    labels: Optional[List[int]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取任务列表"""
    # 验证用户权限
    from app.models import ProjectMember
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    query = db.query(Task).filter(
        Task.project_id == project_id,
        Task.is_deleted == False
    )
    
    if status:
        query = query.filter(Task.status == status)
    
    if priority:
        query = query.filter(Task.priority == priority)
    
    if assignee_id is not None:
        query = query.filter(Task.assignee_id == assignee_id)
    
    if labels:
        query = query.join(TaskLabel).filter(
            TaskLabel.label_id.in_(labels)
        )
    
    tasks = query.order_by(Task.created_at.desc()).offset(skip).limit(limit).all()
    
    # 获取总数量
    total = query.count()
    
    return {
        "items": tasks,
        "total": total,
        "skip": skip,
        "limit": limit
    }


@router.post("/{project_id}/tasks")
async def create_task(
    project_id: int,
    title: str,
    description: str = None,
    parent_id: int = None,
    priority: TaskPriority = TaskPriority.MEDIUM,
    assignee_id: int = None,
    start_date: datetime = None,
    due_date: datetime = None,
    estimated_hours: int = None,
    labels: Optional[List[int]] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新任务"""
    # 验证用户权限
    from app.models import ProjectMember
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # 验证父任务存在
    if parent_id:
        parent_task = db.query(Task).filter(Task.id == parent_id).first()
        if not parent_task:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent task not found"
            )
    
    # 验证指派人存在且是项目成员
    if assignee_id:
        assignee = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == assignee_id
        ).first()
        
        if not assignee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee is not a project member"
            )
    
    # 创建任务
    task = Task(
        project_id=project_id,
        parent_id=parent_id,
        title=title,
        description=description,
        priority=priority,
        assignee_id=assignee_id,
        created_by_id=current_user.id,
        start_date=start_date,
        due_date=due_date,
        estimated_hours=estimated_hours,
        status=TaskStatus.TODO
    )
    
    db.add(task)
    db.flush()
    
    # 添加标签
    if labels:
        for label_id in labels:
            label = db.query(Label).filter(Label.id == label_id).first()
            if label:
                task_label = TaskLabel(task_id=task.id, label_id=label_id)
                db.add(task_label)
    
    db.commit()
    db.refresh(task)
    
    return {
        "message": "Task created successfully",
        "task": task
    }


@router.get("/{project_id}/tasks/{task_id}")
async def get_task(
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取任务详情"""
    # 验证用户权限
    from app.models import ProjectMember
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task or task.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # 获取子任务
    subtasks = db.query(Task).filter(
        Task.parent_id == task_id,
        Task.is_deleted == False
    ).all()
    
    # 获取评论
    comments = db.query(Comment).filter(
        Comment.task_id == task_id,
        Comment.is_deleted == False
    ).order_by(Comment.created_at.asc()).all()
    
    # 获取标签
    task_labels = db.query(TaskLabel).filter(
        TaskLabel.task_id == task_id
    ).all()
    label_ids = [tl.label_id for tl in task_labels]
    labels = db.query(Label).filter(Label.id.in_(label_ids)).all() if label_ids else []
    
    return {
        "task": task,
        "subtasks": subtasks,
        "comments": comments,
        "labels": labels
    }


@router.put("/{project_id}/tasks/{task_id}")
async def update_task(
    project_id: int,
    task_id: int,
    title: str = None,
    description: str = None,
    status: TaskStatus = None,
    priority: TaskPriority = None,
    assignee_id: int = None,
    start_date: datetime = None,
    due_date: datetime = None,
    estimated_hours: int = None,
    progress: int = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新任务"""
    # 验证用户权限
    from app.models import ProjectMember
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task or task.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # 更新字段
    if title:
        task.title = title
    if description is not None:
        task.description = description
    if status:
        task.status = status
        if status == TaskStatus.DONE:
            task.completed_at = datetime.utcnow()
    if priority:
        task.priority = priority
    if assignee_id is not None:
        task.assignee_id = assignee_id
    if start_date is not None:
        task.start_date = start_date
    if due_date is not None:
        task.due_date = due_date
    if estimated_hours is not None:
        task.estimated_hours = estimated_hours
    if progress is not None:
        task.progress = min(100, max(0, progress))
    
    db.commit()
    db.refresh(task)
    
    return {
        "message": "Task updated successfully",
        "task": task
    }


@router.delete("/{project_id}/tasks/{task_id}")
async def delete_task(
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除任务（软删除）"""
    # 验证用户权限
    from app.models import ProjectMember
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
        ProjectMember.role.in_([UserRole.ADMIN, UserRole.MANAGER])
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task or task.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # 软删除
    task.is_deleted = True
    db.commit()
    
    return {"message": "Task deleted successfully"}


# 任务评论
@router.post("/{project_id}/tasks/{task_id}/comments")
async def add_comment(
    project_id: int,
    task_id: int,
    content: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加任务评论"""
    # 验证用户权限
    from app.models import ProjectMember
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # 验证任务存在
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task or task.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # 创建评论
    comment = Comment(
        task_id=task_id,
        author_id=current_user.id,
        content=content
    )
    
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return {
        "message": "Comment added successfully",
        "comment": comment
    }


@router.get("/{project_id}/tasks/{task_id}/comments")
async def get_comments(
    project_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取任务评论"""
    # 验证用户权限
    from app.models import ProjectMember
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    comments = db.query(Comment).filter(
        Comment.task_id == task_id,
        Comment.is_deleted == False
    ).order_by(Comment.created_at.asc()).all()
    
    return {"items": comments, "total": len(comments)}


# 任务标签
@router.get("/{project_id}/labels")
async def get_labels(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目标签列表"""
    # 验证用户权限
    from app.models import ProjectMember
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    labels = db.query(Label).filter(
        (Label.project_id == project_id) | (Label.project_id == None)
    ).all()
    
    return {"items": labels, "total": len(labels)}


@router.post("/{project_id}/labels")
async def create_label(
    project_id: int,
    name: str,
    color: str = "#0079bf",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建项目标签"""
    # 验证用户权限
    from app.models import ProjectMember
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
        ProjectMember.role.in_([UserRole.ADMIN, UserRole.MANAGER])
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    label = Label(
        name=name,
        color=color,
        project_id=project_id
    )
    
    db.add(label)
    db.commit()
    db.refresh(label)
    
    return {
        "message": "Label created successfully",
        "label": label
    }


# 导出
__all__ = ["router"]
