# 前端测试示例

本目录包含前端组件的测试文件。

## 测试文件命名规范

- 文件名: `*.test.js` 或 `*.test.ts`
- 位置: 与被测组件同一目录

## 运行测试

```bash
# 运行所有测试
npm test

# 运行并显示详细信息
npm run test:run

# 运行并生成覆盖率报告
npm run test:coverage
```

## 现有测试文件

| 文件 | 测试组件 | 状态 |
|------|---------|------|
| `dashboard/Index.test.js` | 仪表盘页面 | ✅ 示例 |
| `tasks/Board.test.js` | 任务看板 | ✅ 示例 |

## 覆盖率报告

运行 `npm run test:coverage` 后，覆盖率报告生成在 `coverage/` 目录。

打开 `coverage/index.html` 查看详细报告。

## 添加新测试

1. 创建测试文件: `YourComponent.test.js`
2. 导入依赖:
   ```javascript
   import { describe, it, expect } from 'vitest'
   import { mount } from '@vue/test-utils'
   ```
3. 编写测试用例
4. 运行 `npm test` 验证

## 最佳实践

- 每个功能模块至少一个测试
- 测试用户可见行为，而非实现细节
- 保持测试独立，避免相互依赖
- 使用有意义的测试名称
