#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Krita2CSP installer: a Clip Studio Paint style interface for Krita 6.
#
#   ./install.sh            install with the dark theme
#   ./install.sh --light    install with the light theme
#   ./install.sh --help     all options
#
# Close Krita before running this script.

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KCONF="python3 $HERE/tools/kconfig_edit.py"

THEME="Krita2CSP Dark"
DO_THEME=1
DO_SHORTCUTS=1
TARGET="auto"

usage() {
  cat <<'EOF'
Usage: ./install.sh [options]

  --dark           use the dark theme (default)
  --light          use the light theme
  --no-theme       keep your current Krita theme
  --no-shortcuts   keep your current keyboard shortcuts
  --flatpak        install into the Flatpak version of Krita
  --native         install into a distribution package or AppImage of Krita
  -h, --help       show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dark) THEME="Krita2CSP Dark" ;;
    --light) THEME="Krita2CSP Light" ;;
    --no-theme) DO_THEME=0 ;;
    --no-shortcuts) DO_SHORTCUTS=0 ;;
    --flatpak) TARGET="flatpak" ;;
    --native) TARGET="native" ;;
    -h|--help) usage; exit 0 ;;
    *) echo "Unknown option: $1"; usage; exit 2 ;;
  esac
  shift
done

say() { printf '%s\n' "$*"; }

command -v python3 >/dev/null 2>&1 || { say "python3 is needed to edit Krita's settings. Please install it first."; exit 1; }

if pgrep -x krita >/dev/null 2>&1; then
  say "Krita is running. Please close Krita first (it rewrites its settings when it exits)."
  exit 1
fi

# Where does Krita keep its settings and resources?
if [[ "$TARGET" == "auto" ]]; then
  if command -v flatpak >/dev/null 2>&1 && flatpak info org.kde.krita >/dev/null 2>&1 \
     && ! command -v krita >/dev/null 2>&1; then
    TARGET="flatpak"
  else
    TARGET="native"
  fi
fi

if [[ "$TARGET" == "flatpak" ]]; then
  CONF_DIR="$HOME/.var/app/org.kde.krita/config"
  DATA_DIR="$HOME/.var/app/org.kde.krita/data/krita"
else
  CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}"
  DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/krita"
fi
KRITARC="$CONF_DIR/kritarc"
SHORTCUTSRC="$CONF_DIR/kritashortcutsrc"

# A custom resource folder (Settings > Configure Krita > General) wins.
if [[ -f "$KRITARC" ]]; then
  CUSTOM="$($KCONF "$KRITARC" get "" ResourceDirectory 2>/dev/null || true)"
  if [[ -n "$CUSTOM" ]]; then DATA_DIR="$CUSTOM"; fi
fi

say "Krita2CSP installer"
say "  Krita type:       $TARGET"
say "  Settings:         $CONF_DIR"
say "  Resource folder:  $DATA_DIR"
say ""

# Back up the settings we touch.
STAMP="$(date +%Y%m%d-%H%M%S)"
for f in "$KRITARC" "$SHORTCUTSRC"; do
  if [[ -f "$f" ]]; then
    cp -p "$f" "$f.krita2csp-backup-$STAMP"
    say "Backup: $f.krita2csp-backup-$STAMP"
  fi
done

# Plugin and color schemes
mkdir -p "$DATA_DIR/pykrita" "$DATA_DIR/color-schemes"
rm -rf "$DATA_DIR/pykrita/krita2csp"
cp -r "$HERE/krita-resources/pykrita/krita2csp" "$DATA_DIR/pykrita/"
cp "$HERE/krita-resources/pykrita/krita2csp.desktop" "$DATA_DIR/pykrita/"
cp "$HERE"/krita-resources/color-schemes/*.colors "$DATA_DIR/color-schemes/"
find "$DATA_DIR/pykrita/krita2csp" -name '__pycache__' -prune -exec rm -rf {} +
say "Installed plugin and color schemes."

# Enable the plugin and re-apply the layout at the next start.
mkdir -p "$CONF_DIR"
$KCONF "$KRITARC" set python enable_krita2csp true
$KCONF "$KRITARC" unset krita2csp layoutApplied

if [[ $DO_THEME -eq 1 ]]; then
  $KCONF "$KRITARC" set theme Theme "$THEME"
  say "Theme: $THEME"
fi

if [[ $DO_SHORTCUTS -eq 1 ]]; then
  # Krita's built-in "Clip Studio Paint compatible" scheme (Krita 6.0.4 and newer) ...
  $KCONF "$KRITARC" set "Shortcut Schemes" "Current Scheme" clip_studio_paint_compatible
  # ... plus CSP tool keys handled by this plugin. The Krita actions that
  # used these keys are moved or cleared so nothing is assigned twice.
  $KCONF "$SHORTCUTSRC" set Shortcuts krita2csp_tool_pen P
  $KCONF "$SHORTCUTSRC" set Shortcuts krita2csp_tool_brush B
  $KCONF "$SHORTCUTSRC" set Shortcuts krita2csp_tool_eraser E
  $KCONF "$SHORTCUTSRC" set Shortcuts krita2csp_tool_blend J
  $KCONF "$SHORTCUTSRC" set Shortcuts KarbonCalligraphyTool none
  $KCONF "$SHORTCUTSRC" set Shortcuts KritaShape/KisToolBrush none
  $KCONF "$SHORTCUTSRC" set Shortcuts erase_action C
  $KCONF "$SHORTCUTSRC" set Shortcuts pathpoint-join none
  say "Shortcuts: Clip Studio Paint compatible scheme, P/B/E/J for CSP tools."
fi

say ""
say "Done. Start Krita: the CSP layout is applied a moment after the window opens."
say "If the layout ever gets messed up: Tools > Scripts > Apply CSP layout."
