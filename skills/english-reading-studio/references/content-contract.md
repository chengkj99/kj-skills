# 内容数据格式 v1

UTF-8 JSON，根对象如下；可运行 `examples/sample.json` 是完整示例。所有文字使用纯文本，渲染器会转义 HTML。换行可保留列表、引用和代码的原貌。

```json
{
  "title": "文章标题",
  "author": "作者或未提供",
  "source": "URL、本地文件名或用户粘贴",
  "source_date": "原文日期或未核实",
  "overview": "中文导读",
  "conclusions": [{"text": "结论及限制", "paragraph_ids": ["p1"]}],
  "paragraphs": [{
    "id": "p1",
    "original": "英文原段落",
    "translation": "对应中文译文",
    "deep": {
      "meaning": "意思与必要解释",
      "role": "实际段落作用",
      "connection": "前后关系",
      "details": [{"label": "补充解释：术语", "text": "说明与归属"}],
      "question": "理解题",
      "answer": "参考答案及核对点"
    }
  }],
  "language": {
    "intro": "中文主题导入",
    "phrases": [{"text": "原文词组", "meaning": "语境含义", "paragraph_id": "p1", "example": "AI 编写的英文教学例句", "example_translation": "例句中文"}],
    "sentences": [{"paragraph_id": "p1", "original": "原文中的完整句子", "chunks": [{"text": "原句片段", "meaning": "片段含义"}], "explanation": "结构和含义说明"}],
    "exercises": [{"type": "choice", "paragraph_id": "p1", "prompt": "问题", "options": ["选项一", "选项二"], "answer": "选项一", "explanation": "为什么，依据在哪里"}],
    "review": ["明天的回忆问题"]
  }
}
```

- 段落 id 按顺序为 p1、p2……，不跳号；所有引用必须存在。
- deep.details 可为空；其他数组须有内容。每段均需翻译和精读。
- 训练句在对应原文中连续、逐字存在；chunks 拼接后忽略空白须与训练句相同，不能删除标点。
- exercise.type 为 choice、cloze 或 open；choice 的 answer 必须等于某一完整选项。其他题可省略 options。
- 结构验证只检查可判定条件，不校验译文准确、结论真假或读者水平。模型需单独审读。
- 渲染器拒绝覆盖已有 HTML；修订时保留旧版本并使用新的文件名。
- HTML 中复制追问包含目标段落及相邻上下文。题目输入不持久化，不依赖浏览器本地存储。
