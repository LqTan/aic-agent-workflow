#!/usr/bin/env bash
# Kill any running AIC backend processes.
#
# Targets:
#   * processes whose cmdline matches "aic-dev" or "uvicorn app.main"
#   * processes bound to APP_PORT (default 8000)
#
# Usage:
#   ./scripts/kill_app.sh

set -u

PORT="${APP_PORT:-8000}"
echo "Scanning for AIC backend processes (port=${PORT})..."

PATTERNS=("aic-dev" "uvicorn app.main")
PIDS=()

for pattern in "${PATTERNS[@]}"; do
    while IFS= read -r pid; do
        [[ -n "$pid" ]] && PIDS+=("$pid")
    done < <(pgrep -f "$pattern" 2>/dev/null)
done

# Also catch anything bound to the port.
if command -v ss >/dev/null 2>&1; then
    port_pids=$(ss -ltnp "sport = :${PORT}" 2>/dev/null \
        | grep -oP 'pid=\K[0-9]+' || true)
elif command -v lsof >/dev/null 2>&1; then
    port_pids=$(lsof -ti ":${PORT}" 2>/dev/null || true)
fi

[[ -n "${port_pids:-}" ]] && PIDS+=($port_pids)

# Deduplicate + drop self.
UNIQUE_PIDS=($(printf '%s\n' "${PIDS[@]}" | sort -u | grep -v "^$$\$" || true))

if [[ ${#UNIQUE_PIDS[@]} -eq 0 ]]; then
    echo "  no running processes found."
    exit 1
fi

for pid in "${UNIQUE_PIDS[@]}"; do
    comm="$(cat /proc/${pid}/comm 2>/dev/null || echo '?')"
    if kill -TERM "$pid" 2>/dev/null; then
        echo "  + sent SIGTERM to pid=${pid} (${comm})"
    else
        echo "  ! no permission to kill pid=${pid}"
    fi
done
