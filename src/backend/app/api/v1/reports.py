# 企业项目管理系统 - 报表统计API
"""
数据统计和报表API
"""

from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import User, Project, Task, Plan, WBSTask, ProjectStatus, TaskStatus
from app.models.database import get_db
from app.core.security import get_current_user

router = APIRouter()


@router.get("/reports/stats")
async def get_statistics(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    project_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取核心统计数据"""
    # 项目统计
    project_query = db.query(Project).filter(Project.is_deleted == False)
    if project_id:
        project_query = project_query.filter(Project.id == project_id)

    total_projects = project_query.count()
    active_projects = project_query.filter(Project.status == ProjectStatus.ACTIVE).count()
    completed_projects = project_query.filter(Project.status == ProjectStatus.COMPLETED).count()

    # 逾期项目（当前日期超过结束日期且未完成）
    overdue_projects = project_query.filter(
        Project.end_date < datetime.utcnow(),
        Project.status.notin_([ProjectStatus.COMPLETED, ProjectStatus.ARCHIVED])
    ).count()

    # 任务统计
    task_query = db.query(Task).filter(Task.is_deleted == False)
    if project_id:
        task_query = task_query.filter(Task.project_id == project_id)

    total_tasks = task_query.count()
    completed_tasks = task_query.filter(Task.status == TaskStatus.DONE).count()

    # 逾期任务
    overdue_tasks = task_query.filter(
        Task.due_date < datetime.utcnow(),
        Task.status.notin_([TaskStatus.DONE, TaskStatus.ARCHIVED])
    ).count()

    # 计算平均进度（从任务计算，不依赖Project.progress列）
    avg_progress = 0
    if total_projects > 0:
        # 从关联任务计算项目平均进度
        avg_progress = db.query(func.avg(Task.progress)).filter(
            Task.is_deleted == False,
            Task.project_id.isnot(None)
        ).scalar() or 0

    return {
        "overview": {
            "project_total": total_projects,
            "project_active": active_projects,
            "project_completed": completed_projects,
            "project_overdue": overdue_projects,
            "task_total": total_tasks,
            "task_completed": completed_tasks,
            "task_overdue": overdue_tasks,
            "avg_progress": int(avg_progress),
            "budget_usage": 0,  # TODO: 预算相关
            "resource_usage": 0  # TODO: 资源相关
        }
    }


@router.get("/reports/project-rank")
async def get_project_rank(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    order: str = "updated_at",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目排行榜"""
    projects = db.query(Project).filter(
        Project.is_deleted == False
    ).offset(skip).limit(limit).all()

    result = []
    for project in projects:
        total_tasks = db.query(Task).filter(
            Task.project_id == project.id,
            Task.is_deleted == False
        ).count()

        completed_tasks = db.query(Task).filter(
            Task.project_id == project.id,
            Task.status == TaskStatus.DONE,
            Task.is_deleted == False
        ).count()

        result.append({
            "id": project.id,
            "name": project.name,
            "manager": project.owner.full_name if project.owner else "",
            "progress": project.progress or 0,
            "task_completed": completed_tasks,
            "task_total": total_tasks,
            "status": project.status.value,
            "updated_at": project.updated_at.strftime("%Y-%m-%d %H:%M:%S") if project.updated_at else ""
        })

    return {
        "items": result,
        "total": db.query(func.count(Project.id)).filter(Project.is_deleted == False).scalar()
    }


@router.get("/reports/task-stats")
async def get_task_stats(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    project_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取任务统计"""
    query = db.query(Task).filter(Task.is_deleted == False)

    if project_id:
        query = query.filter(Task.project_id == project_id)
    if status:
        query = query.filter(Task.status == TaskStatus(status))

    tasks = query.offset(skip).limit(limit).all()

    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "name": task.title,
            "project": task.project.name if task.project else "",
            "assignee": task.assignee.full_name if task.assignee else "",
            "status": task.status.value,
            "progress": task.progress or 0,
            "due_date": task.due_date.strftime("%Y-%m-%d") if task.due_date else ""
        })

    return {
        "items": result,
        "total": query.count()
    }


@router.get("/reports/resource-usage")
async def get_resource_usage(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    department_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取资源使用情况"""
    users = db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()

    result = []
    for user in users:
        assigned_tasks = db.query(Task).filter(
            Task.assignee_id == user.id,
            Task.is_deleted == False
        ).count()

        # 计算利用率（简化计算）
        planned_hours = assigned_tasks * 8  # 假设每个任务8小时
        actual_hours = planned_hours * (user.id % 3 + 5) / 10  # 模拟实际工时
        utilization = int(actual_hours / planned_hours * 100) if planned_hours > 0 else 0

        result.append({
            "id": user.id,
            "name": user.full_name or user.username,
            "department": "技术部",  # TODO: 添加部门字段
            "project_count": assigned_tasks,
            "planned_hours": planned_hours,
            "actual_hours": int(actual_hours),
            "utilization": utilization,
            "status": "high" if utilization > 100 else "normal" if utilization >= 50 else "low"
        })

    return {
        "items": result,
        "total": db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    }


@router.get("/reports/department-stats")
async def get_department_stats(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取部门统计数据"""
    # 模拟部门数据
    return [
        {
            "id": 1,
            "name": "技术部",
            "project_count": 8,
            "completed_count": 3,
            "avg_progress": 65,
            "member_count": 15
        },
        {
            "id": 2,
            "name": "产品部",
            "project_count": 5,
            "completed_count": 2,
            "avg_progress": 72,
            "member_count": 8
        },
        {
            "id": 3,
            "name": "设计部",
            "project_count": 4,
            "completed_count": 1,
            "avg_progress": 45,
            "member_count": 6
        },
        {
            "id": 4,
            "name": "市场部",
            "project_count": 3,
            "completed_count": 1,
            "avg_progress": 58,
            "member_count": 10
        }
    ]


@router.get("/reports/export")
async def export_report(
    report_type: str,
    format: str = "excel",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    project_id: Optional[int] = None,
    include_charts: bool = True,
    current_user: User = Depends(get_current_user)
):
    """导出报表"""
    # TODO: 实现实际导出功能
    return {
        "message": "导出功能开发中",
        "report_type": report_type,
        "format": format
    }


@router.get("/reports/templates")
async def get_report_templates(current_user: User = Depends(get_current_user)):
    """获取报表模板列表"""
    return {
        "items": [
            {"id": 1, "name": "项目进度周报", "type": "weekly", "description": "每周项目进度汇总"},
            {"id": 2, "name": "项目进度月报", "type": "monthly", "description": "每月项目进度汇总"},
            {"id": 3, "name": "任务完成报表", "type": "task", "description": "任务完成情况统计"},
            {"id": 4, "name": "资源使用报表", "type": "resource", "description": "资源使用情况统计"}
        ]
    }


@router.get("/reports/timeline")
async def get_project_timeline(
    project_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目时间线"""
    query = db.query(Project).filter(Project.is_deleted == False)
    if project_id:
        query = query.filter(Project.id == project_id)
    
    projects = query.all()
    
    items = []
    for project in projects:
        items.append({
            "id": project.id,
            "name": project.name,
            "start_date": project.start_date.isoformat() if project.start_date else None,
            "end_date": project.end_date.isoformat() if project.end_date else None,
            "status": project.status
        })
    
    return {"items": items}


@router.get("/reports/burndown")
async def get_burndown_chart(
    project_id: int = Query(..., description="项目ID"),
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取燃尽图数据"""
    # TODO: 实现实际燃尽图计算逻辑
    # 返回模拟数据
    import datetime
    
    if not start_date:
        start_date = (datetime.datetime.now() - datetime.timedelta(days=14)).strftime("%Y-%m-%d")
    if not end_date:
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    items = []
    total = 100
    current = total
    
    start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    days = (end - start).days + 1
    
    for i in range(days):
        date = start + datetime.timedelta(days=i)
        current = max(0, current - total // days)
        items.append({
            "date": date.strftime("%Y-%m-%d"),
            "remaining": current,
            "ideal": int(total * (1 - i / days)),
            "completed": total - current
        })
    
    return {
        "project_id": project_id,
        "items": items,
        "total": total
    }


@router.get("/reports/workload")
async def get_workload_distribution(
    project_id: Optional[int] = None,
    department_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取工作量分布"""
    # 返回模拟数据
    return {
        "items": [
            {"user_id": 1, "name": "张三", "task_count": 5, "hours": 40},
            {"user_id": 2, "name": "李四", "task_count": 3, "hours": 24},
            {"user_id": 3, "name": "王五", "task_count": 7, "hours": 56}
        ]
    }

