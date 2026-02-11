# 企业项目管理系统 - 风险管理API
"""
风险管理API
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import User, Project, Risk, RiskResponse, Task, RiskLevel, RiskStatus
from app.models.database import get_db
from app.core.security import get_current_user

router = APIRouter()


# ============ Pydantic Models ============
class RiskCreate(BaseModel):
    """创建风险请求"""
    title: str
    project_id: int
    description: Optional[str] = None
    level: Optional[RiskLevel] = RiskLevel.MEDIUM
    probability: Optional[int] = 0
    impact: Optional[int] = 0
    category: Optional[str] = None
    source: Optional[str] = None
    mitigation: Optional[str] = None
    contingency_plan: Optional[str] = None
    owner_id: Optional[int] = None
    task_id: Optional[int] = None
    due_date: Optional[str] = None


class RiskUpdate(BaseModel):
    """更新风险请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    level: Optional[RiskLevel] = None
    status: Optional[RiskStatus] = None
    probability: Optional[int] = None
    impact: Optional[int] = None
    category: Optional[str] = None
    source: Optional[str] = None
    mitigation: Optional[str] = None
    contingency_plan: Optional[str] = None
    owner_id: Optional[int] = None
    task_id: Optional[int] = None
    due_date: Optional[str] = None
    closed_date: Optional[str] = None


class RiskResponseCreate(BaseModel):
    """创建风险应对记录请求"""
    action: str
    result: Optional[str] = None


# ============ Helper Functions ============
def calculate_risk_score(probability: int, impact: int) -> int:
    """计算风险评分"""
    return (probability * impact) // 100


# ============ API Endpoints ============

