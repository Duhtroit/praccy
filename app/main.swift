//  main.swift
//  Praccy
//
//  A window around the existing web UI. Deliberately thin: the app's job is to
//  start the bundled Python server, point a webview at it, and get out of the
//  way. Everything the user sees -- the practice view, the course, the
//  progression -- is the same HTML the command-line and browser builds serve,
//  so there is one implementation of the product rather than two.
//
//  Three things here are not boilerplate:
//
//    1. The server is a child process and has to be reaped. Quit cleanly means
//       SIGTERM then SIGKILL, because a leaked server holds its port and the
//       next launch looks like a bug.
//    2. The port is ephemeral. The server prints `PORT=<n>` on stdout before it
//       serves, and this reads that line rather than assuming 8777, so two
//       copies of Praccy can coexist.
//    3. The environment is not the user's. A Finder-launched app inherits
//       `PATH=/usr/bin:/bin:/usr/sbin:/sbin`. The server's toolchain module
//       probes install paths for that reason, but the app still prepends the
//       common ones so anything the app itself shells out to behaves.

import AppKit
import WebKit

// MARK: - Bundled layout

/// Root of Praccy.app/Contents/Resources, where the build script puts both the
/// trimmed interpreter and the `cbp` package.
///
/// Named `Resources` rather than `Bundle` on purpose: a type called `Bundle`
/// shadows `Swift.Bundle` for the rest of the file, and every `Bundle.main`
/// below it silently becomes this enum.
enum Resources {
    static var root: URL {
        Foundation.Bundle.main.resourceURL ?? URL(fileURLWithPath: ".")
    }

    /// The interpreter the build script copied in. Spelled out rather than
    /// discovered so a malformed bundle fails loudly at launch instead of
    /// quietly falling back to whatever Python is on the machine.
    static var python: URL {
        root.appendingPathComponent("python/bin/python3.12")
    }

    /// The `cbp` package, imported via PYTHONPATH rather than copied into
    /// site-packages, so upgrading the app is replacing one directory.
    static var package: URL {
        root.appendingPathComponent("cbp")
    }
}

// MARK: - The server child process

final class ServerProcess {
    private var process: Process?
    private var port: Int?
    /// stderr is drained on a background queue. Left alone, a chatty traceback
    /// fills the pipe buffer and the server blocks on its next write.
    private var errorSink: Pipe?

