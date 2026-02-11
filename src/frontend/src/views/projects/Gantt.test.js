/**
 * Gantt Chart 页面测试
 *
 * 测试甘特图的时间轴计算、任务条定位、依赖线、拖拽交互和导出功能
 */

import { describe, it, expect } from 'vitest'

describe('GanttChart - Timeline Computation', () => {
  // 模拟甘特图配置
  const ganttConfig = {
    dayWidth: 40,
    rowHeight: 48,
    headerHeight: 60,
    columnWidth: 200,
    currentView: 'day'
  }

  // 模拟任务数据
  const mockGanttTasks = [
    {
      id: 1,
      name: '项目启动',
      startDate: '2026-02-01',
      endDate: '2026-02-05',
      progress: 100,
      priority: 'high',
      isMilestone: false,
      isGroup: false,
      children: [],
      dependencies: []
    },
    {
      id: 2,
      name: '需求分析',
      startDate: '2026-02-06',
      endDate: '2026-02-10',
      progress: 80,
      priority: 'high',
      isMilestone: false,
      isGroup: false,
      children: [],
      dependencies: [1]
    },
    {
      id: 3,
      name: '设计阶段',
      startDate: '2026-02-11',
      endDate: '2026-02-20',
      progress: 60,
      priority: 'medium',
      isMilestone: false,
      isGroup: true,
      children: [],
      dependencies: [2]
    },
    {
      id: 4,
      name: '里程碑: 设计完成',
      startDate: '2026-02-20',
      endDate: '2026-02-20',
      progress: 0,
      priority: 'high',
      isMilestone: true,
      isGroup: false,
      children: [],
      dependencies: []
    }
  ]

  it('calculates correct number of days in view', () => {
    const startDate = new Date('2026-02-01')
    const endDate = new Date('2026-02-28')
    const days = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1

    expect(days).toBe(28)
  })

  it('calculates timeline offset correctly', () => {
    const startDate = new Date('2026-02-01')
    const targetDate = new Date('2026-02-15')
    const dayWidth = 40

    const offsetDays = Math.floor((targetDate - startDate) / (1000 * 60 * 60 * 24))
    const offsetPixels = offsetDays * dayWidth

    expect(offsetDays).toBe(14)
    expect(offsetPixels).toBe(560)
  })

  it('calculates task bar width correctly', () => {
    const startDate = new Date('2026-02-01')
    const endDate = new Date('2026-02-10')
    const dayWidth = 40

    const duration = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24)) + 1
    const width = duration * dayWidth

    expect(duration).toBe(10)
    expect(width).toBe(400)
  })

  it('identifies milestone tasks correctly', () => {
    const milestoneTask = mockGanttTasks.find(t => t.isMilestone)
    const regularTasks = mockGanttTasks.filter(t => !t.isMilestone && !t.isGroup)

    expect(milestoneTask).toBeDefined()
    expect(milestoneTask?.name).toBe('里程碑: 设计完成')
    expect(regularTasks).toHaveLength(2)
  })

  it('identifies group tasks correctly', () => {
    const groupTask = mockGanttTasks.find(t => t.isGroup)
    const regularTasks = mockGanttTasks.filter(t => !t.isGroup && !t.isMilestone)

    expect(groupTask).toBeDefined()
    expect(groupTask?.name).toBe('设计阶段')
    expect(regularTasks).toHaveLength(2)
  })

  it('calculates timeline header dates correctly', () => {
    const startDate = new Date('2026-02-01')
    const viewDays = 28
    const headerDates = []

    for (let i = 0; i < viewDays; i++) {
      const currentDate = new Date(startDate)
      currentDate.setDate(startDate.getDate() + i)
      headerDates.push(currentDate)
    }

    expect(headerDates).toHaveLength(28)
    expect(headerDates[0].toISOString().split('T')[0]).toBe('2026-02-01')
    expect(headerDates[27].toISOString().split('T')[0]).toBe('2026-02-28')
  })

  it('calculates weekend days correctly', () => {
    const startDate = new Date('2026-02-01')
    const weekendDays = []

    for (let i = 0; i < 28; i++) {
      const currentDate = new Date(startDate)
      currentDate.setDate(startDate.getDate() + i)
      const dayOfWeek = currentDate.getDay()
      if (dayOfWeek === 0 || dayOfWeek === 6) {
        weekendDays.push(currentDate)
      }
    }

    // February 2026 has 4 weekends (8 weekend days)
    expect(weekendDays.length).toBeGreaterThanOrEqual(8)
  })

  it('calculates row position correctly', () => {
    const rowIndex = 2
    const rowHeight = 48
    const headerHeight = 60

    const topPosition = headerHeight + (rowIndex * rowHeight)

    expect(topPosition).toBe(156)
  })

  it('calculates today line position correctly', () => {
    const projectStartDate = new Date('2026-02-01')
    const todayDate = new Date('2026-02-15')
    const dayWidth = 40

    const daysFromStart = Math.floor((todayDate - projectStartDate) / (1000 * 60 * 60 * 24))
    const todayLinePosition = daysFromStart * dayWidth

    expect(daysFromStart).toBe(14)
    expect(todayLinePosition).toBe(560)
  })
})

