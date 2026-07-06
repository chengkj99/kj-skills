const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, HeadingLevel, AlignmentType, LevelFormat, BorderStyle,
  WidthType, ShadingType, VerticalAlign, PageBreak,
} = require("docx");
const fs = require("fs");
const path = require("path");

const TOPIC = "mattpocock-skills";
const DISPLAY_TOPIC = "mattpocock/skills";
const DATE = "2026-07-06";
const AUTHOR = "程序员AI破局指南";
const OUTPUT_DIR = resolveOutputDir();
const ASSETS = path.resolve(__dirname, "../assets");

function resolveOutputDir() {
  if (process.env.TUTORIAL_GUIDE_OUTPUT_DIR) {
    return process.env.TUTORIAL_GUIDE_OUTPUT_DIR;
  }

  let dir = process.cwd();
  while (dir !== path.dirname(dir)) {
    if (path.basename(dir) === "kj-llm-wiki") {
      return path.join(dir, "raw", "papers");
    }
    dir = path.dirname(dir);
  }

  throw new Error("未找到 kj-llm-wiki 仓库根目录。请在 kj-llm-wiki 内运行脚本，或设置 TUTORIAL_GUIDE_OUTPUT_DIR。");
}

const C = {
  primary: "1A3A6B", accent: "2E75B6", accent2: "C45911",
  lightBg: "EBF3FB", headerBg: "1A3A6B",
  coverBg: "1A3A6B", coverSub: "A8CCEB", strip: "C45911",
  mutedText: "666666", white: "FFFFFF", black: "1A1A1A",
};

