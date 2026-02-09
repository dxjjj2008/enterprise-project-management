# 项目计划模块 - 详细设计

**版本**: v1.0  
**创建日期**: 2026-02-08  
**关联主设计**: 2026-02-08-project-management-system-design.md

---

## 1. 功能概述

| 功能 | 描述 |
|------|------|
| **版本管理** | 每次计划变更生成新版本，保留完整历史 |
| **基线管理** | 保存关键里程碑的计划快照，支持对比分析 |
| **资源规划** | 人员、设备、外部资源的分配和调度 |
| **工时规划** | 任务的预估工时、计划工时分配 |
| **审批流程** | 计划需要审批后才能生效执行 |

---

## 2. 数据库设计

### 2.1 项目计划主表 (project_plans)

```
id: Integer, PK
project_id: Integer, FK(projects.id)             [所属项目]
name: String(100)                                [计划名称，如"项目总体规划V1"]
description: Text                                [计划描述]
current_version_id: Integer, FK(project_plan_versions.id) [当前生效版本]
status: String(20)                               [draft/pending_approval/approved/rejected/archived]
created_by: Integer, FK(users.id)                [创建人]
created_at: DateTime
updated_at: DateTime
```

**说明**：
- 一个项目可以有多个计划（如"总体计划"、"详细计划"）
- `current_version_id` 指向当前正在使用的版本
- `draft` = 草稿中，`pending_approval` = 待审批

### 2.2 计划版本表 (project_plan_versions)

```
id: Integer, PK
plan_id: Integer, FK(project_plans.id)           [所属计划]
version_number: Integer                           [版本号 1,2,3...]
parent_version_id: Integer, FK(project_plan_versions.id) [父版本（基于谁修改）]
status: String(20)                               [draft/pending_approval/approved]
name: String(100)                                [版本名称，如"V1.0正式版"]
description: Text                                [版本说明]
is_baseline: Boolean                              [是否已设为基线]
baseline_name: String(100), nullable              [基线名称，如"总体设计基线"]
baseline_description: Text, nullable              [基线说明]
created_by: Integer, FK(users.id)                [创建人]
approved_by: Integer, FK(users.id), nullable      [审批人]
approved_at: DateTime, nullable                   [审批时间]
rejected_by: Integer, FK(users.id), nullable      [驳回人]
rejected_at: DateTime, nullable                  [驳回时间]
rejection_reason: Text, nullable                 [驳回原因]
effective_start_date: Date                       [计划开始日期]
effective_end_date: Date                         [计划结束日期]
total_estimated_hours: Float                      [总预估工时]
total_tasks: Integer                              [任务总数]
change_summary: JSON, nullable                   [变更摘要]
created_at: DateTime
updated_at: DateTime
```

**版本关系示例**：
```
project_plan (id=1, name="项目主计划")
├── project_plan_version (id=1, version_number=1, name="V1.0草稿")
├── project_plan_version (id=2, version_number=2, parent_version_id=1, name="V1.1修订")
│   └── project_plan_version (id=3, version_number=3, parent_version_id=2, is_baseline=true, baseline_name="设计阶段基线")
└── project_plan_version (id=4, version_number=4, parent_version_id=1, name="V2.0终稿")
```

### 2.3 计划任务明细表 (project_plan_tasks)

```
id: Integer, PK
version_id: Integer, FK(project_plan_versions.id) [所属版本]
task_id: Integer, FK(tasks.id), nullable          [关联实际任务（执行时）]
wbs_code: String(50)                              [WBS编码，如"1.2.3"]
parent_wbs_code: String(50), nullable            [父级WBS编码]
level: Integer                                   [层级深度 0,1,2...]
name: String(200)                                [任务名称]
description: Text
task_type: String(50)                             [task/milestone/deliverable]
start_date: Date                                  [计划开始]
end_date: Date                                    [计划结束]
duration_days: Integer                            [持续天数]
estimated_hours: Float                            [预估工时]
planned_hours: Float                              [计划工时（分配给资源）]
progress: Integer [0-100]                         [完成百分比]
weight: Float                                     [权重（用于统计）]
priority: String(20)                             [low/medium/high/critical]
status: String(20)                               [planned/in_progress/completed/cancelled]
dependency_json: JSON, nullable                   [依赖关系 JSON]
notes: Text, nullable                             [备注]
created_by: Integer, FK(users.id)
created_at: DateTime
updated_at: DateTime
```

