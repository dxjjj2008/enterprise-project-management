# 任务API路由模块
"""
任务相关的API端点
包括任务的CRUD操作和依赖关系管理
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.database import get_db
from app.models.task import TaskDependency
from app.models import Task
from app.schemas.task import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskDetailResponse,
    TaskDependencyCreate,
    TaskDependencyUpdate,
    TaskDependencyResponse,
    TaskQuery,
    TaskListResponse,
    TaskDependenciesResponse,
)
from app.core.security import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ============================================================================
# 任务CRUD API
# ============================================================================

@router.post("/", response_model=TaskResponse, summary="创建任务", status_code=201)
def create_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    创建新任务

    - **name**: 任务名称（必填）
    - **description**: 任务描述
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    - **status**: 任务状态
    - **progress**: 进度百分比 (0-100)
    - **priority**: 优先级
    - **project_id**: 项目ID
    - **parent_id**: 父任务ID（用于分组）
    - **task_type**: 任务类型
    - **is_milestone**: 是否为里程碑
    - **is_group**: 是否为任务组
    - **dependencies**: 依赖的任务ID列表
    """
    # 创建任务对象
    task = Task(**task_data.dict(exclude_unset=True))

    # 设置默认值
    if not task.start_date:
        task.start_date = datetime.utcnow()

    if not task.end_date:
        task.end_date = datetime.utcnow()

    # 计算持续时间
    if task.start_date and task.end_date:
        delta = task.end_date - task.start_date
        task.duration = delta.days + 1  # 包括结束日

    # 设置创建者和更新者
    task.created_by = current_user.get("id")
    task.updated_by = current_user.get("id")

    # 添加到数据库
    db.add(task)
    db.commit()
    db.refresh(task)

    # 加载关联数据
    load_task_relations(db, task)

    return task


@router.get("/{task_id}", response_model=TaskDetailResponse, summary="获取任务详情")
def get_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取任务详细信息

    包含：
    - 任务基本信息
    - 子任务列表
    - 依赖的任务
    - 依赖此任务的任务
    - 负责人信息
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 加载关联数据
    load_task_relations(db, task)

    return task


