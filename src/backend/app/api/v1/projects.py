# 企业项目管理系统 - 项目API
"""
项目管理和成员管理API
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import (
    User, Project, ProjectMember, Task, Milestone,
    UserRole, ProjectStatus
)
from app.models.database import get_db
from app.core.security import get_current_user, get_admin_user

router = APIRouter()


def generate_project_key(db: Session) -> str:
    """自动生成项目Key: PJ + 6位流水号"""
    # 获取最大流水号
    max_key = db.query(func.max(Project.key)).filter(
        Project.key.like('PJ%')
    ).scalar()
    
    if max_key:
        # 提取流水号部分并+1
        try:
            num = int(max_key[2:]) + 1  # 去掉"PJ"前缀
        except ValueError:
            num = 1
    else:
        num = 1
    
    # 生成新key，确保6位流水号
    new_key = f"PJ{num:06d}"
    
    # 如果key已存在（并发情况），递归重试
    existing = db.query(Project).filter(Project.key == new_key).first()
    if existing:
        return generate_project_key(db)
    
    return new_key


@router.get("/next-key")
async def get_next_project_key(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取下一个可用的项目Key（用于前端预览）"""
    next_key = generate_project_key(db)
    return {
        "key": next_key,
        "format": "PJ######",
        "description": "项目标识由系统自动生成，格式为PJ+6位流水号"
    }


@router.get("")
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    status: Optional[ProjectStatus] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目列表"""
    # 获取用户参与的项目
    project_ids = db.query(ProjectMember.project_id).filter(
        ProjectMember.user_id == current_user.id
    ).all()
    
    project_ids = [p[0] for p in project_ids]
    
    query = db.query(Project).filter(
        Project.id.in_(project_ids),
        Project.is_deleted == False
    )
    
    if status:
        query = query.filter(Project.status == status)
    
    projects = query.offset(skip).limit(limit).all()
    
    return {
        "items": projects,
        "total": query.count(),
        "skip": skip,
        "limit": limit
    }


@router.get("/list")
async def get_projects_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目列表（下拉框用）"""
    # 获取用户参与的项目
    project_ids = db.query(ProjectMember.project_id).filter(
        ProjectMember.user_id == current_user.id
    ).all()
    
    project_ids = [p[0] for p in project_ids]
    
    projects = db.query(Project).filter(
        Project.id.in_(project_ids),
        Project.is_deleted == False
    ).all()
    
    return {
        "items": [{"id": p.id, "name": p.name, "key": p.key} for p in projects],
        "total": len(projects)
    }


@router.post("")
async def create_project(
    name: str = Form(...),
    description: str = Form(None),
    start_date: datetime = Form(None),
    end_date: datetime = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建新项目（自动生成项目Key: PJ + 6位流水号）"""

    # 自动生成项目Key
    new_key = generate_project_key(db)

    # 创建项目
    project = Project(
        name=name,
        key=new_key,
        description=description,
        owner_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        status=ProjectStatus.PLANNING
    )
    
    db.add(project)
    db.flush()
    
    # 添加创建者为项目管理员
    member = ProjectMember(
        project_id=project.id,
        user_id=current_user.id,
        role=UserRole.ADMIN
    )
    db.add(member)
    
    db.commit()
    db.refresh(project)
    
    return {
        "message": "Project created successfully",
        "project": project
    }


@router.get("/{project_id}")
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目详情"""
    # 验证用户权限
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project or project.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # 获取项目统计
    task_count = db.query(Task).filter(
        Task.project_id == project_id,
        Task.is_deleted == False
    ).count()
    
    completed_task_count = db.query(Task).filter(
        Task.project_id == project_id,
        Task.is_deleted == False,
        Task.status == "done"
    ).count()
    
    milestone_count = db.query(Milestone).filter(
        Milestone.project_id == project_id
    ).count()
    
    return {
        "project": project,
        "stats": {
            "total_tasks": task_count,
            "completed_tasks": completed_task_count,
            "milestones": milestone_count,
            "progress": round(completed_task_count / task_count * 100, 2) if task_count > 0 else 0
        },
        "user_role": member.role.value
    }


@router.put("/{project_id}")
async def update_project(
    project_id: int,
    name: str = Form(None),
    description: str = Form(None),
    status: ProjectStatus = Form(None),
    start_date: datetime = Form(None),
    end_date: datetime = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新项目"""
    # 验证用户权限
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
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project or project.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # 更新字段
    if name:
        project.name = name
    if description is not None:
        project.description = description
    if status:
        project.status = status
    if start_date:
        project.start_date = start_date
    if end_date:
        project.end_date = end_date
    
    db.commit()
    db.refresh(project)
    
    return {
        "message": "Project updated successfully",
        "project": project
    }


@router.delete("/{project_id}")
async def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除项目（软删除）"""
    # 验证用户权限
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
        ProjectMember.role == UserRole.ADMIN
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    project = db.query(Project).filter(Project.id == project_id).first()
    
    if not project or project.is_deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # 软删除
    project.is_deleted = True
    db.commit()
    
    return {"message": "Project deleted successfully"}


# 项目成员管理
@router.get("/{project_id}/members")
async def get_project_members(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目成员列表"""
    # 验证用户权限
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    members = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id
    ).all()
    
    return {
        "items": members,
        "total": len(members)
    }


@router.post("/{project_id}/members")
async def add_project_member(
    project_id: int,
    user_id: int = Form(...),
    role: UserRole = Form(UserRole.MEMBER),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加项目成员"""
    # 验证用户权限
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
    
    # 验证用户存在
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 检查是否已是成员
    existing = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already a member"
        )
    
    # 添加成员
    new_member = ProjectMember(
        project_id=project_id,
        user_id=user_id,
        role=role
    )
    db.add(new_member)
    db.commit()
    db.refresh(new_member)
    
    return {
        "message": "Member added successfully",
        "member": new_member
    }


@router.delete("/{project_id}/members/{user_id}")
async def remove_project_member(
    project_id: int,
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """移除项目成员"""
    # 验证用户权限
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id,
        ProjectMember.role == UserRole.ADMIN
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    # 不能移除自己（如果是唯一管理员）
    if user_id == current_user.id:
        admin_count = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id,
            ProjectMember.role == UserRole.ADMIN
        ).count()
        
        if admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot remove the only admin"
            )
    
    member_to_remove = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == user_id
    ).first()
    
    if not member_to_remove:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    
    db.delete(member_to_remove)
    db.commit()
    
    return {"message": "Member removed successfully"}


# 里程碑管理
@router.get("/{project_id}/milestones")
async def get_project_milestones(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目里程碑列表"""
    # 验证用户权限
    member = db.query(ProjectMember).filter(
        ProjectMember.project_id == project_id,
        ProjectMember.user_id == current_user.id
    ).first()
    
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    milestones = db.query(Milestone).filter(
        Milestone.project_id == project_id
    ).order_by(Milestone.created_at.desc()).all()
    
    return {"items": milestones, "total": len(milestones)}


@router.post("/{project_id}/milestones")
async def create_milestone(
    project_id: int,
    name: str = Form(...),
    description: str = Form(None),
    due_date: datetime = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建项目里程碑"""
    # 验证用户权限
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
    
    milestone = Milestone(
        project_id=project_id,
        name=name,
        description=description,
        due_date=due_date
    )
    
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    
    return {
        "message": "Milestone created successfully",
        "milestone": milestone
    }


# 导出
__all__ = ["router"]
