import os
import argparse
from pdf2image import convert_from_path

def render_pdf_to_images(pdf_path, out_dir, dpi=200):
    pages = convert_from_path(pdf_path, dpi=dpi)
    os.makedirs(out_dir, exist_ok=True)
    out_paths = []
    base = os.path.splitext(os.path.basename(pdf_path))[0]
    for i, page in enumerate(pages, start=1):
        pth = os.path.join(out_dir, f"{base}_page_{i:04d}.png")
        page.save(pth, "PNG")
        out_paths.append(pth)
    return out_paths

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--pdf_dir', required=True)
    parser.add_argument('--out_dir', required=True)
    parser.add_argument('--dpi', type=int, default=200)
    args = parser.parse_args()
    pdfs = [os.path.join(args.pdf_dir, f) for f in os.listdir(args.pdf_dir) if f.lower().endswith('.pdf')]
    for pdf in pdfs:
        print('Rendering', pdf)
        render_pdf_to_images(pdf, args.out_dir, dpi=args.dpi)
