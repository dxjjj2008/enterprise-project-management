from fastapi import APIRouter, Depends, Query, Path
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.schemas.common import ResponseModel
from app.core.database import get_db
from app.models.project import Task

router = APIRouter(
    prefix="/api/v1/projects/{project_id}/gantt",
    tags=["甘特图"],
    responses={404: {"description": "数据未找到"}}
)


@router.get("", response_model=ResponseModel[dict])
async def get_gantt_data(
    project_id: int = Path(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    
    all_dates = []
    for task in tasks:
        if task.start_date:
            all_dates.append(task.start_date)
        if task.end_date:
            all_dates.append(task.end_date)
    
    min_date = min(all_dates) if all_dates else datetime.now()
    max_date = max(all_dates) if all_dates else datetime.now()
    
    result = {
        "project_id": project_id,
        "tasks": tasks,
        "timeline": {
            "start": str(min_date),
            "end": str(max_date)
        },
        "stats": {
            "total": len(tasks),
            "completed": len([t for t in tasks if t.status == "done"]),
            "in_progress": len([t for t in tasks if t.status == "in_progress"]),
            "not_started": len([t for t in tasks if t.status == "todo"])
        }
    }
    
    return ResponseModel[dict](
        data=result,
        message="获取甘特图数据成功"
    )


@router.get("/milestones", response_model=ResponseModel[list])
async def get_project_milestones(
    project_id: int = Path(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    return ResponseModel[list](
        data=[],
        message="里程碑功能待实现"
    )