const chapters = [
  {
    title: "第一章  先搞清楚 mattpocock/skills 解决什么问题",
    intro: "我第一次看这个仓库时，差点把它当成“提示词合集”。后来读完 README 才发现，它真正想解决的是另一个问题：我们把 Agent 当实习生用，却很少给它稳定的工作方法。",
    sections: [
      {
        title: "1.1  它不是大而全流程，而是一组小工具",
        body: [
          "mattpocock/skills 的定位很明确：真实工程师每天用的 Agent Skills。它反对把流程全部交给一个巨大框架，因为大框架一旦跑偏，修起来也很重。",
          "这个仓库的技能都尽量做小。比如 `/grill-with-docs` 负责需求对齐和项目术语，`/tdd` 负责红绿重构，`/diagnosing-bugs` 负责复现、缩小、假设、埋点、修复、回归测试。",
          "新手最容易误会的一点是：装完这些技能，不代表 Agent 自动变聪明。真正有用的是你在合适的节点主动调用合适的 Skill。"
        ],
        list: ["需求不清时先用 grilling 类技能", "要写代码时让 TDD 约束反馈环", "Bug 很硬时切到 diagnosing-bugs", "项目变乱时用 architecture 技能做设计体检"],
        code: ["# 这个仓库的安装入口", "npx skills@latest add mattpocock/skills"],
        note: "💡小贴士：把它理解成“工程方法工具箱”，比理解成“提示词市场”更接近原作者的意图。",
        pitfall: "我当时踩的坑是直接想找“万能技能”。结果越找越乱。这个仓库更适合按场景拿工具：先对齐、再实现、再诊断、再治理。"
      },
      {
        title: "1.2  两类技能：你主动叫的，和模型自动拿的",
        body: [
          "README 里把技能分成 user-invoked 和 model-invoked。前者通常是你手动输入的命令，比如 `/grill-me`、`/setup-matt-pocock-skills`。后者是 Agent 在任务匹配时可以自动使用的纪律，比如 `tdd`、`codebase-design`、`code-review`。",
          "这个分法很重要。用户调用的技能像“流程入口”，模型调用的技能像“工作习惯”。一个用户技能可以引导模型技能，但不应该互相套来套去。"
        ],
        code: ["# 一个典型工作流", "/grill-with-docs", "/to-prd", "/to-issues", "# 然后在每个 issue 上使用 tdd / diagnosing-bugs"],
        note: "✅最佳实践：第一次用时先读 README 的 Reference 表，别急着全装全用。先挑 3 个高频入口就够了。",
        pitfall: "常见误区是把所有 Skill 都塞进一次对话里。表现通常是 Agent 开始长篇解释流程，但代码一点没动。我的习惯是一个阶段只让一个主技能主导。"
      }
    ]
  },
  {
    title: "第二章  安装与第一次配置",
    intro: "真正卡人的地方往往不是安装命令，而是装完以后不知道下一步做什么。我第一次给项目接 Skill 时，就漏跑了 setup，后面 triage 和 docs 相关命令全都缺上下文。",
    sections: [
      {
        title: "2.1  用 skills.sh 安装仓库",
        body: [
          "官方 README 给的 Quickstart 很短：运行 installer，选择需要的 skills 和目标编码 Agent，然后一定选中 `/setup-matt-pocock-skills`。",
          "安装命令依赖 Node 环境。终端里先确认 `node` 和 `npx` 可用，再执行安装。"
        ],
        list: ["确认 Node.js 已安装", "在你要使用技能的项目目录里运行安装命令", "选择 mattpocock/skills 中需要的技能", "确认选中 `/setup-matt-pocock-skills`"],
        code: ["node -v", "npx -v", "npx skills@latest add mattpocock/skills"],
        note: "⚠️注意：如果终端提示 `npx: command not found`，先安装 Node.js LTS，再重新打开终端。",
        pitfall: "一个真实报错是 `command not found: npx`。这不是 Skill 的问题，是 Node 工具链没准备好。先把 Node 装好，比在 Agent 里反复解释更省时间。"
      },
      {
        title: "2.2  跑一次 `/setup-matt-pocock-skills`",
        body: [
          "setup 会问三个关键问题：你用哪个 issue tracker、triage 标签怎么配、文档放在哪里。这一步决定后续 `/triage`、`/grill-with-docs`、ADR 和共享语言文档写到哪。",
          "如果你在团队项目里用，我建议文档目录选项目内的 `docs/` 或类似位置；个人实验项目可以先选本地文件。"
        ],
        code: ["/setup-matt-pocock-skills", "# 按提示选择：GitHub / Linear / local files", "# 设置 triage labels", "# 设置 docs 保存目录"],
        note: "✅最佳实践：setup 的答案最好和团队真实流程一致。别为了演示随便选，否则后面生成的 issue 和文档会散。",
        pitfall: "我见过的坑是装完直接用 `/triage`，然后 Agent 反问一堆本该 setup 里回答的问题。表现是流程启动了，但缺少 issue tracker 和标签配置。"
      }
    ]
  },
  {
    title: "第三章  用 `/grill-with-docs` 做需求对齐",
    intro: "很多 AI 编程翻车，不是模型不会写代码，而是它以为自己懂了。人也是这样。你说“做个权限系统”，每个人脑子里的权限系统都不一样。",
    sections: [
      {
        title: "3.1  先被追问，再开始写",
        body: [
          "`/grill-with-docs` 的价值是让 Agent 在动手前追问你，把模糊需求拆成具体决策。它比普通 `/grill-me` 多了一层：会沉淀项目语言、术语和重要决策。",
          "这一步一开始会有点烦，因为它会问细。但这正是它的价值。没问出来的问题，最后会变成返工。"
        ],
        code: ["/grill-with-docs", "我要给后台增加批量导入用户功能，支持 CSV 上传、字段校验、错误行下载。"],
        note: "💡小贴士：你可以把它当成一个不怕麻烦的产品同事。它问得越具体，后面代码越少跑偏。",
        pitfall: "常见误区是对 Agent 说“别问了，直接做”。短期看快，长期看最慢。典型后果是它默认了错误的边界，比如把同步导入写成了异步任务。"
      },
      {
        title: "3.2  共享语言比长解释更省 token",
        body: [
          "README 里举了一个很好的例子：把“课程章节文件系统落位后触发的一连串变化”浓缩成一个项目术语。共享语言不是为了显得高级，而是让人和 Agent 都少说废话。",
          "如果你的项目有大量业务黑话，把它们写进 `CONTEXT.md` 或类似文档。以后 Agent 看到这个词，就能直接进入正确语境。"
        ],
        list: ["术语名", "一句话定义", "反例或易混概念", "相关模块或文件", "典型场景"],
        code: ["# CONTEXT.md 示例", "## Materialization Cascade", "A lesson becoming real on disk triggers section ordering, metadata sync, and render cache updates."],
        note: "✅最佳实践：术语文档要短。一个术语如果要解释十行，通常说明你还没找到真正的名字。",
        pitfall: "我踩过的坑是把 glossary 写成百科全书。Agent 读完仍然抓不到重点。更好的写法是“名字 + 边界 + 代码位置”。"
      }
    ]
  },
  {
    title: "第四章  把想法变成 PRD 和 Issues",
    intro: "需求对齐后，最容易出现的新问题是：计划太大。Agent 一口吃下去，最后吐出来一坨看似完整、实际没法 review 的改动。",
    sections: [
      {
        title: "4.1  用 `/to-prd` 固化已经聊清楚的内容",
        body: [
          "`/to-prd` 不是重新访谈你，而是把当前对话已经形成的共识整理成 PRD。它适合在 grill 之后用，把目标、范围、模块、验收标准写下来。",
          "好的 PRD 不追求长，追求可执行。尤其要写清楚不做什么。"
        ],
        code: ["/to-prd", "# 让 Agent 基于当前对话生成 PRD，并发布到配置好的 issue tracker 或文档位置"],
        note: "💡小贴士：如果你发现 PRD 里有一堆“提升体验”“优化流程”，让 Agent 改成可观察的验收标准。",
        pitfall: "常见问题是 PRD 写得像宣传稿。表现是实现者看完不知道先改哪个文件，也不知道怎么判断完成。"
      },
      {
        title: "4.2  用 `/to-issues` 切成垂直切片",
        body: [
          "`/to-issues` 的重点是把一个计划拆成可以独立抓取的 issue。这里的关键词是 vertical slice，不是按前端、后端、测试横切。",
          "比如“批量导入用户”不要拆成“写 UI”“写接口”“写测试”。更适合拆成“上传 CSV 并解析前 10 行预览”“提交导入任务并显示状态”“下载错误行报告”。"
        ],
        list: ["每个 issue 都有用户可见结果", "每个 issue 都能独立验证", "每个 issue 都尽量小", "issue 之间依赖关系清楚"],
        code: ["/to-issues", "# 输入：已生成的 PRD 或当前计划", "# 输出：可独立实现的 issue 列表"],
        note: "✅最佳实践：一个 issue 如果只能在合并其他 5 个 issue 后验证，通常还没有切对。",
        pitfall: "我以前很爱按技术层拆任务，结果 review 时每个 PR 都“还不能跑”。Agent 更容易在这种结构里迷路。"
      }
    ]
  },
  {
    title: "第五章  用 `/tdd` 建反馈环",
    intro: "Agent 写代码最快的时候，也是它最容易自信犯错的时候。没有测试，它会把“看起来像对”当成“已经对”。",
    sections: [
      {
        title: "5.1  红绿重构不是仪式，是刹车系统",
        body: [
          "`/tdd` 强调 red-green-refactor：先写失败测试，再写实现让它通过，最后整理代码。对 Agent 来说，这个过程尤其重要，因为它需要真实反馈，而不是凭感觉续写。",
          "新手不用追求一开始就写完美测试。先写一个能失败、能证明问题存在的测试，就已经比直接改实现强很多。"
        ],
        code: ["# 示例：让 Agent 从失败测试开始", "/tdd", "修复用户导入时空邮箱没有报错的问题。先补一个失败测试，再实现修复。"],
        note: "💡小贴士：测试名要说业务行为，不要说实现细节。比如 `rejects rows with empty email` 比 `calls validateEmail` 更稳。",
        pitfall: "真实坑：Agent 有时会写一个永远通过的测试。表现是你故意把实现改坏，测试仍然绿。处理方式是让它先证明测试红过。"
      },
      {
        title: "5.2  每次只做一个垂直切片",
        body: [
          "TDD 最怕任务太大。你让 Agent 一次做完整导入系统，它会同时改 UI、服务、校验、状态和测试，失败时很难定位。",
          "我的习惯是把每个切片压到一个明确行为：输入是什么、输出是什么、错误是什么。"
        ],
        list: ["先选一个行为", "写失败测试", "跑测试确认失败原因对", "写最小实现", "跑测试通过", "重构命名和边界"],
        code: ["pnpm test -- user-import", "# 或者只跑相关测试文件", "pnpm vitest src/user-import/validate-csv.test.ts"],
        note: "✅最佳实践：让 Agent 在每轮结束时贴出测试命令和结果摘要。别只接受“测试已通过”这句话。",
        pitfall: "常见报错是测试环境缺 mock，比如 `ReferenceError: fetch is not defined`。不要急着改业务代码，先补测试环境或 mock。"
      }
    ]
  },
  {
    title: "第六章  用 `/diagnosing-bugs` 查硬 Bug",
    intro: "有些 Bug 不能靠多写几行代码解决。越修越乱时，说明你缺的不是灵感，是诊断流程。",
    sections: [
      {
        title: "6.1  复现、缩小、假设、埋点",
        body: [
          "`/diagnosing-bugs` 把调试拆成一个很朴素的循环：先复现，再缩小范围，再提出假设，再加日志或断点验证。这个顺序听起来慢，但比盲改快。",
          "我建议你把错误现场尽量完整给 Agent：输入、期望、实际、日志、最近改动、能否稳定复现。"
        ],
        code: ["/diagnosing-bugs", "页面保存后偶发回到列表页，但接口返回 200。请先复现和缩小范围，不要直接改。"],
        note: "⚠️注意：如果 Agent 一上来就要改 5 个文件，让它停下来先写“当前最小复现是什么”。",
        pitfall: "真实表现：Agent 看到 200 就以为后端没问题，直接改前端路由。结果根因是响应体字段 `success: false`。诊断流程能逼它先看事实。"
      },
      {
        title: "6.2  修完以后补回归测试",
        body: [
          "诊断不是到“代码能跑”就结束。最后一步应该是回归测试：把这次 Bug 变成一个以后能自动抓住的问题。",
          "如果这个 Bug 很难自动化，也至少写一条手动验证清单，放到 PR 描述里。"
        ],
        list: ["记录根因", "补最小回归测试", "跑相关测试", "说明为什么这个测试能防止复发"],
        code: ["pnpm test -- changed-feature", "pnpm lint", "# 手动验证：保存表单后停留在详情页，并显示成功 toast"],
        note: "✅最佳实践：修 Bug 的提交信息里写出根因，比只写 `fix bug` 更有价值。",
        pitfall: "我踩过的坑是修完没补测试，两周后同一个行为在另一个入口复发。Agent 跑得快，重复犯错也快。"
      }
    ]
  },
  {
    title: "第七章  让项目不变成一团乱",
    intro: "AI 编程最大的问题不是写不出代码，而是太能写代码。速度上来以后，架构债也会按倍速增长。",
    sections: [
      {
        title: "7.1  用 `/improve-codebase-architecture` 做体检",
        body: [
          "README 里提到，Agent 会加速软件熵。`/improve-codebase-architecture` 的用途就是扫描代码库，找那些能让模块更深、接口更小、边界更清楚的机会。",
          "我不会每天都跑，但在一个功能连续迭代几天后跑一次很有价值。它能把“这里有点乱”的感觉变成可讨论的报告。"
        ],
        code: ["/improve-codebase-architecture", "# 让 Agent 扫描当前代码库，生成可视化 HTML 报告，然后选择一个点继续 grill"],
        note: "💡小贴士：架构优化不要和业务功能混在一个 PR 里。先让报告列候选，再挑一个小点做。",
        pitfall: "常见误区是看到报告就全改。结果 PR 巨大，风险也巨大。我的习惯是一次只改一个边界。"
      },
      {
        title: "7.2  深模块、浅接口、可测试边界",
        body: [
          "这个仓库里的 `codebase-design` 倾向于用工程设计语言约束 Agent：模块应该把复杂行为藏在简单接口后面，边界要能测试。",
          "对新手来说，最实用的判断是：如果一个调用者为了完成普通操作要知道 5 个内部步骤，这个模块可能太浅了。"
        ],
        list: ["调用方看到的接口少", "内部规则集中", "测试能穿过公共接口验证行为", "命名来自项目共享语言"],
        code: ["// 不理想：调用方知道太多步骤", "parseCsv(file); validateRows(rows); normalizeRows(rows); submitRows(rows);", "", "// 更稳：模块暴露一个清楚动作", "importUsersFromCsv(file);"],
        note: "✅最佳实践：让 Agent 重构前先写“保持不变的外部行为”。这样不容易把架构整理变成功能改写。",
        pitfall: "真实坑是 Agent 把“抽象”理解成多建几个工具函数。函数变多不等于设计变好，调用方负担下降才算。"
      }
    ]
  },
  {
    title: "第八章  写和改自己的 Skill",
    intro: "用别人的 Skill 一段时间后，你一定会想改。别不好意思。这个仓库本来就鼓励 hack around and make them your own。",
    sections: [
      {
        title: "8.1  先改触发条件，再改流程",
        body: [
          "一个 Skill 最关键的是它什么时候该被用。触发条件太宽，Agent 会乱用；触发条件太窄，你又想不起来用它。",
          "我改 Skill 时会先看三件事：description 是否清楚、输入条件是否明确、完成标准是否可验证。"
        ],
        code: ["---", "name: my-debug-loop", "description: Use when a bug is reproducible but the root cause is unclear; force reproduce -> isolate -> instrument -> fix -> regression test.", "---"],
        note: "💡小贴士：description 要写“何时使用”，不要只写“这个 Skill 很有用”。",
        pitfall: "常见坏味道是 description 只写 `help with coding`。Agent 看到这种描述，几乎不知道什么时候该调用。"
      },
      {
        title: "8.2  把大段知识放进引用文件或脚本",
        body: [
          "Skill 不是越长越好。太长会稀释重点，也更容易藏进过时指令。复杂流程可以拆到 references，重复机械操作可以放 scripts。",
          "如果你的 Skill 需要生成固定格式文件，脚本比让 Agent 每次手写更稳。"
        ],
        list: ["SKILL.md 放触发条件和主流程", "references 放详细规范", "scripts 放可复跑操作", "examples 放好坏样例"],
        code: ["skills/my-skill/", "  SKILL.md", "  references/checklist.md", "  scripts/generate-report.js", "  examples/good-output.md"],
        note: "✅最佳实践：每次改 Skill 后，用一个小任务实测。Skill 是工作流代码，也需要回归验证。",
        pitfall: "我踩过的坑是把所有细节堆在 SKILL.md，最后 Agent 每次读完都抓不住主线。拆文件之后反而更稳定。"
      }
    ]
  },
  {
    title: "第九章  新手常见问题与排错",
    intro: "刚开始用 Skill，最挫败的不是报错，而是你分不清是安装问题、配置问题、还是用法问题。",
    sections: [
      {
        title: "9.1  安装类问题",
        body: [
          "如果 `npx skills@latest add mattpocock/skills` 失败，先不要怀疑仓库内容。优先检查 Node、网络、包管理器缓存和目标 Agent 是否支持 skills 安装。",
          "如果公司网络拦截 npm registry，可以换网络或配置代理。"
        ],
        code: ["node -v", "npx -v", "npm config get registry", "npx skills@latest add mattpocock/skills"],
        note: "⚠️注意：看到 `ENOTFOUND registry.npmjs.org`，通常是网络或 DNS，不是技能本身坏了。",
        pitfall: "典型报错：`ERR_PNPM_META_FETCH_FAIL` 或 `ENOTFOUND`。解决方向是网络和 registry，不是去改 Skill 文件。"
      },
      {
        title: "9.2  使用类问题",
        body: [
          "如果 Agent 变得很啰嗦，先检查是否缺共享语言文档。如果 Agent 总是跑偏，先用 grill 类技能重新对齐。如果 Agent 改完不稳定，把任务切小并使用 TDD。",
          "Skill 不是替你做判断的人。它更像一个固定工作法，帮你在关键节点少犯错。"
        ],
        list: ["跑偏：先 grill", "啰嗦：补共享语言", "代码不稳：用 TDD", "Bug 反复：用 diagnosing-bugs", "项目变乱：做 architecture scan"],
        code: ["# 一个排错决策表", "if requirement_unclear: /grill-with-docs", "if failing_behavior_unclear: /diagnosing-bugs", "if implementation_large: /to-issues + /tdd"],
        note: "✅最佳实践：每次只修一个问题类型。别同时要求 Agent 对齐需求、重构架构、修 Bug、写测试。",
        pitfall: "我见过最常见的问题是“一个提示词塞完所有目标”。这会让 Skill 的边界失效，最后谁也没主导流程。"
      }
    ]
  },
  {
    title: "第十章  推荐学习路线",
    intro: "如果你今天刚接触这个仓库，不需要一次学完所有 Skill。先把三条主线跑通：对齐、反馈、治理。",
    sections: [
      {
        title: "10.1  七天上手路线",
        body: [
          "第一天只安装和 setup。第二天拿一个真实小需求跑 `/grill-with-docs`。第三天把结果转成 PRD。第四天拆 issues。第五天用 `/tdd` 做一个小切片。第六天用 `/diagnosing-bugs` 处理一个真实 Bug。第七天回顾哪些流程对你最有用。",
          "别拿玩具项目练太久。Skill 的价值在真实约束里才明显。"
        ],
        list: ["Day 1：安装并 setup", "Day 2：用 grill 对齐一个真实需求", "Day 3：生成 PRD", "Day 4：拆成 issues", "Day 5：TDD 完成一个切片", "Day 6：诊断一个 Bug", "Day 7：整理自己的使用规则"],
        code: ["/setup-matt-pocock-skills", "/grill-with-docs", "/to-prd", "/to-issues", "/tdd", "/diagnosing-bugs"],
        note: "💡小贴士：学习路线的目标不是记命令，而是形成“什么时候该慢下来”的直觉。",
        pitfall: "新手容易一天内把所有 Skill 都试一遍。最后只记住命令名，没形成工作习惯。慢一点，反而学得快。"
      },
      {
        title: "10.2  什么时候该自己改 Skill",
        body: [
          "当你连续三次对同一个 Skill 做同样补充时，就该改 Skill 了。比如你每次都提醒 Agent 不要自动 force push，那就把这条写进本地版本。",
          "团队用 Skill 时更应该定期回顾。好 Skill 会越来越贴近项目，而不是永远停在通用模板。"
        ],
        code: ["# 一个简单规则", "如果同一句提醒说了 3 次，把它写进 Skill 或项目 AGENTS.md。"],
        note: "✅最佳实践：团队 Skill 要有 owner。没人维护的流程文档，很快就会变成摆设。",
        pitfall: "我以前把所有提醒都留在聊天里。换一个线程就丢。后来发现，能沉淀进 Skill 的经验，才算真正降低了下次成本。"
      }
    ]
  }
];

