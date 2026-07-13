# Evidence and Scoring Rubric｜证据与评分规则

## 1. 证据等级

| 等级 | 来源 | 可用方式 |
|---|---|---|
| S | 官方发布、官方文档、API changelog、标准/监管文件、权威 benchmark | 可作为事实基础，但仍需检查适用范围和日期 |
| A | 论文 + 代码 + benchmark，或高质量同行评议论文 | 可作为方法依据，但要检查产品化距离 |
| B | 高活跃开源项目、工程社区多方复现、严肃工程复盘、高校/研究机构课程或实验室材料与论文或项目互证 | 可作为工程可行性或方法趋势信号 |
| C | 专家博客、newsletter、播客、行业分析、行业影响力人物演讲/访谈/公开课、未被研究或工程互证的高校/机构 seminar | 可作为解释框架或趋势观点，不可单独作为事实 |
| D | 社媒、传闻、单点 demo、截图、单个用户评价 | 只能作为弱信号或待验证线索 |

## 2. 评分维度

每条候选信号按 0-100 评分。

### 行业最佳实践材料的动态时效模型

不要只按“发布时间超过 1 年”机械降权。行业最佳实践材料必须先归类，再按材料类型、领域变化速度和近期复核状态计权。

#### 2.0.1 材料类型

| material_type | 示例 | 默认时效半衰期 | 计权原则 |
|---|---|---:|---|
| breaking_change | API、价格、模型、监管、产品 release、漏洞 | 30-90 天 | 强依赖最新版本，超过 1 年通常只能当历史背景 |
| product_practice | 竞品功能、案例、上线实践、商业包装 | 90-180 天 | 需要最新产品页、release notes 或用户反馈复核 |
| engineering_practice | 架构、工具链、开源框架、生产复盘 | 180-365 天 | 看最近 release、commit、issue、生产采用案例 |
| benchmark_or_eval | benchmark、评测方法、数据集、质量体系 | 180-365 天 | 看是否仍被近期论文/项目采用，避免旧 benchmark 失真 |
| academic_method | 论文、课程、实验室方法、seminar | 365 天；快速变化主题 180 天 | 经典方法可保留，但行动建议必须有近期互证 |
| standard_or_framework | NIST、ISO、W3C、行业框架、监管指南 | 以最新版本/修订状态为准 | 不能因发布超过 1 年直接降权；检查是否仍是当前有效版本、是否正在修订 |
| classic_principle | 基础理论、经典设计原则、长期有效方法论 | 不设硬阈值 | 只能作为背景或约束，不能单独驱动高优先级建议 |
| expert_talk | 演讲、访谈、播客、newsletter | 90-180 天 | 默认是观点；超过 1 年通常降权，除非被近期事实/产品/论文验证 |

#### 2.0.2 effective_recency

每条材料都要计算有效新鲜度，而不是只看首次发布时间：

```text
effective_recency = max(
  published_or_updated_at,
  latest_version_at,
  latest_revision_at,
  latest_release_at,
  latest_independent_adoption_at,
  latest_citation_or_revalidation_at
)
```

如果无法确定上述时间，使用 `published_or_updated_at`，并降低可信度。

#### 2.0.3 领域变化速度

按主题设置 `domain_velocity`：

- `fast`：快速迭代的软件平台、模型/API、工具链、安全漏洞、前端框架等。
- `medium`：SaaS 产品实践、数据平台、企业流程、评估体系等。
- `slow`：治理框架、合规、组织流程、基础设计原则、标准化方法等。

同一材料在不同领域速度下的时效权重不同。快速变化主题中，超过 6-12 个月的演讲、开源实践、产品实践通常要降权；标准、法规和经典理论则按当前有效状态处理。

#### 2.0.4 freshness_penalty

建议扣分范围：

| 状态 | 判定 | 扣分 |
|---|---|---:|
| fresh | 在主题默认窗口内，或有近期更新 | 0 |
| recent | 稍超默认窗口，但仍在材料类型半衰期内 | 0-5 |
| aging | 超过半衰期但未超过 1 年，或最新验证不足 | 5-12 |
| stale | 超过 1 年且没有近期复核、版本更新或采用证据 | 12-25 |
| classic | 超过 1 年但属于经典/标准/基础方法，且有近期复核 | 0-8；同时标注“背景/经典” |

#### 2.0.5 近期复核和采用证据

以下信号可以降低时效惩罚或提升来源多样性：

- 官方最新版本、修订说明、profile、playbook、changelog。
- 最近 1 年内被权威论文、课程、标准、工程复盘或竞品实践引用。
- 最近 1 年内有真实产品采用、案例研究、生产复盘、开源活跃维护。
- 多个独立来源在近期给出一致判断。

以下情况必须降权：