**WBS 示例**：
```
1.0              项目启动
├── 1.1          需求分析
│   ├── 1.1.1    用户调研
│   └── 1.1.2    需求文档
├── 1.2          系统设计
│   ├── 1.2.1    架构设计
│   └── 1.2.2    详细设计
└── 1.3          开发实施
```

### 2.4 资源分配表 (project_resources)

```
id: Integer, PK
version_id: Integer, FK(project_plan_versions.id) [所属计划版本]
resource_type: String(20)                         [human/equipment/material/external]
user_id: Integer, FK(users.id), nullable         [关联用户（human类型）]
name: String(100)                                [资源名称]
department: String(100)                          [所属部门/团队]
role: String(50)                                 [角色]
capacity_hours_per_day: Float                    [日可用工时]
availability_start: Date                          [可用开始日期]
availability_end: Date                            [可用结束日期]
hourly_rate: Float, nullable                      [小时费率]
cost_center: String(50), nullable                [成本中心]
notes: Text, nullable
is_active: Boolean, default=True
created_by: Integer, FK(users.id)
created_at: DateTime
updated_at: DateTime
```

### 2.5 资源任务分配表 (project_resource_allocations)

```
id: Integer, PK
version_id: Integer, FK(project_plan_versions.id) [所属计划版本]
plan_task_id: Integer, FK(project_plan_tasks.id)  [计划任务]
resource_id: Integer, FK(project_resources.id)    [资源ID]
allocation_type: String(20)                      [primary/secondary/support]
allocated_hours: Float                            [分配工时]
start_date: Date                                  [分配开始]
end_date: Date                                    [分配结束]
utilization_rate: Float [0-1]                     [利用率 0.0-1.0]
cost: Float                                      [分配成本]
notes: Text, nullable
created_by: Integer, FK(users.id)
created_at: DateTime
updated_at: DateTime
```

**示例**：
```
版本V1.3 的 "用户调研" 任务 (plan_task_id=5)
├── 资源分配: 张三 (resource_id=1), primary, 16小时
├── 资源分配: 李四 (resource_id=2), secondary, 8小时
└── 总计: 24小时
```

### 2.6 审批流程表 (project_plan_approvals)

```
id: Integer, PK
version_id: Integer, FK(project_plan_versions.id) [待审批的版本]
plan_id: Integer, FK(project_plans.id)             [所属计划]
approval_type: String(50)                        [plan_submission/plan_revision/baseline_creation]
status: String(20)                               [pending/approved/rejected/cancelled]
submitted_by: Integer, FK(users.id)               [提交人]
submitted_at: DateTime                            [提交时间]
current_step: Integer                             [当前审批步骤]
approval_steps: JSON                             [审批步骤配置]
│ └── 示例:
│   [
│     { "step": 1, "role": "project_manager", "approvers": [], "status": "pending" },
│     { "step": 2, "role": "department_head", "approvers": [], "status": "pending" },
│     { "step": 3, "role": "finance", "approvers": [], "status": "pending" }
│   ]
current_approver_id: Integer, FK(users.id), nullable [当前待审批人]
due_date: Date, nullable                         [审批截止日期]
comments: JSON, nullable                         [审批意见
│   [
│     { "step": 1, "user_id": 102, "decision": "approved", "comment": "同意", "timestamp": "..." }
│   ]
decided_at: DateTime, nullable                   [最终决定时间]
created_at: DateTime
updated_at: DateTime
```

**审批流程示例**：
```
提交计划 V1.0:
├── Step 1: 项目经理审批 → 通过
├── Step 2: 部门负责人审批 → 驳回（附意见）
└── 申请人修改后重新提交 → 重新开始审批流程
```

### 2.7 基线表 (project_baselines)

