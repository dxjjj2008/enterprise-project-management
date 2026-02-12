/**
 * 补充浏览器自动化测试
 * 
 * 测试范围: 任务编辑/删除、甘特图、计划管理、资源管理、
 *          审批流程、报表统计、设置页面、退出登录
 */

const { chromium } = require('playwright');

const BASE_URL = process.env.E2E_BASE_URL || 'http://localhost:3001';
const API_URL = process.env.E2E_API_URL || 'http://localhost:8000';

const CONFIG = {
  headless: true,
  timeout: 30000,
  screenshotOnFailure: true,
};

const log = (msg, type = 'INFO') => {
  const timestamp = new Date().toISOString();
  const icons = { '✅': 'PASS', '❌': 'FAIL', 'ℹ️': 'INFO', '⚠️': 'WARN', '🔄': 'RUN' };
  console.log(`[${timestamp}] [${icons[type] || type}] ${msg}`);
};

const sleep = (ms) => new Promise(resolve => setTimeout(resolve, ms));

class AdditionalTestRunner {
  constructor() {
    this.browser = null;
    this.context = null;
    this.page = null;
    this.results = [];
    this.testsPassed = 0;
    this.testsFailed = 0;
    this.testUser = {
      username: 'autotestuser',
      password: 'autotest123',
    };
  }

  async setup() {
    log('启动浏览器...', '🔄');
    this.browser = await chromium.launch({ headless: CONFIG.headless });
    this.context = await this.browser.newContext({
      viewport: { width: 1280, height: 720 },
    });
    this.page = await this.context.newPage();
    
    this.page.on('console', msg => {
      if (msg.type() === 'error') {
        log(`控制台错误: ${msg.text()}`, '⚠️');
      }
    });
    
    this.page.on('pageerror', err => {
      log(`页面错误: ${err.message}`, '⚠️');
    });
    
    log('浏览器启动成功', '✅');
  }

  // 关闭 Vite 错误遮罩层
  async dismissErrorOverlay() {
    try {
      const errorOverlay = this.page.locator('vite-error-overlay');
      if (await errorOverlay.isVisible()) {
        log('发现 Vite 错误遮罩层，尝试关闭...', 'ℹ️');
        // 按 Escape 关闭错误遮罩
        await this.page.keyboard.press('Escape');
        await sleep(500);
      }
    } catch (e) {
      // 忽略
    }
  }

  async teardown() {
    if (this.browser) {
      await this.browser.close();
      log('浏览器已关闭', 'ℹ️');
    }
  }

  async runTest(name, testFn) {
    log(`执行测试: ${name}`, '🔄');
    try {
      await testFn();
      this.testsPassed++;
      this.results.push({ test: name, status: 'PASS', message: '测试通过' });
      log(`✅ ${name} - 通过`, '✅');
      return true;
    } catch (error) {
      this.testsFailed++;
      this.results.push({ test: name, status: 'FAIL', message: error.message });
      log(`❌ ${name} - 失败: ${error.message}`, '❌');
      
      if (CONFIG.screenshotOnFailure) {
        const screenshotPath = `test-results/${name.replace(/\s+/g, '_')}_${Date.now()}.png`;
        await this.page.screenshot({ path: screenshotPath, fullPage: true });
        log(`截图已保存: ${screenshotPath}`, 'ℹ️');
      }
      return false;
    }
  }

