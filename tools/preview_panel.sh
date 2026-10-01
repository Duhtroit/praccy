#!/usr/bin/env bash
#  preview_panel.sh
#
#  Shows the first-run dependency panel on a machine where all four toolchains
#  are installed, which is the machine this was written on.
#
#  Compiles the real DependencyPanel from app/DependencyPanel.swift with a
#  simulated report rather than a copy, so what is on screen is what the user
#  sees. The panel lives in its own file precisely so this can link it without
#  dragging in the app's entry point.
#
#      ./tools/preview_panel.sh
set -euo pipefail

cd "$(dirname "$0")/.."

# Swift only permits top-level code in a file named main.swift, so the preview
# is staged under that name. Copied rather than symlinked because swiftc
# applies the top-level-code rule to the path it is handed.
staged=$(mktemp -d)
trap 'rm -rf "$staged"' EXIT
cp "$PWD/tools/preview_panel.swift" "$staged/main.swift"

swiftc -O -swift-version 5 \
  -framework AppKit \
  -o "$staged/panel" \
  "$staged/main.swift" "$PWD/app/DependencyPanel.swift"

echo "  showing the dependency panel with rust and dotnet simulated as missing"
exec "$staged/panel" "$@"
