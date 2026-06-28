# jianchang512/stt Reference

Upstream project: https://github.com/jianchang512/stt

`jianchang512/stt` is a local speech-to-text web service based on
faster-whisper. It can transcribe video/audio into plain text, SRT subtitles,
or JSON. The service is useful when the user wants local/offline transcription
or hosted transcription is unavailable.

This skill does not vendor `jianchang512/stt`, Python dependencies, or model
weights. Keep them in an external checkout such as `/Users/chengkangjian/work/stt`
because the runtime includes Torch/faster-whisper and GB-scale model files.

## Local Setup

Requirements from upstream:

- Python 3.9 through 3.11
- `ffmpeg` and `ffprobe` available on PATH on Linux/macOS
- CPU is supported; Nvidia CUDA can be configured manually for acceleration

Preferred bootstrap on a new machine:

```bash
bash /Users/chengkangjian/work/kj-skills/skills/local-stt-transcription/scripts/bootstrap_stt_runtime.sh \
  --stt-root "/Users/chengkangjian/work/stt"
```

To preview without changing files:

```bash
bash /Users/chengkangjian/work/kj-skills/skills/local-stt-transcription/scripts/bootstrap_stt_runtime.sh \
  --stt-root "/Users/chengkangjian/work/stt" \
  --dry-run
```

Manual source deployment, if the bootstrap script is not appropriate:

```bash
git clone https://github.com/jianchang512/stt.git
cd stt
python3 -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
pip install 'numpy<2'
```

Starting the Flask service with `python start.py` is optional; this skill uses
direct execution by default and does not require a running service.

The service opens a local web UI and exposes its API at:

```text
http://127.0.0.1:9977/api
```

Models live under the upstream `models/` directory. The upstream README maps:

- `base` -> `models/models--Systran--faster-whisper-base`
- `small` -> `models/models--Systran--faster-whisper-small`
- `medium` -> `models/models--Systran--faster-whisper-medium`
- `large-v3` -> `models/models--Systran--faster-whisper-large-v3`

Use `medium` for the default transcript workflow. Use `large-v3` for
high-accuracy passes when the machine has enough resources and the user accepts
the extra runtime. Use `base` only for quick drafts or low-resource machines.

## API Contract

Endpoint:

```text
POST http://127.0.0.1:9977/api
```

Multipart fields:

- `file`: media file binary
- `language`: language code
- `model`: model name
- `response_format`: `text`, `json`, or `srt`

Successful JSON response:

```json
{
  "code": 0,
  "msg": "ok",
  "data": "recognized text or subtitles"
}
```

Nonzero `code` indicates failure; report `msg`.

## Language Codes

Common language codes:

- Chinese: `zh`
- English: `en`
- Japanese: `ja`
- Korean: `ko`
- French: `fr`
- German: `de`
- Spanish: `es`
- Russian: `ru`
- Portuguese: `pt`
- Vietnamese: `vi`
- Arabic: `ar`
- Turkish: `tr`

## Notes

- Chinese may occasionally be returned as Traditional Chinese depending on the
  model result.
- CPU transcription can be slow on long videos.
- Do not use `large-v3` casually on CPU-only machines; it can exhaust memory.
