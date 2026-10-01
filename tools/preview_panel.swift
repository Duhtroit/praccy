//  PanelPreview.swift
//  Praccy build tool
//
//  Renders the dependency panel with a simulated report, so the one screen that
//  only appears when something is missing can be checked on a machine where
//  everything is installed.
//
//  Compiled against the real app/DependencyPanel.swift, so this is the same
//  class the app uses rather than a copy that can drift. Swift only allows
//  top-level code in a file called main.swift, so this is staged under that
//  name in a temp directory; see tools/preview_panel.sh.

import AppKit

let panel = DependencyPanel()
let report: [String: Any] = [
    "languages": [
        ["language": "python", "ok": true,
         "version": "Python 3.12.14 (bundled with Praccy)", "install": nil],
        ["language": "cpp", "ok": true,
         "version": "Apple clang version 21.0.0 (clang-2100.3.34.2)", "install": nil],
        ["language": "rust", "ok": false, "version": nil,
         "install": "brew install rustup\n\nOr rustup.rs, which puts rustc in ~/.cargo/bin."],
        ["language": "java", "ok": true, "version": "javac 21.0.12.1", "install": nil],
        ["language": "csharp", "ok": false, "version": nil,
         "install": "brew install --cask dotnet\n\nOr the installer from dot.net, which puts .NET in /usr/local/share/dotnet."],
    ],
    "missing": ["rust", "csharp"],
    "allPresent": false,
]

panel.update(with: report)

// `--dump` prints the laid-out geometry instead of showing a window, so the
// panel can be checked where screen capture is unavailable. Auto Layout has to
// have run, hence the layoutSubtreeIfNeeded.
if CommandLine.arguments.contains("--dump") {
    panel.contentView?.layoutSubtreeIfNeeded()
    print("  panel \(Int(panel.frame.width))x\(Int(panel.frame.height))")
    func walk(_ view: NSView, depth: Int) {
        let frame = view.frame
        print(String(repeating: "  ", count: depth + 1)
              + "\(type(of: view)) \(Int(frame.width))x\(Int(frame.height))"
              + " at (\(Int(frame.minX)),\(Int(frame.minY)))")
        for sub in view.subviews { walk(sub, depth: depth + 1) }
    }
    if let content = panel.contentView { walk(content, depth: 0) }
    exit(0)
}

panel.makeKeyAndOrderFront(nil)
panel.orderFrontRegardless()
NSApp.activate(ignoringOtherApps: true)
NSApp.run()
