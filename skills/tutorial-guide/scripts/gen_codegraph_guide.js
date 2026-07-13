const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, AlignmentType, LevelFormat, BorderStyle, WidthType,
  ShadingType, VerticalAlign, PageBreak,
} = require("docx");
const fs = require("fs");
const path = require("path");

const TOPIC = "codegraph";
const DISPLAY_TOPIC = "colbymchenry/codegraph";
const DATE = "2026-07-08";
const AUTHOR = "程序员AI破局指南";
const ASSETS = path.resolve(__dirname, "../assets");
const OUTPUT_DIR = resolveOutputDir();

const C = {
  primary: "0D3B6E", accent: "0969DA", accent2: "7C3AED",
  lightBg: "E8F4FD", headerBg: "0D3B6E",
  coverBg: "0D3B6E", coverSub: "87CEEB", strip: "0969DA",
  mutedText: "334155", white: "FFFFFF", black: "0F172A",
};

const sources = [
  "GitHub README: https://github.com/colbymchenry/codegraph",
  "官方文档站: https://colbymchenry.github.io/codegraph/",
  "npm package: @colbymchenry/codegraph",
];

const chapters = [
  {
    title: "第一章  先搞懂 CodeGraph 解决的真实问题",
    intro: "我第一次看 CodeGraph 的 README 时，最打动我的不是“省 token”，而是它把 Agent 最浪费时间的一步拿掉了：一遍遍 grep、Read、猜调用链。",
    sections: [
      {
        title: "1.1  它不是另一个聊天插件",
        body: [
          "CodeGraph 是一个本地优先的代码智能工具。它会把项目预先索引成知识图谱，里面有文件、符号、调用边、依赖关系和全文搜索索引。",
          "Agent 想理解代码时，不再从零开始翻文件，而是直接问图谱：这个函数在哪里、谁调用它、它会影响哪些地方、某条业务流怎么走。",
          "这和普通搜索的区别很大。grep 能找到字符串，CodeGraph 试图找到结构。比如接口实现、回调、React 重渲染、跨语言桥接这类关系，单靠文本搜索很容易漏。"
        ],
        list: ["本地索引项目代码", "通过 MCP 暴露给 Claude Code、Codex、Cursor 等 Agent", "用 `codegraph_explore` 返回相关源码、调用路径和影响半径", "文件变化后自动同步图谱"],
        code: ["# 一句话体验入口", "npx @colbymchenry/codegraph"],
        note: "💡小贴士：把 CodeGraph 理解成“给 Agent 用的代码地图”，比理解成“更快的 grep”更准确。",
        pitfall: "我当时的误区是期待它替代所有阅读。后来发现最合理的用法是：先让 CodeGraph 找结构，再对正在编辑的少量文件做人工级确认。"
      },
      {
        title: "1.2  什么时候值得装",
        body: [
          "如果你的项目只有十几个文件，CodeGraph 的收益不会特别夸张。README 也说得很实在：成本节省在小项目上会比较小，真正稳定的收益是速度和精准上下文。",
          "项目一旦超过几百个文件，尤其有跨模块调用、Web 路由、服务层、数据层，Agent 的探索成本会明显上升。这个时候，预索引的价值就出来了。"
        ],
        list: ["你经常问“这个流程怎么走”", "Agent 每次都要先读十几个文件", "代码里有多语言、框架路由或回调", "改一个函数前想知道影响面"],
        code: ["# 典型问题", "codegraph explore \"How does a request reach the database?\""],
        note: "✅最佳实践：小项目先别追求省钱，先用它减少 Agent 的无效探索。大项目再认真评估 token 和团队成本。",
        pitfall: "常见踩坑是装完以后仍然让 Agent 自己 grep 一圈。这样就把 CodeGraph 的优势吃掉了。提示词里要明确：结构问题先问 CodeGraph。"
      }
    ]
  },
  {
    title: "第二章  安装 CLI 与第一次接入 Agent",
    intro: "安装 CodeGraph 最容易漏的点是：装 CLI、接入 Agent、初始化项目是三件事。少做其中一步，表面看装好了，实际 Agent 还是用不上。",
    sections: [
      {
        title: "2.1  用官方安装脚本或 npm 安装",
        body: [
          "官方推荐的 macOS / Linux 安装方式是一行 curl。它会拉取适合你系统的自包含构建，不要求你本机已经有 Node.js。",
          "如果你已经有 Node，也可以用 npm 安装 `@colbymchenry/codegraph`。这个包提供 `codegraph` 命令。"
        ],
        list: ["macOS / Linux 用 install.sh", "Windows PowerShell 用 install.ps1", "Node 用户可直接 npm 全局安装", "安装后重新打开终端，让 PATH 生效"],
        code: [
          "# macOS / Linux",
          "curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh",
          "",
          "# 或者已有 Node.js 时",
          "npm i -g @colbymchenry/codegraph"
        ],
        note: "⚠️注意：安装器会把 `codegraph` 放到 PATH，但它不会修改当前已经打开的 shell。装完以后新开一个终端再继续。",
        pitfall: "真实报错通常是 `codegraph: command not found`。先别怀疑安装失败，先新开终端，或者检查 `echo $PATH`。"
      },
      {
        title: "2.2  用 `codegraph install` 接入 Agent",
        body: [
          "CLI 安装只是把命令放到机器上。要让 Claude Code、Codex CLI、Cursor、Gemini CLI 等 Agent 能用，还要运行 `codegraph install`。",
          "这个命令会检测你机器上的 Agent，并把 CodeGraph MCP server 写进对应配置。官方 README 特别强调：这一步只负责接入 Agent，不会索引任何项目。"
        ],
        code: ["codegraph install", "# 非交互场景", "codegraph install --target=codex,claude --yes", "# 只打印某个 Agent 配置片段", "codegraph install --print-config codex"],
        note: "✅最佳实践：团队脚本里可以用 `--target` 和 `--yes` 固化安装选择，个人机器第一次用交互模式更稳。",
        pitfall: "我见过最常见的误会是：跑完 `codegraph install` 就问 Agent 项目结构。结果 Agent 仍然提示没有索引，因为你还没在项目里跑 `codegraph init`。"
      }
    ]
  },
  {
    title: "第三章  给项目建立第一张代码图谱",
    intro: "CodeGraph 真正开始工作的时刻，是你在项目根目录执行 `codegraph init`。这一步像给仓库拍一张结构 CT。",
    sections: [
      {
        title: "3.1  在每个项目里运行 `codegraph init`",
        body: [
          "`codegraph init` 会在当前项目创建本地 `.codegraph/` 目录，并完成第一次全量索引。这个目录就是 Agent 后续查询的本地知识图谱。",
          "一个全局安装可以服务很多项目，但每个项目都要单独初始化。你切到另一个仓库时，那里没有 `.codegraph/`，Agent 就不会凭空有图谱。"
        ],
        code: ["cd your-project", "codegraph init", "ls -la .codegraph"],
        note: "💡小贴士：把 `.codegraph/` 当成本地缓存。通常不需要提交到 Git，具体按团队规范处理。",
        pitfall: "常见问题是你在父目录跑了 init，但真正代码在子目录。表现是索引很快完成，Agent 却查不到业务文件。处理方式是在真实项目根目录重新跑。"
      },
      {
        title: "3.2  用 `codegraph status` 看索引状态",
        body: [
          "初始化后，先跑一次 `codegraph status`。它能告诉你当前索引是否可用、是否有待同步文件。",
          "官方 README 提到，如果自动同步还有 pending 文件，状态里会出现 Pending sync。Agent 查询命中未同步文件时，也会收到显式提示。"
        ],
        code: ["codegraph status", "# 如果看到 pending 文件，稍等 debounce 完成，或手动同步", "codegraph sync"],
        note: "✅最佳实践：在大改之前跑一次 `status`，比对话中发现图谱过期更省心。",
        pitfall: "如果你在 sandbox 或特殊环境里禁用了 watcher，图谱不会自动刷新。表现是 Agent 看到旧代码。这个时候手动跑 `codegraph sync`。"
      }
    ]
  },
  {
    title: "第四章  让 Agent 正确使用 `codegraph_explore`",
    intro: "装好工具以后，真正影响体验的是一句话：结构问题先问 CodeGraph，别让 Agent 又走回 grep + Read 的老路。",
    sections: [
      {
        title: "4.1  什么问题适合 explore",
        body: [
          "`codegraph_explore` 是默认暴露的核心 MCP 工具。它适合回答“X 怎么工作”“请求从 A 怎么走到 B”“改这个符号会影响哪里”这类结构问题。",
          "返回结果通常包括相关源码、按文件分组的符号、调用路径、关系图和影响范围。对 Agent 来说，这相当于一次拿到整理好的上下文包。"
        ],
        list: ["解释某个模块工作流", "找一个功能入口", "追踪调用链", "改动前做影响分析", "快速扫一个目录或领域"],
        code: [
          "codegraph explore \"How does authentication work?\"",
          "codegraph explore \"What calls createUser?\"",
          "codegraph explore \"Impact of changing src/auth/session.ts\""
        ],
        note: "💡小贴士：问题里加文件名、符号名或业务词，会让返回更准。别只问“讲讲这个项目”。",
        pitfall: "常见误区是让子 Agent 去探索。README 提到，CodeGraph 只有被直接查询才有帮助；如果子 Agent 仍然读文件，优势就会被稀释。"
      },
      {
        title: "4.2  MCP 工具和 CLI 命令怎么对应",
        body: [
          "MCP 默认主要显示 `codegraph_explore`。其他工具如 node、search、callers、callees、impact、files、status 仍可用，只是默认不全部列在 MCP 表面。",
          "如果你需要更多 MCP 工具，可以设置 `CODEGRAPH_MCP_TOOLS`。日常使用里，我建议先让 Agent 用 explore，必要时再扩展。"
        ],
        code: [
          "# 重新暴露部分 MCP 工具",
          "CODEGRAPH_MCP_TOOLS=explore,node,search,callers codegraph serve --mcp",
          "",
          "# CLI 侧也有对应能力",
          "codegraph callers createUser",
          "codegraph impact createUser"
        ],
        note: "✅最佳实践：新手阶段别急着打开所有工具。一个 `explore` 覆盖大多数结构问题，认知负担最低。",
        pitfall: "如果 Agent 提示没有 `.codegraph/` 索引，不是 MCP 坏了，而是当前项目没初始化。回到第三章检查项目根目录。"
      }
    ]
  },
  {
    title: "第五章  自动同步与“图谱会不会过期”",
    intro: "我最开始担心 CodeGraph 的点是：Agent 一边改代码，一边查图谱，图谱会不会落后？官方设计里专门处理了这个问题。",
    sections: [
      {
        title: "5.1  文件 watcher 会自动更新索引",
        body: [
          "当 Agent 启动 `codegraph serve --mcp` 时，CodeGraph 会通过系统文件事件监听源码变化。macOS 用 FSEvents，Linux 用 inotify，Windows 用 ReadDirectoryChangesW。",
          "默认有一个 debounce 窗口，README 写的是 2000ms，可通过 `CODEGRAPH_WATCH_DEBOUNCE_MS` 调整，并限制在 100ms 到 60s 之间。"
        ],
        code: [
          "# 调整同步防抖时间",
          "CODEGRAPH_WATCH_DEBOUNCE_MS=1000 codegraph serve --mcp",
          "",
          "# 查看是否有待同步文件",
          "codegraph status"
        ],
        note: "💡小贴士：大批量格式化或代码生成时，debounce 能把很多文件变化合并成一次索引，别急着手动 sync。",
        pitfall: "如果你保存后立刻提问，可能正好撞上 pending 窗口。CodeGraph 会提示某些文件未同步，这时候让 Agent 直接 Read 这些文件即可。"
      },
      {
        title: "5.2  重新连接时会做 catch-up",
        body: [
          "如果 MCP server 断开期间你做了 `git pull` 或在另一个编辑器里改了代码，下次连接时 CodeGraph 会做一次快速对账。",
          "它会用文件大小、mtime 和内容 hash 和工作区同步，避免 Agent 一上线就拿旧图谱回答。"
        ],
        code: ["git pull --rebase", "# 下一次 Agent / MCP 连接时会 catch up", "codegraph status"],
        note: "✅最佳实践：长时间切分支后，先跑 `codegraph status`，看到图谱正常再问结构问题。",
        pitfall: "常见问题是切分支后忘了看状态。表现是 Agent 回答里混入旧分支文件。遇到这种情况，先 `codegraph sync`，再继续。"
      }
    ]
  },
  {
    title: "第六章  配置 include、exclude 与自定义扩展名",
    intro: "CodeGraph 默认很省心，但项目一复杂，总有些目录你不想索引，也有些被忽略的源代码你又想拉回来。",
    sections: [
      {
        title: "6.1  默认会跳过哪些东西",
        body: [
          "CodeGraph 默认跳过依赖、构建、缓存目录，比如 `node_modules`、`vendor`、`dist`、`build`、`target`、`.venv`、`Pods`、`.next` 等。",
          "它也会尊重 `.gitignore`，并跳过超过 1MB 的大文件。这个默认很关键，因为你通常想索引自己的代码，不想把第三方依赖和构建产物塞进图谱。"
        ],
        code: [
          "# 推荐：先用 .gitignore 管住普通噪音",
          "dist/",
          "coverage/",
          ".codegraph/"
        ],
        note: "💡小贴士：能用 `.gitignore` 表达的排除规则，先放 `.gitignore`。CodeGraph 会跟着读。",
        pitfall: "如果把生成代码提交进仓库，`.gitignore` 可能管不到。表现是索引慢、结果噪音大。这时用 `codegraph.json` 的 exclude。"
      },
      {
        title: "6.2  用 `codegraph.json` 做项目级微调",
        body: [
          "如果某个已提交目录不该进图谱，可以在项目根目录加 `codegraph.json`，用 gitignore 风格的 `exclude` 排除。",
          "反过来，如果真实源码因为 `.gitignore` 被隐藏，也可以用 `include` 拉回来。对非标准扩展名，使用 `extensions` 映射到支持的语言。"
        ],
        code: [
          "{",
          "  \"exclude\": [\"static/\", \"**/vendor/**\"],",
          "  \"include\": [\"Tools/\"],",
          "  \"extensions\": {",
          "    \".tpl\": \"php\",",
          "    \".dota_lua\": \"lua\"",
          "  }",
          "}"
        ],
        note: "⚠️注意：改了扩展名映射后，重新跑 `codegraph index` 或 `codegraph init`，让新规则生效。",
        pitfall: "常见报错不是崩溃，而是 warning：语言名拼错或 JSON 格式不对。CodeGraph 会跳过错误配置，不会强行中断索引。"
      }
    ]
  },
  {
    title: "第七章  语言、框架路由与跨语言桥接",
    intro: "CodeGraph 比“函数搜索”更有意思的地方，是它知道很多框架和语言的结构，不只是把文件切成文本块。",
    sections: [
      {
        title: "7.1  多语言结构提取",
        body: [
          "README 列出的语言覆盖很广：TypeScript、JavaScript、Python、Go、Rust、Java、C#、PHP、Ruby、C/C++、Swift、Kotlin、Scala、Dart、Vue、Svelte、Astro、Terraform、Nix 等。",
          "这背后依赖 Tree-sitter 解析真实 AST。也就是说，它不只是搜关键字，而是尽量识别符号、定义、引用和调用边。"
        ],
        list: ["前端仓库：TypeScript、JavaScript、Vue、Svelte、Astro", "后端仓库：Python、Go、Java、Rust、C#", "移动仓库：Swift、Objective-C、Kotlin、Dart", "基础设施：Terraform / OpenTofu、Nix"],
        code: ["codegraph explore \"Find the API route for creating users\""],
        note: "✅最佳实践：多语言项目里先问“从 JS 调用到 native 的路径”，这正是 CodeGraph 比 grep 更有优势的地方。",
        pitfall: "别把语言支持理解成语义完美。跨语言桥接里会有 heuristic 边，Agent 应该知道这类边是推断出来的。"
      },
      {
        title: "7.2  框架路由和移动端桥接",
        body: [
          "CodeGraph 能识别不少 Web 框架路由：Django、Flask、FastAPI、Express、NestJS、Laravel、Rails、Spring、Gin、Axum、ASP.NET、SvelteKit、Nuxt、Astro 等。",
          "移动端方面，它关注 Swift 与 Objective-C 桥接、React Native legacy bridge、TurboModules、Fabric view components、Expo Modules、native 到 JS event channel。"
        ],
        code: [
          "codegraph explore \"Which route handles POST /users?\"",
          "codegraph explore \"How does NativeModules.Camera.open reach native code?\""
        ],
        note: "💡小贴士：路由问题尽量带 HTTP method 和路径，移动端问题尽量带 JS 调用名或 native module 名。",
        pitfall: "常见误区是只搜 controller 名。文件式路由或装饰器路由里，入口可能不是你以为的文件名。直接问 URL 到 handler 更准。"
      }
    ]
  },
  {
    title: "第八章  在真实开发里怎么提问",
    intro: "工具装好了，提问方式不对，Agent 还是会绕远路。CodeGraph 最适合的是带目标的结构查询。",
    sections: [
      {
        title: "8.1  从“讲讲项目”改成“追一条流”",
        body: [
          "“讲讲这个项目”太宽，CodeGraph 也只能给你概览。更好的问题是从一个用户动作、接口、函数或错误现场出发。",
          "比如登录失败、订单提交、CSV 导入、权限判断、WebSocket 推送，这些都可以变成一条可追踪的流。"
        ],
        list: ["入口是什么", "期望终点是什么", "你关心调用链还是影响面", "是否限定某个目录或文件"],
        code: [
          "codegraph explore \"Trace login from POST /api/login to session creation\"",
          "codegraph explore \"What breaks if I change validateCsvRow?\""
        ],
        note: "✅最佳实践：一个好问题最好包含动词。比如 trace、find callers、impact、route to handler。",
        pitfall: "如果 Agent 返回一堆不相关文件，通常不是工具坏了，而是问题太泛。收窄到路径、符号或错误文本。"
      },
      {
        title: "8.2  改代码前先做影响分析",
        body: [
          "我建议把 CodeGraph 放到“改之前”的环节，而不是“改坏以后”的补救环节。尤其是共享工具函数、权限逻辑、支付/风控链路，先看调用方很值得。",
          "影响分析不是让你不改，而是让你知道哪里要测，哪里要小心。"
        ],
        code: [
          "codegraph explore \"Impact radius of changing src/lib/permissions.ts\"",
          "# 然后让 Agent 基于影响面列测试清单",
          "pnpm test -- permissions"
        ],
        note: "💡小贴士：影响分析结果可以直接变成 PR 测试计划。这样 review 人也更容易相信改动边界。",
        pitfall: "常见坑是只看直接调用方。真正出问题的经常是二级调用或路由入口。让 CodeGraph 展开到业务流，而不是只列一层 callers。"
      }
    ]
  },
  {
    title: "第九章  常见错误与排查清单",
    intro: "新工具的挫败感通常来自三类问题：命令找不到、索引没建好、Agent 没接上。按这个顺序排，比乱试快。",
    sections: [
      {
        title: "9.1  命令与安装问题",
        body: [
          "如果终端不认识 `codegraph`，先确认安装方式、PATH 和当前 shell。官方 README 明确说安装器不会影响当前 shell，所以重开终端是第一步。",
          "如果 npm 安装失败，再检查 Node 版本和网络。package.json 当前声明 Node engine 是 `>=20.0.0 <25.0.0`，但库模式用 Node 22.5+ 的内置 sqlite 更稳。"
        ],
        code: ["which codegraph", "codegraph --version", "node -v", "npm view @colbymchenry/codegraph version"],
        note: "⚠️注意：CLI 和 MCP server 使用自包含运行时；把 CodeGraph 当库嵌入你自己的 Node 进程时，才更需要关注 Node 版本。",
        pitfall: "报错 `Cannot find module '@colbymchenry/codegraph'` 通常是你在写库模式代码，但项目里没安装 npm 包。CLI 可用不等于你的应用依赖里有这个包。"
      },
      {
        title: "9.2  Agent 看不到 CodeGraph",
        body: [
          "如果 Agent 没有 CodeGraph 工具，检查三件事：是否跑过 `codegraph install`、是否重启 Agent、当前项目是否有 `.codegraph/`。",
          "如果 MCP 已接上但项目没索引，Agent 应该会给出清晰提示，让你先初始化。"
        ],
        code: [
          "codegraph install --print-config codex",
          "cd your-project",
          "test -d .codegraph && echo indexed || echo missing",
          "codegraph status"
        ],
        note: "✅最佳实践：把“安装 CLI、接 Agent、初始化项目、重启 Agent”写成团队 onboarding 清单。",
        pitfall: "我最常见的漏步是忘记重启 Agent。MCP 配置已经写进去了，但当前会话没加载，所以工具列表里还是没有。"
      }
    ]
  },
  {
    title: "第十章  学习路线与团队落地",
    intro: "CodeGraph 不应该变成又一个“装了但不用”的工具。要让它发挥价值，最好从一个真实痛点开始，而不是从全员推广开始。",
    sections: [
      {
        title: "10.1  个人学习路线",
        body: [
          "第一天先在一个熟悉项目里装好，跑 `init`，问三类问题：找入口、追调用链、看影响面。你熟悉项目，所以能判断答案准不准。",
          "第二阶段再放到陌生项目。陌生项目里，CodeGraph 的价值会更明显，但也更需要你对结果保持工程判断。"
        ],
        list: ["第 1 天：安装并初始化一个熟悉项目", "第 2 天：用它追 3 条真实业务流", "第 3 天：改一个小函数前做影响分析", "第 1 周：总结哪些问题最适合 CodeGraph"],
        code: [
          "codegraph explore \"Where does user import start?\"",
          "codegraph explore \"Trace createUser from route to database\"",
          "codegraph explore \"Impact of changing normalizeUserInput\""
        ],
        note: "💡小贴士：用熟悉项目校准工具，比一上来丢给陌生大仓库更容易建立判断力。",
        pitfall: "别用一次不准就否定工具。先看问题是否太泛、索引是否新、目录是否排除了源码。"
      },
      {
        title: "10.2  团队落地建议",
        body: [
          "团队里最适合从两个场景开始：新人理解代码和高风险改动前的影响分析。这两个场景收益明确，也不强迫所有人改变开发习惯。",
          "等大家熟悉以后，再把 CodeGraph 查询结果纳入 PR 描述：我改了什么、影响到哪些调用方、我测了哪些路径。"
        ],
        list: ["在 README 或 AGENTS.md 加 CodeGraph 使用约定", "为核心仓库初始化图谱", "把影响分析加入 PR 模板", "收集团队常用查询句式"],
        code: [
          "## PR 检查项示例",
          "- [ ] 已用 CodeGraph 查看核心符号影响面",
          "- [ ] 已覆盖影响路径的自动/手动测试"
        ],
        note: "✅最佳实践：先让两三个愿意尝试的人跑通，再沉淀查询模板。别一开始就要求全员强制使用。",
        pitfall: "推广工具最怕变成口号。没有绑定具体场景，大家很快会忘。绑定 onboarding 和 PR 风险评估，才容易留下来。"
      }
    ]
  }
];