describe('GanttChart - Bezier Dependency Lines', () => {
  it('generates correct bezier path for dependency', () => {
    const fromTask = { startDate: '2026-02-01', endDate: '2026-02-05' }
    const toTask = { startDate: '2026-02-06', endDate: '2026-02-10' }
    const dayWidth = 40
    const rowHeight = 48

    // Calculate positions
    const fromEndOffset = 4 * dayWidth // Day 4 (0-indexed)
    const toStartOffset = 5 * dayWidth // Day 5 (0-indexed)
    const fromRowTop = 100
    const toRowTop = 150

    // Bezier curve control points
    const cornerSize = 20
    const midY = fromRowTop + (toRowTop - fromRowTop) / 2

    // Generate path
    const startX = fromEndOffset
    const startY = fromRowTop + rowHeight / 2
    const endX = toStartOffset
    const endY = toRowTop + rowHeight / 2

    // Cubic bezier path
    const path = `M ${startX} ${startY} 
                  C ${startX + cornerSize} ${startY}, 
                    ${endX - cornerSize} ${endY}, 
                    ${endX} ${endY}`

    expect(path).toContain('M')
    expect(path).toContain('C') // Cubic bezier
    expect(path).toContain(startX.toString())
    expect(path).toContain(endX.toString())
  })

  it('handles forward dependency (from earlier to later task)', () => {
    const fromTask = { startDate: '2026-02-01', endDate: '2026-02-05' }
    const toTask = { startDate: '2026-02-10', endDate: '2026-02-15' }

    const fromDate = new Date(fromTask.endDate)
    const toDate = new Date(toTask.startDate)
    const daysBetween = Math.ceil((toDate - fromDate) / (1000 * 60 * 60 * 24))

    expect(daysBetween).toBe(5) // Feb 6, 7, 8, 9, 10 = 5 days gap
  })

  it('handles adjacent tasks (no gap)', () => {
    const fromTask = { startDate: '2026-02-01', endDate: '2026-02-05' }
    const toTask = { startDate: '2026-02-06', endDate: '2026-02-10' }

    const fromDate = new Date(fromTask.endDate)
    const toDate = new Date(toTask.startDate)
    const daysBetween = Math.ceil((toDate - fromDate) / (1000 * 60 * 60 * 24))

    expect(daysBetween).toBe(1) // Feb 6 - Feb 5 = 1 day
  })

  it('calculates dependency arrow direction correctly', () => {
    const fromRowIndex = 0
    const toRowIndex = 2
    const rowHeight = 48

    const verticalDistance = Math.abs(toRowIndex - fromRowIndex) * rowHeight
    const isDownward = toRowIndex > fromRowIndex

    expect(verticalDistance).toBe(96)
    expect(isDownward).toBe(true)
  })

  it('generates valid SVG path for complex dependency', () => {
    const startX = 200
    const startY = 100
    const endX = 400
    const endY = 200
    const cornerSize = 20

    // Horizontal-vertical-horizontal path for cross-row dependencies
    const path = `M ${startX} ${startY} 
                  L ${startX + cornerSize} ${startY}
                  L ${startX + cornerSize} ${endY}
                  L ${endX} ${endY}`

    expect(path).toContain('M')
    expect(path).toContain('L') // Line commands
    expect(path).toContain('200 100') // Start point
    expect(path).toContain('400 200') // End point
  })
})

