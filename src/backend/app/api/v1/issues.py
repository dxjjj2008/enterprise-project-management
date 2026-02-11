# 企业项目管理系统 - 问题跟踪API
"""
问题跟踪API
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.models import User, Project, Issue, IssueComment, Task, IssueStatus, IssuePriority
from app.models.database import get_db
from app.core.security import get_current_user

router = APIRouter()


# ============ Pydantic Models ============
class IssueCreate(BaseModel):
    """创建问题请求"""
    title: str
    project_id: int
    description: Optional[str] = None
    priority: Optional[IssuePriority] = IssuePriority.MEDIUM
    assignee_id: Optional[int] = None
    task_id: Optional[int] = None
    due_date: Optional[str] = None


class IssueUpdate(BaseModel):
    """更新问题请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[IssueStatus] = None
    priority: Optional[IssuePriority] = None
    assignee_id: Optional[int] = None
    task_id: Optional[int] = None
    due_date: Optional[str] = None
    resolved_date: Optional[str] = None
    solution: Optional[str] = None


class IssueCommentCreate(BaseModel):
    """创建问题评论请求"""
    content: str


# ============ API Endpoints ============

@router.get("/projects/{project_id}/issues")
async def get_issues(
    project_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status: Optional[IssueStatus] = None,
    priority: Optional[IssuePriority] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取项目问题列表"""
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    query = db.query(Issue).filter(Issue.project_id == project_id)

    if status:
        query = query.filter(Issue.status == status)
    if priority:
        query = query.filter(Issue.priority == priority)
    if keyword:
        query = query.filter(Issue.title.contains(keyword))

    total = query.count()
    issues = query.offset(skip).limit(limit).order_by(Issue.created_at.desc()).all()

    result = []
    for issue in issues:
        issue_data = {
            **issue.__dict__,
            "reporter_name": issue.reporter.full_name if issue.reporter else "",
            "assignee_name": issue.assignee.full_name if issue.assignee else "",
            "task_title": issue.task.title if issue.task else ""
        }
        result.append(issue_data)

    return {
        "items": result,
        "total": total,
        "page": skip // limit + 1,
        "page_size": limit
    }


@router.get("/projects/{project_id}/issues/{issue_id}")
async def get_issue_detail(
    project_id: int,
    issue_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取问题详情"""
    issue = db.query(Issue).filter(
        Issue.id == issue_id,
        Issue.project_id == project_id
    ).first()

    if not issue:
        raise HTTPException(status_code=404, detail="问题不存在")

    # 获取评论
    comments = db.query(IssueComment).filter(
        IssueComment.issue_id == issue_id,
        IssueComment.is_deleted == False
    ).order_by(IssueComment.created_at.asc()).all()

    return {
        **issue.__dict__,
        "reporter_name": issue.reporter.full_name if issue.reporter else "",
        "assignee_name": issue.assignee.full_name if issue.assignee else "",
        "task_title": issue.task.title if issue.task else "",
        "comments": [c.__dict__ for c in comments]
    }


@router.post("/projects/{project_id}/issues")
async def create_issue(
    project_id: int,
    issue_data: IssueCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建问题"""
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    issue = Issue(
        title=issue_data.title,
        project_id=project_id,
        description=issue_data.description,
        priority=issue_data.priority or IssuePriority.MEDIUM,
        assignee_id=issue_data.assignee_id,
        task_id=issue_data.task_id,
        due_date=issue_data.due_date,
        reporter_id=current_user.id,
        status=IssueStatus.OPEN
    )
    db.add(issue)
    db.commit()
    db.refresh(issue)

    return {
        **issue.__dict__,
        "reporter_name": current_user.full_name or current_user.username,
        "assignee_name": issue.assignee.full_name if issue.assignee else "",
        "task_title": issue.task.title if issue.task else ""
    }


@router.put("/projects/{project_id}/issues/{issue_id}")
async def update_issue(
    project_id: int,
    issue_id: int,
    issue_data: IssueUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新问题"""
    issue = db.query(Issue).filter(
        Issue.id == issue_id,
        Issue.project_id == project_id
    ).first()

    if not issue:
        raise HTTPException(status_code=404, detail="问题不存在")

    # 更新字段
    if issue_data.title:
        issue.title = issue_data.title
    if issue_data.description is not None:
        issue.description = issue_data.description
    if issue_data.status:
        issue.status = issue_data.status
    if issue_data.priority:
        issue.priority = issue_data.priority
    if issue_data.assignee_id is not None:
        issue.assignee_id = issue_data.assignee_id
    if issue_data.task_id is not None:
        issue.task_id = issue_data.task_id
    if issue_data.due_date is not None:
        issue.due_date = issue_data.due_date
    if issue_data.resolved_date is not None:
        issue.resolved_date = issue_data.resolved_date
    if issue_data.solution is not None:
        issue.solution = issue_data.solution

    db.commit()
    db.refresh(issue)

    return {
        **issue.__dict__,
        "reporter_name": issue.reporter.full_name if issue.reporter else "",
        "assignee_name": issue.assignee.full_name if issue.assignee else "",
        "task_title": issue.task.title if issue.task else ""
    }


@router.delete("/projects/{project_id}/issues/{issue_id}")
async def delete_issue(
    project_id: int,
    issue_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除问题"""
    issue = db.query(Issue).filter(
        Issue.id == issue_id,
        Issue.project_id == project_id
    ).first()

    if not issue:
        raise HTTPException(status_code=404, detail="问题不存在")

    db.delete(issue)
    db.commit()

    return {"message": "问题已删除"}


@router.post("/projects/{project_id}/issues/{issue_id}/comments")
async def add_issue_comment(
    project_id: int,
    issue_id: int,
    comment_data: IssueCommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加问题评论"""
    issue = db.query(Issue).filter(
        Issue.id == issue_id,
        Issue.project_id == project_id
    ).first()

    if not issue:
        raise HTTPException(status_code=404, detail="问题不存在")

    comment = IssueComment(
        issue_id=issue_id,
        author_id=current_user.id,
        content=comment_data.content
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {
        **comment.__dict__,
        "author_name": current_user.full_name or current_user.username
    }


@router.get("/issues/stats")
async def get_issue_stats(
    project_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取问题统计"""
    query = db.query(Issue)
    
    if project_id:
        query = query.filter(Issue.project_id == project_id)

    total = query.count()
    by_status = {}
    for status in IssueStatus:
        by_status[status.value] = query.filter(Issue.status == status).count()

    by_priority = {}
    for priority in IssuePriority:
        by_priority[priority.value] = query.filter(Issue.priority == priority).count()

    open_issues = query.filter(Issue.status == IssueStatus.OPEN).count()
    overdue = query.filter(
        Issue.due_date < datetime.utcnow(),
        Issue.status != IssueStatus.CLOSED
    ).count()

    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "open": open_issues,
        "overdue": overdue
    }
