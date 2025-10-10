# CNN+ViT PDF Snippet Retrieval (Demo)

## Overview
This project provides a runnable starter implementation of a **CNN+ViT hybrid retrieval system**
that matches a screenshot snippet (image) to PDF page images. It includes:

- PDF rendering helper (uses `pdf2image`)
- Dataset generator that produces snippet/page pairs
- Hybrid encoder (ResNet -> small Transformer)
- Contrastive training loop (InfoNCE)
- FAISS index builder and query script
- Optional OCR verification using Tesseract

**Important:** This is a starter demo to get you working quickly. It runs on CPU but benefits greatly from a GPU.

## What you get in the zip
- `src/` — all Python code (see below)
- `requirements.txt` — pip packages required
- `example/` — example folder structure (place your PDFs under `example/pdfs/`)
- `run_demo.sh` — quick commands to run a small demo (edit paths as needed)

## Quick setup (Linux / WSL / macOS)
1. Create a Python environment (recommend Python 3.9+):
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Install Poppler (required by `pdf2image`):
   - Ubuntu/Debian: `sudo apt-get install poppler-utils`
   - macOS (brew): `brew install poppler`
3. (Optional) Install Tesseract for OCR:
   - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
   - macOS (brew): `brew install tesseract`
   - Install language packs as needed (e.g., `tesseract-ocr-ben` for Bengali)

## Basic usage
1. Put PDFs into `example/pdfs/` (each .pdf).
2. Render pages:
   ```bash
   python src/render_pdfs.py --pdf_dir example/pdfs --out_dir example/pages --dpi 200
   ```
3. Prepare a simple dataset (creates random crops from pages):
   ```bash
   python src/prepare_dataset.py --pages_dir example/pages --out_meta example/pages_meta.json
   ```
4. Train for a few epochs (demo):
   ```bash
   python src/train.py --meta example/pages_meta.json --epochs 2 --batch_size 8 --device cpu
   ```
5. Build FAISS index:
   ```bash
   python src/build_index.py --meta example/pages_meta.json --index_out example/index.faiss --emb_out example/embeddings.npy
   ```
6. Query with a screenshot image:
   ```bash
   python src/query.py --index example/index.faiss --meta example/pages_meta.json --snippet example/snippet.png --top_k 5
   ```

## Notes & next steps
- Add more PDFs and train longer for better accuracy.
- Use a GPU and larger model (resnet50) for improved results.
- For paragraph-level matching, enable OCR verification in `query.py`.

