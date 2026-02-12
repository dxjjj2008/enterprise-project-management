from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime

# 导入 Pydantic 模型
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectDetailResponse, TaskCreate
from app.schemas.common import ResponseModel, PaginationResponse
from app.core.database import get_db
from sqlalchemy.orm import Session

# 创建项目路由器
router = APIRouter(
    prefix="/api/v1/projects",
    tags=["项目管理"],
    responses={404: {"description": "未找到"}}
)

# 获取所有项目
@router.get("", response_model=PaginationResponse[ProjectResponse])
async def get_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取项目列表
    
    返回分页的项目简要信息
    """
    from app.models.project import Project
    
    # 查询项目总数
    total = db.query(Project).count()
    
    # 查询项目列表
    projects = db.query(Project).offset(skip).limit(limit).all()
    
    # 转换为响应模型
    project_list = []
    for project in projects:
        project_list.append(ProjectResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            start_date=project.start_date,
            end_date=project.end_date,
            is_active=project.is_active,
            created_at=project.created_at,
            updated_at=project.updated_at
        ))
    
    return PaginationResponse[ProjectResponse](
        data=project_list,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        message="获取项目列表成功"
    )

# 创建新项目
@router.post("", response_model=ResponseModel[ProjectResponse])
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db)
):
    """
    创建新项目
    
    接收项目基本信息并返回创建结果
    """
    from app.models.project import Project
    
    # 创建项目实例
    db_project = Project(
        name=project.name,
        description=project.description,
        status=project.status or "draft",
        start_date=project.start_date,
        end_date=project.end_date,
        is_active=True
    )
    
    # 保存到数据库
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # 返回创建的项目信息
    return ResponseModel[ProjectResponse](
        data=ProjectResponse(
            id=db_project.id,
            name=db_project.name,
            description=db_project.description,
            status=db_project.status,
            start_date=db_project.start_date,
            end_date=db_project.end_date,
            is_active=db_project.is_active,
            created_at=db_project.created_at,
            updated_at=db_project.updated_at
        ),
        message="项目创建成功"
    )