```
id: Integer, PK
project_id: Integer, FK(projects.id)             [所属项目]
version_id: Integer, FK(project_plan_versions.id) [关联的版本]
name: String(100)                                [基线名称]
description: Text                                [基线说明]
snapshot_date: DateTime                          [快照时间]
status: String(20)                               [active/archived/replaced]
replaced_by_baseline_id: Integer, FK(project_baselines.id), nullable [替代基线]
total_tasks: Integer                              [快照时的任务数]
total_estimated_hours: Float                    [快照时的总工时]
total_cost: Float                                 [快照时的总成本]
created_by: Integer, FK(users.id)
created_at: DateTime
updated_at: DateTime
```

**基线与版本的关系**：
```
project_baseline (id=1, name="总体设计基线")
├── version_id: 3 (project_plan_version.id=3)
└── snapshot_date: 2026-02-10 10:30:00

后续可对比：当前执行 vs 基线
```

### 2.8 基线快照明细表 (project_baseline_snapshots)

```
id: Integer, PK
baseline_id: Integer, FK(project_baselines.id)    [所属基线]
wbs_code: String(50)                              [WBS编码]
task_name: String(200)                            [任务名称]
planned_start_date: Date                          [计划开始]
planned_end_date: Date                            [计划结束]
planned_hours: Float                              [计划工时]
planned_cost: Float                              [计划成本]
resource_allocations: JSON, nullable             [资源分配快照]
created_at: DateTime
```

**说明**：保存基线时刻的完整状态，用于后续对比分析。

### 2.9 计划对比分析表 (plan_comparisons)

```
id: Integer, PK
project_id: Integer, FK(projects.id)             [所属项目]
baseline_id: Integer, FK(project_baselines.id)   [基线版本]
comparison_version_id: Integer, FK(project_plan_versions.id) [对比版本]
comparison_type: String(50)                      [baseline_vs_current/version_vs_version]
generated_at: DateTime                           [生成时间]
total_tasks_added: Integer                      [新增任务数]
total_tasks_removed: Integer                   [删除任务数]
total_tasks_modified: Integer                   [变更任务数]
total_hours_change: Float                       [工时变化]
total_cost_change: Float                        [成本变化]
schedule_variance_days: Float                  [进度偏差天数]
analysis_summary: Text                          [分析摘要]
tasks_diff: JSON, nullable                      [任务变更明细
│   {
│     "added": [...],
│     "removed": [...],
│     "modified": [
│       { "wbs_code": "1.1.1", "field": "end_date", "old_value": "2026-03-01", "new_value": "2026-03-05" }
│     ]
│   }
]
created_by: Integer, FK(users.id)
created_at: DateTime
```

---

## 3. API 接口设计

### 3.1 计划管理 (Plans)

```
GET    /api/projects/{id}/plans                  # 获取项目计划列表
POST   /api/projects/{id}/plans                  # 创建计划
GET    /api/projects/{id}/plans/{plan_id}       # 获取计划详情
PUT    /api/projects/{id}/plans/{plan_id}       # 更新计划
DELETE /api/projects/{id}/plans/{plan_id}       # 删除计划
```

### 3.2 计划版本管理 (Plan Versions)

```
GET    /api/plans/{plan_id}/versions             # 获取版本列表
POST   /api/plans/{plan_id}/versions            # 创建新版本
GET    /api/plans/{plan_id}/versions/{ver_id}   # 获取版本详情
PUT    /api/plans/{plan_id}/versions/{ver_id}   # 更新版本
GET    /api/plans/{plan_id}/versions/{ver_id}/tasks  # 获取版本任务列表
PUT    /api/plans/{plan_id}/versions/{ver_id}/tasks  # 批量更新任务
```

### 3.3 WBS 管理

```
GET    /api/plans/{plan_id}/wbs                  # 获取WBS树
POST   /api/plans/{plan_id}/wbs                 # 添加WBS节点
PUT    /api/plans/{plan_id}/wbs/{wbs_code}     # 更新WBS节点
DELETE /api/plans/{plan_id}/wbs/{wbs_code}     # 删除WBS节点
PUT    /api/plans/{plan_id}/wbs/reorder         # 重新排序WBS
```

