# Search Query Playbook｜查询矩阵生成法

## 1. 查询矩阵原则

查询不要只写一个宽泛关键词。每次调研应生成矩阵：

```text
主题 × 来源族 × 时间范围 × 证据类型 × 输出目标
```

## 2. 基础查询模板

### 官方发布

```text
site:{official_domain} {topic} release notes changelog docs new feature
site:{official_domain} {topic} API update limitation pricing enterprise
{company} {topic} announcement {last_30_days}
```

### 论文

```text
{topic} arxiv {method_keyword} evaluation benchmark
{topic} OpenReview {conference} {year}
{topic} dataset benchmark code
"{topic}" "method" "evaluation" "benchmark"
```

### 开源

```text
GitHub {topic} framework benchmark evaluation
{topic} site:github.com stars release issues
{topic} Hugging Face Spaces demo
```

### 工程社区

```text
{topic} Hacker News production lessons learned
{topic} Reddit engineering failure cost reliability
{topic} blog architecture postmortem
```

### 行业专家

```text
{expert_name} {topic}
{topic} newsletter analysis product architecture
{topic} podcast transcript trends
{expert_name} {topic} keynote talk lecture transcript video
{expert_name} {topic} interview podcast fireside chat
```

### 高校和研究机构

按主题选择高相关高校、实验室、研究中心和行业研究机构。不要固定迷信排名；如果用户明确要求“顶尖高校”，再用最新权威榜单校准名单，并标注榜单时间和适用边界。

通用候选来源类型：

```text
university research center
industry lab
public policy institute
standards body
professional association
```

高校/机构查询模板：

```text
site:{institution_domain} {topic} research center seminar lecture
site:{university_domain} {topic} course syllabus lecture slides
{institution_name} {topic} seminar colloquium transcript video
{institution_name} {topic} benchmark evaluation method
{institution_name} {topic} "best practices" "case study"
```

### 行业影响力人物/权威专家

按主题选择该领域的研究者、工程负责人、产品负责人、标准制定者、投资研究者、行业协会专家或高质量实践者。专家观点默认属于观点信号，必须和事实来源交叉验证。

查询模板：

```text
{person_name} {topic} keynote talk lecture transcript
{person_name} {topic} interview podcast fireside chat
{topic} keynote conference webinar transcript
{person_name} {topic} best practices case study
{person_name} {topic} trends report interview
```

### 竞品

```text
{competitor} {topic} release notes help docs
{competitor} {topic} pricing enterprise case study
{topic} Product Hunt launch alternatives
{topic} G2 reviews complaints
```

## 3. 关键词扩展

每次调研都要生成：

- 中文关键词
- 英文关键词
- 同义词
- 上位概念
- 下位概念
- 竞品名
- 方法名
- 用户场景词
- 评价指标词

## 4. 时间策略

默认：

- 最近 24 小时：日报。
- 最近 7 天：周报。
- 最近 30 天：默认深度调研。
- 最近 90 天：补充背景。
- 1 年内：重要论文和工程转折点。
- 更早：经典基础方法，必须标注“背景来源”。

## 5. 查询输出格式

在报告中可以简要列出查询矩阵，不要占据过多篇幅：

```markdown
## 查询矩阵摘要
| 来源族 | 查询方向 | 目的 |
|---|---|---|
| 官方 | ... | 验证产品/API变化 |
| 论文 | ... | 发现方法和评估 |
| 开源 | ... | 判断工程可行性 |
```