- 旧演讲/旧访谈没有近期互证。
- 旧产品案例对应产品形态已明显变化。
- 旧 benchmark 已被新数据集或新评测方法替代。
- 开源项目超过 1 年无 release/commit/issue 活跃，但仍被当作当前最佳实践。
- 标准或框架已有新版本、修订中或被替代，却仍引用旧版本做行动建议。

#### 2.0.6 输出要求

每条重点信号都要标注：

```yaml
material_type:
domain_velocity:
published_or_updated_at:
effective_recency_at:
freshness_status:
freshness_penalty:
revalidation_evidence:
why_still_relevant_or_downweighted:
```

#### 2.0.7 参考案例

本模型参考以下成熟行业最佳实践材料的处理方式：

- Thoughtworks Technology Radar：https://www.thoughtworks.com/radar 。它按期发布技术快照，用 Adopt / Trial / Assess / Caution 表达推荐强度，并标注 New / Moved / No change，说明最佳实践需要同时表达成熟度、推荐变化和时效。
- NIST AI Risk Management Framework：https://www.nist.gov/itl/ai-risk-management-framework 。AI RMF 1.0 发布于 2023 年，但 NIST 后续发布 Generative AI Profile（2024）和 Critical Infrastructure Profile 概念说明（2026），说明标准/框架应按当前有效版本和最新 profile 计权，而不是按首次发布时间直接降权。
- ISO Standards：https://www.iso.org/standards.html 。ISO 将标准定义为专家共识下“做某事的最佳方式”，并提供可查询最新内容的 Online Browsing Platform，说明标准类材料要看当前版本、适用范围和最新修订状态。
- GRADE Working Group：https://www.gradeworkinggroup.org/ 。GRADE 区分证据确定性和推荐强度，并要求显式考虑证据域、结果、成本、可行性等决策因素，说明“证据强”不等于“建议强”，行业最佳实践也必须经过情境转译。

### product_fit：产品相关性，权重 25%

- 90-100：直接解决用户当前优化对象的核心问题。
- 70-89：与一个关键能力高度相关。
- 50-69：有间接启发。
- 0-49：相关性弱。

### novelty：新颖度，权重 18%

- 90-100：最近 7 天重大变化。
- 70-89：最近 30 天清晰新信号。
- 50-69：最近 90 天背景变化。
- 0-49：旧内容或重复概念。

说明：`novelty` 衡量“新变化”强度，不等同于材料是否仍可用。经典理论、有效标准和长期方法论可以 novelty 较低，但如果 `revalidation_evidence` 充分，`freshness_penalty` 可以较低；它们通常作为背景、约束或评估框架，而不是单独作为高优先级行动建议。

### evidence_strength：证据强度，权重 20%

- S：90-100
- A：75-89
- B：60-74
- C：40-59
- D：10-39

### source_diversity：来源多样性，权重 10%

- 90-100：官方 + 论文/开源 + 社区/竞品多源互证。
- 70-89：两个独立来源互证。
- 40-69：单个高质量来源。
- 0-39：单个弱来源。

### architecture_transferability：架构可迁移性，权重 12%

- 90-100：可直接转成模块、数据结构、流程或工具调用。
- 70-89：需要中等改造。
- 50-69：需要较多研发或依赖外部条件。
- 0-49：难迁移。

### evalability：可评估性，权重 10%

- 90-100：可以用明确数据集、测试集、指标验证。
- 70-89：可以通过 A/B、人工评审或离线评估验证。
- 50-69：只能做定性验证。
- 0-49：很难验证。

### implementation_efficiency：实现效率，权重 5%

- 90-100：1 周内可做 MVP。
- 70-89：1 个月内可做原型。
- 50-69：1 个季度级别。
- 0-49：成本过高。

### hype_penalty：炒作惩罚，0-25 分

扣分情形：

- 只有新名词，没有可靠证据：扣 10-20。
- 只有 demo，没有真实场景：扣 5-15。
- 来源存在明显利益相关且无第三方验证：扣 5-15。
- 单场演讲、访谈或高校活动未被论文/工程/竞品信号验证：扣 5-15。
- 不能解释失败边界：扣 5-10。
- 与用户产品无关但看起来热门：扣 10-25。

## 3. 输出分流

| 分数 | 处理 |
|---|---|
| 80+ | 进入重点建议和机会池 |
| 65-79 | 进入观察池或原型验证 |
| 50-64 | 记录，非优先行动 |
| <50 | 忽略，除非用户指定关注 |

## 4. 可信度措辞

- 高可信：S/A 证据，多源互证。
- 中可信：B 证据或单个强来源。
- 低可信：C/D 观点，需验证。
- 推断：基于多个事实做出的产品判断，必须说明推断链路。
