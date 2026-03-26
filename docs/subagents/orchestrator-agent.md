# Orchestrator Agent

## Scope

- 根据 `TaskState` 决定下一步动作。
- 管理预算、早停、ensemble 触发和 reflection 触发。

## Action Space

- `invoke_manager`
- `invoke_locator`
- `invoke_developer`
- `invoke_reviewer`
- `invoke_reflector`
- `invoke_tester`
- `invoke_ensemble`
- `terminate`

## Required Fields

- 状态空间定义
- 动作合法性约束
- 奖励拆分
- 早停规则
- 决策理由记录

## Boundaries

- 不直接运行测试
- 不直接修改 patch 内容

