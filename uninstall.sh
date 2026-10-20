#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Removes Krita2CSP and the settings it changed. Close Krita first.
#   ./uninstall.sh            (native or AppImage Krita)
#   ./uninstall.sh --flatpak  (Flatpak Krita)

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
KCONF="python3 $HERE/tools/kconfig_edit.py"

if [[ "${1:-}" == "--flatpak" ]]; then
  CONF_DIR="$HOME/.var/app/org.kde.krita/config"
  DATA_DIR="$HOME/.var/app/org.kde.krita/data/krita"
else
  CONF_DIR="${XDG_CONFIG_HOME:-$HOME/.config}"
  DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/krita"
fi
KRITARC="$CONF_DIR/kritarc"
SHORTCUTSRC="$CONF_DIR/kritashortcutsrc"

if pgrep -x krita >/dev/null 2>&1; then
  echo "Krita is running. Please close Krita first."
  exit 1
fi

if [[ -f "$KRITARC" ]]; then
  CUSTOM="$($KCONF "$KRITARC" get "" ResourceDirectory 2>/dev/null || true)"
  if [[ -n "$CUSTOM" ]]; then DATA_DIR="$CUSTOM"; fi
fi

rm -rf "$DATA_DIR/pykrita/krita2csp" "$DATA_DIR/pykrita/krita2csp.desktop"
rm -f "$DATA_DIR/color-schemes/Krita2CSP-Dark.colors" "$DATA_DIR/color-schemes/Krita2CSP-Light.colors"

if [[ -f "$KRITARC" ]]; then
  $KCONF "$KRITARC" unset python enable_krita2csp
  THEME="$($KCONF "$KRITARC" get theme Theme 2>/dev/null || true)"
  if [[ "$THEME" == Krita2CSP* ]]; then
    $KCONF "$KRITARC" set theme Theme "Krita dark"
  fi
fi
if [[ -f "$SHORTCUTSRC" ]]; then
  for key in krita2csp_tool_pen krita2csp_tool_brush krita2csp_tool_eraser krita2csp_tool_blend \
             KarbonCalligraphyTool KritaShape/KisToolBrush erase_action pathpoint-join; do
    $KCONF "$SHORTCUTSRC" unset Shortcuts "$key"
  done
fi

echo "Krita2CSP removed."
echo "The 'Clip Studio Paint compatible' shortcut scheme stays selected; change it in"
echo "Settings > Configure Krita > Keyboard Shortcuts if you like."
echo "To get Krita's standard docker layout back: Window > Workspace > Default."
