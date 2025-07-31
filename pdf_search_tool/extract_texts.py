import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import json
import os
import pdfplumber

def extract_text_from_pdf(pdf_path, langs='eng+ben+urd+heb'):
    doc = fitz.open(pdf_path)
    result = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if not text.strip():
            pix = page.get_pixmap(dpi=300)
            img = Image.open(io.BytesIO(pix.tobytes()))
            text = pytesseract.image_to_string(img, lang=langs)
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        result.append(lines)
    return result

def build_index(pdf_dir='pdfs', out_file='indexed_texts.json'):
    if os.path.exists(out_file):
        with open(out_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = {}

    for fname in os.listdir(pdf_dir):
        if not fname.lower().endswith('.pdf'):
            continue

        fpath = os.path.join(pdf_dir, fname)
        mtime = os.path.getmtime(fpath)
        key = f"{fname}|{mtime}"

        if any(k.startswith(fname) for k in index if key in k):
            continue  # already indexed

        print(f"Indexing {fname} ...")
        try:
            index[key] = extract_text_from_pdf(fpath)
        except Exception as e:
            print(f"⚠️ Failed: {fname} → {e}")
    
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    build_index()