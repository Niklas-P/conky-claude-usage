#!/usr/bin/env bash
# Claude Code Usage — Conky Widget Installer
# Installs the data-fetch script and Conky config to their expected locations.
# Run from any directory: bash install.sh

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing Claude Code Conky widget..."

# 1. Python fetch/format script
install -D -m 755 "$SCRIPT_DIR/conky-claude-usage.py" "$HOME/.claude/conky-claude-usage.py"
echo "  -> ~/.claude/conky-claude-usage.py"

# 2. Conky config
mkdir -p "$HOME/.conky/claude-usage"
install -m 644 "$SCRIPT_DIR/conkyrc" "$HOME/.conky/claude-usage/conkyrc"
echo "  -> ~/.conky/claude-usage/conkyrc"

echo ""
echo "Done. Launch with:"
echo "  conky -c ~/.conky/claude-usage/conkyrc --daemonize"
echo ""
echo "Add that line to ~/.conky/conky-startup.sh for autostart."
