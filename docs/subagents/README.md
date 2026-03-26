# SubAgent Memory Docs

这些文档只定义职责和接口，不承载实现代码。

## Shared Rules

- 所有 SubAgent 共享同一套 `TaskState`、`AgentAction`、`PatchCandidate` 和日志字段。
- 任何跨模块字段变更，先改本文档，再改各自记忆文档和实现。
- 所有模型、数据和实验输出统一遵循 `/Data/public` 与项目配置的路径约定。
- Environment Agent 只负责执行事实，Orchestrator Agent 只负责决策，Evaluation Agent 不参与在线决策。

## Shared State Contract

- `issue_id`: 当前任务唯一标识
- `budget_remaining`: 剩余决策预算
- `located_files`: 当前定位出的文件集合
- `patch_candidates`: 候选补丁列表
- `tests_passed`: 是否通过测试
- `failure_count`: 测试失败轮数
- `uncertainty`: 当前修复不确定性
- `review_notes`: reviewer 输出
- `reflection_notes`: reflector 输出

## Logging Rules

- 记录开始时间、配置、动作序列、每步 reward 分解、最终状态。
- 每次运行保存 `trajectory.json` 和 `summary.json`。
- 显存、内存和数据路径检查在运行日志里留痕。

