from fastapi import APIRouter, Depends, Query, Path
from typing import Optional, List
from sqlalchemy.orm import Session
from datetime import datetime

from app.schemas.common import ResponseModel, PaginationResponse
from app.core.database import get_db
from app.models.resource import Resource
from app.models.user import User

router = APIRouter(
    prefix="/api/v1/resources",
    tags=["资源管理"],
    responses={404: {"description": "资源未找到"}}
)


# 获取用户列表（前端调用）
@router.get("/users", response_model=ResponseModel[dict])
async def get_users(
    is_active: Optional[bool] = Query(None, description="是否在职"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    db: Session = Depends(get_db)
):
    query = db.query(User)
    
    # 使用 is_active 字段（User模型中）
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    
    user_list = []
    for user in users:
        user_list.append({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_active": user.is_active,
            "is_superuser": user.is_superuser,
            "created_at": user.created_at.isoformat() if user.created_at else None
        })
    
    return ResponseModel[dict](
        data={
            "items": user_list,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "page_size": limit
        },
        message="获取用户列表成功"
    )


# 获取团队工作负载（前端调用）
@router.get("/workload", response_model=ResponseModel[dict])
async def get_team_workload(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.is_active == True).all()
    
    workload_data = []
    for user in users:
        # 计算用户的工作负载（这里使用模拟数据）
        planned_hours = 160  # 假设每月计划工时
        user_id_val = int(user.id) if user.id else 0
        actual_hours = min(planned_hours, int(planned_hours * (0.7 + (user_id_val % 30) / 100)))
        utilization_value = round((actual_hours / planned_hours) * 100, 1)
        
        status = "high" if utilization_value >= 90 else "medium" if utilization_value >= 70 else "low"
        
        workload_data.append({
            "id": user.id,
            "name": user.username,
            "email": user.email,
            "planned_hours": planned_hours,
            "actual_hours": actual_hours,
            "utilization": utilization_value,
            "status": status
        })
    
    # 按利用率分组
    high_count = sum(1 for w in workload_data if w["status"] == "high")
    medium_count = sum(1 for w in workload_data if w["status"] == "medium")
    low_count = sum(1 for w in workload_data if w["status"] == "low")
    distribution = {"high": high_count, "medium": medium_count, "low": low_count}
    
    return ResponseModel[dict](
        data={
            "items": workload_data,
            "total": len(workload_data),
            "distribution": distribution
        },
        message="获取团队工作负载成功"
    )


# 获取资源利用率（前端调用）
@router.get("/utilization", response_model=ResponseModel[dict])
async def get_resource_utilization(
    project_id: Optional[int] = Query(None, description="项目ID"),
    db: Session = Depends(get_db)
):
    users = db.query(User).filter(User.is_active == True).all()
    
    total_users = len(users)
    if total_users == 0:
        return ResponseModel[dict](
            data={
                "total_users": 0,
                "completed_tasks": 0,
                "in_progress_tasks": 0,
                "high_load_users": 0,
                "utilization_details": []
            },
            message="获取资源利用率成功"
        )
    
    # 模拟利用率数据
    completed_tasks = 0
    in_progress_tasks = 0
    high_load_users = 0
    
    utilization_details = []
    for user in users:
        # 模拟任务数量
        user_id_val = int(user.id) if user.id else 0
        task_count = user_id_val % 10
        completed = int(task_count * 0.6)
        in_progress_val = int(task_count * 0.3)
        
        utilization_value = min(100, 50 + user_id_val % 50)
        
        high_load = 1 if utilization_value >= 90 else 0
        
        completed_tasks += completed
        in_progress_tasks += in_progress_val
        
        utilization_details.append({
            "user_id": user.id,
            "user_name": user.username,
            "email": user.email,
            "task_count": task_count,
            "completed_tasks": completed,
            "in_progress_tasks": in_progress_val,
            "utilization": utilization_value
        })
        
        high_load_users += high_load
    
    return ResponseModel[dict](
        data={
            "total_users": total_users,
            "completed_tasks": completed_tasks,
            "in_progress_tasks": in_progress_tasks,
            "high_load_users": high_load_users,
            "utilization_details": utilization_details
        },
        message="获取资源利用率成功"
    )


@router.get("", response_model=PaginationResponse[dict])
async def get_resources(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    department: Optional[str] = Query(None, description="部门筛选"),
    role: Optional[str] = Query(None, description="角色筛选"),
    min_utilization: Optional[int] = Query(None, ge=0, le=100, description="最低利用率"),
    db: Session = Depends(get_db)
):
    query = db.query(Resource)
    
    if department:
        query = query.filter(Resource.department == department)
    if role:
        query = query.filter(Resource.role == role)
    if min_utilization is not None:
        query = query.filter(Resource.utilization >= min_utilization)
    
    total = query.count()
    resources = query.offset(skip).limit(limit).all()
    
    # Convert SQLAlchemy objects to dictionaries
    resource_list = []
    for r in resources:
        resource_list.append({
            "id": r.id,
            "name": r.name,
            "department": r.department,
            "role": r.role,
            "utilization": r.utilization,
            "workload": r.workload,
            "skills": r.skills,
            "availability": r.availability,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "updated_at": r.updated_at.isoformat() if r.updated_at else None
        })
    
    return PaginationResponse[dict](
        data=resource_list,
        total=total,
        page=skip // limit + 1 if limit > 0 else 1,
        page_size=limit,
        message="获取资源列表成功"
    )


@router.get("/{resource_id}", response_model=ResponseModel[dict])
async def get_resource_detail(
    resource_id: int = Path(..., description="资源ID"),
    db: Session = Depends(get_db)
):
    resource = db.query(Resource).filter(Resource.id == resource_id).first()
    
    if not resource:
        return ResponseModel[dict](
            data=None,
            message="资源未找到"
        )
    
    # Convert SQLAlchemy object to dictionary
    resource_dict = {
        "id": resource.id,
        "name": resource.name,
        "department": resource.department,
        "role": resource.role,
        "utilization": resource.utilization,
        "workload": resource.workload,
        "skills": resource.skills,
        "availability": resource.availability,
        "created_at": resource.created_at.isoformat() if resource.created_at else None,
        "updated_at": resource.updated_at.isoformat() if resource.updated_at else None
    }
    
    return ResponseModel[dict](
        data=resource_dict,
        message="获取资源成功"
    )


@router.get("/utilization/report", response_model=ResponseModel[dict])
async def get_utilization_report(db: Session = Depends(get_db)):
    resources = db.query(Resource).all()
    
    total_workload = sum([r.workload or 0 for r in resources])
    avg_utilization_value = sum([r.utilization or 0 for r in resources]) / len(resources) if resources else 0
    
    departments = {}
    for r in resources:
        dept = r.department or "未分类"
        if dept not in departments:
            departments[dept] = {"count": 0, "total_utilization": 0}
        departments[dept]["count"] += 1
        departments[dept]["total_utilization"] += r.utilization or 0
    
    dept_stats = {}
    for dept, data in departments.items():
        dept_stats[dept] = {
            "count": data["count"],
            "avg_utilization": round(data["total_utilization"] / data["count"], 1)
        }
    
    low_count = sum(1 for r in resources if (r.utilization or 0) < 70)
    medium_count = sum(1 for r in resources if 70 <= (r.utilization or 0) < 90)
    high_count = sum(1 for r in resources if (r.utilization or 0) >= 90)
    distribution = {"low": low_count, "medium": medium_count, "high": high_count}
    
    result = {
        "total_resources": len(resources),
        "avg_utilization": round(avg_utilization_value, 1),
        "total_workload": total_workload,
        "department_stats": dept_stats,
        "distribution": distribution
    }
    
    return ResponseModel[dict](
        data=result,
        message="获取利用率统计成功"
    )


@router.get("/departments", response_model=ResponseModel[list])
async def get_department_list(db: Session = Depends(get_db)):
    resources = db.query(Resource).all()
    
    departments = {}
    for r in resources:
        dept = r.department or "未分类"
        if dept not in departments:
            departments[dept] = {
                "name": dept,
                "count": 0,
                "members": []
            }
        departments[dept]["count"] += 1
        departments[dept]["members"].append({
            "id": r.id,
            "name": r.name,
            "role": r.role
        })
    
    return ResponseModel[list](
        data=list(departments.values()),
        message="获取部门列表成功"
    )