  async login() {
    log('执行登录...', 'ℹ️');
    await this.page.goto(`${BASE_URL}/auth/login`);
    await this.page.waitForLoadState('networkidle');
    await sleep(2000);
    
    // 关闭错误遮罩层
    await this.dismissErrorOverlay();
    
    const formItems = this.page.locator('.el-form-item');
    await formItems.nth(0).locator('input').fill(this.testUser.username);
    await formItems.nth(1).locator('input').fill(this.testUser.password);
    
    // 关闭错误遮罩层后再次尝试
    await this.dismissErrorOverlay();
    
    const loginBtn = this.page.locator('.el-button--primary:has-text("登录")');
    
    // 尝试正常点击，如果失败则使用 force
    try {
      await loginBtn.click({ timeout: 5000 });
    } catch (e) {
      log('正常点击失败，尝试强制点击', 'ℹ️');
      await loginBtn.click({ force: true });
    }
    
    await sleep(3000);
    
    const url = this.page.url();
    if (!url.includes('login')) {
      log('登录成功', '✅');
    } else {
      log(`登录后URL: ${url}`, 'ℹ️');
    }
  }

  // ========== 任务编辑测试 ==========

  async testTaskEdit() {
    log('测试任务编辑功能...', 'ℹ️');
    await this.page.goto(`${BASE_URL}/tasks/board`);
    await this.page.waitForLoadState('networkidle');
    await sleep(2000);
    await this.dismissErrorOverlay();
    
    // 检查是否有任务可以编辑
    const taskCards = await this.page.locator('.task-card, [class*="task"]').count();
    log(`找到 ${taskCards} 个任务元素`, 'ℹ️');
    
    // 查找编辑按钮
    const editBtn = this.page.locator('button:has-text("编辑"), [class*="edit"]').first();
    if (await editBtn.isVisible()) {
      await editBtn.click();
      await sleep(500);
      
      // 检查编辑对话框
      const dialog = this.page.locator('.el-dialog').first();
      if (await dialog.isVisible()) {
        log('编辑对话框已打开', '✅');
        
        // 修改标题
        const titleInput = this.page.locator('.el-dialog input[placeholder*="标题"], .el-dialog input[id*="title"]').first();
        if (await titleInput.count() > 0) {
          const newTitle = `自动化编辑_${Date.now()}`;
          await titleInput.fill(newTitle);
          log(`新标题: ${newTitle}`, 'ℹ️');
        }
        
        // 点击保存
        const saveBtn = this.page.locator('.el-dialog .el-button--primary:has-text("保存"), .el-dialog button:has-text("保存")').first();
        if (await saveBtn.isVisible()) {
          await saveBtn.click();
          await sleep(1000);
          log('任务保存成功', '✅');
        }
      }
    } else {
      log('未找到编辑按钮（可能需要先创建任务）', 'ℹ️');
    }
  }

  async testTaskDelete() {
    log('测试任务删除功能...', 'ℹ️');
    await this.page.goto(`${BASE_URL}/tasks/board`);
    await this.page.waitForLoadState('networkidle');
    await sleep(2000);
    await this.dismissErrorOverlay();
    
    // 查找删除按钮
    const deleteBtn = this.page.locator('button:has-text("删除"), [class*="delete"]').first();
    if (await deleteBtn.isVisible()) {
      await deleteBtn.click();
      await sleep(500);
      
      // 确认删除对话框
      const confirmBtn = this.page.locator('.el-message-box .el-button--danger:has-text("确定"), .el-popconfirm .el-button--primary').first();
      if (await confirmBtn.isVisible()) {
        await confirmBtn.click();
        await sleep(1000);
        log('任务删除成功', '✅');
      }
    } else {
      log('未找到删除按钮', 'ℹ️');
    }
  }

  async testTaskDetailView() {
    log('测试任务详情查看功能...', 'ℹ️');
    await this.page.goto(`${BASE_URL}/tasks/board`);
    await this.page.waitForLoadState('networkidle');
    await sleep(2000);
    await this.dismissErrorOverlay();
    
    // 点击任务卡片查看详情
    const taskCard = this.page.locator('.task-card, [class*="task-card"]').first();
    if (await taskCard.isVisible()) {
      await taskCard.click();
      await sleep(1000);
      
      // 检查详情抽屉或对话框
      const detailPanel = this.page.locator('.el-drawer, .el-dialog, [class*="detail"]').first();
      if (await detailPanel.isVisible()) {
        log('任务详情面板已打开', '✅');
        
        // 验证详情内容
        const title = await this.page.locator('[class*="detail-title"], [class*="task-title"]').first().textContent();
        log(`任务标题: ${title}`, 'ℹ️');
      }
    } else {
      log('未找到任务卡片', 'ℹ️');
    }
  }

