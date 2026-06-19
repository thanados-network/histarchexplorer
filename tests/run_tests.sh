#!/bin/bash

# Script to run tests in batches to avoid timeouts
# Usage: ./tests/run_tests.sh [quick|parallel|full|batch]

MODE=${1:-quick}

case $MODE in
  quick)
    echo "Running quick tests (excluding slow)..."
    uv run pytest -m "not slow"
    ;;
  parallel)
    echo "Running quick tests in parallel..."
    uv run pytest -m "not slow" -n auto --dist loadfile
    ;;
  full)
    echo "Running all tests..."
    uv run pytest -m ""
    ;;
  batch)
    echo "Running tests in batches (file by file)..."
    for f in tests/test_*.py; do
      echo "Running $f..."
      uv run pytest "$f" || exit 1
    done
    ;;
  *)
    echo "Unknown mode: $MODE"
    echo "Usage: $0 [quick|parallel|full|batch]"
    exit 1
    ;;
esac