@router.get("/", response_model=TaskListResponse, summary="获取任务列表")
def get_tasks(
    project_id: Optional[int] = Query(None, description="项目ID"),
    status: Optional[str] = Query(None, description="任务状态"),
    priority: Optional[str] = Query(None, description="优先级"),
    task_type: Optional[str] = Query(None, description="任务类型"),
    is_milestone: Optional[bool] = Query(None, description="是否为里程碑"),
    is_group: Optional[bool] = Query(None, description="是否为任务组"),
    parent_id: Optional[int] = Query(None, description="父任务ID"),
    assignee_id: Optional[int] = Query(None, description="负责人ID"),
    start_date: Optional[str] = Query(None, description="开始日期（起始）"),
    end_date: Optional[str] = Query(None, description="结束日期（结束）"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取任务列表（支持分页和筛选）

    - **project_id**: 项目ID
    - **status**: 任务状态
    - **priority**: 优先级
    - **task_type**: 任务类型
    - **is_milestone**: 是否为里程碑
    - **is_group**: 是否为任务组
    - **parent_id**: 父任务ID
    - **assignee_id**: 负责人ID
    - **start_date**: 开始日期（起始）
    - **end_date**: 结束日期（结束）
    """
    query = db.query(Task)

    # 筛选条件
    if project_id is not None:
        query = query.filter(Task.project_id == project_id)

    if status:
        query = query.filter(Task.status == status)

    if priority:
        query = query.filter(Task.priority == priority)

    if task_type:
        query = query.filter(Task.task_type == task_type)

    if is_milestone is not None:
        query = query.filter(Task.is_milestone == is_milestone)

    if is_group is not None:
        query = query.filter(Task.is_group == is_group)

    if parent_id is not None:
        query = query.filter(Task.parent_id == parent_id)

    if assignee_id is not None:
        query = query.filter(Task.assignee_id == assignee_id)

    if start_date:
        query = query.filter(Task.start_date >= start_date)

    if end_date:
        query = query.filter(Task.end_date <= end_date)

    # 分页
    page = QueryParams().page
    page_size = QueryParams().page_size

    total = query.count()
    tasks = query.offset((page - 1) * page_size).limit(page_size).all()

    # 加载关联数据
    for task in tasks:
        load_task_relations(db, task)

    return TaskListResponse(
        total=total,
        items=tasks,
        page=page,
        page_size=page_size
    )


@router.put("/{task_id}", response_model=TaskResponse, summary="更新任务")
def update_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    更新任务信息

    - **name**: 任务名称
    - **description**: 任务描述
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    - **status**: 任务状态
    - **progress**: 进度百分比
    - **priority**: 优先级
    - **parent_id**: 父任务ID
    - **task_type**: 任务类型
    - **is_milestone**: 是否为里程碑
    - **is_group**: 是否为 task组
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 更新字段
    update_data = task_data.dict(exclude_unset=True)

    # 处理日期
    if "start_date" in update_data:
        task.start_date = datetime.fromisoformat(update_data["start_date"])

    if "end_date" in update_data:
        task.end_date = datetime.fromisoformat(update_data["end_date"])

    # 计算持续时间
    if task.start_date and task.end_date:
        delta = task.end_date - task.start_date
        task.duration = delta.days + 1

    # 更新任务状态
    if "status" in update_data:
        task.status = update_data["status"]

    if "progress" in update_data:
        task.progress = update_data["progress"]

        # 如果进度是100%，自动设置状态为done
        if update_data["progress"] == 100 and task.status != "done":
            task.status = "done"
            task.is_completed = True

    if "priority" in update_data:
        task.priority = update_data["priority"]

    if "parent_id" in update_data:
        task.parent_id = update_data["parent_id"]

    if "task_type" in update_data:
        task.task_type = update_data["task_type"]

    if "is_milestone" in update_data:
        task.is_milestone = update_data["is_milestone"]

    if "is_group" in update_data:
        task.is_group = update_data["is_group"]

    # 更新者
    task.updated_by = current_user.get("id")

    db.commit()
    db.refresh(task)

    # 加载关联数据
    load_task_relations(db, task)

    return task


@router.delete("/{task_id}", summary="删除任务")
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    删除任务

    **注意**：删除任务会级联删除其子任务
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 如果是任务组，删除所有子任务
    if task.is_group:
        child_ids = [child.id for child in task.children]
        db.query(Task).filter(Task.id.in_(child_ids)).delete(synchronize_session=False)

    # 删除依赖关系
    db.query(TaskDependency).filter(
        (TaskDependency.parent_id == task_id) | (TaskDependency.dependent_id == task_id)
    ).delete(synchronize_session=False)

    # 删除任务
    db.delete(task)
    db.commit()

    return {"message": "任务删除成功", "task_id": task_id}


# ============================================================================
# 任务依赖关系API
# ============================================================================

@router.post("/dependencies/", response_model=TaskDependencyResponse, summary="创建依赖关系", status_code=201)
def create_dependency(
    dependency_data: TaskDependencyCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    创建任务依赖关系

    - **parent_id**: 父任务ID（被依赖的任务）
    - **dependent_id**: 子任务ID（依赖的任务）
    - **type**: 依赖类型（fs, ss, ff, sf）
    - **condition**: 依赖条件描述
    """
    # 检查任务是否存在
    parent = db.query(Task).filter(Task.id == dependency_data.parent_id).first()
    dependent = db.query(Task).filter(Task.id == dependency_data.dependent_id).first()

    if not parent:
        raise HTTPException(status_code=404, detail=f"父任务 {dependency_data.parent_id} 不存在")
    if not dependent:
        raise HTTPException(status_code=404, detail=f"子任务 {dependency_data.dependent_id} 不存在")

    # 检查是否已经存在依赖关系
    existing = db.query(TaskDependency).filter(
        TaskDependency.parent_id == dependency_data.parent_id,
        TaskDependency.dependent_id == dependency_data.dependent_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="依赖关系已存在")

    # 创建依赖关系
    dependency = TaskDependency(**dependency_data.dict())

    db.add(dependency)
    db.commit()
    db.refresh(dependency)

    return dependency


@router.get("/dependencies/{task_id}", response_model=TaskDependenciesResponse, summary="获取任务依赖")
def get_task_dependencies(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    获取任务的依赖关系

    包含：
    - 依赖的任务
    - 依赖此任务的任务
    """
    task = db.query(Task).filter(Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 获取依赖的任务
    dependencies = db.query(Task).join(
        TaskDependency, TaskDependency.dependent_id == Task.id
    ).filter(TaskDependency.parent_id == task_id).all()

    # 获取依赖此任务的任务
    dependents = db.query(Task).join(
        TaskDependency, TaskDependency.parent_id == Task.id
    ).filter(TaskDependency.dependent_id == task_id).all()

    # 加载关联数据
    for task_item in dependencies + dependents:
        load_task_relations(db, task_item)

    return TaskDependenciesResponse(
        task_id=task_id,
        dependencies=dependencies,
        dependents=dependents
    )


@router.delete("/dependencies/", summary="删除依赖关系")
def delete_dependency(
    parent_id: int = Query(..., description="父任务ID"),
    dependent_id: int = Query(..., description="子任务ID"),
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    删除任务依赖关系

    - **parent_id**: 父任务ID
    - **dependent_id**: 子任务ID
    """
    dependency = db.query(TaskDependency).filter(
        TaskDependency.parent_id == parent_id,
        TaskDependency.dependent_id == dependent_id
    ).first()

    if not dependency:
        raise HTTPException(status_code=404, detail="依赖关系不存在")

    db.delete(dependency)
    db.commit()

    return {"message": "依赖关系删除成功"}


# ============================================================================
# 工具函数
# ============================================================================

def load_task_relations(db: Session, task: Task):
    """
    加载任务的关联数据
    """
    # 加载子任务（递归加载）
    task.children = db.query(Task).filter(Task.parent_id == task.id).all()
    for child in task.children:
        load_task_relations(db, child)

    # 加载依赖的任务
    task.dependencies = db.query(Task).join(
        TaskDependency, TaskDependency.dependent_id == Task.id
    ).filter(TaskDependency.parent_id == task.id).all()

    # 加载依赖此任务的任务
    task.dependents = db.query(Task).join(
        TaskDependency, TaskDependency.parent_id == Task.id
    ).filter(TaskDependency.dependent_id == task.id).all()

    # 加载负责人信息
    if task.assignee_id:
        # 这里可以添加用户信息加载
        task.assignee = {"id": task.assignee_id, "name": f"用户{task.assignee_id}"}


class QueryParams:
    """查询参数类"""
    page = 1
    page_size = 20


# 导出
__all__ = ["router"]
