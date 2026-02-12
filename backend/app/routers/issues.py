from fastapi import APIRouter, Depends, HTTPException, Query, Path
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.schemas.common import ResponseModel, PaginationResponse
from app.core.database import get_db
from app.models.issue import Issue, IssueComment

router = APIRouter(
    prefix="/api/v1/projects/{project_id}/issues",
    tags=["问题跟踪"],
    responses={404: {"description": "问题未找到"}}
)


@router.get("", response_model=PaginationResponse[dict])
async def get_issues(
    project_id: int = Path(..., description="项目ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1),
    status: Optional[str] = Query(None, description="状态筛选"),
    priority: Optional[str] = Query(None, description="优先级筛选"),
    severity: Optional[str] = Query(None, description="严重程度筛选"),
    assignee: Optional[str] = Query(None, description="负责人筛选"),
    db: Session = Depends(get_db)
):
    query = db.query(Issue).filter(Issue.project_id == project_id)
    
    if status:
        query = query.filter(Issue.status == status)
    if priority:
        query = query.filter(Issue.priority == priority)
    if severity:
        query = query.filter(Issue.severity == severity)
    if assignee:
        query = query.filter(Issue.assignee == assignee)
    
    total = query.count()
    issues = query.offset(skip).limit(limit).all()
    
    return PaginationResponse[dict](
        data=issues,
        total=total,
        page=skip // limit + 1,
        page_size=limit,
        message="获取问题列表成功"
    )


@router.get("/{issue_id}", response_model=ResponseModel[dict])
async def get_issue_detail(
    project_id: int = Path(..., description="项目ID"),
    issue_id: int = Path(..., description="问题ID"),
    db: Session = Depends(get_db)
):
    issue = db.query(Issue).filter(
        Issue.id == issue_id,
        Issue.project_id == project_id
    ).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="问题未找到")
    
    comments = db.query(IssueComment).filter(IssueComment.issue_id == issue_id).all()
    
    result = {
        **issue.__dict__,
        "comments": comments
    }
    
    return ResponseModel[dict](
        data=result,
        message="获取问题详情成功"
    )


@router.post("", response_model=ResponseModel[dict])
async def create_issue(
    project_id: int = Path(..., description="项目ID"),
    title: str = Query(..., description="问题标题"),
    description: str = Query(..., description="问题描述"),
    priority: str = Query("medium", description="优先级"),
    severity: str = Query("minor", description="严重程度"),
    assignee: Optional[str] = Query(None, description="负责人"),
    reporter: str = Query(..., description="报告人"),
    db: Session = Depends(get_db)
):
    issue = Issue(
        project_id=project_id,
        title=title,
        description=description,
        priority=priority,
        severity=severity,
        assignee=assignee,
        reporter=reporter,
        status="open"
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)
    
    return ResponseModel[dict](
        data=issue,
        message="问题创建成功"
    )


@router.put("/{issue_id}", response_model=ResponseModel[dict])
async def update_issue(
    project_id: int = Path(..., description="项目ID"),
    issue_id: int = Path(..., description="问题ID"),
    status: Optional[str] = Query(None, description="状态"),
    priority: Optional[str] = Query(None, description="优先级"),
    assignee: Optional[str] = Query(None, description="负责人"),
    db: Session = Depends(get_db)
):
    issue = db.query(Issue).filter(
        Issue.id == issue_id,
        Issue.project_id == project_id
    ).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="问题未找到")
    
    if status:
        issue.status = status
    if priority:
        issue.priority = priority
    if assignee:
        issue.assignee = assignee
    
    db.commit()
    db.refresh(issue)
    
    return ResponseModel[dict](
        data=issue,
        message="问题更新成功"
    )


@router.post("/{issue_id}/comments", response_model=ResponseModel[dict])
async def add_comment(
    project_id: int = Path(..., description="项目ID"),
    issue_id: int = Path(..., description="问题ID"),
    user: str = Query(..., description="评论人"),
    content: str = Query(..., description="评论内容"),
    db: Session = Depends(get_db)
):
    issue = db.query(Issue).filter(
        Issue.id == issue_id,
        Issue.project_id == project_id
    ).first()
    
    if not issue:
        raise HTTPException(status_code=404, detail="问题未找到")
    
    comment = IssueComment(
        issue_id=issue_id,
        user=user,
        content=content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    return ResponseModel[dict](
        data=comment,
        message="评论添加成功"
    )


@router.get("/statistics", response_model=ResponseModel[dict])
async def get_issue_statistics(
    project_id: int = Path(..., description="项目ID"),
    db: Session = Depends(get_db)
):
    issues = db.query(Issue).filter(Issue.project_id == project_id).all()
    
    stats = {
        "total": len(issues),
        "by_status": {
            "open": len([i for i in issues if i.status == "open"]),
            "in_progress": len([i for i in issues if i.status == "in_progress"]),
            "resolved": len([i for i in issues if i.status == "resolved"]),
            "closed": len([i for i in issues if i.status == "closed"])
        },
        "by_priority": {
            "high": len([i for i in issues if i.priority == "high"]),
            "medium": len([i for i in issues if i.priority == "medium"]),
            "low": len([i for i in issues if i.priority == "low"])
        }
    }
    
    return ResponseModel[dict](
        data=stats,
        message="获取统计成功"
    )
