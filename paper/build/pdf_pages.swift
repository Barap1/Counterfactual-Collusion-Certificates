import PDFKit
import AppKit
let url = URL(fileURLWithPath: CommandLine.arguments[1])
let out = CommandLine.arguments[2]
guard let doc = PDFDocument(url: url) else { print("open failed"); exit(1) }
print("pages", doc.pageCount)
for i in 0..<doc.pageCount {
  let p = doc.page(at: i)!
  let t = p.string ?? ""
  var marks: [String] = []
  for k in ["Abstract","1. Introduction","Related Work","Methods","Results","Discussion","Conclusion","References","Appendix","LLM Usage"] { if t.contains(k) { marks.append(k) } }
  print("page \(i+1): \(marks.joined(separator: ", "))")
  let r = p.bounds(for: .mediaBox)
  let img = NSImage(size: NSSize(width: r.width*1.5, height: r.height*1.5))
  img.lockFocus(); NSColor.white.set(); NSRect(origin: .zero, size: img.size).fill()
  let ctx = NSGraphicsContext.current!.cgContext; ctx.scaleBy(x: 1.5, y: 1.5); p.draw(with: .mediaBox, to: ctx); img.unlockFocus()
  let rep = NSBitmapImageRep(data: img.tiffRepresentation!)!
  try! rep.representation(using: .png, properties: [:])!.write(to: URL(fileURLWithPath: "\(out)/p\(i+1).png"))
}
