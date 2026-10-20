# English Reading Studio

输入英文文章，生成一份可离线打开的 HTML，切换全文双语、逐段精读和英语练习。

## 调用

```text
用 english-reading-studio 把这篇英文生成三模式阅读材料：<文件或正文>
```

也可说明“多数段落需要中文帮助”“这次只练几个重要句子”“我已经能流畅阅读”。缺省采用较充分的中文支持，不需要先测英语等级。

## 交付

- `content-vN.json`：可修改的原文、译文、解释与练习。
- `reader-vN.html`：单文件离线阅读页，打开即可使用。

页面支持模式切换、段落导航、字号、译文显隐、折叠答案和复制上下文追问。开放题由读者自查或回到 AI 对话讨论；页面输入关闭或刷新后不保存。模板使用系统字体，无远程依赖。

## 本地生成示例

```bash
python3 scripts/render.py examples/sample.json --check
python3 scripts/render.py examples/sample.json --output /tmp/reading-example.html
python3 -m unittest discover -s tests -v
```

脚本只渲染已经生成的内容，不自动调用模型。需要 Python 3.10+。若输出已存在，请使用新的版本文件名。

原始教学示例与数字为自编，用于展示结构，不能作为真实研究证据。第一版支持文本及其换行，不提供图片/OCR/复杂公式引擎；模型应先取得可信正文并说明影响理解的缺口。