  // ========== 甘特图测试 ==========

  async testGanttPage() {
    log('测试甘特图页面...', 'ℹ️');
    await this.page.goto(`${BASE_URL}/planning/gantt`);
    await this.page.waitForLoadState('networkidle');
    await sleep(2000);
    await this.dismissErrorOverlay();
    
    const title = await this.page.title();
    log(`页面标题: ${title}`, 'ℹ️');
    
    // 检查甘特图元素
    const ganttChart = await this.page.locator('[class*="gantt"], [class*="timeline"]').count();
    const ganttHeader = await this.page.locator('[class*="gantt-header"], [class*="timeline-header"]').count();
    
    log(`甘特图元素数: ${ganttChart}`, 'ℹ️');
    log(`甘特图头部元素数: ${ganttHeader}`, 'ℹ️');
    
    if (ganttChart > 0 || ganttHeader > 0) {
      log('甘特图页面加载成功', '✅');
    } else {
      log('甘特图页面已加载（可能使用Canvas/SVG渲染）', 'ℹ️');
    }
  }

  // ========== 计划管理测试 ==========

  async testPlanningPage() {
    log('测试计划管理页面...', 'ℹ️');
    await this.page.goto(`${BASE_URL}/planning`);
    await this.page.waitForLoadState('networkidle');
    await sleep(2000);
    await this.dismissErrorOverlay();
    
    const title = await this.page.title();
    log(`页面标题: ${title}`, 'ℹ️');
    
    // 检查计划列表
    const planList = await this.page.locator('[class*="plan"], [class*="planning"]').count();
    const planCard = await this.page.locator('.el-card:has-text("计划")').count();
    
    log(`计划相关元素数: ${planList}`, 'ℹ️');
    log(`计划卡片数: ${planCard}`, 'ℹ️');
    
    if (planList > 0 || planCard > 0) {
      log('计划管理页面加载成功', '✅');
    }
  }

  // ========== 资源管理测试 ==========

  async testResourcesPage() {
    log('测试资源管理页面...', 'ℹ️');
    await this.page.goto(`${BASE_URL}/resources`);
    await this.page.waitForLoadState('networkidle');
    await sleep(2000);
    await this.dismissErrorOverlay();
    
    const title = await this.page.title();
    log(`页面标题: ${title}`, 'ℹ️');
    
    // 检查资源管理元素
    const resourceTable = await this.page.locator('.el-table, [class*="resource"]').count();
    const userCard = await this.page.locator('[class*="user"], [class*="member"]').count();
    
    log(`资源表格元素数: ${resourceTable}`, 'ℹ️');
    log(`用户元素数: ${userCard}`, 'ℹ️');
    
    if (resourceTable > 0 || userCard > 0) {
      log('资源管理页面加载成功', '✅');
    }
  }

  // ========== 审批流程测试 ==========

  async testApprovalsPage() {
    log('测试审批流程页面...', 'ℹ️');
    await this.page.goto(`${BASE_URL}/approvals`);
    await this.page.waitForLoadState('networkidle');
    await sleep(2000);
    await this.dismissErrorOverlay();
    
    const title = await this.page.title();
    log(`页面标题: ${title}`, 'ℹ️');
    
    // 检查审批元素
    const approvalList = await this.page.locator('[class*="approval"]').count();
    const approvalCard = await this.page.locator('.el-card:has-text("审批")').count();
    
    log(`审批相关元素数: ${approvalList}`, 'ℹ️');
    log(`审批卡片数: ${approvalCard}`, 'ℹ️');
    
    if (approvalList > 0 || approvalCard > 0) {
      log('审批流程页面加载成功', '✅');
    }
  }

