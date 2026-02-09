# 企业项目管理系统 - 资源管理API
"""
团队成员和工作负载管理API
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import User, Project, Task, ProjectMember, UserRole
from app.models.database import get_db
from app.core.security import get_current_user

router = APIRouter()


@router.get("/users")
async def get_users(
    role: Optional[str] = None,
    is_active: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    query = db.query(User).filter(User.is_active == is_active)
    
    if role:
        query = query.filter(User.role == role)
    
    users = query.all()
    
    return {
        "items": [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value if user.role else None,
                "avatar": user.avatar,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            for user in users
        ],
        "total": len(users)
    }


@router.get("/users/{user_id}")
async def get_user_detail(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户详细信息和工作负载"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # 获取用户参与的项目
    project_ids = db.query(ProjectMember.project_id).filter(
        ProjectMember.user_id == user_id
    ).all()
    project_ids = [p[0] for p in project_ids]
    
    projects = db.query(Project).filter(Project.id.in_(project_ids)).all()
    
    # 获取用户任务统计
    task_stats = db.query(
        Task.status,
        func.count(Task.id).label('count')
    ).filter(
        Task.assignee_id == user_id
    ).group_by(Task.status).all()
    
    stats = {}
    for status_val, count in task_stats:
        status_key = status_val.value if hasattr(status_val, 'value') else str(status_val)
        stats[status_key] = count
    
    # 待处理任务 (使用字符串)
    pending_tasks = db.query(Task).filter(
        Task.assignee_id == user_id,
        Task.status.in_(['todo', 'in_progress'])
    ).limit(10).all()
    
    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
            "role": user.role.value if user.role else None,
            "avatar": user.avatar,
            "created_at": user.created_at.isoformat() if user.created_at else None
        },
        "projects": [
            {
                "id": p.id,
                "name": p.name,
                "key": p.key,
                "status": p.status.value if p.status else None
            }
            for p in projects
        ],
        "task_stats": stats,
        "pending_tasks": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status.value if t.status else None,
                "priority": t.priority.value if t.priority else None,
                "due_date": t.due_date.isoformat() if t.due_date else None
            }
            for t in pending_tasks
        ]
    }


@router.get("/workload")
async def get_team_workload(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取团队工作负载视图"""
    users = db.query(User).filter(User.is_active == True).all()
    
    workload_data = []
    
    for user in users:
        # 项目数量
        project_count = db.query(ProjectMember).filter(
            ProjectMember.user_id == user.id
        ).count()
        
        # 任务统计
        task_stats = db.query(
            Task.status,
            func.count(Task.id).label('count')
        ).filter(
            Task.assignee_id == user.id
        ).group_by(Task.status).all()
        
        total_tasks = sum(count for _, count in task_stats)
        completed_tasks = sum(count for status, count in task_stats 
                           if (hasattr(status, 'value') and status.value == 'done') 
                           or status == 'done')
        
        in_progress = sum(count for status, count in task_stats 
                         if (hasattr(status, 'value') and status.value == 'in_progress') 
                         or status == 'in_progress')
        
        # 计算工作负载评分 (0-100)
        workload_score = min(100, (total_tasks * 10))
        
        workload_data.append({
            "user": {
                "id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "avatar": user.avatar
            },
            "project_count": project_count,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress,
            "workload_score": workload_score,
            "workload_level": "high" if workload_score > 70 else "medium" if workload_score > 30 else "low"
        })
    
    # 按工作负载排序
    workload_data.sort(key=lambda x: x["workload_score"], reverse=True)
    
    return {
        "items": workload_data,
        "total": len(workload_data)
    }


@router.get("/utilization")
async def get_resource_utilization(
    project_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取资源利用率视图"""
    if project_id:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        members = db.query(ProjectMember).filter(
            ProjectMember.project_id == project_id
        ).all()
        
        utilization = []
        for member in members:
            user = db.query(User).filter(User.id == member.user_id).first()
            if not user:
                continue
            
            task_count = db.query(Task).filter(
                Task.assignee_id == member.user_id,
                Task.project_id == project_id,
                Task.status.in_(['todo', 'in_progress'])
            ).count()
            
            utilization.append({
                "user_id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "role": member.role.value if member.role else "member",
                "task_count": task_count
            })
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "utilization": utilization
        }
    else:
        users = db.query(User).filter(User.is_active == True).all()
        
        utilization = []
        for user in users:
            total_assigned = db.query(Task).filter(
                Task.assignee_id == user.id,
                Task.status.in_(['todo', 'in_progress'])
            ).count()
            
            utilization.append({
                "user_id": user.id,
                "username": user.username,
                "full_name": user.full_name,
                "assigned_tasks": total_assigned
            })
        
        return {
            "items": utilization,
            "total": len(utilization)
        }
