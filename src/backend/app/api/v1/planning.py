# 企业项目管理系统 - 计划管理API
"""
计划管理和WBS任务API
"""

from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models import User, Project, Plan, WBSTask, PlanMilestone, ProjectStatus, PlanStatus
from app.models.database import get_db
from app.core.security import get_current_user

router = APIRouter()


# ============ Pydantic Models ============
class PlanCreate(BaseModel):
    """创建计划请求"""
    name: str
    project_id: int
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class PlanUpdate(BaseModel):
    """更新计划请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[PlanStatus] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class WBSTaskCreate(BaseModel):
    """创建WBS任务请求"""
    name: str
    parent_id: Optional[int] = None
    level: int = 1
    planned_start: Optional[str] = None
    planned_end: Optional[str] = None
    planned_duration: Optional[int] = None
    progress: Optional[int] = 0
    status: Optional[str] = "pending"
    assignee_id: Optional[int] = None
    is_milestone: Optional[bool] = False


class WBSTaskUpdate(BaseModel):
    """更新WBS任务请求"""
    name: Optional[str] = None
    parent_id: Optional[int] = None
    level: Optional[int] = None
    planned_start: Optional[str] = None
    planned_end: Optional[str] = None
    planned_duration: Optional[int] = None
    progress: Optional[int] = None
    status: Optional[str] = None
    assignee_id: Optional[int] = None
    is_milestone: Optional[bool] = None


class MilestoneCreate(BaseModel):
    """创建里程碑请求"""
    name: str
    plan_date: str
    task_id: Optional[int] = None
    status: Optional[str] = "pending"


@router.get("/plans")
async def get_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    project_id: Optional[int] = None,
    status: Optional[PlanStatus] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取计划列表"""
    query = db.query(Plan).filter(Plan.is_deleted == False)

    if project_id:
        query = query.filter(Plan.project_id == project_id)
    if status:
        query = query.filter(Plan.status == status)
    if keyword:
        query = query.filter(Plan.name.contains(keyword))

    # 获取用户有权限的项目
    project_ids = db.query(Project.id).filter(
        Project.owner_id == current_user.id
    ).all()
    project_ids = [p[0] for p in project_ids]

    query = query.filter(Plan.project_id.in_(project_ids))

    total = query.count()
    plans = query.offset(skip).limit(limit).all()

    # 计算任务统计
    result = []
    for plan in plans:
        task_count = db.query(WBSTask).filter(
            WBSTask.plan_id == plan.id,
            WBSTask.is_deleted == False
        ).count()

        completed_count = db.query(WBSTask).filter(
            WBSTask.plan_id == plan.id,
            WBSTask.status == "completed",
            WBSTask.is_deleted == False
        ).count()

        plan_data = {
            **plan.__dict__,
            "task_count": task_count,
            "completed_task_count": completed_count,
            "project_name": plan.project.name if plan.project else ""
        }
        result.append(plan_data)

    return {
        "items": result,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/plans/{plan_id}")
async def get_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取计划详情"""
    plan = db.query(Plan).filter(
        Plan.id == plan_id,
        Plan.is_deleted == False
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    return {
        **plan.__dict__,
        "project_name": plan.project.name if plan.project else ""
    }


@router.post("/plans")
async def create_plan(
    plan_data: PlanCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建计划"""
    project = db.query(Project).filter(Project.id == plan_data.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # Convert date strings to date objects
    start_date = date.fromisoformat(plan_data.start_date) if plan_data.start_date else None
    end_date = date.fromisoformat(plan_data.end_date) if plan_data.end_date else None

    plan = Plan(
        name=plan_data.name,
        project_id=plan_data.project_id,
        description=plan_data.description,
        start_date=start_date,
        end_date=end_date,
        owner_id=current_user.id
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    return {
        **plan.__dict__,
        "project_name": project.name
    }


@router.put("/plans/{plan_id}")
async def update_plan(
    plan_id: int,
    plan_data: PlanUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新计划"""
    plan = db.query(Plan).filter(
        Plan.id == plan_id,
        Plan.is_deleted == False
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    if plan_data.name:
        plan.name = plan_data.name
    if plan_data.description is not None:
        plan.description = plan_data.description
    if plan_data.status:
        plan.status = plan_data.status
    if plan_data.start_date:
        plan.start_date = date.fromisoformat(plan_data.start_date)
    if plan_data.end_date:
        plan.end_date = date.fromisoformat(plan_data.end_date)

    plan.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(plan)

    return plan


@router.delete("/plans/{plan_id}")
async def delete_plan(
    plan_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除计划"""
    plan = db.query(Plan).filter(
        Plan.id == plan_id,
        Plan.is_deleted == False
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    plan.is_deleted = True
    db.commit()

    return {"message": "计划已删除"}


# WBS任务相关接口
@router.get("/plans/{plan_id}/wbs")
async def get_wbs_tasks(
    plan_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取WBS任务列表"""
    # 检查计划是否存在
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.is_deleted == False).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    
    total = db.query(WBSTask).filter(
        WBSTask.plan_id == plan_id,
        WBSTask.is_deleted == False
    ).count()
    
    tasks = db.query(WBSTask).filter(
        WBSTask.plan_id == plan_id,
        WBSTask.is_deleted == False
    ).order_by(WBSTask.sort_order).offset(skip).limit(limit).all()
    
    return {
        "items": tasks,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }


@router.post("/plans/{plan_id}/wbs")
async def add_wbs_task(
    plan_id: int,
    task_data: WBSTaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加WBS任务"""
    plan = db.query(Plan).filter(
        Plan.id == plan_id,
        Plan.is_deleted == False
    ).first()

    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")

    level = 1
    if task_data.parent_id:
        parent = db.query(WBSTask).filter(WBSTask.id == task_data.parent_id).first()
        if parent:
            level = parent.level + 1

    max_order = db.query(func.max(WBSTask.sort_order)).filter(
        WBSTask.plan_id == plan_id,
        WBSTask.parent_id == task_data.parent_id
    ).scalar() or -1

    # Convert date strings to date objects
    start_date = date.fromisoformat(task_data.planned_start) if task_data.planned_start else None
    end_date = date.fromisoformat(task_data.planned_end) if task_data.planned_end else None

    task = WBSTask(
        plan_id=plan_id,
        parent_id=task_data.parent_id,
        name=task_data.name,
        level=level,
        sort_order=max_order + 1,
        assignee_id=task_data.assignee_id,
        start_date=start_date,
        end_date=end_date,
        duration=task_data.planned_duration or 1,
        progress=task_data.progress or 0,
        is_milestone=task_data.is_milestone or False
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    update_plan_progress(plan_id, db)

    return {
        "id": task.id,
        "name": task.name,
        "level": task.level,
        "progress": task.progress,
        "status": task.status,
        "message": "任务创建成功"
    }


@router.put("/plans/{plan_id}/wbs/{task_id}")
async def update_wbs_task(
    plan_id: int,
    task_id: int,
    task_data: WBSTaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新WBS任务"""
    task = db.query(WBSTask).filter(
        WBSTask.id == task_id,
        WBSTask.plan_id == plan_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task_data.name:
        task.name = task_data.name
    if task_data.assignee_id is not None:
        task.assignee_id = task_data.assignee_id
    if task_data.planned_start:
        task.start_date = date.fromisoformat(task_data.planned_start)
    if task_data.planned_end:
        task.end_date = date.fromisoformat(task_data.planned_end)
    if task_data.planned_duration is not None:
        task.duration = task_data.planned_duration
    if task_data.progress is not None:
        task.progress = task_data.progress
    if task_data.is_milestone is not None:
        task.is_milestone = task_data.is_milestone
    if task_data.status:
        task.status = task_data.status

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)

    # 更新计划进度
    update_plan_progress(plan_id, db)

    return {
        "id": task.id,
        "name": task.name,
        "progress": task.progress,
        "status": task.status,
        "message": "任务更新成功"
    }


@router.delete("/plans/{plan_id}/wbs/{task_id}")
async def delete_wbs_task(
    plan_id: int,
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除WBS任务"""
    task = db.query(WBSTask).filter(
        WBSTask.id == task_id,
        WBSTask.plan_id == plan_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 软删除
    task.is_deleted = True
    db.commit()

    # 更新计划进度
    update_plan_progress(plan_id, db)

    return {"message": "任务已删除"}


# 里程碑相关接口
@router.get("/plans/{plan_id}/milestones")
async def get_plan_milestones(
    plan_id: int,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取计划里程碑列表"""
    # 检查计划是否存在
    plan = db.query(Plan).filter(Plan.id == plan_id, Plan.is_deleted == False).first()
    if not plan:
        raise HTTPException(status_code=404, detail="计划不存在")
    
    total = db.query(PlanMilestone).filter(PlanMilestone.plan_id == plan_id).count()
    
    milestones = db.query(PlanMilestone).filter(
        PlanMilestone.plan_id == plan_id
    ).offset(skip).limit(limit).all()

    return {
        "items": milestones,
        "total": total,
        "page": skip // limit + 1 if limit > 0 else 1,
        "page_size": limit
    }


@router.post("/plans/{plan_id}/milestones")
async def add_plan_milestone(
    plan_id: int,
    name: str,
    plan_date: str,
    task_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加里程碑"""
    # Convert date string to date object
    milestone_date = date.fromisoformat(plan_date)
    
    milestone = PlanMilestone(
        plan_id=plan_id,
        task_id=task_id,
        name=name,
        plan_date=milestone_date
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)

    return milestone


@router.put("/plans/{plan_id}/milestones/{milestone_id}")
async def update_plan_milestone(
    plan_id: int,
    milestone_id: int,
    name: Optional[str] = None,
    plan_date: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新里程碑"""
    milestone = db.query(PlanMilestone).filter(
        PlanMilestone.id == milestone_id,
        PlanMilestone.plan_id == plan_id
    ).first()

    if not milestone:
        raise HTTPException(status_code=404, detail="里程碑不存在")

    if name:
        milestone.name = name
    if plan_date:
        milestone.plan_date = date.fromisoformat(plan_date)
    if status:
        milestone.status = status

    db.commit()
    db.refresh(milestone)

    return milestone


@router.delete("/plans/{plan_id}/milestones/{milestone_id}")
async def delete_plan_milestone(
    plan_id: int,
    milestone_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除里程碑"""
    milestone = db.query(PlanMilestone).filter(
        PlanMilestone.id == milestone_id,
        PlanMilestone.plan_id == plan_id
    ).first()

    if not milestone:
        raise HTTPException(status_code=404, detail="里程碑不存在")

    db.delete(milestone)
    db.commit()

    return {"message": "里程碑已删除"}


@router.get("/projects/list")
async def get_project_list(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目列表（用于下拉选择）"""
    projects = db.query(Project).filter(
        Project.is_deleted == False
    ).all()

    return [{"id": p.id, "name": p.name} for p in projects]


def update_plan_progress(plan_id: int, db: Session):
    """更新计划进度"""
    tasks = db.query(WBSTask).filter(
        WBSTask.plan_id == plan_id,
        WBSTask.is_deleted == False
    ).all()

    if not tasks:
        return

    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == "completed")
    progress = int(completed / total * 100) if total > 0 else 0

    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    if plan:
        plan.progress = progress
        plan.updated_at = datetime.utcnow()
        db.commit()