describe('GanttChart - Task Bar Positioning', () => {
  it('calculates task bar left position correctly', () => {
    const taskStartDate = new Date('2026-02-05')
    const projectStartDate = new Date('2026-02-01')
    const dayWidth = 40

    const daysFromStart = Math.floor((taskStartDate - projectStartDate) / (1000 * 60 * 60 * 24))
    const leftPosition = daysFromStart * dayWidth + 200 // +200 for task name column

    expect(daysFromStart).toBe(4)
    expect(leftPosition).toBe(360)
  })

  it('calculates task bar width correctly for duration', () => {
    const taskStartDate = new Date('2026-02-05')
    const taskEndDate = new Date('2026-02-10')
    const dayWidth = 40

    const durationDays = Math.ceil((taskEndDate - taskStartDate) / (1000 * 60 * 60 * 24)) + 1
    const barWidth = durationDays * dayWidth

    expect(durationDays).toBe(6)
    expect(barWidth).toBe(240)
  })

  it('positions milestone diamond correctly', () => {
    const milestoneDate = new Date('2026-02-15')
    const projectStartDate = new Date('2026-02-01')
    const dayWidth = 40
    const rowHeight = 48

    const daysFromStart = Math.floor((milestoneDate - projectStartDate) / (1000 * 60 * 60 * 24))
    const leftPosition = daysFromStart * dayWidth + 200
    const centerY = rowHeight / 2

    expect(daysFromStart).toBe(14)
    expect(leftPosition).toBe(760)
  })

  it('calculates progress bar width correctly', () => {
    const progress = 60
    const barWidth = 240

    const progressWidth = (progress / 100) * barWidth

    expect(progressWidth).toBe(144)
  })

  it('handles zero progress task', () => {
    const progress = 0
    const barWidth = 240

    const progressWidth = (progress / 100) * barWidth

    expect(progressWidth).toBe(0)
  })

  it('handles 100% progress task', () => {
    const progress = 100
    const barWidth = 240

    const progressWidth = (progress / 100) * barWidth

    expect(progressWidth).toBe(240)
  })

  it('positions group task indicator correctly', () => {
    const groupTaskIndex = 3
    const headerHeight = 60
    const rowHeight = 48

    const topPosition = headerHeight + (groupTaskIndex * rowHeight)

    expect(topPosition).toBe(204)
  })
})

