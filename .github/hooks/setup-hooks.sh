#!/bin/bash
# ===========================================================
# HistArch hook setup script
# Automatically links Git hooks into .git/hooks/
# ===========================================================

set -e

# Ensure we're in the repo root
REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo "")"
if [ -z "$REPO_ROOT" ]; then
  echo "❌ Not inside a git repository."
  exit 1
fi

HOOK_SRC_DIR="$REPO_ROOT/.github/hooks"
HOOK_DEST_DIR="$REPO_ROOT/.git/hooks"

echo "🔧 Installing Git hooks from $HOOK_SRC_DIR to $HOOK_DEST_DIR"

# List of hooks you want to install
HOOKS=("post-checkout" "post-merge")

for hook in "${HOOKS[@]}"; do
  SRC="$HOOK_SRC_DIR/$hook"
  DEST="$HOOK_DEST_DIR/$hook"

  if [ -f "$SRC" ]; then
    echo "➡️  Installing $hook hook..."
    ln -sf "../../.github/hooks/$hook" "$DEST"
    chmod +x "$SRC"
  else
    echo "⚠️  Hook file $SRC not found, skipping."
  fi
done

echo "✅ Git hooks installed successfully!"
