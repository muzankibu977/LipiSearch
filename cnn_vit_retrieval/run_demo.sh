#!/bin/bash
echo "This script shows the order of commands for the demo. Edit paths as needed."
echo "1) Render PDFs: python src/render_pdfs.py --pdf_dir example/pdfs --out_dir example/pages --dpi 200"
echo "2) Prepare dataset: python src/prepare_dataset.py --pages_dir example/pages --out_meta example/pages_meta.json"
echo "3) Train (demo): python src/train.py --meta example/pages_meta.json --epochs 2 --batch_size 8 --device cpu"
echo "4) Build index: python src/build_index.py --meta example/pages_meta.json --index_out example/index.faiss --emb_out example/embeddings.npy"
echo "5) Query: python src/query.py --index example/index.faiss --meta example/pages_meta.json --snippet example/snippet.png --top_k 5"
