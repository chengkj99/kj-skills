#!/usr/bin/env bash
# Wiki Intelligence: SessionStart hook
# Removes stale session state files (TTL 24h)

HOOKS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${HOOKS_DIR}/lib/wiki-intelligence.sh"

trap 'exit 0' ERR

wi_load_config
[ "$WI_ENABLED" = "true" ] || exit 0

wi_cleanup_stale_state

exit 0