    func start() throws -> Int {
        guard FileManager.default.isExecutableFile(atPath: Resources.python.path) else {
            throw AppError("Praccy is incomplete: no interpreter at "
                           + Resources.python.path)
        }
        guard FileManager.default.fileExists(
            atPath: Resources.package.appendingPathComponent("server.py").path) else {
            throw AppError("Praccy is incomplete: no cbp package at "
                           + Resources.package.path)
        }

        let process = Process()
        process.executableURL = Resources.python
        process.arguments = ["-m", "cbp.server", "--port", "0", "--quiet"]
        // The Resources directory, not the package. `import cbp` has to
        // resolve from the directory *containing* cbp/, so pointing this at
        // cbp/ itself makes Python look for cbp/cbp and fail.
        process.currentDirectoryURL = Resources.root

        var environment = ProcessInfo.processInfo.environment
        // Bare from Finder, so give the child what a shell would have had.
        environment["PATH"] = Self.searchPath
        environment["PYTHONPATH"] = Resources.root.path
        // A signed bundle must not grow files, and writing .pyc into it would
        // invalidate the signature. It is also slower to start.
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        // No user site-packages: the bundled interpreter is the whole point.
        environment["PYTHONNOUSERSITE"] = "1"
        process.environment = environment

        // stderr goes to a log file, not to the app's own stderr. A
        // Finder-launched app has no terminal attached, so a traceback written
        // there goes nowhere and the failure looks like a hang. The log is
        // opened in the Log menu so the user can reach it.
        let errors = Pipe()
        process.standardError = errors
        errorSink = errors
        if let sink = Self.logFile() {
            DispatchQueue.global(qos: .utility).async { [errors] in
                errors.fileHandleForReading.readabilityHandler = { handle in
                    let data = handle.availableData
                    if data.isEmpty { return }
                    if let text = String(data: data, encoding: .utf8) {
                        sink.write(Data(text.utf8))
                    }
                }
            }
        } else {
            DispatchQueue.global(qos: .utility).async { [errors] in
                errors.fileHandleForReading.readabilityHandler = { handle in
                    let data = handle.availableData
                    if data.isEmpty { return }
                    FileHandle.standardError.write(data)
                }
            }
        }

        // stdout is the handshake channel, so it is read synchronously and
        // only until the port arrives. `readDataToEndOfFile` would block until
        // the server exits, which is never, so it cannot be used here.
        let out = Pipe()
        process.standardOutput = out

        try process.run()
        self.process = process

        let deadline = Date().addingTimeInterval(20)
        var buffer = Data()
        while Date() < deadline {
            let chunk = out.fileHandleForReading.availableData
            if chunk.isEmpty {
                if !process.isRunning {
                    throw AppError("The server exited before it reported a port.")
                }
                Thread.sleep(forTimeInterval: 0.02)
                continue
            }
            buffer.append(chunk)
            let text = String(decoding: buffer, as: UTF8.self)
            for line in text.split(separator: "\n") where line.hasPrefix("PORT=") {
                if let value = Int(line.dropFirst("PORT=".count).trimmingCharacters(in: .whitespaces)) {
                    port = value
                    break
                }
            }
            if port != nil { break }
        }

        guard let port else {
            process.terminate()
            throw AppError("The server did not report a port within 20 seconds.")
        }

        // Hand the reader to a handler so a later write cannot block the child.
        out.fileHandleForReading.readabilityHandler = { handle in
            let data = handle.availableData
            if data.isEmpty {
                handle.readabilityHandler = nil
                return
            }
            FileHandle.standardOutput.write(data)
        }

        return port
    }

    /// The bound port, once `start` has succeeded.
    var boundPort: Int? { port }

    /// Application Support is used rather than Caches: this is a diagnostic
    /// record, and macOS is entitled to empty Caches behind your back.
    static func logFile() -> FileHandle? {
        let base = FileManager.default.urls(for: .applicationSupportDirectory,
                                            in: .userDomainMask).first
        guard let base else { return nil }
        let folder = base.appendingPathComponent("Praccy", isDirectory: true)
        try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        let path = folder.appendingPathComponent("praccy.log")
        if !FileManager.default.fileExists(atPath: path.path) {
            FileManager.default.createFile(atPath: path.path, contents: nil)
        }
        return try? FileHandle(forWritingTo: path)
    }

    /// A PATH a shell would recognise, for anything the app itself runs.
    static let searchPath: String = [
        "/opt/homebrew/bin",
        "/usr/local/bin",
        NSString(string: "~/.cargo/bin").expandingTildeInPath,
        "/usr/bin", "/bin", "/usr/sbin", "/sbin",
    ].joined(separator: ":")

    func stop() {
        guard let process, process.isRunning else { return }
        process.terminate()
        // SIGTERM is enough in normal use. The deadline is for a server wedged
        // in a compile, where a clean shutdown is not coming.
        let deadline = Date().addingTimeInterval(3)
        while process.isRunning && Date() < deadline {
            Thread.sleep(forTimeInterval: 0.05)
        }
        if process.isRunning {
            kill(process.processIdentifier, SIGKILL)
        }
        errorSink?.fileHandleForReading.readabilityHandler = nil
        errorSink = nil
        self.process = nil
    }

    deinit { stop() }
}

struct AppError: LocalizedError {
    let message: String
    init(_ message: String) { self.message = message }
    var errorDescription: String? { message }
}

// MARK: - Launch log

