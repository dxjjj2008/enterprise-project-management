from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.schemas.common import ResponseModel, PaginationResponse
from app.core.database import get_db
from app.models.approval import Approval, ApprovalHistory

router = APIRouter(
    prefix="/api/v1/approvals",
    tags=["审批流程"],
    responses={404: {"description": "审批未找到"}}
)


@router.get("", response_model=PaginationResponse[dict])
async def get_approvals(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    status: Optional[str] = Query(None, description="状态筛选"),
    approval_type: Optional[str] = Query(None, description="类型筛选"),
    applicant: Optional[str] = Query(None, description="申请人"),
    db: Session = Depends(get_db)
):
    query = db.query(Approval)
    
    if status:
        query = query.filter(Approval.status == status)
    if approval_type:
        query = query.filter(Approval.approval_type == approval_type)
    if applicant:
        query = query.filter(Approval.applicant == applicant)
    
    total = query.count()
    approvals = query.offset(skip).limit(limit).all()
    
    return PaginationResponse[dict](
        data=approvals,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        message="获取审批列表成功"
    )


@router.get("/{approval_id}", response_model=ResponseModel[dict])
async def get_approval_detail(
    approval_id: int = Path(..., description="审批ID"),
    db: Session = Depends(get_db)
):
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    
    if not approval:
        raise HTTPException(status_code=404, detail="审批未找到")
    
    history = db.query(ApprovalHistory).filter(
        ApprovalHistory.approval_id == approval_id
    ).all()
    
    result = {
        **approval.__dict__,
        "history": history
    }
    
    return ResponseModel[dict](
        data=result,
        message="获取审批详情成功"
    )


@router.post("", response_model=ResponseModel[dict])
async def create_approval(
    title: str = Query(..., description="审批标题"),
    description: str = Query(..., description="审批描述"),
    approval_type: str = Query(..., description="审批类型"),
    applicant: str = Query(..., description="申请人"),
    approver: str = Query(..., description="审批人"),
    priority: str = Query("medium", description="优先级"),
    db: Session = Depends(get_db)
):
    approval = Approval(
        title=title,
        description=description,
        approval_type=approval_type,
        applicant=applicant,
        approver=approver,
        priority=priority,
        status="pending"
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)
    
    return ResponseModel[dict](
        data=approval,
        message="审批创建成功"
    )


@router.post("/{approval_id}/approve", response_model=ResponseModel[dict])
async def approve_approval(
    approval_id: int = Path(..., description="审批ID"),
    comment: Optional[str] = Query(None, description="审批意见"),
    db: Session = Depends(get_db)
):
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    
    if not approval:
        raise HTTPException(status_code=404, detail="审批未找到")
    
    if approval.status != "pending":
        return ResponseModel[dict](
            data=None,
            message="该审批已处理"
        )
    
    approval.status = "approved"
    
    history = ApprovalHistory(
        approval_id=approval_id,
        action="approve",
        user=approval.approver,
        comment=comment or "审批通过"
    )
    db.add(history)
    db.commit()
    db.refresh(approval)
    
    return ResponseModel[dict](
        data=approval,
        message="审批通过"
    )


@router.post("/{approval_id}/reject", response_model=ResponseModel[dict])
async def reject_approval(
    approval_id: int = Path(..., description="审批ID"),
    reason: str = Query(..., description="驳回原因"),
    db: Session = Depends(get_db)
):
    approval = db.query(Approval).filter(Approval.id == approval_id).first()
    
    if not approval:
        raise HTTPException(status_code=404, detail="审批未找到")
    
    if approval.status != "pending":
        return ResponseModel[dict](
            data=None,
            message="该审批已处理"
        )
    
    approval.status = "rejected"
    
    history = ApprovalHistory(
        approval_id=approval_id,
        action="reject",
        user=approval.approver,
        comment=reason
    )
    db.add(history)
    db.commit()
    db.refresh(approval)
    
    return ResponseModel[dict](
        data=approval,
        message="审批已驳回"
    )


@router.get("/statistics", response_model=ResponseModel[dict])
async def get_approval_statistics(db: Session = Depends(get_db)):
    approvals = db.query(Approval).all()
    
    stats = {
        "total": len(approvals),
        "by_status": {
            "pending": len([a for a in approvals if a.status == "pending"]),
            "approved": len([a for a in approvals if a.status == "approved"]),
            "rejected": len([a for a in approvals if a.status == "rejected"])
        }
    }
    
    return ResponseModel[dict](
        data=stats,
        message="获取统计成功"
    )