### 3.4 资源管理 (Resources)

```
GET    /api/projects/{id}/resources              # 获取资源列表
POST   /api/projects/{id}/resources              # 添加资源
GET    /api/projects/{id}/resources/{res_id}    # 获取资源详情
PUT    /api/projects/{id}/resources/{res_id}    # 更新资源
DELETE /api/projects/{id}/resources/{res_id}    # 删除资源
GET    /api/projects/{id}/resources/utilization  # 资源利用率
```

### 3.5 资源分配 (Resource Allocations)

```
GET    /api/plans/{plan_id}/allocations          # 获取分配列表
POST   /api/plans/{plan_id}/allocations         # 批量分配资源
PUT    /api/plans/{plan_id}/allococations/{alloc_id}  # 更新分配
DELETE /api/plans/{plan_id}/allocations/{alloc_id}   # 删除分配
GET    /api/plans/{plan_id}/allocations/gantt   # 获取分配甘特图
```

### 3.6 审批流程 (Approvals)

```
POST   /api/plans/{plan_id}/versions/{ver_id}/submit   # 提交审批
GET    /api/approvals/pending             # 获取待我审批的列表
GET    /api/approvals/{approval_id}       # 获取审批详情
POST   /api/approvals/{approval_id}/approve   # 批准
POST   /api/approvals/{approval_id}/reject    # 驳回
GET    /api/approvals/history             # 审批历史
```

### 3.7 基线管理 (Baselines)

```
GET    /api/projects/{id}/baselines              # 获取基线列表
POST   /api/projects/{id}/baselines             # 创建基线
GET    /api/projects/{id}/baselines/{base_id}   # 获取基线详情
GET    /api/projects/{id}/baselines/{base_id}/tasks  # 基线任务快照
PUT    /api/projects/{id}/baselines/{base_id}   # 更新基线
DELETE /api/projects/{id}/baselines/{base_id}   # 删除基线
```

### 3.8 计划对比 (Plan Comparisons)

```
GET    /api/projects/{id}/comparisons            # 获取对比记录列表
POST   /api/projects/{id}/comparisons           # 生成对比分析
GET    /api/projects/{id}/comparisons/{comp_id} # 获取对比详情
GET    /api/projects/{id}/baselines/{base_id}/vs/current  # 基线 vs 当前
GET    /api/projects/{id}/baselines/{base_id}/vs/version/{ver_id}  # 基线 vs 版本
```

### 3.9 报表与分析 (Reports)

```
GET    /api/plans/{plan_id}/overview             # 计划概览
GET    /api/plans/{plan_id}/timeline             # 时间线视图
GET    /api/plans/{plan_id}/gantt               # 计划甘特图
GET    /api/plans/{plan_id}/resource-load        # 资源负载
GET    /api/plans/{plan_id}/critical-path        # 关键路径
GET    /api/plans/{plan_id}/cost-analysis        # 成本分析
```

---

## 4. 前端页面设计

### 4.1 页面结构

```
/planning                          # 计划管理入口
├── /projects/:id/plans           # 计划列表
│   ├── /:planId                  # 计划详情
│   │   ├── /overview             # 概览
│   │   ├── /wbs                  # WBS分解
│   │   ├── /timeline             # 时间线
│   │   ├── /gantt                # 甘特图
│   │   ├── /resources            # 资源管理
│   │   ├── /allocations          # 资源分配
│   │   ├── /baselines            # 基线管理
│   │   └── /comparisons          # 对比分析
│   └── /:planId/versions         # 版本历史
│       └── /:verId               # 版本详情
└── /approvals                    # 待我审批
    └── /:approvalId              # 审批页面
```

### 4.2 核心组件

| 组件 | 用途 |
|------|------|
| **WBSTree** | WBS 树形结构，支持拖拽、缩进 |
| **GanttChart** | 甘特图，支持拖拽调整日期 |
| **ResourceGrid** | 资源分配网格视图 |
| **ResourceLoadChart** | 资源负载图 |
| **BaselineComparison** | 基线对比视图 |
| **ApprovalFlow** | 审批流程可视化 |
| **CriticalPathHighlight** | 关键路径高亮 |
| **VarianceChart** | 偏差图表 |

