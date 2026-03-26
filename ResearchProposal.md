# Dynamic Topology and Learnable Orchestration for Multi-Agent Code Repair

## 1. Summary

本项目聚焦一个明确且有研究价值的问题：如何让多智能体系统从“静态 SOP + 固定拓扑”演进为“基于 RL 的动态拓扑与可学习编排”，并在代码修复任务中实现性能与成本的联合优化。

结合现有调研结果，第一版不建议直接复刻单一已有框架，而是采用“开源工作为基线思想 + 新项目干净实现”的策略：

- 编排层参考 `Multi-Agent Collaboration via Evolving Orchestration (Puppeteer)`，把“调用谁、何时反思、何时早停”建模为策略学习问题。
- 任务层参考 `MAGIS`，将代码修复流程拆为 `manager / locator / developer / reviewer / tester` 等角色。
- 反思层借鉴 `COPPER`，把 reflection / critique 视为可训练、可归因的模块，而不是纯 prompt 技巧。
- 聚合层借鉴 `Mixture-of-Agents`，只在高不确定场景触发多候选 patch 聚合，避免无差别并行调用。

第一版的目标不是做一个“更复杂的 ChatDev 变体”，而是做一个可复现、可度量、可消融、可扩展到论文的研究原型：

> 在 `SWE-bench Lite` 上学习一个预算感知的动态编排器，在尽量减少 token / 调用轮数 / 无效通信的同时，提高真实代码修复成功率。

## 2. Core Research Hypothesis

核心假设如下：

1. 静态多智能体 SOP 在代码修复这类长程任务中存在明显冗余，尤其表现为重复定位、无效 review、过晚终止和低价值反思。
2. 如果把系统级编排建模为策略优化问题，那么 agent 拓扑可以按任务难度、当前进展和预算动态演化，而不必固定为线性链路。
3. 如果进一步把 reflection / peer review 纳入反事实信用分配，系统可以学习“哪些反思值得触发、哪些 reviewer 真的有贡献”，从而使反思模块从启发式组件变为可进化组件。

对应的论文方向可以定义为：

**Dynamic Topology for Budgeted Multi-Agent Code Repair**

副标题建议：

**RL-based orchestration with counterfactual reflection credit and cost-aware patch ensembling**

## 3. Why This Direction

相较于直接沿用 MetaGPT、ChatDev 这类静态协作流程，本方向更有突破性，原因有三点：

- 它把“系统结构”本身变成学习对象，而不只优化单个 agent prompt。
- 它天然允许多目标优化，能够显式权衡 `resolved rate` 与 `token/API cost`。
- 它能把“反思、互评、聚合、早停”这些通常写死的工程规则，统一纳入策略与信用分配框架。

第一版选择代码修复而不是 GUI/Web，有两个现实优势：

- 基准与成功信号更清晰：是否通过测试、是否生成有效 patch，便于做 RL 奖励设计。
- 开源复现条件更成熟：`SWE-bench`、`MAGIS`、代码修复类 agent baseline 已经较完整。

## 4. Chosen Baselines and How We Will Build on Them

### 4.1 Baseline A: MAGIS

`MAGIS` 提供了很合适的任务骨架：将代码修复拆成规划、定位、编码、验证等角色。这一框架适合作为静态基线和行为数据采集器。

我们不直接复刻其整体工程，而是吸收其角色职责：

- `Manager`: 读取 issue，规划修复路线。
- `Locator`: 定位相关文件、函数、调用链和报错上下文。
- `Developer`: 生成和更新 patch。
- `Reviewer`: 从语义、风格和潜在副作用上审查 patch。
- `Tester`: 执行测试并将失败信号结构化返回。

### 4.2 Baseline B: Puppeteer / Evolving Orchestration

`Puppeteer` 的关键贡献是证明“编排器即策略”是成立的：中心化 orchestrator 可以动态决定下一步调用哪个 agent，以及何时终止。

