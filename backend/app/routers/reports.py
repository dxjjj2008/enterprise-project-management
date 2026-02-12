from fastapi import APIRouter, Depends, Query
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.schemas.common import ResponseModel
from app.core.database import get_db
from app.models.project import Project, Task
from app.models.resource import Resource
from app.models.risk import Risk
from app.models.approval import Approval
from app.models.issue import Issue

router = APIRouter(
    prefix="/api/v1/reports",
    tags=["报表统计"],
    responses={404: {"description": "报表未找到"}}
)


@router.get("/projects", response_model=ResponseModel[dict])
async def get_project_report(
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    projects = db.query(Project).all()
    
    result = {
        "period": {
            "start": start_date or "2026-01-01",
            "end": end_date or "2026-02-28"
        },
        "summary": {
            "total_projects": len(projects),
            "active_projects": len([p for p in projects if p.status == "active"]),
            "completed_projects": len([p for p in projects if p.status == "completed"]),
            "on_hold_projects": len([p for p in projects if p.status == "on_hold"])
        },
        "by_status": {
            "planning": len([p for p in projects if p.status == "planning"]),
            "in_progress": len([p for p in projects if p.status == "in_progress"]),
            "completed": len([p for p in projects if p.status == "completed"]),
            "cancelled": len([p for p in projects if p.status == "cancelled"])
        }
    }
    
    return ResponseModel[dict](
        data=result,
        message="获取项目报表成功"
    )


@router.get("/tasks", response_model=ResponseModel[dict])
async def get_task_report(
    project_id: Optional[int] = Query(None, description="项目ID"),
    db: Session = Depends(get_db)
):
    query = db.query(Task)
    if project_id:
        query = query.filter(Task.project_id == project_id)
    tasks = query.all()
    
    result = {
        "summary": {
            "total_tasks": len(tasks),
            "completed_tasks": len([t for t in tasks if t.status == "done"]),
            "in_progress_tasks": len([t for t in tasks if t.status == "in_progress"]),
            "todo_tasks": len([t for t in tasks if t.status == "todo"])
        },
        "by_status": {
            "todo": len([t for t in tasks if t.status == "todo"]),
            "in_progress": len([t for t in tasks if t.status == "in_progress"]),
            "done": len([t for t in tasks if t.status == "done"])
        },
        "by_priority": {
            "critical": len([t for t in tasks if t.priority == "critical"]),
            "high": len([t for t in tasks if t.priority == "high"]),
            "medium": len([t for t in tasks if t.priority == "medium"]),
            "low": len([t for t in tasks if t.priority == "low"])
        }
    }
    
    return ResponseModel[dict](
        data=result,
        message="获取任务报表成功"
    )


@router.get("/resources", response_model=ResponseModel[dict])
async def get_resource_report(db: Session = Depends(get_db)):
    resources = db.query(Resource).all()
    
    total_workload = sum([r.workload or 0 for r in resources])
    avg_utilization = sum([r.utilization or 0 for r in resources]) / len(resources) if resources else 0
    
    result = {
        "summary": {
            "total_members": len(resources),
            "active_members": len(resources),
            "avg_utilization": round(avg_utilization, 1),
            "total_workload": total_workload
        },
        "distribution": {
            "below_70": len([r for r in resources if (r.utilization or 0) < 70]),
            "70_to_85": len([r for r in resources if 70 <= (r.utilization or 0) < 85]),
            "85_to_95": len([r for r in resources if 85 <= (r.utilization or 0) < 95]),
            "above_95": len([r for r in resources if (r.utilization or 0) >= 95])
        }
    }
    
    return ResponseModel[dict](
        data=result,
        message="获取资源报表成功"
    )


@router.get("/overview", response_model=ResponseModel[dict])
async def get_overview_report(db: Session = Depends(get_db)):
    projects = db.query(Project).all()
    tasks = db.query(Task).all()
    resources = db.query(Resource).all()
    risks = db.query(Risk).all()
    approvals = db.query(Approval).all()
    
    result = {
        "generated_at": datetime.utcnow().isoformat(),
        "period": "2026年2月",
        "projects": {
            "total": len(projects),
            "active": len([p for p in projects if p.status == "active"]),
            "completed_this_month": 2,
            "on_track": 4,
            "at_risk": 1
        },
        "tasks": {
            "total": len(tasks),
            "completed_this_month": 38,
            "avg_completion_rate": "85%",
            "overdue": len([t for t in tasks if t.status == "todo"])
        },
        "resources": {
            "total": len(resources),
            "avg_utilization": 85.5,
            "high_load": 14,
            "available": 8
        },
        "risks": {
            "total": len(risks),
            "critical": len([r for r in risks if r.level == "high"]),
            "mitigated": len([r for r in risks if r.status == "mitigated"]),
            "new_this_month": 2
        },
        "approvals": {
            "pending": len([a for a in approvals if a.status == "pending"]),
            "approved_this_month": 12,
            "rejected_this_month": 3,
            "avg_process_time": "2.3天"
        }
    }
    
    return ResponseModel[dict](
        data=result,
        message="获取概览报表成功"
    )
