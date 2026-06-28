---
name: local-stt-transcription
description: Transcribe local audio or video files into Chinese or multilingual text, SRT subtitles, JSON segments, or polished short-video transcripts using a local jianchang512/stt checkout, preferably without starting a server. Use when the user asks to convert local videos/audio to transcripts, short-video scripts, cleaned publishable drafts, subtitles, timed captions, or offline/private speech-to-text output.
---

# Local STT Transcription

Use this skill for local, offline-friendly speech-to-text with
`jianchang512/stt`, a faster-whisper based project. Prefer direct execution for
one-off transcriptions; use the Flask service only when it is already running or
the user explicitly wants a persistent local API.

## Strategy

- Default: use `medium` + terminology correction + light polish, and keep only
  the polished transcript as the final artifact.
- High accuracy: use `large-v3` + terminology correction + light polish, and
  keep only the polished transcript as the final artifact.
- Choose high accuracy when the user asks for `large`, `高精度`, `发布稿`,
  `重要内容`, or when the material has dense English terms, framework names, or
  paid-content/course reuse value.
- Do not assume a stronger STT model removes the need for correction. Always
  inspect and polish transcripts intended for reading or publishing.
- When a new recurring STT mistake is found, add it to
  `references/transcript-polish.md` so the skill improves over time.

## Workflow

1. Confirm the source media path exists. Accept local video or audio paths such
   as `.mov`, `.mp4`, `.m4a`, `.mp3`, `.wav`, `.aac`, `.flac`, and `.webm`.
2. Verify a `jianchang512/stt` checkout exists. If not, read `references/stt.md`
   and run `scripts/bootstrap_stt_runtime.sh` to prepare it.
3. Run `scripts/transcribe_with_stt.py` with `--direct-stt-root <stt-root>` by
   default. This bypasses the Flask service and directly uses the upstream
   project's faster-whisper code, models, and config.
4. Use the local STT service at `http://127.0.0.1:9977` only if it is already
   running or the user explicitly asks for an API/server workflow.
5. Choose the model and output format:
   - Use `--model medium` by default.
   - Use `--model large-v3` for high accuracy.
   - `--format text` for short-video text drafts.
   - `--format srt` for subtitles or edit timing.
   - `--format json` when downstream tooling needs segment structure.
6. Save final user-facing outputs outside temporary/cache directories. For this
   wiki, use `raw/studio/transcripts/` unless the user specifies another path.
7. If the user asks for a "短视频文字稿" or readable transcript, read
   `references/transcript-polish.md`, then create a polished `.md` export with:
   - source filename
   - language/model/format metadata
   - raw STT model used
   - corrected transcript body
   - optional SRT path when subtitles were generated
8. Do not keep raw STT drafts in the final output directory. If a raw transcript
   is needed for polishing, write it to a temporary path such as
   `/tmp/local-stt-transcription/<source-stem>-raw.md`, then remove it after the
   polished transcript is complete.

## Commands

Bootstrap runtime on a new machine:

```bash
bash /Users/chengkangjian/work/kj-skills/skills/local-stt-transcription/scripts/bootstrap_stt_runtime.sh \
  --stt-root "/Users/chengkangjian/work/stt"
```

Preview bootstrap actions:

```bash
bash /Users/chengkangjian/work/kj-skills/skills/local-stt-transcription/scripts/bootstrap_stt_runtime.sh \
  --stt-root "/Users/chengkangjian/work/stt" \
  --dry-run
```

Default temporary STT draft:

```bash
python3 .agents/skills/local-stt-transcription/scripts/transcribe_with_stt.py \
  --input "/path/to/video.mov" \
  --output "/tmp/local-stt-transcription/video-transcript-raw.md" \
  --language zh \
  --model medium \
  --format text \
  --direct-stt-root "/Users/chengkangjian/work/stt"
```

High-accuracy temporary STT draft:

```bash
python3 .agents/skills/local-stt-transcription/scripts/transcribe_with_stt.py \
  --input "/path/to/video.mov" \
  --output "/tmp/local-stt-transcription/video-transcript-large-v3-raw.md" \
  --language zh \
  --model large-v3 \
  --format text \
  --direct-stt-root "/Users/chengkangjian/work/stt" \
  --timeout 7200
```

Direct subtitle output:

```bash
python3 .agents/skills/local-stt-transcription/scripts/transcribe_with_stt.py \
  --input "/path/to/video.mov" \
  --output "raw/studio/transcripts/video.srt" \
  --language zh \
  --model medium \
  --format srt \
  --direct-stt-root "/Users/chengkangjian/work/stt"
```

## Defaults

- Use `language=zh` for Chinese unless the user specifies another language.
- Use `model=medium` by default for short-video transcripts.
- Use `large-v3` only for high-accuracy passes. On CPU it is slower and less
  portable, but can improve mixed Chinese/English terms.
- Use `base` only for fast drafts or low-resource machines.
- Use timeouts generously for long media; pass `--timeout 3600` when needed.

## Polishing

For final readable transcripts, do not stop at raw STT and do not preserve raw
STT drafts as final artifacts. Read `references/transcript-polish.md` and
produce a single polished transcript file, normally:

```text
raw/studio/transcripts/<source-stem>-文字稿.md
```

If the user explicitly asks to compare models or keep drafts, suffix files
clearly, for example `-raw.md`, `-medium.md`, or `-large-v3.md`. Preserve meaning
and cadence while correcting obvious recognition errors such as `5WH -> 5W2H`,
`Watt -> What`, `体效 -> 提效`, and `反攻 -> 返工`.

## Cohesion And Dependencies

Keep reusable automation inside this skill directory:

- Use `scripts/transcribe_with_stt.py` for STT execution.
- Use `scripts/bootstrap_stt_runtime.sh` for new-machine runtime setup.
- Use `references/stt.md` for setup/API/model notes.
- Use `references/transcript-polish.md` for correction rules.

The upstream `jianchang512/stt` checkout remains an external dependency because
it contains the application code, Python environment, Torch/faster-whisper
runtime, and downloaded model weights that can reach GB scale. Do not vendor
that project or model files into this skill. Instead, document the checkout path
with `--direct-stt-root`, typically `/Users/chengkangjian/work/stt`.

## Failure Handling

- If direct mode fails because the `stt` checkout or dependencies are missing,
  report the exact failure and point to `references/stt.md`.
- If API mode is requested and the STT service is unreachable, do not pretend
  transcription succeeded. Report that the local service must be started.
- If the API returns `code != 0`, report the returned `msg`.
- If the media path is outside the current workspace, request filesystem
  approval as needed instead of copying the file silently.

## Reference

Read `references/stt.md` when setup, dependency, API, model, or language details
are needed.
Read `references/transcript-polish.md` when choosing default vs high-accuracy
mode or producing a corrected/polished transcript.