本项目将把这一思想从通用推理任务迁移到代码修复场景，并做三点扩展：

- 从简单性能奖励扩展为 `成功率 + 测试改进 + 成本惩罚 + 冗余惩罚 + 提前终止奖励` 的多目标 reward。
- 将动作空间从“选择 agent”扩展到“选择 agent + 是否触发 reflection + 是否触发 patch ensemble + 是否 terminate”。
- 将静态角色编排提升为动态拓扑搜索，即允许任务在不同阶段形成不同的局部协作图。

### 4.3 Baseline C: COPPER

`COPPER` 最值得吸收的不是具体训练代码，而是“共享反思器 + 反事实信用分配”的思想。

本项目中，reviewer / reflector 不应只被当作固定中间步骤，而应被视为可学习的高成本决策节点。系统要学会：

- 什么情况下值得触发反思；
- 哪种反思真的提升了后续 patch；
- 哪些 review 只是增加 token 成本而没有贡献。

### 4.4 Baseline D: Mixture-of-Agents

`MoA` 提供了一个重要启发：多智能体集成的价值不在于“永远并行调用更多模型”，而在于“只在不确定性高时，让多候选互相提供互补视角”。

因此本项目不会默认让多个 coder 并行生成 patch，而会把 patch ensemble 视为一种受预算约束的动作，仅在以下情形触发：

- 当前 patch 置信度低；
- 多轮修复失败；
- reviewer 给出相互冲突的意见；
- 测试反馈显示修复方向可能偏离。

## 5. First-Version Task Definition

第一版任务固定为：

- 环境：`SWE-bench Lite`
- 任务：给定 GitHub issue 和仓库快照，生成 patch 并运行测试验证
- 评价目标：
  - 最大化 `resolved rate`
  - 最小化平均 token 消耗
  - 最小化平均 agent 调用轮数
  - 减少重复调用与无效反思

范围控制：

- 第一版只做 Python 项目
- 第一版先跑 Lite 子集，不直接追求全量 Verified
- 第一版以本地开源模型为主，不依赖闭源 API 才能复现主结果

## 6. Models and Datasets to Download

所有模型和数据集统一放在 `/Data/public`。

### 6.1 Models

建议下载如下模型组合：

- 主 coder：`Qwen2.5-Coder-7B-Instruct`
- 强 coder / reranker：`Qwen2.5-Coder-14B-Instruct`
- reviewer / reflector / judge：`Qwen2.5-7B-Instruct`
- embedding 检索模型：`bge-small-en-v1.5`

模型选择依据：

- 7B/14B 组合在本机多卡 L20 环境下容易部署和并行调度。
- 第一版重点是验证“动态编排是否成立”，而不是追求最大模型上限。
- 本地开源模型更符合后续 RL 微调与复现要求。

### 6.2 Datasets

建议下载：

- `SWE-bench/SWE-bench_Lite`
- `SWE-bench/SWE-bench_Verified`
- 可选：`princeton-nlp/SWE-bench_oracle`
- 可选：`princeton-nlp/SWE-bench_bm25_13K`

此外，项目会自生成以下研究数据：

- 静态编排轨迹
- 动态编排轨迹
- reward 分解日志
- 失败模式标签
- patch candidate 排名记录

## 7. Training Formulation

### 7.1 State

编排器观测到的状态 `TaskState` 需要至少包含：

- issue 描述与历史摘要
- 当前候选文件与定位置信度
- 已尝试 patch 的数量与结果
- 最近测试失败类型
- 当前剩余预算
- 最近调用过的 agent 序列
- 当前 patch quality score
- reviewer / reflector 是否已触发

### 7.2 Action

动作空间定义为：

- `invoke_manager`
- `invoke_locator`
- `invoke_developer`
- `invoke_reviewer`
- `invoke_reflector`
- `invoke_tester`
- `invoke_ensemble`
- `terminate`

### 7.3 Reward