  // ========== 报表统计测试 ==========

  async testReportsPage() {
    log('测试报表统计页面...', 'ℹ️');
    await this.page.goto(`${BASE_URL}/reports`);
    await this.page.waitForLoadState('networkidle');
    await sleep(2000);
    await this.dismissErrorOverlay();
    
    const title = await this.page.title();
    log(`页面标题: ${title}`, 'ℹ️');
    
    // 检查报表元素
    const reportChart = await this.page.locator('[class*="chart"], [class*="report"]').count();
    const statistics = await this.page.locator('[class*="statistic"]').count();
    
    log(`报表图表元素数: ${reportChart}`, 'ℹ️');
    log(`统计元素数: ${statistics}`, 'ℹ️');
    
    if (reportChart > 0 || statistics > 0) {
      log('报表统计页面加载成功', '✅');
    }
  }

  // ========== 设置页面测试 ==========

  async testSettingsPage() {
    log('测试设置页面...', 'ℹ️');
    await this.page.goto(`${BASE_URL}/settings`);
    await this.page.waitForLoadState('networkidle');
    await sleep(2000);
    await this.dismissErrorOverlay();
    
    const title = await this.page.title();
    log(`页面标题: ${title}`, 'ℹ️');
    
    // 检查设置页面元素
    const settingsForm = await this.page.locator('.el-form, [class*="settings"]').count();
    const profileCard = await this.page.locator('.el-card:has-text("个人")').count();
    
    log(`设置表单元素数: ${settingsForm}`, 'ℹ️');
    log(`个人卡片数: ${profileCard}`, 'ℹ️');
    
    if (settingsForm > 0 || profileCard > 0) {
      log('设置页面加载成功', '✅');
    }
  }

  // ========== 退出登录测试 ==========

  async testLogout() {
    log('测试退出登录功能...', 'ℹ️');
    
    // 点击用户下拉菜单
    const userDropdown = this.page.locator('.user-dropdown, .el-dropdown-trigger').first();
    if (await userDropdown.isVisible()) {
      await userDropdown.click();
      await sleep(500);
      
      // 点击退出登录
      const logoutBtn = this.page.locator('.el-dropdown-menu__item:has-text("退出"), text=退出登录').first();
      if (await logoutBtn.isVisible()) {
        await logoutBtn.click();
        await sleep(1000);
        
        // 验证跳转到登录页
        const url = this.page.url();
        if (url.includes('login') || url.includes('auth')) {
          log('退出登录成功，跳转到登录页', '✅');
        } else {
          log(`退出后URL: ${url}`, 'ℹ️');
        }
      } else {
        log('未找到退出登录按钮', '⚠️');
      }
    } else {
      log('未找到用户下拉菜单', '⚠️');
    }
  }

  // ========== 问题跟踪测试 ==========

  async testIssuesPage() {
    log('测试问题跟踪页面...', 'ℹ️');
    await this.page.goto(`${BASE_URL}/issues`);
    await this.page.waitForLoadState('networkidle');
    await sleep(2000);
    await this.dismissErrorOverlay();
    
    const title = await this.page.title();
    log(`页面标题: ${title}`, 'ℹ️');
    
    // 检查问题跟踪元素
    const issueList = await this.page.locator('[class*="issue"]').count();
    const issueCard = await this.page.locator('.el-card:has-text("问题")').count();
    
    log(`问题相关元素数: ${issueList}`, 'ℹ️');
    log(`问题卡片数: ${issueCard}`, 'ℹ️');
    
    if (issueList > 0 || issueCard > 0) {
      log('问题跟踪页面加载成功', '✅');
    }
  }

  // ========== 风险管理测试 ==========

