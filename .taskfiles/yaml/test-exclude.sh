#!/usr/bin/env bash

set -eo pipefail

SCRIPT_DIR="$(dirname "$0")"
EXCLUDE_ARGS=""

# Process arguments
while [[ $# -gt 0 ]]; do
  case "$1" in
    --exclude)
      if [[ -n "$2" ]]; then
        EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude $2"
        shift
      fi
      ;;
    --dry-run)
      DRY_RUN="--dry-run"
      ;;
    *)
      # Ignore other arguments
      ;;
  esac
  shift
done

echo "Exclude args: $EXCLUDE_ARGS"
echo "Dry run: $DRY_RUN"

echo "Would run: python3 ${SCRIPT_DIR}/standardize_yaml.py --dir ${SCRIPT_DIR}/../../kubernetes $EXCLUDE_ARGS $DRY_RUN"
