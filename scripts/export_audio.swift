import Foundation
import AVFoundation

let args = CommandLine.arguments
if args.count < 3 {
    fputs("usage: swift export_audio.swift <video_path> <out_audio_path>\n", stderr)
    exit(1)
}
let inputURL = URL(fileURLWithPath: args[1])
let outputURL = URL(fileURLWithPath: args[2])
try? FileManager.default.removeItem(at: outputURL)
let asset = AVURLAsset(url: inputURL)

guard let session = AVAssetExportSession(asset: asset, presetName: AVAssetExportPresetAppleM4A) else {
    fputs("cannot create export session\n", stderr)
    exit(2)
}
session.outputURL = outputURL
session.outputFileType = .m4a
let sem = DispatchSemaphore(value: 0)
session.exportAsynchronously { sem.signal() }
_ = sem.wait(timeout: .now() + 1800)
print(outputURL.path)