/// A record of what the app did at startup, on disk.
///
/// A Finder-launched app has no terminal, so anything printed to stdout or
/// stderr is discarded by the window server. When a GUI app misbehaves there
/// is otherwise no evidence at all, which is exactly the situation this
/// exists for: it is how the missing-window bug below was diagnosed.
enum AppLog {
    static let url: URL? = {
        let base = FileManager.default.urls(for: .applicationSupportDirectory,
                                            in: .userDomainMask).first
        guard let base else { return nil }
        let folder = base.appendingPathComponent("Praccy", isDirectory: true)
        try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true)
        return folder.appendingPathComponent("launch.log")
    }()

    private static let handle: FileHandle? = {
        guard let url else { return nil }
        // Truncated each launch: a startup log is only interesting for the run
        // that just happened, and an append-only file grows forever.
        try? Data().write(to: url)
        return try? FileHandle(forWritingTo: url)
    }()

    static func write(_ message: String) {
        guard let handle else { return }
        handle.write(Data((message + "\n").utf8))
    }
}

// MARK: - First-run dependency panel

// MARK: - The window

final class MainWindow: NSWindowController, WKNavigationDelegate {
    private let webView = WKWebView()
    private let server = ServerProcess()
    private let panel = DependencyPanel()
    private let spinner = NSProgressIndicator()

    private static let checkedDependenciesKey = "praccy.dependenciesChecked"

    init() {
        let window = NSWindow(
            contentRect: NSRect(x: 0, y: 0, width: 1320, height: 860),
            styleMask: [.titled, .closable, .miniaturizable, .resizable],
            backing: .buffered,
            defer: false
        )
        window.title = "Praccy"
        // Small enough that present() can always find a frame that fits. A
        // larger minimum would override the computed size on a small display
        // and put the window back off the edge it was just fitted to.
        window.minSize = NSSize(width: 420, height: 320)
        // Autsave is deliberately NOT used for the main window. It restores a
        // saved frame over the one set above, and a frame saved on a display
        // that is no longer attached lands the window off-screen, where the
        // app looks like it never started. The frame below is constrained to
        // the visible area of whichever screen is actually there.
        window.setFrameAutosaveName("")
        super.init(window: window)

        window.contentView = NSView()
        webView.translatesAutoresizingMaskIntoConstraints = false
        webView.setValue(false, forKey: "drawsBackground")
        // Required on every view that takes constraints. Leaving the
        // autoresizing mask on the spinner while also constraining its centre
        // gives Auto Layout two conflicting sources of truth, and the system it
        // builds is unsatisfiable -- which collapses the *content view* to
        // 0x0, not just the spinner. The window then opens, the server runs,
        // the webview is there and correctly wired, and nothing is visible,
        // because it has no size. This one line was the entire bug.
        spinner.translatesAutoresizingMaskIntoConstraints = false
        window.contentView?.addSubview(webView)
        window.contentView?.addSubview(spinner)

        NSLayoutConstraint.activate([
            webView.leadingAnchor.constraint(equalTo: window.contentView!.leadingAnchor),
            webView.trailingAnchor.constraint(equalTo: window.contentView!.trailingAnchor),
            webView.topAnchor.constraint(equalTo: window.contentView!.topAnchor),
            webView.bottomAnchor.constraint(equalTo: window.contentView!.bottomAnchor),
            spinner.centerXAnchor.constraint(equalTo: window.contentView!.centerXAnchor),
            spinner.centerYAnchor.constraint(equalTo: window.contentView!.centerYAnchor),
            // Explicit size as well, so the spinner never depends on an
            // intrinsic size that is only settled once it is animating.
            spinner.widthAnchor.constraint(equalToConstant: 32),
            spinner.heightAnchor.constraint(equalToConstant: 32),
        ])

        NotificationCenter.default.addObserver(
            self, selector: #selector(onRecheckDependencies),
            name: .praccyRecheckDependencies, object: nil
        )

        AppLog.write("MainWindow.init: window=\(window.frame) content=\(Int(window.contentView?.frame.width ?? 0))x\(Int(window.contentView?.frame.height ?? 0))")
    }