function p(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, size: opts.size || 24, color: opts.color || C.black, bold: !!opts.bold, font: "Arial" })],
    alignment: opts.align || AlignmentType.LEFT,
    spacing: { before: opts.before || 80, after: opts.after || 80, line: 330 },
    heading: opts.heading,
  });
}

function code(lines) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA }, columnWidths: [9360],
    rows: lines.map((line, i) => new TableRow({ children: [new TableCell({
      width: { size: 9360, type: WidthType.DXA },
      shading: { fill: "1E2A3A", type: ShadingType.CLEAR },
      margins: { top: 55, bottom: 55, left: 180, right: 180 },
      borders: {
        top: { style: i === 0 ? BorderStyle.SINGLE : BorderStyle.NONE, size: 1, color: "3A5070" },
        bottom: { style: i === lines.length - 1 ? BorderStyle.SINGLE : BorderStyle.NONE, size: 1, color: "3A5070" },
        left: { style: BorderStyle.SINGLE, size: 6, color: C.accent2 },
        right: { style: BorderStyle.SINGLE, size: 1, color: "3A5070" },
      },
      children: [new Paragraph({
        children: [new TextRun({ text: line || " ", font: "Courier New", size: 18, color: "A8FF60" })],
        spacing: { after: 0 },
      })],
    })] })),
  });
}