function resolveOutputDir() {
  if (process.env.TUTORIAL_GUIDE_OUTPUT_DIR) return process.env.TUTORIAL_GUIDE_OUTPUT_DIR;
  let dir = process.cwd();
  while (dir !== path.dirname(dir)) {
    if (path.basename(dir) === "kj-llm-wiki") return path.join(dir, "raw", "papers");
    dir = path.dirname(dir);
  }
  throw new Error("未找到 kj-llm-wiki 仓库根目录。请在 kj-llm-wiki 内运行脚本，或设置 TUTORIAL_GUIDE_OUTPUT_DIR。");
}

function run(text, opts = {}) {
  return new TextRun({ text, font: opts.font || "Arial", size: opts.size || 24, bold: opts.bold, italics: opts.italics, color: opts.color || C.black });
}

function p(text, opts = {}) {
  return new Paragraph({
    alignment: opts.align || AlignmentType.LEFT,
    heading: opts.heading,
    spacing: { before: opts.before ?? 80, after: opts.after ?? 120, line: 330 },
    children: [run(text, opts)],
  });
}

function noteBox(text) {
  const isWarn = text.startsWith("⚠️");
  const isBest = text.startsWith("✅");
  const fill = isWarn ? "FEF9E7" : isBest ? "E6F4EA" : C.lightBg;
  const color = isWarn ? "FBBC04" : isBest ? "34A853" : C.accent;
  return new Paragraph({
    shading: { fill, type: ShadingType.CLEAR },
    border: { left: { style: BorderStyle.SINGLE, size: 16, color } },
    spacing: { before: 100, after: 140 },
    indent: { left: 220 },
    children: [run(text, { color: C.black })],
  });
}

