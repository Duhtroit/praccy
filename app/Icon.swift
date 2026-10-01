//  Icon.swift
//  Praccy build tool
//
//  Renders the app icon to the PNG set `iconutil` expects, then exits.
//
//  Drawn rather than shipped because the mark is already defined in the web UI
//  -- a plate with a progress ring, where the ring is the app's status -- and a
//  generator is reviewable in a diff while a binary .icns is not. The ring
//  shows a little progress rather than being a full circle, which is the one
//  detail that makes it an app icon instead of a generic ring. The plate sits on
//  Apple's icon grid (an 824pt rounded square with a 22.5% corner radius inside
//  a 1024pt canvas) so it lines up with the system icons beside it in the Dock.
//
//  Run by tools/build_app.py at build time, not shipped:
//
//      swiftc -O -o /tmp/makeicon app/Icon.swift && /tmp/makeicon <outdir>

import AppKit
import CoreGraphics
import Foundation

let sizes = [16, 32, 64, 128, 256, 512, 1024]

func render(size: Int) -> Data? {
    guard let context = CGContext(
        data: nil,
        width: size, height: size,
        bitsPerComponent: 8, bytesPerRow: 0,
        space: CGColorSpace(name: CGColorSpace.sRGB)!,
        bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
    ) else { return nil }

    let s = CGFloat(size)
    // Drawn in a 36-unit space to match the SVG in the web UI, so the two
    // marks stay recognisably the same object.
    func u(_ v: CGFloat) -> CGFloat { v / 36 * s }

    // The plate follows Apple's macOS icon grid instead of filling the canvas.
    // The rounded square is 824 of 1024 points with a corner radius of 22.5% of
    // its own size; drawing it edge to edge made the icon visibly larger than
    // every system icon beside it in the Dock.
    let plateSide = u(36 * 824 / 1024)
    let path = CGPath(
        roundedRect: CGRect(
            x: (s - plateSide) / 2, y: (s - plateSide) / 2,
            width: plateSide, height: plateSide
        ),
        cornerWidth: plateSide * 0.225, cornerHeight: plateSide * 0.225,
        transform: nil
    )
    context.saveGState()
    context.addPath(path)
    context.clip()
    let space = CGColorSpace(name: CGColorSpace.sRGB)!
    // Petrol, matching the app's own surfaces: the plate is `--surface-2` at
    // the top and a shade under `--canvas` at the bottom. A neutral black plate
    // under a bright ring reads as a spinner, which is the one thing an icon
    // must not look like.
    let gradient = CGGradient(
        colorsSpace: space,
        colors: [
            CGColor(red: 0.102, green: 0.157, blue: 0.173, alpha: 1),
            CGColor(red: 0.047, green: 0.078, blue: 0.086, alpha: 1),
        ] as CFArray,
        locations: [0, 1]
    )!
    context.drawLinearGradient(
        gradient,
        start: CGPoint(x: 0, y: s), end: CGPoint(x: 0, y: 0),
        options: []
    )
    // A soft pool of the accent behind the top of the plate, so the material has
    // a light source rather than being a flat gradient.
    let glow = CGGradient(
        colorsSpace: space,
        colors: [
            CGColor(red: 0.851, green: 0.643, blue: 0.255, alpha: 0.22),
            CGColor(red: 0.851, green: 0.643, blue: 0.255, alpha: 0.0),
        ] as CFArray,
        locations: [0, 1]
    )!
    context.drawRadialGradient(
        glow,
        startCenter: CGPoint(x: s * 0.5, y: s * 0.92), startRadius: 0,
        endCenter: CGPoint(x: s * 0.5, y: s * 0.92), endRadius: s * 0.66,
        options: []
    )
    context.restoreGState()

    // Brass, the app's accent. The ring is the mark and the status at once, so
    // the icon and the header are the same object at two sizes.
    let accent = CGColor(red: 0.851, green: 0.643, blue: 0.255, alpha: 1)
    let radius = u(9.4)
    let centre = CGPoint(x: s / 2, y: s / 2)
    let width = u(2.3)
    let start = CGFloat.pi / 2

    // The unfilled track. Butt caps, because a round cap on a closed circle adds
    // a bulge where the path starts and ends that reads as a flaw at 512px.
    context.setStrokeColor(accent.copy(alpha: 0.20)!)
    context.setLineWidth(width)
    context.setLineCap(.butt)
    context.addArc(center: centre, radius: radius,
                   startAngle: 0, endAngle: 2 * .pi, clockwise: false)
    context.strokePath()

    // The progress: a little over three quarters. Sweeps clockwise from the
    // top, which is the direction a progress indicator fills.
    context.setLineCap(.round)
    context.setStrokeColor(accent)
    context.addArc(center: centre, radius: radius,
                   startAngle: start, endAngle: start - 4.9, clockwise: true)
    context.strokePath()

    guard let image = context.makeImage() else { return nil }
    let rep = NSBitmapImageRep(cgImage: image)
    rep.size = NSSize(width: size, height: size)
    return rep.representation(using: .png, properties: [:])
}

let output = URL(fileURLWithPath: CommandLine.arguments[1])
let iconset = output.appendingPathComponent("AppIcon.iconset")
try? FileManager.default.createDirectory(at: iconset, withIntermediateDirectories: true)

for size in sizes {
    guard let data = render(size: size) else {
        FileHandle.standardError.write(Data("failed to render \(size)\n".utf8))
        exit(1)
    }
    // The 512 and 1024 renders each serve two slots: the plain one and the
    // 2x variant of the half-size one. iconutil requires all ten.
    let names: [String]
    if size == 1024 {
        names = ["icon_512x512@2x.png"]
    } else if size == 512 {
        names = ["icon_512x512.png", "icon_256x256@2x.png"]
    } else {
        names = [
            "icon_\(size)x\(size).png",
            "icon_\(size * 2)x\(size * 2)@2x.png",
        ]
    }
    for name in names {
        // Only the sizes iconutil actually asks for; the odd ones are skipped
        // rather than written, because a stray file fails the whole set.
        let keep = [
            "icon_16x16.png", "icon_16x16@2x.png", "icon_32x32.png",
            "icon_32x32@2x.png", "icon_128x128.png", "icon_128x128@2x.png",
            "icon_256x256.png", "icon_256x256@2x.png", "icon_512x512.png",
            "icon_512x512@2x.png",
        ]
        guard keep.contains(name) else { continue }
        try? data.write(to: iconset.appendingPathComponent(name))
    }
}