第一版 reward 采用显式加权方案：

`R = resolve_reward + test_improvement + patch_quality + early_stop_bonus - token_cost - call_cost - redundancy_penalty`

其中：

- `resolve_reward`：测试全部通过时给予高奖励
- `test_improvement`：失败用例数减少时给予中间奖励
- `patch_quality`：patch 能成功应用、修改位置合理时给予小奖励
- `early_stop_bonus`：在明显无望时节制终止而不是无限尝试
- `token_cost`：总 token 消耗惩罚
- `call_cost`：agent 调用次数惩罚
- `redundancy_penalty`：连续重复低价值调用时惩罚

### 7.4 Learning Schedule

第一版训练采用三阶段：

#### Phase 1: Static Trace Collection

先实现一个 `MAGIS-lite` 固定拓扑基线，采集轨迹、token、patch、测试反馈和失败原因。

#### Phase 2: Warm Start

用静态轨迹做 behavior cloning 或 preference warm start，避免 PPO 从纯随机策略开始。

#### Phase 3: RL Fine-Tuning

在有限子集上做 PPO 微调，让 orchestrator 学习：

- 何时跳过 reviewer
- 何时优先回到 locator
- 何时切换 developer 策略
- 何时触发 ensemble
- 何时 terminate

## 8. Reflection and Counterfactual Credit

这是第一版最有论文价值的增强点。

通常代码 agent 系统里的 reflection 是一个写死的步骤，但本项目中我们把它设计成需要被验证价值的动作。

核心设计：

- `Reviewer` 输出对 patch 的结构化批评。
- `Reflector` 输出更高层的策略修正建议，例如“问题出在文件定位而不是 patch 细节”。
- 系统记录启用与不启用 reflection 时，后续 patch 质量和测试进展的差异。

第一版先采用近似的反事实信用分配：

- 留一法 ablation：比较“跳过当前 reflection”与“使用当前 reflection”后的轨迹收益差
- learned value baseline：用价值网络估计期望收益，降低方差

后续如果第一版有效，再升级为更严格的 counterfactual PPO。

## 9. Cost-Aware Patch Ensembling

项目中的 `ensemble` 不是一个永远开启的模块，而是一个预算感知动作。

设计原则：

- 正常情况下，单 patch 流程优先，减少冗余生成。
- 只有高不确定时，才让多个 coder / 多种 prompt 生成候选 patch。
- 之后由 `PatchEnsembler` 结合 reviewer 信号、测试反馈和置信度进行 rerank。

这样可以把 `MoA` 的思想转化为更节制的“按需集成”，而不是固定多模型并发。

## 10. Failure Taxonomy

为了让系统不只是“跑通”，还真正可研究，建议第一版同时建立一套轻量失败分类体系，参考 `MAST` 的思想但贴合代码修复任务。

建议记录以下失败类型：

- 重复定位：反复在同一文件或同一区域搜索
- 错误验证：reviewer 错误放行明显无效 patch
- 过度反思：reflection 很长但没有实质帮助
- 错误早停：在仍有明显修复空间时提前终止
- 无效 ensemble：生成多个 patch 但无优于单 patch 的收益
- 任务脱轨：修复方向偏离 issue 目标

这些标签将用于：

- 后续 reward 调整
- 失败可视化
- 策略演化分析
- 论文中的 case study

## 11. Project Code Framework

建议项目框架如下：

```text
ResearchProposal.md
configs/
scripts/
src/dyco_repair/
src/dyco_repair/types.py
src/dyco_repair/agents/
src/dyco_repair/orchestrator/
src/dyco_repair/envs/
src/dyco_repair/retrieval/
src/dyco_repair/reflection/
src/dyco_repair/credit/
src/dyco_repair/ensemble/
src/dyco_repair/eval/
src/dyco_repair/logging/
tests/
```

建议首先固定这些核心接口：

