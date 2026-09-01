// Read the text out of an image using the macOS Vision framework.
// No dependency to install: this is the OS. Used by tools/shot-gate.py, which
// checks that what the site SAYS about a screenshot is what the screenshot SHOWS.
//
//     swift tools/ocr.swift <image>                  the text, one line per observation
//     swift tools/ocr.swift <image> --lang es-ES     recognise Spanish
//     swift tools/ocr.swift <image> --boxes          each line prefixed x,y,w,h in 0..1
//
// THE RECOGNISER WAS PINNED TO en-US WHILE GATING A SPANISH PAGE (2026-09-01), so the language
// now travels with the call. Reading Spanish with an English model is wrong on its face and the
// flag costs nothing.
//
// 🔒 BUT MEASURE THE FIX BEFORE YOU CLAIM IT, BECAUSE THIS ONE BOUGHT NOTHING. I wrote this
// comment first asserting the English model was why the same frame came back with "lo que
// trena" for "lo que frena" and "veritico" for "verifico". Then I ran both arms and diffed
// them: es-ES output is BYTE-IDENTICAL to en-US on all four Spanish frames. Those misreads are
// the recogniser's limit on this typeface at this size, not a language setting, and es-ES does
// not repair them.
//
// The consequence is the rule, not the flag: shot-gate refuses a caption whose phrase is not in
// the pixels, and the pixels are whatever THIS tool reads, misreads included. So a caption is
// authored from this tool's OUTPUT (`tools/quotable.py`), never from the screen a human sees.
// Quoting "lo que frena" because that is what the app truly says would fail a gate that is
// working correctly.
//
// 🔒 AND IT COULD NOT SAY WHERE ANYTHING WAS. The home page pins three numbered callouts onto
// the screenshot at hard-coded percentages. Those percentages were measured by eye against one
// English frame, so the Spanish frame (Spanish runs 20-30% longer, and this one carries an
// extra banner) would have put every pin on the wrong element while every gate stayed green:
// no check reads a pin position. `--boxes` exists so a pin is placed from the pixels, the same
// way every other number on this site is.
import Vision
import AppKit

let args = CommandLine.arguments
guard args.count > 1,
      let img = NSImage(contentsOfFile: args[1]),
      let cg = img.cgImage(forProposedRect: nil, context: nil, hints: nil) else {
    FileHandle.standardError.write(Data("cannot read image\n".utf8))
    exit(2)
}

// Default stays en-US so every existing caller is byte-identical.
var languages = ["en-US"]
if let i = args.firstIndex(of: "--lang"), i + 1 < args.count {
    languages = args[i + 1].split(separator: ",").map(String.init)
}
let wantBoxes = args.contains("--boxes")

let req = VNRecognizeTextRequest()
req.recognitionLevel = .accurate
req.usesLanguageCorrection = false
req.recognitionLanguages = languages
try? VNImageRequestHandler(cgImage: cg, options: [:]).perform([req])

for o in (req.results ?? []) {
    guard let c = o.topCandidates(1).first else { continue }
    if wantBoxes {
        // Vision's origin is BOTTOM-left; every consumer here thinks in CSS top-left, so flip
        // y once, at the source, rather than in each caller that would forget.
        let b = o.boundingBox
        let top = 1.0 - b.origin.y - b.height
        print(String(format: "%.4f\t%.4f\t%.4f\t%.4f\t%@",
                     b.origin.x, top, b.width, b.height, c.string))
    } else {
        print(c.string)
    }
}
