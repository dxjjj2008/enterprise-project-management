import { test, expect } from '@playwright/test';

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:3002';
const API_URL = process.env.E2E_API_URL || 'http://localhost:8000';

test.describe('Backend API Tests', () => {
  test('API health check', async ({ request }) => {
    const response = await request.get(`${API_URL}/health`);
    expect(response.status()).toBe(200);
  });
});

test.describe('Frontend Page Load Tests', () => {
  test('Login page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/login`);
    await page.waitForLoadState('networkidle');
    const title = await page.title();
    expect(title).toContain('企业项目管理系统');
  });

  test('Register page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/auth/register`);
    await page.waitForLoadState('networkidle');
    const title = await page.title();
    expect(title).toContain('企业项目管理系统');
  });

  test('Dashboard page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('networkidle');
    const body = await page.content();
    expect(body).toContain('企业项目管理系统');
  });

  test('Projects page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/projects`);
    await page.waitForLoadState('networkidle');
    const body = await page.content();
    expect(body).toContain('企业项目管理系统');
  });

  test('Tasks page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/tasks/board`);
    await page.waitForLoadState('networkidle');
    const body = await page.content();
    expect(body).toContain('企业项目管理系统');
  });

  test('Docs page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/docs`);
    await page.waitForLoadState('networkidle');
    const body = await page.content();
    expect(body).toContain('企业项目管理系统');
  });
});

test.describe('Feature Pages Tests', () => {
  test('Gantt chart page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/projects/1/gantt`);
    await page.waitForLoadState('networkidle');
    const body = await page.content();
    expect(body).toContain('甘特图');
  });

  test('Approvals page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/approvals`);
    await page.waitForLoadState('networkidle');
    const body = await page.content();
    expect(body).toContain('审批中心');
  });

  test('Planning page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/planning`);
    await page.waitForLoadState('networkidle');
    const body = await page.content();
    expect(body).toContain('计划');
  });

  test('Reports page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/reports`);
    await page.waitForLoadState('networkidle');
    const body = await page.content();
    expect(body).toContain('报表');
  });

  test('Settings page loads', async ({ page }) => {
    await page.goto(`${BASE_URL}/settings`);
    await page.waitForLoadState('networkidle');
    const body = await page.content();
    expect(body).toContain('设置');
  });
});

test.describe('User Interactions', () => {
  test('Navigation menu is visible', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('networkidle');

    // Check navigation items exist
    const navItems = await page.locator('.sidebar-menu, .el-menu, nav').count();
    expect(navItems).toBeGreaterThan(0);
  });

  test('Statistics cards are visible on dashboard', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('networkidle');

    // Dashboard should have stats cards
    const body = await page.content();
    // Check for common stat indicators
    expect(body).toMatch(/项目|任务|进行中|已完成/);
  });
});

test.describe('User Journey Tests', () => {
  test('Login flow - success', async ({ page }) => {
    await page.goto(`${BASE_URL}/auth/login`);
    await page.waitForLoadState('networkidle');

    // Check login form exists
    await expect(page.locator('form')).toBeVisible();

    // Fill login form (using test credentials)
    await page.fill('input[name="username"], input[type="text"]', 'testuser');
    await page.fill('input[name="password"], input[type="password"]', 'testpassword123');

    // Submit form
    await page.click('button[type="submit"], button:has-text("登录")');

    // Should redirect to dashboard or show error
    await page.waitForURL(/dashboard|projects|login/);
  });

  test('Dashboard - navigate through sections', async ({ page }) => {
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('networkidle');

    // Check dashboard stats
    await expect(page.locator('.stat-card, .stats-card')).toBeVisible();

    // Navigate to projects
    await page.click('a:has-text("项目"), .el-menu-item:has-text("项目")');
    await page.waitForURL(/projects/);
    await expect(page.locator('h2, .page-title')).toContainText('项目');
  });

  test('Projects - view list and detail', async ({ page }) => {
    await page.goto(`${BASE_URL}/projects`);
    await page.waitForLoadState('networkidle');

    // Check projects table/list exists
    await expect(page.locator('.projects-list, table, .el-table')).toBeVisible();

    // Click on first project if exists
    const firstProject = page.locator('.project-card, tr, .item').first();
    if (await firstProject.isVisible()) {
      await firstProject.click();
      await page.waitForLoadState('networkidle');
      await expect(page.locator('h2, .page-title')).toContainText('项目详情');
    }
  });

  test('Tasks - view kanban board', async ({ page }) => {
    await page.goto(`${BASE_URL}/tasks/board`);
    await page.waitForLoadState('networkidle');

    // Check kanban columns exist
    await expect(page.locator('.kanban-column, .el-collapse')).toBeVisible();

    // Check for task columns
    const columns = await page.locator('.column-header, .kanban-column h3').allTextContents();
    expect(columns.length).toBeGreaterThan(0);
  });

  test('Approvals - view approval center', async ({ page }) => {
    await page.goto(`${BASE_URL}/approvals`);
    await page.waitForLoadState('networkidle');

    // Check approval page elements
    await expect(page.locator('.approval-page, .stats-cards')).toBeVisible();

    // Check tabs
    const tabs = await page.locator('.el-tabs__item, .tab-item').allTextContents();
    expect(tabs.some(t => t.includes('待') || t.includes('审批'))).toBe(true);
  });

  test('Resources - view resource management', async ({ page }) => {
    await page.goto(`${BASE_URL}/resources`);
    await page.waitForLoadState('networkidle');

    // Check resource page elements
    await expect(page.locator('.resources-page, .stats-cards')).toBeVisible();
  });

  test('Settings - view user settings', async ({ page }) => {
    await page.goto(`${BASE_URL}/settings`);
    await page.waitForLoadState('networkidle');

    // Check settings page
    await expect(page.locator('.settings-page, form, .el-form')).toBeVisible();
  });

  test('Docs - view documentation', async ({ page }) => {
    await page.goto(`${BASE_URL}/docs`);
    await page.waitForLoadState('networkidle');

    // Check docs page
    await expect(page.locator('.docs-page, .doc-list, .el-menu')).toBeVisible();
  });
});

test.describe('Form Interactions', () => {
  test('Create project dialog opens', async ({ page }) => {
    await page.goto(`${BASE_URL}/projects`);
    await page.waitForLoadState('networkidle');

    // Click new project button
    await page.click('button:has-text("新建项目"), .new-project-btn');
    await page.waitForLoadState('networkidle');

    // Check dialog opens
    const dialog = page.locator('.el-dialog, .dialog, form').first();
    await expect(dialog).toBeVisible();
  });

  test('Create task dialog opens', async ({ page }) => {
    await page.goto(`${BASE_URL}/tasks/board`);
    await page.waitForLoadState('networkidle');

    // Click add task button
    await page.click('button:has-text("新建任务"), .add-task-btn');
    await page.waitForLoadState('networkidle');

    // Check dialog opens
    const dialog = page.locator('.el-dialog, .dialog').first();
    await expect(dialog).toBeVisible();
  });
});

test.describe('Responsive Design', () => {
  test('Mobile viewport - dashboard', async ({ page }) => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(`${BASE_URL}/`);
    await page.waitForLoadState('networkidle');

    // Should still be functional on mobile
    await expect(page.locator('.page-content, main')).toBeVisible();
  });

  test('Tablet viewport - projects', async ({ page }) => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(`${BASE_URL}/projects`);
    await page.waitForLoadState('networkidle');

    // Should still be functional on tablet
    await expect(page.locator('.page-content, main')).toBeVisible();
  });
});
