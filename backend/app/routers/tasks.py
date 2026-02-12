from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.schemas.common import ResponseModel, PaginationResponse
from app.schemas.project import TaskCreate, TaskUpdate, TaskResponse
from app.core.database import get_db
from app.models.project import Task

# 创建独立的任务路由器（用于全局任务看板）
tasks_router = APIRouter(
    prefix="/api/v1/tasks",
    tags=["全局任务"],
    responses={404: {"description": "任务未找到"}}
)

# 项目内任务路由器
router = APIRouter(
    prefix="/api/v1/projects/{project_id}/tasks",
    tags=["任务管理"],
    responses={404: {"description": "任务未找到"}}
)


# 全局任务看板端点
@tasks_router.get("/board", response_model=ResponseModel[dict])
async def get_all_tasks_board(db: Session = Depends(get_db)):
    """获取所有任务的任务看板（不按项目分组）"""
    tasks = db.query(Task).all()
    
    def task_to_dict(task):
        return {
            "id": task.id,
            "project_id": task.project_id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "assigned_to": task.assigned_to,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }
    
    todo_tasks = [task_to_dict(t) for t in tasks if t.status == "todo"]
    in_progress_tasks = [task_to_dict(t) for t in tasks if t.status == "in_progress"]
    done_tasks = [task_to_dict(t) for t in tasks if t.status == "done"]
    
    board_data = {
        "columns": {
            "todo": todo_tasks,
            "in_progress": in_progress_tasks,
            "done": done_tasks
        },
        "stats": {
            "total": len(tasks),
            "todo": len(todo_tasks),
            "in_progress": len(in_progress_tasks),
            "done": len(done_tasks)
        }
    }
    
    return ResponseModel[dict](
        data=board_data,
        message="获取任务看板成功"
    )


# 获取所有任务
@tasks_router.get("", response_model=ResponseModel[List[TaskResponse]])
async def get_all_tasks(
    status: Optional[str] = Query(None, description="状态筛选"),
    priority: Optional[str] = Query(None, description="优先级筛选"),
    db: Session = Depends(get_db)
):
    query = db.query(Task)
    
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    
    tasks = query.all()
    
    return ResponseModel[List[TaskResponse]](
        data=tasks,
        message="获取任务列表成功"
    )


@router.get("", response_model=PaginationResponse[TaskResponse])
async def get_tasks(
    project_id: int = Path(..., description="项目ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None, description="状态筛选"),
    priority: Optional[str] = Query(None, description="优先级筛选"),
    assignee: Optional[str] = Query(None, description="负责人筛选"),
    db: Session = Depends(get_db)
):
    query = db.query(Task).filter(Task.project_id == project_id)
    
    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assignee:
        query = query.filter(Task.assigned_to == assignee)
    
    total = query.count()
    tasks = query.offset(skip).limit(limit).all()
    
    return PaginationResponse[TaskResponse](
        data=tasks,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        message="获取任务列表成功"
    )


@router.get("/board", response_model=ResponseModel[dict])
async def get_task_board(
    project_id: int = Path(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    
    def task_to_dict(task):
        return {
            "id": task.id,
            "project_id": task.project_id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "assigned_to": task.assigned_to,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        }
    
    board_data = {
        "project_id": project_id,
        "columns": {
            "todo": [task_to_dict(t) for t in tasks if t.status == "todo"],
            "in_progress": [task_to_dict(t) for t in tasks if t.status == "in_progress"],
            "done": [task_to_dict(t) for t in tasks if t.status == "done"]
        },
        "stats": {
            "total": len(tasks),
            "todo": len([t for t in tasks if t.status == "todo"]),
            "in_progress": len([t for t in tasks if t.status == "in_progress"]),
            "done": len([t for t in tasks if t.status == "done"])
        }
    }
    
    return ResponseModel[dict](
        data=board_data,
        message="获取任务看板成功"
    )


@router.get("/{task_id}", response_model=ResponseModel[TaskResponse])
async def get_task(
    project_id: int = Path(..., description="项目ID"),
    task_id: int = Path(..., description="任务ID"),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    
    return ResponseModel[TaskResponse](
        data=task,
        message="获取任务成功"
    )


@router.post("", response_model=ResponseModel[TaskResponse])
async def create_task(
    project_id: int = Path(..., description="项目ID"),
    task_data: TaskCreate = ...,
    db: Session = Depends(get_db)
):
    task = Task(
        project_id=project_id,
        title=task_data.title,
        description=task_data.description,
        status=task_data.status or "todo",
        priority=task_data.priority or "medium",
        assigned_to=task_data.assigned_to,
        due_date=task_data.due_date
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    
    return ResponseModel[TaskResponse](
        data=task,
        message="任务创建成功"
    )


@router.put("/{task_id}", response_model=ResponseModel[TaskResponse])
async def update_task(
    project_id: int = Path(..., description="项目ID"),
    task_id: int = Path(..., description="任务ID"),
    task_update: TaskUpdate = ...,
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    
    update_data = task_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(task, key, value)
    
    db.commit()
    db.refresh(task)
    
    return ResponseModel[TaskResponse](
        data=task,
        message="任务更新成功"
    )


@router.put("/{task_id}/status", response_model=ResponseModel[TaskResponse])
async def update_task_status(
    project_id: int = Path(..., description="项目ID"),
    task_id: int = Path(..., description="任务ID"),
    status: str = Query(..., description="新状态"),
    db: Session = Depends(get_db)
):
    if status not in ["todo", "in_progress", "done"]:
        raise HTTPException(status_code=400, detail="无效的状态值")
    
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    
    task.status = status
    db.commit()
    db.refresh(task)
    
    return ResponseModel[TaskResponse](
        data=task,
        message="任务状态更新成功"
    )


@router.delete("/{task_id}", response_model=ResponseModel)
async def delete_task(
    project_id: int = Path(..., description="项目ID"),
    task_id: int = Path(..., description="任务ID"),
    db: Session = Depends(get_db)
):
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    
    db.delete(task)
    db.commit()
    
    return ResponseModel(
        success=True,
        message="任务删除成功"
    )
