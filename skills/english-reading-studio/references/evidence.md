# 研究依据与设计边界

调研：2026-10-19—20。实时验证状态：部分验证。参考官方文档、教学机构材料、研究综合与学术论文；不是已验证的整套教学干预。来源功能与学习效果分开判断。

| 信号 | 来源 / 日期 / 证据 | 设计影响与边界 |
|---|---|---|
| S001 双语段落支持 | [沉浸式翻译官方文档](https://immersivetranslate.com/docs/usage/)，无发布日期，2026-10-19 核查，S 功能证据 | 全文按段对齐保留原文；文档仅证明产品能力 |
| S002 就近解释 | [Readwise Ghostreader](https://docs.readwise.io/reader/guides/ghostreader/overview)，无发布日期，2026-10-19 核查，S 功能证据 | 解释绑定所选段落；本技能离线生成，继续追问回到对话 |
| S003 准备—正文—任务 | [British Council A2 阅读课程](https://learnenglish.britishcouncil.org/free-resources/reading/a2)，无发布日期，2026-10-20 核查，S 教学实践 | 英语模式先预习再阅读和练习；不据自述确定用户为 A2 |
| S004 分段与预习 | [Cambridge 研究综合](https://www.cambridge.org/core/books/abs/cambridge-handbook-of-multimedia-learning/principles-for-managing-essential-processing-in-multimedia-learning/A9E77D0172F905AC957689D1771E2888)，2021，B 研究综合，2026-10-20 核查摘要 | 可控节奏、概念预习；多媒体研究迁移到 AI 英文文章材料仍需验证 |
| S005 注释与词汇 | [Frontiers 元分析](https://www.frontiersin.org/journals/language-sciences/articles/10.3389/flang.2026.1815571/full)，2026-05-29，A，2026-10-19 核查 | 26 项研究总体支持注释帮助词汇，但条件异质；不能推广为全文译文自动提升英语 |
| S006 提取练习 | [Science](https://doi.org/10.1126/science.1152408)，2008-02-15，A 经典实验，本次仅摘要 | 支持延迟回忆设计；不是 AI 文章学习实验 |
| S007 可访问交互 | [W3C Tabs](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)、[Reflow](https://www.w3.org/WAI/WCAG22/Understanding/reflow.html)，2026-10-20 核查，S 规范说明 | 标签页键盘交互与窄屏重排；规范不证明学习收益 |

## 三项实践转译

1. 同一原文三种视图：基于 S001/S002。MVP 对同一材料生成可切换视图；衡量寻找原文的时间和误读数量。风险是解释挤占阅读，使用逐层展开。
2. 中文支持与精选训练：基于 S003/S004/S005。MVP 每篇少量词组和原句；衡量独立新句理解和求助次数。风险是难度过高或练习过量，短文减量并允许译文常开。
3. 答案分离与回忆：基于 S006。MVP 折叠答案和次日问题；衡量首次独立回答与延迟回忆。风险是只认答案，增加简单解释和新情境题。

5—8 个词组、3—5 个句子是控制负担的产品默认值，不是实验最优值。没有一种排版已证明适合所有读者。

## 个人验证路径

第一周试读一篇真实文章，检查是否能顺畅定位原文、理解解释并完成少量练习。一个月收集多种题材的理解和无辅助表现；一季度再决定增加朗读、长期复习或在线功能。使用满意度与完成篇数只作辅助，不代替独立解释与迁移。
