/**
 * 入门示例测试
 * 
 * 简单演示 Vitest 基本用法
 */

import { describe, it, expect } from 'vitest'

describe('入门示例', () => {
  it('1 + 1 应该等于 2', () => {
    expect(1 + 1).toBe(2)
  })

  it('数组应该能正确添加元素', () => {
    const arr = [1, 2, 3]
    arr.push(4)
    expect(arr).toEqual([1, 2, 3, 4])
  })

  it('字符串应该能正确拼接', () => {
    const str = 'Hello' + ' ' + 'World'
    expect(str).toBe('Hello World')
  })

  it('对象应该能正确比较', () => {
    const obj = { name: 'test', value: 42 }
    expect(obj).toHaveProperty('name')
    expect(obj.name).toBe('test')
  })
})

describe('条件测试', () => {
  it('真值判断', () => {
    expect(true).toBeTruthy()
    expect(false).toBeFalsy()
  })

  it('数字比较', () => {
    expect(10).toBeGreaterThan(5)
    expect(3).toBeLessThan(7)
    expect(5).toBe(5)
  })

  it('数组包含检查', () => {
    const fruits = ['apple', 'banana', 'orange']
    expect(fruits).toContain('banana')
    expect(fruits).not.toContain('grape')
  })
})
