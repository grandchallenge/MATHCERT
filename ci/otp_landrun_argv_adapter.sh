#!/usr/bin/env bash
set -euo pipefail

: "${REAL_LANDRUN:?REAL_LANDRUN must point to the exact landrun binary}"

prefix=()
while (($#)); do
  case "$1" in
    --best-effort|-ldd|--ldd|-add-exec|--add-exec|--ignore-missing|--unrestricted-network|--unrestricted-filesystem|--unrestricted-scoped|--log-disable-originating|--log-enable-subprocesses|--log-disable-subdomains)
      prefix+=("$1")
      shift
      ;;
    --ro|--rw|--rwx|--rox|--env|--unix|--bind-tcp|--connect-tcp|--log-level)
      if (($# < 2)); then
        printf 'landrun argv adapter: missing value for %s\n' "$1" >&2
        exit 64
      fi
      prefix+=("$1" "$2")
      shift 2
      ;;
    --)
      shift
      exec "$REAL_LANDRUN" "${prefix[@]}" -- "$@"
      ;;
    *)
      # Comparator appends the child executable directly after landrun options.
      # Insert an outer `--` so any `--` in the child argv survives landrun's
      # option parser. This is required by lean4export's `MODULE -- DECL...`
      # command line and changes no child argument bytes.
      exec "$REAL_LANDRUN" "${prefix[@]}" -- "$@"
      ;;
  esac
done

printf 'landrun argv adapter: no child command supplied\n' >&2
exit 64