### 4.3 主要页面

#### A. 计划列表页
- 项目下所有计划的卡片列表
- 显示状态（草稿/待审批/已批准）、版本数、基线数
- 快捷操作：新建计划、查看历史、提交审批

#### B. WBS 编辑页
- 树形结构展示
- 支持右键菜单（添加子任务、删除、复制）
- 批量编辑（开始结束日期、工时）
- 导入导出（Excel）

#### C. 资源分配页
- 资源列表（人员、设备）
- 资源日历（显示可用时间）
- 拖拽分配到任务
- 负载可视化（避免过载）

#### D. 基线管理页
- 基线列表
- 创建基线（选择版本）
- 基线对比（表格+图表）
- 导出对比报告

#### E. 审批页
- 审批信息展示（计划概要、变更说明）
- 审批历史
- 批准/驳回操作
- 填写意见

---

## 5. 核心业务流程

### 5.1 创建计划流程

```
1. 创建计划主记录
   └── POST /api/projects/{id}/plans

2. 创建第一个版本 (V1.0 草稿)
   └── POST /api/plans/{plan_id}/versions

3. 编辑 WBS 和任务
   └── PUT /api/plans/{plan_id}/versions/{ver_id}/tasks

4. 添加资源
   └── POST /api/projects/{id}/resources

5. 分配资源到任务
   └── POST /api/plans/{plan_id}/allocations

6. 提交审批
   └── POST /api/plans/{plan_id}/versions/{ver_id}/submit

7. 审批通过后生效
   └── 版本 status = approved
       └── 计划 current_version_id 更新为此版本
```

### 5.2 修订计划流程

```
1. 基于当前版本创建新版本
   └── parent_version_id = 当前版本ID
   └── version_number = 当前版本号 + 1

2. 编辑修改
   └── 调整 WBS、日期、工时等

3. 提交审批
   └── 审批流程重新开始

4. 审批通过后
   └── 新版本变为 current_version
```

### 5.3 创建基线流程

```
1. 选择要基线化的版本
   └── 通常是某个重要里程碑的版本

2. 创建基线快照
   └── POST /api/projects/{id}/baselines
       ├── 保存版本的任务列表
       ├── 保存工时、成本数据
       └── 生成快照时间戳

3. 基线对比
   └── 可以对比当前执行 vs 基线
       └── 识别偏差
       └── 生成分析报告
```

### 5.4 审批流程

```
提交 (Submit)
    │
    ▼
Step 1: 项目经理审批
    ├── 批准 → Step 2
    └── 驳回 → 返回申请人

Step 2: 部门负责人审批
    ├── 批准 → Step 3
    └── 驳回 → 返回申请人

Step 3: 财务审批（如果涉及预算）
    ├── 批准 → 完成
    └── 驳回 → 返回申请人

完成 (Approved)
    └── 版本生效
    └── 计划 current_version 更新
```

---

## 6. 关键算法

### 6.1 WBS 自动编码

```python
def generate_wbs_code(parent_code: str, level: int) -> str:
    # 查询同级任务数量
    count = db.query(Task).filter(
        Task.parent_wbs_code == parent_code
    ).count() + 1
    
    if level == 0:
        return str(count)  # "1", "2", "3"
    else:
        return f"{parent_code}.{count}"  # "1.1", "1.2"
```

### 6.2 关键路径计算

```python
def calculate_critical_path(tasks: List[Task]) -> List[Task]:
    # 1. 构建任务依赖图
    graph = build_dependency_graph(tasks)
    
    # 2. 计算最早开始/结束时间 (Forward Pass)
    for task in topological_sort(graph):
        task.early_start = max(pred.early_finish for pred in graph[task])
        task.early_finish = task.early_start + task.duration
    
    # 3. 计算最晚开始/结束时间 (Backward Pass)
    for task in reversed_topological_sort(graph):
        task.late_finish = min(succ.late_start for succ in graph[task]) if graph[task] else task.early_finish
        task.late_start = task.late_finish - task.duration
    
    # 4. 找出浮动时间为 0 的任务
    critical_tasks = [t for t in tasks if (t.late_start - t.early_start) == 0]
    
    return critical_tasks
```

