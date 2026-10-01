//  DependencyPanel.swift
//  Praccy
//
//  Split out of main.swift so tools/preview_panel.sh can compile the real
//  panel without also compiling the app's entry point. Swift decides which
//  file may hold top-level code by its filename, not by any #if, so a preview
//  that includes main.swift would try to launch a second copy of the app.
//
//  The panel shows the install command and never runs it. See the comment on
//  the class for why.

import AppKit

/// The panel shown when a compiler is missing.
///
/// It shows the command and never runs it. Installing a toolchain is a
/// deliberate act with system-wide consequences, and an app that shells out to
/// Homebrew without being asked is a worse neighbour than one that explains
/// itself and gets out of the way. The button exists to be pressed by a human.
final class DependencyPanel: NSWindow {
    private let scroll = NSScrollView()
    private let text = NSTextView()
    private let recheck = NSButton()
    private let status = NSTextField(labelWithString: "")

    init() {
        super.init(
            contentRect: NSRect(x: 0, y: 0, width: 620, height: 460),
            styleMask: [.titled, .closable],
            backing: .buffered,
            defer: false
        )
        title = "Praccy needs a few tools"
        build()
        center()
    }

    required init?(coder: NSCoder) { fatalError("unused") }

    private func build() {
        guard let content = contentView else { return }

        let heading = NSTextField(labelWithString:
            "Praccy runs your code for real, so it needs a compiler for each language.")
        heading.font = .systemFont(ofSize: 15, weight: .semibold)

        let detail = NSTextField(wrappingLabelWithString:
            "Python is already handled — Praccy ships its own. The rest are one command each. "
            + "Praccy will not run them for you. Copy a line into Terminal, then press Re-check.")
        detail.font = .systemFont(ofSize: 12)
        detail.textColor = .secondaryLabelColor
        detail.maximumNumberOfLines = 0

        text.isEditable = false
        text.isSelectable = true
        text.font = .monospacedSystemFont(ofSize: 12, weight: .regular)
        text.isAutomaticQuoteSubstitutionEnabled = false
        text.backgroundColor = .textBackgroundColor
        text.textContainerInset = NSSize(width: 10, height: 10)
        text.string = ""
        scroll.documentView = text
        scroll.hasVerticalScroller = true
        scroll.borderType = .bezelBorder

        recheck.title = "Re-check"
        recheck.bezelStyle = .rounded
        recheck.target = self
        recheck.action = #selector(onRecheck)

        let copy = NSButton(title: "Copy All", target: self, action: #selector(onCopyAll))
        copy.bezelStyle = .rounded

        status.font = .systemFont(ofSize: 12)
        status.textColor = .secondaryLabelColor

        let buttons = NSStackView(views: [status, NSView(), copy, recheck])
        buttons.orientation = .horizontal

        let stack = NSStackView(views: [heading, detail, scroll, buttons])
        stack.orientation = .vertical
        stack.alignment = .leading
        stack.spacing = 12
        stack.translatesAutoresizingMaskIntoConstraints = false
        content.addSubview(stack)

        NSLayoutConstraint.activate([
            stack.leadingAnchor.constraint(equalTo: content.leadingAnchor, constant: 20),
            stack.trailingAnchor.constraint(equalTo: content.trailingAnchor, constant: -20),
            stack.topAnchor.constraint(equalTo: content.topAnchor, constant: 20),
            stack.bottomAnchor.constraint(equalTo: content.bottomAnchor, constant: -20),
            scroll.widthAnchor.constraint(equalTo: stack.widthAnchor),
            scroll.heightAnchor.constraint(greaterThanOrEqualToConstant: 260),
        ])
    }

    /// Renders the report from `/api/deps`.
    func update(with report: [String: Any]) {
        let languages = report["languages"] as? [[String: Any]] ?? []
        var body = ""
        var missing = 0

        for entry in languages {
            let name = entry["language"] as? String ?? "?"
            let ok = entry["ok"] as? Bool ?? false
            let version = entry["version"] as? String ?? ""
            if ok {
                body += "✓ \(name.padding(toLength: 7, withPad: " ", startingAt: 0)) \(version)\n\n"
            } else {
                missing += 1
                let install = entry["install"] as? String ?? ""
                body += "✗ \(name)\n\(install)\n\n"
            }
        }

        text.string = body
        status.stringValue = missing == 0
            ? "All toolchains found."
            : "\(missing) toolchain\(missing == 1 ? "" : "s") still missing."
    }

    @objc private func onCopyAll() {
        NSPasteboard.general.clearContents()
        NSPasteboard.general.setString(text.string, forType: .string)
    }

    @objc private func onRecheck() {
        NotificationCenter.default.post(name: .praccyRecheckDependencies, object: nil)
    }
}

extension Notification.Name {
    static let praccyRecheckDependencies = Notification.Name("praccy.recheckDependencies")
}
