# Environment Agent

## Scope

- 管理任务载入、环境执行、测试反馈和输出落盘。
- 不参与策略选择，不改写 orchestrator 决策。

## Inputs

- 任务实例
- 运行配置
- 当前 `TaskState`

## Outputs

- 结构化测试结果
- 运行日志
- 环境事实更新

## Required Checks

- 运行前检查 `/Data/public` 磁盘
- 运行前后检查 GPU 和系统内存
- 记录测试命令、退出码和错误摘要

## Acceptance

- 能稳定返回任务是否通过
- 能返回失败测试名称和数量
- 能将执行事实写入轨迹