### 6.3 资源负载计算

```python
def calculate_resource_load(resource_id: str, start_date: Date, end_date: Date) -> Dict:
    allocations = get_allocations(resource_id, start_date, end_date)
    
    # 按日期汇总
    daily_load = {}
    for alloc in allocations:
        days = (alloc.end_date - alloc.start_date).days
        daily_hours = alloc.allocated_hours / days
        
        for i in range(days):
            date = alloc.start_date + timedelta(days=i)
            daily_load[date] = daily_load.get(date, 0) + daily_hours
    
    # 计算利用率
    capacity_hours = resource.capacity_hours_per_day
    utilization = {
        date: hours / capacity_hours 
        for date, hours in daily_load.items()
    }
    
    return {
        "daily_load": daily_load,
        "utilization": utilization,
        "overloaded_days": [d for d, u in utilization.items() if u > 1.0]
    }
```

### 6.4 计划偏差分析

```python
def analyze_plan_variance(baseline_id: int, current_version_id: int) -> PlanComparison:
    baseline = get_baseline(baseline_id)
    current = get_version(current_version_id)
    
    # 任务对比
    added = find_added_tasks(baseline.tasks, current.tasks)
    removed = find_removed_tasks(baseline.tasks, current.tasks)
    modified = find_modified_tasks(baseline.tasks, current.tasks)
    
    # 工时变化
    hours_change = current.total_hours - baseline.total_hours
    
    # 进度偏差
    schedule_variance = calculate_days_diff(
        baseline.end_date, 
        current.end_date
    )
    
    # 生成分析摘要
    summary = generate_summary(added, removed, modified, hours_change, schedule_variance)
    
    return PlanComparison(
        added=added,
        removed=removed,
        modified=modified,
        hours_change=hours_change,
        schedule_variance=schedule_variance,
        summary=summary
    )
```

---

## 7. 开发优先级

### 第一阶段 (Week 3): 基础计划管理

| 功能 | 优先级 | 工作量 |
|------|--------|--------|
| 计划 CRUD | P0 | 2天 |
| 版本管理 | P0 | 2天 |
| WBS 管理 | P0 | 3天 |
| 审批流程 | P0 | 2天 |

### 第二阶段 (Week 4): 资源与工时

| 功能 | 优先级 | 工作量 |
|------|--------|--------|
| 资源管理 | P1 | 2天 |
| 资源分配 | P1 | 2天 |
| 资源负载图 | P1 | 1天 |
| 甘特图展示 | P1 | 2天 |

### 第三阶段 (迭代): 高级功能

| 功能 | 优先级 | 工作量 |
|------|--------|--------|
| 基线管理 | P2 | 2天 |
| 基线对比 | P2 | 2天 |
| 关键路径 | P2 | 1天 |
| 成本分析 | P2 | 1天 |

---

## 8. 功能增强设计

### 8.1 里程碑自动触发下游任务

**触发规则**：
```
里程碑完成 → 自动更新下游任务状态
├── FS (Finish-to-Start): 下游任务自动变为 "可开始"
├── SS (Start-to-Start): 下游任务自动更新开始日期
└── 发送通知 → 下游任务负责人
```

**触发时机**：
- 里程碑状态变更为 `completed` 时
- 手动触发（重新计算）

**触发逻辑**：

```python
def trigger_milestone_completion(milestone_id: int):
    milestone = get_milestone(milestone_id)
    successor_tasks = get_successor_tasks(milestone.task_id)
    
    for task in successor_tasks:
        dependency = get_dependency(milestone.task_id, task.id)
        
        if dependency.type == "finish_to_start":
            if task.status == "todo":
                task.status = "in_progress" if task.assignee_id else "todo"
                task.start_date = milestone.completed_date
                send_notification(task.assignee_id, "前置里程碑已完成，任务可开始")
        
        elif dependency.type == "start_to_start":
            if task.start_date < milestone.completed_date:
                task.start_date = milestone.completed_date
                send_notification(task.assignee_id, "前置任务已开始，时间已更新")
        
        save(task)
    
    # 记录触发日志
    log_trigger_event(milestone_id, successor_tasks)
```