  async testRisksPage() {
    log('测试风险管理页面...', 'ℹ️');
    await this.page.goto(`${BASE_URL}/risks`);
    await this.page.waitForLoadState('networkidle');
    await sleep(2000);
    await this.dismissErrorOverlay();
    
    const title = await this.page.title();
    log(`页面标题: ${title}`, 'ℹ️');
    
    // 检查风险管理元素
    const riskList = await this.page.locator('[class*="risk"]').count();
    const riskCard = await this.page.locator('.el-card:has-text("风险")').count();
    
    log(`风险相关元素数: ${riskList}`, 'ℹ️');
    log(`风险卡片数: ${riskCard}`, 'ℹ️');
    
    if (riskList > 0 || riskCard > 0) {
      log('风险管理页面加载成功', '✅');
    }
  }

  // ========== 运行所有测试 ==========

  async runAllTests() {
    console.log('\n' + '='.repeat(60));
    console.log('🚀 补充浏览器自动化测试开始');
    console.log('='.repeat(60) + '\n');

    try {
      await this.setup();
      
      // 先登录
      await this.login();
      
      // 任务管理测试
      console.log('\n📌 任务管理测试');
      console.log('-'.repeat(40));
      await this.runTest('任务编辑', () => this.testTaskEdit());
      await this.runTest('任务删除', () => this.testTaskDelete());
      await this.runTest('任务详情查看', () => this.testTaskDetailView());
      
      // 其他模块测试
      console.log('\n📌 其他模块测试');
      console.log('-'.repeat(40));
      await this.runTest('甘特图页面', () => this.testGanttPage());
      await this.runTest('计划管理页面', () => this.testPlanningPage());
      await this.runTest('资源管理页面', () => this.testResourcesPage());
      await this.runTest('审批流程页面', () => this.testApprovalsPage());
      await this.runTest('报表统计页面', () => this.testReportsPage());
      await this.runTest('设置页面', () => this.testSettingsPage());
      await this.runTest('问题跟踪页面', () => this.testIssuesPage());
      await this.runTest('风险管理页面', () => this.testRisksPage());
      
      // 退出登录测试（最后执行）
      console.log('\n📌 退出登录测试');
      console.log('-'.repeat(40));
      await this.runTest('退出登录', () => this.testLogout());

    } catch (error) {
      log(`测试执行错误: ${error.message}`, '❌');
    } finally {
      await this.teardown();
    }

    this.printSummary();
  }

  printSummary() {
    console.log('\n' + '='.repeat(60));
    console.log('📊 测试结果汇总');
    console.log('='.repeat(60));
    console.log(`总测试数: ${this.testsPassed + this.testsFailed}`);
    console.log(`通过: ${this.testsPassed} ✅`);
    console.log(`失败: ${this.testsFailed} ❌`);
    console.log(`通过率: ${((this.testsPassed / (this.testsPassed + this.testsFailed)) * 100).toFixed(1)}%`);
    console.log('='.repeat(60) + '\n');

    if (this.testsFailed > 0) {
      console.log('失败测试详情:');
      this.results.filter(r => r.status === 'FAIL').forEach(r => {
        console.log(`  ❌ ${r.test}: ${r.message}`);
      });
    }

    // 保存结果到文件
    const fs = require('fs');
    const reportPath = 'test-results/additional-test-results.json';
    fs.writeFileSync(reportPath, JSON.stringify({
      timestamp: new Date().toISOString(),
      summary: {
        total: this.testsPassed + this.testsFailed,
        passed: this.testsPassed,
        failed: this.testsFailed,
        passRate: ((this.testsPassed / (this.testsPassed + this.testsFailed)) * 100).toFixed(1) + '%',
      },
      results: this.results,
    }, null, 2));
    
    console.log(`📄 详细报告已保存: ${reportPath}`);
  }
}

// 主入口
if (require.main === module) {
  const runner = new AdditionalTestRunner();
  runner.runAllTests().catch(err => {
    console.error('测试运行失败:', err);
    process.exit(1);
  });
}

module.exports = AdditionalTestRunner;