    /// Puts the window on a screen, sized to fit, and in front.
    ///
    /// `showWindow` alone is not enough. It makes the window visible to the
    /// window server, but it does not guarantee the frame lands on a screen
    /// that is actually attached, so a window restored from a frame saved on a
    /// display that has since been unplugged stays invisible -- the process
    /// runs, the server answers, and the app looks dead. Re-deriving the frame
    /// from the screens that are really there removes that whole class of
    /// failure, which is why this does not trust a stored frame at all.
    func present() {
        guard let window else { return }
        let screens = NSScreen.screens
        AppLog.write("present: \(screens.count) screen(s): \(screens.map { "\($0.frame)" }.joined(separator: ", "))")

        // The main display -- the one carrying the menu bar -- not the one the
        // mouse happens to be on. Activating the app moves the window to the
        // main display regardless, so choosing the mouse's screen just means
        // setting a frame and then watching AppKit override it; on a two-screen
        // Mac that lands the window somewhere the request did not ask for.
        // Agreeing with the system is both simpler and what the user expects.
        let target = NSScreen.main ?? screens.first
        guard let target else {
            AppLog.write("present: no screens, cannot place the window")
            return
        }

        let visible = target.visibleFrame
        // Fit the display rather than the other way round. A floor of 940x600
        // would push the window off a small screen, so the usable area is
        // capped by what the screen actually has and the window is then never
        // asked to be larger than the space available.
        let available = NSSize(
            width: max(visible.width - 80, 420),
            height: max(visible.height - 80, 320)
        )
        let size = NSSize(
            width: min(1320, available.width),
            height: min(860, available.height)
        )
        let frame = NSRect(
            x: visible.midX - size.width / 2,
            y: visible.midY - size.height / 2,
            width: size.width,
            height: size.height
        ).integral

        window.setFrame(frame, display: true)
        window.makeKeyAndOrderFront(nil)
        window.orderFrontRegardless()
        NSApp.activate(ignoringOtherApps: true)
        // Force a layout pass now. The webview is pinned to the content view
        // with constraints, and a constrained view keeps a zero frame until
        // Auto Layout has run at least once. Without this the webview is still
        // 0x0 when the page is asked to load, and a zero-sized webview renders
        // nothing at all: a correct window, a working server, and no content.
        window.contentView?.layoutSubtreeIfNeeded()

        AppLog.write("present: set frame \(window.frame) visible=\(window.isVisible) onScreen=\(window.isOnActiveSpace) key=\(window.isKeyWindow) chose=\(target.frame) mainNow=\(NSScreen.main.map { "\($0.frame)" } ?? "nil")")
        AppLog.write("present: content=\(window.contentView?.frame ?? .zero) webview=\(webView.frame)")

        // Logged again once things have settled. On a multi-display Mac the
        // arrangement can finish reconfiguring after launch, and the system
        // will relocate the window onto whichever display has become the main
        // one. That is correct behaviour, and the property that actually
        // matters is not "the frame I asked for" but "the window is on a real
        // screen, on the main one, and is showing something".
        DispatchQueue.main.asyncAfter(deadline: .now() + 2.0) { [weak self] in
            guard let self, let window = self.window else { return }
            let main = NSScreen.main
            let onMain = main.map { $0.visibleFrame.intersects(window.frame) } ?? false
            AppLog.write("settled: frame=\(window.frame) visible=\(window.isVisible) webview=\(self.webView.frame)")
            AppLog.write("settled: onMainScreen=\(onMain) main=\(main.map { "\($0.frame)" } ?? "none") screens=\(NSScreen.screens.count) attached=\(window.screen != nil) activeSpace=\(window.isOnActiveSpace)")
        }
    }

    required init?(coder: NSCoder) { fatalError("unused") }

