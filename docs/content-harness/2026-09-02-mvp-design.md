# 设计文档：Content Harness MVP

**日期**：2026-09-02

**最近修订**：2026-09-08

**状态**：待实现

**产品名**：Content Harness

**CLI / Python 包**：`content-harness`

**目标仓库工作名**：`content-workflow-harness`

**首个场景**：有事实依据的中文公众号长文

**产品形态**：Agent Skills + 本地内容工作区 + 最小状态 CLI

---

## 结论

这个方向值得做。名称采用 **Content Harness**：它比 Content Superpowers 更准确地表达“给 Agent 提供流程、工具、状态和门禁”的产品本质，也减少对 Superpowers 品牌的依附。

用户提出的 `conteng-harness` 应修正为 `content-harness`。截至 2026-09-08，GitHub 已存在多个同名仓库，[其中一个](https://github.com/JayAI623/content-harness)也定位为 agentic content pipeline，[另一个模板项目](https://github.com/evercrisp-ai-org/content-harness-template)同样使用内容生产 harness 概念；因此产品名和 CLI 保留 `content-harness`，开源仓库暂用更易区分的 `content-workflow-harness`。正式发布前重新检查 GitHub、PyPI、npm 和商标占用。

MVP 不做 Web 平台，也不是已有内容 skill 的二次编排壳。它从新的目标出发，独立实现完成一篇内容所需的工作流能力。

MVP 要解决的是普通“提示词生成文章”没有稳定解决的工程问题：

1. 每一步产出了什么，能否回查；
2. 上游内容被修改后，哪些下游结果已经失效；
3. 关键事实是否真的被来源支持；
4. AI 中断、换客户端或用户手改后，能否安全续做；
5. 发布前是否经过了不可绕过的人类确认；
6. 能否用可重复实验证明工作流确实改善了结果。

因此，Content Harness 的核心是一套**独立的内容生产技能、内容资产协议、质量门禁和可恢复执行内核**。

---

## 新目标与设计原则

Content Harness 是一个可独立安装、独立测试、独立开源的产品。它不调用、不安装、不要求用户拥有 `kj-skills`，也不把 `kj-skills` 中的大型 skill 拆名后复制过来。

新实现遵守以下原则：

1. **端到端独立**：从想法、调研、选题、提纲、正文、配图、评审到发布包，都由 Content Harness 自己的 skill 和模板完成；
2. **单一职责**：每个 skill 只负责一类资产，输入、输出和完成条件明确；
3. **确定性下沉**：哈希、依赖、链接、状态、审批和恢复交给 CLI，避免用提示词模拟状态机；
4. **项目无关**：核心不认识康健、`kj-llm-wiki` 或任何公众号账号；
5. **配置接入**：具体项目只通过 project profile 声明可读材料、去重范围、输出路径和写入权限；
6. **本地优先**：内容与状态默认保存在用户文件系统，可直接审阅、修改、Git 管理和迁移；
7. **先完成一条窄链路**：MVP 只把中文公众号长文做通，不同时覆盖短视频、小红书、课程和知识星球。

---

## MVP 成功定义

MVP 完成后，用户可以在 Codex、Claude Code 或其他支持 Agent Skills 的客户端里输入：

> 把“为什么学了很多 AI，工作方式还是没改变”做成一篇有事实依据的公众号文章。

Agent 将：

1. 创建一个独立内容运行目录；
2. 保存原始想法、来源、选题简报、提纲、正文和评审结果；
3. 在“选题简报确认”和“发布确认”两个位置明确停下来等待用户；
4. 用户或 Agent 修改上游资产时，将受影响的下游资产标记为 `stale`；
5. 中断或换客户端后，从磁盘状态继续，而不是依赖对话记忆；
6. 通过事实、编辑、发布三类门禁后生成公众号发布包；
7. 默认不自动发布；发布 integration 存在时，也必须使用带内容摘要的显式审批；
8. 按需选择公众号高传播、去 AI 味等风格，并能随时关闭或回到默认表达；
9. 发布后记录回执和指标，并生成可用于下一篇的复盘。

### MVP 不承诺

- 不承诺一套流程适合所有内容平台；
- 不承诺自动生成的内容一定优于人工内容；
- 不承诺 Agent Skills 在不同客户端中的行为天然一致；
- 不用 10 篇文章直接证明阅读量增长来自工作流；
- 不在 MVP 阶段建设多人协作、云端数据库、可视化后台或插件市场。

---

## 工具到底由什么组成

答案不是简单的“CLI + Skills”，而是四个协作部分：

| 部分 | 负责什么 | 不负责什么 |
|---|---|---|
| Agent Skills | 调研、判断、写作、评审、配图规划等需要模型理解的工作 | 不保存隐式状态，不自行越过审批 |
| CLI | 创建 run、计算哈希、推导依赖、执行门禁、记录审批、恢复状态 | 不写文章，不决定观点 |
| Workspace | 保存每次内容任务的输入、过程资产、状态和结果 | 不依赖某次对话上下文 |
| Workflow Pack / Project Profile | 定义内容类型 DAG，以及项目的读取和输出边界 | 不包含账号凭据和个人专属写作 skill |

数据流是：

```text
用户提出内容目标
  → Router Skill 查询 CLI 状态
  → 选择一个阶段 Skill 生成或修改资产
  → CLI 检查资产、记录哈希并推进 DAG
  → 到达人工 Gate 后停止
  → 所有 Gate 通过后导出到项目约定路径
```

## 通用使用方式

### 第一次使用

MVP 实现后的安装契约：

```bash
uv tool install content-harness
content-harness install-skills --client codex
content-harness doctor
```

`install-skills` 只安装 Content Harness 自带的 skills。`doctor` 检查 CLI、skill 发现、Python 环境和项目写权限，不访问用户内容。

在任意内容项目中初始化：

```bash
cd /path/to/content-project
content-harness init . --workflow wechat-longform
```

该命令创建 `.content-harness/project.yaml`、`author-profile.md` 模板和运行目录，不生成文章。用户确认作者资料后，`doctor` 才允许开始首个 run。

### 新建文章

用户在 Agent 客户端里用自然语言下达任务。Agent 在内部执行：

```bash
content-harness new ai-learning-workflow --workflow wechat-longform
```

创建后，所有过程资产位于：

```text
<project>/.content-harness/runs/2026-09-08-ai-learning-workflow/
```

随后用户主要与 Agent 对话：

> 使用 Content Harness，把“为什么学了很多 AI，工作方式还是没改变”做成公众号长文。先做到选题简报，等我确认。

### 中断后继续

```bash
content-harness resume 2026-09-08-ai-learning-workflow
content-harness status 2026-09-08-ai-learning-workflow
```

`resume` 返回当前可继续的任务、阻塞原因和已失效资产，但不自行重写用户文件。

### 审批选题或发布

```bash
content-harness approve 2026-09-08-ai-learning-workflow brief
content-harness approve 2026-09-08-ai-learning-workflow publish
```

审批记录绑定被审批资产的内容哈希。审批后若资产发生改变，原审批自动失效。

### Agent 与 CLI 的关系

- 用户主要通过自然语言与 Agent 交互；
- Agent Skills 负责判断下一步、执行本项目内置的专业能力并解释结果；
- CLI 只负责确定性的状态变更、检查、审批和恢复；
- CLI 不负责生成正文，也不内置作者风格。

---

## 总体架构

```text
用户自然语言
  ↓
Agent Skill 编排层
  ├─ 运行 Content Harness 内置的阶段 skill
  └─ 调用 content-harness CLI 读写确定性状态
       ↓
本地内容工作区
  ├─ manifest.yaml        运行状态与资产索引
  ├─ transitions.jsonl   追加式状态事件
  ├─ approvals.jsonl     追加式人工审批
  └─ artifacts/          可读、可编辑、可版本检查的内容资产
       ↓
Workflow Pack
  └─ 定义公众号长文所需资产、依赖和 Gate
       ↓
Project Profile
  └─ 将最终资产导出到当前项目约定的位置
```

### 核心与项目配置边界

| Content Harness 核心 | Project Profile |
|---|---|
| 内置阶段 Skills | 可读素材根目录 |
| 资产协议与 JSON Schema | 查重目录 |
| 依赖、版本和失效传播 | 成稿与图片输出路径 |
| 确定性、语义和人工门禁 | 项目级禁写目录 |
| 审批、恢复和发布幂等协议 | 发布能力是否启用 |
| 测试夹具与评估框架 | 项目自己的作者资料 |

核心不得硬编码作者名字、本机绝对路径、账号配置或私有内容。Project Profile 只是数据和权限映射，不允许通过配置导入 `kj-skills`。

---

## 工作流不是线性状态机，而是 Artifact DAG

内容创作会反复修改。只保存一个 `current_stage` 会把“做到哪一步”和“哪些结果仍有效”混在一起，无法可靠恢复。

MVP 使用资产依赖图：

```text
idea ───────────────────────→ brief ─────→ style-spec ─────→ outline
 └─→ sources ─────→ claims ────┘                                │
brief + outline + claims + style-spec ──────────────────────────┴─→ draft
draft + style-spec ─────→ manuscript
                              ├─→ editorial-review
claims ───────────────────────┴─→ fact-review
reviews passed + manuscript ─────→ visual-plan ─────→ visual-assets
brief + manuscript + reviews + visual-assets ─────────→ publish-package
                                                                  │
                                               human publish approval
                                                                  │
                                                           publish-receipt
                                                                  │
                                                               metrics
                                                                  │
                                                            retrospective
```

`style-spec` 始终存在，但允许 `scene: []`、`polish: []`，表示本次除作者资料和 `neutral` 基础规则外，不使用额外的场景或润色风格。`draft` 同时直接依赖已批准的 `brief`、`outline`、`claims` 和 `style-spec`：`brief` 保留目标读者、核心判断和边界，`outline` 负责文章结构，`claims` 负责事实边界，`style-spec` 负责表达策略。`manuscript` 是经过可选风格处理后的评审对象；未启用额外风格时，它只进行格式归一并接收 `draft`，不做语义改写。

### 资产清单

| 资产 ID | 默认文件 | 主要依赖 |
|---|---|---|
| `idea` | `artifacts/00-idea.md` | 无 |
| `sources` | `artifacts/10-sources.yaml` | `idea` |
| `claims` | `artifacts/11-claims.yaml` | `sources` |
| `brief` | `artifacts/20-brief.md` | `idea`, `sources`, `claims` |
| `style-spec` | `artifacts/25-style-spec.yaml` | `brief`, 本次风格选择, 创建时读取的 Style Memory 版本 |
| `outline` | `artifacts/30-outline.md` | `brief`, `style-spec` |
| `draft` | `artifacts/40-draft.md` | `brief`, `outline`, `claims`, `style-spec` |
| `manuscript` | `artifacts/41-manuscript.md` | `draft`, `style-spec` |
| `style-report` | `artifacts/42-style-report.yaml` | `draft`, `manuscript`, `style-spec` |
| `fact-review` | `artifacts/50-fact-review.yaml` | `manuscript`, `claims` |
| `editorial-review` | `artifacts/51-editorial-review.md` | `brief`, `manuscript`, `style-spec` |
| `visual-plan` | `artifacts/52-visual-plan.yaml` | `manuscript`, `claims`, 两类 review |
| `visual-assets` | `artifacts/53-visual-assets.yaml`, `artifacts/assets/` | `visual-plan` |
| `publish-package` | `artifacts/60-publish-package/` | `brief`, `manuscript`, 两类 review, `visual-assets` |
| `publish-receipt` | `artifacts/70-publish-receipt.yaml` | `publish-package`, 发布审批 |
| `metrics` | `artifacts/80-metrics.yaml` | `publish-receipt` |
| `retrospective` | `artifacts/90-retrospective.md` | `metrics`, 所有关键资产 |

### 失效传播规则

每个资产都记录其内容哈希及所依赖资产的哈希快照。执行 `content-harness status` 或 `content-harness check` 时：

1. 重新计算当前文件哈希；
2. 文件内容变化时增加该资产的 revision；
3. 将直接依赖它的已完成资产标记为 `stale`；
4. 继续沿依赖图传播 `stale`；
5. 只允许重做受影响资产，不强制整条流程从头开始；
6. 已发布内容不回滚，只将后续指标或复盘标记为需要重新解释。

例如，用户手改 `draft` 后：

- `idea`、`sources`、`brief`、`outline` 保持有效；
- `manuscript`、`style-report`、`fact-review`、`editorial-review`、`visual-plan`、`visual-assets`、`publish-package` 变为 `stale`；
- 原发布审批因绑定旧 `publish-package` 哈希而失效。

---

## 运行目录与状态协议

```text
content-workspace/
├── workspace.yaml
└── runs/
    └── 2026-09-02-ai-learning-workflow/
        ├── manifest.yaml
        ├── transitions.jsonl
        ├── approvals.jsonl
        ├── artifacts/
        ├── snapshots/          # 已登记 revision 的只读快照，用于冲突恢复和风格反馈 diff
        └── logs/
```

### `manifest.yaml`

`manifest.yaml` 是当前状态的索引，不是唯一历史来源。状态历史由两个 JSONL 文件追加记录；每次资产通过检查并登记新 revision 时，CLI 还要保存内容寻址的只读快照。快照不参与正常写作，只用于冲突恢复、人工修改 diff 和审计，其跟踪策略继承 run 的 tracked / local-only 设置。

```yaml
schema_version: 1
run_id: 2026-09-02-ai-learning-workflow
content_type: wechat
created_at: 2026-09-02T10:00:00+08:00
updated_at: 2026-09-02T11:20:00+08:00
current_focus: fact-review

artifacts:
  manuscript:
    path: artifacts/41-manuscript.md
    status: done
    revision: 3
    content_hash: sha256:abc123
    depends_on:
      draft: sha256:def456
      style-spec: sha256:789abc
    updated_at: 2026-09-02T11:10:00+08:00
  fact-review:
    path: artifacts/50-fact-review.yaml
    status: stale
    revision: 1
    content_hash: sha256:fed321
    depends_on:
      manuscript: sha256:old-manuscript
      claims: sha256:789abc
    stale_reason: dependency_hash_changed:manuscript
```

资产状态只能是：

- `missing`：尚未创建；
- `in_progress`：已开始但没有通过完成检查；
- `done`：存在并通过该资产的确定性检查；
- `blocked`：有明确且可报告的阻塞原因；
- `stale`：自身曾完成，但依赖已经变化。

`current_focus` 只用于改善用户提示，不参与正确性判断。真正的可执行状态从 DAG、资产状态和审批共同推导。

### `transitions.jsonl`

每次状态变更追加一条事件：

```json
{"event_id":"evt_01","at":"2026-09-02T11:20:00+08:00","command":"check","artifact":"fact-review","from":"done","to":"stale","reason":"dependency_hash_changed:manuscript","actor":"content-cli"}
```

禁止重写历史事件。`manifest.yaml` 损坏时，可以从资产文件和事件日志重建。

### `approvals.jsonl`

```json
{"approval_id":"apr_01","at":"2026-09-02T11:30:00+08:00","gate":"publish","artifact":"publish-package","content_hash":"sha256:123abc","actor":"human:local","decision":"approved"}
```

审批必须绑定 gate、资产和内容哈希，不能只记录一个布尔值。

### 审批的信任边界

M0/M1 的审批是**可审计的流程控制**，不是经过身份认证的安全凭证。只要 Agent 与用户共享同一台机器和命令权限，CLI 就不能仅凭一条本地命令证明操作者一定是人类。

因此：

- M1 不连接真实发布 API，`publish` 审批只允许工作流继续生成最终交付状态；
- Agent 到达人工 gate 时必须停止并展示摘要、哈希和待执行命令，不能自行调用 `content-harness approve`；
- `content-harness approve` 默认要求交互式终端，并记录 `actor: human:local-tty`，用于降低误操作而不是宣称强身份认证；
- M3 接入真实发布前，必须使用宿主提供的用户确认事件，或由与 Agent 权限隔离的发布进程签发审批回执；
- 如果目标客户端无法提供可信确认边界，该 integration 只能生成草稿或发布包，不能执行公开发布。

### 并发与手工编辑保护

- 改写资产前，CLI 必须校验调用方提供的 `expected_revision` 或 `expected_hash`；
- 校验失败时拒绝覆盖并返回 `CONFLICT_EXTERNAL_EDIT`；
- 状态文件采用“写临时文件 + 原子替换”；
- JSONL 事件先追加成功，再更新 manifest；
- 恢复命令能够识别“事件已写、manifest 未更新”的中断点并重建索引；
- 同一 run 同时只允许一个状态写入者，使用 run 级锁文件并设置可诊断的过期策略。
- 每次登记 `done` revision 前保存旧内容快照；`style-feedback` 比较“上一个已登记 revision”和当前文件，不依赖对话记忆还原人工修改。

---

## Claim Ledger：证明来源真的支持主张

只检查文章有没有引用链接，会产生大量“有来源但来源不支持正文”的假安全感。MVP 必须把重要主张作为一等资产。

### `artifacts/11-claims.yaml`

```yaml
schema_version: 1
claims:
  - claim_id: claim-001
    text: 使用检查清单可以减少遗漏
    type: factual
    risk: medium
    sources:
      - source_id: source-003
        locator: section-2
        support: direct
        checked_at: 2026-09-02
    status: supported
    article_locations:
      - section: 为什么流程比提示词更重要
  - claim_id: claim-002
    text: 我过去写完正文后经常忘记核对配图
    type: experience
    risk: low
    provenance: user-provided-note
    status: author-confirmed
```

### 主张类型

- `experience`：作者亲历，只能表述为个人经验；
- `observation`：有限样本观察，必须写清范围；
- `factual`：可被外部来源核验的事实；
- `quantitative`：百分比、金额、人数、时间等定量事实；
- `prediction`：对未来的判断，不能伪装成事实。

### 支持等级

- `direct`：来源直接支持主张；
- `partial`：只支持主张的一部分，正文必须收窄；
- `contextual`：来源提供背景，但不能作为直接证据；
- `none`：未找到支持，必须删除、改写或标记为待核验。

### 三层检查

1. **确定性检查**：必填字段、链接格式、来源日期、正文 claim 引用、风险字段是否存在；
2. **语义检查**：由模型判断来源片段与主张的支持关系，并输出理由；
3. **人工检查**：高风险的定量、医疗、法律、金融或可能伤害第三方的主张，必须由人确认。

语义检查结果不能自动改成 `human_verified`。模型评审器要先用人工标注样本校准，再用于日常辅助检查。

---

## 三类门禁

### 1. 确定性门禁

由 CLI 执行，结果必须可重复：

- YAML/JSON Schema 合法；
- 必需文件存在；
- 依赖已完成且没有 `stale`；
- 内容哈希与依赖快照一致；
- Claim Ledger 字段完整；
- 图片和正文相对链接有效；
- 发布包包含标题、摘要、正文、图片和来源说明；
- 审批绑定当前资产哈希；
- 发布请求具有唯一幂等键；
- 待提交资产不含 `.env`、Token 或匹配敏感信息规则的内容。

### 2. 语义门禁

由专业 skill 或模型评审器执行，必须保留结构化理由：

- 选题是否回答真实读者问题；
- 核心判断是否清晰且有边界；
- 来源是否足以支持主张；
- 是否编造经历、反馈或数据；
- 表达是否符合作者声音；
- 读者看完是否有可执行动作。

语义门禁允许“通过但有警告”，但不能覆盖确定性失败和人工审批要求。

### 3. 人工门禁

MVP 固定两个必须停下来的节点：

| Gate | 审批对象 | 目的 |
|---|---|---|
| `brief` | `brief` | 在投入长文前确认读者、角度、核心判断和边界 |
| `publish` | `publish-package` | 确认最终内容、图片、目标渠道和发布动作 |

Agent 不得根据用户之前说过“以后都帮我发”而跳过单次发布确认。

---

## 最小 CLI

MVP 只实现状态协议所需命令：

```text
content-harness install-skills --client <client>
content-harness doctor
content-harness check-workflow <workflow-id>
content-harness init <project> --workflow <workflow-id>
content-harness new <slug> --workflow <workflow-id>
content-harness style <run-id> [--use <style-id>] [--intensity <level>]
content-harness style-feedback <run-id> --artifact <artifact-id> --scope <scope> --reason <text>
content-harness style-promote <run-id> <lesson-id>
content-harness status <run-id> [--json]
content-harness check <run-id> [--artifact <artifact-id>] [--gate <gate-id>]
content-harness approve <run-id> <gate-id>
content-harness resume <run-id> [--json]
content-harness invalidate <run-id> <artifact-id> --reason <text>
content-harness export <run-id> --target <target-id>
content-harness archive <run-id>
```

M3 才增加外部回执和指标导入命令：

```text
content-harness receipt <run-id> --from <receipt-file>
content-harness metrics <run-id> --from <metrics-file>
```

### 命令契约

- 所有成功的变更命令返回更新后的 revision；
- `--json` 输出拥有版本化 schema，供 Agent 稳定读取；
- 检查失败返回非零退出码和机器可读错误码；
- `approve publish` 只产生审批，不直接调用发布 API；
- Agent Skill 不得自行调用 `approve`；到达 gate 后必须把命令交给用户执行；
- `export` 只写入 Project Profile 声明的目标路径，并再次校验审批哈希；
- 真正发布由独立 integration 执行，并再次校验审批哈希；
- `invalidate` 只改变状态，不删除资产文件；
- `archive` 移动到工作区归档区，不做物理删除；
- `style-feedback` 只保存人工修改前后的差异、反馈理由和建议作用域，不直接修改 Style Memory；`scope` 只允许 `run`、`author` 或已登记的 `scenario`，不能从项目命令直接写公共 Style Pack；
- `style-promote` 必须由用户在交互式终端执行，将已审阅的候选规则写入指定作者或场景，并生成新版本；Agent 不得代替用户晋升长期偏好；
- `style` 在已有下游资产时仍可修改，但会让 `style-spec`、outline、draft、manuscript、reviews、visuals 和 publish package 按 DAG 失效；旧文件与旧 revision 快照保留。

### 技术选择

- Python 3.11；
- `Typer` 实现 CLI；
- `Pydantic` 定义状态和输出 schema；
- YAML 作为人工可读配置，JSONL 作为追加事件；
- `pytest` 覆盖状态机、崩溃恢复和安全门禁；
- 使用 `uv` 管理独立仓库环境和锁文件。

MVP 不先发布 `npx create-*` 脚手架。Python 包携带 skills 和 workflow packs，由 `install-skills` 安装到目标客户端；只有初始化复杂度成为主要阻力后再提供项目生成器。

---

## Agent Skills 设计

独立仓库从零实现以下小型 skill：

```text
skills/
├── content-harness/        # 小型 Router：读取状态，只选择一个下一步 skill
├── research-claims/        # 搜集来源，生成 sources 与 Claim Ledger
├── shape-brief/            # 收敛读者、问题、判断、边界和行动价值
├── select-style/           # 按需组合作者、场景和润色风格，生成 style-spec
├── design-outline/         # 根据 brief 与 style-spec 设计文章结构
├── write-draft/            # 根据 brief、outline、claims 与 style-spec 生成正文
├── refine-style/           # 生成 manuscript 与可回查的 style-report
├── learn-style/            # 从人工修改和拒绝中提出待确认的场景风格候选
├── review-draft/           # 对 manuscript 生成事实与编辑评审
├── plan-visuals/           # 生成配图计划、来源映射和替代文本
├── build-visuals/          # 生成或登记可发布图片资产
├── package-wechat/         # 生成公众号正文、标题、摘要和图片清单
└── retrospect-content/     # 根据回执和指标生成复盘与下一篇候选
```

### Skill 输入输出契约

| Skill | 必需输入 | 唯一主要输出 | 完成条件 |
|---|---|---|---|
| `content-harness` | `status --json` | 下一步动作建议 | 只选择一个可执行 skill，或报告 gate / blocker |
| `research-claims` | `idea`、Project Profile 的只读材料 | `sources`, `claims` | 关键事实都有支持等级或待核验状态 |
| `shape-brief` | `idea`, `sources`, `claims` | `brief` | 读者、问题、核心判断、边界、行动价值齐全 |
| `select-style` | 已批准的 `brief`、本次风格选择、Project Style Memory | `style-spec` | 风格层次、强度、适用阶段和不可改内容明确；未选择时写入 Author + `neutral`，`scene` 与 `polish` 为空 |
| `design-outline` | 已批准的 `brief`, `style-spec` | `outline` | 每一节都能追溯到 brief，结构性风格要求已体现 |
| `write-draft` | 已批准的 `brief`, `outline`, `claims`, `style-spec` | `draft` | 正文保持 brief 的读者、核心判断和边界，且不新增无登记的高风险事实 |
| `refine-style` | `draft`, `style-spec` | `manuscript`, `style-report` | 逐项报告风格修改，受保护内容未改变；无额外场景和润色风格时不做语义改写 |
| `learn-style` | 人工修改前后 revision、反馈理由、`style-report`、现有 Style Memory | candidate lesson 与 eval proposal | 区分一次性修改和长期偏好，给出证据与作用域，不自动晋升 |
| `review-draft` | `brief`, `manuscript`, `claims`, `style-spec` | 两类 review | 所有 blocker 有位置、原因和修复建议，风格改写未造成事实漂移 |
| `plan-visuals` | 已通过 review 的 `manuscript`, `claims` | `visual-plan` | 每张图有目的、类型、来源和正文位置 |
| `build-visuals` | `visual-plan` | `visual-assets` | 文件存在、可渲染、引用和来源有效 |
| `package-wechat` | 已通过 review 的 manuscript 与 visuals | `publish-package` | 公众号包通过确定性检查 |
| `retrospect-content` | receipt, metrics | `retrospective` | 区分事实、推断、未采集数据和下一步实验 |

### 约束

- 每个阶段 skill 独立设计，不调用 `kj-skills` 或其他本机私有 skill；
- Router 不包含调研、写作和评审正文，只做路由；
- skill 只通过 CLI 的 JSON 输出判断状态，不解析终端自然语言；
- 每个 skill 必须说明触发条件、拒绝条件、输入资产、输出资产和完成检查；
- 一个阶段的知识只放在该 skill 的 `references/` 中，避免大而全总控文件；
- 客户端不支持某个可选元数据时，核心流程仍可通过明确调用 skill + CLI 工作；
- Agent Skills 规范只解决目录和 `SKILL.md` 打包，不被当作跨客户端行为一致性的证明。

### 独立性测试

CI 在没有 `kj-skills`、没有个人 Wiki、没有作者配置的干净临时目录中运行完整夹具。任何 import、路径引用或 skill 调用指向 `kj-skills` 都直接失败。示例作者和示例材料使用公开的匿名 fixtures。

---

## 表达风格系统

表达风格是独立的可选层，不与事实、观点和作者经历混在一个提示词里。用户没有选择额外风格时，系统只使用 Author 层和 `neutral` 基础规则，可选 style stack 为空，不强行“爆款化”或去 AI 味。

### 三层 Style Stack

| 层级 | 解决的问题 | 示例 |
|---|---|---|
| Author | 这个人通常怎样表达、哪些表达不能替他写 | `project-author` |
| Scene | 这个平台和内容场景需要什么结构、节奏与读者预期 | `wechat-high-engagement`, `technical-explainer`, `story-driven` |
| Polish | 成稿后需要进行什么局部润色 | `natural-human-zh`, `concise-zh` |

`neutral` 作为所有任务的基础规则，三层再按 `Author → Scene → Polish` 合并。后层可以调整语言表现，不能覆盖前层的真实性边界；任何层都不能改写 Claim Ledger 中的事实含义。

### Style Packs 规划

| Style Pack | 作用 | 明确不做 | 阶段 |
|---|---|---|---|
| `neutral` | 清晰、克制、信息优先的默认表达 | 不增加营销语气 | M1 必需 |
| `wechat-high-engagement` | 强化具体标题、开头张力、阅读节奏、段落回报和可执行结尾 | 不保证“爆款”，不制造虚假冲突、焦虑或收益承诺 | M1 必需 |
| `natural-human-zh` | 清理模板化过渡、空洞排比、机械总结、过度对称和无依据的确定语气 | 不依赖“AI 检测率”，不把个人表达统一改成口语 | M1 必需 |
| `technical-explainer` | 用问题、输入输出、数据流和例子解释技术内容 | 不牺牲准确性换取简单化 | 后续场景示例 |
| `story-driven` | 用事件、冲突、转折和反思组织真实经历 | 不补造人物、对白、情节和第一人称经历 | 后续场景示例 |

产品界面可以把 `wechat-high-engagement` 展示为“公众号高传播 / 爆款表达”，但文档和结果不得声称选择该风格就能产生爆款。

### Style Pack 结构

```text
styles/<style-id>/
├── STYLE.md          # 适用场景、正向规则、硬边界
├── rubric.yaml       # 可检查的风格维度和评分锚点
├── examples/         # 最小正例、反例及改写说明
└── evals/            # 风格遵循与事实保真用例
```

Style Pack 不是一个新的大型 Skill。`select-style` 负责把选择编译成 `style-spec`，`design-outline`、`write-draft`、`refine-style` 和 `review-draft` 按各自阶段读取需要的部分。

### `style-spec.yaml`

```yaml
schema_version: 1
base:
  id: neutral
  version: 1
style_stack:
  author:
    id: project-author
    version: 3
  scene:
    - id: wechat-high-engagement
      version: 1
  polish:
    - id: natural-human-zh
      version: 1
memory_snapshot:
  author_version: 3
  scenario: wechat-longform
  scenario_version: 2
  content_hash: sha256:style-memory-abc123
intensity: medium
apply_to:
  outline: [hook, pacing, section_payoff]
  draft: [reader_context, examples, transitions]
  polish: [sentence_rhythm, remove_cliches, remove_empty_summary]
protected:
  - claims
  - numbers_and_units
  - dates_and_names
  - direct_quotes
  - user_written_experience
```

每个 run 固化 Style Pack 的 ID、版本和强度，并把当时读取的 Project Style Memory 版本与哈希写入 `memory_snapshot`。完成后的 `style-spec` 不再依赖实时 Style Memory；项目以后升级风格包或场景记忆时，旧 run 不会变成 `stale`，也不会因为默认配置变化而悄悄重写历史内容。

### 按需使用

用户可以在创建任务时选择：

```bash
content-harness new ai-workflow-gap \
  --workflow wechat-longform \
  --style wechat-high-engagement \
  --polish natural-human-zh \
  --style-intensity medium
```

也可以在 brief 批准后、outline 生成前设置：

```bash
content-harness style <run-id> \
  --use wechat-high-engagement \
  --use natural-human-zh \
  --intensity medium
```

CLI 只记录用户选择；`select-style` 据此生成 `style-spec`，表达改写由后续阶段 Skill 完成。

自然语言用法：

> 这篇使用公众号高传播风格，强度中等；再做一轮去 AI 味。保留我的个人经历、数字、引用和核心判断。

如果用户只说“按正常风格写”，则使用 Author 层与 `neutral`，不自动启用高传播和去 AI 味。

### 应用顺序

```text
approved brief
  → select-style：确定 style-spec
  → design-outline：应用结构性风格
  → write-draft：应用场景表达
  → refine-style：执行按需润色，生成 manuscript + style-report
  → review-draft：重新检查事实、作者声音、读者价值和风格边界
```

“去 AI 味”必须发生在 `draft` 之后，但其结果不能绕过评审。高传播风格需要在 outline 阶段介入，否则只能得到换词式润色，无法改善开头、节奏和段落回报。

### 风格保真门禁

`refine-style` 完成后必须检查：

- Claim Ledger 中的主张、支持等级和限定词是否保持；
- 数字、单位、日期、人名、产品名和直接引用是否改变；
- 用户亲自写的经历是否被补造、泛化或改成未经确认的第一人称；
- 是否为了标题张力制造正文无法兑现的承诺；
- 是否把“部分、可能、在当前样本中”等限制词删掉；
- 人工已确认的句子是否被大面积重写；
- `style-report` 是否记录修改类型、位置、理由和未采用建议。

确定性差异检查保护数字、日期、链接和引用；语义评审检查含义漂移。任一 blocker 出现时，`manuscript` 不得进入配图和发布包阶段。

### 不同场景的风格记忆

Project Style Memory 按场景隔离，不维护一份全局“我的风格”：

```text
.content-harness/style-memory/
├── author.yaml
├── scenarios/
│   ├── wechat-longform.yaml
│   ├── technical-tutorial.yaml
│   └── story-essay.yaml
└── candidates/
    └── <lesson-id>.yaml
```

同一句修改在公众号、技术教程和故事随笔中可能含义不同，因此风格反馈至少记录：

```yaml
lesson_id: style-lesson-001
scope: scenario
scenario: wechat-longform
source_runs: [run-001, run-006, run-009]
observation: 用户连续删除没有具体对象的反问式开头
proposed_rule: 开头优先使用真实场景或具体问题，不默认使用泛化反问
privacy: private
status: candidate
```

### 风格沉淀与迭代

```text
人工修改 / 拒绝某种表达
  → style-feedback event
  → learn-style 生成 candidate lesson + eval proposal
  → 判断作用域：本次文章 / 作者 / 场景 / 通用 style pack
  → 人工确认
  → 增加风格 eval
  → 更新 Project Style Memory 或版本化 Style Pack
  → 对历史样本做盲评和事实保真回归
```

晋升规则：

- 用户明确说“以后都这样写”的规则，可以直接进入项目候选，但仍需显示给用户确认；
- 单篇文章中的一次修改默认只属于该 run，不自动形成长期偏好；
- 在多个独立 run 重复出现的修改，才能建议晋升为场景规则；
- 作者个人偏好只进入 Project Style Memory，不进入公共 Style Pack；
- 通用 Style Pack 的修改必须有跨项目证据、失败 eval 和版本号；
- 与模型、平台算法或热点有关的规则必须设置 `review_after`，到期重新验证；
- 新版本效果下降或事实漂移增加时，可以按版本回滚。

一次具体迭代的使用方式是：用户修改 manuscript 后执行 `style-feedback` 记录“改了什么、为什么改、建议属于哪个场景”；`learn-style` 只生成候选规则和回归样例；用户审阅候选文件后，再亲自执行 `style-promote`。这样既能学习，又不会把一次临时措辞自动固化成永久人设。

完成标准：同一份 brief 可以分别使用 `neutral`、`wechat-high-engagement` 和 `natural-human-zh` 生成可比较版本；风格选择可追溯、可关闭、可回滚，受保护事实保持一致，项目反馈不会泄漏进公共风格包。

---

## Workflow Pack

Skill 说明“怎样完成一种认知任务”，Workflow Pack 说明“这种内容需要哪些资产以及它们如何依赖”。两者分开，避免把公众号特有规则写进 CLI。

MVP 内置 `wechat-longform`：

```text
workflows/wechat-longform/
├── workflow.yaml          # Artifact DAG、必需 Gate、阶段到 skill 的映射
├── artifact-schemas/      # brief、outline、review、visual plan 等 schema
├── templates/             # 公众号正文、标题、摘要、配图清单模板
├── gates/                 # 确定性检查配置
└── evals/                 # 该内容类型的行为用例和评分规则
```

`workflow.yaml` 是流程的唯一事实源。Router Skill 不再重复资产顺序，CLI 也不硬编码公众号步骤。

完成标准：修改 workflow pack 后，`content-harness check-workflow wechat-longform` 能验证 DAG 无环、每个资产都有生产 skill、每个 gate 都有检查器。

---

## 在 `kj-llm-wiki` 中如何使用

`kj-llm-wiki` 是 Content Harness 的第一个真实项目，但不是它的代码依赖。接入只新增项目配置和运行资产，不调用 `kj-skills`。

### 1. 初始化项目

MVP 实现后，在仓库根目录执行：

```bash
cd /Users/didi/ai_space/kj-llm-wiki
content-harness init . --workflow wechat-longform
```

初始化前读取项目的 `AGENTS.md`、`SCHEMA.md` 和内容流程文档。命令创建 `.content-harness/project.yaml` 与作者资料模板，不修改已有 `raw/`、`wiki/` 或 `os/` 文件。

### 2. Project Profile

建议配置如下；路径相对 `kj-llm-wiki` 根目录：

```yaml
schema_version: 1
project_id: kj-llm-wiki
workflow: wechat-longform

style:
  base: neutral
  default_scene: null
  default_polish: []
  memory_root: .content-harness/style-memory/
  allow_run_override: true

policy_files:
  - AGENTS.md
  - SCHEMA.md
  - wiki/playbooks/content-production-flow.md
  - wiki/playbooks/topic-bank/series-planning.md

read_roots:
  - wiki/
  - raw/notes/
  - raw/articles/
  - raw/papers/
  - raw/studio/funnel/transcripts/
  - raw/studio/funnel/backlog/

dedupe_roots:
  - raw/studio/funnel/formatted/wechat/
  - raw/studio/funnel/published/wechat/

author_sources:
  - .content-harness/author-profile.md

run_root: .content-harness/runs/

exports:
  wechat:
    article: raw/studio/funnel/formatted/wechat/{date}-{slug}.md
    assets: raw/studio/funnel/formatted/wechat/assets/{date}-{slug}/

write_policy:
  source_roots: read_only
  existing_raw: no_overwrite
  export_conflict: fail
  publish: disabled
```

这份配置只描述“去哪读、去哪写、哪里不能动”。作者声音由 `author-profile.md` 中的人类确认资料提供，不通过 `kangjian-skill` 或其他私有 skill 注入。`style` 只设置默认风格、项目记忆位置和是否允许单篇覆盖；未指定额外风格时使用 `neutral`。

### 3. 发起一篇文章

可以直接对 Agent 说：

> 使用 Content Harness，基于 `kj-llm-wiki` 现有资料，把“AI 学了很多但工作方式没改变”做成公众号文章。先检查已发布内容和重复风险，完成 brief 后等我确认。

Agent 内部执行：

```bash
content-harness new ai-workflow-gap --workflow wechat-longform
content-harness resume 2026-09-08-ai-workflow-gap --json
```

然后按 CLI 返回值调用 `research-claims` 和 `shape-brief`。到达 `brief` gate 后，Agent 必须展示：

- 目标读者；
- 真实问题；
- 核心判断及不适用边界；
- 与已有文章的重复风险；
- 关键来源和待核验事实；
- 当前 brief 的内容哈希。

用户确认后，在终端执行：

```bash
content-harness approve 2026-09-08-ai-workflow-gap brief
```

### 4. 生成、评审和修改

批准 brief 后，用户可以不选风格，也可以按本篇场景选择风格：

```bash
content-harness style 2026-09-08-ai-workflow-gap \
  --use wechat-high-engagement \
  --use natural-human-zh \
  --intensity medium
```

Agent 随后依次生成 `style-spec`、outline、draft、manuscript、style report、两类 review、visual plan 和 visual assets。用户也可以直接说：

> 这篇用公众号高传播风格，强度中等，再去一轮 AI 味；不要改我的经历、数字、引用和核心判断。

初稿位于 `.content-harness/runs/<run-id>/artifacts/40-draft.md`，经过风格处理且等待评审的正文位于 `41-manuscript.md`。通常修改措辞时编辑 manuscript；如果要改变论点、事实或文章结构，则同时回到 claims、brief、outline 或 draft，避免只在成稿层留下无法追溯的变化。

再次执行 `resume` 时，CLI 会检测文件哈希变化。修改 draft 会使 manuscript、style report、reviews、visuals 和 publish package 失效；只修改 manuscript 时，仅使 reviews、visuals 和 publish package 失效。系统不会覆盖用户正文，也不会重做仍然有效的调研。

### 5. 导出到 Studio

所有门禁通过后，Agent 展示最终文章、标题、摘要、配图、来源边界和目标路径。用户先批准发布包：

```bash
content-harness approve 2026-09-08-ai-workflow-gap publish
content-harness export 2026-09-08-ai-workflow-gap --target wechat
```

导出结果：

```text
raw/studio/funnel/formatted/wechat/2026-09-08-ai-workflow-gap.md
raw/studio/funnel/formatted/wechat/assets/2026-09-08-ai-workflow-gap/
```

`export_conflict: fail` 表示目标已存在时停止并报告，不覆盖旧稿。导出不等于发布，Content Harness 不更新 `published/`，也不提交、推送或调用公众号后台。

### 6. 后续发布和复盘

用户在仓库既有流程中完成发布后，可以把真实回执导入：

```bash
content-harness receipt 2026-09-08-ai-workflow-gap --from <receipt-file>
content-harness metrics 2026-09-08-ai-workflow-gap --from <metrics-file>
```

`retrospect-content` 只根据真实回执和指标生成复盘；缺失数据写 `未采集`。知识化仍服从 `kj-llm-wiki` 的捕获 / Ingest 规则，不由 Content Harness 自动写入 `wiki/`。

### 7. 在 `kj-llm-wiki` 沉淀风格反馈

例如用户把 manuscript 中多个泛化反问改成具体工作场景后，可以记录这次反馈：

```bash
content-harness style-feedback 2026-09-08-ai-workflow-gap \
  --artifact manuscript \
  --scope scenario \
  --reason "公众号长文开头优先具体场景，不默认使用泛化反问"
```

Agent 调用 `learn-style` 后，只在 `.content-harness/style-memory/candidates/` 生成候选规则和回归样例。用户确认它确实适用于未来的公众号长文，再执行：

```bash
content-harness style-promote 2026-09-08-ai-workflow-gap style-lesson-001
```

晋升后的规则只进入 `kj-llm-wiki` 的 `wechat-longform` 场景记忆，并从下一个 run 起生效；当前 run 继续使用已固化的旧版本。技术教程或故事随笔不会继承这条规则，公共 Style Pack 也不会得到私有反馈。

### 8. 版本控制边界

- `.content-harness/project.yaml` 和 `author-profile.md` 是否跟踪，由仓库所有者决定；
- run 中可能包含未公开观点和来源摘录，初始化时必须明确 tracked 或 local-only；
- cache、lock、临时渲染和凭据始终忽略；
- Content Harness 不执行 `git add`、`commit` 或 `push`。

完成标准：在不安装 `kj-skills` 的环境中，使用该 Project Profile 能完成一次 `new → brief approval → optional style → manuscript → reviews → export`，且只新建约定的 run、Style Memory 和 Studio 成稿资产。

---

## 发布安全与幂等

MVP 默认终点是 `publish-package`，不是“已发布”。

后续发布 integration 必须满足：

1. `dry-run` 能展示平台、账号别名、标题、内容哈希和图片清单；
2. 发布审批绑定相同的 `publish-package` 哈希；
3. 每次发布使用 `run_id + package_hash + channel` 生成幂等键；
4. 相同幂等键已有成功回执时，拒绝重复发布；
5. 网络结果不确定时记录 `unknown`，先查询平台状态，不能直接重试；
6. 发布回执包含平台内容 ID、时间、URL 或草稿 ID；
7. Token 只从环境或系统密钥存储读取，永不写入 run 目录；
8. 日志对 Cookie、Token、手机号、读者标识等敏感信息脱敏。

---

## 跨客户端兼容策略

“目录能被发现”不等于“行为一致”。MVP 建立兼容矩阵，每个客户端都必须运行同一组夹具。

| 能力 | Codex | Claude Code | Cursor |
|---|---|---|---|
| skill 安装与发现 | 待测 | 待测 | 待测 |
| 按需读取 references | 待测 | 待测 | 待测 |
| 调用本地 CLI | 待测 | 待测 | 待测 |
| 在 `brief` gate 停止 | 待测 | 待测 | 待测 |
| 在 `publish` gate 停止 | 待测 | 待测 | 待测 |
| 中断后恢复相同状态 | 待测 | 待测 | 待测 |
| 保留用户手工修改 | 待测 | 待测 | 待测 |
| 产生相同结构的资产 | 待测 | 待测 | 待测 |

只有测试通过的组合才能在 README 中写“支持”。未测试客户端只能写“遵循 Agent Skills 目录规范，兼容性未验证”。

---

## 证明方案合理的方法

验证分五层进行，不能用单一文章指标替代工程正确性。

### A. 机制验证：协议是否可靠

使用固定夹具和自动化测试验证：

- 合法与非法状态变更；
- 上游修改后的 `stale` 传播；
- 审批哈希失效；
- 外部手改导致的 revision 冲突；
- 每个持久化步骤前后的故障注入；
- manifest 重建；
- 发布幂等和不确定回执；
- 归档不删除资产；
- Style Pack 版本固定、Project Style Memory 场景隔离和候选规则晋升权限；
- 风格处理前后的数字、日期、链接、引用和受保护片段一致；
- 敏感信息门禁。

完成标准：所有 P0 用例 100% 通过，连续运行 100 次无资产覆盖、无未授权发布、无重复发布。

### B. Agent 行为评估：流程是否被正确执行

建立 20–50 个来自真实失败的任务，其中同时包含：

- 应触发完整工作流的请求；
- 只需要润色、不应触发完整工作流的请求；
- 来源不足、必须阻塞的请求；
- 用户手改后继续的请求；
- 诱导绕过审批的请求；
- 网络中断和客户端重启场景；
- 同一 brief 分别不启用风格、启用高传播风格、只启用去 AI 味的场景；
- 风格改写试图改变数字、限定词、引用或个人经历，必须被门禁阻止的场景。

每个任务至少运行 3 次，记录成功率、错误类型、耗时和模型成本。评估以最终资产和状态为主，不要求 Agent 走完全相同的语言路径。

评分器组合：

- 确定性断言检查文件、状态、哈希和门禁；
- 模型评分器检查内容语义；
- 人工评分校准模型评分器，并抽检高风险案例。

### C. 10 篇真实文章试用：证明可用，不证明效果

选择 10 个真实公众号任务，覆盖从想法、旧稿、研究材料三类入口。记录：

- 是否完成全部必需资产；
- 中断恢复次数和失败原因；
- 人工修改被保留的比例；
- 从想法到发布包的耗时；
- 每一步实际使用率；
- 用户主动跳过或绕开流程的节点；
- 成本、Token 和工具调用数量。

这一阶段只证明流程可执行、数据可收集，并发现故障模式。不得根据阅读量变化直接声称工作流有效。

### D. 配对盲评：证明内容质量变化

试用后再确定正式样本量。对相同输入、相同模型、相同时间或 Token 预算，分别生成：

- 基线组：现有单次写作流程；
- 工作流组：Content Harness。

文章匿名、随机排序，由至少 2 名不了解分组的评审者评分：

- 事实支持度；
- 核心判断清晰度；
- 作者真实性；
- 场景风格匹配度与自然度；
- 读者可执行性；
- 整体偏好。

开始前固定主要指标、评分规则和排除条件。模型只做辅助评分，主要结论以人工盲评和确定性事实检查为准。

### E. 四周持续使用：证明产品价值

最后观察四周：

- 是否持续使用而不是演示一次；
- 是否能减少返工和遗漏；
- 是否形成可复用资产；
- 是否愿意把下一篇继续放进该工作区；
- 维护状态协议的成本是否低于它节省的成本。

阅读量、完读率和转发率可以记录，但受选题、分发、发布时间和账号状态影响，只作为探索指标，不作为单独因果证据。

---

## Go / No-Go 标准

以下阈值是产品决策标准，不是学术意义上的因果证明。

### 必须满足的 P0

- 0 次静默覆盖人工修改；
- 0 次未获得当前内容哈希审批的发布；
- 0 次相同幂等键的重复发布；
- 100% 正确识别预设的 stale 传播夹具；
- 100% 正确阻止缺少必需来源或审批的夹具；
- 100% 阻止风格处理造成的受保护事实变化；
- 0 次未经用户确认把单篇反馈晋升为长期风格规则；
- manifest 可从资产和事件日志恢复。

### 值得继续投入的信号

- 10 篇试用中至少 9 篇能完成到发布包；
- 中断后的继续任务成功率不低于 90%；
- 高风险无来源主张相比基线减少至少 50%；
- 风格处理后的受保护事实保持率为 100%，且人工盲评的场景风格匹配度不低于基线；
- 人工盲评中，工作流组在主要质量指标上的胜率高于 60%；
- 中位人工编辑时间减少至少 25%，或质量明显提升且总成本不超过基线 2 倍；
- 四周后仍有至少 60% 的真实文章通过该工作流启动。

### 停止或收缩的条件

- 状态维护时间长期高于它减少的返工时间；
- 用户频繁绕过 brief 或 review，说明资产粒度不符合真实工作；
- 跨客户端行为无法通过 CLI 和夹具稳定约束；
- 盲评没有质量提升，且人工时间和成本都增加；
- 大多数价值只来自某一个写作提示词，而不是工作流协议。

若触发停止条件，不继续平台化；只保留被证明有用的 Claim Ledger、门禁或恢复组件，作为独立的小工具。

---

## 实施阶段

### M0：协议与测试夹具

交付：

- `manifest`、artifact、event、approval schema；
- DAG 和 stale 传播算法；
- 文件锁、原子写入和冲突检测；
- 10 个机制测试夹具；
- CLI 的 `init/new/status/check/invalidate`。

完成标准：不调用任何模型，也能通过全部状态测试。

### M1：单篇公众号闭环

交付：

- `brief` 和 `publish` 审批；
- Claim Ledger；
- 从零实现 `research-claims`、`shape-brief`、`select-style`、`design-outline`、`write-draft`、`refine-style`、`learn-style`、`review-draft`、`plan-visuals`、`build-visuals` 和 `package-wechat`；
- `neutral`、`wechat-high-engagement` 和 `natural-human-zh` 三个 MVP Style Packs；
- 按场景隔离的 Project Style Memory、候选规则确认和版本回滚；
- `wechat-longform` Workflow Pack；
- Project Profile 解析与安全导出；
- `resume`；
- 发布包，但不接真实发布 API。

完成标准：一个真实主题可以跨至少一次中断完成到发布包，人工修改不会被覆盖；同一 brief 能在默认、高传播和去 AI 味三种选择下生成可比较且事实一致的 manuscript。

### M2：评估与跨客户端验证

交付：

- 20–50 个行为 eval；
- 三类评分器；
- Codex、Claude Code、Cursor 兼容矩阵；
- 10 篇真实任务的试用报告。

完成标准：P0 全部满足，兼容声明与实际测试一致。

### M3：可选发布与指标 Integration

只有 M2 的 Go 信号满足后才进入：

- 公众号草稿箱 integration；
- 幂等发布回执；
- 指标采集；
- 复盘与下一篇建议。

完成标准：发布安全测试全部通过，并且 integration 代码不进入通用核心。

---

## 独立仓库建议结构

```text
content-workflow-harness/
├── README.md
├── LICENSE
├── pyproject.toml
├── uv.lock
├── schemas/
│   ├── manifest.schema.json
│   ├── claims.schema.json
│   ├── style-spec.schema.json
│   ├── style-feedback.schema.json
│   ├── event.schema.json
│   └── approval.schema.json
├── src/content_harness/
│   ├── cli.py
│   ├── graph.py
│   ├── state.py
│   ├── gates.py
│   ├── approvals.py
│   ├── profiles.py
│   ├── workflows.py
│   └── recovery.py
├── skills/
│   ├── content-harness/
│   ├── research-claims/
│   ├── shape-brief/
│   ├── select-style/
│   ├── design-outline/
│   ├── write-draft/
│   ├── refine-style/
│   ├── learn-style/
│   ├── review-draft/
│   ├── plan-visuals/
│   ├── build-visuals/
│   ├── package-wechat/
│   └── retrospect-content/
├── styles/
│   ├── neutral/
│   ├── wechat-high-engagement/
│   ├── natural-human-zh/
│   ├── technical-explainer/
│   └── story-driven/
├── workflows/
│   └── wechat-longform/
│       ├── workflow.yaml
│       ├── artifact-schemas/
│       ├── templates/
│       ├── gates/
│       └── evals/
├── profiles/
│   └── example-project.yaml
├── evals/
│   ├── fixtures/
│   ├── behavior/
│   └── graders/
├── integrations/
│   └── example/
└── tests/
```

---

## 验收标准

实现者只有同时满足以下条件，才能称为“MVP 完成”：

- [ ] 能创建和读取版本化 run；
- [ ] 状态由 Artifact DAG 推导，不依赖单一线性阶段；
- [ ] 上游变化会精确传播 `stale`；
- [ ] 外部手工修改不会被静默覆盖；
- [ ] 审批与具体资产哈希绑定；
- [ ] Claim Ledger 能区分个人经验、观察、事实、定量信息和预测；
- [ ] 不选择额外风格时能以 `neutral` 完成全流程，不被强制“爆款化”或去 AI 味；
- [ ] 风格选择按 run 固化版本，可关闭、覆盖和回滚；
- [ ] 风格改写不会改变数字、日期、引用、限定词、已确认经历和 Claim Ledger 的事实含义；
- [ ] Project Style Memory 按作者和场景隔离，单篇修改不会未经确认自动晋升为长期规则；
- [ ] 确定性、语义和人工门禁互不替代；
- [ ] Agent 中断后可以只依赖磁盘恢复；
- [ ] 默认只生成发布包，不自动发布；
- [ ] 发布 integration 具备 dry-run、幂等和不确定结果恢复；
- [ ] 至少完成机制测试、行为 eval 和 10 篇可用性试用；
- [ ] README 的客户端兼容声明都有对应测试记录；
- [ ] 通用仓库不含个人路径、凭据、私有内容或作者人设。

---

## 明确不做

- Web 管理后台；
- 多人实时协作和权限系统；
- 云端数据库；
- 一键生成所有平台版本；
- 自动追热点和批量洗稿；
- 通用 Agent 框架或任务调度平台；
- 在没有验证需求前引入 LangGraph 等重型运行时；
- 为展示完整度而复制已有内容 skill；
- 用阅读量或 10 篇小样本宣称因果效果。

---

## 设计依据

- [Agent Skills Specification](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx)：用于约束 skill 的目录和元数据，不承担运行时一致性。
- [OpenSpec Custom Schemas](https://github.com/Fission-AI/OpenSpec/blob/main/docs/customization.md)：证明“资产 + 依赖”可以成为可配置工作流的基础；本 MVP 仍需自行实现内容哈希、失效传播和审批。
- [LangGraph Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)：作为未来需要复杂 checkpoint、并行和长运行任务时的参考，不作为 MVP 依赖。
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)：评估采用确定性、模型和人工评分组合，并从真实失败案例构建任务集。

---

## 最终决策

先做 M0 和 M1，不先建平台、不先接真实发布、不先追求跨所有内容类型。

如果 M1 不能证明“安全恢复、保留人工修改、精确失效、可审计审批、风格改写不破坏事实”这五件事，项目不进入 M2；如果 M2 不能证明相对现有流程存在稳定收益，项目不进入发布集成和平台化阶段。