function note(text) {
  const warning = text.startsWith("⚠️");
  const best = text.startsWith("✅");
  return new Paragraph({
    children: [new TextRun({ text, size: 22, font: "Arial", color: C.black })],
    spacing: { before: 120, after: 120 },
    shading: { fill: warning ? "FEF9E7" : best ? "E6F4EA" : C.lightBg, type: ShadingType.CLEAR },
    border: { left: { style: BorderStyle.SINGLE, size: 16, color: warning ? "FBBC04" : best ? "34A853" : C.accent } },
    indent: { left: 240 },
  });
}

function listItem(text, numbered = false) {
  return new Paragraph({
    children: [new TextRun({ text, size: 23, font: "Arial" })],
    numbering: { reference: numbered ? "numbers" : "bullets", level: 0 },
    spacing: { before: 40, after: 40 },
  });
}

function qrCell(title, imageBuffer, desc, altName) {
  const none = { style: BorderStyle.NONE };
  return new TableCell({
    borders: { top: none, bottom: none, left: none, right: none },
    width: { size: 4680, type: WidthType.DXA },
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 200, bottom: 200, left: 200, right: 200 },
    children: [
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: title, bold: true, size: 24 })], spacing: { after: 160 } }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new ImageRun({ data: imageBuffer, transformation: { width: 144, height: 144 }, type: "jpg", altText: { title, description: desc, name: altName } })],
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: desc, size: 20, color: "5f6368" })], spacing: { before: 120 } }),
    ],
  });
}