    /// Stops the spinner and takes it out of the view hierarchy.
    ///
    /// `stopAnimation` alone is not enough: an indeterminate
    /// NSProgressIndicator keeps its last drawn frame, so a spinner that was
    /// showing "working..." stays on screen forever over a window that has
    /// long since finished loading. Removing it is the only way to be sure.
    private func hideSpinner() {
        spinner.stopAnimation(nil)
        spinner.isHidden = true
        spinner.removeFromSuperview()
        AppLog.write("spinner: stopped, hidden and removed")
    }

    // MARK: WKNavigationDelegate

    // Without these the app cannot tell the difference between "the page
    // loaded and is on screen" and "the load was refused and the window is
    // blank", which are the same thing from the outside and were the reason
    // this file was silent while the app showed nothing.

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        // Whether the loading spinner is really gone, checked from inside the
        // app. A spinner that outlives the page it was covering is the kind of
        // thing that is obvious on screen and invisible to every other check.
        let gone = spinner.superview == nil && spinner.isHidden
        AppLog.write("didFinish: title=\(webView.title ?? "(none)") webview=\(webView.frame) spinnerGone=\(gone) url=\(webView.url?.absoluteString ?? "(none)")")
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        AppLog.write("didFail: \(error.localizedDescription)")
    }

    func webView(_ webView: WKWebView, didFailProvisionalNavigation navigation: WKNavigation!, withError error: Error) {
        // A provisional failure is the one ATS produces, so it is logged
        // verbatim: the message names the transport policy that blocked it.
        AppLog.write("didFailProvisional: \(error.localizedDescription) (\((error as NSError).code))")
    }

    func start() {
        spinner.startAnimation(nil)
        DispatchQueue.global(qos: .userInitiated).async { [weak self] in
            guard let self else { return }
            do {
                let port = try server.start()
                AppLog.write("start: server on port \(port)")
                DispatchQueue.main.async {
                    // The spinner only covers the wait for the *server*. Once
                    // the port is known the page is loading and the web UI has
                    // its own states, so the native spinner is stopped and
                    // hidden here rather than left to a stopAnimation that only
                    // halts the animation but leaves the control on screen.
                    self.hideSpinner()
                    let url = URL(string: "http://127.0.0.1:\(port)/")!
                    AppLog.write("start: loading \(url) webview frame=\(self.webView.frame)")
                    self.webView.navigationDelegate = self
                    self.webView.load(URLRequest(url: url))
                }
                // The first-run check waits for the port too, since the API is
                // what answers it.
                self.checkDependencies(firstRun: !UserDefaults.standard
                    .bool(forKey: Self.checkedDependenciesKey))
            } catch {
                AppLog.write("start: FAILED \(error)")
                DispatchQueue.main.async {
                    self.hideSpinner()
                    self.showFailure(error)
                }
            }
        }
    }

    /// Stops the server. Called on the way out, after NSApplication.run()
    /// returns, because a leaked server holds its port.
    func shutdown() {
        server.stop()
    }

    private func checkDependencies(firstRun: Bool) {
        guard let port = server.boundPort else { return }
        var request = URLRequest(url: URL(string: "http://127.0.0.1:\(port)/api/deps")!)
        request.timeoutInterval = 60
        URLSession.shared.dataTask(with: request) { [weak self] data, _, _ in
            guard let self, let data,
                  let report = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
            else { return }
            let missing = (report["missing"] as? [String] ?? []).count
            DispatchQueue.main.async {
                // A missing toolchain is worth interrupting for on the first
                // run, and never afterwards: the user has already been told,
                // and an alert on every launch would be a nuisance they learn
                // to dismiss without reading.
                if missing > 0 && firstRun {
                    self.panel.update(with: report)
                    self.panel.makeKeyAndOrderFront(nil)
                }
                if missing == 0 {
                    UserDefaults.standard.set(true, forKey: Self.checkedDependenciesKey)
                }
            }
        }.resume()
    }

    @objc private func onRecheckDependencies() {
        checkDependencies(firstRun: true)
    }

    private func showFailure(_ error: Error) {
        let alert = NSAlert()
        alert.alertStyle = .critical
        alert.messageText = "Praccy could not start"
        alert.informativeText = (error as? LocalizedError)?.errorDescription
            ?? error.localizedDescription
        alert.addButton(withTitle: "Quit")
        if let button = alert.buttons.first { button.keyEquivalent = "\r" }
        alert.runModal()
        NSApp.terminate(nil)
    }

    // MARK: Menu actions

    @objc func reload() {
        webView.reload()
    }

    @objc func openDataFolder() {
        let folder = Resources.package.appendingPathComponent("data")
        NSWorkspace.shared.open(folder)
    }

    /// Opens the folder holding the user's progress, so it can be read or
    /// backed up outside the app.
    @objc func openStorageFolder() {
        let support = FileManager.default.urls(for: .applicationSupportDirectory,
                                               in: .userDomainMask).first
            ?? URL(fileURLWithPath: NSHomeDirectory())
        try? FileManager.default.createDirectory(at: support, withIntermediateDirectories: true)
        NSWorkspace.shared.open(support)
    }

    /// Reveals the server log, which is where a compiler or engine failure
    /// ends up. Without this a crash in the child process is unreportable.
    @objc func openLog() {
        _ = ServerProcess.logFile()
        let base = FileManager.default.urls(for: .applicationSupportDirectory,
                                            in: .userDomainMask).first
        guard let folder = base?.appendingPathComponent("Praccy") else { return }
        NSWorkspace.shared.activateFileViewerSelecting([folder])
    }

    @objc func showAbout() {
        let info = Foundation.Bundle.main.infoDictionary
        let version = (info?["CFBundleShortVersionString"] as? String) ?? "1.0"
        let alert = NSAlert()
        alert.messageText = "Praccy \(version)"
        alert.informativeText = """
            A local interview practice app. Everything runs on this machine: \
            the server, the compilers, and your progress.

            The course, the practice view and the progression are the same \
            build every other front end serves.
            """
        alert.addButton(withTitle: "OK")
        alert.runModal()
    }

    @objc func checkDependenciesFromMenu() {
        checkDependencies(firstRun: true)
    }
}

