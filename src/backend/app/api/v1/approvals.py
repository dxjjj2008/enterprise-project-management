# 企业项目管理系统 - 审批管理API
"""
审批流程API
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import User, Project, Approval, ApprovalFlowNode, ApprovalType, ApprovalStatus
from app.models.database import get_db
from app.core.security import get_current_user

router = APIRouter()


# ============ Pydantic Models ============
class ApprovalCreate(BaseModel):
    """创建审批请求"""
    type: str
    title: str
    project_id: Optional[int] = None
    description: Optional[str] = None


class ApprovalAction(BaseModel):
    """审批操作请求"""
    comment: Optional[str] = None


class ApprovalReject(BaseModel):
    """驳回审批请求"""
    comment: str


@router.get("/approvals/types")
async def get_approval_types(current_user: User = Depends(get_current_user)):
    """获取审批类型列表"""
    return [
        {"value": "leave", "label": "请假", "icon": "Calendar", "color": "#1890FF"},
        {"value": "expense", "label": "报销", "icon": "Money", "color": "#52C41A"},
        {"value": "trip", "label": "出差", "icon": "Location", "color": "#722ED1"},
        {"value": "purchase", "label": "采购", "icon": "ShoppingCart", "color": "#FAAD14"},
        {"value": "project_init", "label": "项目立项", "icon": "FolderAdd", "color": "#13C2C2"},
        {"value": "project_change", "label": "项目变更", "icon": "Edit", "color": "#EB2F96"}
    ]


@router.get("/approvals")
async def get_approvals(
    skip: int = 0,
    limit: int = 50,
    type: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取审批列表"""
    query = db.query(Approval)

    if type:
        query = query.filter(Approval.type == ApprovalType(type))
    if status:
        query = query.filter(Approval.status == ApprovalStatus(status))
    if keyword:
        query = query.filter(Approval.title.contains(keyword))

    total = query.count()
    approvals = query.offset(skip).limit(limit).all()

    result = []
    for approval in approvals:
        approval_data = {
            **approval.__dict__,
            "applicant_name": approval.applicant.full_name if approval.applicant else "",
            "project_name": approval.project.name if approval.project else ""
        }
        result.append(approval_data)

    return {
        "items": result,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/approvals/{approval_id}")
async def get_approval_detail(
    approval_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取审批详情"""
    approval = db.query(Approval).filter(Approval.id == approval_id).first()

    if not approval:
        raise HTTPException(status_code=404, detail="审批不存在")

    # 获取审批节点
    flow_nodes = db.query(ApprovalFlowNode).filter(
        ApprovalFlowNode.approval_id == approval_id
    ).order_by(ApprovalFlowNode.sort_order).all()

    return {
        **approval.__dict__,
        "applicant_name": approval.applicant.full_name if approval.applicant else "",
        "project_name": approval.project.name if approval.project else "",
        "flow_nodes": [node.__dict__ for node in flow_nodes]
    }


@router.post("/approvals")
async def create_approval(
    approval_data: ApprovalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建审批"""
    approval = Approval(
        type=ApprovalType(approval_data.type),
        title=approval_data.title,
        description=approval_data.description,
        applicant_id=current_user.id,
        project_id=approval_data.project_id,
        status=ApprovalStatus.PENDING
    )
    db.add(approval)
    db.commit()
    db.refresh(approval)

    return {
        **approval.__dict__,
        "applicant_name": current_user.full_name or current_user.username
    }


@router.post("/approvals/{approval_id}/approve")
async def approve_approval(
    approval_id: int,
    action: Optional[ApprovalAction] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """审批通过"""
    approval = db.query(Approval).filter(Approval.id == approval_id).first()

    if not approval:
        raise HTTPException(status_code=404, detail="审批不存在")

    if approval.status != ApprovalStatus.PENDING:
        raise HTTPException(status_code=400, detail="当前审批状态不允许通过")

    comment = action.comment if action else None

    # 更新当前节点
    current_node = db.query(ApprovalFlowNode).filter(
        ApprovalFlowNode.approval_id == approval_id,
        ApprovalFlowNode.status == "pending"
    ).order_by(ApprovalFlowNode.sort_order).first()

    if current_node:
        current_node.status = "approved"
        current_node.comment = comment
        current_node.approved_at = datetime.utcnow()

    # 检查是否还有下一个节点
    next_node = db.query(ApprovalFlowNode).filter(
        ApprovalFlowNode.approval_id == approval_id,
        ApprovalFlowNode.status == "pending"
    ).order_by(ApprovalFlowNode.sort_order).first()

    if next_node:
        approval.status = ApprovalStatus.PROCESSING
        approval.current_node = next_node.name
    else:
        approval.status = ApprovalStatus.APPROVED
        approval.current_node = "已完成"

    db.commit()
    db.refresh(approval)

    return {"message": "审批已通过", "status": approval.status}


@router.post("/approvals/{approval_id}/reject")
async def reject_approval(
    approval_id: int,
    reject_data: ApprovalReject,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """审批拒绝"""
    if not reject_data.comment:
        raise HTTPException(status_code=400, detail="请输入拒绝原因")

    approval = db.query(Approval).filter(Approval.id == approval_id).first()

    if not approval:
        raise HTTPException(status_code=404, detail="审批不存在")

    if approval.status not in [ApprovalStatus.PENDING, ApprovalStatus.PROCESSING]:
        raise HTTPException(status_code=400, detail="当前审批状态不允许拒绝")

    # 更新当前节点
    current_node = db.query(ApprovalFlowNode).filter(
        ApprovalFlowNode.approval_id == approval_id,
        ApprovalFlowNode.status == "pending"
    ).order_by(ApprovalFlowNode.sort_order).first()

    if current_node:
        current_node.status = "rejected"
        current_node.comment = reject_data.comment
        current_node.approved_at = datetime.utcnow()

    approval.status = ApprovalStatus.REJECTED
    approval.current_node = "已拒绝"
    db.commit()
    db.refresh(approval)

    return {"message": "已拒绝该审批", "status": approval.status}


@router.post("/approvals/{approval_id}/cancel")
async def cancel_approval(
    approval_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """撤销审批"""
    approval = db.query(Approval).filter(Approval.id == approval_id).first()

    if not approval:
        raise HTTPException(status_code=404, detail="审批不存在")

    if approval.applicant_id != current_user.id:
        raise HTTPException(status_code=403, detail="只能撤销自己提交的审批")

    if approval.status not in [ApprovalStatus.PENDING, ApprovalStatus.PROCESSING]:
        raise HTTPException(status_code=400, detail="当前审批状态不允许撤销")

    approval.status = ApprovalStatus.CANCELLED
    db.commit()
    db.refresh(approval)

    return {"message": "审批已撤销", "status": approval.status}


@router.get("/approvals/stats")
async def get_approval_stats(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取审批统计"""
    query = db.query(Approval)

    pending = query.filter(Approval.status == ApprovalStatus.PENDING).count()
    approved = query.filter(Approval.status == ApprovalStatus.APPROVED).count()
    rejected = query.filter(Approval.status == ApprovalStatus.REJECTED).count()
    processing = query.filter(Approval.status == ApprovalStatus.PROCESSING).count()

    return {
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
        "processing": processing
    }


@router.get("/approvals/my/pending")
async def get_my_pending_approvals(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的待办审批"""
    # 查找当前用户为审批人的待审批
    approvals = db.query(Approval).filter(
        Approval.status.in_([ApprovalStatus.PENDING, ApprovalStatus.PROCESSING])
    ).offset(skip).limit(limit).all()

    result = []
    for approval in approvals:
        approval_data = {
            **approval.__dict__,
            "applicant_name": approval.applicant.full_name if approval.applicant else "",
            "project_name": approval.project.name if approval.project else ""
        }
        result.append(approval_data)

    return {
        "items": result,
        "total": len(result)
    }


@router.get("/approvals/my/processed")
async def get_my_processed_approvals(
    skip: int = 0,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取我的已办审批"""
    # 查找当前用户已处理的审批
    approvals = db.query(Approval).filter(
        Approval.status.in_([ApprovalStatus.APPROVED, ApprovalStatus.REJECTED, ApprovalStatus.CANCELLED])
    ).offset(skip).limit(limit).all()

    result = []
    for approval in approvals:
        approval_data = {
            **approval.__dict__,
            "applicant_name": approval.applicant.full_name if approval.applicant else "",
            "project_name": approval.project.name if approval.project else ""
        }
        result.append(approval_data)

    return {
        "items": result,
        "total": len(result)
    }
