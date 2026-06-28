# Transcript Polish Reference

Use this reference after STT generation when the user wants a short-video
transcript, publishable draft, or cleaned content material.

## Default Strategy

- Default path: `medium` transcription + terminology correction + light polish.
- High-accuracy path: `large-v3` transcription + terminology correction + light
  polish.
- Use high accuracy when the user says `高精度`, `large`, `重要内容`, `发布稿`,
  or the material has dense English terms, framework names, tool names, or
  course/paid-content reuse value.

## Output Policy

Keep only the polished transcript as the final user-facing artifact by default.
Raw STT output is an intermediate working draft.

Write temporary raw STT drafts outside the final transcript directory, for
example:

```text
/tmp/local-stt-transcription/<source-stem>-raw.md
/tmp/local-stt-transcription/<source-stem>-large-v3-raw.md
```

Final polished outputs:

```text
raw/studio/transcripts/<source-stem>-文字稿.md
raw/studio/transcripts/<source-stem>-文字稿-large-v3.md
```

Only keep raw outputs when the user explicitly asks to compare models, debug
STT, or preserve the unedited transcript.

## Correction Priorities

Preserve the speaker's meaning and cadence. Correct obvious recognition errors,
but do not rewrite into a generic article unless the user asks.

1. Fix mixed Chinese/English framework words.
2. Fix AI/programming tool names.
3. Fix homophones created by speech recognition.
4. Add punctuation and paragraph breaks.
5. Remove filler only when it hurts readability.

## Common Term Map

Use context, not blind global replacement.

| STT error pattern | Preferred form |
| --- | --- |
| 5WH, 5W1H when context includes how much | 5W2H |
| 号, 好, How when discussing method | How |
| Y, why, Why | Why |
| Watt, what, What | What |
| token, Token | Token |
| 体效 | 提效 |
| 格度 | 额度 |
| 返攻, 反攻 | 返工 |
| ASO, AI搜, AI说 | AI |
| Claude code | Claude Code |
| closed code, Closed Code | Claude Code |
| cursor | Cursor |
| codex | Codex |
| PRD, p r d | PRD |
| 普洛会员 | Pro 会员 |
| opt, OPUS when context says Claude model | Opus |
| 海库 | Haiku |
| 三代彩, 三代采 | Sonnet |
| 上下微, 善亚威, 圣下威尼 | 上下文 |
| 绘画 when context is chat/session | 会话 |
| clear, Clear | `clear` |
| compact, Compact | `compact` |
| 拆废 | 拆分 |

## Publishable Transcript Shape

Use this structure for a cleaned Markdown transcript:

```markdown
# <source-stem> 文字稿（校对版）

- Source: `<source path>`
- STT Model: `<medium|large-v3>`
- Polish: `terminology correction + light readability edit`

## Transcript

<cleaned transcript>
```

## Quality Check

Before finishing:

- Search for likely leftovers: `5WH`, `Watt`, `体效`, `反攻`, `AI搜`, `号怎么做`,
  `closed code`, `海库`, `善亚威`, `圣下威尼`, `绘画`, `格度`, `拆废`.
- Compare suspicious phrases against the raw transcript context.
- Confirm the final transcript directory contains the polished artifact. Remove
  temporary raw drafts unless the user explicitly asked to keep them.

## Continuous Improvement

When a recurring STT error is discovered during polishing:

1. Add it to `Common Term Map`.
2. Add a search pattern to `Quality Check` if it is likely to recur.
3. Keep replacements contextual; never use blind global replacement for words
   that can be valid in other contexts.
