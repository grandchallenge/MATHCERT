#!/usr/bin/env bash
set -euo pipefail

real_landrun="${COMPARATOR_LANDRUN_REAL:-landrun-real}"
prefix=()

while (($#)); do
  case "$1" in
    --best-effort|-ldd|-add-exec)
      prefix+=("$1")
      shift
      ;;
    --ro|--rw|--rwx|--rox|--env)
      if (($# < 2)); then
        echo "landrun adapter: option $1 requires a value" >&2
        exit 64
      fi
      prefix+=("$1" "$2")
      shift 2
      ;;
    --)
      shift
      exec "$real_landrun" "${prefix[@]}" -- "$@"
      ;;
    *)
      exec "$real_landrun" "${prefix[@]}" -- "$@"
      ;;
  esac
done

echo "landrun adapter: missing child command" >&2
exit 64
