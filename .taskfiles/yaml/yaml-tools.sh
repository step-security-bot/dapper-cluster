#!/usr/bin/env bash
# Simple wrapper script for YAML standardization and validation tools

set -eo pipefail

SCRIPT_DIR="$(dirname "$0")"
YAML_SCRIPT="${SCRIPT_DIR}/standardize_yaml.py"

function show_usage {
  echo "Usage: yaml-tools.sh [command] [options]"
  echo ""
  echo "Commands:"
  echo "  diff <file>            - Show diff of standardization changes for a single file"
  echo "  diff-all               - Show diff of standardization changes for all YAML files"
  echo "  validate <file>        - Validate a single YAML file"
  echo "  validate-all           - Validate all YAML files"
  echo "  standardize <file>     - Standardize a single YAML file"
  echo "  standardize-all        - Standardize all YAML files"
  echo "  verify <file>          - Verify standardization (diff + validate)"
  echo "  verify-all             - Verify standardization for all files (diff-all + validate-all)"
  echo ""
  echo "Options:"
  echo "  --exclude <pattern>    - Exclude files matching pattern (for *-all commands)"
  echo "  --dry-run              - Show what would be done without making changes"
  echo ""
}

# Check if Python script exists
if [[ ! -f "$YAML_SCRIPT" ]]; then
  echo "Error: standardize_yaml.py script not found at $YAML_SCRIPT"
  exit 1
fi

# Check if ruamel.yaml is installed
if ! pip list | grep -q ruamel.yaml; then
  echo "Error: ruamel.yaml package is not installed. Run: pip install ruamel.yaml"
  exit 1
fi

# Set default kubernetes directory
KUBERNETES_DIR="$(cd "$SCRIPT_DIR/../../kubernetes" && pwd)"

# Parse command
if [[ $# -lt 1 ]]; then
  show_usage
  exit 1
fi

COMMAND="$1"
shift

case "$COMMAND" in
  diff)
    if [[ $# -lt 1 || "$1" == "--"* ]]; then
      echo "Error: Missing file path"
      show_usage
      exit 1
    fi
    FILE_PATH="$1"
    shift
    "$YAML_SCRIPT" --file "$FILE_PATH" --diff --dry-run
    ;;

  diff-all)
    EXCLUDE_ARGS=""
    DRY_RUN="--dry-run"

    # Process arguments
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --exclude)
          if [[ -n "$2" ]]; then
            EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude $2"
            shift
          fi
          ;;
      esac
      shift
    done

    "$YAML_SCRIPT" --dir "$KUBERNETES_DIR" --diff $DRY_RUN $EXCLUDE_ARGS
    ;;

  validate)
    if [[ $# -lt 1 || "$1" == "--"* ]]; then
      echo "Error: Missing file path"
      show_usage
      exit 1
    fi
    FILE_PATH="$1"
    shift
    "$YAML_SCRIPT" --file "$FILE_PATH" --validate --dry-run
    ;;

  validate-all)
    EXCLUDE_ARGS=""
    DRY_RUN="--dry-run"

    # Process arguments
    while [[ $# -gt 0 ]]; do
      case "$1" in
        --exclude)
          if [[ -n "$2" ]]; then
            EXCLUDE_ARGS="$EXCLUDE_ARGS --exclude $2"
            shift
          fi
          ;;
      esac
      shift
    done

    "$YAML_SCRIPT" --dir "$KUBERNETES_DIR" --validate $DRY_RUN $EXCLUDE_ARGS
    ;;

  standardize)
    if [[ $# -lt 1 || "$1" == "--"* ]]; then
      echo "Error: Missing file path"
      show_usage
      exit 1
    fi
    FILE_PATH="$1"
    shift
    "$YAML_SCRIPT" --file "$FILE_PATH"
    ;;

  standardize-all)
    EXCLUDE_ARGS=""
    DRY_RUN=""

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
      esac
      shift
    done

    "$YAML_SCRIPT" --dir "$KUBERNETES_DIR" $DRY_RUN $EXCLUDE_ARGS
    ;;

  verify)
    if [[ $# -lt 1 || "$1" == "--"* ]]; then
      echo "Error: Missing file path"
      show_usage
      exit 1
    fi
    FILE_PATH="$1"
    shift

    echo "=== Showing diff ==="
    "$YAML_SCRIPT" --file "$FILE_PATH" --diff --dry-run
    echo ""
    echo "=== Validating file ==="
    "$YAML_SCRIPT" --file "$FILE_PATH" --validate --dry-run
    echo ""
    echo "If validation passed, you can safely standardize the file with: yaml-tools.sh standardize $FILE_PATH"
    ;;

  verify-all)
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
      esac
      shift
    done

    echo "=== Showing diffs ==="
    "$YAML_SCRIPT" --dir "$KUBERNETES_DIR" --diff --dry-run $EXCLUDE_ARGS
    echo ""
    echo "=== Validating files ==="
    "$YAML_SCRIPT" --dir "$KUBERNETES_DIR" --validate --dry-run $EXCLUDE_ARGS
    echo ""
    echo "If validation passed, you can safely standardize all files with: yaml-tools.sh standardize-all"
    ;;

  *)
    echo "Error: Unknown command '$COMMAND'"
    show_usage
    exit 1
    ;;
esac