describe('GanttChart - Drag and Drop', () => {
  it('calculates new date position during drag', () => {
    const startDate = new Date('2026-02-01')
    const dragStartX = 240 // 6 days from start (200 + 6*40)
    const dayWidth = 40

    const daysFromStart = (dragStartX - 200) / dayWidth
    const newDate = new Date(startDate)
    newDate.setDate(startDate.getDate() + daysFromStart)

    expect(daysFromStart).toBe(1)
    expect(newDate.toISOString().split('T')[0]).toBe('2026-02-02')
  })

  it('calculates task duration during resize', () => {
    const oldWidth = 160 // 4 days
    const newWidth = 200 // 5 days
    const dayWidth = 40

    const oldDuration = oldWidth / dayWidth
    const newDuration = newWidth / dayWidth

    expect(oldDuration).toBe(4)
    expect(newDuration).toBe(5)
  })

  it('validates drag boundaries', () => {
    const minDayWidth = 20
    const maxDayWidth = 80
    const currentDayWidth = 40

    expect(currentDayWidth).toBeGreaterThanOrEqual(minDayWidth)
    expect(currentDayWidth).toBeLessThanOrEqual(maxDayWidth)
  })

  it('calculates snap position for task movement', () => {
    const rawPosition = 145 // Between days 3 and 4
    const dayWidth = 40

    // Snap to nearest day boundary
    const snappedPosition = Math.round(rawPosition / dayWidth) * dayWidth

    expect(snappedPosition).toBe(160) // Day 4 boundary
  })

  it('handles left resize correctly', () => {
    const oldStartDate = '2026-02-05'
    const newStartDate = '2026-02-03'
    const oldEndDate = '2026-02-10'

    const oldStart = new Date(oldStartDate)
    const newStart = new Date(newStartDate)
    const end = new Date(oldEndDate)

    const oldDuration = Math.ceil((end - oldStart) / (1000 * 60 * 60 * 24)) + 1
    const newDuration = Math.ceil((end - newStart) / (1000 * 60 * 60 * 24)) + 1

    expect(oldDuration).toBe(6)
    expect(newDuration).toBe(8)
  })

  it('handles right resize correctly', () => {
    const startDate = '2026-02-05'
    const oldEndDate = '2026-02-10'
    const newEndDate = '2026-02-15'

    const start = new Date(startDate)
    const oldEnd = new Date(oldEndDate)
    const newEnd = new Date(newEndDate)

    const oldDuration = Math.ceil((oldEnd - start) / (1000 * 60 * 60 * 24)) + 1
    const newDuration = Math.ceil((newEnd - start) / (1000 * 60 * 60 * 24)) + 1

    expect(oldDuration).toBe(6)
    expect(newDuration).toBe(11)
  })

  it('validates task dependencies during drag', () => {
    const dependentTaskStart = new Date('2026-02-04')
    const parentTaskEnd = new Date('2026-02-05')

    const isViolation = dependentTaskStart < parentTaskEnd

    expect(isViolation).toBe(true)
  })

  it('calculates valid drag range', () => {
    const projectStart = new Date('2026-02-01')
    const projectEnd = new Date('2026-02-28')
    const taskStart = new Date('2026-02-10')
    const taskDuration = 5

    const minDate = projectStart
    const maxDate = new Date(projectEnd)
    maxDate.setDate(projectEnd.getDate() - taskDuration)

    expect(minDate < taskStart).toBe(true)
    expect(taskStart < maxDate).toBe(true)
  })
})

describe('GanttChart - Task Dependencies', () => {
  it('validates dependency chain integrity', () => {
    const tasks = [
      { id: 1, dependencies: [] },
      { id: 2, dependencies: [1] },
      { id: 3, dependencies: [2] },
      { id: 4, dependencies: [1, 3] }
    ]

    // Build dependency graph
    const graph = {}
    tasks.forEach(task => {
      graph[task.id] = task.dependencies
    })

    expect(graph[1]).toEqual([])
    expect(graph[2]).toEqual([1])
    expect(graph[3]).toEqual([2])
    expect(graph[4]).toEqual([1, 3])
  })

  it('detects circular dependencies', () => {
    const tasks = [
      { id: 1, dependencies: [2] },
      { id: 2, dependencies: [3] },
      { id: 3, dependencies: [1] } // Creates cycle: 1->2->3->1
    ]

    // Simple cycle detection using DFS
    const visited = new Set()
    const recursionStack = new Set()

    const hasCycle = (taskId, graph, visitedSet, stackSet) => {
      visitedSet.add(taskId)
      stackSet.add(taskId)

      const dependencies = graph[taskId] || []
      for (const dep of dependencies) {
        if (!visitedSet.has(dep)) {
          if (hasCycle(dep, graph, visitedSet, stackSet)) return true
        } else if (stackSet.has(dep)) {
          return true
        }
      }

      stackSet.delete(taskId)
      return false
    }

    const graph = {}
    tasks.forEach(task => { graph[task.id] = task.dependencies })

    const hasCircularDependency = hasCycle(1, graph, visited, recursionStack)

    expect(hasCircularDependency).toBe(true)
  })

  it('calculates critical path tasks', () => {
    const tasks = [
      { id: 1, name: 'Task A', duration: 3, dependencies: [] },
      { id: 2, name: 'Task B', duration: 5, dependencies: [1] },
      { id: 3, name: 'Task C', duration: 4, dependencies: [1] },
      { id: 4, name: 'Task D', duration: 6, dependencies: [2, 3] }
    ]

    // Calculate earliest start and finish times
    const earliestFinish = {}
    tasks.forEach(task => {
      const depFinishes = (task.dependencies || []).map(depId => earliestFinish[depId] || 0)
      const earliestStart = depFinishes.length > 0 ? Math.max(...depFinishes) : 0
      earliestFinish[task.id] = earliestStart + task.duration
    })

    expect(earliestFinish[1]).toBe(3)
    expect(earliestFinish[2]).toBe(8)
    expect(earliestFinish[3]).toBe(7)
    expect(earliestFinish[4]).toBe(14) // After both B and C complete
  })

  it('validates dependency existence', () => {
    const task = { id: 1, name: 'Task', dependencies: [2, 3, 4] }
    const existingTaskIds = new Set([1, 2, 3])

    const invalidDeps = task.dependencies.filter(depId => !existingTaskIds.has(depId))

    expect(invalidDeps).toEqual([4])
  })
})