function buildChildren() {
  const children = [
    p(`${DISPLAY_TOPIC} 完全新手指南`, { align: AlignmentType.CENTER, size: 72, bold: true, color: C.primary, before: 1800, after: 240 }),
    p("从零开始，手把手带你入门", { align: AlignmentType.CENTER, size: 36, color: "5f6368", after: 720 }),
    p(`作者：${AUTHOR}`, { align: AlignmentType.CENTER, size: 28 }),
    p(`日期：${DATE}`, { align: AlignmentType.CENTER, size: 24, color: "5f6368" }),
    new Paragraph({ children: [new PageBreak()] }),
    p("目录", { align: AlignmentType.CENTER, heading: HeadingLevel.HEADING_1, size: 36, bold: true, color: C.primary }),
    p("前言", { size: 26 }),
  ];

  for (const ch of chapters) {
    children.push(p(ch.title, { size: 26 }));
    for (const section of ch.sections) children.push(p(`  ${section.title}`, { size: 22, color: C.mutedText }));
  }

  children.push(new Paragraph({ children: [new PageBreak()] }));
  children.push(p("前言", { heading: HeadingLevel.HEADING_1 }));
  children.push(p("这份指南写给已经在用 Claude Code、Codex、Cursor 或其他编程 Agent，但总觉得“它很会写代码，却不总是会做工程”的人。"));
  children.push(p("mattpocock/skills 是 Matt Pocock 维护的一组 Agent Skills，核心思想不是让 Agent 变成万能机器，而是把真实工程里的对齐、反馈、诊断、架构治理这些习惯，变成可重复调用的工作流。"));
  children.push(note("💡小贴士：本文参考 mattpocock/skills GitHub README，重点按新手上手路线重新组织，不照搬官方描述。"));

  for (const ch of chapters) {
    children.push(p(ch.title, { heading: HeadingLevel.HEADING_1 }));
    children.push(p(ch.intro));
    for (const section of ch.sections) {
      children.push(p(section.title, { heading: HeadingLevel.HEADING_2 }));
      for (const line of section.body) children.push(p(line));
      if (section.list) section.list.forEach((item) => children.push(listItem(item)));
      if (section.code) children.push(code(section.code));
      children.push(note(section.note));
      children.push(note(`⚠️注意：${section.pitfall}`));
    }
  }

  const qrGzh = fs.readFileSync(path.join(ASSETS, "qr-gongzhonghao.jpg"));
  const qrSyh = fs.readFileSync(path.join(ASSETS, "qr-shipinhao.jpg"));
  children.push(new Paragraph({ children: [new PageBreak()] }));
  children.push(p("关注我，获取更多教程", { align: AlignmentType.CENTER, heading: HeadingLevel.HEADING_1, color: C.primary }));
  children.push(p("感谢阅读这份指南！如果对你有帮助，欢迎关注我的公众号和视频号，获取更多实用技术教程、工具测评和行业干货 🎉", { align: AlignmentType.CENTER }));
  children.push(new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [4680, 4680],
    rows: [new TableRow({ children: [
      qrCell("📱 公众号", qrGzh, "扫码关注，获取图文教程", "qr-gzh"),
      qrCell("📹 视频号", qrSyh, "扫码关注，获取视频教程", "qr-syh"),
    ] })],
  }));
  children.push(p("💬 有问题？欢迎在公众号后台留言，我会及时回复！", { align: AlignmentType.CENTER, before: 360 }));
  return children;
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 36, bold: true, color: C.primary, font: "Arial" },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 28, bold: true, color: C.accent, font: "Arial" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
    ],
  },
  numbering: { config: [
    { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  ] },
  sections: [{ properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } }, children: buildChildren() }],
});