// MARK: - Menu

func buildMenu(target: MainWindow) -> NSMenu {
    let main = NSMenu()

    let appItem = NSMenuItem()
    let appMenu = NSMenu()
    appMenu.addItem(withTitle: "About Praccy",
                    action: #selector(MainWindow.showAbout), keyEquivalent: "")
        .target = target
    appMenu.addItem(.separator())
    appMenu.addItem(withTitle: "Check Toolchains…",
                    action: #selector(MainWindow.checkDependenciesFromMenu),
                    keyEquivalent: "").target = target
    appMenu.addItem(.separator())
    appMenu.addItem(withTitle: "Hide Praccy", action: #selector(NSApplication.hide(_:)),
                    keyEquivalent: "h")
    appMenu.addItem(.separator())
    appMenu.addItem(withTitle: "Quit Praccy", action: #selector(NSApplication.terminate(_:)),
                    keyEquivalent: "q")
    appItem.submenu = appMenu
    main.addItem(appItem)

    let fileItem = NSMenuItem()
    let fileMenu = NSMenu(title: "File")
    fileMenu.addItem(withTitle: "Reload", action: #selector(MainWindow.reload),
                     keyEquivalent: "r").target = target
    fileMenu.addItem(.separator())
    fileMenu.addItem(withTitle: "Open Data Folder",
                     action: #selector(MainWindow.openDataFolder),
                     keyEquivalent: "").target = target
    fileMenu.addItem(withTitle: "Open Progress Folder",
                     action: #selector(MainWindow.openStorageFolder),
                     keyEquivalent: "").target = target
    fileMenu.addItem(withTitle: "Show Log",
                     action: #selector(MainWindow.openLog),
                     keyEquivalent: "").target = target
    fileItem.submenu = fileMenu
    main.addItem(fileItem)

    let windowItem = NSMenuItem()
    let windowMenu = NSMenu(title: "Window")
    windowMenu.addItem(withTitle: "Minimize", action: #selector(NSWindow.performMiniaturize(_:)),
                       keyEquivalent: "m")
    windowMenu.addItem(withTitle: "Zoom", action: #selector(NSWindow.performZoom(_:)),
                       keyEquivalent: "")
    windowItem.submenu = windowMenu
    main.addItem(windowItem)
    NSApp.windowsMenu = windowMenu

    return main
}

// MARK: - App delegate

/// Owns the window and, more importantly, the shutdown.
///
/// The server is a child process, and it has to die with the app. That is not
/// something to do after `NSApplication.run()` returns, because a Quit does
/// not return: `NSApplication.terminate(_:)` calls `exit()` once the delegate
/// agrees, so any code after `run()` is unreachable in exactly the case it was
/// written for. `applicationShouldTerminate` is the only place that reliably
/// runs on the way out.
final class AppDelegate: NSObject, NSApplicationDelegate {
    private let controller = MainWindow()
    /// Signal sources must outlive this method, or the default disposition
    /// takes over again and SIGTERM kills the process outright.
    private var signalSources: [DispatchSourceSignal] = []

    /// Reap the server on SIGTERM and SIGINT as well as on a graceful Quit.
    ///
    /// `applicationShouldTerminate` covers Cmd-Q and the Dock's Quit, but a
    /// `kill`, a `logout`, or a crash-reporting tool sends SIGTERM, and the
    /// default disposition would end the process with the server still
    /// running and still holding its port. Turning the signal into an ordinary
    /// terminate routes it through the same cleanup as every other exit.
    private func installSignalHandlers() {
        for number in [SIGTERM, SIGINT] {
            // Ignore it first: the disposition has to be SIG_IGN before the
            // source is created, or the signal kills the process before the
            // handler is ever installed.
            signal(number, SIG_IGN)
            let source = DispatchSource.makeSignalSource(signal: number, queue: .main)
            source.setEventHandler { NSApp.terminate(nil) }
            source.resume()
            signalSources.append(source)
        }
    }

    func applicationDidFinishLaunching(_ notification: Notification) {
        AppLog.write("didFinishLaunching: entering")
        installSignalHandlers()
        NSApp.mainMenu = buildMenu(target: controller)
        // present(), not showWindow(): showWindow makes the window visible to
        // the window server but does not place it on a screen that is
        // currently attached, and an unplaced window is invisible.
        controller.showWindow(nil)
        controller.present()
        controller.start()
        AppLog.write("didFinishLaunching: done")
    }

    /// Clicking the Dock icon with no windows open brings the existing one back
    /// rather than starting a second server on a second port.
    func applicationShouldHandleReopen(_ sender: NSApplication, hasVisibleWindows: Bool) -> Bool {
        if !hasVisibleWindows {
            controller.showWindow(nil)
            controller.present()
        }
        return true
    }

    /// Quitting the app should not quit it just because the window closed.
    func applicationShouldTerminateAfterLastWindowClosed(_ sender: NSApplication) -> Bool {
        false
    }

    func applicationShouldTerminate(_ sender: NSApplication) -> NSApplication.TerminateReply {
        AppLog.write("terminating: reaping the server")
        controller.shutdown()
        return .terminateNow
    }
}

// MARK: - Entry point

let application = NSApplication.shared
// Regular, not accessory: the app gets a Dock icon and a menu bar, which is
// the entire point of shipping it as an app rather than a terminal command.
application.setActivationPolicy(.regular)
AppLog.write("entry: policy .regular set, building the delegate")

// A top-level `let` in main.swift is a global, so this outlives the run loop
// for the whole process. That matters: NSApplication.delegate is weak, and a
// delegate deallocated early stops receiving the callbacks that reap the server.
let delegate = AppDelegate()
application.delegate = delegate
application.run()