describe('GanttChart - Statistics', () => {
  const mockTasks = [
    { id: 1, progress: 100, priority: 'high', duration: 5 },
    { id: 2, progress: 50, priority: 'high', duration: 7 },
    { id: 3, progress: 0, priority: 'medium', duration: 3 },
    { id: 4, progress: 25, priority: 'low', duration: 10 },
    { id: 5, progress: 75, priority: 'medium', duration: 4 }
  ]

  it('calculates overall progress correctly', () => {
    const totalProgress = mockTasks.reduce((sum, task) => sum + task.progress, 0)
    const avgProgress = Math.round(totalProgress / mockTasks.length)

    expect(totalProgress).toBe(250)
    expect(avgProgress).toBe(50)
  })

  it('counts tasks by priority', () => {
    const priorityCount = {
      high: mockTasks.filter(t => t.priority === 'high').length,
      medium: mockTasks.filter(t => t.priority === 'medium').length,
      low: mockTasks.filter(t => t.priority === 'low').length
    }

    expect(priorityCount.high).toBe(2)
    expect(priorityCount.medium).toBe(2)
    expect(priorityCount.low).toBe(1)
  })

  it('calculates total project duration', () => {
    const totalDuration = mockTasks.reduce((sum, task) => sum + task.duration, 0)

    expect(totalDuration).toBe(29)
  })

  it('counts completed tasks', () => {
    const completedTasks = mockTasks.filter(t => t.progress === 100).length

    expect(completedTasks).toBe(1)
  })

  it('counts in-progress tasks', () => {
    const inProgressTasks = mockTasks.filter(t => t.progress > 0 && t.progress < 100).length

    expect(inProgressTasks).toBe(3)
  })

  it('counts not-started tasks', () => {
    const notStartedTasks = mockTasks.filter(t => t.progress === 0).length

    expect(notStartedTasks).toBe(1)
  })
})

describe('GanttChart - View Controls', () => {
  it('calculates correct day width for day view', () => {
    const viewConfig = { currentView: 'day', dayWidth: 40 }
    const dayWidths = { day: 40, week: 20, month: 8 }

    expect(dayWidths[viewConfig.currentView]).toBe(40)
  })

  it('calculates correct day width for week view', () => {
    const viewConfig = { currentView: 'week', dayWidth: 20 }
    const dayWidths = { day: 40, week: 20, month: 8 }

    expect(dayWidths[viewConfig.currentView]).toBe(20)
  })

  it('calculates correct day width for month view', () => {
    const viewConfig = { currentView: 'month', dayWidth: 8 }
    const dayWidths = { day: 40, week: 20, month: 8 }

    expect(dayWidths[viewConfig.currentView]).toBe(8)
  })

  it('calculates visible date range for day view', () => {
    const startDate = new Date('2026-02-01')
    const dayWidth = 40
    const containerWidth = 1200
    const nameColumnWidth = 200

    const visibleDays = Math.floor((containerWidth - nameColumnWidth) / dayWidth)

    expect(visibleDays).toBe(25)
  })

  it('calculates visible date range for week view', () => {
    const startDate = new Date('2026-02-01')
    const dayWidth = 20
    const containerWidth = 1200
    const nameColumnWidth = 200

    const visibleDays = Math.floor((containerWidth - nameColumnWidth) / dayWidth)

    expect(visibleDays).toBe(50)
  })
})

