import Foundation
import AVFoundation
import AppKit

func saveJPEG(_ image: CGImage, to url: URL, quality: CGFloat = 0.82) throws {
    let rep = NSBitmapImageRep(cgImage: image)
    guard let data = rep.representation(using: .jpeg, properties: [.compressionFactor: quality]) else {
        throw NSError(domain: "saveJPEG", code: 1)
    }
    try data.write(to: url)
}

let args = CommandLine.arguments
if args.count < 4 {
    fputs("usage: swift extract_frames.swift <video_path> <out_dir> <interval_seconds>\n", stderr)
    exit(1)
}

let videoURL = URL(fileURLWithPath: args[1])
let outDir = URL(fileURLWithPath: args[2], isDirectory: true)
let interval = Double(args[3]) ?? 30
try FileManager.default.createDirectory(at: outDir, withIntermediateDirectories: true)

let asset = AVURLAsset(url: videoURL)
let durationSeconds = CMTimeGetSeconds(asset.duration)
let generator = AVAssetImageGenerator(asset: asset)
generator.appliesPreferredTrackTransform = true

var t: Double = 0
var idx = 0
while t < durationSeconds {
    let time = CMTime(seconds: t, preferredTimescale: 600)
    do {
        let img = try generator.copyCGImage(at: time, actualTime: nil)
        let filename = String(format: "frame_%03d_%05.0fs.jpg", idx, t)
        try saveJPEG(img, to: outDir.appendingPathComponent(filename))
        print(filename)
    } catch {
        fputs("failed at \(t): \(error)\n", stderr)
    }
    t += interval
    idx += 1
}
if durationSeconds > 1 {
    let time = CMTime(seconds: max(0, durationSeconds - 1), preferredTimescale: 600)
    do {
        let img = try generator.copyCGImage(at: time, actualTime: nil)
        let filename = String(format: "frame_%03d_%05.0fs.jpg", idx, CMTimeGetSeconds(time))
        try saveJPEG(img, to: outDir.appendingPathComponent(filename))
        print(filename)
    } catch {
        fputs("failed at tail: \(error)\n", stderr)
    }
}
