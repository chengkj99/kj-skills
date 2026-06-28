#!/usr/bin/env bash
# Bootstrap the external jianchang512/stt runtime used by this skill.

set -euo pipefail

STT_ROOT="${STT_ROOT:-$HOME/work/stt}"
STT_REPO="${STT_REPO:-https://github.com/jianchang512/stt.git}"
PYTHON_BIN="${PYTHON_BIN:-python3}"
SKIP_INSTALL=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  bootstrap_stt_runtime.sh [options]

Options:
  --stt-root PATH      External jianchang512/stt checkout path.
                       Default: $STT_ROOT or $HOME/work/stt
  --python PATH        Python executable for venv creation. Default: python3
  --skip-install       Clone/check only; do not install Python packages.
  --dry-run            Print planned actions without changing files.
  -h, --help           Show this help.

Environment:
  STT_ROOT             Same as --stt-root.
  STT_REPO             Git repo URL. Default: https://github.com/jianchang512/stt.git
  PYTHON_BIN           Same as --python.

Notes:
  - Requires git and Python 3.9-3.11.
  - Requires ffmpeg/ffprobe on PATH; install with Homebrew on macOS:
      brew install ffmpeg
  - Model files are downloaded by faster-whisper on first transcription.
EOF
}

log() {
  printf '[local-stt-bootstrap] %s\n' "$*"
}

run() {
  if [ "$DRY_RUN" -eq 1 ]; then
    printf '[dry-run] '
    printf '%q ' "$@"
    printf '\n'
  else
    "$@"
  fi
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --stt-root)
      STT_ROOT="$2"
      shift 2
      ;;
    --python)
      PYTHON_BIN="$2"
      shift 2
      ;;
    --skip-install)
      SKIP_INSTALL=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

case "$STT_ROOT" in
  "~"|"~/"*)
    STT_ROOT="${STT_ROOT/#\~/$HOME}"
    ;;
esac

command -v git >/dev/null 2>&1 || {
  echo "git is required but was not found on PATH." >&2
  exit 1
}

command -v "$PYTHON_BIN" >/dev/null 2>&1 || {
  echo "Python executable not found: $PYTHON_BIN" >&2
  exit 1
}

if ! command -v ffmpeg >/dev/null 2>&1 || ! command -v ffprobe >/dev/null 2>&1; then
  echo "ffmpeg and ffprobe are required but were not both found on PATH." >&2
  echo "On macOS, install them with: brew install ffmpeg" >&2
  exit 1
fi

PY_VERSION="$("$PYTHON_BIN" - <<'PY'
import sys
print(f"{sys.version_info.major}.{sys.version_info.minor}")
PY
)"

case "$PY_VERSION" in
  3.9|3.10|3.11)
    ;;
  *)
    echo "jianchang512/stt expects Python 3.9-3.11; got $PY_VERSION from $PYTHON_BIN." >&2
    exit 1
    ;;
esac

log "stt root: $STT_ROOT"
log "python: $PYTHON_BIN ($PY_VERSION)"

if [ -e "$STT_ROOT" ] && [ ! -d "$STT_ROOT/.git" ]; then
  echo "Target exists but is not a git checkout: $STT_ROOT" >&2
  exit 1
fi

if [ ! -d "$STT_ROOT/.git" ]; then
  run mkdir -p "$(dirname "$STT_ROOT")"
  run git clone "$STT_REPO" "$STT_ROOT"
else
  log "checkout already exists"
fi

if [ "$SKIP_INSTALL" -eq 1 ]; then
  log "skip install requested"
  exit 0
fi

VENV_PY="$STT_ROOT/venv/bin/python"
VENV_PIP="$STT_ROOT/venv/bin/pip"

if [ ! -x "$VENV_PY" ]; then
  run "$PYTHON_BIN" -m venv "$STT_ROOT/venv"
else
  log "venv already exists"
fi

run "$VENV_PIP" install -r "$STT_ROOT/requirements.txt"
run "$VENV_PIP" install 'numpy<2'

log "runtime ready"
log "python: $VENV_PY"
log "models: $STT_ROOT/models"
