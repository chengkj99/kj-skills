#!/usr/bin/env python3
"""Transcribe a local media file through jianchang512/stt."""

from __future__ import annotations

import argparse
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path


def build_multipart(fields: dict[str, str], file_path: Path) -> tuple[bytes, str]:
    boundary = f"----codex-local-stt-{uuid.uuid4().hex}"
    chunks: list[bytes] = []

    for name, value in fields.items():
        chunks.append(f"--{boundary}\r\n".encode())
        chunks.append(
            f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
        )
        chunks.append(str(value).encode())
        chunks.append(b"\r\n")

    mime = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
    chunks.append(f"--{boundary}\r\n".encode())
    chunks.append(
        (
            f'Content-Disposition: form-data; name="file"; '
            f'filename="{file_path.name}"\r\n'
        ).encode()
    )
    chunks.append(f"Content-Type: {mime}\r\n\r\n".encode())
    chunks.append(file_path.read_bytes())
    chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    return b"".join(chunks), boundary


def call_stt(
    endpoint: str,
    input_path: Path,
    language: str,
    model: str,
    response_format: str,
    timeout: int,
) -> dict:
    fields = {
        "language": language,
        "model": model,
        "response_format": response_format,
    }
    body, boundary = build_multipart(fields, input_path)
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = response.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        raise RuntimeError(
            f"Could not reach local stt service at {endpoint}. "
            "Start jianchang512/stt with `python start.py` first. "
            f"Original error: {exc}"
        ) from exc

    try:
        return json.loads(payload)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"stt service returned non-JSON response: {payload[:500]}") from exc


def call_stt_direct(
    stt_root: Path,
    input_path: Path,
    language: str,
    model: str,
    response_format: str,
):
    """Use jianchang512/stt internals without starting the local Flask server."""
    if not (stt_root / "start.py").is_file():
        raise RuntimeError(f"stt root does not contain start.py: {stt_root}")

    original_cwd = Path.cwd()
    sys.path.insert(0, str(stt_root))
    os.chdir(stt_root)
    try:
        from start import _api_process  # type: ignore
        from stslib import cfg, tool  # type: ignore

        tmp_dir = Path(cfg.TMP_DIR)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        wav_file = tmp_dir / f"{input_path.stem}-{uuid.uuid4().hex}.wav"
        result = tool.runffmpeg(
            ["-i", str(input_path), "-ar", "16000", "-ac", "1", str(wav_file)]
        )
        if result != "ok":
            raise RuntimeError(f"ffmpeg extraction failed: {result}")
        return _api_process(
            model_name=model,
            wav_file=str(wav_file),
            language=language,
            response_format=response_format,
        )
    finally:
        os.chdir(original_cwd)


def write_output(
    output_path: Path,
    input_path: Path,
    language: str,
    model: str,
    response_format: str,
    data,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if response_format == "json":
        text = json.dumps(data, ensure_ascii=False, indent=2)
    elif output_path.suffix.lower() == ".md":
        text = (
            f"# {input_path.stem} 文字稿\n\n"
            f"- Source: `{input_path}`\n"
            f"- Language: `{language}`\n"
            f"- Model: `{model}`\n"
            f"- Format: `{response_format}`\n\n"
            "## Transcript\n\n"
            f"{data}\n"
        )
    else:
        text = str(data)

    output_path.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Transcribe local audio/video with jianchang512/stt."
    )
    parser.add_argument("--input", required=True, help="Local audio/video file path")
    parser.add_argument("--output", required=True, help="Output .md/.txt/.srt/.json path")
    parser.add_argument("--endpoint", default="http://127.0.0.1:9977/api")
    parser.add_argument("--language", default="zh")
    parser.add_argument("--model", default="medium")
    parser.add_argument(
        "--format",
        choices=["text", "json", "srt"],
        default="text",
        dest="response_format",
    )
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument(
        "--direct-stt-root",
        help="Path to a jianchang512/stt checkout; bypasses the Flask API and runs local internals directly.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = Path(args.output).expanduser().resolve()

    if not input_path.is_file():
        print(f"Input file does not exist: {input_path}", file=sys.stderr)
        return 2

    try:
        if args.direct_stt_root:
            data = call_stt_direct(
                Path(args.direct_stt_root).expanduser().resolve(),
                input_path,
                args.language,
                args.model,
                args.response_format,
            )
        else:
            result = call_stt(
                args.endpoint,
                input_path,
                args.language,
                args.model,
                args.response_format,
                args.timeout,
            )
            if result.get("code") != 0:
                print(f"stt API failed: {result.get('msg', result)}", file=sys.stderr)
                return 1
            data = result.get("data", "")
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    write_output(
        output_path,
        input_path,
        args.language,
        args.model,
        args.response_format,
        data,
    )
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