- `TaskState`
- `AgentAction`
- `Transition`
- `RewardBreakdown`
- `PatchCandidate`
- `OrchestratorPolicy.select(state) -> AgentAction`
- `Agent.run(observation) -> AgentResult`
- `BudgetController.should_stop(state) -> bool`
- `PatchEnsembler.rank(candidates) -> list[PatchCandidate]`

## 12. SubAgent Collaboration Plan

第一版本构建建议拆成 5 个并行 SubAgents，主控 agent 负责集成。

### SubAgent 1: Environment Agent

职责：

- 集成 `SWE-bench Lite`
- 拉起仓库快照
- 运行测试并解析结果
- 统一日志与输出协议

交付：

- `src/dyco_repair/envs/`
- `scripts/run_instance.py`
- 测试结果标准化结构

### SubAgent 2: Static Baseline Agent

职责：

- 实现 `MAGIS-lite` 固定流程
- 定义角色 prompt
- 采集静态轨迹

交付：

- `src/dyco_repair/agents/`
- `src/dyco_repair/ensemble/basic_ranker.py`
- 静态 baseline 运行脚本

### SubAgent 3: Orchestrator Agent

职责：

- 设计状态表示
- 定义动作空间
- 实现预算控制与 terminate 逻辑
- 编写 BC / PPO 训练入口

交付：

- `src/dyco_repair/orchestrator/`
- `configs/orchestrator/*.yaml`
- 编排训练脚本

### SubAgent 4: Reflection Agent

职责：

- 实现 reviewer / reflector
- 设计反事实近似信用分配
- 输出失败标签和反思收益分析

交付：

- `src/dyco_repair/reflection/`
- `src/dyco_repair/credit/`
- trajectory annotator

### SubAgent 5: Evaluation Agent

职责：

- 统一度量 resolved rate、token、调用轮数、冗余率
- 做 ablation
- 生成图表、表格和案例分析

交付：

- `src/dyco_repair/eval/`
- `src/dyco_repair/logging/`
- 汇总报告脚本

## 13. Acceptance Criteria for V1

第一版完成的标准不是“做到最强”，而是满足以下研究闭环：

1. 能在 `SWE-bench Lite` 子集上稳定跑通端到端流程。
2. 有一个固定拓扑静态基线可作为对照组。
3. 有一个可训练的动态 orchestrator，能根据状态选择下一步 agent。
4. 能记录 token 成本、调用轮数、patch 演化和测试反馈。
5. 至少完成以下一组有效对比：
   - 静态 SOP vs 动态 orchestrator
   - 有 reflection vs 无 reflection
   - 有 ensemble vs 无 ensemble
   - 有 cost penalty vs 无 cost penalty
6. 至少在以下一项指标上优于静态基线：
   - `resolved rate`
   - 平均 token 成本
   - 平均 agent 调用轮数

## 14. Implementation Notes

结合当前机器条件，建议实现时采用以下默认策略：

- 优先部署 7B/14B 模型，避免大模型基础设施先成为瓶颈
- 所有模型和数据下载路径固定到 `/Data/public`
- 每次运行都记录日志、显存、内存、输出目录和最终状态
- 先构建少量样本的稳定 pipeline，再扩展样本规模
- 先保证数据闭环和可分析性，再追求大规模 RL 训练

## 15. Final Positioning

这个项目的亮点不在于“又做了一个多 agent 系统”，而在于明确回答以下问题：

- 多智能体的协作拓扑能否像策略一样被学习？
- reflection / critique 能否从启发式模块变成可归因、可优化组件？
- 多模型集成能否从固定并行变成预算感知的按需调用？
- 在真实代码修复任务中，动态编排是否能带来可测的性能-成本优势？

如果第一版闭环成功，后续可以自然扩展到：

- `SWE-bench Verified`
- 更强 coder 模型
- 更严格的 counterfactual PPO
- MAST 风格失败建模
- GUI/Web/code 三类任务统一的动态编排框架
