import argparse, faiss, numpy as np, json
from PIL import Image
from torchvision import transforms
import torch
from model import HybridEncoder
import pytesseract

def load_pages_index_json():
    with open('pages_meta_index.json','r',encoding='utf-8') as f:
        return json.load(f)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', required=True)
    parser.add_argument('--meta', required=True)
    parser.add_argument('--snippet', required=True)
    parser.add_argument('--model_ckpt', default='model_checkpoint.pt')
    parser.add_argument('--device', default='cpu')
    parser.add_argument('--top_k', type=int, default=5)
    parser.add_argument('--ocr_langs', default='eng')
    args = parser.parse_args()
    index = faiss.read_index(args.index)
    pages_meta = load_pages_index_json()
    device = torch.device(args.device)
    model = HybridEncoder(resnet_name='resnet34', embed_dim=384, num_transformer_layers=3).to(device)
    model.load_state_dict(torch.load(args.model_ckpt, map_location=device))
    model.eval()
    preprocess = transforms.Compose([
        transforms.Resize((512,512)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485,0.456,0.406], std=[0.229,0.224,0.225])
    ])
    snippet = Image.open(args.snippet).convert('RGB')
    x = preprocess(snippet).unsqueeze(0).to(device)
    with torch.no_grad():
        z = model(x).cpu().numpy().astype('float32')
    faiss.normalize_L2(z)
    D,I = index.search(z, args.top_k)
    results = []
    for score, idx in zip(D[0], I[0]):
        meta = pages_meta[idx]
        # optional OCR verification
        page_img = Image.open(meta['path']).convert('RGB')
        page_text = pytesseract.image_to_string(page_img, lang=args.ocr_langs)
        snippet_text = pytesseract.image_to_string(snippet, lang=args.ocr_langs)
        found = snippet_text.strip() and (snippet_text.strip() in page_text)
        results.append({'score': float(score), 'pdf_id': meta['pdf_id'], 'page': meta['page'], 'path': meta['path'], 'ocr_match': found})
    print('Top results:')
    for r in results:
        print(r)