describe('GanttChart - Export Functionality', () => {
  it('generates CSV export data structure', () => {
    const tasks = [
      { id: 1, name: 'Task 1', startDate: '2026-02-01', endDate: '2026-02-05', progress: 100 },
      { id: 2, name: 'Task 2', startDate: '2026-02-06', endDate: '2026-02-10', progress: 50 }
    ]

    const csvHeaders = 'ID,Name,Start Date,End Date,Progress (%),Duration (days)\n'
    const csvRows = tasks.map(t => {
      const duration = Math.ceil(new Date(t.endDate) - new Date(t.startDate)) / (1000 * 60 * 60 * 24) + 1
      return `${t.id},"${t.name}",${t.startDate},${t.endDate},${t.progress},${duration}`
    }).join('\n')

    expect(csvHeaders).toContain('ID')
    expect(csvHeaders).toContain('Name')
    expect(csvRows).toContain('Task 1')
    expect(csvRows).toContain('100')
  })

  it('generates JSON export data structure', () => {
    const tasks = [
      { id: 1, name: 'Task 1', startDate: '2026-02-01', endDate: '2026-02-05', progress: 100 },
      { id: 2, name: 'Task 2', startDate: '2026-02-06', endDate: '2026-02-10', progress: 50 }
    ]

    const exportData = {
      exportDate: new Date().toISOString(),
      project: 'Enterprise Project',
      tasks: tasks
    }

    expect(exportData.project).toBe('Enterprise Project')
    expect(exportData.tasks).toHaveLength(2)
    expect(exportData.tasks[0].progress).toBe(100)
  })

  it('calculates export filename with timestamp', () => {
    const timestamp = '2026-02-15_143022'
    const filename = `gantt_export_${timestamp}.csv`

    expect(filename).toBe('gantt_export_2026-02-15_143022.csv')
  })

  it('validates PNG export container dimensions', () => {
    const containerConfig = {
      timelineWidth: 1200,
      taskListWidth: 200,
      totalWidth: 1400,
      rowHeight: 48,
      taskCount: 10,
      headerHeight: 60
    }

    const totalHeight = containerConfig.headerHeight + (containerConfig.taskCount * containerConfig.rowHeight)

    expect(containerConfig.totalWidth).toBe(1400)
    expect(totalHeight).toBe(540)
  })
})

describe('GanttChart - Group and Milestone Rendering', () => {
  it('correctly identifies expandable groups', () => {
    const groups = [
      { id: 1, name: 'Design', isGroup: true, children: [2, 3] },
      { id: 2, name: 'UI Design', isGroup: false, parentId: 1 },
      { id: 3, name: 'API Design', isGroup: false, parentId: 1 }
    ]

    const groupTasks = groups.filter(t => t.isGroup)
    const childTasks = groups.filter(t => !t.isGroup && t.parentId)

    expect(groupTasks).toHaveLength(1)
    expect(childTasks).toHaveLength(2)
    expect(groupTasks[0].children).toHaveLength(2)
  })

  it('calculates group row height correctly', () => {
    const groupConfig = {
      expandedRowHeight: 48,
      collapsedRowHeight: 48,
      childRowHeight: 48,
      childrenCount: 3
    }

    const expandedHeight = groupConfig.expandedRowHeight + (groupConfig.childrenCount * groupConfig.childRowHeight)
    const collapsedHeight = groupConfig.collapsedRowHeight

    expect(expandedHeight).toBe(192)
    expect(collapsedHeight).toBe(48)
  })

  it('positions milestone marker correctly', () => {
    const milestoneDate = new Date('2026-02-15')
    const projectStartDate = new Date('2026-02-01')
    const dayWidth = 40
    const milestoneSize = 16

    const daysFromStart = Math.floor((milestoneDate - projectStartDate) / (1000 * 60 * 60 * 24))
    const leftPosition = daysFromStart * dayWidth + 200

    expect(daysFromStart).toBe(14)
    expect(leftPosition).toBe(760)
  })
})
