from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.schemas.common import ResponseModel, PaginationResponse
from app.core.database import get_db
from app.models.risk import Risk

router = APIRouter(
    prefix="/api/v1/projects/{project_id}/risks",
    tags=["风险管理"],
    responses={404: {"description": "风险未找到"}}
)


@router.get("", response_model=PaginationResponse[dict])
async def get_risks(
    project_id: int = Path(..., description="项目ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    level: Optional[str] = Query(None, description="风险等级"),
    status: Optional[str] = Query(None, description="状态"),
    category: Optional[str] = Query(None, description="类别"),
    owner: Optional[str] = Query(None, description="负责人"),
    db: Session = Depends(get_db)
):
    query = db.query(Risk).filter(Risk.project_id == project_id)
    
    if level:
        query = query.filter(Risk.level == level)
    if status:
        query = query.filter(Risk.status == status)
    if category:
        query = query.filter(Risk.category == category)
    if owner:
        query = query.filter(Risk.owner == owner)
    
    total = query.count()
    risks = query.offset(skip).limit(limit).all()
    
    return PaginationResponse[dict](
        data=risks,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        message="获取风险列表成功"
    )


@router.get("/{risk_id}", response_model=ResponseModel[dict])
async def get_risk_detail(
    project_id: int = Path(..., description="项目ID"),
    risk_id: int = Path(..., description="风险ID"),
    db: Session = Depends(get_db)
):
    risk = db.query(Risk).filter(
        Risk.id == risk_id,
        Risk.project_id == project_id
    ).first()
    
    if not risk:
        raise HTTPException(status_code=404, detail="风险未找到")
    
    return ResponseModel[dict](
        data=risk,
        message="获取风险成功"
    )


@router.get("/matrix", response_model=ResponseModel[dict])
async def get_risk_matrix(
    project_id: int = Path(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    risks = db.query(Risk).filter(Risk.project_id == project_id).all()
    
    matrix = {
        "high_high": [r for r in risks if r.level == "high" and r.probability == "high"],
        "high_medium": [r for r in risks if r.level == "high" and r.probability == "medium"],
        "high_low": [r for r in risks if r.level == "high" and r.probability == "low"],
        "medium_high": [r for r in risks if r.level == "medium" and r.probability == "high"],
        "medium_medium": [r for r in risks if r.level == "medium" and r.probability == "medium"],
        "medium_low": [r for r in risks if r.level == "medium" and r.probability == "low"],
        "low_high": [r for r in risks if r.level == "low" and r.probability == "high"],
        "low_medium": [r for r in risks if r.level == "low" and r.probability == "medium"],
        "low_low": [r for r in risks if r.level == "low" and r.probability == "low"]
    }
    
    result = {
        "matrix": matrix,
        "summary": {
            "critical": len(matrix["high_high"]) + len(matrix["high_medium"]),
            "high": len(matrix["medium_high"]),
            "medium": len(matrix["high_low"]) + len(matrix["medium_medium"]) + len(matrix["low_high"]),
            "low": len(matrix["medium_low"]) + len(matrix["low_medium"]) + len(matrix["low_low"])
        },
        "total": len(risks)
    }
    
    return ResponseModel[dict](
        data=result,
        message="获取风险矩阵成功"
    )


@router.post("", response_model=ResponseModel[dict])
async def create_risk(
    project_id: int = Path(..., description="项目ID"),
    title: str = Query(..., description="风险标题"),
    description: str = Query(..., description="风险描述"),
    level: str = Query("medium", description="风险等级"),
    probability: str = Query("medium", description="发生概率"),
    impact: str = Query("medium", description="影响程度"),
    owner: Optional[str] = Query(None, description="负责人"),
    category: str = Query("其他", description="风险类别"),
    mitigation: Optional[str] = Query(None, description="应对措施"),
    contingency: Optional[str] = Query(None, description="应急预案"),
    db: Session = Depends(get_db)
):
    risk = Risk(
        project_id=project_id,
        title=title,
        description=description,
        level=level,
        probability=probability,
        impact=impact,
        owner=owner,
        category=category,
        mitigation=mitigation,
        contingency=contingency,
        status="identified"
    )
    db.add(risk)
    db.commit()
    db.refresh(risk)
    
    return ResponseModel[dict](
        data=risk,
        message="风险创建成功"
    )


@router.put("/{risk_id}", response_model=ResponseModel[dict])
async def update_risk(
    project_id: int = Path(..., description="项目ID"),
    risk_id: int = Path(..., description="风险ID"),
    status: Optional[str] = Query(None, description="状态"),
    mitigation: Optional[str] = Query(None, description="应对措施"),
    contingency: Optional[str] = Query(None, description="应急预案"),
    db: Session = Depends(get_db)
):
    risk = db.query(Risk).filter(
        Risk.id == risk_id,
        Risk.project_id == project_id
    ).first()
    
    if not risk:
        raise HTTPException(status_code=404, detail="风险未找到")
    
    if status:
        risk.status = status
    if mitigation:
        risk.mitigation = mitigation
    if contingency:
        risk.contingency = contingency
    
    db.commit()
    db.refresh(risk)
    
    return ResponseModel[dict](
        data=risk,
        message="风险更新成功"
    )


@router.get("/statistics", response_model=ResponseModel[dict])
async def get_risk_statistics(
    project_id: int = Path(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    risks = db.query(Risk).filter(Risk.project_id == project_id).all()
    
    stats = {
        "total": len(risks),
        "by_level": {
            "high": len([r for r in risks if r.level == "high"]),
            "medium": len([r for r in risks if r.level == "medium"]),
            "low": len([r for r in risks if r.level == "low"])
        },
        "by_status": {
            "identified": len([r for r in risks if r.status == "identified"]),
            "monitoring": len([r for r in risks if r.status == "monitoring"]),
            "mitigated": len([r for r in risks if r.status == "mitigated"]),
            "accepted": len([r for r in risks if r.status == "accepted"])
        }
    }
    
    return ResponseModel[dict](
        data=stats,
        message="获取风险统计成功"
    )
