#!/usr/bin/env bash
set -euo pipefail

# SDLC Plugin Installer for Claude Code
# Registers and enables the sdlc@funcoding-skills plugin

PLUGIN_NAME="sdlc"
MARKETPLACE_NAME="funcoding-skills"
PLUGIN_ID="${PLUGIN_NAME}@${MARKETPLACE_NAME}"
PLUGIN_DIR="$(cd "$(dirname "$0")" && pwd)"
CLAUDE_DIR="$HOME/.claude"
PLUGINS_DIR="$CLAUDE_DIR/plugins"
CACHE_DIR="$PLUGINS_DIR/cache/$MARKETPLACE_NAME"
CACHE_PATH="$CACHE_DIR/$PLUGIN_NAME"
SETTINGS_FILE="$CLAUDE_DIR/settings.json"
INSTALLED_FILE="$PLUGINS_DIR/installed_plugins.json"
MARKETPLACES_FILE="$PLUGINS_DIR/known_marketplaces.json"

echo "Installing $PLUGIN_ID from $PLUGIN_DIR"
echo ""

# Check dependencies
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required. Install with: brew install jq"
  exit 1
fi

# Ensure directories exist
mkdir -p "$PLUGINS_DIR" "$CACHE_DIR"

# --- 0. Symlink plugin into Claude Code's cache dir (required for discovery) ---
# Claude Code only loads plugins from ~/.claude/plugins/cache/<marketplace>/<plugin>/
ln -snf "$PLUGIN_DIR" "$CACHE_PATH"
echo "[ok] Linked $CACHE_PATH -> $PLUGIN_DIR"

# --- 1. Register in installed_plugins.json ---
NOW="$(date -u +%Y-%m-%dT%H:%M:%S.000Z)"
VERSION=$(jq -r '.version // "1.0.0"' "$PLUGIN_DIR/.claude-plugin/plugin.json")

if [ ! -f "$INSTALLED_FILE" ] || [ ! -s "$INSTALLED_FILE" ]; then
  echo '{"version":2,"plugins":{}}' > "$INSTALLED_FILE"
fi

# Add or update the plugin entry (installPath must be the cache symlink, not source)
jq --arg id "$PLUGIN_ID" \
   --arg path "$CACHE_PATH" \
   --arg ver "$VERSION" \
   --arg now "$NOW" \
   '.plugins[$id] = [{
     "scope": "user",
     "installPath": $path,
     "version": $ver,
     "installedAt": $now,
     "lastUpdated": $now
   }]' "$INSTALLED_FILE" > "${INSTALLED_FILE}.tmp" && mv "${INSTALLED_FILE}.tmp" "$INSTALLED_FILE"

echo "[ok] Registered in installed_plugins.json"

# --- 2. Register local marketplace in known_marketplaces.json ---
if [ ! -f "$MARKETPLACES_FILE" ] || [ ! -s "$MARKETPLACES_FILE" ]; then
  echo '{}' > "$MARKETPLACES_FILE"
fi

jq --arg name "$MARKETPLACE_NAME" \
   --arg path "$PLUGIN_DIR" \
   --arg now "$NOW" \
   '.[$name] = {
     "source": {"source": "local", "path": $path},
     "installLocation": $path,
     "lastUpdated": $now
   }' "$MARKETPLACES_FILE" > "${MARKETPLACES_FILE}.tmp" && mv "${MARKETPLACES_FILE}.tmp" "$MARKETPLACES_FILE"

echo "[ok] Registered marketplace in known_marketplaces.json"

# --- 3. Enable in settings.json ---
if [ ! -f "$SETTINGS_FILE" ]; then
  echo '{}' > "$SETTINGS_FILE"
fi

jq --arg id "$PLUGIN_ID" \
   '.enabledPlugins[$id] = true' "$SETTINGS_FILE" > "${SETTINGS_FILE}.tmp" && mv "${SETTINGS_FILE}.tmp" "$SETTINGS_FILE"

echo "[ok] Enabled in settings.json"

echo ""
echo "Done! $PLUGIN_ID is now installed and enabled."
echo "Restart Claude Code for changes to take effect."