**前端交互**：
- 里程碑完成时，弹窗提示"将自动触发 X 个下游任务"
- 确认后执行触发
- 显示触发结果

---

### 8.2 资源超载提醒机制

**超载定义**：
```
利用率 > 100% = 超载
利用率 80%-100% = 高负载（黄色预警）
利用率 < 80% = 正常（绿色）
```

**提醒时机**：

| 场景 | 触发方式 |
|------|----------|
| 分配资源时 | 实时检测，显示警告弹窗 |
| 手动检查 | 点击"检查资源负载"按钮 |
| 定时检测 | 每日凌晨检测，发送邮件提醒 |

**超载检测 API**：

```
GET    /api/plans/{plan_id}/resources/{res_id}/load-check?start_date=XXX&end_date=XXX
```

**响应示例**：
```json
{
  "resource_id": 1,
  "resource_name": "张三",
  "period": "2026-03-01 ~ 2026-03-31",
  "daily_load": {
    "2026-03-05": {
      "allocated_hours": 12,
      "capacity_hours": 8,
      "utilization": 1.5,
      "status": "overloaded",
      "tasks": ["任务A (8h)", "任务B (4h)"]
    }
  },
  "summary": {
    "overloaded_days": 5,
    "overloaded_tasks": 8,
    "avg_utilization": 0.85
  }
}
```

**前端交互 - 资源选择弹窗**：

```vue
<template>
  <ResourceSelectModal
    :task="currentTask"
    :show-overload-warning="true"
    @select="handleSelect"
  />
</template>

<script>
// 选择资源时，如果超载显示警告
const handleSelect = (resource, allocation) => {
  if (allocation.utilization > 1.0) {
    showWarning({
      title: "资源超载提醒",
      message: `${resource.name} 在此期间已分配 ${allocation.allocated_hours}h，日产能 ${allocation.capacity_hours}h`,
      details: allocation.overloadedDays,
      confirmText: "仍然分配",
      cancelText: "重新选择"
    })
  }
}
</script>
```

**定时检测配置**：

```
系统配置表 (system_settings):
├── resource_overload_alert_enabled: boolean (default: true)
├── resource_overload_alert_time: string (default: "08:00")
├── resource_overload_alert_recipients: json (["project_manager", "resource_owner"])
└── resource_overload_alert_email_enabled: boolean (default: true)
```

---

### 8.3 对比报告导出

**支持的导出格式**：

| 格式 | 说明 | 使用场景 |
|------|------|----------|
| PDF | 正式报告，带页眉页脚 | 存档、汇报 |
| Excel | 可编辑数据 | 进一步分析 |
| HTML | 网页格式 | 在线分享 |

**导出 API**：

```
POST   /api/projects/{id}/comparisons/{comp_id}/export
Body: {
  "format": "pdf" | "excel" | "html",
  "sections": ["summary", "tasks_added", "tasks_removed", "tasks_modified", "variance_chart"],
  "title": "项目计划对比分析报告",
  "include_charts": true
}

Response: {
  "download_url": "/api/files/download/xxx",
  "expires_at": "2026-02-08T10:00:00Z"
}
```

**PDF 报告模板**：