@router.get("/projects/{project_id}/risks")
async def get_risks(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    level: Optional[RiskLevel] = None,
    status: Optional[RiskStatus] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目风险列表"""
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    query = db.query(Risk).filter(Risk.project_id == project_id)

    if level:
        query = query.filter(Risk.level == level)
    if status:
        query = query.filter(Risk.status == status)
    if keyword:
        query = query.filter(Risk.title.contains(keyword))

    total = query.count()
    risks = query.offset(skip).limit(limit).order_by(Risk.created_at.desc()).all()

    result = []
    for risk in risks:
        risk_data = {
            **risk.__dict__,
            "owner_name": risk.owner.full_name if risk.owner else "",
            "task_title": risk.task.title if risk.task else ""
        }
        result.append(risk_data)

    return {
        "items": result,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/projects/{project_id}/risks/{risk_id}")
async def get_risk_detail(
    project_id: int,
    risk_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取风险详情"""
    risk = db.query(Risk).filter(
        Risk.id == risk_id,
        Risk.project_id == project_id
    ).first()

    if not risk:
        raise HTTPException(status_code=404, detail="风险不存在")

    # 获取应对记录
    responses = db.query(RiskResponse).filter(
        RiskResponse.risk_id == risk_id
    ).order_by(RiskResponse.created_at.desc()).all()

    return {
        **risk.__dict__,
        "owner_name": risk.owner.full_name if risk.owner else "",
        "task_title": risk.task.title if risk.task else "",
        "responses": [r.__dict__ for r in responses]
    }


@router.post("/projects/{project_id}/risks")
async def create_risk(
    project_id: int,
    risk_data: RiskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建风险"""
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 计算风险评分
    score = calculate_risk_score(
        risk_data.probability or 0,
        risk_data.impact or 0
    )

    risk = Risk(
        title=risk_data.title,
        project_id=project_id,
        description=risk_data.description,
        level=risk_data.level or RiskLevel.MEDIUM,
        probability=risk_data.probability or 0,
        impact=risk_data.impact or 0,
        score=score,
        category=risk_data.category,
        source=risk_data.source,
        mitigation=risk_data.mitigation,
        contingency_plan=risk_data.contingency_plan,
        owner_id=risk_data.owner_id,
        task_id=risk_data.task_id,
        due_date=risk_data.due_date,
        status=RiskStatus.IDENTIFIED
    )
    db.add(risk)
    db.commit()
    db.refresh(risk)

    return {
        **risk.__dict__,
        "owner_name": risk.owner.full_name if risk.owner else "",
        "task_title": risk.task.title if risk.task else ""
    }


@router.put("/projects/{project_id}/risks/{risk_id}")
async def update_risk(
    project_id: int,
    risk_id: int,
    risk_data: RiskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新风险"""
    risk = db.query(Risk).filter(
        Risk.id == risk_id,
        Risk.project_id == project_id
    ).first()

    if not risk:
        raise HTTPException(status_code=404, detail="风险不存在")

    # 更新字段
    if risk_data.title:
        risk.title = risk_data.title
    if risk_data.description is not None:
        risk.description = risk_data.description
    if risk_data.level:
        risk.level = risk_data.level
    if risk_data.status:
        risk.status = risk_data.status
    if risk_data.probability is not None:
        risk.probability = risk_data.probability
        risk.score = calculate_risk_score(risk.probability, risk.impact or 0)
    if risk_data.impact is not None:
        risk.impact = risk_data.impact
        risk.score = calculate_risk_score(risk.probability or 0, risk.impact)
    if risk_data.category is not None:
        risk.category = risk_data.category
    if risk_data.source is not None:
        risk.source = risk_data.source
    if risk_data.mitigation is not None:
        risk.mitigation = risk_data.mitigation
    if risk_data.contingency_plan is not None:
        risk.contingency_plan = risk_data.contingency_plan
    if risk_data.owner_id is not None:
        risk.owner_id = risk_data.owner_id
    if risk_data.task_id is not None:
        risk.task_id = risk_data.task_id
    if risk_data.due_date is not None:
        risk.due_date = risk_data.due_date
    if risk_data.closed_date is not None:
        risk.closed_date = risk_data.closed_date

    db.commit()
    db.refresh(risk)

    return {
        **risk.__dict__,
        "owner_name": risk.owner.full_name if risk.owner else "",
        "task_title": risk.task.title if risk.task else ""
    }


@router.delete("/projects/{project_id}/risks/{risk_id}")
async def delete_risk(
    project_id: int,
    risk_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除风险"""
    risk = db.query(Risk).filter(
        Risk.id == risk_id,
        Risk.project_id == project_id
    ).first()

    if not risk:
        raise HTTPException(status_code=404, detail="风险不存在")

    db.delete(risk)
    db.commit()

    return {"message": "风险已删除"}


@router.post("/projects/{project_id}/risks/{risk_id}/responses")
async def add_risk_response(
    project_id: int,
    risk_id: int,
    response_data: RiskResponseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加风险应对记录"""
    risk = db.query(Risk).filter(
        Risk.id == risk_id,
        Risk.project_id == project_id
    ).first()

    if not risk:
        raise HTTPException(status_code=404, detail="风险不存在")

    response = RiskResponse(
        risk_id=risk_id,
        action=response_data.action,
        result=response_data.result,
        performed_by_id=current_user.id
    )
    db.add(response)
    db.commit()
    db.refresh(response)

    return response


@router.get("/risks/stats")
async def get_risk_stats(
    project_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取风险统计"""
    query = db.query(Risk)
    
    if project_id:
        query = query.filter(Risk.project_id == project_id)

    total = query.count()
    by_level = {}
    for level in RiskLevel:
        by_level[level.value] = query.filter(Risk.level == level).count()

    by_status = {}
    for status in RiskStatus:
        by_status[status.value] = query.filter(Risk.status == status).count()

    high_risks = query.filter(Risk.level == RiskLevel.HIGH).count() + query.filter(Risk.level == RiskLevel.CRITICAL).count()

    return {
        "total": total,
        "by_level": by_level,
        "by_status": by_status,
        "high_risks": high_risks
    }
