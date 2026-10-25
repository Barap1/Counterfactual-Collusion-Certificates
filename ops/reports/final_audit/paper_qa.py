"""Final PDF/page provenance, text boundaries and contact sheets (local only)."""
from pathlib import Path
import hashlib
import json
import subprocess
from PIL import Image, ImageDraw
import pdfplumber

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent / "paper"


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    pdf_path = ROOT / "paper/v2/build/submission_v2.pdf"
    paths = sorted((OUT / "final-annotation-pages").glob("page-*.png"))
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        assert len(paths) == len(pdf.pages) == 23
        for i, p in enumerate(pdf.pages, 1):
            text = p.extract_text() or ""
            assert text.strip(), f"blank page {i}"
            outside = [c for c in p.chars if c["x0"] < 60 or c["x1"] > 552 or c["top"] < 60 or c["bottom"] > 735]
            assert not outside, f"text outside safe page box: {i}"
            previous = OUT / "legible-pages" / paths[i-1].name
            pages.append({"page":i,"png":str(paths[i-1].relative_to(ROOT)),"png_sha256":sha(paths[i-1]),
                          "text_characters":len(text),"smallest_extracted_font_pt":min(c["size"] for c in p.chars),
                          "text_outside_60pt_safe_box":len(outside),"identical_to_reviewed_pre_annotation_render":sha(previous)==sha(paths[i-1]),
                          "references_heading":"References" in text,"appendices_heading":"Appendices" in text,
                          "first_text":text[:110]})
        assert "References" in (pdf.pages[8].extract_text() or "")
        assert "Appendices" in (pdf.pages[9].extract_text() or "")
    for start in range(0,len(paths),4):
        contact = Image.new("RGB",(1800,2380),"#cccccc")
        draw = ImageDraw.Draw(contact)
        for j,p in enumerate(paths[start:start+4]):
            im = Image.open(p).convert("RGB")
            im.thumbnail((900,1165))
            x,y=(j%2)*900,(j//2)*1190
            contact.paste(im,(x,y+25)); draw.text((x+15,y+7),p.stem,fill="black")
        contact.save(OUT/f"final-annotation-contact-{start//4+1}.jpg",quality=92)
    old = OUT / "page_geometry.json"
    if old.exists() and not (OUT / "page_geometry.pre-legibility.json").exists():
        old.rename(OUT / "page_geometry.pre-legibility.json")
    elif old.exists() and not (OUT / "page_geometry.pre-final-annotation.json").exists():
        (OUT / "page_geometry.pre-final-annotation.json").write_bytes(old.read_bytes())
    result={"classification":"EXECUTED","pdf_sha256":sha(pdf_path),"page_count":23,"main_text_pages":[1,8],
            "references_pages":[9,9],"appendices_pages":[10,23],"render_dpi":150,"pages":pages,
            "visual_review":"All final contact sheets inspected by root; main Figures1–3 and tables legible; dense legacy appendix matrix/curve annotations require owner graphics polish. No broad aesthetic redesign performed.",
            "remaining_owner_items":["author/affiliation","template adaptation approval","LLM/human verification wording","dual-use/release sign-off","final visual approval"]}
    old.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:result[k] for k in ("pdf_sha256","page_count","main_text_pages","references_pages","appendices_pages")},indent=2))


if __name__ == "__main__":
    main()