```markdown
==============================================
        项目计划对比分析报告
==============================================

报告编号: COMP-2026-001
生成时间: 2026-02-08 09:30:00
基线名称: 总体设计基线
对比版本: V2.0

==============================================
                  一、执行摘要
==============================================

- 基线版本: V1.3 (2026-02-01)
- 当前版本: V2.0 (2026-02-08)
- 对比周期: 7 天

关键指标变化:
┌─────────────────────────────────────┐
│ 指标              │  基线  │  当前  │  变化  │
├─────────────────────────────────────┤
│ 任务总数          │   45   │   48   │   +3   │
│ 预估总工时 (h)    │  320   │  350   │  +30   │
│ 计划开始日期      │ 03-01  │ 03-01  │   -    │
│ 计划结束日期      │ 03-31  │ 04-05  │  +5天  │
│ 预算成本 (元)     │ 48000  │ 52500  │ +4500  │
└─────────────────────────────────────┘

==============================================
                二、新增任务
==============================================

#1. 1.3.5 安全性测试
    - 类型: 新增
    - 原因: 客户新增安全合规要求
    - 预估工时: 16h
    - 责任人: 王工

#2. 1.3.6 用户培训
    - 类型: 新增
    - 原因: 合同新增培训条款
    - 预估工时: 8h
    - 责任人: 张经理

==============================================
                三、变更任务
==============================================

#1. 1.2.1 架构设计
    - 变更前: 03/01 - 03/10 (40h)
    - 变更后: 03/01 - 03/15 (56h)
    - 变更原因: 技术方案调整，增加微服务架构
    - 审批: 已通过 (李总 2026-02-05)

==============================================
                  四、进度偏差
==============================================

整体偏差: +5 天
关键路径变化: 无

甘特图对比:
[基线 ──────]████████████|████████████[当前 ──────]███████████
             03/01      03/15        03/20        04/05

==============================================
                  五、资源变化
==============================================

新增资源:
- 赵工 (测试工程师) +24h

资源调整:
- 张三: 40h → 56h (+16h)
- 李四: 32h → 24h (-8h)

==============================================
                  六、建议措施
==============================================

1. 资源调配: 李四工作量可转移部分给赵工
2. 进度追赶: 建议并行处理 "1.3 开发实施" 与测试任务
3. 风险提示: 04/05 为合同交付截止日期，需关注

==============================================
            报告生成: 项目管理系统 v1.0
==============================================
```

**Excel 导出模板**：

```
Sheet1: 摘要
├── 项目名称, 对比周期, 基线版本, 当前版本
├── 任务变化, 工时变化, 成本变化, 进度偏差

Sheet2: 新增任务
├── WBS, 任务名称, 类型, 原因, 工时, 责任人, 开始日期, 结束日期

Sheet3: 变更任务
├── WBS, 任务名称, 变更字段, 原值, 新值, 变更原因, 审批人, 审批日期

Sheet4: 删除任务
├── WBS, 任务名称, 原工时, 删除原因

Sheet5: 资源对比
├── 资源, 原分配工时, 新分配工时, 变化, 利用率变化

Sheet6: 详细数据
├── 完整任务列表 (基线 vs 当前)
```

---

## 9. 开发优先级

### 第一阶段 (Week 3): 基础计划管理

| 功能 | 优先级 | 工作量 |
|------|--------|--------|
| 计划 CRUD | P0 | 2天 |
| 版本管理 | P0 | 2天 |
| WBS 管理 | P0 | 3天 |
| 审批流程 | P0 | 2天 |

### 第二阶段 (Week 4): 资源与工时

| 功能 | 优先级 | 工作量 |
|------|--------|--------|
| 资源管理 | P1 | 2天 |
| 资源分配 | P1 | 2天 |
| 资源负载图 | P1 | 1天 |
| 资源超载检测 | P1 | 1天 |
| 甘特图展示 | P1 | 2天 |

### 第三阶段 (迭代): 高级功能

| 功能 | 优先级 | 工作量 |
|------|--------|--------|
| 里程碑自动触发 | P2 | 1天 |
| 基线管理 | P2 | 2天 |
| 基线对比 | P2 | 2天 |
| 报告导出 (PDF/Excel) | P2 | 2天 |
| 关键路径 | P2 | 1天 |
| 成本分析 | P2 | 1天 |

---

## 10. 变更记录

| 日期 | 版本 | 变更内容 |
|------|------|---------|
| 2026-02-08 | v1.0 | 初始设计 |
| 2026-02-08 | v1.1 | 补充：里程碑自动触发、资源超载检测与提醒、对比报告导出 |

---

**待确认问题已全部解决 ✅**
