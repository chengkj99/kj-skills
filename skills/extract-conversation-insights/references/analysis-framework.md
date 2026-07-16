# 录音对话分析框架

## 目录

- 保真层级
- 证据类型与强度
- 质疑卡
- 晋升评分
- 隐私规则
- 社区实践依据

## 保真层级

| 层级 | 目的 | 允许处理 |
|---|---|---|
| 原始录音 | 最终回查 | 不修改；控制访问范围 |
| 原始转写 | 搜索与核对 | 保留口误、歧义和识别错误标记 |
| 整理稿 | 阅读与分析 | 修断句、明显错词、无意义重复；不改语义 |
| 提炼卡 | 决策与复用 | 观察、假设、质疑、内容/行动去向 |

优先保留“智能逐字稿”：删掉不影响语义的填充词和重复，同时保留完整观点、故事和上下文。不得用摘要替代原始转写。

## 证据类型与强度

### 证据类型

| 类型 | 含义 | 用法 |
|---|---|---|
| `direct_quote` | 能回查的原句 | 可作为直接证据，公开前确认授权 |
| `paraphrase` | 保留原意的转述 | 必须附锚点，避免伪装成原话 |
| `reported_claim` | 说话人转述第三方/事件 | 只能证明“对方如此陈述” |
| `inference` | 分析者解释 | 必须进入质疑卡，不能写进观察列 |
| `uncertain` | 转写或语境不明 | 回听或保留不确定，不猜测 |

### 证据等级

| 等级 | 定义 | 可用范围 |
|---|---|---|
| A | 原话/行为清晰，且有多段或多源互证 | 可形成较强洞见，仍需说明边界 |
| B | 单次对话中有清晰证据，解释合理 | 可做内容和实验假设，不可当普遍事实 |
| C | 单句、转述或语境不足 | 仅作线索/追问 |
| D | 无锚点、纯猜测或识别不清 | 不进入结论 |

## 质疑卡

```markdown
### H-01 <假设标题>

- 主张：
- 支撑观察：O-01、O-03
- 证据等级：A / B / C / D
- 原话、转述还是解释：
- 可能反例：
- 替代解释：
- 缺失证据：
- 证伪条件：
- 隐私/表达风险：
- 当前状态：线索 / 待验证 / 暂时支持 / 已推翻
```

### 必查逻辑错误

- 样本外推：一个朋友的体验不代表目标用户群体。
- 赞同偏差：熟人说“很好”不等于会付费。
- 因果错置：发生先后或同时出现不等于因果。
- 成功者偏差：只谈成功路径，忽略成本、退出者和条件。
- Hook 夸大：标题张力不能抹去正文边界。
- AI 补全：转写缺口不能靠常识补成事实。

## 晋升评分

每项 1 分：

1. 证据：能回指时间戳/段落/可搜索短语。
2. 张力：存在具体痛点、分歧或决策冲突。
3. 机制：能解释“为什么”，而非只复述现象。
4. 支撑：有案例、反例或外部资料。
5. 连接：能接已有知识、内容或真实行动。

评分只决定加工优先级，不代表结论真伪。

## 隐私规则

- 默认私人聊天为 `private`。
- 将“可匿名表达”与“可直接引用”分开授权。
- 去除姓名、单位、具体职位、收入、住址、孩子信息、健康信息与可识别时间线。
- 不把对方的脆弱经历改编成流量故事，即使技术上已匿名。
- 使用第三方 AI/STT 服务前确认录音授权和数据范围；无法确认时优先本地处理。

## 社区实践依据

- GOV.UK 建议区分 full verbatim、intelligent verbatim 和 summary；智能逐字稿通常更适合分析与阅读：<https://www.gov.uk/service-manual/user-research/taking-notes-and-recording-user-research-sessions>
- GOV.UK 建议先记录可观察事实，再聚类并形成 finding/insight，同时保留录音供核查：<https://www.gov.uk/service-manual/user-research/analyse-a-research-session>
- GitLab 将 insight 区分为 informative 与 actionable；可行动洞见应含洞见、原因证据和明确动作：<https://handbook.gitlab.com/handbook/product/ux/experience-research/research-insights/>
- GitLab 的持续访谈实践在获得同意后保存录音、转写和标签，供未来复用：<https://handbook.gitlab.com/handbook/product/product-processes/continuous-interviewing/>
- Dovetail 将可回指原始证据的 insight 作为研究库基本单元，并用受治理的 taxonomy 支持检索和跨源综合：<https://dovetail.com/research/synthesize-research-across-product-squads-unified-insight-library/>
