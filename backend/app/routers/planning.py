from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.schemas.common import ResponseModel, PaginationResponse
from app.core.database import get_db
from app.models.plan import Plan, Milestone

router = APIRouter(
    prefix="/api/v1/planning",
    tags=["计划管理"],
    responses={404: {"description": "计划未找到"}}
)


@router.get("", response_model=PaginationResponse[dict])
async def get_plans(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    status: Optional[str] = Query(None, description="状态筛选"),
    owner: Optional[str] = Query(None, description="负责人"),
    db: Session = Depends(get_db)
):
    query = db.query(Plan)
    
    if status:
        query = query.filter(Plan.status == status)
    if owner:
        query = query.filter(Plan.owner == owner)
    
    total = query.count()
    plans = query.offset(skip).limit(limit).all()
    
    return PaginationResponse[dict](
        data=plans,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        message="获取计划列表成功"
    )


@router.get("/{plan_id}", response_model=ResponseModel[dict])
async def get_plan_detail(
    plan_id: int = Path(..., description="计划ID"),
    db: Session = Depends(get_db)
):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="计划未找到")
    
    milestones = db.query(Milestone).filter(Milestone.plan_id == plan_id).all()
    
    result = {
        **plan.__dict__,
        "milestones": milestones
    }
    
    return ResponseModel[dict](
        data=result,
        message="获取计划详情成功"
    )


@router.post("", response_model=ResponseModel[dict])
async def create_plan(
    title: str = Query(..., description="计划标题"),
    description: Optional[str] = Query(None, description="计划描述"),
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    owner: Optional[str] = Query(None, description="负责人"),
    db: Session = Depends(get_db)
):
    plan = Plan(
        title=title,
        description=description,
        start_date=start_date,
        end_date=end_date,
        owner=owner,
        status="draft"
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    
    return ResponseModel[dict](
        data=plan,
        message="计划创建成功"
    )


@router.put("/{plan_id}", response_model=ResponseModel[dict])
async def update_plan(
    plan_id: int = Path(..., description="计划ID"),
    title: Optional[str] = Query(None, description="标题"),
    description: Optional[str] = Query(None, description="描述"),
    status: Optional[str] = Query(None, description="状态"),
    progress: Optional[int] = Query(None, ge=0, le=100, description="进度"),
    owner: Optional[str] = Query(None, description="负责人"),
    db: Session = Depends(get_db)
):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="计划未找到")
    
    if title:
        plan.title = title
    if description:
        plan.description = description
    if status:
        plan.status = status
    if progress is not None:
        plan.progress = progress
    if owner:
        plan.owner = owner
    
    db.commit()
    db.refresh(plan)
    
    return ResponseModel[dict](
        data=plan,
        message="计划更新成功"
    )


@router.post("/{plan_id}/milestones", response_model=ResponseModel[dict])
async def add_milestone(
    plan_id: int = Path(..., description="计划ID"),
    title: str = Query(..., description="里程碑标题"),
    date: str = Query(..., description="里程碑日期"),
    description: Optional[str] = Query(None, description="描述"),
    db: Session = Depends(get_db)
):
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="计划未找到")
    
    milestone = Milestone(
        plan_id=plan_id,
        title=title,
        date=date,
        description=description,
        status="pending"
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    
    return ResponseModel[dict](
        data=milestone,
        message="里程碑添加成功"
    )


@router.put("/{plan_id}/milestones/{milestone_id}", response_model=ResponseModel[dict])
async def update_milestone(
    plan_id: int = Path(..., description="计划ID"),
    milestone_id: int = Path(..., description="里程碑ID"),
    status: Optional[str] = Query(None, description="状态"),
    db: Session = Depends(get_db)
):
    milestone = db.query(Milestone).filter(
        Milestone.id == milestone_id,
        Milestone.plan_id == plan_id
    ).first()
    
    if not milestone:
        raise HTTPException(status_code=404, detail="里程碑未找到")
    
    if status:
        milestone.status = status
    
    db.commit()
    db.refresh(milestone)
    
    return ResponseModel[dict](
        data=milestone,
        message="里程碑更新成功"
    )
