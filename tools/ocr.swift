// Read the text out of an image using the macOS Vision framework.
// No dependency to install: this is the OS. Used by tools/shot-gate.py, which
// checks that what the site SAYS about a screenshot is what the screenshot SHOWS.
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count > 1,
      let img = NSImage(contentsOfFile: args[1]),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    FileHandle.standardError.write("cannot read image\n".data(using: .utf8)!)
    exit(2)
}
let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.usesLanguageCorrection = false
req.recognitionLanguages = ["en-US"]
try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])
for o in (req.results ?? []) {
    if let c = o.topCandidates(1).first { print(c.string) }
}
