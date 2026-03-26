# Static Baseline Agent

## Scope

- 实现固定拓扑的 `MAGIS-lite` 基线。
- 负责采集静态 SOP 轨迹，作为动态编排的对照组。

## Flow

`manager -> locator -> developer -> reviewer -> tester`

## Required Outputs

- 固定流程轨迹
- 候选 patch
- baseline 成功率和成本统计

## Boundaries

- 不训练策略
- 不修改环境执行逻辑

