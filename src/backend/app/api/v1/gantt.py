# 企业项目管理系统 - 甘特图 API
"""
甘特图相关 API 端点
包括甘特图任务列表、配置、导出、统计等
"""

from typing import Optional, List
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.orm import Session
from sqlalchemy import func
from io import BytesIO
from fpdf import FPDF

from app.models import User, Project, Task, TaskStatus, TaskPriority, Milestone
from app.models.database import get_db
from app.core.security import get_current_user

router = APIRouter()


@router.get("/projects/{project_id}/gantt")
async def get_gantt_tasks(
    project_id: int,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assignee_id: Optional[int] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取甘特图任务列表"""
    # 验证项目存在
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 构建查询
    query = db.query(Task).filter(
        Task.project_id == project_id,
        Task.is_deleted == False
    )

    if status:
        query = query.filter(Task.status == status)
    if priority:
        query = query.filter(Task.priority == priority)
    if assignee_id:
        query = query.filter(Task.assignee_id == assignee_id)
    if keyword:
        query = query.filter(Task.title.contains(keyword))

    tasks = query.order_by(Task.start_date).all()

    # 转换为甘特图格式
    result = []
    for task in tasks:
        result.append({
            "id": task.id,
            "project_id": task.project_id,
            "parent_id": task.parent_id,
            "title": task.title,
            "description": task.description,
            "status": task.status,
            "priority": task.priority,
            "assignee_id": task.assignee_id,
            "assignee_name": task.assignee.full_name if task.assignee else None,
            "start_date": task.start_date.isoformat() if task.start_date else None,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "progress": task.progress,
            "is_milestone": task.task_type == "milestone",
            "is_group": task.is_group,
            "dependencies": task.dependencies or [],
            "estimated_hours": task.estimated_hours,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "updated_at": task.updated_at.isoformat() if task.updated_at else None
        })

    return {"items": result}


@router.get("/projects/{project_id}/gantt/config")
async def get_gantt_config(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取甘特图配置"""
    return {
        "view_mode": "week",
        "day_width": 40,
        "row_height": 48,
        "show_weekends": True,
        "show_today": True,
        "show_progress": True,
        "show_dependencies": True
    }


@router.put("/projects/{project_id}/gantt/config")
async def update_gantt_config(
    project_id: int,
    config: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新甘特图配置"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    return {
        "view_mode": config.get("view_mode", "week"),
        "day_width": config.get("day_width", 40),
        "row_height": config.get("row_height", 48),
        "show_weekends": config.get("show_weekends", True),
        "show_today": config.get("show_today", True),
        "show_progress": config.get("show_progress", True),
        "show_dependencies": config.get("show_dependencies", True)
    }


@router.put("/projects/{project_id}/tasks/{task_id}/dates")
async def update_task_dates(
    project_id: int,
    task_id: int,
    start_date: Optional[str] = None,
    due_date: Optional[str] = None,
    duration: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新任务日期（拖拽调整）"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if start_date:
        task.start_date = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
    if due_date:
        task.due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
    if duration:
        task.estimated_hours = duration * 8  # 假设每天8小时

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)

    return {"success": True, "task": {
        "id": task.id,
        "start_date": task.start_date.isoformat() if task.start_date else None,
        "due_date": task.due_date.isoformat() if task.due_date else None
    }}


@router.put("/projects/{project_id}/tasks/{task_id}/progress")
async def update_task_progress(
    project_id: int,
    task_id: int,
    progress: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新任务进度"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if progress < 0 or progress > 100:
        raise HTTPException(status_code=400, detail="进度必须在0-100之间")

    task.progress = progress
    if progress == 100:
        task.status = TaskStatus.DONE
        task.completed_at = datetime.utcnow()
    elif progress > 0:
        task.status = TaskStatus.IN_PROGRESS

    task.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(task)

    return {"success": True, "progress": task.progress}


@router.post("/projects/{project_id}/tasks/{task_id}/dependencies")
async def add_task_dependency(
    project_id: int,
    task_id: int,
    dependent_id: int,
    dep_type: str = "fs",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加任务依赖"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    dependent = db.query(Task).filter(Task.id == dependent_id).first()
    if not dependent:
        raise HTTPException(status_code=404, detail="依赖任务不存在")

    # 更新依赖列表
    dependencies = task.dependencies or []
    if dependent_id not in dependencies:
        dependencies.append(dependent_id)
        task.dependencies = dependencies

    task.updated_at = datetime.utcnow()
    db.commit()

    return {"success": True, "dependencies": task.dependencies}


@router.delete("/projects/{project_id}/tasks/{task_id}/dependencies/{dependent_id}")
async def remove_task_dependency(
    project_id: int,
    task_id: int,
    dependent_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除任务依赖"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.project_id == project_id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    dependencies = task.dependencies or []
    if dependent_id in dependencies:
        dependencies.remove(dependent_id)
        task.dependencies = dependencies

    task.updated_at = datetime.utcnow()
    db.commit()

    return {"success": True, "dependencies": task.dependencies}


@router.get("/projects/{project_id}/gantt/stats")
async def get_gantt_stats(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取甘特图统计信息"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 任务统计
    total_tasks = db.query(func.count(Task.id)).filter(
        Task.project_id == project_id,
        Task.is_deleted == False,
        Task.is_group == False
    ).scalar()

    completed_tasks = db.query(func.count(Task.id)).filter(
        Task.project_id == project_id,
        Task.is_deleted == False,
        Task.is_group == False,
        Task.status == TaskStatus.DONE
    ).scalar()

    in_progress_tasks = db.query(func.count(Task.id)).filter(
        Task.project_id == project_id,
        Task.is_deleted == False,
        Task.is_group == False,
        Task.status == TaskStatus.IN_PROGRESS
    ).scalar()

    today = datetime.utcnow().date()
    overdue_tasks = db.query(func.count(Task.id)).filter(
        Task.project_id == project_id,
        Task.is_deleted == False,
        Task.is_group == False,
        Task.due_date < datetime.combine(today, datetime.min.time()),
        Task.status != TaskStatus.DONE
    ).scalar()

    # 里程碑统计
    milestones = db.query(func.count(Milestone.id)).filter(
        Milestone.project_id == project_id
    ).scalar()

    completed_milestones = db.query(func.count(Milestone.id)).filter(
        Milestone.project_id == project_id,
        Milestone.status == "completed"
    ).scalar()

    # 计算整体进度
    overall_progress = 0
    if total_tasks > 0:
        avg_progress = db.query(func.avg(Task.progress)).filter(
            Task.project_id == project_id,
            Task.is_deleted == False,
            Task.is_group == False
        ).scalar()
        overall_progress = int(avg_progress) if avg_progress else 0

    return {
        "total_tasks": total_tasks or 0,
        "completed_tasks": completed_tasks or 0,
        "in_progress_tasks": in_progress_tasks or 0,
        "overdue_tasks": overdue_tasks or 0,
        "overall_progress": overall_progress,
        "milestones_completed": completed_milestones or 0,
        "milestones_total": milestones or 0,
        "critical_path": []
    }


@router.get("/projects/{project_id}/milestones")
async def get_milestones(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取里程碑列表"""
    milestones = db.query(Milestone).filter(
        Milestone.project_id == project_id
    ).order_by(Milestone.due_date).all()

    return {
        "items": [
            {
                "id": m.id,
                "project_id": m.project_id,
                "name": m.name,
                "due_date": m.due_date.isoformat() if m.due_date else None,
                "status": m.status,
                "description": m.description
            }
            for m in milestones
        ]
    }


@router.get("/projects/{project_id}/gantt/export")
async def export_gantt(
    project_id: int,
    format: str = Query("xlsx", regex="^(png|pdf|xlsx|csv)$"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出甘特图"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 获取任务数据
    tasks = db.query(Task).filter(
        Task.project_id == project_id,
        Task.is_deleted == False
    ).order_by(Task.start_date).all()

    # 根据格式返回不同响应
    if format == "xlsx":
        # 返回JSON数据，前端可以转换为Excel
        data = [{
            "id": t.id,
            "标题": t.title,
            "状态": t.status,
            "优先级": t.priority,
            "开始日期": t.start_date.isoformat() if t.start_date else None,
            "截止日期": t.due_date.isoformat() if t.due_date else None,
            "进度": f"{t.progress}%",
            "负责人": t.assignee.full_name if t.assignee else None
        } for t in tasks]

        return Response(
            content=str(data),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=gantt_{project_id}.json"}
        )

    elif format == "csv":
        csv_content = "ID,标题,状态,优先级,开始日期,截止日期,进度,负责人\n"
        for t in tasks:
            csv_content += f"{t.id},{t.title},{t.status},{t.priority},"
            csv_content += f"{t.start_date.isoformat() if t.start_date else ''},"
            csv_content += f"{t.due_date.isoformat() if t.due_date else ''},"
            csv_content += f"{t.progress}%,"
            csv_content += f"{t.assignee.full_name if t.assignee else ''}\n"

        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=gantt_{project_id}.csv"}
        )

    else:
        # PNG/PDF 需要前端生成
        return {"message": f"Export format {format} requires frontend generation"}


class GanttPDF(FPDF):
    def header(self):
        self.set_font('helvetica', 'B', 16)
        self.cell(0, 10, '甘特图导出报告', border=False, align='C')
        self.ln(15)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'第 {self.page_no()} 页', align='C')


@router.get("/projects/{project_id}/gantt/export/pdf")
async def export_gantt_pdf(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """导出甘特图为PDF格式"""
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="项目不存在")

    # 获取任务数据
    tasks = db.query(Task).filter(
        Task.project_id == project_id,
        Task.is_deleted == False
    ).order_by(Task.start_date).all()

    milestones = db.query(Milestone).filter(
        Milestone.project_id == project_id
    ).order_by(Milestone.due_date).all()

    # 创建PDF
    pdf = GanttPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # 项目信息
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 8, f"项目名称: {project.name}", border=False)
    pdf.ln(6)
    pdf.cell(0, 8, f"导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}", border=False)
    pdf.ln(12)

    # 任务统计
    total_tasks = len([t for t in tasks if not t.is_group])
    completed_tasks = len([t for t in tasks if not t.is_group and t.status == TaskStatus.DONE])
    overall_progress = int(sum(t.progress or 0 for t in tasks if not t.is_group) / total_tasks * 100) if total_tasks > 0 else 0

    pdf.set_font('helvetica', '', 10)
    pdf.cell(0, 6, f"任务总数: {total_tasks}  |  已完成: {completed_tasks}  |  整体进度: {overall_progress}%", border=False)
    pdf.ln(10)

    # 任务表格
    pdf.set_font('helvetica', 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(15, 8, 'ID', fill=True)
    pdf.cell(60, 8, '任务名称', fill=True)
    pdf.cell(25, 8, '开始日期', fill=True)
    pdf.cell(25, 8, '截止日期', fill=True)
    pdf.cell(15, 8, '进度', fill=True)
    pdf.cell(20, 8, '优先级', fill=True)
    pdf.cell(25, 8, '状态', fill=True)
    pdf.cell(50, 8, '负责人', fill=True)
    pdf.ln()

    pdf.set_font('helvetica', '', 8)
    for task in tasks:
        if task.is_group:
            pdf.set_font('helvetica', 'B', 8)
        else:
            pdf.set_font('helvetica', '', 8)

        pdf.cell(15, 7, str(task.id))
        pdf.cell(60, 7, task.title[:25] if task.title else '', )
        pdf.cell(25, 7, task.start_date.strftime('%Y-%m-%d') if task.start_date else '')
        pdf.cell(25, 7, task.due_date.strftime('%Y-%m-%d') if task.due_date else '')
        pdf.cell(15, 7, f"{task.progress or 0}%")

        # 优先级颜色
        priority_map = {'high': '高', 'medium': '中', 'low': '低'}
        pdf.cell(20, 7, priority_map.get(task.priority, task.priority or ''))

        # 状态颜色
        status_map = {
            TaskStatus.TODO: '待办',
            TaskStatus.IN_PROGRESS: '进行中',
            TaskStatus.DONE: '已完成',
            TaskStatus.BLOCKED: '阻塞'
        }
        pdf.cell(25, 7, status_map.get(task.status, task.status or ''))

        assignee_name = task.assignee.full_name if task.assignee else '-'
        pdf.cell(50, 7, assignee_name[:20])
        pdf.ln()

    # 里程碑列表
    if milestones:
        pdf.ln(10)
        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(0, 8, '里程碑', )
        pdf.ln(8)

        pdf.set_font('helvetica', 'B', 9)
        pdf.cell(15, 8, 'ID', fill=True)
        pdf.cell(80, 8, '里程碑名称', fill=True)
        pdf.cell(30, 8, '计划日期', fill=True)
        pdf.cell(25, 8, '状态', fill=True)
        pdf.ln()

        pdf.set_font('helvetica', '', 8)
        for m in milestones:
            pdf.cell(15, 7, str(m.id))
            pdf.cell(80, 7, m.name[:35] if m.name else '')
            pdf.cell(30, 7, m.due_date.strftime('%Y-%m-%d') if m.due_date else '')
            status_map = {'pending': '待完成', 'completed': '已完成', 'delayed': '延迟'}
            pdf.cell(25, 7, status_map.get(m.status, m.status or ''))
            pdf.ln()

    # 生成PDF
    pdf_buffer = BytesIO()
    pdf_output = pdf.output(dest='S').encode('latin1')
    pdf_buffer.write(pdf_output)
    pdf_buffer.seek(0)

    return Response(
        content=pdf_buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=gantt_{project_id}_{datetime.now().strftime('%Y%m%d')}.pdf"}
    )
