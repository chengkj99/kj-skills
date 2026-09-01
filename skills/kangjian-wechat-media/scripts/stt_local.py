#!/usr/bin/env python3
"""用本地 faster-whisper 模型转写音视频，不访问 Hugging Face。"""

from __future__ import annotations

import argparse
import os
import subprocess
import tempfile
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")


def extract_wav(input_path: Path, wav_path: Path) -> None:
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-ar",
        "16000",
        "-ac",
        "1",
        "-vn",
        str(wav_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr[-400:] or "ffmpeg 提取音频失败")


def transcribe_file(input_path: Path, model_dir: Path, language: str) -> str:
    from faster_whisper import WhisperModel

    model = WhisperModel(
        str(model_dir),
        device="cpu",
        compute_type="int8",
        local_files_only=True,
    )
    with tempfile.TemporaryDirectory() as tmp:
        wav_path = Path(tmp) / f"{input_path.stem}.wav"
        extract_wav(input_path, wav_path)
        segments, _info = model.transcribe(
            str(wav_path),
            language=language,
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=False,
        )
        texts = [segment.text.strip() for segment in segments if segment.text.strip()]
    return "\n".join(texts)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--model-dir", default=str(Path.home() / "work/stt/models/faster-whisper-medium"))
    parser.add_argument("--language", default="zh")
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()
    text = transcribe_file(input_path, Path(args.model_dir), args.language)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        f"# {input_path.stem} 文字稿\n\n"
        f"- Source: `{input_path}`\n"
        f"- Language: `{args.language}`\n"
        f"- Model: `medium`\n"
        f"- Format: `text`\n\n"
        "## Transcript\n\n"
        f"{text}\n",
        encoding="utf-8",
    )
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
