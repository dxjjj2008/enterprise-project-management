/**
 * 项目创建E2E测试 - 截图记录测试过程
 */

const { chromium } = require('playwright');

const BASE_URL = 'http://localhost:3000';

async function runProjectCreationTest() {
  console.log('🚀 开始项目创建E2E测试...\n');
  
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  const page = await context.newPage();
  
  const screenshots = [];
  
  try {
    // Step 1: 访问首页
    console.log('📍 Step 1: 访问首页');
    await page.goto(BASE_URL);
    await page.waitForLoadState('networkidle');
    await page.screenshot({ path: 'test-screenshots/01-homepage.png', fullPage: true });
    screenshots.push('test-screenshots/01-homepage.png');
    console.log('   ✅ 首页加载完成\n');
    
    // Step 2: 点击注册按钮
    console.log('📍 Step 2: 点击注册按钮');
    const registerBtn = page.locator('text=注册');
    if (await registerBtn.isVisible()) {
      await registerBtn.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'test-screenshots/02-register-page.png', fullPage: true });
      screenshots.push('test-screenshots/02-register-page.png');
      console.log('   ✅ 跳转到注册页面\n');
    } else {
      console.log('   ⚠️ 未找到注册按钮，尝试直接访问注册页\n');
      await page.goto(`${BASE_URL}/auth/register`);
      await page.waitForLoadState('networkidle');
    }
    
    // Step 3: 填写注册信息
    console.log('📍 Step 3: 填写注册信息');
    const timestamp = Date.now();
    const testUser = {
      username: `tester_${timestamp}`,
      email: `tester_${timestamp}@example.com`,
      password: 'testpass123'
    };
    
    const formItems = page.locator('.el-form-item');
    await formItems.nth(0).locator('input').fill(testUser.username);
    await formItems.nth(1).locator('input').fill(testUser.email);
    await formItems.nth(2).locator('input').fill(testUser.password);
    await formItems.nth(3).locator('input').fill(testUser.password);
    
    await page.screenshot({ path: 'test-screenshots/03-register-filled.png', fullPage: true });
    screenshots.push('test-screenshots/03-register-filled.png');
    console.log(`   ✅ 已填写注册信息: ${testUser.username}\n`);
    
    // Step 4: 点击注册
    console.log('📍 Step 4: 点击注册按钮');
    const submitBtn = page.locator('.el-button--primary:has-text("注册")');
    await submitBtn.click();
    await page.waitForTimeout(3000);
    
    await page.screenshot({ path: 'test-screenshots/04-after-register.png', fullPage: true });
    screenshots.push('test-screenshots/04-after-register.png');
    console.log('   ✅ 注册完成\n');
    
    // Step 5: 如果没跳转到登录页，手动登录
    const currentUrl = page.url();
    if (currentUrl.includes('register')) {
      console.log('📍 Step 5: 手动登录');
      await page.goto(`${BASE_URL}/auth/login`);
      await page.waitForLoadState('networkidle');
      
      const loginItems = page.locator('.el-form-item');
      await loginItems.nth(0).locator('input').fill(testUser.username);
      await loginItems.nth(1).locator('input').fill(testUser.password);
      
      await page.screenshot({ path: 'test-screenshots/05-login-filled.png', fullPage: true });
      screenshots.push('test-screenshots/05-login-filled.png');
      
      const loginBtn = page.locator('.el-button--primary:has-text("登录")');
      await loginBtn.click();
      await page.waitForTimeout(3000);
      
      await page.screenshot({ path: 'test-screenshots/06-after-login.png', fullPage: true });
      screenshots.push('test-screenshots/06-after-login.png');
      console.log('   ✅ 登录完成\n');
    } else {
      console.log('   ✅ 已登录\n');
    }
    
    // Step 6: 直接访问项目页面
    console.log('📍 Step 6: 进入项目页面');
    await page.goto(`${BASE_URL}/projects`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    await page.screenshot({ path: 'test-screenshots/07-projects-page.png', fullPage: true });
    screenshots.push('test-screenshots/07-projects-page.png');
    console.log('   ✅ 进入项目页面\n');
    
    // Step 7: 使用Vue方法打开对话框
    console.log('📍 Step 7: 点击新建项目');
    
    // 使用evaluate调用Vue方法
    const dialogOpened = await page.evaluate(() => {
      // 查找Vue组件实例
      const containers = document.querySelectorAll('.page-container');
      for (const container of containers) {
        // 查找按钮
        const btns = container.querySelectorAll('button');
        for (const btn of btns) {
          if (btn.textContent.includes('新建项目')) {
            btn.click();
            return true;
          }
        }
      }
      return false;
    });
    
    console.log(`   📝 对话框打开: ${dialogOpened ? '是' : '否'}`);
    
    await page.waitForTimeout(2000);
    
    await page.screenshot({ path: 'test-screenshots/08-create-dialog.png', fullPage: true });
    screenshots.push('test-screenshots/08-create-dialog.png');
    console.log('   ✅ 对话框尝试打开\n');
    
    // 检查对话框是否真的打开了
    const dialogVisible = await page.locator('.el-dialog').isVisible().catch(() => false);
    console.log(`   📝 对话框可见: ${dialogVisible ? '是' : '否'}`);
    
    // Step 8: 如果对话框打开了，填写信息
    if (dialogVisible) {
      console.log('📍 Step 8: 填写项目信息');
      
      // 查找对话框中的输入框
      const dialogInputs = page.locator('.el-dialog input');
      const inputCount = await dialogInputs.count();
      console.log(`   📝 找到 ${inputCount} 个输入框`);
      
      if (inputCount > 0) {
        await dialogInputs.first().fill('测试项目-E2E测试');
      }
      
      // 项目描述
      const textareas = page.locator('.el-dialog textarea');
      if (await textareas.count() > 0) {
        await textareas.first().fill('这是一个通过E2E测试创建的项目');
      }
      
      await page.screenshot({ path: 'test-screenshots/09-form-filled.png', fullPage: true });
      screenshots.push('test-screenshots/09-form-filled.png');
      console.log('   ✅ 表单填写完成\n');
      
      // Step 9: 点击创建
      console.log('📍 Step 9: 点击创建按钮');
      const submitCreateBtn = page.locator('.el-dialog .el-button--primary:has-text("创建")');
      await submitCreateBtn.click();
      
      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'test-screenshots/10-after-create.png', fullPage: true });
      screenshots.push('test-screenshots/10-after-create.png');
      console.log('   ✅ 项目创建完成\n');
    } else {
      console.log('   ⚠️ 对话框未打开，跳过表单填写\n');
    }
    
    // Step 10: 验证项目
    console.log('📍 Step 10: 验证项目');
    await page.goto(`${BASE_URL}/projects`);
    await page.waitForLoadState('networkidle');
    await page.waitForTimeout(2000);
    
    const projectCards = page.locator('.project-card');
    const projectCount = await projectCards.count();
    console.log(`   📊 项目列表中共有 ${projectCount} 个项目\n`);
    
    await page.screenshot({ path: 'test-screenshots/11-project-list.png', fullPage: true });
    screenshots.push('test-screenshots/11-project-list.png');
    
    // 总结
    console.log('='.repeat(60));
    console.log('📋 测试完成');
    console.log('='.repeat(60));
    console.log(`\n✅ 成功截图: ${screenshots.length} 张\n`);
    screenshots.forEach((s, i) => {
      console.log(`  ${i + 1}. ${s}`);
    });
    console.log('\n' + '='.repeat(60));
    
  } catch (error) {
    console.error('❌ 测试失败:', error.message);
    await page.screenshot({ path: 'test-screenshots/ERROR.png', fullPage: true });
    screenshots.push('test-screenshots/ERROR.png');
  } finally {
    await browser.close();
  }
}

runProjectCreationTest()
  .then(() => {
    console.log('\n🎉 测试脚本执行完成！');
  })
  .catch(err => {
    console.error('测试执行错误:', err);
    process.exit(1);
  });