function code(lines) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: lines.map((line, i) => new TableRow({
      children: [new TableCell({
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
          spacing: { after: 0 },
          children: [new TextRun({ text: line || " ", font: "Courier New", size: 18, color: "A8FF60" })],
        })],
      })],
    })),
  });
}

function bullet(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    spacing: { before: 20, after: 60 },
    children: [run(text)],
  });
}

function qrCell(title, img, desc, altName) {
  return new TableCell({
    borders: {
      top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE },
      left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE },
    },
    width: { size: 4680, type: WidthType.DXA },
    verticalAlign: VerticalAlign.CENTER,
    margins: { top: 200, bottom: 200, left: 200, right: 200 },
    children: [
      new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [run(title, { bold: true, size: 24, color: C.primary })] }),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { after: 120 },
        children: [new ImageRun({ data: img, transformation: { width: 144, height: 144 }, type: "jpg", altText: { title, description: desc, name: altName } })],
      }),
      new Paragraph({ alignment: AlignmentType.CENTER, children: [run(desc, { size: 20, color: C.mutedText })] }),
    ],
  });
}

function buildChildren() {
  const qrGzh = fs.readFileSync(path.join(ASSETS, "qr-gongzhonghao.jpg"));
  const qrSyh = fs.readFileSync(path.join(ASSETS, "qr-shipinhao.jpg"));
  const children = [];

  children.push(
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 1200, after: 260 }, children: [run(`${DISPLAY_TOPIC} 完全新手指南`, { size: 44, bold: true, color: C.primary })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 360 }, children: [run("从零开始，手把手带你入门", { size: 28, color: C.mutedText })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [run(`作者：${AUTHOR}`, { size: 24 })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 900 }, children: [run(`日期：${DATE}`, { size: 22, color: C.mutedText })] }),
    noteBox("💡小贴士：这份指南基于 CodeGraph 官方 README、文档站和 npm package 信息整理，重点放在个人和团队如何真正用起来。"),
    new Paragraph({ children: [new PageBreak()] }),
    new Paragraph({ alignment: AlignmentType.CENTER, heading: "Heading1", children: [run("目录", { size: 36, bold: true, color: C.primary })] }),
    p("前言", { size: 26 }),
  );
  chapters.forEach((ch) => {
    children.push(p(ch.title, { size: 26 }));
    ch.sections.forEach((s) => children.push(p(`  ${s.title}`, { size: 22, color: C.mutedText, after: 40 })));
  });
  children.push(
    p("参考来源", { size: 26 }),
    p("关注我，获取更多教程", { size: 26 }),
    new Paragraph({ children: [new PageBreak()] }),
    p("前言", { heading: "Heading1", size: 36, bold: true, color: C.primary }),
    p("CodeGraph 是一个面向 AI 编程 Agent 的本地代码知识图谱工具。它把代码库里的符号、调用关系、文件和路由预先组织好，让 Agent 不必每次都从 grep、glob、Read 开始探索。"),
    p("这份指南适合三类读者：已经在用 Claude Code、Codex、Cursor 等 Agent 的开发者；维护中大型项目、希望降低 AI 探索成本的团队；以及想理解“代码知识图谱 + MCP”怎么落到日常开发的人。"),
    p("我会按真实上手顺序写：先理解价值，再安装接入，再初始化项目，最后讲提问方式、配置、排错和团队落地。")
  );

  chapters.forEach((ch) => {
    children.push(p(ch.title, { heading: "Heading1", size: 36, bold: true, color: C.primary }));
    children.push(p(ch.intro, { italics: true, color: C.mutedText }));
    ch.sections.forEach((s) => {
      children.push(p(s.title, { heading: "Heading2", size: 28, bold: true, color: C.accent }));
      s.body.forEach((line) => children.push(p(line)));
      if (s.list) s.list.forEach((item) => children.push(bullet(item)));
      if (s.code) children.push(code(s.code));
      if (s.note) children.push(noteBox(s.note));
      children.push(noteBox(`⚠️注意：${s.pitfall}`));
    });
  });

  children.push(
    p("参考来源", { heading: "Heading1", size: 36, bold: true, color: C.primary }),
    ...sources.map((s) => bullet(s)),
    new Paragraph({ children: [new PageBreak()] }),
    new Paragraph({ alignment: AlignmentType.CENTER, heading: "Heading1", children: [run("关注我，获取更多教程", { size: 36, bold: true, color: C.primary })] }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 100, after: 260 }, children: [run("感谢阅读这份指南！如果对你有帮助，欢迎关注我的公众号和视频号，获取更多实用技术教程、工具测评和行业干货。", { size: 24, color: C.black })] }),
    new Table({
      width: { size: 9360, type: WidthType.DXA },
      columnWidths: [4680, 4680],
      rows: [new TableRow({ children: [
        qrCell("📱 公众号", qrGzh, "扫码关注，获取图文教程", "qr-gzh"),
        qrCell("📹 视频号", qrSyh, "扫码关注，观看视频教程", "qr-syh"),
      ] })],
    }),
    new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 300 }, children: [run("💬 有问题？欢迎在公众号后台留言，我会及时回复！", { size: 22, color: C.mutedText })] })
  );
  return children;
}

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
    "---",
    "",
    "## 目录",
    "",
    "- [前言](#前言)",
    ...chapters.flatMap((ch) => [
      `- [${ch.title}](#${slug(ch.title)})`,
      ...ch.sections.map((s) => `  - [${s.title}](#${slug(s.title)})`)
    ]),
    "- [参考来源](#参考来源)",
    "- [关注我，获取更多教程](#关注我获取更多教程)",
    "",
    "---",
    "",
    "## 前言",
    "",
    "CodeGraph 是一个面向 AI 编程 Agent 的本地代码知识图谱工具。它把代码库里的符号、调用关系、文件和路由预先组织好，让 Agent 不必每次都从 grep、glob、Read 开始探索。",
    "",
    "这份指南适合三类读者：已经在用 Claude Code、Codex、Cursor 等 Agent 的开发者；维护中大型项目、希望降低 AI 探索成本的团队；以及想理解“代码知识图谱 + MCP”怎么落到日常开发的人。",
    "",
    "我会按真实上手顺序写：先理解价值，再安装接入，再初始化项目，最后讲提问方式、配置、排错和团队落地。",
    "",
  ];

  chapters.forEach((ch) => {
    out.push(`## ${ch.title}`, "", ch.intro, "");
    ch.sections.forEach((s) => {
      out.push(`### ${s.title}`, "");
      s.body.forEach((line) => out.push(line, ""));
      if (s.list) s.list.forEach((item) => out.push(`- ${item}`));
      if (s.list) out.push("");
      if (s.code) out.push("```bash", ...s.code, "```", "");
      if (s.note) out.push(`> ${s.note.replace("小贴士：", "**小贴士**：").replace("注意：", "**注意**：").replace("最佳实践：", "**最佳实践**：")}`, "");
      out.push(`> ⚠️ **注意**：${s.pitfall}`, "");
    });
  });

  out.push("## 参考来源", "", ...sources.map((s) => `- ${s}`), "", "---", "", "## 关注我，获取更多教程", "", "感谢阅读这份指南！如果对你有帮助，欢迎关注我的公众号和视频号，获取更多实用技术教程、工具测评和行业干货。", "", "- 公众号：程序员AI破局指南", "- 视频号：程序员AI破局指南", "", "有问题？欢迎在公众号后台留言，我会及时回复！", "");
  return out.join("\n");
}

function slug(title) {
  return title.replace(/\s+/g, "-").replace(/[\/]/g, "").toLowerCase();
}

const doc = new Document({
  styles: {
    default: { document: { run: { font: "Arial", size: 24 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 36, bold: true, color: C.primary, font: "Arial" }, paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { size: 28, bold: true, color: C.accent, font: "Arial" }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
      { reference: "numbers", levels: [{ level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    children: buildChildren(),
  }],
});

fs.mkdirSync(OUTPUT_DIR, { recursive: true });
Packer.toBuffer(doc).then((buf) => {
  const docxPath = path.join(OUTPUT_DIR, `${TOPIC}-完全新手指南.docx`);
  const mdPath = path.join(OUTPUT_DIR, `${TOPIC}-完全新手指南.md`);
  fs.writeFileSync(docxPath, buf);
  fs.writeFileSync(mdPath, generateMarkdown());
  console.log(`DOCX: ${docxPath}`);
  console.log(`MD:   ${mdPath}`);
});