function generateMarkdown() {
  const out = [
    "---",
    `title: ${DISPLAY_TOPIC} 完全新手指南`,
    `author: ${AUTHOR}`,
    `date: ${DATE}`,
    "---",
    "",
    `# ${DISPLAY_TOPIC} 完全新手指南`,
    "",
    "> 程序员康健 出品 · 公众号：程序员AI破局指南",
    "",
    "## 目录",
    "",
    "- [前言](#前言)",
  ];
  for (const ch of chapters) {
    out.push(`- [${ch.title}](#${ch.title.replace(/\s+/g, "-")})`);
    for (const section of ch.sections) out.push(`  - [${section.title}](#${section.title.replace(/\s+/g, "-")})`);
  }
  out.push("", "---", "", "## 前言", "", "这份指南写给已经在用 Claude Code、Codex、Cursor 或其他编程 Agent，但总觉得“它很会写代码，却不总是会做工程”的人。", "", "mattpocock/skills 是 Matt Pocock 维护的一组 Agent Skills，核心思想不是让 Agent 变成万能机器，而是把真实工程里的对齐、反馈、诊断、架构治理这些习惯，变成可重复调用的工作流。", "", "> 💡 **提示**：本文参考 mattpocock/skills GitHub README，重点按新手上手路线重新组织，不照搬官方描述。", "");

  for (const ch of chapters) {
    out.push(`## ${ch.title}`, "", ch.intro, "");
    for (const section of ch.sections) {
      out.push(`### ${section.title}`, "");
      section.body.forEach((line) => out.push(line, ""));
      if (section.list) section.list.forEach((item) => out.push(`- ${item}`));
      if (section.list) out.push("");
      if (section.code) out.push("```bash", ...section.code, "```", "");
      out.push(`> ${section.note}`, "");
      out.push(`> ⚠️ **注意**：${section.pitfall}`, "");
    }
  }
  out.push("---", "", "## 参考资料", "", "- [mattpocock/skills GitHub README](https://github.com/mattpocock/skills)", "- [skills.sh 上的 mattpocock/skills 页面](https://skills.sh/mattpocock/skills)", "", "## 关注我，获取更多教程", "", "感谢阅读这份指南！如果对你有帮助，欢迎关注我的公众号和视频号，获取更多实用技术教程、工具测评和行业干货。", "");
  return out.join("\n");
}

fs.mkdirSync(OUTPUT_DIR, { recursive: true });
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(path.join(OUTPUT_DIR, `${TOPIC}-完全新手指南.docx`), buf);
  fs.writeFileSync(path.join(OUTPUT_DIR, `${TOPIC}-完全新手指南.md`), generateMarkdown());
  console.log(`DOCX: ${path.join(OUTPUT_DIR, `${TOPIC}-完全新手指南.docx`)}`);
  console.log(`MD:   ${path.join(OUTPUT_DIR, `${TOPIC}-完全新手指南.md`)}`);
});
